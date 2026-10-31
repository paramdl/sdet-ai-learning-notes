# PART 15 — AI Observability

> **Goal of this part:** ensure that when something goes wrong in production, it can be investigated. In a non-deterministic system, **an incident you cannot reproduce is an incident you can only debug from its trace.** If the trace does not exist, the investigation does not happen.
>
> This makes observability a **testable requirement**, not an ops nicety. "There is no trace for this request" is a legitimate, high-priority defect.

---

## 15.1 Why observability is a QA concern here

In traditional software you reproduce a bug locally. With GenAI you often cannot: the same input gives a different output, the model version may have shifted, and the retrieved context depended on an index that has since changed.

So the trace *is* the evidence. Your requirements become:

| Requirement | Test |
|---|---|
| Every request produces a trace | Assert trace existence for a sampled request |
| The trace contains the full prompt sent | Including assembled context and history |
| The trace contains the full response | Including tool calls |
| Token counts and cost are recorded | Reconcile against the provider |
| Model, prompt version, and parameters are recorded | Enables "what produced this?" |
| Latency is broken down by stage | Retrieval vs model vs tools |
| A correlation ID links UI → API → model | End-to-end investigation |
| **PII is redacted before storage** | A privacy requirement, tested |
| Retention is defined and enforced | Compliance |

---

## 15.2 The three signals

| Signal | What it is | GenAI examples |
|---|---|---|
| **Logs** | Discrete events with context | Request received, guardrail triggered, retry attempted |
| **Metrics** | Aggregated numbers over time | p95 TTFT, tokens/min, cost/hour, eval score, refusal rate |
| **Traces** | The causal tree of one request | The one that matters most here |

## 15.3 Traces and spans

> **Imagine this…** A trace is the full story of one request. Spans are the chapters, nested to show what caused what and how long each took.

### Example — an LLM-only application

```
TRACE  id=a1b2c3  user=u_88  session=s_41  duration=1 240 ms  cost=$0.0021
│
├─ SPAN  http.request              12 ms
├─ SPAN  guardrail.input           35 ms    verdict=pass
├─ SPAN  prompt.assemble            4 ms    prompt_version=v3.2  tokens=412
├─ SPAN  llm.chat                1 150 ms
│        model=claude-x  temperature=0.3
│        input_tokens=412  output_tokens=118
│        ttft_ms=380  finish_reason=stop  cost=$0.0021
├─ SPAN  guardrail.output           28 ms   verdict=pass
└─ SPAN  persist                    11 ms
```

### Example — a RAG application

```
TRACE  id=d4e5f6  duration=2 890 ms  cost=$0.0038
│
├─ SPAN  guardrail.input              31 ms
├─ SPAN  query.rewrite               210 ms   original="refunds?" → rewritten=…
├─ SPAN  embed.query                  64 ms   model=embed-3  dim=1536
├─ SPAN  vector.search               142 ms   k=20  filter=tenant:acme
│        └─ returned: 20 chunks, top_score=0.89, min_score=0.61
├─ SPAN  rerank                      380 ms   in=20  out=5  model=rerank-v2
├─ SPAN  context.assemble             8 ms    chunks=5  context_tokens=1 840
│        └─ chunk_ids=[doc12#3, doc12#4, doc7#1, doc31#9, doc7#2]
├─ SPAN  llm.chat                  1 980 ms   input=2 310  output=142
├─ SPAN  citation.validate            44 ms   cited=3  verified=3  fabricated=0
└─ SPAN  guardrail.output             31 ms
```

**Note what this trace makes possible.** Given a bad answer, you can immediately see whether the right chunks were retrieved (the retrieval-vs-generation question from Part 7 §7.2) without re-running anything. **A RAG trace that does not record chunk IDs and scores is not fit for purpose**, and that is a specific, actionable finding you can raise on day one.

### Example — an agent application

```
TRACE  id=g7h8i9  duration=8 420 ms  cost=$0.0142  steps=4
│
├─ SPAN  agent.run  goal="Refund order ORD-4471"
│  ├─ SPAN  agent.step[1]
│  │  ├─ SPAN  llm.plan          820 ms   decision=call:get_order
│  │  └─ SPAN  tool.get_order    340 ms   args={"order_id":"ORD-4471"}  status=200
│  ├─ SPAN  agent.step[2]
│  │  ├─ SPAN  llm.plan          760 ms   decision=call:check_eligibility
│  │  └─ SPAN  tool.check_eligibility  180 ms  result={"eligible":true}
│  ├─ SPAN  agent.step[3]
│  │  ├─ SPAN  llm.plan          910 ms   decision=request_confirmation
│  │  └─ SPAN  human.confirm   4 100 ms   approved=true  actor=u_88
│  └─ SPAN  agent.step[4]
│     ├─ SPAN  llm.plan          690 ms   decision=call:issue_refund
│     └─ SPAN  tool.issue_refund 620 ms   args={"amount_cents":2500}  status=201
└─ SPAN  agent.finalise          
```

This trace is what makes the trajectory assertions in Part 9 §9.3 possible. **Without agent tracing, agent testing is guesswork.**

---

## 15.4 OpenTelemetry for GenAI ⏳

OpenTelemetry is the vendor-neutral standard for traces, metrics, and logs. It has **GenAI semantic conventions** — an agreed set of attribute names for LLM operations — so that traces are portable between backends.

