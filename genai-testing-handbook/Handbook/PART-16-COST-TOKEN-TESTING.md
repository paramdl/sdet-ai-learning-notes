# PART 16 — Cost & Token Testing

> **Goal of this part:** treat cost as a testable, gateable, regressable quality attribute. GenAI is the first common software category where **a code change can multiply your infrastructure bill by ten without any performance symptom**. Nobody else in the team is testing this. It is the fastest way for a QA engineer to demonstrate business value.

⏳ Maps to OWASP **LLM06 Unbounded Consumption**, which rose four places in the 2026 list.

---

## 16.1 The cost model

```
COST PER REQUEST =
    (input_tokens        × input_price_per_token)
  + (output_tokens       × output_price_per_token)
  + (reasoning_tokens    × reasoning_price_per_token)     ← often invisible
  + (cached_input_tokens × cached_price_per_token)        ← usually discounted
  + (embedding_tokens    × embedding_price_per_token)     ← RAG only
  + (rerank_units        × rerank_price)                  ← RAG only
  + (tool_call_costs)                                     ← agents: external APIs
```

**Three facts that surprise people:**
1. **Output tokens usually cost several times more than input tokens.** A change that makes answers longer is more expensive than one that makes prompts longer.
2. **Reasoning tokens are billed and often not shown.** A 200-token visible answer may have cost 4,000 tokens.
3. **Cached input is much cheaper.** A stable prompt prefix that hits the cache can cut costs dramatically — which makes prompt *stability* a cost feature, and prompt churn a cost regression.

```python
# pricing.py — keep prices in config, never in code.
# ⏳ Prices change; read them from a versioned config file and test that
#    the config matches the provider's published rates.
def compute_cost(usage: dict, model: str, pricing: dict) -> float:
    p = pricing[model]
    cached = usage.get("cached_input_tokens", 0)
    fresh_input = usage["input_tokens"] - cached
    return (
        fresh_input             * p["input"]
      + cached                  * p.get("cached_input", p["input"])
      + usage["output_tokens"]  * p["output"]
      + usage.get("reasoning_tokens", 0) * p.get("reasoning", p["output"])
    ) / 1_000_000        # prices are typically quoted per million tokens
```

---

## 16.2 The derived metrics

| Metric | Formula | Why |
|---|---|---|
| **Cost per request** | as above | The atom |
| **Cost per conversation** | Σ over turns | Grows superlinearly — history is resent each turn |
| **Cost per user per month** | Σ over their conversations | Unit economics |
| **Cost per resolved task** | total cost ÷ successful outcomes | **The metric that matters.** A cheap model that fails half the time is not cheap |
| **Cost per eval run** | | Budget for CI |
| **Token efficiency** | useful output tokens ÷ total tokens | Detects waste |

**Cost per resolved task is the number to push a team toward.** It reframes "which model is cheaper?" into "which model is cheaper *per outcome*?", and it frequently reverses the answer. A model at half the price that needs two attempts costs the same and delivers a worse experience.

**Conversation cost grows superlinearly.** Turn 10 resends nine previous turns:
```
Turn 1:  500 in  →  cost c
Turn 5:  2 500 in → cost 5c
Turn 20: 12 000 in → cost 24c
```
```
TC-COST-001  Conversation cost curve
Method:     Run a scripted 30-turn conversation; record cumulative cost
            per turn; plot it
Expected:   Growth is bounded by a documented history strategy
            (windowing, summarisation, or a hard cap)
Failure:    Unbounded linear-in-history growth — a long conversation
            costs 50× a short one, and one user can be 90% of the bill
Priority:   High
```

---

## 16.3 The cost test suite

### 1. Cost accounting accuracy 🔴
```python
def test_reported_cost_matches_provider(client, pricing):
    """The foundational test. If the app's own cost number is wrong,
    every dashboard and every budget alert downstream is wrong."""
    resp = client.chat(TEST_PAYLOAD)
    app_cost = app.get_recorded_cost(resp.request_id)
    true_cost = compute_cost(resp.usage.__dict__, resp.model, pricing)
    assert abs(app_cost - true_cost) / true_cost < 0.01, (
        f"Cost accounting drift: app says ${app_cost:.6f}, "
        f"provider usage implies ${true_cost:.6f}"
    )

def test_reasoning_tokens_are_counted(client, pricing):
    """Hidden reasoning tokens are the most commonly under-reported cost."""
    resp = client.chat(REASONING_PAYLOAD, model=REASONING_MODEL)
    assert resp.usage.get("reasoning_tokens", 0) > 0, "No reasoning tokens reported"
    app_cost = app.get_recorded_cost(resp.request_id)
    assert app_cost >= compute_cost(resp.usage.__dict__, REASONING_MODEL, pricing) * 0.99
```

### 2. Cost regression gate 🔴
The highest-value CI test in this part:
```python
def test_cost_per_case_has_not_regressed(golden_set, baseline):
    """Run the golden set, compare mean cost per case against the stored
    baseline. Catches prompt bloat, context bloat, and verbosity drift
    before they reach production."""
    costs = [run_and_cost(c) for c in golden_set]
    mean_cost = statistics.mean(costs)
    delta = (mean_cost - baseline["mean_cost"]) / baseline["mean_cost"]
    assert delta < 0.15, (
        f"Cost per case rose {delta:.0%} "
        f"(${baseline['mean_cost']:.5f} → ${mean_cost:.5f}). "
        f"Investigate prompt/context growth."
    )
```

