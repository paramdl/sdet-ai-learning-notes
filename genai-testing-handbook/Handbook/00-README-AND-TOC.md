# The GenAI Testing Handbook

### A Self-Study Textbook, Career Roadmap, and Practical Testing Reference for AI Quality Engineers

**Edition:** 1.0 — compiled 8 September 2026
**Written for:** an experienced manual + automation QA engineer moving into GenAI / AI Quality Engineering
**Assumed starting point:** strong QA fundamentals, working automation experience (Playwright, API testing), **no** prior AI/ML background
**Target end state:** Advanced GenAI Tester / AI Quality Engineer able to own quality for production LLM applications, RAG systems, agents, multimodal systems, and AI APIs

---

## How to use this book

This is not a book to read cover to cover before starting. It is a **reference you work through in a specific order**, doing the exercises.

| If you want to… | Go to |
|---|---|
| Know what to do tomorrow morning | [`WHAT-TO-DO-TOMORROW.md`](WHAT-TO-DO-TOMORROW.md) |
| See the strict learning sequence | [`LEARNING-ORDER.md`](LEARNING-ORDER.md) (Levels 0–14) |
| See a day-by-day plan | [`STUDY-PLANS.md`](STUDY-PLANS.md) (30 / 60 / 90 day, 6 and 12 month) |
| Know where you currently stand | [`SKILL-MATRIX.md`](SKILL-MATRIX.md) |
| Avoid the classic traps | [`COMMON-MISTAKES.md`](COMMON-MISTAKES.md) |
| Learn a specific topic | The PART files below |
| Look up a tool | [`APPENDIX-B-TOOL-INDEX.md`](APPENDIX-B-TOOL-INDEX.md) |
| Look up a term | [`APPENDIX-A-GLOSSARY.md`](APPENDIX-A-GLOSSARY.md) |

### Reading conventions used throughout

Every significant concept is presented in the same five-part shape:

> **Imagine this…** — a plain-language analogy, no jargon
> **Technically** — the precise definition
> **Real-world example** — where you meet it in a live product
> **Testing implications** — what this means for *you*, the tester
> **Failure modes** — how it breaks in production, with example test cases

Priority labels appear on every topic:

| Label | Meaning |
|---|---|
| 🔴 **MUST LEARN** | You cannot do the job without it |
| 🟠 **SHOULD LEARN** | Expected of a senior/advanced practitioner |
| 🟡 **OPTIONAL** | Useful in some roles, skip until needed |
| ⚪ **NOT REQUIRED** | Explicitly skip — it belongs to another role |

Volatility labels appear on anything that dates quickly:

> ⏳ **May change** — verified 8 Sept 2026; re-check the primary source before relying on it.

---

## Table of Contents

### Front matter
- **[LEARNING-ORDER.md](LEARNING-ORDER.md)** — Levels 0–14, with prerequisites, exercises, and interview questions per level
- **[SKILL-MATRIX.md](SKILL-MATRIX.md)** — Beginner → Intermediate → Advanced → Expert across 16 skills
- **[STUDY-PLANS.md](STUDY-PLANS.md)** — 30/60/90-day, 6-month, 12-month daily plans at 1–2 h/day
- **[COMMON-MISTAKES.md](COMMON-MISTAKES.md)** — What traditional QA engineers get wrong on GenAI

### Part 1 — Foundations
- **[PART-01-GENAI-FOUNDATIONS.md](PART-01-GENAI-FOUNDATIONS.md)** — AI, ML, DL, GenAI, NLP, transformers, attention, embeddings, fine-tuning, LoRA, quantization, distillation, RLHF/RLAIF, reasoning models, multimodal models — each with testing implications

### Part 2 — Programming
- **[PART-02-PROGRAMMING.md](PART-02-PROGRAMMING.md)** — Python (topic-by-topic, graded), JavaScript/TypeScript, SQL + pgvector, Bash/Linux, and a verdict on Java/C#/Go/C++/Rust

### Part 3 — LLM Fundamentals
- **[PART-03-LLM-FUNDAMENTALS.md](PART-03-LLM-FUNDAMENTALS.md)** — Tokens, context windows, sampling parameters, inference, the full request lifecycle diagram, and which layer a QA engineer tests at each stage

### Part 4 — Prompt Engineering & Prompt Testing
- **[PART-04-PROMPT-ENGINEERING.md](PART-04-PROMPT-ENGINEERING.md)** — Prompt anatomy, few-shot, CoT, structured output, templates, versioning; then prompt correctness, regression, ambiguity, conflict, boundary, adversarial, multilingual testing

