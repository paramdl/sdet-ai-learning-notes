# Capstone Project — "Sentinel"

> A test platform that validates a conventional web app **and** an AI feature, running containerised in CI, with an LLM evaluation layer.
>
> This is the artefact you put at the top of your CV. It proves TypeScript, OOP, Playwright, API testing, Docker, CI, Python, and LLM evaluation in one repository — which is exactly the combination that almost nobody in the Bengaluru QA market can show.

---

## 1. Why this project

Interviewers don't believe claims; they believe repos. A hiring manager scanning your GitHub for ninety seconds should be able to see:

- You write real TypeScript, not JavaScript with types bolted on
- You understand framework architecture, not just test scripts
- You can containerise and run things in CI
- You can test a non-deterministic system rigorously

The last one is the differentiator. The first three get you to an SDET interview; the fourth gets you the AI Quality Engineer salary band.

---

## 2. System under test

You need an app with both conventional flows and an AI feature. Pick one:

**Option A — build a small one (recommended).** A "Support Desk" app: ticket list, ticket detail, login, and an AI assistant that answers questions from a knowledge base of markdown documents. About 300 lines of Next.js. You control the bugs, which means you can demonstrate the tests catching them.

**Option B — use an existing open-source app** with an AI feature bolted on.

**Option C — use your own prior work.** You may already have AI-product testing experience from client work. 🔑 If you use client systems, **sanitise completely** — no real hostnames, no credentials, no client names, no real findings. Rebuild the *pattern*, not the artefact.

**Recommendation: Option A.** Full control, no confidentiality risk, and "I built the app and the harness" is a stronger story.

---

## 3. Repository structure

```
sentinel/
├── README.md                       ← the most important file. see §7
├── docker-compose.yml
├── Dockerfile.playwright
├── Dockerfile.app
├── playwright.config.ts
├── package.json
├── tsconfig.json
├── .github/workflows/
│   ├── e2e.yml
│   └── llm-eval.yml
│
├── app/                            the system under test
│   ├── pages/
│   ├── api/
│   └── knowledge-base/             markdown docs for RAG
│
├── src/
│   ├── pages/                      page objects
│   │   ├── BasePage.ts             abstract
│   │   ├── LoginPage.ts
│   │   ├── TicketListPage.ts
│   │   └── AssistantPage.ts
│   ├── components/                 composed UI parts
│   │   ├── TableComponent.ts
│   │   ├── ModalComponent.ts
│   │   └── ChatComponent.ts
│   ├── api/
│   │   ├── ApiClient.ts            generic typed client
│   │   └── TicketApi.ts
│   ├── data/
│   │   ├── TicketBuilder.ts        builder pattern
│   │   └── UserFactory.ts
│   ├── fixtures/
│   │   └── index.ts                custom Playwright fixtures
│   └── eval/                       ← the differentiator
│       ├── types.ts
│       ├── scorers.ts              similarity, llm-judge, refusal detection
│       ├── runner.ts
│       ├── report.ts
│       └── thresholds.json
│
├── tests/
│   ├── e2e/
│   ├── api/
│   ├── visual/
│   └── llm/
│       ├── quality.spec.ts
│       ├── rag.spec.ts
│       └── redteam.spec.ts
│
├── data/
│   ├── golden.json                 50+ curated cases
│   ├── human-labels.json           30 hand-scored, for judge calibration
│   └── redteam-attacks.yaml
│
└── python/                         the Python slice
    ├── requirements.txt
    ├── conftest.py
    ├── test_deepeval_metrics.py
    └── calibrate_judge.py
```

---

## 4. Build order — four weeks

### Week 10 — foundation
- [ ] Scaffold the app with login, ticket list, ticket detail, and a REST API
- [ ] Add the AI assistant: knowledge base of 10–15 markdown docs, embedding + retrieval, chat endpoint
- [ ] Seed data and a reset endpoint so tests start clean
- [ ] Repo initialised, `.gitignore`, `.dockerignore`, README skeleton

### Week 11 — the test framework
- [ ] `BasePage` abstract with two abstract members
- [ ] Four page objects, all locators private
- [ ] Three components, composed into pages (prove reuse — same `TableComponent` on two pages)
- [ ] Custom fixtures: authenticated page, each page object, worker-scoped API token
- [ ] `storageState` auth for two roles via a setup project
- [ ] Typed `ApiClient<T>` and full CRUD API tests with negative cases
- [ ] Data builders using the builder pattern
- [ ] Data-driven tests from JSON
- [ ] Visual regression on two pages, baselines generated in Docker

### Week 12 — the LLM evaluation layer
- [ ] Golden dataset: 50 cases across all six categories
- [ ] Hand-label 30 cases for calibration
- [ ] Scorers: semantic similarity, LLM-as-judge, refusal detection
- [ ] Runner with `--repeat 3` and per-case stability tracking
- [ ] **Judge calibration script — report Cohen's kappa in the README**
- [ ] RAG tests: retrieval and generation asserted separately
- [ ] Red-team suite including **indirect injection via a poisoned knowledge-base doc**
- [ ] HTML report: pass rates, flake detection, cost, p95 latency
- [ ] Python side: DeepEval faithfulness and relevancy metrics via pytest

