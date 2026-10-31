# PART 17 — Data & Dataset Testing

> **Goal of this part:** build and maintain the datasets everything else depends on. In GenAI testing, **the dataset is the test suite.** A mediocre metric on an excellent dataset beats an excellent metric on a bad one, every time.

---

## 17.1 The dataset types

| Type | Contents | Used for |
|---|---|---|
| **Golden / evaluation set** | Inputs + expected behaviour + acceptance criteria | The core eval suite |
| **Ground truth** | Inputs + verified correct answers | Reference-based metrics |
| **Retrieval golden set** | Queries + labelled relevant document IDs | RAG retrieval metrics (Part 7) |
| **Adversarial set** | Attack payloads + expected refusals | Security regression |
| **Guardrail corpora** | Allowed / blocked / borderline / adversarial | Guardrail testing (Part 13) |
| **Held-out set** | Never seen during development | Overfitting detection |
| **Anchor set** | Frozen cases with known scores | Judge drift detection |
| **Production sample** | Real traffic, labelled | The most valuable of all |

---

## 17.2 Building a golden dataset

### The specification
```json
{
  "id": "billing-refund-window-001",
  "input": "How long do I have to request a refund on an annual plan?",
  "expected_behaviour": {
    "must_contain": ["30 days"],
    "must_not_contain": ["guarantee", "automatically approved"],
    "must_cite": true,
    "max_sentences": 3,
    "should_escalate": false
  },
  "gold_answer": "Annual plans can be refunded within 30 days of purchase.",
  "relevant_doc_ids": ["policy-refunds#s2"],
  "category": "billing",
  "difficulty": "easy",
  "source": "production_log_2026_07",
  "added": "2026-07-14",
  "author": "qa",
  "notes": "Added after INC-233: bot quoted the monthly window for annual plans."
}
```

**Every field earns its place.** `source` and `notes` are what stop a dataset decaying into a set of cases nobody remembers the reason for. When a case fails two years from now, `notes` tells the next engineer whether it matters.

### Composition — the distribution that finds bugs

A dataset drawn only from documentation tests the documentation. Aim for roughly:

| Slice | Share | Why |
|---|---|---|
| Common happy paths | 30% | The bulk of traffic |
| Edge cases | 20% | Boundaries, unusual phrasing |
| **Unanswerable** | 15% | Does it abstain? The most under-represented slice |
| Ambiguous | 10% | Does it clarify rather than guess? |
| Adversarial / injection | 10% | Security regression |
| Multilingual | 10% | If you serve multiple languages |
| Known past failures | 5% | Regression protection for real incidents |

### Sizing
| Size | Use |
|---|---|
| 20–30 | Smoke suite for PRs |
| 50–100 | Meaningful signal; a good starting point |
| 200–500 | Mature product; per-category confidence |
| 1000+ | Only if you can afford to run it and keep it curated |

**Bigger is not better past the point where you stop maintaining it.** A curated 100-case set that everyone trusts beats a stale 2,000-case set that half the team ignores because it is always partly red.

---

## 17.3 Synthetic test data generation

Useful for bulk, dangerous unsupervised.

```python
GENERATE_PROMPT = """Given this document, write {n} questions a real
customer might ask that this document answers.

Vary: phrasing, formality, length, and specificity. Include at least
two questions phrased the way a frustrated or confused customer would
write them — with typos, incomplete sentences, or missing context.

DOCUMENT: {doc}

Return JSON: [{{"question": str, "answerable": true}}]"""

NEGATIVE_PROMPT = """Given this document, write {n} questions that are
ADJACENT to its topic but which it does NOT answer. These should be
plausible questions a customer might ask that require information not
present here.

DOCUMENT: {doc}

Return JSON: [{{"question": str, "answerable": false}}]"""
```

**The negative generator is the more valuable of the two.** Adjacent-but-unanswerable questions are the hardest cases for a RAG system and the ones humans rarely think to write.

### The rules for synthetic data 🔴

| Rule | Why |
|---|---|
| **A human verifies every case before it enters the golden set** | Unverified synthetic data tests the generator's imagination |
| Never use the system under test as the generator | You will bake its blind spots into your dataset |
| Never let a generated *answer* become ground truth unverified | You will certify hallucinations as correct |
| Record that a case is synthetic | So you can measure whether synthetic cases behave differently from real ones |
| Use synthetic data for *volume*, real data for *validity* | Different jobs |

**The failure mode to name in a review:** a team generates 500 questions with model X, answers them with model X, and evaluates model X against those answers. The score is high and means nothing. It is a closed loop.

### Legitimate uses of synthetic data
- Bulk adversarial variants (paraphrasing a known attack 50 ways)
- Multilingual expansion of an English set (with native-speaker review)
- Load-test prompt corpora (no ground truth needed)
- Negative/unanswerable cases
- PII test fixtures (never use real PII in test data)

---

## 17.4 Data quality testing

For the **RAG corpus** and any **fine-tuning dataset**:

