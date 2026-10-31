# PART 23 — LLMOps / MLOps Fundamentals

> **Goal of this part:** understand the operational discipline your testing plugs into, and be able to state clearly where your role ends and another begins. Role confusion is the most common source of untested gaps in AI teams — everyone assumes someone else owns evaluation.

---

## 23.1 The four roles, distinguished

| Role | Owns | Ships | Success measured by |
|---|---|---|---|
| **AI Engineer** | The application: prompts, RAG pipeline, agent logic, tool integration | Features | Feature works, users adopt it |
| **MLOps Engineer** | Infrastructure for models: training, serving, scaling, deployment | Platform | Uptime, throughput, cost efficiency |
| **LLMOps Engineer** | The LLM-specific operational layer: prompt management, eval infrastructure, tracing, model routing | Operational tooling | Deploys are safe and observable |
| **AI Quality Engineer (you)** | **Evidence that it works, and evidence of how it fails** | Test suites, evals, findings, gates | Defects found before users find them; releases are decidable |

**The overlap is real and worth naming explicitly.** In a small team, one person does all four. In a large one, the boundaries blur most around evaluation infrastructure — LLMOps builds the eval platform; you build the datasets, metrics, and thresholds that run on it, and you own the verdict.

**The sentence to have ready in an interview:** *"LLMOps owns the pipeline that runs the evaluation. I own what the evaluation measures, whether it is valid, and what its result means for the release."*

---

## 23.2 The four lifecycles

A GenAI product has four artefacts that version independently, and each needs its own quality gate. Teams that manage only one of them have gaps.

```
MODEL LIFECYCLE       select → evaluate → deploy → monitor → upgrade → deprecate
PROMPT LIFECYCLE      draft → review → eval → deploy → monitor → iterate → rollback
DATA LIFECYCLE        ingest → validate → chunk → embed → index → refresh → retire
EVAL LIFECYCLE        define → build dataset → calibrate judge → baseline → gate → evolve
```

**The insight that makes you useful:** any of the four can change without the others. A prompt edit with no code change; a corpus refresh with no deploy; a provider silently updating a model. **Each needs its own trigger and its own regression suite** (Part 19 §19.2). A CI pipeline that only runs on code commits misses three of the four.

---

## 23.3 Prompt lifecycle management 🔴

The lifecycle most often unmanaged, and where a QA engineer can add the most process value fastest.

| Practice | Test |
|---|---|
| Prompts in version control | Assert the deployed prompt hash matches a committed file |
| Prompt versions are immutable and identified | Every request logs `prompt_version` |
| Review required before deployment | Process check |
| **Eval gate before deployment** | Part 19 §19.3 suite 1 |
| Rollback independent of code | Can you revert a prompt in one action? Test it |
| A/B capability | Two versions serving simultaneously, comparable |
| Deployed prompt is traceable from any response | Given a support ticket, can you retrieve the exact prompt? |

```
TC-OPS-001  Prompt rollback
Steps:      1. Deploy prompt v3.3
            2. Trigger a rollback to v3.2
            3. Verify: responses reflect v3.2, logs record v3.2, and
               the rollback took under N minutes without a code deploy
Expected:   Clean, fast, independently auditable
Failure:    Rollback requires a code deploy → mean time to recovery for
            a prompt incident is measured in hours, not minutes
Priority:   High
```

---

## 23.4 Model registry and experiment tracking 🟠

| Concept | What it holds | Your interest |
|---|---|---|
| **Model registry** | Versioned models with stage tags (staging/production) and lineage | Which version is serving? Is it the one you certified? |
| **Experiment tracking** | Runs, parameters, metrics, artefacts | Where your eval results should live, so they are comparable over time |
| **Dataset registry** | Versioned datasets | Which dataset produced which result (Part 17 §17.6) |
| **Feature store** | Precomputed features | Mostly classical ML; rarely relevant to GenAI QA |

Tools: MLflow, Weights & Biases, Vertex AI Model Registry, SageMaker Model Registry, Langfuse (for prompts and eval).

