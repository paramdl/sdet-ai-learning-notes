# PART 6 — LLM Evaluation

> **Goal of this part:** be able to design an evaluation from scratch — choose metrics, build the dataset, set thresholds, validate your judge, and defend every number in a release meeting. This is the core competency that distinguishes an AI Quality Engineer from a QA engineer who happens to test an AI feature.

---

## 6.1 The mental model

> **Imagine this…** You are marking 200 student essays. You cannot say "correct" or "incorrect" — essays are not multiple choice. So you build a **rubric** (structure 0–5, evidence 0–5, clarity 0–5), you mark against it consistently, you compute averages, and you compare this year's class to last year's. If someone questions your marking, you show the rubric and the distribution.
>
> LLM evaluation is exactly that, with the marking automated.

**The four components of every evaluation:**

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  ① DATASET   │ → │  ② RUNNER    │ → │  ③ METRICS   │ → │  ④ THRESHOLD │
│  inputs +    │   │  calls the   │   │  score each  │   │  pass/fail   │
│  expectations│   │  system N×   │   │  output      │   │  gate        │
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
```

Get ① wrong and nothing else matters. **Most failed eval programmes fail at the dataset**, not the metric.

---

## 6.2 The evaluation taxonomy

### By what you compare against

| Approach | You have | Use when | Cost |
|---|---|---|---|
| **Reference-based** | A known correct answer | Extraction, classification, translation, closed-book QA | Low |
| **Reference-free** | Only criteria | Open-ended generation: chat, summaries, creative | Higher (needs a judge) |
| **Pairwise** | Two outputs to compare | Model/prompt A-vs-B decisions | Medium |

**Pairwise is under-used and more reliable than people expect.** Humans and LLM judges are both far better at "which of these two is better?" than at "score this from 1 to 10". When you need to choose between two models or two prompts, prefer pairwise. When you need a trend line over time, you need absolute scores.

### By who judges

| Judge | Accuracy | Cost | Speed | Scale |
|---|---|---|---|---|
| **Deterministic code** | Perfect for what it measures | ~0 | ms | Unlimited |
| **Embedding similarity** | Good for semantic match | Very low | ms | Very high |
| **LLM-as-judge** | Good, with caveats | Medium | seconds | High |
| **Human** | The ground truth | Very high | minutes | Low |

**The strategy that actually works in production:**

```
       ┌─────────────────────────┐
       │  HUMAN (20–50 cases)    │  ← calibrates & validates the judge
       ├─────────────────────────┤
       │  LLM-JUDGE (100s)       │  ← nightly, for subjective quality
       ├─────────────────────────┤
       │  EMBEDDING (1000s)      │  ← semantic regression, cheap
       ├─────────────────────────┤
       │  DETERMINISTIC (all)    │  ← every PR, free, fast
       └─────────────────────────┘
```
Push every check as far down this pyramid as it will go. If a requirement can be expressed as a regex or a schema, **never** spend a judge call on it. Teams that put everything through an LLM judge get slow, expensive, noisy suites and eventually abandon them.

---

## 6.3 Deterministic metrics

### Exact match
```python
score = 1.0 if output.strip() == expected.strip() else 0.0
```
**Use for:** classification labels, extracted IDs, enum values, yes/no answers.
**Never use for:** any free-text generation.

**Example.** Extracting an invoice number. Expected `INV-4471`. Output `INV-4471` → 1.0. Output `The invoice number is INV-4471` → 0.0, which is why you normalise first, or use a regex.

### Normalised / fuzzy match
```python
import re
def normalise(s: str) -> str:
    """Strip the differences you don't care about, before comparing."""
    s = s.lower().strip()
    s = re.sub(r"[^\w\s]", "", s)      # punctuation
    s = re.sub(r"\s+", " ", s)         # whitespace
    return s

score = 1.0 if normalise(output) == normalise(expected) else 0.0
```
**Document what you normalise away.** If you strip punctuation, you can no longer detect a missing decimal point — which matters for numeric answers.

### Contains / regex
```python
# "Must mention the escalation path"
assert re.search(r"\b(escalat\w+|transfer\w* you|human agent)\b", output, re.I)
```
**Use for:** required elements, forbidden terms, format markers, refusal detection.
**Limitation:** brittle to paraphrase. Maintain the alternatives list, or move up to embedding similarity.

### JSON validity and schema conformance
```python
from pydantic import ValidationError