| Check | SQL / method | Threshold |
|---|---|---|
| **Duplicates** | Exact hash, then near-duplicate by embedding | < 2% |
| Missing required fields | `WHERE field IS NULL` | 0 |
| **Contradictions** | Retrieve pairs on the same topic; judge for conflict | Flag all |
| Stale content | `WHERE updated_at < now() - interval '2 years'` | Reviewed |
| **PII in the corpus** | Detector scan | 0, or documented and access-controlled |
| Encoding damage | Search for `�` and mojibake patterns | 0 |
| Empty / near-empty chunks | `WHERE length(chunk_text) < 50` | Reviewed |
| Boilerplate dominance | Frequency of repeated headers/footers | < 10% of tokens |
| Language mislabelling | Detect language; compare to metadata | 0 mismatches |
| Orphaned chunks | Chunk whose source document was deleted | 0 |
| Broken links/citations | Resolve every referenced ID | 0 broken |

**Contradiction detection is the highest-value and least-performed check.** Two documents stating different refund windows guarantee that the system is wrong for someone, and no amount of model or prompt work fixes it. Finding contradictions is a *data* finding that saves weeks of misdirected debugging.

```python
def find_contradictions(corpus, topics, retriever, judge):
    """For each topic, retrieve the top chunks and ask a judge whether
    any pair conflicts. Expensive, but run it once per corpus refresh —
    it finds problems no amount of prompt tuning can fix."""
    conflicts = []
    for topic in topics:
        chunks = retriever.search(topic, k=8)
        for a, b in itertools.combinations(chunks, 2):
            v = judge(f"Do these two passages state CONFLICTING facts?\n"
                      f"A: {a.text}\nB: {b.text}\n"
                      f'JSON: {{"conflict": true|false, "detail": "..."}}')
            if json.loads(v)["conflict"]:
                conflicts.append({"topic": topic, "a": a.id, "b": b.id,
                                  "detail": json.loads(v)["detail"]})
    return conflicts
```

---

## 17.5 Data drift

> **Imagine this…** Your test set was built from last year's support tickets. Since then the product changed, a new market opened, and users started asking different questions in a different language. Your suite still passes, and it is measuring a product that no longer exists.

| Drift type | Detection |
|---|---|
| **Input drift** | Compare production query embeddings this month vs last; measure distribution shift |
| **Topic drift** | Cluster production queries; watch for new clusters |
| Language mix drift | Track language distribution over time |
| **Corpus drift** | Document count, age distribution, and topic coverage over time |
| Model drift | The provider changes the model behind an alias — detect with the anchor set |
| Quality drift | Online eval scores over time (Part 15 §15.7) |

```
TC-DATA-001  Golden set representativeness
Method:     Embed the golden set and a sample of last month's production
            queries. For each production query, compute similarity to the
            nearest golden case.
Expected:   ≥ 80% of production queries have a golden-set neighbour above
            a similarity floor.
Failure:    Your eval suite no longer represents what users ask, and its
            green result means nothing.
Frequency:  Quarterly
Priority:   High
```

That test is the antidote to the slow decay every eval suite suffers. Without it, suites pass indefinitely while the product's real failure modes go untested.

---

## 17.6 Dataset versioning 🔴

Datasets are code. They need the same discipline.

| Practice | Why |
|---|---|
| **Store in Git** | Diffable, reviewable, revertable |
| Semantic version | `golden-v2.3.0` — referenced in every eval result |
| Changelog | What was added and why (the incident it came from) |
| **Never edit a case to make a test pass** | That is deleting the bug, not fixing it. If a case is genuinely wrong, fix it in a separate, reviewed commit with a reason |
| Freeze at release | The exact dataset that certified a release is recoverable |
| Split dev / held-out | Held-out is opened only at release |
| Attribute every case | `source`, `author`, `added` |
| Review additions | A second pair of eyes on expected behaviour |

**The "never edit to make it pass" rule is the one that gets broken.** Under deadline pressure, the easiest way to turn a suite green is to soften the expectation. Make this an explicit, written team rule before that pressure arrives — you will need to point at it.

**Large datasets:** for datasets too large for Git, use a data-versioning tool (DVC, or your ML platform's dataset registry) and keep the *pointer* in Git. The requirement is that "which dataset produced this result?" always has an answer.

---

## 17.7 Data poisoning 🟠

⏳ OWASP **LLM05 Data and Model Poisoning**, which in the 2026 edition also absorbed fine-tuning subversion.

| Question | Test |
|---|---|
| Who can write to the corpus? | Enumerate every path (Part 11 A2) |
| Is ingested content reviewed? | Is there a gate at all? |
| Is provenance recorded? | Author + timestamp per chunk |
| Can a bad answer be traced to a document? | Citations enable this |
| Is there an audit trail for corpus changes? | Who added what, when |
| Are corpus deletions propagated? | Deleted source → chunk removed within SLA |
| Post-fine-tune safety regression | **Re-run the full red-team suite** — tuning can strip alignment |

---

## 17.8 Self-check

1. Why is the dataset more important than the metric?
2. What proportion of a golden set should be unanswerable, and why?
3. What is the closed-loop failure in synthetic data generation?
4. Why is contradiction detection more valuable than most model-level tests?
5. What does the golden-set representativeness test protect against?
6. Why must you never edit a case to make a test pass?
7. What must be re-run after fine-tuning, and why?

---

**Next:** [PART-18-MODEL-TESTING.md](PART-18-MODEL-TESTING.md) — selecting, comparing, and upgrading models objectively.