⏳ These conventions are still evolving; check the current OpenTelemetry semantic-conventions documentation for exact attribute names before standardising on them. The stable, useful part is the *shape*: an operation name, a model identifier, token counts, and finish reason, as span attributes.

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def traced_chat(messages, model, **params):
    """Instrumenting your own calls is often the fastest way to get
    useful traces, and it is vendor-neutral."""
    with tracer.start_as_current_span("chat") as span:
        span.set_attribute("gen_ai.system", "openai")
        span.set_attribute("gen_ai.request.model", model)
        span.set_attribute("gen_ai.request.temperature", params.get("temperature", 1.0))
        span.set_attribute("gen_ai.request.max_tokens", params.get("max_tokens", 0))
        span.set_attribute("app.prompt_version", PROMPT_VERSION)   # your own

        resp = client.chat.completions.create(model=model, messages=messages, **params)

        span.set_attribute("gen_ai.response.model", resp.model)
        span.set_attribute("gen_ai.response.finish_reasons", [resp.choices[0].finish_reason])
        span.set_attribute("gen_ai.usage.input_tokens", resp.usage.prompt_tokens)
        span.set_attribute("gen_ai.usage.output_tokens", resp.usage.completion_tokens)
        span.set_attribute("app.cost_usd", compute_cost(resp.usage, model))
        return resp
```

**Why prefer OTel over a vendor SDK:** portability. A team locked into one tracing vendor's SDK cannot move. Raising this in an architecture review is a genuinely useful contribution.

---

## 15.5 The tools

| Tool | Type | Notes |
|---|---|---|
| **Langfuse** | Open source, self-host or cloud | Traces, prompt management with versioning, datasets, online eval. Strong all-rounder; self-hosting needs Docker |
| **Arize Phoenix** | Open source, runs locally | Excellent RAG trace inspection; notebook-friendly; no server needed to start |
| **LangSmith** | Commercial | Very good; LangChain-centric; closed |
| **Helicone** | Proxy-based | One-line integration — change the base URL. Lowest-effort adoption |
| **W&B Weave / MLflow** | Experiment platforms | If the org already uses them for ML |
| **OpenTelemetry + your existing APM** | Standard | Best long-term answer for enterprises with existing observability |

**Recommendation for learning:** Phoenix locally first (no infrastructure), Langfuse for a real project (persistence and prompt versioning).

---

## 15.6 Metrics to define and alert on

| Metric | Alert when |
|---|---|
| p95 TTFT | Above SLO |
| p95 total latency | Above SLO |
| Error rate by type (429/500/timeout) | Rises above baseline |
| **Cost per hour** | Above budget rate — the alert that prevents a bad month |
| Cost per user (top N) | Anomalous concentration |
| Tokens per request (p95) | Rising — prompt or context bloat |
| Refusal rate | Spikes (guardrail regression) or drops (guardrail broken) |
| **Retrieval empty rate** | Rises — index or corpus problem |
| Citation fabrication rate | Any non-zero |
| Guardrail trigger rate | Sudden change in either direction |
| Fallback model usage | Any sustained use — the primary is unhealthy |
| Online eval score (sampled) | Drops — quality regression in production |
| Tool error rate by tool | Rises |
| Agent step count (p95) | Rises — agents flailing |

**"Refusal rate dropping" as an alert is worth explaining.** A sudden fall in refusals usually means a guardrail was disabled or a prompt change removed a constraint — a safety regression that no functional test would catch. Alerting on a metric *falling* is unintuitive and valuable.

---

## 15.7 Online evaluation

Offline eval tests a dataset before release. **Online eval samples real production traffic and scores it.**

```python
def online_eval_sampler(trace_store, sample_rate=0.02, judge=None):
    """Score a small sample of real traffic continuously.

    This is how you detect quality regressions caused by things your
    offline suite cannot see: real user phrasing, corpus drift, and
    silent provider-side model changes."""
    for trace in trace_store.stream():
        if random.random() > sample_rate:
            continue
        scores = {
            "faithfulness": faithfulness(trace.output, trace.context, judge)["score"],
            "relevancy": answer_relevancy(trace.output, trace.input, judge),
            "refused": is_refusal(trace.output),
            "cited_ok": not validate_citations(trace.output, trace.chunks, judge)["fabricated_citations"],
        }
        metrics.record(scores, tags={"prompt_version": trace.prompt_version,
                                     "model": trace.model})
        if scores["faithfulness"] < 0.6:
            trace_store.flag_for_review(trace.id)     # feeds the golden set
```

**The feedback loop that makes this compound:** flagged production failures become new golden-set cases. Over six months, your dataset stops being something you invented and becomes a record of how your system actually fails. That is the difference between an eval suite that decays and one that improves.

---

## 15.8 Privacy in observability 🔴

Tracing sends prompts and responses somewhere. That is a data-protection surface.

| Test | Expected |
|---|---|
| PII redaction before storage | Canary PII never reaches the trace store (Part 11 A5b) |
| Third-party processor agreement | If traces go to a SaaS, a DPA exists |
| Retention enforced | Traces older than the policy are deleted — verify, don't assume |
| Access control on traces | Not everyone in the company can read customer conversations |
| Data residency | Traces from EU users stored appropriately |
| Right to erasure | A user's deletion request removes their traces too |
| Secrets never traced | API keys, tokens, and internal credentials excluded |

The right-to-erasure case is routinely missed: teams delete the user's account and their conversation records, and leave a full copy of every conversation in the tracing platform.

---

## 15.9 Self-check

1. Why is a missing trace a legitimate defect rather than an ops issue?
2. What must a RAG trace record to be useful, and why?
3. Why is agent tracing a prerequisite for agent testing?
4. Why prefer OpenTelemetry over a vendor SDK?
5. Why alert on refusal rate *falling*?
6. What is online evaluation and what does it catch that offline cannot?
7. Name three privacy tests for a tracing platform.

---

**Next:** [PART-16-COST-TOKEN-TESTING.md](PART-16-COST-TOKEN-TESTING.md) — the money chapter.
