# Python for LLM Testing — the 20-hour slice

> **You are not learning Python as a second career language.** You are learning enough to read an eval notebook, modify it, write pytest-based eval suites, and call an LLM API. TypeScript stays your interview language.
>
> **Budget: 20 hours.** If you find yourself learning Django or asyncio internals, you've gone too far.

---

## 1. Why Python at all

| Tool | Language | Can you avoid it? |
|---|---|---|
| **promptfoo** | JS/TS + YAML | No need to — it's already your language |
| **DeepEval** | Python | No. It's the standard for metric-based LLM eval |
| **RAGAS** | Python | No. The standard for RAG evaluation |
| **LangChain / LlamaIndex** | Python (JS exists but lags) | Mostly no |
| **OpenAI / Anthropic SDKs** | Both | Either works |
| **Jupyter notebooks** | Python | Every eval tutorial and interview take-home |

**The honest split:** do your *production* eval harness in TypeScript with promptfoo so it lives next to your Playwright suite. Use Python for DeepEval metrics, RAGAS, and anything notebook-shaped.

---

## 2. Setup

```bash
# check what you have
python --version          # need 3.10+
py --version              # Windows launcher

# install from python.org if needed, or:
winget install Python.Python.3.12

# ALWAYS use a virtual environment
python -m venv .venv

# activate
.venv\Scripts\activate              # Windows cmd
.venv\Scripts\Activate.ps1          # PowerShell
source .venv/bin/activate           # Git Bash / Linux / Mac

# deactivate
deactivate

# packages
pip install openai anthropic python-dotenv
pip install deepeval ragas pytest
pip install pandas jupyter

pip list
pip freeze > requirements.txt
pip install -r requirements.txt
pip install --upgrade deepeval
pip uninstall deepeval
pip show deepeval

# faster modern alternative — worth using
pip install uv
uv venv
uv pip install -r requirements.txt
```

**`.gitignore` additions:**
```
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.ipynb_checkpoints/
.env
```

---

## 3. Python for a TypeScript developer — the deltas

