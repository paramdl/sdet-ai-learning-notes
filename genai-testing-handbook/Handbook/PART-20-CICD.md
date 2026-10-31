# PART 20 — CI/CD for GenAI Testing

> **Goal of this part:** build a pipeline the team keeps switched on. Most GenAI eval pipelines are disabled within two months because they are slow, expensive, and flaky. Designing against those three failure modes *is* the job.

---

## 20.1 The pipeline

```
DEVELOPER
   │  push
   ▼
GIT ─────────────────────────────────────────────────────────────
   │
   ▼
┌─ STAGE 1 · STATIC ──────────────────── 30 s · free ──────────┐
│  lint · types · secret scan · dependency audit               │
│  PROMPT LINT: token budget, canary present, no hard-coded    │
│               secrets, template variables validated          │
└──────────────────────────┬───────────────────────────────────┘
                           ▼
┌─ STAGE 2 · UNIT + CONTRACT ─────────── 2 min · free ─────────┐
│  unit tests · API schema (mocked) · error paths (mocked)     │
│  parser tests · retry/backoff logic · cost calculator        │
└──────────────────────────┬───────────────────────────────────┘
                           ▼
┌─ STAGE 3 · INTEGRATION ─────────────── 5 min · ~$0.05 ───────┐
│  real API, small model, happy paths, streaming, tool calls   │
│  usage accounting reconciliation                             │
└──────────────────────────┬───────────────────────────────────┘
                           ▼
┌─ STAGE 4 · EVAL SMOKE ──────────────── 4 min · ~$0.30 ───────┐
│  40-case golden subset × 1 run · hard constraints 100%       │
│  quality delta vs baseline · cost delta vs baseline          │
└──────────────────────────┬───────────────────────────────────┘
                           ▼
┌─ STAGE 5 · SECURITY FAST ───────────── 3 min · ~$0.20 ───────┐
│  canary leakage · permission enforcement · output handling   │
└──────────────────────────┬───────────────────────────────────┘
                           ▼
                    ╔═══════════════╗
                    ║ QUALITY GATE  ║  ← merge blocked below this line
                    ╚═══════╤═══════╝
                            ▼
                         MERGE
                            │
        ┌───────────────────┴───────────────────┐
        ▼                                       ▼
┌─ NIGHTLY ─────────────────┐        ┌─ PRE-RELEASE ─────────────┐
│ full eval (all × 3)       │        │ full performance / load    │
│ full retrieval            │        │ full red team              │
│ full security             │        │ model upgrade suite        │
│ agent scenarios           │        │ held-out set (opened)      │
│ performance smoke         │        │ cost projection            │
│ ~45 min · ~$4             │        │ ~3 h · ~$40                │
└───────────────────────────┘        └───────────────────────────┘
        │
        ▼
┌─ WEEKLY ──────────────────┐
│ anchor set (drift)        │
│ golden-set representativeness (quarterly)
└───────────────────────────┘
```

**The design principles behind that layout:**
1. **Free and deterministic first.** Stages 1–2 catch most defects at zero cost.
2. **Nothing slow before the gate.** Total pre-merge time under 15 minutes, or developers route around it.
3. **Cost visible and capped at every paid stage.**
4. **Expensive suites are scheduled, not per-commit.**
5. **Every stage can fail the build** — a stage that only warns is decoration.

---

## 20.2 GitHub Actions — a working configuration

