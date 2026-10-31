# PART 14 — Performance & Reliability

> **Goal of this part:** load-test a system where every request costs money, latency depends on the length of an answer nobody has generated yet, and "the same request" produces different work each time.

---

# PART A — PERFORMANCE

## 14.1 Why LLM performance testing is different

| | Traditional API | LLM API |
|---|---|---|
| Response time | Roughly fixed per endpoint | **Depends on output length**, which varies per request |
| The metric users feel | Total response time | **TTFT** — because streaming shows progress |
| Cost of a load test | Compute you already own | **Real money per request** |
| Scaling | Add servers | Provider quota, GPU capacity, queueing |
| Cache | Response caching is normal | Semantic caching is possible but risky |
| Failure under load | Timeouts, 503 | 429s, queue depth, **degraded quality** |

**The metric that matters most is the one traditional load tools do not measure by default: TTFT.**

## 14.2 The metrics

| Metric | Definition | Target (typical chat UX) |
|---|---|---|
| **TTFT** | Time to first token | p95 < 1 s |
| **Tokens/sec** | Decode throughput per request | > 20 t/s feels fluent |
| **Total latency** | Request to last token | Depends on length; report with output-token count |
| **Time per output token** | Total decode time ÷ output tokens | Normalises across answer lengths |
| **Throughput** | Requests completed per second | Capacity planning |
| **Concurrency** | Simultaneous in-flight requests | Where degradation starts |
| **Queue time** | Wait before processing begins | The hidden killer under load |
| **Error rate** | By type: 429 vs 500 vs timeout | 429s mean quota; 500s mean something else |
| **Cost per request** | See Part 16 | Must be reported alongside latency |
| **Quality under load** | Eval score at concurrency | **The one everyone forgets** |

That final row is the distinctly GenAI concern. Under pressure, a system may fall back to a smaller model, reduce retrieved context, or trim history — all of which cut latency and quietly cut quality. **A load test that measures only latency will certify a system that has silently degraded.**

```
TC-PERF-001  Quality under load
Method:     Run the standard eval golden set (a) idle, (b) at target
            concurrency, (c) at 2× target
Expected:   Eval scores within 3% across all three conditions
Detects:    Silent model downgrade, context truncation, and reranker
            skipping under pressure
Priority:   High — and almost never tested
```

## 14.3 Designing the load profile

**Never load-test with `"hi"`.** Latency scales with input *and* output length, so a synthetic short prompt measures nothing real.

```python
# Build the profile from production data.
LOAD_PROFILE = [
    {"weight": 0.60, "input_tokens": 150,  "expected_output": 80,   "name": "short_qa"},
    {"weight": 0.25, "input_tokens": 800,  "expected_output": 200,  "name": "rag_answer"},
    {"weight": 0.10, "input_tokens": 3000, "expected_output": 400,  "name": "long_context"},
    {"weight": 0.05, "input_tokens": 500,  "expected_output": 1500, "name": "long_generation"},
]
```
Derive these numbers from real traffic: query your traces for the p50/p90/p99 of input and output tokens. If nobody is recording that, **the absence of the data is your first finding.**

## 14.4 k6 — worked example

```javascript
// k6 run --vus 20 --duration 5m llm_load.js
import http from 'k6/http';
import { check } from 'k6';
import { Trend, Rate } from 'k6/metrics';

const ttft = new Trend('ttft_ms');            // custom metric: the one that matters
const tokensPerSec = new Trend('tokens_per_sec');
const rateLimited = new Rate('rate_limited');

export const options = {
  scenarios: {
    ramp: {
      executor: 'ramping-vus',
      stages: [
        { duration: '2m', target: 10 },   // warm up
        { duration: '5m', target: 50 },   // target load
        { duration: '2m', target: 100 },  // find the knee
        { duration: '2m', target: 0 },
      ],
    },
  },
  thresholds: {
    'ttft_ms': ['p(95)<1000'],
    'http_req_failed': ['rate<0.01'],
    'rate_limited': ['rate<0.05'],
  },
};

const PROFILE = JSON.parse(open('./prompts.json'));   // realistic mixed prompts

export default function () {
  const p = PROFILE[Math.floor(Math.random() * PROFILE.length)];
  const start = Date.now();

  // Non-streaming: measure time-to-first-byte as a TTFT proxy.
  const res = http.post(`${__ENV.BASE_URL}/v1/chat/completions`,
    JSON.stringify({ model: __ENV.MODEL, messages: p.messages, max_tokens: p.max_tokens }),
    { headers: { 'Content-Type': 'application/json',
                 'Authorization': `Bearer ${__ENV.API_KEY}` },
      timeout: '120s' });

  rateLimited.add(res.status === 429);

  if (res.status === 200) {
    const body = res.json();
    const total = (Date.now() - start) / 1000;
    ttft.add(res.timings.waiting);                       // TTFB ≈ TTFT here
    tokensPerSec.add(body.usage.completion_tokens / total);

    check(res, {
      'completed cleanly': (r) => r.json().choices[0].finish_reason === 'stop',
      'usage reported':    (r) => r.json().usage !== undefined,
    });
  }
}
```