def json_schema_score(output: str, model_cls) -> tuple[float, str]:
    """Returns (score, reason). Reason is what makes the failure actionable."""
    try:
        model_cls.model_validate_json(output)
        return 1.0, "valid"
    except ValidationError as e:
        return 0.0, str(e.errors()[0])   # names the exact failing field
    except Exception as e:
        return 0.0, f"not JSON: {e}"
```
**This is the highest value-per-effort metric in the book** for any structured-output feature. Run it on every case, every run, forever.

### Length, format, and structural constraints
```python
def structural_checks(output: str) -> dict[str, bool]:
    return {
        "under_3_sentences": len([s for s in re.split(r"(?<=[.!?])\s+", output.strip()) if s]) <= 3,
        "no_markdown_headers": not output.lstrip().startswith("#"),
        "has_citation": bool(re.search(r"\[\d+\]|\(source:", output)),
        "no_forbidden_terms": not any(t in output.lower() for t in FORBIDDEN),
        "not_empty": len(output.strip()) > 0,
        "no_placeholder": "[INSERT" not in output.upper(),   # catches template leakage
    }
```

### Refusal detection
```python
REFUSAL_MARKERS = [
    "i can't", "i cannot", "i'm not able", "i am unable",
    "i won't", "as an ai", "i'm sorry, but", "against my guidelines",
]
def is_refusal(output: str) -> bool:
    head = output.lower()[:200]        # refusals appear early
    return any(m in head for m in REFUSAL_MARKERS)
```
You need this in **two opposite directions**: refusal *required* for unsafe input, and refusal *forbidden* for legitimate input (over-refusal, Part 13). Same function, opposite assertion.

---

## 6.4 Semantic metrics

### Embedding / cosine similarity 🔴
The workhorse. Replaces exact match for free text.

```python
import numpy as np

def cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity: 1.0 = identical direction, 0 = unrelated.
    Normalising first makes this just a dot product."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def semantic_score(output: str, reference: str, embed) -> float:
    return cosine(embed(output), embed(reference))
```

**Worked example.**
| Reference | Output | Cosine | Verdict |
|---|---|---|---|
| "Go to Account Settings to reset your password." | "You can reset it in Account Settings." | 0.93 | Pass |
| | "Visit the settings page and choose reset." | 0.87 | Pass |
| | "Contact support for help." | 0.52 | Fail |
| | "You cannot reset your password." | 0.71 | **Fail — but only just.** Note how weakly embeddings handle negation |

That last row is the caution: **cosine similarity is not a correctness metric.** An answer that means the *opposite* can still score 0.7. Pair it with a targeted negation or polarity check on anything where correctness inverts.

### Calibrating the threshold 🔴
Never pick 0.85 because a blog post said so. Do this once per project:

```python
def calibrate_threshold(pairs_good, pairs_bad, embed):
    """pairs_good: (output, reference) you judge acceptable.
       pairs_bad:  (output, reference) you judge unacceptable.
    Returns the threshold that best separates them, plus the overlap —
    which tells you whether this metric works at all for your task."""
    good = np.array([semantic_score(o, r, embed) for o, r in pairs_good])
    bad  = np.array([semantic_score(o, r, embed) for o, r in pairs_bad])

    best_t, best_acc = 0.5, 0.0
    for t in np.arange(0.5, 0.99, 0.01):
        acc = ((good >= t).sum() + (bad < t).sum()) / (len(good) + len(bad))
        if acc > best_acc:
            best_t, best_acc = float(t), float(acc)

    return {
        "threshold": round(best_t, 2),
        "separation_accuracy": round(best_acc, 3),
        "good_mean": round(good.mean(), 3), "good_min": round(good.min(), 3),
        "bad_mean":  round(bad.mean(), 3),  "bad_max":  round(bad.max(), 3),
        "overlap": round(max(0.0, float(bad.max() - good.min())), 3),
    }
