# SDET + AI Quality Engineer — 3 Month Roadmap

**Start:** 2026-09-23
**End:** 2026-12-23 (13 weeks)
**Daily commitment:** 2–3 h/day. Missed days are covered on the weekend — that is the rule, not the exception.
**Total budget:** ~225 hours

---

## The one question you asked: do I need Python?

**Yes, but only a slice of it — about 20 hours.**

| Language | Role in this plan | Depth needed |
|---|---|---|
| **TypeScript** | Primary. Playwright, promptfoo, all your existing framework work | Deep — this is your interview language |
| **Python** | Secondary. DeepEval, RAGAS, notebooks, most LLM eval tooling | Working knowledge — read it, write scripts, run pytest |

Why you can't skip Python entirely: the LLM evaluation ecosystem is Python-first. `promptfoo` is TS/YAML and covers a lot, but `DeepEval`, `RAGAS`, and almost every eval notebook you'll be asked about in an interview are Python. You need to be able to open one, understand it, and modify it.

Why you shouldn't go deeper than that: two full language tracks inside 13 weeks means you'd be mediocre at both. Stay excellent in TypeScript; be functional in Python.

---

## Folder map

```
SDET-AI-Roadmap/
├── README.md                          ← you are here
├── SCHEDULE.md                        ← week-by-week plan
│
├── 01-TypeScript-Playwright/
│   ├── 01-typescript-core.md          syntax, types, generics, async
│   ├── 02-oops-realtime.md            OOP mapped to real Playwright code
│   ├── 03-playwright-commands.md      full CLI + API reference
│   ├── 04-practice-programs.md        40 programs, easy → hard
│   └── 05-interview-questions.md      TS + Playwright Q&A
│
├── 02-DevOps/
│   ├── 01-git-commands.md             complete command reference + Q&A
│   ├── 02-docker-commands.md          commands, Dockerfile, compose + Q&A
│   ├── 03-jenkins.md                  setup, Jenkinsfile, commands + Q&A
│   └── 04-kubernetes-highlevel.md     concepts + essential kubectl
│
├── 03-LLM/
│   ├── 01-python-for-llm.md           the 20-hour Python slice
│   ├── 02-llm-theory-notes.md         concepts, theory, study notes
│   ├── 03-llm-testing-evaluation.md   promptfoo, DeepEval, RAG eval, red-teaming
│   └── 04-llm-interview-questions.md  Q&A
│
└── 04-Project/
    └── capstone-project.md            the thing you show in interviews
```

---

## How to use this

1. **Follow `SCHEDULE.md`.** Don't jump ahead. The order is deliberate — TypeScript before Playwright patterns, Docker before Jenkins, Python before DeepEval.
2. **Type every command.** Don't copy-paste. Muscle memory is the point.
3. **Every program in `04-practice-programs.md` gets written by you first**, then compared to the solution. Reading solutions teaches you nothing.
4. **Commit daily.** The capstone repo's commit history is itself interview evidence — it shows consistency.
5. **Log misses.** Keep a line in your notes: `2026-10-04 — missed, covered Sat 2h`. If you're missing more than two days a week, the plan is too big and we cut Track D.

---

## Phase structure

| Phase | Weeks | Focus | Deliverable |
|---|---|---|---|
| **1** | 1–4 | TypeScript deep + OOP + Playwright patterns | Rebuilt framework with proper POM |
| **2** | 5–7 | Git, Docker, Jenkins, Kubernetes basics | Framework runs containerised in CI |
| **3** | 8–11 | Python slice + LLM theory + LLM evaluation | Working eval harness with golden dataset |
| **4** | 12–13 | Capstone integration + interview prep | Two public repos + rewritten CV |

---

## What success looks like at the end

You can walk into an interview and say:

> "I built a test platform that runs Playwright and API suites in Docker, gated by Jenkins, and it includes an LLM evaluation layer with a golden dataset and an LLM-as-judge scorer that catches regressions in non-deterministic output. Here's the repo."

Very few QA candidates in Bengaluru can say that sentence. That's the whole point of the next 13 weeks.

**Target outcome:** an SDET or AI Quality Engineer role at a product company.
