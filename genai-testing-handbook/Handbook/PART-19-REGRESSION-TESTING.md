# PART 19 — Regression Testing for GenAI

> **Goal of this part:** build the suite that runs forever. Regression testing is where GenAI QA becomes an engineering discipline rather than a series of one-off investigations.

---

## 19.1 What "regression" means when nothing is deterministic

Traditional regression: *the output changed, therefore something broke.* Useless here — the output changes every run.

**GenAI regression: the *distribution* of outcomes got worse.**

```
Baseline (v3.1):   pass_rate 0.94   faithfulness 0.89   cost $0.0021
Candidate (v3.2):  pass_rate 0.81   faithfulness 0.88   cost $0.0034
                          ▲ regression              ▲ regression
```

**Three gate types, and you need all three:**

| Gate | Rule | Use for |
|---|---|---|
| **Hard constraint** | Must be 100% | Schema validity, canary non-leakage, forbidden terms, permission enforcement |
| **Absolute threshold** | Must exceed X | Established metrics with a calibrated floor |
| **Delta gate** | Must not drop more than X from baseline | Everything subjective — **the most defensible gate** |

The delta gate is what makes regression testing survive contact with a team. "Faithfulness must be 0.90" invites argument about whether 0.90 is the right number. "Faithfulness must not drop more than 3 points from last release" is unarguable.

---

## 19.2 What triggers a regression run

| Change | Suites to run |
|---|---|
| **Prompt edit** | Prompt, quality, security, cost |
| **Model change / upgrade** | Everything (Part 18 §18.3) |
| Sampling parameter change | Quality, determinism baseline |
| **RAG corpus change** | Retrieval, RAG quality, data quality, security |
| Chunking / embedding config | Retrieval, cost, reindex validation |
| Tool added or changed | Agent, security (tool inventory), cost |
| Guardrail change | Guardrail corpora — **both directions** |
| App code change | API contract, integration |
| Dependency upgrade | Contract + smoke |
| **Nothing (scheduled)** | Anchor set — detects provider-side drift |

That last row matters: **you need a regression run triggered by nothing at all.** Hosted models change without your involvement, and a weekly scheduled run is the only thing that catches it.

---

## 19.3 The seven regression suites

### 1. Prompt regression
```python
def test_prompt_regression(golden_set, baseline):
    """Runs on every prompt change. The most frequently triggered suite."""
    results = run_suite(golden_set, prompt=CURRENT_PROMPT, n=3)

    # A. Hard constraints — no tolerance.
    assert results["schema_valid_rate"] == 1.0
    assert results["canary_leak_count"] == 0

    # B. Newly failing cases — named, not counted.
    newly_failing = [c for c in golden_set
                     if baseline[c["id"]]["passed"] and not results[c["id"]]["passed"]]
    assert not newly_failing, (
        "Cases that passed on the previous prompt now fail:\n"
        + "\n".join(f"  - {c['id']}: {c['input'][:60]}" for c in newly_failing)
    )

    # C. Aggregate delta.
    delta = results["mean_score"] - baseline["mean_score"]
    assert delta > -0.03, f"Quality dropped {delta:.3f} vs baseline"

    # D. Cost delta (Part 16).
    cost_delta = (results["mean_cost"] - baseline["mean_cost"]) / baseline["mean_cost"]
    assert cost_delta < 0.15, f"Cost rose {cost_delta:.0%}"
```

### 2. Model regression
Part 18 §18.3. Triggered by any model ID or version change, and by the weekly anchor run.

### 3. RAG regression
```python
def test_rag_regression(golden_queries, baseline):
    """Two layers, tested separately — retrieval and generation.
    Testing them together hides which one regressed."""
    retrieval = evaluate_retrieval(retriever, golden_queries, k=5)
    assert retrieval["recall@5"] >= baseline["recall@5"] - 0.03
    assert retrieval["precision@5"] >= baseline["precision@5"] - 0.05

    generation = evaluate_generation(rag, golden_queries)
    assert generation["faithfulness"] >= baseline["faithfulness"] - 0.03
    assert generation["fabricated_citations"] == 0        # hard constraint

    # Corpus health (Part 17)
    assert corpus_duplicate_rate() < 0.02
    assert corpus_null_metadata_count() == 0
```
**Corpus changes need their own trigger.** A document added to the corpus can change answers for unrelated queries by crowding out previously-retrieved chunks. Run retrieval regression on every corpus change, not only on code changes.

### 4. Agent regression
```python
def test_agent_regression(scenarios, baseline):
    results = run_agent_scenarios(scenarios, n=3)
    assert results["task_completion_rate"] >= baseline["completion"] - 0.05
    assert results["unsafe_action_count"] == 0              # hard
    assert results["avg_steps"] <= baseline["avg_steps"] * 1.2   # flailing = cost
    assert results["tool_selection_accuracy"] >= baseline["tool_accuracy"] - 0.05
    assert results["cost_per_task"] <= baseline["cost_per_task"] * 1.15
```

### 5. API regression
Ordinary contract testing (Part 5). Deterministic, fast, free — every PR.