### Week 13 — ship it
- [ ] `Dockerfile.playwright` pinned to the Playwright version
- [ ] `docker-compose.yml`: app + db + tests on one network, `--exit-code-from tests`
- [ ] GitHub Actions: e2e sharded 4 ways with merged blob reports
- [ ] GitHub Actions: llm-eval with threshold gates and PR comment
- [ ] **Deliberately introduce three bugs on a branch and prove the suite catches them** — screenshot this for the README
- [ ] README finished (§7)
- [ ] One written post on the methodology

---

## 5. Requirements that make it credible

These are the details interviewers actually probe.

**Architecture**
- Zero `any` in the codebase. `strict: true`, `npx tsc --noEmit` passes.
- No selectors in any spec file. Grep for `page.locator(` under `tests/` — should return nothing.
- Composition over inheritance — at most two levels of page inheritance.

**Rigour**
- Every LLM case runs 3×; results report mean and standard deviation.
- Judge calibrated against human labels, kappa reported honestly. 🔑 If your kappa is 0.55, **publish 0.55 and say the rubric needs work.** An honest weak number beats a suspiciously perfect one — and interviewers test exactly this.
- Safety thresholds at 1.00, quality thresholds statistical.
- Retrieval and generation asserted separately.

**Operations**
- Runs green in Docker and in CI, not only on your machine.
- Visual baselines generated in the same image CI uses.
- Total CI run under 10 minutes.
- Cost per full eval run stated in the README.

---

## 6. The three bugs to plant

This is the demo that closes interviews. On a branch, introduce:

1. **A conventional bug** — an off-by-one in ticket pagination. Caught by an E2E test.
2. **A RAG retrieval bug** — reduce top-k from 5 to 1. Context recall drops; faithfulness holds. 🔑 This demonstrates *why* you test the stages separately: the final answer often still looks plausible while recall has collapsed.
3. **A safety regression** — soften the system prompt's refusal instruction. Unanswerable-question refusal rate falls; the red-team suite goes red.

Screenshot each failing CI run. Put all three in the README. You now have a concrete, demonstrable answer to "tell me about a time your tests caught something."

---

## 7. The README — write this carefully

Most of your interview value is in this one file. Structure:

```markdown
# Sentinel — Test Platform for Web + AI Systems

One paragraph: what it tests, what makes it different.

## What this demonstrates
- TypeScript test framework: POM, components, fixtures, builders
- API + E2E + visual coverage
- **LLM evaluation: golden dataset, calibrated judge, RAG stage isolation, red-teaming**
- Containerised, sharded, CI-gated

## Results
| Metric | Value |
|---|---|
| E2E tests | 48 |
| API tests | 32 |
| LLM golden cases | 54 (× 3 runs) |
| Judge agreement (Cohen's κ) | 0.71 |
| Full CI run | 8m 20s |
| Cost per eval run | $0.34 |

## Architecture
<a diagram. hand-drawn is fine.>

## The interesting part: testing non-deterministic output
<300 words. Baseline variance, threshold assertions, why safety
gates at 100% and quality at 90%, why the judge needed calibrating.>

## Bugs caught
<the three planted bugs, with CI screenshots>

## Running it
docker compose up --build --abort-on-container-exit --exit-code-from tests
```

🔑 The "interesting part" section is what gets read. Write it last, write it well, and make it about **judgement**, not tooling. Anyone can list libraries; very few can explain why a safety test that passes 95% of the time is a failing test.

---

## 8. After it's built

**Second repo:** productionise your existing `QA-Framework-Template` — containerised, CI-wired, documented. Two repos showing different things beats one showing everything.

**The written post:** "Testing systems that give different answers every time." Draw on your real experience — you have genuinely done AI-product QA. Publish on LinkedIn and dev.to. It's interview material and it's discoverable by recruiters.

**CV positioning:** the title line becomes **SDET / AI Quality Engineer**, not QA Engineer. Lead with the capstone, then your security findings, then years of experience. 🔑 Your CORS-any-origin, rate-limit, and enumeration findings are strong — but frame them as *impact*, not as a bug list.

---

## 9. Scope discipline

**In scope:** everything above.

**Out of scope — resist these:**
- Making the app under test good. It's a test fixture, not a product.
- Performance/load testing. Different skill, different sprint.
- Mobile. No.
- Training or fine-tuning a model. You are testing them, not building them.
- Kubernetes deployment of the capstone. Overkill; your 8 hours of K8s is for interviews.
- A second AI feature. One RAG assistant, tested deeply, beats three tested shallowly.

🔑 The failure mode for this project is scope creep — you spend week 13 polishing the app's CSS and ship no eval layer. The eval layer is the entire point. If you run out of time, cut visual regression, cut a page object, cut the app's styling. **Never cut the LLM evaluation work.**

---

**Next:** `../SCHEDULE.md`