```yaml
name: genai-quality

on:
  pull_request:
  schedule:
    - cron: '0 2 * * *'      # nightly full suite
    - cron: '0 3 * * 1'      # weekly anchor / drift run
  workflow_dispatch:

env:
  PYTHON_VERSION: '3.12'

jobs:
  # ---------- STAGE 1 + 2 : free, every PR ----------
  static-and-unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip
      - run: pip install -r requirements-dev.txt

      - name: Secret scan
        run: gitleaks detect --no-git -v

      - name: Prompt lint
        # Prompts are code: budget them, and require the canary that
        # every leakage test depends on.
        run: python -m tools.prompt_lint --max-tokens 800 --require-canary

      - name: Unit + contract tests (mocked, no API calls)
        run: pytest tests/contract tests/unit -v --junitxml=results/contract.xml

      - uses: actions/upload-artifact@v4
        if: always()
        with: {name: contract-results, path: results/}

  # ---------- STAGE 3-5 : paid, every PR, budget-capped ----------
  eval-smoke:
    runs-on: ubuntu-latest
    needs: static-and-unit
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.12', cache: pip}
      - run: pip install -r requirements-dev.txt

      # Cache LLM responses keyed by prompt hash: an unchanged suite
      # costs nothing to re-run. This single step is what makes
      # per-PR evaluation affordable.
      - uses: actions/cache@v4
        with:
          path: .llm_cache
          key: llm-cache-${{ hashFiles('prompts/**', 'data/golden*.json') }}
          restore-keys: llm-cache-

      - name: Integration tests
        run: pytest tests/integration -v
        env:
          LLM_API_KEY: ${{ secrets.LLM_API_KEY }}

      - name: Evaluation smoke (40 cases)
        run: |
          python -m eval.run \
            --dataset data/golden-v2.3.0.json --subset 40 --runs 1 \
            --baseline baselines/quality/current.json \
            --max-quality-drop 0.03 \
            --max-cost-increase 0.15 \
            --budget-usd 0.50 \
            --output results/eval.json
        env:
          LLM_API_KEY: ${{ secrets.LLM_API_KEY }}

      - name: Security fast checks
        run: pytest tests/security -m fast -v
        env:
          LLM_API_KEY: ${{ secrets.LLM_API_KEY }}

      # Put the numbers where reviewers will see them.
      - name: Comment results on PR
        if: always()
        run: python -m tools.pr_comment --results results/eval.json
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  # ---------- NIGHTLY ----------
  nightly:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.12', cache: pip}
      - run: pip install -r requirements-dev.txt

      - name: Full evaluation
        run: |
          python -m eval.run --dataset data/golden-v2.3.0.json --runs 3 \
            --baseline baselines/quality/current.json --budget-usd 5.00 \
            --output results/nightly.json
        env: {LLM_API_KEY: "${{ secrets.LLM_API_KEY }}"}

      - name: Full retrieval evaluation
        run: python -m eval.retrieval --dataset data/retrieval-golden.json

      - name: Full security suite
        run: pytest tests/security -v

      - name: Agent scenarios
        run: pytest tests/agent -v

      - name: Publish report
        if: always()
        run: python -m tools.publish_report --results results/

      - name: Alert on regression
        if: failure()
        run: python -m tools.notify --channel qa-alerts --results results/
```

**The three lines that make this pipeline survive:**
- `actions/cache` on `.llm_cache` — an unchanged suite is free
- `--budget-usd` — a bug cannot spend the quarter's budget overnight
- `pr_comment` — results appear where developers already are

---

## 20.3 The PR comment

```markdown
## 🤖 GenAI Quality Report — prompt v3.2

| Gate | Result | Baseline | Δ |
|---|---|---|---|
| Schema validity | 40/40 (100%) | 100% | — |
| Canary leakage | 0 | 0 | — |
| Quality (mean) | **0.84** | 0.87 | **−0.03** ⚠️ |
| Faithfulness | 0.91 | 0.89 | +0.02 ✅ |
| Instruction following | **0.78** | 0.90 | **−0.12** ❌ |
| Cost / case | $0.0026 | $0.0021 | **+24%** ❌ |
| Security fast | 0/12 succeeded | 0/12 | — |

### ❌ Blocking

**Instruction following −0.12.** The `≤3 sentences` constraint is met in
71% of runs (was 96%). Likely cause: this PR adds "explain your reasoning",
which conflicts with the length limit.

**Cost +24%.** System prompt grew 412 → 610 tokens.

### Newly failing cases
- `billing-refund-window-001`
- `policy-escalation-004`

<sub>40 cases × 1 run · $0.31 · judge kappa 0.78 · run #4412</sub>
```

**Why this format works:** it names the probable cause rather than only the number, it lists the failing cases by ID, and it shows the cost. A developer can act on it without opening a dashboard.

---

## 20.4 Other CI systems