**The QA-relevant test:** `TC-OPS-002` — assert that the model/prompt/dataset versions recorded in the production deployment match the versions in the release record. Version drift between what you tested and what shipped is a class of incident that nobody catches until it causes a visible failure.

---

## 23.5 Deployment strategies and what each lets you test

| Strategy | How it works | Testing value |
|---|---|---|
| **Shadow / mirror** | New version receives a copy of real traffic; output discarded | **The safest and most underused.** Compare new vs current on real traffic with zero user risk |
| **Canary** | Small % of real traffic to the new version | Real signal, limited blast radius. Needs per-version metrics |
| **A/B** | Split traffic, compare outcomes | Statistically comparable quality and business metrics |
| **Blue/green** | Two full environments, instant switch | Fast rollback |
| **Feature flag** | Per-user or per-segment toggle | Fine-grained control; enables internal-only rollout |

**Shadow deployment is the strategy to advocate for.** It is the only way to evaluate a model or prompt change against *real production traffic distribution* before any user is exposed — which directly addresses the golden-set representativeness problem from Part 17 §17.5.

```
TC-OPS-003  Shadow comparison
Method:     Mirror 100% of traffic to the candidate version for 48 hours.
            Score both outputs with online eval (Part 15 §15.7).
Report:     Per-category quality delta, cost delta, latency delta, and
            the specific queries where the candidate is worse
Value:      Converts a release decision from a judgement call into a
            measurement on real data
```

---

## 23.6 Drift, monitoring, and rollback

| Drift type | Detection | Owner |
|---|---|---|
| **Model drift** (provider changed it) | Weekly anchor set (Part 18 §18.6) | You |
| Input drift (users changed) | Query embedding distribution over time | You / LLMOps |
| Corpus drift | Document age and topic coverage | You |
| Quality drift | Online eval on sampled traffic | You |
| Cost drift | Cost per request over time | You / Finance |
| Infrastructure drift | Config differences between environments | LLMOps |

**Rollback readiness is a testable property**, and testing it is unusual enough to be noticed:
```
TC-OPS-004  Rollback drill
Method:     Quarterly. Deliberately roll back prompt, model, and corpus
            to the previous version in a staging environment. Measure
            the time and the number of manual steps for each.
Expected:   Each is under the documented MTTR target and requires no
            code deploy.
Value:      Most teams have never tested rollback. Discovering during an
            incident that the corpus cannot be reverted is the worst
            possible time to find out.
```

---

## 23.7 The maturity model

Useful for assessing a team quickly, and for showing a hiring manager you think structurally.

| Level | Characteristics | What to push for next |
|---|---|---|
| **0 — Ad hoc** | Prompts in a console. Manual spot-checking. No versioning. No traces. | Version control for prompts; basic tracing |
| **1 — Basic** | Prompts in Git. Some traces. A handful of manual test cases. | A golden dataset; deterministic assertions in CI |
| **2 — Systematic** | Golden dataset, automated eval, CI gate, cost tracking. | Judge validation; security regression suite |
| **3 — Managed** | Validated judges, security regression, online eval, drift detection, cost gates. | Shadow deployment; per-category SLOs |
| **4 — Optimised** | Shadow deploys, automated rollback, production feedback into datasets, quality SLOs with error budgets. | Maintain it |

**Most teams calling themselves "AI-first" are at level 0 or 1.** Moving a team from 1 to 2 is a six-week project with an obvious payoff, and it is the single highest-value thing a new AI QA engineer can do in a role.

---

## 23.8 Self-check

1. What are the four independently-versioned artefacts, and why does that matter for CI?
2. Where does QA end and LLMOps begin on evaluation?
3. Why is prompt rollback a testable requirement?
4. What is shadow deployment and what problem does it solve that a golden set cannot?
5. What does the weekly anchor set detect that nothing else can?
6. Why is a rollback drill worth running quarterly?
7. Assess a team at level 1 — what do you push for first?

---

**Next:** [PART-24-AI-GOVERNANCE.md](PART-24-AI-GOVERNANCE.md) — the frameworks, and what a QA engineer is actually accountable for.
