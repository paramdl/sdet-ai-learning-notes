# PART 2 — Programming for GenAI Testing

> **Goal of this part:** know exactly which languages to learn, in what order, to what depth, and — crucially — **which topics you can skip**. Most Python courses spend 40% of their time on material a QA engineer will never use.

---

## 2.0 The verdict, up front

| Language | Verdict | Why | Time to working competence |
|---|---|---|---|
| **Python** | 🔴 **MUST LEARN** | The entire GenAI ecosystem is Python-first. Every eval framework, every provider SDK, every red-team tool has Python as its primary or only interface. Non-negotiable. | 6–10 weeks to useful; ongoing |
| **Bash / Linux CLI** | 🔴 **MUST LEARN** | Every model server, container, and CI runner is Linux. You cannot debug a deployment you cannot navigate. | 2 weeks to competent |
| **SQL** | 🔴 **MUST LEARN** | Test data, ground-truth sets, eval results, trace analysis, and pgvector-backed RAG all live in databases. | 3 weeks to competent |
| **JavaScript / TypeScript** | 🟠 **SHOULD LEARN** | Playwright for AI UI testing, promptfoo config, Node-based tooling, and most AI product front-ends. You already have a head start here. | 3–4 weeks (working level) |
| **Go** | 🟡 OPTIONAL | Appears in infrastructure and some vector DBs (Qdrant is Rust; Milvus has Go components). Reading-level only, if ever. | — |
| **Java** | 🟡 OPTIONAL | Only if your employer's stack is Java (Spring AI, LangChain4j) and you must write in-repo tests. Do not learn pre-emptively. | — |
| **C#** | 🟡 OPTIONAL | Same logic — only for .NET shops. ⏳ Microsoft Agent Framework ships .NET alongside Python, so .NET-heavy enterprises are a real case. | — |
| **C++** | ⚪ **NOT REQUIRED** | Inference-engine internals (llama.cpp). You will never need to modify it. | — |
| **Rust** | ⚪ **NOT REQUIRED** | Some vector DBs and tokenizers are written in Rust. You consume them; you do not write them. | — |

**The honest summary:** learn Python properly, get comfortable in a Linux shell, know enough SQL to answer questions with data, and keep your JavaScript for Playwright. Everything else is situational.

---

## 2.1 Python — the complete topic breakdown

Python is graded here on two axes: **general difficulty level** and **how much GenAI testing actually needs it**. The second column is the one that saves you months.

### Legend
- **Need:** 🔴 daily · 🟠 weekly · 🟡 occasionally · ⚪ almost never in this role

### 2.1.1 Beginner tier — build in weeks 1–3

| Topic | Need | Why it matters for GenAI testing | What "enough" looks like |
|---|---|---|---|
| Variables, types, operators | 🔴 | Everything | — |
| **Strings & f-strings** | 🔴 | Prompts are strings. Template building, escaping, multi-line prompts. | Confident with `f""`, `"""triple quotes"""`, `.format()`, `.strip()`, `.split()`, `.join()`, slicing |
| **Lists, dicts, sets, tuples** | 🔴 | API responses are nested dicts; datasets are lists of dicts; sets find data leakage | Nested access, `.get()` with defaults, set operations |
| **Comprehensions** | 🔴 | `[t for t in tests if t["priority"]=="P1"]` — you write these all day | List and dict comprehensions with conditions |
| Conditionals, loops | 🔴 | — | Including `enumerate`, `zip` |
| **Functions, args, kwargs, defaults** | 🔴 | Every test helper | Including `*args`/`**kwargs` |
| **f-string vs concatenation for prompts** | 🔴 | Prompt injection can start with naive string concatenation | Understand why user input must be structurally separated |
| **File handling** | 🔴 | Reading test datasets, writing eval results | `with open()`, encoding='utf-8' (**always specify it** — Windows defaults will bite you) |
| **JSON** | 🔴 | The lingua franca of LLM APIs | `json.loads`/`dumps`, `indent`, `ensure_ascii=False` for non-Latin text |
| **CSV** | 🟠 | Golden datasets, test-case exports | `csv.DictReader`/`DictWriter`, or pandas |
| **Exceptions** | 🔴 | Every API call can fail; tests must distinguish "assertion failed" from "network died" | `try/except/else/finally`, catching specific exceptions, custom exception classes |
| **Modules & packages** | 🔴 | Organising a test suite | `import`, `from x import y`, `__init__.py`, relative imports |
| **Virtual environments** | 🔴 | Project isolation; non-negotiable hygiene | `python -m venv`, activate, `requirements.txt` or `uv` |
| **Environment variables** | 🔴 | API keys never go in code | `os.getenv`, `python-dotenv`, `.env` in `.gitignore` |

