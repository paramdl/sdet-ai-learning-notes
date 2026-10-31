# PART 18 — Model Testing

> **Goal of this part:** answer "which model should we use?" and "is it safe to upgrade?" with evidence rather than opinion. These are two of the most expensive decisions an AI team makes, and they are usually made on vibes and a Twitter benchmark.

---

## 18.1 Public benchmarks — and why they cannot answer your question

You will be shown leaderboards. Know what they are and what they are not.

| Benchmark family | Measures |
|---|---|
| MMLU and successors | Broad multiple-choice knowledge |
| GSM8K / MATH | Mathematical reasoning |
| HumanEval / SWE-bench | Code generation and repair |
| TruthfulQA | Resistance to common misconceptions |
| HELM | Multi-dimensional standardised evaluation |
| Chatbot Arena–style | Human preference via pairwise voting |

**Why they do not settle your decision:**
1. **Contamination.** Benchmark questions leak into training data. A high score may be recall.
2. **Task mismatch.** Nothing in that list resembles "summarise this customer's support history in our house style."
3. **Aggregate scores hide category collapse.** A model can be strong overall and weak at exactly your task.
4. **They ignore your constraints** — latency, cost, data residency, rate limits, context window.
5. **They are marketing surfaces**, and are optimised for as such.

**Use them for shortlisting** (which 3 models to evaluate), never for deciding. The decision belongs to your own eval set, on your own tasks. Saying this clearly in a meeting is a good demonstration of judgement.

---

## 18.2 The model selection framework

```python
SELECTION_CRITERIA = {
    "quality":     {"weight": 0.35, "source": "your eval suite"},
    "cost":        {"weight": 0.20, "source": "cost per resolved task"},
    "latency":     {"weight": 0.15, "source": "p95 TTFT + total"},
    "safety":      {"weight": 0.15, "source": "red-team pass rate"},
    "operational": {"weight": 0.15, "source": "rate limits, SLA, residency, deprecation policy"},
}
```

### The comparison harness
```python
def compare_models(models, golden_set, n=3):
    """Run the SAME dataset, SAME prompts, SAME parameters against every
    candidate. Anything that differs between runs invalidates the
    comparison — this is the most common methodological error."""
    rows = []
    for model in models:
        results = [run_case(model, c, n=n) for c in golden_set]
        rows.append({
            "model": model,
            "quality_mean": mean(r["mean_score"] for r in results),
            "quality_min": min(r["min_score"] for r in results),
            "pass_rate": mean(r["pass_rate"] for r in results),
            "faithfulness": mean(r["faithfulness"] for r in results),
            "instruction_following": mean(r["constraints_met"] for r in results),
            "cost_per_case": mean(r["cost"] for r in results),
            "cost_per_success": (sum(r["cost"] for r in results)
                                 / max(sum(r["passed"] for r in results), 1)),
            "p95_latency_ms": percentile([r["latency"] for r in results], 95),
            "p95_ttft_ms": percentile([r["ttft"] for r in results], 95),
            "refusal_rate": mean(r["refused"] for r in results),
            "variance": mean(r["std"] for r in results),
        })
    return pd.DataFrame(rows)
```

### Report per category, not just in aggregate
```
                    Model A   Model B   Model C
  billing             0.94      0.91      0.72
  technical           0.89      0.90      0.81
  policy              0.92      0.71  ←   0.79
  multilingual        0.68  ←   0.88      0.84
  adversarial         0.97      0.95      0.61  ←
  ───────────────────────────────────────────────
  OVERALL             0.88      0.87      0.75
```
A and B look equivalent overall. They are not: A fails multilingual, B fails policy. **The aggregate hides the only information that matters.** Always produce this table.

---

## 18.3 Model upgrade regression 🔴

**The scenario:** the provider deprecates your model, or releases a better one. This is the highest-risk routine event in an AI product's life, and your eval suite is what makes it safe.

```
MODEL UPGRADE CHECKLIST

□ 1. Run the full golden set against old and new. Compare PER CATEGORY.
□ 2. Run the full security/red-team suite. Alignment differs between
     versions — an injection that failed before may succeed now.
□ 3. Run guardrail corpora. Refusal behaviour is the most commonly
     changed characteristic between model versions.
□ 4. Check structured-output reliability. JSON-mode behaviour changes.
□ 5. Check tool-calling behaviour: selection, argument format, types.
□ 6. Re-measure cost. Pricing and verbosity both change.
□ 7. Re-measure latency and TTFT.
□ 8. Re-measure the determinism baseline (Part 3 §3.4).
□ 9. Re-validate the judge if the judge model also changed.
□ 10. Check parameter support — some parameters are restricted on
      newer models.
□ 11. Re-test prompt-cache behaviour if you rely on it.
□ 12. Plan a rollback: can you revert within one deploy?
```

**Items 2 and 3 are the ones teams skip and regret.** A model upgrade is an *alignment* change as much as a capability change. A prompt tuned to a model's refusal behaviour can break in either direction — new over-refusals blocking real users, or new under-refusals letting content through.