### Part 5 — LLM API Testing
- **[PART-05-LLM-API-TESTING.md](PART-05-LLM-API-TESTING.md)** — Auth, schemas, streaming/SSE, rate limits, retries, timeouts, error handling, token usage; full worked REQUEST → RESPONSE → TEST CASE → PYTHON TEST examples

### Part 6 — LLM Evaluation
- **[PART-06-LLM-EVALUATION.md](PART-06-LLM-EVALUATION.md)** — Exact match through LLM-as-judge; every metric defined with a worked example; judge validation and judge bias

### Part 7 — RAG Testing
- **[PART-07-RAG-TESTING.md](PART-07-RAG-TESTING.md)** — Full pipeline, stage-by-stage test strategy, Precision@K / Recall@K / MRR / NDCG, faithfulness, citation validation

### Part 8 — Vector Database Testing
- **[PART-08-VECTOR-DB-TESTING.md](PART-08-VECTOR-DB-TESTING.md)** — Similarity metrics, indexing (HNSW/IVF), metadata filtering, pgvector and Qdrant worked examples, failure modes

### Part 9 — AI Agent & Tool-Calling Testing
- **[PART-09-AGENT-TESTING.md](PART-09-AGENT-TESTING.md)** — Agent loop, tool selection/arguments, failure injection, loops, memory, permissions, excessive agency, goal hijack, trajectory evaluation

### Part 10 — Multimodal Testing
- **[PART-10-MULTIMODAL-TESTING.md](PART-10-MULTIMODAL-TESTING.md)** — Vision, OCR, STT/TTS, video, cross-modal consistency, and cross-modal prompt injection

### Part 11 — AI Security Testing
- **[PART-11-AI-SECURITY.md](PART-11-AI-SECURITY.md)** — Every attack class with definition, example, expected secure behaviour, test case, automation, mitigation; **OWASP LLM Top 10 (2026)** and **OWASP Agentic Top 10 (ASI01–ASI10)** fully mapped

### Part 12 — AI Red Teaming
- **[PART-12-RED-TEAMING.md](PART-12-RED-TEAMING.md)** — How professional red teams operate, attack taxonomies, garak/PyRIT/promptfoo redteam/DeepTeam, safe methodology, severity rating, reporting

### Part 13 — Safety, Hallucination, Bias & Guardrails
- **[PART-13-SAFETY-GUARDRAILS.md](PART-13-SAFETY-GUARDRAILS.md)** — Seven hallucination types and how to build a hallucination dataset; bias/toxicity/fairness testing done objectively; guardrail testing including over-refusal

### Part 14 — Performance & Reliability
- **[PART-14-PERFORMANCE-RELIABILITY.md](PART-14-PERFORMANCE-RELIABILITY.md)** — TTFT, tokens/sec, throughput, concurrency, streaming under load, k6/Locust scripts; then non-determinism, variance, fallbacks, partial failures

### Part 15 — Observability
- **[PART-15-OBSERVABILITY.md](PART-15-OBSERVABILITY.md)** — Logging, tracing, metrics, OpenTelemetry GenAI semantic conventions, example traces for LLM-only / RAG / agent apps

### Part 16 — Cost & Token Testing
- **[PART-16-COST-TOKEN-TESTING.md](PART-16-COST-TOKEN-TESTING.md)** — Cost formulas, cost per request/user/conversation, detecting token explosions and infinite agent loops

### Part 17 — Data & Dataset Testing
- **[PART-17-DATA-DATASET-TESTING.md](PART-17-DATA-DATASET-TESTING.md)** — Golden datasets, ground truth, synthetic generation, data quality, drift, poisoning, dataset versioning

### Part 18 — Model Testing
- **[PART-18-MODEL-TESTING.md](PART-18-MODEL-TESTING.md)** — Model selection and objective comparison, benchmarking, upgrade regression, fine-tuned and open-weight model testing

### Part 19 — Regression Testing
- **[PART-19-REGRESSION-TESTING.md](PART-19-REGRESSION-TESTING.md)** — Prompt / model / RAG / agent / API / security / performance regression, and how to build the suite

### Part 20 — CI/CD
- **[PART-20-CICD.md](PART-20-CICD.md)** — Full pipeline design, quality gates, GitHub Actions / GitLab / Jenkins / Azure DevOps configs, cost control in CI

### Part 21 — Docker & Kubernetes
- **[PART-21-DOCKER-KUBERNETES.md](PART-21-DOCKER-KUBERNETES.md)** — Exactly the Docker and K8s a QA engineer needs, no more