> **Beginner-tier exit test:** write a script that reads a CSV of 20 test prompts, calls an LLM API for each, writes results to a JSON file, handles network errors without crashing, and never hard-codes a key. If you can do that, move on.

### 2.1.2 Intermediate tier — weeks 4–8

| Topic | Need | Why it matters | Notes |
|---|---|---|---|
| **pytest** | 🔴 | Your primary test runner. DeepEval, Ragas and most eval code are pytest-native | See §2.1.5 — this is the single highest-value topic in Part 2 |
| **Fixtures** | 🔴 | Shared LLM clients, loaded datasets, scoped setup | `@pytest.fixture`, scopes (`function`/`module`/`session`), `conftest.py` |
| **Parametrize** | 🔴 | One test function × 200 dataset rows = 200 tests | `@pytest.mark.parametrize` — the backbone of dataset-driven eval |
| **Markers** | 🔴 | Splitting cheap deterministic tests from expensive judge tests in CI | `@pytest.mark.llm`, `-m "not llm"` |
| **HTTP clients (`requests`)** | 🔴 | Raw API testing, custom endpoints | Sessions, timeouts (**always set one**), headers, status handling |
| **`httpx`** | 🟠 | Async-capable and streaming-friendly; the modern choice | Needed for SSE and concurrency work |
| **Classes / OOP** | 🟠 | Page objects, client wrappers, custom metric classes | You need to *read and extend* classes; deep inheritance design is not required |
| **`typing`** | 🟠 | Readable test code; required by Pydantic | `list[str]`, `dict[str, Any]`, `Optional`, `Literal` |
| **Pydantic** | 🔴 | **Validating LLM structured output** — the cleanest way to assert an LLM's JSON is correct | v2 syntax; `BaseModel`, `model_validate_json`, `ValidationError`, `Field` constraints |
| **`jsonschema`** | 🟠 | Schema assertions when you are not using Pydantic | `validate()`, draft versions |
| **Regular expressions** | 🔴 | Extracting values from free-form output, PII detection, refusal detection | `re.search`, groups, `re.IGNORECASE`, `re.DOTALL`. Know the limits: **regex is a weak PII detector** — good for smoke tests, insufficient as a control |
| **Logging** | 🔴 | Debugging non-deterministic failures requires the full prompt+response captured | `logging` module, levels, handlers. **Never log API keys or user PII** |
| **`pathlib`** | 🟠 | Cross-platform paths; you are on Windows, CI is Linux | `Path`, `/` operator, `.exists()` |
| **`datetime`** | 🟡 | Timestamps in eval runs, temporal hallucination tests | Timezone awareness |
| **Configuration management** | 🟠 | Model, temperature, thresholds must be config, not literals | YAML/TOML + Pydantic Settings; one config per environment |
| **`argparse` / CLI** | 🟡 | Making your eval scripts runnable by others | |
| **pandas** | 🟠 | Eval results analysis: score distributions, run-to-run variance, regression deltas | `DataFrame`, `read_csv`, `groupby`, `merge`, `describe`, `to_markdown` |
| **`statistics` / basic stats** | 🟠 | Mean, median, stdev, percentiles (p50/p95/p99) on latency and scores | You need p95, not average — averages hide the pain |

> **Intermediate exit test:** a pytest suite that loads a 50-row golden dataset, parametrizes over it, calls an LLM, validates output against a Pydantic model, records latency and token usage to a DataFrame, and prints a summary table with p95 latency and pass-rate.

### 2.1.3 Advanced tier — weeks 9+