```python
def upgrade_report(old_model, new_model, golden_set, security_set):
    """The artefact that makes an upgrade a decision rather than a hope."""
    old = evaluate_all(old_model, golden_set)
    new = evaluate_all(new_model, golden_set)

    regressions = [
        {"case": c["id"],
         "old": old[c["id"]]["score"],
         "new": new[c["id"]]["score"],
         "delta": new[c["id"]]["score"] - old[c["id"]]["score"]}
        for c in golden_set
        if old[c["id"]]["passed"] and not new[c["id"]]["passed"]
    ]
    return {
        "quality_delta_by_category": category_deltas(old, new),
        "newly_failing": regressions,             # ← the blocking list
        "newly_passing": improvements(old, new),
        "security_delta": security_delta(old_model, new_model, security_set),
        "cost_delta_pct": cost_delta(old, new),
        "latency_delta_pct": latency_delta(old, new),
        "recommendation": "BLOCK" if regressions or security_regressed else "PROCEED",
    }
```

**Deprecation is a scheduled risk you can manage.** ⏳ Providers publish deprecation dates. Put them in the team calendar, and run the upgrade suite against the successor model *before* the deadline rather than during an outage. Being the person who tracks this is a small effort with visible value.

---

## 18.4 Fine-tuned model testing

A fine-tuned model is a **new model**, not a patched one.

| Test | Why |
|---|---|
| **Full baseline regression** | Catastrophic forgetting — improved on the target task, worse elsewhere |
| **Full safety/red-team suite** | Fine-tuning can weaken or strip alignment |
| Training-data memorisation | Prompt for verbatim recall of distinctive training strings |
| PII leakage from training data | Especially if trained on customer data |
| Paraphrase robustness | Evaluate on rephrased versions of training inputs; a large gap means overfitting to phrasing |
| Out-of-distribution behaviour | Inputs unlike anything in training |
| Adapter/version served | Assert the response metadata names the intended version |
| Comparison vs the prompted base model | **Was the fine-tune worth it at all?** Frequently the answer is no |

That last row is the most useful test to run, and the one nobody asks for. A base model with a good prompt often matches a fine-tune that cost weeks of effort. Producing that comparison saves real money and is exactly the kind of finding that gets a QA engineer taken seriously.

---

## 18.5 Open-weight / self-hosted model testing

Additional surface when the org runs its own models:

| Area | Test |
|---|---|
| **Quantization impact** | Same eval, FP16 vs INT8 vs INT4, **per category** (Part 1 §1.17) |
| Serving-engine parity | The same model served by two engines can differ; test the one you deploy |
| Model provenance | Verified source, checksum, licence compatibility |
| **Unsafe formats** | Legacy pickle-based weights can execute code on load; prefer safetensors |
| Prompt-template correctness | Self-hosted models need the correct chat template; a wrong template silently degrades everything |
| Context length actually supported | Advertised vs effective — test at the limit |
| Throughput at target batch size | Capacity planning |
| GPU memory headroom | OOM under concurrency |
| Cold start | Model load time after restart |

**The chat-template bug is the classic self-hosting defect.** Each model family expects a specific format for turn markers. Get it wrong and the model still produces fluent output — just noticeably worse, with no error anywhere. Testing that the served template matches the model card is a five-minute check that saves weeks.

---

## 18.6 Hosted vs self-hosted — the testing trade-off

| | Hosted API | Self-hosted |
|---|---|---|
| Model changes | **Can change under you** — anchor-set drift detection required | You control it |
| Availability | Provider's problem; needs fallback testing | Your problem; needs capacity testing |
| Cost model | Per token | Per GPU-hour — utilisation testing matters |
| Data residency | Contractual; verify | You control it |
| Debugging | Black box | Full visibility |
| Deprecation | **Forced upgrades on their schedule** | Your schedule |
| Rate limits | Provider quotas | Your capacity |

**The anchor-set drift test is essential for hosted models:**
```
TC-MODEL-001  Silent model drift detection
Method:     A frozen set of 30 cases with recorded scores. Run WEEKLY
            against the same model ID with identical parameters.
Expected:   Scores stable within normal variance
Failure:    A sustained shift means the provider changed the model
            behind the alias
Value:      This is the ONLY way to detect a change that nobody
            announced, and it explains otherwise inexplicable
            production regressions
Priority:   High
```

---

## 18.7 The model decision record

Write this down. It is the artefact that stops the decision being relitigated every quarter, and it makes you the person who owns the evidence.

```
MODEL DECISION RECORD — 2026-09-08

Decision:    Model B for production; Model C as fallback
Dataset:     golden-v2.3.0 (120 cases), security-v1.4 (85 attacks)
Method:      3 runs per case, production parameters, judge = different
             family, kappa 0.78

Evidence:
  Quality    B 0.87 vs A 0.88 vs C 0.75   (per-category table attached)
  Weakness   A fails multilingual (0.68); B fails policy (0.71) —
             mitigated by an added policy constraint in prompt v3.3,
             re-tested at 0.89
  Cost       B $0.0024/resolved vs A $0.0089 — 3.7× cheaper
  Latency    B p95 TTFT 480 ms vs A 910 ms
  Security   B 0/85 attacks succeeded; A 1/85; C 4/85
  Fallback   C scores 0.75; product shows a degraded-service banner
             when C is serving

Re-evaluate: on any model deprecation notice, or quarterly, whichever
             is sooner. Anchor set runs weekly.
```

---

## 18.8 Self-check

1. Why can a public benchmark not decide your model choice?
2. Why report per-category scores rather than an aggregate?
3. What two suites do teams skip during a model upgrade, and what breaks?
4. Why is a fine-tuned model treated as a new model?
5. What is the chat-template bug and why is it invisible?
6. How do you detect that a hosted provider changed the model behind an alias?
7. What single comparison most often shows a fine-tune was unnecessary?

---

**Next:** [PART-19-REGRESSION-TESTING.md](PART-19-REGRESSION-TESTING.md) — the seven regression suites and how to build them.