```
If `separation_accuracy` is below ~0.85 or `overlap` is large, **embedding similarity is the wrong metric for this task** — move up to a judge. Knowing when a metric does not work is as valuable as computing it.

### BLEU / ROUGE / METEOR 🟡
Covered in Part 1 §1.5. Use as cheap regression tripwires for translation and summarisation, never as quality gates.

### BERTScore 🟡
Token-level embedding similarity; more robust than ROUGE, more expensive. Worth knowing by name; rarely the right tool when you already have sentence embeddings and a judge.

---

## 6.5 LLM-as-judge 🔴

> **Imagine this…** You hire a second marker to grade the essays. They are fast, cheap, tireless, and mostly agree with you — but they have quirks: they favour longer essays, they prefer the first one they read, and they are unusually kind to essays written in their own style. You would not fire them; you would **calibrate against them and correct for the quirks.** That is judge validation.

### The three judge patterns

**① Rubric / criteria scoring (absolute)**
```python
JUDGE_PROMPT = """You are evaluating a customer support reply.

CRITERIA:
1. Accuracy — does it correctly answer using only the given context?
2. Policy — does it avoid promising refunds or inventing policy?
3. Escalation — if the context lacks the answer, does it offer escalation?

CONTEXT:
{context}

CUSTOMER QUESTION:
{question}

REPLY TO EVALUATE:
{output}

Score each criterion 1-5. Then give an overall PASS or FAIL.
Respond ONLY as JSON:
{{"accuracy": int, "policy": int, "escalation": int,
  "verdict": "PASS"|"FAIL", "reason": "one sentence"}}"""
```

**Design rules that materially change judge reliability:**
1. **Ask for structured output.** Free-text judgements are unparseable and unaggregatable.
2. **Require a reason.** It makes failures debuggable, and it improves the score's quality.
3. **Use a small scale.** 1–5 is more reliable than 1–100. Binary PASS/FAIL is most reliable of all.
4. **Define each point on the scale** if you use numbers, or the judge invents its own calibration per call.
5. **One rubric per concern.** A judge asked to weigh accuracy, tone, and length at once produces mush. Run three cheap judges instead of one confused one.
6. **Give the judge the context.** A judge without the retrieved documents cannot assess faithfulness — it will guess, and it will guess confidently.

**② Pairwise comparison (relative)**
```python
PAIRWISE_PROMPT = """Which reply better answers the question, given the context?

QUESTION: {question}
CONTEXT: {context}
REPLY A: {a}
REPLY B: {b}

Answer ONLY as JSON: {{"winner": "A"|"B"|"TIE", "reason": "one sentence"}}"""
```
**Mandatory:** run every pair **twice with the order swapped**, and discard pairs where the winner flips. That flip rate *is* your position-bias measurement. A judge with a 30% flip rate is telling you it cannot distinguish these outputs — which is itself a finding.

```python
def pairwise_robust(judge, question, context, a, b):
    """Order-swapped pairwise. Returns a winner only if the judge agrees
    with itself. Otherwise TIE — which is honest, not a failure."""
    r1 = judge(question, context, a, b)["winner"]
    r2 = judge(question, context, b, a)["winner"]
    flip = {"A": "B", "B": "A", "TIE": "TIE"}
    return r1 if r1 == flip[r2] else "TIE"
```

**③ Reference-guided judging**
Give the judge a gold answer as well as the output. Substantially more reliable than reference-free, when you have gold answers. Use it whenever you can.

### Judge biases you must control for 🔴

| Bias | What happens | Control |
|---|---|---|
| **Position bias** | Prefers whichever came first (or last) | Swap order, run twice |
| **Verbosity bias** | Prefers longer answers regardless of quality | Include length in the rubric; check score-vs-length correlation |
| **Self-preference** | A model rates its own family's output higher | **Use a different model family as judge than the one under test** |
| **Formatting bias** | Prefers markdown, bullets, confident tone | Normalise formatting before judging, or score it separately |
| **Leniency drift** | Scores creep over time as prompts evolve | Keep a frozen "anchor set" with known scores; re-run it every time |
| **Sycophancy to the prompt** | Wording like "this excellent answer" inflates scores | Neutral rubric language only |

**Self-preference is the one people miss.** If your product runs on model family X and your judge is also family X, your evaluation systematically flatters your product. Cross-family judging is a cheap fix and a strong point to raise in a design review.

### Judge validation — the step that makes evaluation credible 🔴

**This is the difference between a real evaluation programme and theatre.** An unvalidated judge is an opinion generator.

```python
from sklearn.metrics import cohen_kappa_score   # or compute agreement by hand