| Topic | Need | Why it matters | Notes |
|---|---|---|---|
| **Decorators** | 🟠 | Retry logic, timing, cost tracking, caching wrappers around LLM calls | Write your own `@retry_on_rate_limit` and `@track_cost` — genuinely useful |
| **Generators / `yield`** | 🟠 | **Streaming responses are generators.** Testing SSE means consuming them | Also memory-efficient dataset iteration |
| **Context managers** | 🟡 | `with` blocks for clients, temp resources, timing blocks | `contextlib.contextmanager` |
| **`async`/`await` + `asyncio`** | 🟠 | LLM calls are I/O-bound and slow. 200 sequential eval calls = 15 minutes; async = 40 seconds | `async def`, `await`, `asyncio.gather`, `asyncio.Semaphore` for rate limiting |
| **`pytest-asyncio`** | 🟠 | Running async tests | |
| **Concurrency: threads vs async vs processes** | 🟠 | Know *why* async beats threads for API-bound work | `ThreadPoolExecutor` is a valid, simpler alternative for many suites |
| **Rate-limit handling** | 🔴 | Every real eval run hits 429s | Exponential backoff with jitter; `tenacity` library |
| **`functools`** | 🟡 | `lru_cache` for embedding caching — big cost saver | |
| **NumPy** | 🟠 | Cosine similarity, vector maths, score arrays | You need `np.dot`, `np.linalg.norm`, array ops. **Not** linear algebra theory |
| **Packaging** | 🟡 | Shipping your eval framework as an installable internal package | `pyproject.toml` |
| **`unittest.mock`** | 🟠 | Mocking LLM responses to test *your harness* deterministically and for free | `patch`, `MagicMock`. Critical for testing retry/error paths |
| **Type checking (`mypy`)** | 🟡 | Larger frameworks | |
| **Property-based testing (`hypothesis`)** | 🟡 | Generating adversarial input variations automatically | Nice-to-have; powerful for fuzzing prompt inputs |

### 2.1.4 What you can genuinely skip ⚪

Do not spend time on these for this role:
- Metaclasses, descriptors, `__slots__`, multiple inheritance MRO puzzles
- GUI programming (tkinter, PyQt)
- Web frameworks beyond a minimal FastAPI app to *host a test target* (Part 25)
- Deep ML: PyTorch/TensorFlow training loops, autograd, custom layers
- C extensions, Cython, performance micro-optimisation
- Django, ORMs beyond basic SQLAlchemy reading
- Algorithm-interview material (dynamic programming, graph algorithms) — unless a specific employer screens on it

### 2.1.5 pytest — the deep dive you actually need

pytest is where your GenAI testing lives. This is the minimum working set:

```python
# conftest.py — shared fixtures, discovered automatically
import os, pytest
from openai import OpenAI

@pytest.fixture(scope="session")
def llm():
    """One client for the whole run. scope='session' means built once."""
    return OpenAI(
        base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"),
        api_key=os.getenv("OPENAI_API_KEY", "ollama"),
    )

@pytest.fixture(scope="session")
def golden_set():
    """Load the eval dataset once, reuse across all tests."""
    import json
    with open("data/golden.json", encoding="utf-8") as f:
        return json.load(f)

def pytest_addoption(parser):
    """Adds `pytest --runs=5` so you can control N-run sampling."""
    parser.addoption("--runs", action="store", default=1, type=int)

@pytest.fixture
def runs(request):
    return request.config.getoption("--runs")
```

```python
# test_support.py
import pytest

# Each dict becomes its own test with a readable name.
CASES = [
    {"id": "email-change", "q": "How do I change my email?", "must": ["settings"]},
    {"id": "refund",       "q": "Refund me now.",            "must_not": ["refund will be"]},
]

@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_reply_constraints(llm, case):
    out = ask(llm, case["q"])
    for token in case.get("must", []):
        assert token.lower() in out.lower(), f"missing {token!r} in: {out}"
    for token in case.get("must_not", []):
        assert token.lower() not in out.lower(), f"forbidden {token!r} in: {out}"

@pytest.mark.llm          # expensive: excluded from PR runs with -m "not llm"
@pytest.mark.flaky_ok     # your own marker documenting expected variance
def test_pass_rate_over_n_runs(llm, runs):
    """The GenAI-native assertion shape: a RATE, not a single result."""
    passes = sum(1 for _ in range(runs) if is_acceptable(ask(llm, "Refund me.")))
    rate = passes / runs
    assert rate >= 0.9, f"pass rate {rate:.0%} below 90% threshold"
```

