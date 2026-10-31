# 13-Week Schedule

**Start:** Wed 2026-09-23 · **End:** Wed 2026-12-23
**Weekday:** 2–3 h/day · **Weekend:** catch-up buffer for anything missed
**Total:** ~225 hours

---

## How the weekend rule works

Weekdays carry the plan. Saturday and Sunday are **buffer, not extra scope**.

- Missed a weekday → repay it on the weekend.
- Missed nothing → take the weekend off, or do DSA only.
- Missing 3+ weekdays two weeks running → the plan is too big. Cut Week 7 (Kubernetes/Jenkins depth) first, then reduce LLM red-teaming scope. **Do not cut the capstone.**

Log it. One line per day in `progress.md`:
```
2026-09-24  2.5h  TS generics + P07-P08          ✅
2026-09-25  0h    client escalation               ❌ → repay Sat
2026-09-27  3h    repaid: P07-P08, started P09    ✅
```

---

## Phase 1 — TypeScript & Playwright (Weeks 1–4, ~68h)

### Week 1 · Sep 23–29 — TypeScript core
| Day | ~2.5h | Reference |
|---|---|---|
| Mon | Setup, tsconfig strict, types, arrays, tuples | `01-typescript-core.md` §1–2 |
| Tue | Interfaces vs types, unions, narrowing, type guards | §3–4 |
| Wed | Functions, optional/default/rest params, overloads | §5 |
| Thu | **Generics** — constraints, `keyof`, generic classes | §6 |
| Fri | Utility types, `Partial`/`Pick`/`Omit`/`Record` | §7 |
| Weekend | P01–P06 | `04-practice-programs.md` |

**Deliverable:** 6 programs, zero `any`, `tsc --noEmit` clean.

### Week 2 · Sep 30–Oct 6 — TypeScript advanced + OOP
| Day | ~2.5h |
|---|---|
| Mon | Mapped & conditional types, `infer`, template literals |
| Tue | Async, promises, typed error handling, custom Error classes |
| Wed | Classes, access modifiers, `readonly`, parameter properties |
| Thu | **Abstract classes, inheritance, `super`, `override`** |
| Fri | **Polymorphism + composition over inheritance** |
| Weekend | P07–P12 |

**Deliverable:** the `PaymentMethod` polymorphism example working, written from scratch.

### Week 3 · Oct 7–13 — Playwright fundamentals
| Day | ~2.5h | Reference |
|---|---|---|
| Mon | Install, config, CLI flags, UI mode | `03-playwright-commands.md` §1–4 |
| Tue | Locators — role/label/text only, filtering, chaining | §5 |
| Wed | Actions, keyboard, file upload, select | §6 |
| Thu | Assertions, auto-retry, soft, `poll`, `toPass` | §7 |
| Fri | Waiting properly, hooks, test organisation, tags | §8–9 |
| Weekend | P27–P30 + DSA P13–P16 |

**Deliverable:** 5 tests green, run 10× with zero flake.

### Week 4 · Oct 14–20 — Playwright advanced
| Day | ~2.5h |
|---|---|
| Mon | **Fixtures** — test scope, worker scope, teardown |
| Tue | Auth via `storageState`, setup projects, multi-role |
| Wed | API testing with the `request` fixture |
| Thu | Network mocking, interception, HAR |
| Fri | Contexts, frames, dialogs, downloads |
| Weekend | P31–P34 + DSA P17–P21 |

**Deliverable:** working two-role auth setup, API suite with negative cases.

---

## Phase 2 — DevOps (Weeks 5–7, ~50h)

### Week 5 · Oct 21–27 — Framework build + Git
| Day | ~2.5h |
|---|---|
| Mon | P35 — POM from scratch |
| Tue | P36 — component objects, prove reuse |
| Wed | P37 — custom fixtures, remove all `new Page()` from specs |
| Thu | Git: branching, merge vs rebase, conflicts | `01-git-commands.md` |
| Fri | Git: reset vs revert, stash, reflog recovery, `bisect run` |
| Weekend | P38–P40 + DSA P22–P26 |

**Deliverable:** full harness from P40. This becomes the capstone base.

### Week 6 · Oct 28–Nov 3 — Docker
| Day | ~2.5h | Reference |
|---|---|---|
| Mon | Images, containers, lifecycle, exec, logs | `02-docker-commands.md` §1–3 |
| Tue | **Dockerfile for Playwright**, layer caching, `.dockerignore` | §4–5 |
| Wed | Volumes, networks, service-name DNS | §6 |
| Thu | **Docker Compose**: app + db + tests | §7 |
| Fri | `--exit-code-from`, report volumes, the `/dev/shm` fix | §9 |
| Weekend | Catch-up + Docker interview questions |

**Deliverable:** `docker compose up` runs your full suite and exits with its code.

### Week 7 · Nov 4–10 — CI + Kubernetes
| Day | ~2.5h |
|---|---|
| Mon | Jenkins in Docker, plugins, first pipeline job |
| Tue | Jenkinsfile: stages, parameters, credentials, `post` |
| Wed | Jenkins: parallel shards, HTML + JUnit publishing |
| Thu | GitHub Actions: matrix sharding, blob report merging |
| Fri | **Kubernetes — all 8 hours compressed here.** Concepts, kubectl, run suite as a Job |
| Weekend | Catch-up. **Take a break if you're on track.** |

**Deliverable:** same suite green in both Jenkins and GitHub Actions.

> Week 7 is the heaviest and the most cuttable. If you're behind, do Jenkins basics + GitHub Actions properly and give Kubernetes 3 hours of reading only.

---

## Phase 3 — Python & LLM (Weeks 8–11, ~70h)

