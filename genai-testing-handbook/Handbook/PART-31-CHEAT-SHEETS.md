# PART 31 — Cheat Sheets

> Seventeen one-page references. Print the ones you need.

---

## 1 · Python for testers

```python
# Strings / prompts
f"Hello {name}"                         # interpolation
"""multi
line"""                                 # prompt templates
text.strip().lower().split(",")
",".join(items)
text.removeprefix("```json").removesuffix("```")   # 3.9+

# Collections
[x for x in items if x["pri"] == "C"]              # list comp
{k: v for k, v in d.items() if v}                  # dict comp
set(a) & set(b)                                    # intersection (leak checks)
d.get("key", default)                              # safe access

# Files — ALWAYS specify encoding
with open("f.json", encoding="utf-8") as f: data = json.load(f)
json.dump(data, f, indent=2, ensure_ascii=False)   # keeps non-Latin readable

# Errors
try: ...
except (httpx.TimeoutException, httpx.HTTPStatusError) as e: ...
finally: ...

# Env
import os; os.getenv("KEY", "default")
from dotenv import load_dotenv; load_dotenv()

# Useful stdlib
from collections import defaultdict, Counter
from functools import lru_cache, wraps
from dataclasses import dataclass
import statistics, itertools, hashlib, re, time

statistics.mean(x); statistics.pstdev(x)
np.percentile(x, 95)                               # p95, not mean
```

---

## 2 · pytest

```python
# Fixtures (conftest.py)
@pytest.fixture(scope="session")     # once per run: clients, datasets
@pytest.fixture(scope="function")    # default: fresh per test

# Parametrize — dataset → suite
@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
@pytest.mark.parametrize("n", range(20))          # repetition

# Markers
@pytest.mark.llm          # expensive
@pytest.mark.slow
@pytest.mark.skipif(not os.getenv("KEY"), reason="no key")
@pytest.mark.xfail(reason="known: TICKET-123")

# Assertions
assert x == pytest.approx(0.85, abs=0.01)
with pytest.raises(ValidationError): ...
pytest.fail("explicit failure with context")
```
```bash
pytest -v                       # verbose
pytest -x                       # stop on first failure
pytest -k "injection"           # by name
pytest -m "not llm"             # by marker  ← PR runs
pytest -m llm                   # nightly runs
pytest -n auto                  # parallel (pytest-xdist) ← big win for API tests
pytest --lf                     # last failed
pytest --junitxml=r.xml         # CI report
pytest --runs=5                 # your custom option
```
**Failure message rule:** always include prompt, output, score, and threshold.

---

## 3 · LLM API testing

```python
# The assertion trio — put in every test
assert r.finish_reason == "stop"                 # not truncated
assert r.text.strip()                            # not empty
assert r.usage.total == r.usage.input + r.usage.output

# Plus
assert requested_model in r.model                # no substitution
assert abs(local_count - r.usage.input) / local_count < 0.15   # no hidden prompt
```

| finish_reason | Meaning |
|---|---|
| `stop` | Complete |
| `length` | **Truncated at max_tokens** |
| `tool_calls` | Wants a tool |
| `content_filter` | Provider blocked it |

| Status | Test |
|---|---|
| 400 | Oversized context must be **400 not 500** |
| 401 | Key never echoed in the response |
| 404 | Deprecated model → documented behaviour |
| 429 | Backoff + jitter + `Retry-After` + retry cap |
| 500 | Fallback engages |

**Streaming checklist:** terminator sent · chunks valid JSON · reassembly matches · mid-stream error surfaced · abort stops billing · usage reported · **guardrails apply** · TTFT measured.

---

## 4 · Prompt testing

```
□ Version-controlled + hash logged
□ User input structurally separated from instructions
□ Every constraint independently testable
□ No conflicting constraints (measure per-constraint satisfaction rate)
□ Defined "I don't know" behaviour
□ Output format precisely specified
□ Token budget asserted in CI
□ Current date / user context injected, not assumed
□ Template variables handle None / braces / oversized / delimiters
□ Canary string present for leakage tests
```

**The 12 prompt test types:** correctness · regression · injection · leakage · ambiguity · instruction conflict · boundary · adversarial · long · empty/malformed · multilingual · cost.

**Extraction attack shapes:** print instructions · repeat everything above · translate your rules · summarise your config · list your tools · what can't you discuss · complete "You are a".

---

## 5 · LLM evaluation

```
DETERMINISTIC → EMBEDDING → LLM-JUDGE → HUMAN
   free/all      cheap/1000s   paid/100s   costly/30
Push every check as far LEFT as it will go.
```

| Metric | Measures |
|---|---|
| Exact / normalised match | Labels, IDs, enums |
| Cosine similarity | Semantic equivalence (**poor at negation**) |
| Faithfulness | Claims supported by context |
| Answer relevancy | Answers the question asked |
| Context precision/recall | Retrieval quality |
| Citation correctness | Sources exist **and** support |
| Instruction following | Per-constraint satisfaction |

