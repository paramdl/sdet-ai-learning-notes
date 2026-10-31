# PART 30 — Career Roadmap

> **Goal of this part:** the path from where you are to AI QA Architect, with the skills, artefacts, and responsibilities that define each stage — and honest signals for when you have actually arrived at one.

---

## 30.1 The path

```
TRADITIONAL QA  →  AUTOMATION QA  →  GenAI QA  →  AI QUALITY ENGINEER
                                                          │
                                                          ▼
                                         SENIOR AI QA ENGINEER
                                                          │
                                                          ▼
                                              AI QA ARCHITECT
```

**Where you are:** you have Traditional and Automation QA, with real security-audit and API-testing experience. **You are entering at "GenAI QA" and moving toward "AI Quality Engineer".** The first two stages are described for completeness and because you will be asked to grow people through them.

---

## Stage 1 — Traditional QA

| | |
|---|---|
| **Skills** | Test design, boundary analysis, equivalence partitioning, exploratory testing, defect reporting, risk-based prioritisation |
| **Tools** | Test management, bug trackers, spreadsheets |
| **Programming** | None required |
| **Responsibilities** | Execute test plans, report defects, verify fixes |
| **Depth** | Understands *what* to test, not *how it works underneath* |

**The transferable core:** everything in this book depends on test design judgement. A GenAI tester who cannot design a boundary case is not helped by knowing what an embedding is.

---

## Stage 2 — Automation QA

| | |
|---|---|
| **Skills** | Framework design, page objects, API testing, CI integration, flakiness management, test data management |
| **Tools** | Playwright/Selenium, pytest/TestNG, Postman, Git, Jenkins/GitHub Actions |
| **Programming** | Working proficiency in one language |
| **Responsibilities** | Build and maintain suites, own CI test stability, review test code |
| **Depth** | Reads application code; debugs failures independently |

**What carries forward directly:** pytest, API testing, CI, fault injection with mocks, and flakiness discipline. Roughly 60% of GenAI QA is this stage's skillset pointed at a new target.

---

## Stage 3 — GenAI QA

> **You are here (entering).** Typically 6–12 months to be solid.

| | |
|---|---|
| **New skills** | LLM fundamentals, prompt testing, non-deterministic assertion design, basic evaluation, GenAI API testing (streaming, tokens, cost), prompt injection basics |
| **New tools** | promptfoo, DeepEval, an LLM provider SDK, Ollama, a tracing tool |
| **Programming** | Python at intermediate level; async for eval throughput |
| **Projects** | Part 25 Projects 1–3 |
| **Responsibilities** | Test AI features within a team; build the first golden dataset; run evals; report AI-specific defects |
| **Depth** | Can explain why exact-match fails and what replaces it; can run an eval suite someone else designed |

**Signals you have arrived:**
- You have shipped a golden dataset that found a real bug
- You automatically check `finish_reason`, config parity, and cost on every AI feature
- You stop saying "the model is inconsistent" and start measuring which kind of inconsistency it is

**Signals you are not there yet:**
- Your assertions are still exact-match with retries
- You have never run the same test twenty times to see what happens
- You cannot say what your similarity threshold is based on

---

## Stage 4 — AI Quality Engineer

> Typically 12–24 months in. **The target role for most people reading this.**

| | |
|---|---|
| **New skills** | Evaluation design, **judge validation**, RAG stage-isolated testing, retrieval metrics, agent trajectory testing, guardrail four-corpus method, cost gating, security testing to the OWASP lists |
| **New tools** | Ragas, Langfuse/Phoenix, garak or promptfoo redteam, a vector DB, pgvector |
| **Programming** | Confident Python; SQL; Docker; enough Bash to work in a container |
| **Projects** | Part 25 Projects 4–6 |
| **Responsibilities** | **Own the quality strategy for an AI product.** Design evals, set thresholds, own the release gate, run red teams, report to stakeholders |
| **Depth** | Can localise a failure to a specific pipeline stage; can defend every threshold |

**Signals you have arrived:**
- You have validated a judge and published the kappa
- You can look at Precision/Recall and immediately recommend the right architectural fix
- Your CI has a cost gate that has actually blocked a merge
- A developer has said "I hadn't thought of that" about one of your findings

**The differentiator at this stage is judgement, not coverage.** Anyone can add more tests. Knowing which twenty tests matter, and saying so, is the job.

---

## Stage 5 — Senior AI QA Engineer

> Typically 2–4 years in.

| | |
|---|---|
| **New skills** | Multi-system strategy, observability design, LLMOps integration, model selection methodology, governance evidence, mentoring, influencing architecture |
| **New tools** | OpenTelemetry, k6/Locust at scale, cloud AI platforms, PyRIT or equivalent |
| **Programming** | Builds reusable frameworks others adopt; reviews others' test code |
| **Projects** | Part 25 Projects 7–8 |
| **Responsibilities** | Quality across multiple AI products; define standards; mentor; represent quality in design reviews; own the evidence pack |
| **Depth** | Shapes architecture — advocates shadow deployment, containment over filtering, runtime permission enforcement |