**For true TTFT you must stream**, which k6 handles less naturally than Python. A common split: k6 or Locust for throughput and error behaviour at scale, plus a small Python async harness for accurate streaming TTFT.

```python
# Python streaming TTFT under concurrency
import asyncio, time, httpx, numpy as np

async def one_request(client, payload, sem):
    async with sem:                        # cap concurrency deliberately
        t0 = time.perf_counter()
        ttft = None
        n = 0
        async with client.stream("POST", URL, json={**payload, "stream": True},
                                 headers=HEADERS, timeout=120) as r:
            async for line in r.aiter_lines():
                if line.startswith("data: ") and "[DONE]" not in line:
                    if ttft is None:
                        ttft = time.perf_counter() - t0
                    n += 1
        return {"ttft": ttft, "total": time.perf_counter() - t0, "chunks": n}

async def run_load(concurrency=50, total=500):
    sem = asyncio.Semaphore(concurrency)
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*[
            one_request(client, sample_payload(), sem) for _ in range(total)
        ], return_exceptions=True)
    ok = [r for r in results if isinstance(r, dict)]
    return {
        "n": len(ok), "errors": len(results) - len(ok),
        "ttft_p50": float(np.percentile([r["ttft"] for r in ok], 50)),
        "ttft_p95": float(np.percentile([r["ttft"] for r in ok], 95)),
        "total_p95": float(np.percentile([r["total"] for r in ok], 95)),
    }
```

## 14.5 Tool selection

| Tool | Use for | Note |
|---|---|---|
| **k6** | Throughput, ramping, thresholds in CI | JS; excellent CI story; SSE needs extra work |
| **Locust** | Python-native, complex scenarios | Easiest if your team is Python; async workers handle streaming well |
| **JMeter** | Enterprise standard, existing suites | Heavy; poor fit for streaming |
| **Artillery** | JS, good SSE/WebSocket support | Reasonable middle ground |
| **Custom async Python** | Accurate TTFT, cost tracking, quality-under-load | Usually the right answer for the GenAI-specific metrics |

## 14.6 Cost control for load testing

**A load test against a paid API is a bill.** Before running one:

1. **Get written approval for a spend cap**, and put a hard cap in the provider console.
2. Estimate first: `requests × (input_tokens × in_price + output_tokens × out_price)`.
3. Use a local model (Ollama) or a cheap model to validate the *harness* before spending.
4. Test **your infrastructure** against a mocked provider to isolate your own bottlenecks — most capacity problems are in your app, not the model.
5. Cap `max_tokens` in load tests, and note that this changes the latency profile.
6. Run the expensive full-scale test once, not nightly.

```
TC-PERF-002  Cost of the load test itself
Before running: estimate and get approval.
  500 requests × (800 in + 200 out tokens)
  = 400k input + 100k output tokens
  ≈ $X at current pricing.
Record actual vs estimate afterwards — that ratio is itself useful data
about your cost model.
```

## 14.7 What to look for in the results

| Symptom | Likely cause |
|---|---|
| TTFT rises but tokens/sec is stable | Queueing — requests waiting to start |
| Tokens/sec falls | Compute contention or batch pressure |
| Sudden 429 wall | Provider rate limit reached |
| Latency fine, errors rise | Your own connection pool or timeout config |
| **Quality drops under load** | Silent fallback to a smaller model or reduced context |
| Cost per request rises under load | Retries multiplying work |
| p99 far above p95 | A slow path: cold start, cache miss, or a specific prompt type |

---

# PART B — RELIABILITY

## 14.8 Testing a non-deterministic system for reliability

**Reframe the question.** Not "does it work?" but **"how often does it work, and how bad is the worst case?"**

