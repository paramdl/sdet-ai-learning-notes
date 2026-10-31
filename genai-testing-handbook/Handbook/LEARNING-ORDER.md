# LEARNING ORDER — Levels 0 to 14

> The strict sequence. Each level lists what to learn, why, the tools, the exercise, the project, the prerequisite skills for moving on, and the interview questions you should be able to answer before you do.

**I have adjusted the sequence you proposed in two places, and here is why:**

1. **Security moved earlier (Level 7, not 8).** Injection and leakage testing is largely deterministic, requires no eval infrastructure, and produces the highest-severity findings. Waiting until after agents delays your most valuable output by months. Basic security now, advanced red teaming later.

2. **Observability moved earlier (Level 6, alongside RAG).** You cannot test RAG or agents effectively without traces — the "was the right content retrieved?" question is unanswerable without them. Tracing is a *prerequisite* for Levels 8–9, not a later addition.

Everything else follows your proposed order, which is sound.

---

## LEVEL 0 — QA foundations
**Status for you: complete.** Listed for reference and for people you mentor.

| | |
|---|---|
| **Learn** | Test design, boundary analysis, equivalence partitioning, risk-based prioritisation, defect reporting, exploratory testing |
| **Why** | Everything in this book is test design applied to a new target. A GenAI tester who cannot design a boundary case is not saved by knowing what an embedding is |
| **Exercise** | Take any AI feature and write 20 boundary cases before learning anything about AI |
| **Move on when** | You can produce a risk-ranked test plan for an unfamiliar feature |

---

## LEVEL 1 — Python
| | |
|---|---|
| **Learn** | Part 2 §2.1 beginner + intermediate tiers. Especially: strings, collections, comprehensions, JSON, files with encoding, exceptions, venv, env vars, **pytest** |
| **Why** | The entire GenAI ecosystem is Python-first. Non-negotiable |
| **Tools** | Python 3.12+, venv, pytest, VS Code |
| **Exercise** | Read a CSV of prompts, call a local model, write results to JSON, handle errors, never hard-code a key |
| **Project** | Part 25 Project 1 (harness portion) |
| **Prerequisite to move on** | You can write a parametrized pytest suite with fixtures without looking it up |
| **Interview Qs** | *When would you use `scope="session"`? Why always specify `encoding='utf-8'`? What does `parametrize` give you that a loop does not?* |

---

## LEVEL 2 — API automation
| | |
|---|---|
| **Learn** | `requests`/`httpx`, HTTP fundamentals, status codes, headers, auth, timeouts, retries, schema validation with Pydantic, mocking with `respx` |
| **Why** | LLM APIs are APIs. This is 40% of GenAI testing and it transfers completely |
| **Tools** | httpx, Pydantic, respx, Postman, curl, jq |
| **Exercise** | Build a client with exponential backoff and jitter; prove it with mocked 429s |
| **Project** | Part 25 Project 1 complete |
| **Prerequisite** | You can test an error path without making a real API call |
| **Interview Qs** | *Why must a client timeout be shorter than the gateway timeout? Why does retry logic need jitter?* |

---

## LEVEL 3 — LLM fundamentals
| | |
|---|---|
| **Learn** | Parts 1 and 3 entirely. Tokens, context window, sampling, inference, the twelve-layer request lifecycle, streaming, `finish_reason`, error taxonomy |
| **Why** | You cannot test what you cannot describe. This level is what lets you sit in a design review |
| **Tools** | Ollama, tiktoken, curl for SSE |
| **Exercise** | Send one prompt 20 times at temperature 0 and at 1.0; publish the determinism baseline. Send an over-window input and record what happens |
| **Project** | Part 25 Project 2 (multi-provider) |
| **Prerequisite** | You can draw the twelve-layer diagram and name a failure mode per layer |
| **Interview Qs** | *Why isn't temperature 0 deterministic? Why is a character limit inadequate for a token limit, and which users does that hurt first? How can streaming bypass an output guardrail?* |

---

## LEVEL 4 — Prompt testing
| | |
|---|---|
| **Learn** | Part 4 entirely. Prompt anatomy, the review checklist, the 12 test types, canary technique, template variable testing |
| **Why** | Prompts are the least-governed artefact in most AI products. Bringing engineering discipline here is often your fastest visible win |
| **Tools** | promptfoo |
| **Exercise** | Take a production prompt, run the 12-point review checklist, and produce a per-constraint satisfaction table over 20 runs |
| **Project** | A promptfoo suite with 20 cases across correctness, injection, leakage, boundary, and multilingual |
| **Prerequisite** | You can distinguish model variance from prompt ambiguity, with evidence |
| **Interview Qs** | *A stakeholder says the AI is inconsistent — what do you do? What is a canary string and why does it help?* |