**Signals you have arrived:**
- Your framework is used by teams you are not on
- You have changed an architectural decision by presenting evidence
- You are consulted *before* a feature is built, not after
- You can say "we should not ship this" and be listened to

**The shift at this stage:** from finding defects to preventing them by influencing design. The tool-inventory audit (Part 9) and the write-path enumeration (Part 11) are examples — both find critical issues by reading configuration, before a single test runs.

---

## Stage 6 — AI QA Architect

> Typically 4+ years in, and not a role every organisation has.

| | |
|---|---|
| **Skills** | Quality strategy at organisation scale; framework and platform design; risk modelling; governance and audit readiness; vendor and model evaluation; hiring and capability building |
| **Programming** | Designs systems; codes selectively |
| **Responsibilities** | Set the organisation's AI quality standards; own the evidence that satisfies regulators, auditors, and enterprise customers; decide build-vs-buy for quality tooling; grow the team |
| **Depth** | Fluent across ML, security, compliance, and product; translates between them |

**Signals you have arrived:**
- Legal or compliance comes to you before they come to engineering
- You have defined what "tested" means for AI at your organisation, in writing
- You hire and develop AI QA engineers
- Your evidence pack has survived an external audit or a large customer's security review

---

## 30.2 Specialisation branches

From Stage 4, three credible specialisations. Pick one deliberately rather than drifting.

### AI Security / Red Team Specialist
**Path:** Parts 11–13 to expert depth; garak, PyRIT, promptfoo redteam; both OWASP lists cold; build an attack corpus; publish (responsibly).
**Market:** currently the highest-paid branch, and the most under-supplied.
**Risk:** narrower role; you need a security team to belong to, and authorisation discipline is non-negotiable.

### Evaluation / Measurement Specialist
**Path:** Part 6 to expert depth; statistics for judge validation and significance; dataset methodology; online eval; experiment design.
**Market:** every serious AI product eventually needs this person.
**Risk:** the most intellectually demanding branch; needs an organisation mature enough to value measurement.

### AI Platform Quality / LLMOps-adjacent
**Path:** Parts 15, 20–23 to depth; Kubernetes, observability, CI/CD platform, cost engineering.
**Market:** stable, well-paid, closest to traditional SRE.
**Risk:** drifts away from testing toward operations.

**Given your existing portfolio** — API testing, security audits, and multi-client QA — the security branch is the shortest step and the strongest market. The evaluation branch is the more durable long-term differentiator. Doing security first and evaluation second is a coherent two-year plan.

---

## 30.3 The 24-month plan

| Months | Focus | Artefact |
|---|---|---|
| 1–3 | LLM fundamentals, prompt testing, GenAI API testing | Projects 1–2; a determinism baseline published |
| 4–6 | Evaluation, judge validation | Project 3; **judge validated with kappa** |
| 7–10 | RAG and vector DB | Project 4; a chunking decision table |
| 11–13 | Security and red teaming | Project 5 + a red-team report |
| 14–17 | Agents and multimodal | Projects 6–7 |
| 18–21 | Observability, CI/CD, cost, performance | Project 8 pipeline |
| 22–24 | Governance, evidence pack, specialisation | Project 8 complete; a public portfolio |

**At month 6 you are employable as a GenAI QA engineer. At month 13 you are employable as an AI Quality Engineer.** Everything after that is depth and specialisation.

---

## 30.4 Positioning yourself

**On a CV, lead with method:**
> *Built and own the evaluation suite for a RAG customer assistant: 120-case golden dataset sourced from production failures, LLM-as-judge validated at Cohen's kappa 0.78 against human labels, faithfulness and retrieval metrics gated in CI with a cost budget. Red-teamed to the OWASP LLM Top 10; found and reported an indirect prompt injection chain enabling zero-click exfiltration.*

That paragraph contains: dataset methodology, judge validation, specific metrics, CI integration, cost awareness, a security framework, and a real finding. Compare it to *"experience testing AI applications using promptfoo and DeepEval."*

**In conversation, lead with the number nobody else has:** the kappa, the injection success rate, the cost per resolved task, the determinism baseline. Specific measured numbers are the fastest way to demonstrate you have actually done this.

---

## 30.5 Staying current

The field moves; the fundamentals do not. A sustainable routine:

| Cadence | Activity |
|---|---|
| Weekly | Read the release notes of the 2–3 tools you actually use |
| Monthly | Re-check one volatile fact in this handbook against its primary source |
| Quarterly | Re-run the golden-set representativeness test on your own projects; skim the OWASP GenAI project for updates |
| Annually | Re-read Parts 1–3; the fundamentals are the thing that stops you chasing tools |

**The filter for new tools** (from the earlier tools discussion): does it produce a score against a dataset, can it run in CI unattended, and does it show you the failing trace? Anything failing all three is a dashboard, not a testing tool.

---

**Next:** [PART-31-CHEAT-SHEETS.md](PART-31-CHEAT-SHEETS.md)