**The pytest features that matter most here, ranked:**
1. `parametrize` — turns a dataset into a test suite
2. `fixture` with `scope="session"` — avoids re-creating clients and re-loading data
3. Markers + `-m` — separates the 5-second CI suite from the 20-minute nightly one
4. `conftest.py` — shared setup without imports
5. `--maxfail`, `-x`, `-k` — controlling expensive runs during development
6. `pytest-xdist` (`-n auto`) — parallel execution; essential when each test costs 2 seconds of network wait
7. `pytest-html` or `--junitxml` — reports CI can render
8. `pytest.approx` — float comparison for score assertions

**Reporting non-determinism properly.** A failing GenAI test should tell you *what came back*, not just that an assertion failed:

```python
assert score >= 0.8, (
    f"\nPROMPT:   {prompt}"
    f"\nOUTPUT:   {output}"
    f"\nSCORE:    {score:.2f} (threshold 0.80)"
    f"\nREASON:   {judge_reason}"
)
```
Without this, every failure costs 20 minutes of manual reproduction — and reproduction may not even be possible.

---

## 2.2 JavaScript / TypeScript 🟠 SHOULD LEARN

**Why it matters for this role, concretely:**

1. **Playwright** — testing AI *applications*, not just AI APIs. Streaming chat UIs have failure modes invisible at the API layer: partial render, broken stop button, markdown injection, scroll jump, missing loading state during a 12-second reasoning delay.
2. **promptfoo** — Node-based; its config is YAML but custom assertions are JavaScript.
3. **Product front-ends** — most AI products are React/Next.js. Reading the front-end tells you what the API contract really is.
4. ⏳ **Growing eval-tool support** — DeepEval now ships a TypeScript SDK in addition to Python, so JS-first teams have a native path.

**What to learn:**

| Topic | Need | Note |
|---|---|---|
| Node.js + npm/npx basics | 🔴 (if using JS tools) | `npx` runs a tool without installing it — how you should run promptfoo |
| `async`/`await`, Promises | 🔴 | Everything network in JS |
| `fetch` and REST calls | 🟠 | API checks from the browser context |
| JSON handling | 🔴 | |
| **Playwright core** | 🔴 | Locators, auto-waiting, assertions, fixtures, traces |
| **Playwright for streaming UIs** | 🟠 | `expect.poll`, network interception (`page.route`), waiting for text *growth* not text *presence* |
| TypeScript basics | 🟠 | Types, interfaces, generics-lite. Enough to read and edit typed test code |
| Jest/Vitest | 🟡 | Only if the team's unit tests are JS |

**The single most useful JS skill for AI UI testing** is intercepting and stubbing the model response so the UI test is deterministic:

```ts
// Make an AI UI test deterministic by controlling the stream.
await page.route('**/api/chat', route =>
  route.fulfill({
    status: 200,
    headers: { 'content-type': 'text/event-stream' },
    body: 'data: {"delta":"Hello"}\n\ndata: {"delta":" world"}\n\ndata: [DONE]\n\n',
  })
);
```
This separates *"does the UI render a stream correctly"* (deterministic, fast, run on every PR) from *"is the model's answer good"* (non-deterministic, slow, run nightly). **Keeping those two questions apart is the core skill of AI UI testing.**

⚪ **Skip:** React internals, state management libraries, build tooling, CSS frameworks. You are testing the app, not building it.

---

## 2.3 SQL 🔴 MUST LEARN

**Why a GenAI tester needs SQL more than a traditional tester does:** eval results, traces, token/cost records, feedback, and ground-truth datasets are all tabular. The questions you will be asked — *"has quality dropped since the model upgrade?"*, *"which user is burning 40% of our token spend?"*, *"which document chunks are never retrieved?"* — are SQL questions.