```python
# ---------- syntax basics ----------
# no semicolons, no braces — INDENTATION defines blocks
# 4 spaces, consistently, or nothing works

name = "Alex"              # no const/let
age: int = 30                   # type hints are optional and NOT enforced at runtime
PI = 3.14159                    # uppercase = convention for constant, not enforced

# f-strings (like template literals)
print(f"Name: {name}, Age: {age}")
print(f"Next year: {age + 1}")
print(f"{age=}")                # prints "age=30" — great for debugging

# ---------- collections ----------
items = [1, 2, 3]                       # list      ≈ array
point = (10, 20)                        # tuple     ≈ readonly tuple
unique = {1, 2, 3}                      # set
user = {"name": "P", "age": 30}         # dict      ≈ object/Map

user["name"]                            # KeyError if missing
user.get("email")                       # None if missing
user.get("email", "default")            # with fallback

items.append(4)
items.extend([5, 6])
items.pop()
len(items)
items[0]
items[-1]                               # last element
items[1:3]                              # slice
items[::-1]                             # reversed

# ---------- conditionals ----------
if age > 18 and name:
    print("adult")
elif age > 12 or False:
    print("teen")
else:
    print("child")

# ternary — reads backwards from TS
status = "adult" if age > 18 else "minor"

# truthiness
if not items:           # empty list is falsy
    print("empty")

if value is None:       # use `is` for None, not ==
    pass

# ---------- loops ----------
for item in items:
    print(item)

for i, item in enumerate(items):
    print(f"{i}: {item}")

for key, value in user.items():
    print(f"{key}={value}")

for i in range(5):          # 0..4
    print(i)

for i in range(1, 10, 2):   # start, stop, step
    print(i)

while count < 10:
    count += 1              # no ++ in Python

# ---------- comprehensions — the most Pythonic thing ----------
squares = [x ** 2 for x in range(10)]
evens = [x for x in range(20) if x % 2 == 0]
names = [u["name"] for u in users if u["age"] > 18]
lookup = {u["id"]: u["name"] for u in users}        # dict comprehension
unique_tags = {t for u in users for t in u["tags"]} # set comprehension

# ---------- functions ----------
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}"

def summarise(*args, **kwargs):      # ≈ rest params + named options
    print(args)     # tuple
    print(kwargs)   # dict

greet("P")
greet(name="P", greeting="Hi")       # keyword arguments — very common

# lambda ≈ arrow function, single expression only
double = lambda x: x * 2
sorted_users = sorted(users, key=lambda u: u["age"], reverse=True)

# ---------- classes ----------
class EvalCase:
    def __init__(self, prompt: str, expected: str):    # constructor
        self.prompt = prompt          # `self` is explicit, always first param
        self.expected = expected
        self._internal = None         # single underscore = "private" by convention

    def run(self, model) -> str:
        return model.generate(self.prompt)

    def __repr__(self) -> str:        # like toString()
        return f"EvalCase({self.prompt[:30]}...)"

case = EvalCase("What is 2+2?", "4")   # no `new` keyword

# inheritance
class RagEvalCase(EvalCase):
    def __init__(self, prompt, expected, context):
        super().__init__(prompt, expected)
        self.context = context

# dataclass — much less boilerplate. use this.
from dataclasses import dataclass, field

@dataclass
class TestCase:
    prompt: str
    expected: str
    tags: list[str] = field(default_factory=list)
    threshold: float = 0.8

tc = TestCase(prompt="hi", expected="hello")
print(tc)    # auto __repr__, __eq__ for free

# ---------- error handling ----------
try:
    result = call_llm(prompt)
except TimeoutError as e:
    print(f"Timed out: {e}")
except (ValueError, KeyError) as e:
    print(f"Bad input: {e}")
except Exception as e:
    print(f"Unexpected: {e}")
    raise
else:
    print("no exception occurred")
finally:
    cleanup()

raise ValueError("Invalid threshold")

class EvalError(Exception):
    pass

# ---------- files and context managers ----------
with open("data.json") as f:          # auto-closes — always use `with`
    content = f.read()

import json
with open("cases.json") as f:
    cases = json.load(f)

with open("results.json", "w") as f:
    json.dump(results, f, indent=2)

import csv
with open("cases.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        print(row["prompt"])

# ---------- imports ----------
import os
import json as j
from pathlib import Path
from typing import Optional, Any
from deepeval.metrics import AnswerRelevancyMetric

# ---------- env vars ----------
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("OPENAI_API_KEY not set")

# ---------- type hints (optional but do use them) ----------
from typing import Optional

def score(text: str, threshold: float = 0.8) -> Optional[float]:
    ...

def process(items: list[dict[str, Any]]) -> dict[str, int]:
    ...

# ---------- async ----------
import asyncio

async def evaluate(case: TestCase) -> float:
    result = await call_llm_async(case.prompt)
    return score(result)

async def main():
    results = await asyncio.gather(*[evaluate(c) for c in cases])   # ≈ Promise.all
    return results

asyncio.run(main())
```

### Quick translation table

| TypeScript | Python |
|---|---|
| `const x = 5` | `x = 5` |
| `` `Hi ${n}` `` | `f"Hi {n}"` |
| `null` / `undefined` | `None` |
| `true` / `false` | `True` / `False` |
| `&&` `\|\|` `!` | `and` `or` `not` |
| `===` | `==` (use `is` only for `None`) |
| `arr.map(f)` | `[f(x) for x in arr]` |
| `arr.filter(f)` | `[x for x in arr if f(x)]` |
| `Object.entries(o)` | `o.items()` |
| `JSON.parse` / `stringify` | `json.loads` / `json.dumps` |
| `Promise.all` | `asyncio.gather` |
| `console.log` | `print` |
| `this` | `self` (explicit first param) |
| `class X { }` | `class X:` |
| `npm install` | `pip install` |
| `package.json` | `requirements.txt` / `pyproject.toml` |

---

## 4. pytest — the 30 minutes that matter

DeepEval runs on pytest, so you need this.

```bash
pip install pytest
pytest                          # run all
pytest test_eval.py
pytest test_eval.py::test_relevancy
pytest -k "relevancy"           # by name
pytest -v                       # verbose
pytest -s                       # show print output
pytest -x                       # stop on first failure
pytest --tb=short               # shorter tracebacks
pytest -m smoke                 # by marker
pytest -n 4                     # parallel (pip install pytest-xdist)
```