def validate_judge(cases, human_labels, judge_fn):
    """Run the judge against cases YOU have already labelled by hand.

    - agreement: raw % match. Easy to read, but inflated when classes
      are imbalanced (95% of cases pass → 95% agreement by always saying PASS).
    - kappa: agreement corrected for chance. This is the number to report.
    """
    judge_labels = [judge_fn(c)["verdict"] for c in cases]
    agreement = sum(j == h for j, h in zip(judge_labels, human_labels)) / len(cases)
    kappa = cohen_kappa_score(human_labels, judge_labels)

    disagreements = [
        {"case": c, "human": h, "judge": j}
        for c, h, j in zip(cases, human_labels, judge_labels) if h != j
    ]
    return {"agreement": round(agreement, 3),
            "cohens_kappa": round(kappa, 3),
            "n": len(cases),
            "disagreements": disagreements}    # ← read these; they fix the rubric
```

**The procedure:**
1. Hand-label 30–50 outputs yourself, honestly, before seeing the judge's answers.
2. Run the judge on the same cases.
3. Compute agreement and Cohen's kappa.
4. **Read every disagreement.** Usually the rubric is ambiguous, not the judge.
5. Revise the rubric. Repeat.
6. Publish the final agreement number **next to every score the judge produces**.

**Interpretation of kappa** (the conventional reading):

| Kappa | Meaning | Action |
|---|---|---|
| < 0.40 | Poor | Do not use this judge. Fix the rubric or change approach |
| 0.40–0.60 | Moderate | Usable for trends only; never for release gates |
| 0.60–0.80 | Substantial | Good enough for gating with human spot-checks |
| > 0.80 | Excellent | Trustworthy |

When you report "quality is 87%", the follow-up question from any competent stakeholder is *"according to whom?"* The answer — "an LLM judge with kappa 0.74 against my labels on 40 cases" — is what makes the number mean anything. **Nobody else in the room will have this.**

### Cost control for judging
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=10_000)
def _cached_judge(key: str, prompt: str) -> str:
    return call_judge(prompt)

def judge(output: str, context: str, question: str) -> dict:
    """Cache on a hash of the inputs. Re-running an unchanged suite
    should cost nothing. This alone makes nightly evals affordable."""
    prompt = JUDGE_PROMPT.format(output=output, context=context, question=question)
    key = hashlib.sha256(prompt.encode()).hexdigest()
    return json.loads(_cached_judge(key, prompt))
```

---

## 6.6 The metric catalogue — every metric, defined with an example

### Classification metrics (for discriminative tasks and for guardrails)

Set-up: 100 support tickets, classify as `billing` or `technical`. 30 are truly billing.

|  | Predicted billing | Predicted technical |
|---|---|---|
| **Actually billing** | TP = 24 | FN = 6 |
| **Actually technical** | FP = 10 | TN = 60 |

| Metric | Formula | Value | Plain meaning | When it is the right metric |
|---|---|---|---|---|
| **Accuracy** | (TP+TN)/all | 84% | Fraction correct overall | Only when classes are balanced. **Misleading otherwise** |
| **Precision** | TP/(TP+FP) | 24/34 = 71% | When it says billing, how often is it right? | When false positives are costly (a guardrail blocking legitimate users) |
| **Recall** | TP/(TP+FN) | 24/30 = 80% | Of all real billing tickets, how many did it catch? | When false negatives are costly (a guardrail missing harmful content) |
| **F1** | 2·P·R/(P+R) | 75% | Harmonic mean; punishes imbalance between the two | Single-number summary when both matter |

**The GenAI application of this table is guardrail testing.** A content filter has exactly this structure:
- **Recall** = how much harmful content it catches. Low recall = safety incident.
- **Precision** = how much of what it blocks is genuinely harmful. Low precision = **over-refusal**, blocking real users.

Report both, always. A team reporting only recall is hiding an over-refusal problem; a team reporting only accuracy is hiding both.

### Generation metrics

| Metric | Question it answers | How it is computed | Failure it detects |
|---|---|---|---|
| **Relevance** | Does the answer address the question asked? | Judge or embedding(answer, question) | Model answers a *different* question — extremely common with RAG |
| **Faithfulness / Groundedness** | Is every claim supported by the provided context? | Decompose the answer into claims; verify each against context (judge) | **Hallucination.** The single most important RAG metric |
| **Answer correctness** | Is it factually right vs a gold answer? | Judge with reference, or exact/semantic match | Wrong answers that are well-grounded in wrong context |
| **Completeness** | Does it cover everything it should? | Judge against a checklist of required elements | Partial answers that pass a similarity check |
| **Coherence** | Is it internally consistent and readable? | Judge rubric | Rambling, contradictory output |
| **Instruction following** | Did it obey every stated constraint? | Per-constraint deterministic checks | The conflict table from Part 4 §4.3 |
| **Citation correctness** | Do the cited sources exist and support the claim? | Verify each citation ID exists **and** that its text supports the sentence | **Fabricated citations** — high severity, easy to detect, rarely tested |
| **Tone / persona** | Does it match the intended voice? | Judge rubric or a style classifier | Persona drift over long chats |
| **Toxicity** | Does it contain harmful language? | Classifier model or judge | Safety incident |
| **Bias** | Does it treat demographic groups differently? | Counterfactual pairs (Part 13) | Fairness incident |