| Topic | Need | GenAI-specific use |
|---|---|---|
| `SELECT`, `WHERE`, `ORDER BY`, `LIMIT` | 🔴 | Pulling traces for a time window |
| `JOIN` (inner/left) | 🔴 | Joining eval results to test-case metadata |
| `GROUP BY` + aggregates | 🔴 | Mean score per prompt version; total tokens per user |
| `COUNT`, `SUM`, `AVG`, `MIN`, `MAX` | 🔴 | Cost and quality rollups |
| **Percentiles** | 🟠 | p95 latency — `PERCENTILE_CONT` in Postgres |
| Subqueries + CTEs (`WITH`) | 🟠 | Readable multi-step analysis; strongly prefer CTEs |
| `CASE WHEN` | 🟠 | Bucketing scores into pass/warn/fail |
| Window functions | 🟡 | Comparing a run to the previous run (`LAG`) — excellent for regression deltas |
| Indexes | 🟠 | Why your trace query takes 4 minutes |
| Transactions, ACID | 🟠 | Data-integrity testing in the app around the model |
| `NULL` semantics | 🔴 | Silent bug source in eval aggregation |
| DDL basics | 🟡 | Creating your own results tables |

**Worked example — the query you will write most often:**
```sql
-- Quality and cost per prompt version, last 7 days
WITH runs AS (
  SELECT prompt_version,
         eval_score,
         input_tokens * 0.000003 + output_tokens * 0.000015 AS cost_usd
  FROM eval_results
  WHERE created_at > NOW() - INTERVAL '7 days'
)
SELECT prompt_version,
       COUNT(*)                                   AS n,
       ROUND(AVG(eval_score)::numeric, 3)         AS mean_score,
       ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY eval_score)::numeric, 3) AS p95_score,
       ROUND(SUM(cost_usd)::numeric, 2)           AS total_cost,
       SUM(CASE WHEN eval_score < 0.7 THEN 1 ELSE 0 END) AS failures
FROM runs
GROUP BY prompt_version
ORDER BY prompt_version DESC;
```

### PostgreSQL + pgvector 🔴 MUST LEARN

`pgvector` is a Postgres extension adding a `vector` column type and similarity operators. It is the most common "we already have Postgres, we don't need a separate vector DB" choice, and therefore the vector store you are most likely to test.

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE chunks (
  id          BIGSERIAL PRIMARY KEY,
  doc_id      TEXT NOT NULL,
  chunk_text  TEXT NOT NULL,
  metadata    JSONB,
  embedding   VECTOR(1536)          -- MUST match your embedding model's dimension
);

-- Approximate-nearest-neighbour index (HNSW). Without an index this is a
-- full scan: correct, but slow at scale.
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops);

-- Top-5 most similar chunks. <=> is cosine DISTANCE (0 = identical),
-- so similarity = 1 - distance.
SELECT id, chunk_text,
       1 - (embedding <=> :query_vec) AS similarity
FROM chunks
WHERE metadata->>'tenant_id' = :tenant   -- metadata filter: multi-tenant safety
ORDER BY embedding <=> :query_vec
LIMIT 5;
```

**The three operators to memorise:** `<->` Euclidean (L2), `<=>` cosine distance, `<#>` negative inner product. **Using the wrong one silently returns wrong-but-plausible results** — a bug that no exception will ever reveal. Checking that the operator matches the index's `ops` class and the embedding model's intended metric is a real, findable defect.

Full vector-DB test strategy is Part 8.

---

## 2.4 Bash / Linux 🔴 MUST LEARN

You are on Windows; production and CI are Linux. Git Bash and WSL both work locally.

| Topic | Need | Why |
|---|---|---|
| Navigation: `cd ls pwd find` | 🔴 | Basic survival in a container |
| `cat head tail less` | 🔴 | Reading logs; `tail -f` to watch live |
| **`grep`** | 🔴 | Finding an error in 200MB of logs. Learn `-i -r -n -A -B -C -E` |
| **`jq`** | 🔴 | **Essential.** LLM APIs return deep JSON; jq is how you inspect it from the shell |
| **`curl`** | 🔴 | The ground truth of API behaviour, free of SDK abstraction. Learn `-X -H -d -N -s -i -w` |
| Pipes and redirection | 🔴 | `\|`, `>`, `>>`, `2>&1` |
| `sed` | 🟠 | Quick substitution in files/logs |
| `awk` | 🟠 | Column extraction and summing — e.g. total tokens from a log |
| Env vars, `export`, `.env` | 🔴 | Key management |
| `chmod`, permissions | 🟠 | Fixing "permission denied" in CI |
| Processes: `ps top kill` | 🟠 | Killing a hung local model server |
| `ssh`, `scp` | 🟠 | Reaching test environments |
| Shell scripting: variables, `if`, `for`, functions, exit codes | 🟠 | CI glue. **Exit codes are how CI knows you failed** |
| `watch`, `xargs`, `tee` | 🟡 | Convenience |