### Part 22 — Cloud AI Platforms
- **[PART-22-CLOUD-AI.md](PART-22-CLOUD-AI.md)** — Azure OpenAI/AI Foundry/AI Search, AWS Bedrock/OpenSearch/SageMaker, Google Vertex AI — from a tester's seat

### Part 23 — LLMOps / MLOps
- **[PART-23-LLMOPS.md](PART-23-LLMOPS.md)** — Lifecycles, registries, experiment tracking, drift, rollback; and the QA vs MLOps vs LLMOps vs AI Engineering boundary

### Part 24 — AI Governance
- **[PART-24-AI-GOVERNANCE.md](PART-24-AI-GOVERNANCE.md)** — Responsible AI, NIST AI RMF, ISO/IEC 42001 and 23894, EU AI Act (current status), and what a QA engineer is actually accountable for

### Part 25 — Real-World Projects
- **[PART-25-PROJECTS.md](PART-25-PROJECTS.md)** — 8 progressive projects, each with architecture, test strategy, test plan, cases, data, automation, metrics, security, performance, CI/CD

### Part 26 — Test Case Library
- **[PART-26-TEST-CASE-LIBRARY.md](PART-26-TEST-CASE-LIBRARY.md)** — 200+ reusable test cases across 17 categories, fully specified

### Part 27 — Automation Examples
- **[PART-27-AUTOMATION-EXAMPLES.md](PART-27-AUTOMATION-EXAMPLES.md)** — Line-by-line explained Python for every testing type in this book

### Part 28 — Interview Preparation
- **[PART-28-INTERVIEW-PREP.md](PART-28-INTERVIEW-PREP.md)** — Beginner → expert questions with answers *and* why the answer is right

### Part 29 — Certifications
- **[PART-29-CERTIFICATIONS.md](PART-29-CERTIFICATIONS.md)** — Honest tiering; what is worth money and what is not

### Part 30 — Career Roadmap
- **[PART-30-CAREER-ROADMAP.md](PART-30-CAREER-ROADMAP.md)** — Traditional QA → Automation QA → GenAI QA → AI Quality Engineer → Senior → AI QA Architect

### Part 31 — Cheat Sheets
- **[PART-31-CHEAT-SHEETS.md](PART-31-CHEAT-SHEETS.md)** — Python, pytest, API, prompt, eval, RAG, vector DB, agents, security, OWASP, performance, Docker, Git, Linux, SQL, CI/CD, observability

### Appendices
- **[APPENDIX-A-GLOSSARY.md](APPENDIX-A-GLOSSARY.md)** — ~180 terms
- **[APPENDIX-B-TOOL-INDEX.md](APPENDIX-B-TOOL-INDEX.md)** — Full tool matrix: purpose, level, install, usage, limits, alternatives, deprecation status
- **[APPENDIX-C-RESOURCES.md](APPENDIX-C-RESOURCES.md)** — Primary sources only

---

## The one paragraph that matters most

Traditional testing asks *"does output equal the expected value?"* GenAI testing cannot ask that, because the same input does not produce the same output twice. So the question becomes *"does output score above a threshold, on a dataset, across repeated runs, on metrics that capture what we actually care about?"* Everything in this book — golden datasets, LLM-as-judge, faithfulness, red teaming, tracing, cost gates — is downstream of that single change. If you internalise nothing else, internalise this: **you are moving from assertions to measurements, and from single cases to distributions.**

---

## A note on currency

GenAI tooling changes faster than any documentation cycle. Everything in this book marked ⏳ was verified against primary sources on **8 September 2026**. Specific facts worth knowing are already in flux as of that date:

- **OWASP published a 2026 LLM Top 10** (August 2026) that significantly reorders the 2025 list and renames *System Prompt Leakage* to *Hidden Context Exposure*. Both versions are covered in Part 11 — many teams are still on the 2025 numbering.
- **OWASP Top 10 for Agentic Applications (ASI01–ASI10)** was published December 2025 and is now the reference for agent security.
- **`trulens_eval` is dead** — the package is `trulens`. Do not follow tutorials using the old name.
- **AutoGen and Semantic Kernel are in maintenance mode**, merged into **Microsoft Agent Framework** (1.0, April 2026).
- **EU AI Act high-risk obligations were deferred** to December 2027 by the Digital Omnibus.

Assume any tool version number in this book is stale and check the project's own docs. Assume the *concepts* are stable — they have barely moved in three years.