### Faithfulness, worked in full

This is the metric you will implement most often, so here it is end to end.

```python
CLAIM_EXTRACT = """Break the following answer into atomic factual claims.
Return a JSON list of strings. Exclude opinions, greetings, and hedges.

ANSWER: {answer}"""

CLAIM_VERIFY = """Does the CONTEXT support the CLAIM?
Answer ONLY as JSON: {{"supported": true|false, "reason": "..."}}

CONTEXT: {context}
CLAIM: {claim}"""

def faithfulness(answer: str, context: str, judge) -> dict:
    """Faithfulness = supported claims / total claims.

    Decomposing into claims is what makes this actionable: instead of
    'the answer is 0.6 faithful', you get 'these two specific sentences
    are unsupported' — which is a bug report a developer can act on."""
    claims = json.loads(judge(CLAIM_EXTRACT.format(answer=answer)))
    if not claims:
        return {"score": 1.0, "claims": [], "unsupported": []}

    results = [
        (c, json.loads(judge(CLAIM_VERIFY.format(context=context, claim=c))))
        for c in claims
    ]
    unsupported = [{"claim": c, "reason": r["reason"]}
                   for c, r in results if not r["supported"]]
    return {
        "score": 1 - len(unsupported) / len(claims),
        "n_claims": len(claims),
        "unsupported": unsupported,
    }
```

**Worked example.**
> **Context:** "Refunds are available within 14 days of purchase. Contact support to request one."
> **Answer:** "You can request a refund within 14 days. Refunds are processed in 3–5 business days and there is a 10% restocking fee."
>
> Claims: ① refund window is 14 days → **supported**. ② processed in 3–5 business days → **unsupported**. ③ 10% restocking fee → **unsupported**.
> **Faithfulness = 1/3 = 0.33.**

Note that the answer *sounds* authoritative and specific, which is exactly why hallucination is dangerous, and exactly why claim-level decomposition beats a single holistic judgement.

---

## 6.7 Thresholds, sampling, and honest reporting

### N-run sampling
```python
def pass_rate(system, case, n=5) -> dict:
    """The GenAI-native assertion. One run tells you almost nothing."""
    results = [evaluate(system(case["input"]), case) for _ in range(n)]
    passes = sum(r["passed"] for r in results)
    scores = [r["score"] for r in results]
    return {
        "pass_rate": passes / n,
        "mean_score": sum(scores) / n,
        "min_score": min(scores),        # the worst a user could see
        "std": statistics.pstdev(scores) if n > 1 else 0.0,
        "runs": results,                 # keep them: needed to debug failures
    }
```

**How to choose N.** N=1 for deterministic checks. N=3 for CI gates on a budget. N=5–10 for release decisions. N=20 for establishing a baseline or investigating a specific flaky case. Cost scales linearly with N, so spend it where variance actually matters.

### Setting thresholds without arguments
1. **Measure the baseline first.** Run the current system on the dataset. That score is your floor.
2. **Gate on delta, not absolute.** "No more than a 3-point drop from the previous release" is objective. "Must score 90" is a negotiation.
3. **Separate hard from soft.** Hard constraints (schema valid, no forbidden term, no canary leak) must be 100%. Soft quality gets a threshold.
4. **Write down the flake budget.** "We accept a 5% failure rate at N=5" — agreed in advance, in writing, before the first red build.

### Reporting: what a good eval report contains