```python
def reliability_profile(system, case, n=50):
    """Run the same case 50 times. Report the DISTRIBUTION, not the mean.
    The min is what a real user will eventually hit."""
    results = [evaluate(system(case["input"]), case) for _ in range(n)]
    scores = [r["score"] for r in results]
    return {
        "pass_rate": sum(r["passed"] for r in results) / n,
        "mean": statistics.mean(scores),
        "p10": float(np.percentile(scores, 10)),   # the bad-day experience
        "min": min(scores),                        # the worst case that exists
        "stdev": statistics.pstdev(scores),
        "distinct_failure_modes": categorise_failures(results),
    }
```

**Report `min` and `p10`, not just the mean.** A feature with a mean score of 0.88 and a minimum of 0.20 has a failure a user *will* meet. A feature with a mean of 0.85 and a minimum of 0.78 is more reliable despite the lower average. Averages are the wrong summary for a system users experience one sample at a time.

## 14.9 The reliability test matrix

| # | Category | Test | Expected |
|---|---|---|---|
| 1 | **Variance** | N=50 on core cases | Pass-rate ≥ threshold; min above a floor |
| 2 | Variance | Same test across a week | No drift — detects provider-side model changes |
| 3 | **Provider outage** | Force 503 from the primary | Fallback model engages; user sees a degraded but working service |
| 4 | Fallback quality | Run the eval set against the *fallback* model | Fallback quality is known and acceptable — most teams have never measured it |
| 5 | Partial failure | RAG retrieval down, LLM up | Honest degraded answer ("I can't reach the knowledge base"), not a silent unsourced guess |
| 6 | Partial failure | One tool down in an agent | Other capabilities still work |
| 7 | **Timeout** | Slow provider | Bounded wait; the user is told |
| 8 | Retry | Transient error | Retries with backoff and jitter; **idempotent for side effects** |
| 9 | Retry storm | Many clients failing together | Jitter prevents synchronised retries |
| 10 | Rate limit | Sustained 429 | Queue or shed load gracefully; never a 500 |
| 11 | **Model deprecation** | Point at a retired model ID | Clean, actionable error — or a documented fallback |
| 12 | Cold start | First request after idle | Acceptable, or warmed |
| 13 | Long conversation | 100 turns | Coherent; guardrails intact; cost bounded |
| 14 | Concurrent same-user | Two requests, one session | No history corruption |
| 15 | **Idempotency** | Repeat a side-effecting request | One effect, not two |

**Item 4 is the one to raise in every design review.** Teams configure a fallback model for outages and never evaluate it. The fallback is by definition used during an incident — the worst possible time to discover it produces bad answers.

```
TC-REL-004  Fallback model quality
Method:     Run the full eval golden set against the configured fallback
            model at production settings
Expected:   Documented score. If materially worse than primary, the
            product should degrade VISIBLY (a banner, a disclaimer),
            not silently.
Priority:   High
Finding shape: "The fallback model scores 0.61 on faithfulness vs 0.89
            for the primary, and users receive no indication. During an
            outage, answer quality drops by a third with no signal."
```

## 14.10 Graceful degradation ladder

Design the ladder, then test each rung:

```
FULL SERVICE        primary model + RAG + reranker + tools
      ↓ reranker unavailable
DEGRADED 1          primary model + RAG (no rerank)     → quality noted
      ↓ retrieval unavailable
DEGRADED 2          primary model, no context           → MUST say so
      ↓ primary model unavailable
DEGRADED 3          fallback model + RAG                → quality noted
      ↓ all models unavailable
DEGRADED 4          cached / templated response, or an honest error
      ↓
FAIL                clear message, no fabrication
```

**The critical rung is DEGRADED 2.** If retrieval fails and the model answers anyway from parametric knowledge, the user receives an ungrounded answer that looks identical to a grounded one. That is the most dangerous state the system can be in, and it is trivially testable by disabling the retriever.

---

## 14.11 Self-check

1. Why is TTFT more important than total latency for a chat product?
2. Why is load-testing with `"hi"` meaningless?
3. What is "quality under load" and what does it detect?
4. Why report `min` and `p10` rather than the mean for reliability?
5. Why is an untested fallback model a serious risk?
6. What happens at DEGRADED 2, and why is it the most dangerous rung?
7. Why must retries be idempotent in agent systems?

---

**Next:** [PART-15-OBSERVABILITY.md](PART-15-OBSERVABILITY.md) — traces, spans, and the OpenTelemetry GenAI conventions.