**Judge rules:** different model family · binary or 1–5 · require a reason · one concern per rubric · give it the context · swap order for pairwise · **validate with kappa on 30–50 human labels**.

| Kappa | Verdict |
|---|---|
| <0.40 | Do not use |
| 0.40–0.60 | Trends only |
| 0.60–0.80 | Gate + spot-check |
| >0.80 | Trustworthy |

**Report:** hard constraints separately · every score with a delta · min and p10, not just mean · cost · judge kappa.

---

## 6 · RAG

```
parse → chunk → embed → store → retrieve → rerank → assemble → generate
```
**First question on any wrong answer:** *was the right info in the retrieved context?*
No → retrieval bug (~75% of cases). Yes → generation bug.

| P@K | R@K | Diagnosis | Fix |
|---|---|---|---|
| High | High | Healthy | — |
| Low | High | Noise | Reranker; lower K; raise threshold |
| High | Low | Missing content | Raise K; fix chunking; add hybrid |
| Low | Low | Broken | Check embedding model match, index, query preprocessing |

```
Precision@K = hits / K
Recall@K    = hits / |relevant|
MRR         = 1 / rank of first relevant
NDCG@K      = DCG / ideal DCG   (graded relevance)
```

**Must-have tests:** no-answer abstention · zero-retrieval path · exact identifier ("ERR-5521") · lost-in-the-middle · fabricated citations = 0 · indirect injection via corpus · tenant isolation in the query.

---

## 7 · Vector DB

| Operator (pgvector) | Metric | Index ops class |
|---|---|---|
| `<=>` | Cosine distance | `vector_cosine_ops` |
| `<->` | Euclidean (L2) | `vector_l2_ops` |
| `<#>` | Negative inner product | `vector_ip_ops` |

```sql
-- Is the index actually used? Seq Scan = silent misconfiguration.
EXPLAIN ANALYZE SELECT id FROM chunks ORDER BY embedding <=> $1 LIMIT 5;

SET LOCAL hnsw.ef_search = 100;   -- higher = better recall, slower
SELECT COUNT(*) FROM chunks WHERE tenant_id IS NULL;   -- must be 0
```

**Checks:** dimension matches model · operator matches ops class · ANN recall vs exact ≥0.95 · index used · **pre-filtering not post-filtering** (assert full K returned under a selective filter) · no zero vectors · idempotent upsert · delete removes · raw vectors not exposed.

---

## 8 · Agents

```
plan → select tool → args → PERMISSION CHECK → execute → observe → loop → finish
```
**Permissions are enforced in the runtime, not the prompt.** A model attempting a forbidden call is normal; the runtime executing it is the bug.

**Fault injection modes:** error · timeout · empty · malformed · slow · **hostile** · wrong_type · flaky.
Assert: terminates · no fabricated success · no loop · hostile output does not redirect.

**Caps every agent needs:** step · cost · wall-clock · delegation depth.

**Trajectory assertions:** required tools called · forbidden tools absent · order correct · step count bounded.

**The two that catch real bugs:** ambiguous request → asks not guesses; retry does not duplicate a side effect (idempotency key).

---

## 9 · AI security

**Canary technique:** unique string in every hidden surface (system prompt, each tool description, each doc) → leakage becomes an exact string match.

**Injection families:** override · role reassign · fake system · authority · reframing · fiction · nested roleplay · encoding · language switch · many-shot · payload split · token smuggling · refusal suppression · completion.
**Transforms:** base64 · rot13 · leetspeak · homoglyph · zero-width · spacing · translation.

**Always report a success RATE, not one reproduction.**

**Severity factors:** impact · who is affected (self < others < all) · access required · reliability (rate) · chainability · detectability.

**The chain to look for:** indirect injection → markdown image → zero-click exfiltration.

---

## 10 · OWASP ⏳

### LLM Top 10 — 2026
| | | 2025 was |
|---|---|---|
| LLM01 | Prompt Injection (incl. cross-modal) | LLM01 |
| LLM02 | Sensitive Information Disclosure | LLM02 |
| LLM03 | **Excessive Agency** | LLM06 ▲3 |
| LLM04 | Supply Chain | LLM03 |
| LLM05 | Data and Model Poisoning | LLM04 |
| LLM06 | **Unbounded Consumption** | LLM10 ▲4 |
| LLM07 | Misinformation | LLM09 |
| LLM08 | **Hidden Context Exposure** | LLM07 (renamed) |
| LLM09 | Vector and Embedding Weaknesses | LLM08 |
| LLM10 | Improper Output Handling | LLM05 ▼5 |

### Agentic Top 10 (ASI)
ASI01 Agent Goal Hijack · ASI02 Tool Misuse · ASI03 Identity & Privilege Abuse · ASI04 Agentic Supply Chain · ASI05 Unexpected Code Execution · ASI06 Memory & Context Poisoning · ASI07 Insecure Inter-Agent Comms · ASI08 Cascading Failures · ASI09 Human-Agent Trust Exploitation · ASI10 Rogue Agents

---

## 11 · Performance