```
EVAL RUN 2026-09-08 14:22  ·  prompt v3.2  ·  model llama3.1:8b  ·  temp 0.3

  DATASET      120 cases × 5 runs = 600 generations
  JUDGE        different-family model, kappa 0.78 vs 40 human labels

  HARD CONSTRAINTS                     must be 100%
    schema valid                        600/600   100%   ✅
    no canary leak                      600/600   100%   ✅
    no forbidden terms                  598/600    99.7%  ❌  2 failures
                                        → cases: refund-edge-01 (2 runs)

  QUALITY                              threshold   result   Δ vs v3.1
    faithfulness                          ≥0.85     0.91     +0.02  ✅
    answer relevancy                      ≥0.80     0.84     −0.01  ✅
    instruction following                 ≥0.90     0.87     −0.06  ❌
        └ "≤3 sentences" satisfied 71% of runs   ← the actual problem

  COST         $0.42 total  ·  $0.0007/case
  LATENCY      p50 820 ms · p95 2 140 ms · TTFT p95 410 ms

  VERDICT      BLOCK — instruction following regressed below threshold.
               Root cause: v3.2 added "explain your reasoning", which
               conflicts with the existing 3-sentence limit.
```

Three things make this report good, and all three are learnable habits: hard and soft constraints are separated; every score carries a **delta**; and the verdict names a **cause**, not just a number. A report that says "quality score 0.87" gives a product manager nothing to decide with.

---

## 6.8 Doing this with tools

### promptfoo — fastest to a result
```yaml
tests:
  - vars: {question: "What is the refund window?"}
    assert:
      - {type: contains, value: "14 days"}                    # deterministic
      - {type: similar, value: "Refunds within 14 days", threshold: 0.85}
      - {type: llm-rubric, value: "States the 14-day window and does not invent extra policy"}
      - {type: javascript, value: "output.length < 400"}
```
```bash
npx promptfoo@latest eval --repeat 5 && npx promptfoo@latest view
```

### DeepEval — evaluation as pytest ⏳
```python
from deepeval import assert_test
from deepeval.metrics import GEval, AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

def test_support_reply(llm):
    case = LLMTestCase(
        input="What is the refund window?",
        actual_output=ask(llm, "What is the refund window?"),
        retrieval_context=["Refunds are available within 14 days of purchase."],
    )
    assert_test(case, [
        FaithfulnessMetric(threshold=0.85),
        AnswerRelevancyMetric(threshold=0.80),
        GEval(
            name="PolicyCompliance",
            criteria="The reply must not promise a refund amount or invent policy.",
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            threshold=0.8,
        ),
    ])
```
⏳ DeepEval's metric catalogue and API surface move quickly, and a TypeScript SDK now exists alongside Python. Check the current docs for exact class names before copying older tutorials.

### Ragas — RAG metrics (Part 7)
### Custom — when tools do not fit
Do not force your domain into a framework's metric names. A hand-written metric that measures the thing your product actually cares about beats a borrowed one that nearly does.

---

## 6.9 Common evaluation mistakes

| Mistake | Why it is wrong | Fix |
|---|---|---|
| Judge is the same model as the system | Self-preference bias | Different family |
| Judge never validated against humans | The number is unfounded | Kappa on 30–50 hand labels |
| Threshold chosen by intuition | Unfalsifiable; endless argument | Calibrate on labelled good/bad pairs |
| One run per case | Ignores variance entirely | N≥3, report pass-rate |
| Everything goes through the judge | Slow, expensive, noisy | Push checks down the pyramid |
| Only aggregate scores reported | Hides a collapse in one category | Report per-category |
| Golden set built from happy paths | Passes forever, catches nothing | Seed it from production failures |
| Eval set leaks into prompt development | You are marking your own homework | Hold out a set you never look at while iterating |
| Metrics without deltas | No signal about change | Always compare to the previous baseline |
| No cost reported | Eval gets cancelled when the bill lands | Report cost per run |

The **held-out set** point deserves emphasis. If you tune the prompt until the eval passes, the eval no longer measures quality — it measures how hard you tuned. Keep 20% of the dataset sealed, run it only at release, and treat a gap between the two sets as evidence of overfitting to your own tests.

---

## 6.10 Self-check

1. Why is pairwise comparison more reliable than absolute scoring, and what does it cost you?
2. What is Cohen's kappa, and why report it rather than raw agreement?
3. Name three judge biases and the control for each.
4. Why must the judge see the retrieved context when scoring faithfulness?
5. Why decompose an answer into claims rather than judging faithfulness holistically?
6. A guardrail reports 96% accuracy. What two numbers do you ask for instead?
7. How do you set a quality threshold that a product manager cannot argue with?
8. What is a held-out set, and what does a gap between it and your dev set mean?

---

**Next:** [PART-07-RAG-TESTING.md](PART-07-RAG-TESTING.md) — the RAG pipeline, stage by stage, with retrieval metrics and a complete test strategy.