---

## LEVEL 5 — LLM evaluation
| | |
|---|---|
| **Learn** | Part 6 entirely. Metric taxonomy, threshold calibration, LLM-as-judge, **judge validation with kappa**, judge biases, N-run sampling, honest reporting |
| **Why** | **This is the core competency of the role.** Everything else is application |
| **Tools** | DeepEval, embeddings, promptfoo |
| **Exercise** | Build a judge rubric. Hand-label 40 outputs. Compute kappa. Read every disagreement. Rewrite the rubric. Repeat until kappa > 0.7 |
| **Project** | Part 25 Project 3 |
| **Prerequisite** | You have a validated judge with a published kappa, and you can defend every threshold you set |
| **Interview Qs** | *How do you know you can trust your judge? Name three judge biases and their controls. How do you set a threshold a PM cannot argue with?* |

---

## LEVEL 6 — Observability (moved earlier)
| | |
|---|---|
| **Learn** | Part 15. Traces and spans, what a RAG trace and an agent trace must contain, OpenTelemetry GenAI conventions, online eval, privacy in tracing |
| **Why** | **Prerequisite for Levels 8 and 9.** Without traces you cannot answer "was the right content retrieved?" or "what path did the agent take?" |
| **Tools** | Arize Phoenix (local, no server), Langfuse |
| **Exercise** | Instrument your Level 5 harness; inspect a full trace; add PII redaction and prove it works with a canary |
| **Prerequisite** | You can retrieve the exact prompt that produced any given response |
| **Interview Qs** | *Why is a missing trace a defect? What must a RAG trace record? Why alert on refusal rate falling?* |

---

## LEVEL 7 — AI security fundamentals (moved earlier)
| | |
|---|---|
| **Learn** | Part 11 §§11.1–11.3 (A1–A6), Part 13 Part C (guardrails). OWASP LLM Top 10 (2026 and 2025 numbering) |
| **Why** | Largely deterministic, needs no eval infrastructure, produces the highest-severity findings. Delaying this wastes your best early output |
| **Tools** | Your own injection sweep (Part 27 §27.10), promptfoo redteam |
| **Exercise** | Canary every hidden surface; run 5 payload families × 4 transforms × 5 repetitions; report success rates per variant |
| **Project** | A security suite added to Project 3 |
| **Prerequisite** | You can write a finding with a success rate, impact, and affected surface enumeration |
| **Interview Qs** | *Why must a security finding carry a success rate? Explain the markdown-image exfiltration chain. Why is injection architectural rather than patchable?* |

---

## LEVEL 8 — RAG and vector databases
| | |
|---|---|
| **Learn** | Parts 7 and 8. The pipeline, stage isolation, retrieval metrics, chunking sweeps, citation validation, indirect injection, vector DB failure modes |
| **Why** | The most common production AI architecture, and where most quality problems live |
| **Tools** | Chroma or pgvector, Ragas, sentence-transformers, LlamaIndex |
| **Exercise** | Build a small RAG. Deliberately break it: chunk size 50, K=1, remove the reranker. Watch which metric moves |
| **Project** | Part 25 Projects 4 and 5 |
| **Prerequisite** | Given a wrong answer, you can localise it to a stage with evidence |
| **Interview Qs** | *What's your first question on a wrong RAG answer? What does high precision + low recall mean and what do you recommend? Why does vector search fail on "ERR-5521"?* |

---

## LEVEL 9 — Agents and tool calling
| | |
|---|---|
| **Learn** | Part 9 entirely. Tool-call testing, trajectory assertions, fault injection, caps, runtime permission enforcement, memory poisoning, the ASI list |
| **Why** | Agents act. Blast radius changes from a wrong answer to a wrong action. **OWASP LLM03 in 2026 — the biggest riser** |
| **Tools** | Tracing platform, DeepEval agent metrics, custom fault-injection harness |
| **Exercise** | Build the `FaultyTool` wrapper; run all 8 fault modes against a 4-tool agent |
| **Project** | Part 25 Project 6 |
| **Prerequisite** | You can explain why testing the model's refusal is testing the wrong layer |
| **Interview Qs** | *Why is outcome-only testing insufficient? Where are permissions enforced? Why is retry logic dangerous for agents?* |