**The two commands that will earn their keep daily:**

```bash
# Stream an SSE response and watch tokens arrive. -N disables buffering,
# which is the whole point — without it you see nothing until the end.
curl -N -X POST http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"llama3.1:8b","stream":true,
       "messages":[{"role":"user","content":"Count to 5"}]}'
```

```bash
# Total tokens and cost across a JSONL log of API responses.
jq -s 'map(.usage.total_tokens) | add' responses.jsonl

# Find the 5 slowest requests in a trace log.
jq -s 'sort_by(-.latency_ms) | .[0:5] | .[] | {id, latency_ms, model}' traces.jsonl
```

---

## 2.5 The other languages — the honest answer

### Java 🟡 OPTIONAL
Learn **only** if your employer's backend is Java and you are expected to write tests inside that repo. The AI ecosystem there is real but secondary (Spring AI, LangChain4j). If you are learning on your own time to become employable in GenAI QA, Python gives a far better return. **Do not learn Java pre-emptively for this role.**

### C# 🟡 OPTIONAL
Same reasoning. ⏳ The case is slightly stronger than Java's because Microsoft Agent Framework ships first-class .NET support alongside Python, so enterprise Microsoft shops building agents may want .NET test engineers. Situational, not foundational.

### Go 🟡 OPTIONAL (reading level at most)
Shows up in infrastructure and parts of the vector-DB ecosystem. The realistic need is *reading* a Go error message or a small handler to understand behaviour — not writing Go. Do not schedule study time.

### C++ ⚪ NOT REQUIRED
The efficient inference engines (llama.cpp and relatives) are C++. You will run them, never modify them.

### Rust ⚪ NOT REQUIRED
Qdrant, several tokenizer libraries, and various high-performance components are Rust. Same logic: you are a consumer.

**The general principle:** learn a second language when a *specific job* requires it, not to feel prepared. Depth in Python beats breadth across five languages for every GenAI QA role that exists today.

---

## 2.6 A 10-week Python plan for a working QA engineer

Assumes 1–2 h/day and existing programming exposure.

| Week | Focus | Deliverable |
|---|---|---|
| 1 | Syntax, types, strings, collections, comprehensions | Script that transforms a CSV of test cases |
| 2 | Functions, modules, venv, `.env`, exceptions, file/JSON I/O | Script calling a local Ollama model, results to JSON, errors handled |
| 3 | `requests`, HTTP fundamentals, status handling, timeouts, retries | Raw REST client for an LLM API with backoff |
| 4 | **pytest**: assertions, fixtures, conftest | 10 tests against your Week-3 client |
| 5 | **pytest**: parametrize, markers, reporting | Dataset-driven suite over 30 prompts, split cheap/expensive by marker |
| 6 | Pydantic + `jsonschema` + regex | Structured-output validation suite |
| 7 | Logging, config management, decorators (`@retry`, `@track_cost`) | Reusable harness module |
| 8 | pandas + basic stats | Results analysis: pass-rate, p95 latency, score distribution |
| 9 | `async`/`asyncio`/`httpx`, concurrency, rate-limit handling | 200-case eval running concurrently in under a minute |
| 10 | NumPy, cosine similarity, `unittest.mock` | Semantic-similarity assertions + mocked tests for your error paths |

At the end of week 10 you have not "learned Python" — you have built a working GenAI eval harness, which is the actual goal.

---

## 2.7 Self-check

1. Why is `scope="session"` the right fixture scope for an LLM client but wrong for mutable test state?
2. Your eval suite takes 18 minutes for 200 cases. What are the two independent fixes, and which do you do first?
3. Why must you always pass `encoding='utf-8'` when reading prompt datasets on Windows?
4. What does `<=>` mean in pgvector, and what breaks if you use `<->` instead?
5. Why should a failing GenAI assertion print the model output, and what does that cost you if you skip it?
6. When would you mock the LLM response instead of calling the real model — and what are you testing in that case?
7. Why does `-N` matter in a `curl` streaming test?

---

**Next:** [PART-03-LLM-FUNDAMENTALS.md](PART-03-LLM-FUNDAMENTALS.md) — the full request lifecycle, layer by layer, and exactly where a QA engineer tests each one.