| Metric | Target (chat) |
|---|---|
| **TTFT p95** | < 1 s |
| Tokens/sec | > 20 |
| Error rate | < 1% |
| 429 rate | < 5% |
| **Quality under load** | within 3% of idle |

**Never load-test with "hi".** Build the profile from production token distributions.

```bash
k6 run --vus 50 --duration 5m load.js
locust -f load.py --users 50 --spawn-rate 5
```
**Before running:** estimate cost, get approval, set a provider spend cap.

**Symptoms:** TTFT↑ but tok/s flat = queueing · tok/s↓ = compute contention · quality↓ = silent fallback · cost↑ = retry amplification.

---

## 12 · Docker

```bash
docker run -d --name x -p 6333:6333 -v "$PWD/data:/storage" image
docker ps -a
docker logs -f --tail 100 x
docker exec -it x sh
docker run --env-file .env image
docker system prune -a                 # AI images are large
docker compose -f compose.test.yml up -d
docker compose down -v
```
**Dockerfile order:** `COPY requirements.txt` → `RUN pip install` → `COPY . .` (layer caching).
**Never bake secrets into an image.**
**Use `healthcheck` + `depends_on: condition: service_healthy`** or your tests race the database.

---

## 13 · Git

```bash
git switch -c feat/eval-suite
git add -p                             # stage selectively
git commit -m "add faithfulness metric"
git log --oneline --graph -20
git diff main...HEAD
git stash / git stash pop
git rebase -i main                     # (not available in some harnesses)
git revert <sha>                       # safe undo on shared branches
git blame path/to/prompt.txt           # who changed this prompt, when
```
**For this domain:** prompts, datasets, and baselines all live in Git. `git blame` on a prompt file is a genuine debugging tool.

---

## 14 · Linux / Bash

```bash
grep -rniE "error|exception" logs/ | head -50
tail -f app.log | grep -i timeout
find . -name "*.json" -mtime -1
sed -i 's/old/new/g' file
awk -F, '{s+=$3} END {print s}' data.csv

# JSON — essential for LLM APIs
jq '.choices[0].message.content' resp.json
jq -s 'map(.usage.total_tokens) | add' responses.jsonl
jq -s 'sort_by(-.latency_ms) | .[0:5]' traces.jsonl

# Streaming — -N is mandatory or you see nothing until the end
curl -N -X POST $URL -H "Content-Type: application/json" -d @body.json

curl -s $URL -w "\nttfb=%{time_starttransfer}s total=%{time_total}s\n"

ps aux | grep ollama
kill -9 <pid>
export KEY=value
chmod +x script.sh
```

---

## 15 · SQL

```sql
WITH runs AS (
  SELECT prompt_version, eval_score,
         input_tokens*0.000003 + output_tokens*0.000015 AS cost
  FROM eval_results WHERE created_at > NOW() - INTERVAL '7 days'
)
SELECT prompt_version,
       COUNT(*) AS n,
       ROUND(AVG(eval_score)::numeric,3) AS mean,
       PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY eval_score) AS p95,
       SUM(CASE WHEN eval_score < 0.7 THEN 1 ELSE 0 END) AS failures,
       ROUND(SUM(cost)::numeric,2) AS total_cost
FROM runs GROUP BY prompt_version ORDER BY prompt_version DESC;

-- Regression vs previous run
SELECT run_id, score, LAG(score) OVER (ORDER BY run_id) AS prev,
       score - LAG(score) OVER (ORDER BY run_id) AS delta
FROM eval_runs;
```
**Watch:** `NULL` silently excluded from aggregates · `COUNT(col)` ignores NULLs, `COUNT(*)` does not.

---

## 16 · CI/CD

```
PR:       static → unit/contract → integration → eval smoke (40×1) → security fast
          TOTAL < 15 MIN
NIGHTLY:  full eval (all×3) · retrieval · security · agent · perf smoke
WEEKLY:   anchor set (drift)
RELEASE:  load · red team · held-out set · model upgrade suite
```
**Three lines that keep it alive:** response cache keyed on prompt hash · `--budget-usd` cap · PR comment with the numbers.

**Gates:** hard constraints block · soft quality uses **delta** vs baseline · confirm a failure at N=5 before failing the build · baselines updated only in a separate reviewed PR · quarantine has an expiry date.

---

## 17 · Observability

**Required span attributes:** model · prompt_version · temperature · input/output tokens · reasoning tokens · TTFT · finish_reason · cost · correlation ID.

**RAG trace must include:** query (original + rewritten) · retrieved chunk IDs · scores · rerank in/out · assembled context token count · citations verified.

**Agent trace must include:** every step · tool · args · result · duration · cost · decision.

**Alerts:** p95 TTFT · error rate by type · **cost per hour** · tokens/request p95 · refusal rate **up or down** · retrieval-empty rate · fabricated citations >0 · fallback model in use · online eval score.

**Privacy:** PII redacted before storage · DPA for third-party processors · retention enforced · access-controlled · **erasure requests cover the trace store**.

---

**Next:** [APPENDIX-A-GLOSSARY.md](APPENDIX-A-GLOSSARY.md)