```python
# test_eval.py
import pytest

# plain test — function name must start with test_
def test_addition():
    assert 2 + 2 == 4

def test_with_message():
    score = 0.75
    assert score > 0.8, f"Score {score} below threshold"

# fixture ≈ Playwright fixture
@pytest.fixture
def sample_cases():
    return [
        {"prompt": "What is the capital of France?", "expected": "Paris"},
        {"prompt": "What is 2+2?", "expected": "4"},
    ]

def test_cases_load(sample_cases):
    assert len(sample_cases) == 2

# fixture with teardown
@pytest.fixture
def llm_client():
    client = create_client()
    yield client            # test runs here
    client.close()          # teardown

# scope: function (default), class, module, session
@pytest.fixture(scope="session")
def expensive_model():
    return load_model()

# parametrize ≈ data-driven tests
@pytest.mark.parametrize("prompt,expected", [
    ("What is 2+2?", "4"),
    ("Capital of India?", "New Delhi"),
    ("Largest planet?", "Jupiter"),
])
def test_factual_accuracy(prompt, expected):
    answer = call_llm(prompt)
    assert expected.lower() in answer.lower()

# markers
@pytest.mark.slow
def test_full_regression():
    ...

@pytest.mark.skip(reason="model endpoint down")
def test_broken():
    ...

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="no API key")
def test_needs_key():
    ...

@pytest.mark.xfail(reason="known hallucination issue, tracked in JIRA-42")
def test_known_failure():
    ...

# expecting an exception
def test_raises():
    with pytest.raises(ValueError, match="Invalid threshold"):
        set_threshold(1.5)

# approximate comparison — essential for scores
def test_score():
    assert score == pytest.approx(0.85, abs=0.05)
```

```python
# conftest.py — shared fixtures, auto-discovered
import pytest
from dotenv import load_dotenv

def pytest_configure(config):
    load_dotenv()
    config.addinivalue_line("markers", "slow: long-running tests")

@pytest.fixture(scope="session")
def golden_dataset():
    import json
    with open("data/golden.json") as f:
        return json.load(f)
```

---

## 5. Calling an LLM API

```python
# openai_example.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a concise assistant."},
        {"role": "user", "content": "What is the capital of Karnataka?"},
    ],
    temperature=0,          # 0 = as deterministic as you can get
    max_tokens=100,
)

print(response.choices[0].message.content)
print(f"Tokens: {response.usage.total_tokens}")
```

```python
# anthropic_example.py
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

message = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    system="You are a concise assistant.",
    messages=[{"role": "user", "content": "What is the capital of Karnataka?"}],
)

print(message.content[0].text)
print(f"In: {message.usage.input_tokens}, Out: {message.usage.output_tokens}")
```

```python
# structured output — critical for eval, forces parseable results
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Rate this answer 1-5 and explain."}],
    response_format={"type": "json_object"},
)
import json
result = json.loads(response.choices[0].message.content)
print(result["rating"], result["explanation"])
```

> **Cost control while learning:** use the cheapest model (`gpt-4o-mini`, `claude-haiku`), set `max_tokens` low, cache responses to disk during development, and set a hard spend limit in the provider dashboard on day one. A runaway loop over a golden dataset can burn real money.

---

## 6. Your 20-hour plan

| Hours | Topic | Deliverable |
|---|---|---|
| 1–2 | Setup, venv, pip, first script | `hello.py` runs in a venv |
| 3–6 | Syntax: collections, loops, comprehensions, functions | Rewrite 5 of your TypeScript P01–P12 programs in Python |
| 7–9 | Classes, dataclasses, error handling, files | A `TestCase` dataclass + JSON/CSV loader |
| 10–12 | pytest: fixtures, parametrize, markers | A parametrized test suite over a JSON dataset |
| 13–16 | LLM API calls, structured output, cost tracking | A script that queries 20 prompts and saves results |
| 17–20 | DeepEval basics (continues in the next file) | One metric running against your dataset |

---

## 7. Practice exercises

**PY01** — Read `cases.json`, print each prompt and expected answer.
**PY02** — Rewrite your TypeScript `groupBy` as a Python function using a dict comprehension.
**PY03** — A `@dataclass TestCase` with prompt, expected, tags, threshold. Load a list from JSON into it.
**PY04** — A parametrized pytest that checks 10 factual prompts against expected substrings.
**PY05** — Call an LLM API for each case, save results to `results.json` with token counts and latency.
**PY06** — Add a disk cache: if a prompt was already asked, reuse the saved answer instead of calling the API.
**PY07** — Compute a pass rate across all cases and print a summary table.
**PY08** — Add retry-with-backoff around the API call (same logic as your TypeScript P10).

---

## 8. What NOT to learn

Skip these entirely — they're not on your path:

- Django, Flask, FastAPI (web frameworks)
- Deep `asyncio` internals beyond `gather`
- Metaclasses, descriptors, `__slots__`
- NumPy/Pandas beyond reading a CSV into a DataFrame
- Training or fine-tuning models
- Packaging and publishing to PyPI

---

**Next:** `02-llm-theory-notes.md`
