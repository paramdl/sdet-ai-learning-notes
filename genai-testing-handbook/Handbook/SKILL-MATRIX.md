# SKILL MATRIX — Beginner → Expert

> Use this to locate yourself honestly and to pick the next thing to work on. **Be strict.** The gap between "I have used it" and "I can defend the decisions I made with it" is the whole difference between stages.

---

## How to read this

For each skill, find the highest row where you can honestly say *"yes, and I could demonstrate it in an interview."* That is your level. Then read one cell to the right — that is your next target.

---

## 1 · Python

| | |
|---|---|
| **Beginner** | Scripts, functions, JSON, files. Copies pytest examples that work |
| **Intermediate** | Fixtures, parametrize, markers, Pydantic, decorators, logging, config management. Writes suites others can read |
| **Advanced** | async/asyncio for eval throughput, retries with backoff, mocking, pandas analysis, packaging a reusable harness |
| **Expert** | Designs frameworks other teams adopt. Reviews others' test code. Chooses when *not* to abstract |

## 2 · API testing

| | |
|---|---|
| **Beginner** | Sends requests, checks status codes, reads JSON |
| **Intermediate** | Schema validation, auth negative cases, timeouts, retries, mocked error paths |
| **Advanced** | Streaming/SSE, tool-call payload validation, token/usage reconciliation, fault injection, idempotency |
| **Expert** | Designs contract strategy across providers; catches gateway substitution and prompt-modification via metadata drift |

## 3 · LLM fundamentals

| | |
|---|---|
| **Beginner** | Knows tokens, temperature, context window as terms |
| **Intermediate** | Can draw the request lifecycle; explains why temperature 0 is not deterministic; reads `finish_reason` |
| **Advanced** | Predicts failure modes from architecture; explains multilingual token inflation, lost-in-the-middle, prefill vs decode |
| **Expert** | Sits in a design review and identifies the flaw before it is built |

## 4 · Prompt engineering & testing

| | |
|---|---|
| **Beginner** | Writes and edits prompts; notices when output is wrong |
| **Intermediate** | Runs the review checklist; tests per-constraint satisfaction; uses canaries; tests templates with hostile variables |
| **Advanced** | Distinguishes ambiguity from variance with evidence; runs regression on prompt versions; measures instruction conflict |
| **Expert** | Owns prompt governance: versioning, review, gating, rollback across an organisation |

## 5 · LLM evaluation ← **the core skill**

| | |
|---|---|
| **Beginner** | Runs promptfoo or DeepEval with someone else's config |
| **Intermediate** | Builds a golden dataset; writes rubrics; runs N-run pass-rate assertions; calibrates a similarity threshold |
| **Advanced** | **Validates the judge with kappa**; controls for judge bias; designs delta gates; reports per category with deltas and cost |
| **Expert** | Designs measurement strategy for systems they did not build; knows when a metric is invalid and says so |

## 6 · RAG

| | |
|---|---|
| **Beginner** | Understands the pipeline; can run a RAG query |
| **Intermediate** | Builds a retrieval golden set; measures Precision@K, Recall@K, MRR |
| **Advanced** | Stage-isolated diagnosis; chunking sweeps producing decision tables; faithfulness with claim decomposition; citation validation; indirect injection |
| **Expert** | Diagnoses an unfamiliar RAG system from its traces and recommends the architectural fix |

## 7 · Vector databases

| | |
|---|---|
| **Beginner** | Knows what a vector and cosine similarity are |
| **Intermediate** | Queries pgvector/Qdrant; understands metrics and top-K |
| **Advanced** | Verifies operator/ops-class agreement, ANN recall vs exact, pre- vs post-filtering, index usage via `EXPLAIN` |
| **Expert** | Advises on store selection and index tuning with a measured recall/latency curve |

## 8 · Agents

| | |
|---|---|
| **Beginner** | Understands the loop and tool calling |
| **Intermediate** | Tests tool selection, arguments, schemas; catches type and unit errors |
| **Advanced** | Trajectory assertions; 8-mode fault injection; caps; runtime permission enforcement; memory poisoning; hostile tool output |
| **Expert** | Runs the tool inventory audit and changes the architecture as a result |

## 9 · AI security