### Week 8 · Nov 11–17 — Python + LLM theory
| Day | ~2.5h | Reference |
|---|---|---|
| Mon | venv, pip, syntax deltas from TS, collections | `01-python-for-llm.md` §2–3 |
| Tue | Comprehensions, classes, dataclasses, files | §3 |
| Wed | **pytest**: fixtures, parametrize, markers | §4 |
| Thu | LLM API calls, structured output, cost tracking | §5 |
| Fri | **Theory:** tokens, context window, temperature, embeddings | `02-llm-theory-notes.md` §1–5 |
| Weekend | PY01–PY08 |

**Deliverable:** Python script querying 20 prompts, caching to disk, with token counts.

### Week 9 · Nov 18–24 — RAG theory + promptfoo
| Day | ~2.5h |
|---|---|
| Mon | **Theory:** prompting, RAG pipeline, failure modes per stage |
| Tue | **Theory:** agents, hallucination, evaluation families |
| Wed | promptfoo: install, config, assertion types |
| Thu | promptfoo: A/B two prompt versions, `llm-rubric`, `--repeat` |
| Fri | **Build the golden dataset** — 50 cases, all six categories |
| Weekend | Hand-label 30 cases for calibration |

**Deliverable:** `data/golden.json` with 50 cases; `data/human-labels.json` with 30.

### Week 10 · Nov 25–Dec 1 — Evaluation depth
| Day | ~2.5h | Reference |
|---|---|---|
| Mon | DeepEval: metrics, `assert_test`, G-Eval custom rubric | `03-llm-testing-evaluation.md` §3 |
| Tue | RAGAS: faithfulness, context precision/recall | §4 |
| Wed | **Judge calibration — measure Cohen's kappa** | §6 |
| Thu | Non-determinism: baseline variance, `--repeat`, thresholds | §7 |
| Fri | Build the TypeScript eval runner + scorers | §8 |
| Weekend | Capstone Week 10 tasks — app scaffold |

**Deliverable:** calibrated judge with kappa reported honestly.

### Week 11 · Dec 2–8 — Security + capstone framework
| Day | ~2.5h |
|---|---|
| Mon | OWASP LLM Top 10; prompt injection theory |
| Tue | Red-team suite: jailbreaks, extraction, encoding bypass |
| Wed | **Indirect injection via poisoned knowledge-base doc** |
| Thu | Agent trajectory testing, failure injection |
| Fri | CI integration: threshold gates, PR comments |
| Weekend | Capstone Week 11 tasks — page objects, components, fixtures |

**Deliverable:** red-team suite green; CI fails correctly on a threshold breach.

---

## Phase 4 — Capstone & interviews (Weeks 12–13, ~37h)

### Week 12 · Dec 9–15 — Build
| Day | ~3h |
|---|---|
| Mon | Golden dataset wired into the runner; 3× repeat working |
| Tue | RAG tests — retrieval and generation asserted separately |
| Wed | HTML report: pass rate, flake, cost, p95 latency |
| Thu | Dockerfile + compose for the whole platform |
| Fri | GitHub Actions: both workflows green |
| Weekend | **Plant the three bugs, prove the suite catches them, screenshot CI** |

### Week 13 · Dec 16–23 — Package & apply
| Day | ~3h |
|---|---|
| Mon | README — especially the "testing non-deterministic output" section |
| Tue | Second repo: productionise `QA-Framework-Template` |
| Wed | Write the methodology post; publish |
| Thu | CV rewrite → **SDET / AI Quality Engineer**; LinkedIn headline |
| Fri | Interview prep: TS + Playwright Q&A out loud |
| Weekend | LLM Q&A out loud; mock interview; **start applying** |

---

## Parallel track — DSA

**30 min/day from Week 3 onward, every weekday.** Non-negotiable.

| Weeks | Target | Cumulative |
|---|---|---|
| 3–4 | P13–P21 | ~20 problems |
| 5–7 | P22–P26 + LeetCode easy | ~55 |
| 8–10 | LeetCode medium: arrays, strings, hashmaps | ~90 |
| 11–13 | Mixed medium + mock rounds | ~120 |

🔑 This is the gate most QA engineers fail. Everything else in this plan gets you the interview; this is what stops you losing it in round two.

---

## Milestones

| Week | Checkpoint | Done? |
|---|---|---|
| 2 | TypeScript OOP solid — abstract classes, polymorphism, composition | ☐ |
| 4 | Playwright fixtures + auth + API testing working | ☐ |
| 5 | Full test harness built (P40) | ☐ |
| 6 | Suite runs in Docker | ☐ |
| 7 | Suite runs in Jenkins and GitHub Actions | ☐ |
| 8 | Python + pytest working; LLM API calls with cost tracking | ☐ |
| 9 | 50-case golden dataset built | ☐ |
| 10 | Judge calibrated, kappa measured | ☐ |
| 11 | Red-team suite including indirect injection | ☐ |
| 12 | Capstone green in CI; three bugs caught and screenshotted | ☐ |
| 13 | Two public repos, post published, CV rewritten, applications out | ☐ |

---

## Weekly hour budget

| Phase | Weeks | Hours |
|---|---|---|
| TypeScript & Playwright | 1–4 | 68 |
| DevOps | 5–7 | 50 |
| Python & LLM | 8–11 | 70 |
| Capstone & interviews | 12–13 | 37 |
| **Total** | **13** | **225** |

---

## If you fall behind — cut in this order

1. Kubernetes depth → reading only, 3h
2. Visual regression testing
3. Jenkins → GitHub Actions only (most product companies use Actions anyway)
4. RAGAS → DeepEval alone is enough
5. The second repo

**Never cut:** DSA, the golden dataset, judge calibration, the red-team suite, the capstone README.

🔑 Those five are the entire differentiator. Everything else is table stakes that any competent QA engineer can also claim.