### 3. Static prompt budget
```python
def test_prompt_token_budgets():
    """Prompts grow silently, one 'just add this line' at a time.
    Every request in production pays for it."""
    for name, prompt in ALL_PROMPTS.items():
        n = count_tokens(prompt)
        assert n <= BUDGETS[name], f"{name}: {n} tokens (budget {BUDGETS[name]})"
```

### 4. Context bloat detection
| Test | Expected |
|---|---|
| Retrieved context size | Within budget; K not silently increased |
| Duplicate chunks in context | None — deduplication works |
| History window enforced | Bounded |
| Tool definitions token cost | Measured — 20 tools can be 3,000 tokens on *every* request |
| Few-shot example cost | Measured; is each example earning its keep? |

The tool-definitions row is a frequently-missed cost sink. Every tool schema is resent on every request in a conversation. An agent with 25 tools may spend more on describing its tools than on the user's actual question.

### 5. Token explosion detection
| Pattern | Test |
|---|---|
| Runaway generation (repetition loop) | Assert output tokens < 2× the expected maximum |
| Agent loop | Step cap + cost cap (Part 9 §9.5) |
| Recursive summarisation | Bounded depth |
| Retry amplification | Retries counted in cost, and capped |
| User-controlled length | "Write 50,000 words" — capped server-side, not by prompt instruction |

### 6. Per-user quota enforcement 🔴
```
TC-COST-002  Denial of wallet (see Part 11 A8)
Measure:    Maximum spend per hour achievable by one account within the
            documented usage rules
Expected:   Per-user token quota, request quota, and cost cap enforced
            server-side
Report:     "$X/hour from a single free account"
```

### 7. Caching effectiveness
```
TC-COST-003  Prompt cache hit rate
Method:     Send 20 requests sharing a stable prefix; read the provider's
            cached-token counts
Expected:   Cache hit rate above the documented threshold
Detects:    A prompt whose prefix varies per request (e.g. a timestamp
            or user ID placed at the START of the system prompt),
            destroying cache eligibility
Value:      Moving one variable line from the top of a prompt to the
            bottom can cut input costs substantially. This is a
            concrete, high-impact finding.
```

---

## 16.4 Model selection on cost-effectiveness

The table your eval suite should produce, and the one that ends model-choice arguments:

| Model | Quality (eval) | Cost/req | Success rate | **Cost per resolved task** | p95 latency |
|---|---|---|---|---|---|
| Large | 0.91 | $0.0084 | 94% | **$0.0089** | 2.9 s |
| Mid | 0.86 | $0.0021 | 88% | **$0.0024** | 1.4 s |
| Small | 0.71 | $0.0004 | 62% | **$0.0006** | 0.6 s |
| Small + retry | 0.78 | $0.0008 | 74% | **$0.0011** | 1.1 s |

**How to read it:** the mid model is 3.7× cheaper per resolved task than the large one at 88% success. Whether that trade is acceptable is a product decision — but it is now a decision with numbers, made by the product owner, rather than an argument between engineers.

**A hybrid routing strategy often wins**, and is testable: route easy queries to the small model, hard ones to the large. The test is whether the *router* classifies correctly — a router that misroutes 20% of hard queries to the small model produces a quality problem that looks like a model problem.

---

## 16.5 Cost in CI

```yaml
# Budget-capped evaluation in CI
- name: Run evaluation with a hard budget
  run: |
    python -m eval.run \
      --dataset golden.json \
      --max-cost-usd 2.00 \
      --fail-on-budget-exceeded
  env:
    LLM_API_KEY: ${{ secrets.LLM_API_KEY }}

- name: Cost regression gate
  run: python -m eval.compare_cost --baseline baselines/cost.json --max-increase 0.15
```

**Practical controls that keep eval affordable:**
1. **Cache aggressively** — hash the prompt; an unchanged suite should cost nothing to re-run.
2. **Split PR from nightly** — deterministic checks on PR (free), judged eval nightly (paid).
3. **Use a smaller model for the judge** where validation shows acceptable agreement.
4. **Sample** — a 40-case subset on PR, the full 300 nightly.
5. **Hard budget cap in the runner**, so a bug cannot spend a month's budget in an hour.
6. **Report cost in every CI summary** — visibility prevents the surprise that gets eval cancelled.

---

## 16.6 Self-check

1. Why does conversation cost grow superlinearly?
2. What are reasoning tokens and why are they a billing-accuracy risk?
3. Why is cost per resolved task better than cost per request?
4. How can moving one line in a prompt materially cut costs?
5. Why can 25 tool definitions cost more than the user's question?
6. What are the six controls that keep an eval suite affordable in CI?
7. How would you express a denial-of-wallet finding so management acts on it?

---

**Next:** [PART-17-DATA-DATASET-TESTING.md](PART-17-DATA-DATASET-TESTING.md) — golden datasets, synthetic data, drift, and dataset versioning.