| | |
|---|---|
| **Beginner** | Knows what prompt injection is; runs a scanner |
| **Intermediate** | Canary technique; payload × transform sweeps; reports success rates; knows the OWASP LLM Top 10 |
| **Advanced** | Indirect injection through every write path; chains findings; output-handling exfiltration; tenant isolation; denial of wallet as a spend rate |
| **Expert** | Runs scoped red teams with written objectives; produces reports a security team acts on; advises on containment architecture |

## 10 · Performance

| | |
|---|---|
| **Beginner** | Measures response time |
| **Intermediate** | Separates TTFT from total; builds realistic load profiles; reports p95 |
| **Advanced** | Measures **quality under load**; diagnoses queueing vs contention; profiles variance and reports min/p10 |
| **Expert** | Designs and tests the degradation ladder; measures fallback quality; sets SLOs with error budgets |

## 11 · Observability

| | |
|---|---|
| **Beginner** | Reads logs |
| **Intermediate** | Instruments traces; inspects spans; retrieves the prompt behind a response |
| **Advanced** | Designs trace schemas (OTel conventions); online eval on sampled traffic; drift detection; PII redaction verified |
| **Expert** | Defines the organisation's AI observability standard; feeds production failures back into datasets |

## 12 · CI/CD

| | |
|---|---|
| **Beginner** | Runs tests in a pipeline |
| **Intermediate** | Stages by cost and speed; artefacts and reports; secret handling |
| **Advanced** | Delta gates, response caching, budget caps, quarantine, confirm-before-fail, PR comments that name causes |
| **Expert** | Designs quality gates an organisation adopts; keeps them switched on for years |

## 13 · Docker

| | |
|---|---|
| **Beginner** | Runs a container someone else defined |
| **Intermediate** | Writes a Dockerfile with correct layer ordering; Compose with healthchecks; volumes and env files |
| **Advanced** | Builds reproducible test environments; debugs container networking and startup races |
| **Expert** | Not required for this role — this is where you stop |

## 14 · Cloud

| | |
|---|---|
| **Beginner** | Navigates the console; finds a deployment |
| **Intermediate** | Reads logs and metrics; calls the model via SDK; understands quotas, regions, deployments |
| **Advanced** | Tests managed guardrails and managed RAG; verifies data residency and cross-region behaviour; config parity between environments |
| **Expert** | Not required — architects handle this |

## 15 · LLMOps

| | |
|---|---|
| **Beginner** | Knows the term |
| **Intermediate** | Understands the four lifecycles; reads a model registry |
| **Advanced** | Tests prompt rollback; runs anchor-set drift detection; advocates shadow deployment; runs rollback drills |
| **Expert** | Defines the boundary between QA and LLMOps for an organisation and staffs both sides |

## 16 · AI governance

| | |
|---|---|
| **Beginner** | Has heard of the EU AI Act |
| **Intermediate** | Knows NIST AI RMF's four functions and where QA sits; tests AI disclosure |
| **Advanced** | Produces a governance evidence pack with an honest limitations section; designs auditable test artefacts |
| **Expert** | Represents quality to auditors, regulators, and enterprise security reviews |

---

## Self-assessment scoring

Count your levels: Beginner = 1, Intermediate = 2, Advanced = 3, Expert = 4. Sixteen skills, maximum 64.

| Total | You are |
|---|---|
| 16–24 | Entering GenAI QA. Focus Levels 1–4 |
| 25–34 | **GenAI QA.** Focus Level 5 (evaluation) — it unlocks everything else |
| 35–46 | **AI Quality Engineer.** Focus your weakest of RAG / agents / security |
| 47–56 | **Senior AI QA Engineer.** Focus influence: design reviews, mentoring, standards |
| 57–64 | **AI QA Architect.** Focus organisation-scale strategy |

**The honest calibration check:** for any skill you scored Advanced or Expert, could you defend a specific decision you made — a threshold, a metric choice, a severity rating — under questioning from someone who disagreed? If not, drop it a level. That question is exactly what a senior interview does.

---

## The five skills that matter most

If you optimise for employability rather than completeness, these five carry disproportionate weight:

1. **LLM evaluation** — the core competency; nothing substitutes for it
2. **AI security** — highest demand, lowest supply
3. **RAG** — the most common architecture in production
4. **Python** — the substrate for all of it
5. **Observability** — the prerequisite that makes 1, 2, and 3 possible

Reaching Advanced in those five makes you employable as an AI Quality Engineer regardless of where the other eleven sit.
