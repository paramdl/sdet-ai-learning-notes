# STUDY PLANS

> **Assumption:** 1–2 hours per day, most days. Built on your existing QA and automation experience, so the Python ramp is compressed.
>
> **Rule for all plans:** every week ends with something that runs. Reading without building produces someone who can discuss GenAI testing and cannot do it.

---

# THE 30-DAY PLAN — "Employable as a GenAI QA engineer"

**Goal:** working eval harness, real security findings, and the vocabulary to interview.

### Week 1 — Foundations and setup

| Day | Topic | Exercise | Reading |
|---|---|---|---|
| 1 | Setup | Install Ollama, `ollama pull llama3.1:8b`, venv, pip install stack, run `verify_setup.py` | Handbook SETUP |
| 2 | AI/ML/DL/GenAI/LLM concepts | Write your own one-paragraph definition of each; no copying | Part 1 §§1.1–1.7 |
| 3 | **Tokens** | Count tokens for the same paragraph in English, Tamil, Hindi. Record the ratios | Part 1 §1.10 |
| 4 | Context window + embeddings | Send an over-window input; record the behaviour. Compute cosine similarity for 5 sentence pairs | Part 1 §§1.11–1.12 |
| 5 | **Sampling & determinism** | Run one prompt 20× at temp 0 and 20× at 1.0. **Publish your determinism baseline** | Part 1 §1.15 |
| 6 | Fine-tuning, RLHF, reasoning models | Write the RAG-vs-fine-tuning decision table from memory | Part 1 §§1.16–1.21 |
| 7 | **Review + self-check** | Answer all 10 questions in Part 1 §1.22 without looking | Part 1 |

### Week 2 — The request lifecycle and API testing

| Day | Topic | Exercise |
|---|---|---|
| 8 | The 12-layer diagram | Draw it from memory; name a failure per layer (Part 3) |
| 9 | Raw API by curl | Call a model with curl; inspect `usage` and `finish_reason` with jq |
| 10 | Python client + Pydantic | Build `harness/client.py` and the contract test (Part 27 §§27.0–27.1) |
| 11 | **Streaming/SSE** | Stream with curl `-N`; then in Python; measure TTFT |
| 12 | Errors and retries | Mock 429/500/timeout with respx; prove backoff with jitter (Part 27 §27.13) |
| 13 | Message structure | Test whether the client can supply an `assistant` turn (Part 3 §3.5) |
| 14 | **Project 1 complete** | Full contract suite green; determinism baseline published |

### Week 3 — Prompts and evaluation

| Day | Topic | Exercise |
|---|---|---|
| 15 | Prompt anatomy | Run the 12-point review checklist on a real prompt (Part 4 §4.1) |
| 16 | promptfoo | `npx promptfoo@latest init`; 10 cases; `eval`; `view` |
| 17 | Assertion types | Add `contains`, `is-json`, `javascript`, `similar`, `llm-rubric` |
| 18 | **Per-constraint testing** | Build the constraint satisfaction table over 20 runs (Part 4 §4.3) |
| 19 | Metric taxonomy | Implement exact match, normalised match, cosine, schema (Part 6 §§6.3–6.4) |
| 20 | **Threshold calibration** | Calibrate your similarity threshold on 30 good + 30 bad pairs |
| 21 | Review | Part 6 self-check |

### Week 4 — Judge, security, and delivery

| Day | Topic | Exercise |
|---|---|---|
| 22 | LLM-as-judge | Write a rubric; binary verdict + required reason (Part 6 §6.5) |
| 23 | **Judge validation** | Hand-label 40 outputs; compute kappa; read every disagreement |
| 24 | Rubric iteration | Rewrite the rubric; re-measure kappa; target > 0.7 |
| 25 | **OWASP LLM Top 10** | Read it end to end. Map each entry to one test you could write |
| 26 | Injection sweep | Build the payload × transform sweep with canaries (Part 27 §27.10) |
| 27 | Leakage testing | Canary every hidden surface; run 7 extraction techniques |
| 28 | **Project 3** | Assemble everything into one suite; run at N=3 |
| 29 | CI | GitHub Actions: deterministic on PR, eval nightly, budget cap |
| 30 | **Portfolio** | Write the README explaining *why* each threshold and metric was chosen |

**Day-30 state:** a public repository containing an eval suite with a validated judge, a security sweep, and CI. You can answer most of Part 28's beginner and intermediate questions.

---

# THE 60-DAY PLAN — adds RAG and observability

Days 1–30 as above, then:

### Week 5 — Observability first
| Days | Focus |
|---|---|
| 31–32 | Phoenix locally; instrument the Week-4 harness; inspect traces |
| 33–34 | Span design: what an LLM trace must carry (Part 15 §15.3) |
| 35 | PII redaction; prove it with a canary |
| 36–37 | Cost tracking: reconcile app-reported cost against provider usage (Part 16) |

### Week 6 — RAG construction
| Days | Focus |
|---|---|
| 38–39 | Build a small RAG over documents you own (Chroma + sentence-transformers) |
| 40 | Ingestion tests: extraction fidelity, table integrity, metadata completeness |
| 41–42 | **Build a 50-query golden retrieval set** with labelled relevant chunks |
| 43–44 | Implement Precision@K, Recall@K, MRR, NDCG |