---

## LEVEL 10 — Performance and reliability
| | |
|---|---|
| **Learn** | Part 14. TTFT vs total latency, realistic load profiles, quality under load, variance profiling, degradation ladder, fallback quality |
| **Why** | The GenAI-specific performance metrics are not what your existing tools measure by default |
| **Tools** | k6 or Locust, custom async Python for TTFT |
| **Exercise** | Load test with a realistic token-distribution profile; measure quality at idle, at target, and at 2× target |
| **Prerequisite** | You have measured a fallback model's quality |
| **Interview Qs** | *Why is TTFT more important than total latency? Why is load-testing with "hi" meaningless? What is DEGRADED 2 and why is it dangerous?* |

---

## LEVEL 11 — CI/CD, Docker, cost, regression
| | |
|---|---|
| **Learn** | Parts 16, 19, 20, 21 Part A. Cost gates, the seven regression suites, baseline discipline, pipeline design, containers |
| **Why** | This is what turns your work from a series of investigations into a permanent quality system |
| **Tools** | GitHub Actions, Docker, Docker Compose |
| **Exercise** | Build the pipeline from Part 20 §20.2 with response caching, a budget cap, and a PR comment |
| **Prerequisite** | Your pipeline has blocked a merge for a real regression, and stayed switched on |
| **Interview Qs** | *Why must pre-merge stay under 15 minutes? What makes per-PR evaluation affordable? Why can CI never auto-update a baseline?* |

---

## LEVEL 12 — Cloud, LLMOps, Kubernetes basics
| | |
|---|---|
| **Learn** | Parts 21 Part B, 22, 23. One cloud properly; the four lifecycles; deployment strategies; drift detection; rollback |
| **Why** | Where the systems you test actually run, and the operational context your gates plug into |
| **Tools** | Your employer's cloud; kubectl; a model registry or Langfuse |
| **Exercise** | Run a rollback drill: revert prompt, model, and corpus in staging; time each |
| **Interview Qs** | *Why can two deployments of the same model behave differently? What is shadow deployment and what does it solve? Name the three sources of a refusal.* |

---

## LEVEL 13 — Advanced AI QA
| | |
|---|---|
| **Learn** | Parts 10, 12, 13 Parts A–B, 17, 18, 24. Multimodal, professional red teaming, hallucination taxonomy, bias methodology, dataset discipline, model selection, governance |
| **Why** | The depth that distinguishes an AI Quality Engineer from someone running an eval suite |
| **Tools** | garak, PyRIT, multimodal test corpora |
| **Exercise** | Run a scoped red team with written objectives; produce a report in the Part 12 format including "controls that held" |
| **Project** | Part 25 Projects 7 and 8 |
| **Prerequisite** | You have produced a governance evidence pack with an honest limitations section |
| **Interview Qs** | *What makes a bias finding defensible? What two suites do teams skip on model upgrade? Why is section 10 of an evidence pack the most valuable?* |

---

## LEVEL 14 — AI QA Architect
| | |
|---|---|
| **Learn** | Organisation-scale strategy; quality standards definition; risk modelling; audit readiness; build-vs-buy; hiring and mentoring |
| **Why** | Influence over architecture and process, rather than coverage of a single product |
| **Exercise** | Write your organisation's definition of "tested" for AI features, and get it adopted |
| **Signals you are here** | Legal comes to you before engineering; you hire AI QA engineers; your evidence pack has survived an external review |

---

## The dependency graph

```
L0 QA foundations
 └─ L1 Python
     └─ L2 API automation
         └─ L3 LLM fundamentals
             ├─ L4 Prompt testing
             │   └─ L5 Evaluation ◄── the core competency
             │       ├─ L6 Observability ──┐
             │       └─ L7 Security        │
             │            └────────────────┼─ L8 RAG + Vector DB
             │                             │      └─ L9 Agents
             │                             │
             └─────────────────────────────┴─ L10 Performance
                                                └─ L11 CI/CD + Docker + Cost
                                                    └─ L12 Cloud + LLMOps
                                                        └─ L13 Advanced
                                                            └─ L14 Architect
```

**Levels 5 and 6 are the load-bearing ones.** Evaluation is the competency; observability is what makes Levels 8–9 possible. Rushing past either produces someone who can run tools but not answer questions.