### 6. Security regression 🔴
```python
def test_security_regression(attack_suite):
    """Every previously-fixed vulnerability becomes a permanent test.
    Because fixes are probabilistic, run at N and assert on the RATE."""
    results = run_attacks(attack_suite, n=10)

    assert results["canary_leaks"] == 0
    assert results["permission_bypasses"] == 0
    assert results["cross_user_leaks"] == 0

    for attack in attack_suite:
        rate = results[attack["id"]]["success_rate"]
        assert rate <= attack["max_acceptable_rate"], (
            f"{attack['id']} succeeded {rate:.0%} of the time "
            f"(max {attack['max_acceptable_rate']:.0%})"
        )
```
**The discipline:** every security finding, once fixed, is added to this suite permanently, with its own acceptable rate. A fix that reduces injection success from 80% to 5% is real progress and should be recorded as 5%, not as "fixed" — because a later prompt change can undo it silently.

### 7. Performance regression
```python
def test_performance_regression(baseline):
    perf = run_perf_smoke(n=50)
    assert perf["ttft_p95"] <= baseline["ttft_p95"] * 1.2
    assert perf["total_p95"] <= baseline["total_p95"] * 1.2
    assert perf["error_rate"] <= 0.01
```

---

## 19.4 Baseline management

```
baselines/
├── quality/golden-v2.3.0__prompt-v3.1__model-B.json
├── retrieval/golden-v2.3.0__embed-v3__chunk-800-200.json
├── security/attacks-v1.4__prompt-v3.1.json
├── cost/golden-v2.3.0__prompt-v3.1__model-B.json
└── performance/perf-smoke__2026-09.json
```

**The naming convention is the point.** A baseline is only valid for a specific *combination* of dataset, prompt, and model. Comparing against a baseline generated with a different prompt is meaningless, and the filename makes that mistake visible.

**Rules:**
| Rule | Why |
|---|---|
| Baselines are committed to Git | Reviewable, revertable |
| **Updating a baseline is a reviewed PR** | Prevents "make the test pass by moving the goalposts" |
| The PR must state *why* the baseline moved | Improvement, or an accepted regression with a reason |
| Regenerate on any config change | Stale baselines produce false alarms and get ignored |
| Keep the last N baselines | Trend analysis |

**The single most important process control in this part:** a developer must not be able to update a baseline in the same commit as the change that moved it. That is the GenAI equivalent of editing the assertion to match the bug.

---

## 19.5 Flakiness — telling real regressions from variance

```python
def is_real_regression(case_id, baseline, candidate, n=20, alpha=0.05):
    """Distinguish a genuine regression from normal run-to-run variance.

    If the candidate's pass-rate confidence interval overlaps the
    baseline's, you cannot claim a regression from this evidence.
    Saying so honestly is better than crying wolf — a suite that
    cries wolf gets ignored, and then it protects nothing."""
    base = [run(case_id, version="baseline") for _ in range(n)]
    cand = [run(case_id, version="candidate") for _ in range(n)]

    base_rate = sum(base) / n
    cand_rate = sum(cand) / n
    ci = 1.96 * math.sqrt(base_rate * (1 - base_rate) / n)   # normal approx

    return {
        "baseline_rate": base_rate,
        "candidate_rate": cand_rate,
        "confidence_interval": (base_rate - ci, base_rate + ci),
        "verdict": "REGRESSION" if cand_rate < base_rate - ci else "WITHIN VARIANCE",
    }
```

**The escalation ladder for a red build:**
1. Re-run the failing case at N=20 — is it a real rate change or a single unlucky sample?
2. Compare against the baseline's own confidence interval.
3. If real, bisect: prompt, model, corpus, or code?
4. If not real, the failing case has a threshold that is too tight — fix the *threshold*, in a reviewed PR, with a reason.

---

## 19.6 The regression run cadence

| Suite | Trigger | Duration | Cost |
|---|---|---|---|
| API contract | Every PR | < 1 min | free (mocked) |
| Deterministic prompt checks | Every PR | < 2 min | ~free |
| Quality smoke (40 cases × 1) | Every PR | ~3 min | low |
| Security fast (canaries, permissions) | Every PR | ~2 min | low |
| **Full quality (all × 3)** | Nightly | ~20 min | medium |
| Full retrieval | Nightly | ~5 min | low |
| Full security | Nightly | ~15 min | medium |
| Agent scenarios | Nightly | ~20 min | medium |
| Performance smoke | Nightly | ~10 min | medium |
| **Anchor set (drift)** | Weekly, scheduled | ~5 min | low |
| Full performance / load | Pre-release | ~1 h | high |
| Model upgrade suite | On model change | ~2 h | high |

---

## 19.7 Self-check

1. Why is a delta gate more defensible than an absolute threshold?
2. Why do you need a regression run triggered by no change at all?
3. Why must retrieval and generation regression be measured separately?
4. Why record a fixed vulnerability's *rate* rather than marking it fixed?
5. Why must a baseline update be a separate reviewed PR?
6. How do you tell a real regression from variance?
7. What does the baseline filename convention protect against?

---

**Next:** [PART-20-CICD.md](PART-20-CICD.md) — wiring all of this into a pipeline that a team will actually keep switched on.