### GitLab CI
```yaml
stages: [static, unit, integration, eval, security]

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

eval-smoke:
  stage: eval
  image: python:3.12
  cache:
    key: llm-cache-$CI_COMMIT_REF_SLUG
    paths: [.llm_cache/, .cache/pip]
  script:
    - pip install -r requirements-dev.txt
    - python -m eval.run --subset 40 --budget-usd 0.50 --output results/eval.json
  artifacts:
    when: always
    reports: {junit: results/*.xml}
    paths: [results/]
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

### Jenkins
```groovy
pipeline {
  agent any
  environment { LLM_API_KEY = credentials('llm-api-key') }
  stages {
    stage('Static')      { steps { sh 'python -m tools.prompt_lint --max-tokens 800' } }
    stage('Contract')    { steps { sh 'pytest tests/contract --junitxml=results/contract.xml' } }
    stage('Eval smoke')  { steps { sh 'python -m eval.run --subset 40 --budget-usd 0.50' } }
  }
  post {
    always { junit 'results/*.xml'; archiveArtifacts 'results/**' }
    failure { emailext subject: "GenAI quality gate failed", body: readFile('results/summary.txt') }
  }
}
```

### Azure DevOps
```yaml
trigger: [main]
pool: {vmImage: ubuntu-latest}
steps:
  - task: UsePythonVersion@0
    inputs: {versionSpec: '3.12'}
  - script: pip install -r requirements-dev.txt
  - script: pytest tests/contract --junitxml=results/contract.xml
  - script: python -m eval.run --subset 40 --budget-usd 0.50
    env: {LLM_API_KEY: $(LLM_API_KEY)}
  - task: PublishTestResults@2
    condition: always()
    inputs: {testResultsFiles: 'results/*.xml'}
```

---

## 20.5 Managing flakiness in CI

A GenAI suite that fails randomly gets ignored, then disabled. Controls:

| Control | Implementation |
|---|---|
| **Separate hard from soft gates** | Hard constraints block; soft quality warns until a trend is established |
| **Use delta gates** | Compare to baseline, not to an absolute |
| **N-run on the gate itself** | If a case fails, re-run it at N=5 before failing the build |
| **Quarantine** | A newly flaky case moves to a quarantine suite that reports but does not block, with an expiry date |
| **Track flake rate as a metric** | Rising flake rate is itself a signal about the system |
| **Never auto-update baselines** | Requires a reviewed PR (Part 19 §19.4) |
| **Cache** | Removes both cost and variance for unchanged inputs |

```python
def gate_with_retry(case, n_confirm=5):
    """Confirm a failure before failing the build. One unlucky sample
    should not block a merge; a genuine rate change should."""
    if evaluate(case)["passed"]:
        return True
    rate = sum(evaluate(case)["passed"] for _ in range(n_confirm)) / n_confirm
    return rate >= case["min_pass_rate"]
```

---

## 20.6 Secrets and environments

| Practice | Note |
|---|---|
| API keys in the CI secret store only | Never in a repo, never in a log |
| Separate keys per environment | Dev/CI/prod — with separate spend caps |
| **A dedicated CI key with a hard budget cap** | Set in the provider console; the last line of defence |
| Redact keys from logs | Most CI systems do this for registered secrets; verify it |
| Rotate on schedule | And test that rotation does not break the pipeline |
| Fork PRs do not get secrets | Run only the free stages for external contributors |

That last row is a real gap in public repositories: an eval workflow that runs on `pull_request` from a fork will either fail confusingly or, if misconfigured with `pull_request_target`, expose your key. Run only Stages 1–2 for forks.

---

## 20.7 Self-check

1. Why must pre-merge stages stay under ~15 minutes?
2. What makes per-PR evaluation affordable?
3. Why should a soft quality gate warn rather than block at first?
4. What is quarantine, and why does it need an expiry date?
5. Why must baselines never be auto-updated by CI?
6. What is the risk with fork pull requests?
7. What three things make a PR comment actionable?

---

**Next:** [PART-21-DOCKER-KUBERNETES.md](PART-21-DOCKER-KUBERNETES.md) — exactly as much container knowledge as this job requires.