### Week 7 — RAG evaluation
| Days | Focus |
|---|---|
| 45–46 | **Chunking sweep** — produce the decision table |
| 47 | Break it deliberately: chunk 50, K=1, no reranker. Watch the metrics move |
| 48–49 | Faithfulness with claim decomposition; citation validation |
| 50–51 | No-answer behaviour; zero-retrieval and low-similarity paths |

### Week 8 — RAG security and vector DB
| Days | Focus |
|---|---|
| 52–53 | pgvector: schema, index, `EXPLAIN`, operator/ops-class agreement |
| 54 | ANN recall vs exact search |
| 55–56 | **Indirect injection** via a planted corpus document |
| 57 | Tenant isolation and pre- vs post-filtering |
| 58–59 | Project 4 assembly and CI integration |
| 60 | **Portfolio update**: chunking decision table + retrieval dashboard |

**Day-60 state:** employable as an AI Quality Engineer for RAG products.

---

# THE 90-DAY PLAN — adds agents, performance, and a red team

Days 1–60 as above, then:

### Week 9–10 — Agents
| Days | Focus |
|---|---|
| 61–63 | Build a 4-tool agent; trace every step |
| 64–66 | Tool-call testing: selection, arguments, types, units, ambiguity, missing params |
| 67–69 | **Fault injection**: the 8-mode `FaultyTool` wrapper |
| 70–72 | Trajectory assertions; step/cost/time caps; hostile tool output |
| 73–75 | Runtime permission enforcement; confirmation bypass attempts; memory poisoning |

### Week 11 — Performance and reliability
| Days | Focus |
|---|---|
| 76–77 | Realistic load profile from token distributions; k6 or Locust |
| 78 | Async Python TTFT harness under concurrency |
| 79 | **Quality under load** at idle / target / 2× target |
| 80–81 | Variance profiling (N=50, report min and p10); fallback model quality |
| 82 | Degradation ladder — test each rung |

### Week 12–13 — Red team and consolidation
| Days | Focus |
|---|---|
| 83–85 | Scoped red team on your own system: written objectives, garak + promptfoo redteam |
| 86–87 | **Write the report** in the Part 12 format, including "controls that held" |
| 88 | Regression suite: the seven suites, baselines, delta gates (Part 19) |
| 89 | Full CI pipeline with all stages and budget caps (Part 20) |
| 90 | **Portfolio consolidation**: Projects 1–6, one README per project explaining decisions |

**Day-90 state:** a complete portfolio. You can answer every question in Part 28.

---

# THE 6-MONTH PLAN

Months 1–3 as above. Then:

| Month | Focus | Output |
|---|---|---|
| **4** | **Multimodal + advanced hallucination/bias.** Parts 10, 13 Parts A–B. Vision, OCR, cross-modal injection, hallucination taxonomy, counterfactual bias method | Project 7; a bias assessment with stated limitations |
| **5** | **Infrastructure and platform.** Parts 21–23. Docker Compose test stacks, kubectl basics, one cloud properly, LLMOps lifecycles, shadow deployment, rollback drill | A containerised test environment; a rollback drill result |
| **6** | **Governance and certification.** Part 24; ISTQB CT-AI if pursuing it. Evidence pack; audit-ready artefacts | A governance evidence pack with an honest limitations section |

**Also across months 4–6:** start applying. You do not need month 12 to be hired — you need month 3 plus the ability to talk about it.

---

# THE 12-MONTH PLAN

Months 1–6 as above. Months 7–12 are **specialisation plus real-world application**.

| Month | Focus |
|---|---|
| **7** | Project 8: the production-grade platform. Architecture and pipeline |
| **8** | Project 8: observability, cost dashboard, quality SLOs |
| **9** | Project 8: full red team, load test, evidence pack. **Publish it** |
| **10** | **Pick a specialisation** (Part 30 §30.2): security, evaluation, or platform. Go deep on one |
| **11** | Depth in the specialisation: for security, PyRIT and multi-turn adaptive attacks; for evaluation, statistics and experiment design; for platform, OTel and cost engineering |
| **12** | **Produce something public**: a detailed write-up of one finding, a conference talk, or an open-source contribution. Then re-read Parts 1–3 |

**Month-12 state:** Senior AI QA Engineer capability, with a public body of work.

---

## Making the plan survive contact with reality

| Problem | Fix |
|---|---|
| You miss three days | Do not restart. Resume where you stopped. The sequence matters, the calendar does not |
| A topic takes twice as long | Let it. The plan is ordered by dependency, not by duration |
| You get pulled into work | Apply the day's topic to a work system instead of a lab one. Better learning, and it is billable |
| You lose momentum | Drop to 30 minutes a day rather than to zero. Consistency beats intensity here |
| Something in the handbook is out of date | Verify against Appendix C's primary source and **update your copy**. Maintaining the document is part of the learning |

**The single highest-leverage habit:** at the end of each week, write three sentences on what you learned and what surprised you. In six months that file is your interview preparation, your blog post backlog, and the evidence that you actually did this.
