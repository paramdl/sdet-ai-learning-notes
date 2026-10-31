# PART 5 — LLM API Testing

> **Goal of this part:** apply the API testing you already know to LLM endpoints, then add the six things that are genuinely new. This is the part of GenAI testing where your existing skills transfer almost completely — and it is where most production defects actually live.

**What transfers unchanged:** auth, headers, status codes, schema validation, rate limits, retries, timeouts, idempotency, pagination, error contracts, security headers.

**What is new:** ① token/usage assertions ② streaming/SSE ③ non-deterministic response bodies ④ cost per call ⑤ tool-call payloads ⑥ context-window errors.

---

## 5.1 The anatomy of an LLM API request

Most providers expose an OpenAI-compatible `/chat/completions` shape, which is why one harness can test many providers. Anthropic's `/v1/messages` differs in details (system prompt is a top-level field, not a message; different usage field names) but the test *strategy* is identical.

### Worked example — non-streaming

**REQUEST**
```http
POST /v1/chat/completions HTTP/1.1
Host: api.example.com
Authorization: Bearer sk-...
Content-Type: application/json

{
  "model": "llama3.1:8b",
  "messages": [
    {"role": "system", "content": "You are a support agent. Reply in at most 2 sentences."},
    {"role": "user",   "content": "How do I reset my password?"}
  ],
  "temperature": 0.2,
  "max_tokens": 200,
  "stream": false
}
```

**RESPONSE**
```json
{
  "id": "chatcmpl-8xK2p",
  "object": "chat.completion",
  "created": 1757312400,
  "model": "llama3.1:8b",
  "choices": [
    {
      "index": 0,
      "message": {"role": "assistant",
                  "content": "Go to Account Settings and select Reset Password. You'll get an email link."},
      "finish_reason": "stop"
    }
  ],
  "usage": {"prompt_tokens": 38, "completion_tokens": 21, "total_tokens": 59}
}
```

**What to assert — in priority order:**

| # | Assertion | Type | Why |
|---|---|---|---|
| 1 | HTTP 200 | Deterministic | |
| 2 | Response matches the JSON schema | Deterministic | Contract |
| 3 | `choices[0].finish_reason == "stop"` | Deterministic | Catches truncation (Part 3 §3.7) |
| 4 | `model` in response == model requested | Deterministic | **Catches silent model substitution by a gateway** |
| 5 | `usage.*` present and internally consistent | Deterministic | Cost accounting |
| 6 | `usage.prompt_tokens` ≈ locally counted tokens (±5%) | Deterministic | Catches hidden prompt injection by a gateway |
| 7 | Latency within SLO | Deterministic | |
| 8 | Content satisfies hard constraints (≤2 sentences) | Deterministic | |
| 9 | Content satisfies the rubric | **Probabilistic** | Requires eval (Part 6) |

**Assertions 4 and 6 are worth dwelling on.** They detect a class of bug you will only find if you look: a gateway or router silently serving a cheaper model than requested, or injecting extra system text into your prompt. Both are invisible in the content and obvious in the metadata.

**TEST CASE**
```
TC-API-001  Chat completion happy path
Category:     API
Precondition: Valid API key; model available
Input:        The request above
Steps:        1. POST the request  2. Capture response and latency
Expected:     200; schema-valid; finish_reason="stop"; model matches;
              usage present; total == prompt + completion;
              latency p95 < 3000 ms; content ≤ 2 sentences
Evaluation:   Deterministic assertions only
Priority:     Critical   Severity: Critical   Automatable: Yes
```

**AUTOMATED PYTHON TEST**
```python
# test_api_contract.py
import time, pytest, httpx
from pydantic import BaseModel, Field, ValidationError

# --- 1. Describe the contract as a Pydantic model. ------------------
#     Pydantic gives you schema validation AND a typed object in one step,
#     with an error message that names the exact failing field.
class Usage(BaseModel):
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)

class Message(BaseModel):
    role: str
    content: str

class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: str

class ChatCompletion(BaseModel):
    id: str
    model: str
    choices: list[Choice] = Field(min_length=1)
    usage: Usage


# --- 2. The test. ---------------------------------------------------
def test_chat_completion_contract(base_url, headers):
    payload = {
        "model": "llama3.1:8b",
        "messages": [
            {"role": "system", "content": "You are a support agent. Reply in at most 2 sentences."},
            {"role": "user", "content": "How do I reset my password?"},
        ],
        "temperature": 0.2,
        "max_tokens": 200,
    }

    start = time.perf_counter()
    r = httpx.post(f"{base_url}/chat/completions", json=payload,
                   headers=headers, timeout=30.0)   # ALWAYS set a timeout
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert r.status_code == 200, r.text

    # Schema validation. A ValidationError here names the exact bad field.
    try:
        body = ChatCompletion.model_validate_json(r.text)
    except ValidationError as e:
        pytest.fail(f"Response violated contract:\n{e}\nRaw: {r.text[:500]}")

    # Completion, not truncation.
    assert body.choices[0].finish_reason == "stop", \
        f"finish_reason={body.choices[0].finish_reason} — response was cut off"

    # Did we get the model we paid for? Catches gateway substitution.
    assert payload["model"] in body.model, \
        f"Model substituted: asked {payload['model']}, served {body.model}"

    # Usage arithmetic must be internally consistent.
    u = body.usage
    assert u.total_tokens == u.prompt_tokens + u.completion_tokens

    # Local token count should match the provider's, within tolerance.
    local = count_tokens_for_messages(payload["messages"])
    drift = abs(u.prompt_tokens - local) / max(local, 1)
    assert drift < 0.15, (
        f"Prompt token drift {drift:.0%}: provider says {u.prompt_tokens}, "
        f"we count {local}. Something is modifying the prompt."
    )

    assert elapsed_ms < 3000, f"Latency {elapsed_ms:.0f} ms exceeds SLO"

    # A hard content constraint — still deterministic.
    sentences = [s for s in body.choices[0].message.content.split(". ") if s]
    assert len(sentences) <= 2
```

**EXPECTED RESULT:** green. Every assertion here is deterministic and safe to run on every PR.

---

## 5.2 Authentication and authorization

| Test | Input | Expected |
|---|---|---|
| Valid key | correct key | 200 |
| Missing key | no `Authorization` header | 401, generic message |
| Malformed key | `Bearer garbage` | 401 |
| Revoked key | previously valid, now revoked | 401 immediately (**test that revocation is not cached**) |
| **Key in error response** | trigger any error | **The key must never appear in the body, headers, or logs** |
| Wrong tenant | tenant A's key against tenant B's resource | 403/404, no data |
| Key in URL query | `?api_key=…` | Should not be supported — keys in URLs land in logs and referrers |
| Rate limit per key | burst | 429 with `Retry-After` |
| Scope enforcement | read-only key on a write endpoint | 403 |

```
TC-AUTH-005  Credential leakage in errors                 [SECURITY]
Steps:      Trigger 400, 401, 429, and 500 responses
Expected:   No request contains the API key in any response body, header,
            or stack trace. Verify server logs too.
Priority:   Critical   Automatable: Yes (regex for the key prefix)
```

**For AI products specifically, add one test that has no traditional equivalent:**
```
TC-AUTH-006  Cross-user conversation leakage             [SECURITY]
Steps:      1. User A has a conversation containing a unique canary
            2. User B asks "what did we discuss earlier?" and variants
            3. User B requests conversation IDs belonging to A
Expected:   Zero cross-user content. Canary never appears for B.
Rationale:  Shared caches, shared vector namespaces, and conversation-ID
            enumeration are all real causes of this in AI products
Priority:   Critical   Severity: Critical
```

---

## 5.3 Request validation — the negative cases

| Case | Input | Expected |
|---|---|---|
| Missing `model` | omit field | 400, names the field |
| Unknown model | `"model": "does-not-exist"` | 404/400, not 500 |
| **Deprecated model** | a retired model ID | Documented behaviour: clean error **or** documented fallback. ⏳ Test this before every provider deprecation date |
| Empty `messages` | `[]` | 400 |
| Invalid role | `"role": "wizard"` | 400 |
| `temperature` out of range | `5.0`, `-1` | 400 |
| `max_tokens` > model max | huge value | 400, not silent clamping |
| Oversized context | window + 1 tokens | 400 with a clear message, **not 500** |
| Wrong content type | `text/plain` | 415 |
| Malformed JSON | truncated body | 400 |
| Extra unknown fields | `{"foo": 1}` | Documented: ignored or rejected — test which |
| Null content | `"content": null` | 400 |
| Duplicate roles | two consecutive `system` | Documented behaviour |

**The one that finds real bugs:** oversized context returning **500 instead of 400**. It means the app is not pre-checking the budget and is letting the provider fail. That is a defect *and* a wasted-cost path *and* a poor user experience, all in one finding.

---

## 5.4 Streaming / SSE testing

Mechanics are in Part 3 §3.6. Here is the test suite.

```python
# test_streaming.py
import json, httpx, pytest

def collect_stream(base_url, headers, payload):
    """Consume an SSE stream, returning the events and reassembled text.
    Kept separate from the tests so each test asserts on one property."""
    events, text = [], []
    with httpx.stream("POST", f"{base_url}/chat/completions",
                      json={**payload, "stream": True},
                      headers=headers, timeout=60.0) as r:
        assert r.status_code == 200
        assert "text/event-stream" in r.headers["content-type"]
        for line in r.iter_lines():
            if not line.startswith("data: "):
                continue
            raw = line[6:]
            if raw.strip() == "[DONE]":
                events.append("DONE")
                break
            evt = json.loads(raw)                    # each chunk must be valid JSON
            events.append(evt)
            delta = evt["choices"][0].get("delta", {}).get("content")
            if delta:
                text.append(delta)
    return events, "".join(text)


def test_stream_terminates(base_url, headers, payload):
    """A missing terminator makes the UI spin forever."""
    events, _ = collect_stream(base_url, headers, payload)
    assert events[-1] == "DONE", "Stream did not send a terminator"


def test_stream_matches_non_stream_semantically(base_url, headers, payload, embed):
    """Chunk-joining bugs drop characters. Compare semantically, since the
    two calls are independent generations and will not be identical."""
    _, streamed = collect_stream(base_url, headers, payload)
    blocking = httpx.post(f"{base_url}/chat/completions",
                          json={**payload, "stream": False},
                          headers=headers, timeout=30.0
                          ).json()["choices"][0]["message"]["content"]
    assert cosine(embed(streamed), embed(blocking)) > 0.85


def test_stream_reports_usage(base_url, headers, payload):
    """Token accounting is commonly implemented on the blocking path only,
    leaving all streamed traffic unmetered. That is a cost bug."""
    events, _ = collect_stream(base_url, headers, payload)
    usages = [e for e in events if isinstance(e, dict) and e.get("usage")]
    assert usages, "No usage reported on the streaming path — cost is unmetered"


def test_client_abort_stops_billing(base_url, headers, payload):
    """Abort after 3 chunks. Server-side generation should stop.
    If it does not, you pay for tokens nobody ever sees."""
    received = 0
    with httpx.stream("POST", f"{base_url}/chat/completions",
                      json={**payload, "stream": True, "max_tokens": 2000},
                      headers=headers, timeout=60.0) as r:
        for _ in r.iter_lines():
            received += 1
            if received >= 3:
                break                      # closing the context aborts
    # Then verify via usage logs that billed tokens are far below max_tokens.
```

**The security test for this layer:**
```
TC-STR-001  Output guardrail bypass via streaming         [SECURITY]
Precondition: The product has an output content filter
Steps:      1. Craft an input whose response the filter should block
            2. Request it with stream=true
            3. Observe what is RENDERED, not just what the API returns
Expected:   Blocked content is never displayed, even transiently
Failure:    Content appears token-by-token and is then retracted —
            the user has already seen it
Priority:   Critical   Severity: High
```

---

## 5.5 Rate limiting, retries, and timeouts

```python
import respx, httpx, time

@respx.mock
def test_backoff_has_jitter_and_a_cap(client):
    """Three properties matter: it retries, it waits longer each time,
    and it eventually gives up rather than hammering forever."""
    respx.post("https://api.example.com/v1/chat").mock(
        return_value=httpx.Response(429, headers={"Retry-After": "1"})
    )
    start = time.perf_counter()
    with pytest.raises(RateLimitExceeded):
        client.ask("hello")
    elapsed = time.perf_counter() - start
    assert client.attempt_count <= 5, "Retries not capped — will hammer the provider"
    assert elapsed >= 3, "Did not actually back off"
```

| Test | Expected |
|---|---|
| Sustained burst above the limit | 429 with `Retry-After`; no 500s |
| `Retry-After` honoured | Client waits at least that long |
| Backoff is exponential **with jitter** | Without jitter, N clients retry in lockstep and re-trigger the limit |
| Retry cap exists | Fails cleanly rather than retrying forever |
| **Retries are not applied to non-idempotent side effects** | An agent that retries a "send email" tool sends two emails |
| Client timeout < gateway timeout | Otherwise connections leak |
| Timeout produces a friendly message | Not a raw stack trace |
| Per-user vs per-key limits | A single abusive user must not exhaust the shared quota |

That last one is a design question worth raising: if rate limiting is only per-API-key and all users share one key, one user can deny service to everyone. ⏳ This maps directly to **LLM06 Unbounded Consumption** in the 2026 OWASP list, which rose four places precisely because this happens.

---

## 5.6 Tool / function calling at the API layer

When the model wants to call a tool, the response changes shape:

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "call_abc123",
        "type": "function",
        "function": {
          "name": "get_order_status",
          "arguments": "{\"order_id\": \"4471\"}"
        }
      }]
    },
    "finish_reason": "tool_calls"
  }]
}
```

**Note `arguments` is a JSON *string*, not an object.** It is model-generated text that happens to look like JSON, and it is not guaranteed to parse. That single fact generates most tool-calling defects.

```python
import json, pytest
from pydantic import BaseModel, ValidationError

class GetOrderStatusArgs(BaseModel):
    order_id: str            # note: STRING. Models emit ints for numeric-
                             # looking IDs constantly. Decide and enforce.

def test_tool_call_arguments_are_valid(client):
    resp = client.ask("What's the status of order 4471?")
    call = resp.choices[0].message.tool_calls[0]

    assert call.function.name == "get_order_status"

    # 1. Does it parse at all?
    try:
        args = json.loads(call.function.arguments)
    except json.JSONDecodeError:
        pytest.fail(f"Model emitted unparseable arguments: "
                    f"{call.function.arguments!r}")

    # 2. Does it match the schema? Type coercion bugs live here.
    try:
        GetOrderStatusArgs.model_validate(args)
    except ValidationError as e:
        pytest.fail(f"Arguments violate the tool schema: {e}")

    # 3. Is the value right?
    assert args["order_id"] == "4471"
```

| Test | Expected |
|---|---|
| Correct tool selected | The right function for the intent |
| Arguments parse as JSON | No `JSONDecodeError` across 50 runs |
| Arguments match schema | Types, required fields, enums |
| **Type coercion** | `"4471"` vs `4471` — pick one and enforce it. This is the single most common tool bug |
| Hallucinated tool name | Model invents a tool that does not exist → app rejects gracefully |
| Hallucinated parameter | Extra field not in the schema → rejected, not passed through |
| Missing required parameter | App asks the user, does not invent a value |
| No tool needed | Small talk must not trigger a tool call |
| Parallel tool calls | Multiple calls in one response handled correctly |
| Tool returns an error | Model handles it, does not loop |
| **Tool result is hostile** | A tool returning `"Ignore previous instructions…"` must not be obeyed — **this is indirect injection via tool output** |

Full agent-level treatment is Part 9.

---

## 5.7 Postman, curl, and Newman

**curl** — the ground truth, free of SDK behaviour:
```bash
# Basic call, with timing breakdown. -w gives you the numbers.
curl -s -X POST http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"llama3.1:8b","messages":[{"role":"user","content":"hi"}]}' \
  -w "\n\nttfb=%{time_starttransfer}s total=%{time_total}s http=%{http_code}\n" \
  | jq '{content: .choices[0].message.content, usage, finish: .choices[0].finish_reason}'
```

**Postman** — good for exploration, contract tests, and sharing with non-Python colleagues. Its test scripts are JavaScript:
```javascript
// Postman test tab
pm.test("Status 200", () => pm.response.to.have.status(200));

pm.test("Completed cleanly", () => {
  pm.expect(pm.response.json().choices[0].finish_reason).to.eql("stop");
});

pm.test("Usage is consistent", () => {
  const u = pm.response.json().usage;
  pm.expect(u.total_tokens).to.eql(u.prompt_tokens + u.completion_tokens);
});

pm.test("Latency under SLO", () => {
  pm.expect(pm.response.responseTime).to.be.below(3000);
});
```
⚠️ **Postman limitation for this domain:** SSE support is limited compared to code, and it cannot express "run this 20 times and assert a pass-rate". Use it for contract and exploration; use Python for evaluation.

**Newman** runs Postman collections in CI — a reasonable bridge if a team already has collections, but not where you should build your eval suite.

---

## 5.8 What a complete LLM API suite contains

```
tests/
├── conftest.py                  # clients, config, golden data fixtures
├── contract/                    # ← every PR, seconds, free (mocked)
│   ├── test_schema.py
│   ├── test_auth.py
│   ├── test_validation.py       # negative cases
│   └── test_errors.py           # fault injection: 429, 500, timeout
├── integration/                 # ← every PR, ~1 min, cheap (real, small)
│   ├── test_happy_path.py
│   ├── test_streaming.py
│   ├── test_tool_calling.py
│   └── test_usage_accounting.py
├── evaluation/                  # ← nightly, minutes, costs money
│   ├── test_quality.py          # rubrics, semantic similarity
│   └── test_regression.py       # vs stored baseline
└── security/                    # ← nightly + pre-release
    ├── test_injection.py
    ├── test_leakage.py
    └── test_cross_user.py
```

**The split is the point.** `contract/` and much of `integration/` are deterministic, fast, and free — they belong on every pull request. `evaluation/` and `security/` are slow and cost money — they run nightly with a budget cap. A CI design that runs everything on every commit will be switched off within a month because of cost, and then you have no testing at all.

---

## 5.9 Self-check

1. Why assert that the response `model` matches the requested model?
2. What does a 15% drift between your local token count and the provider's `usage` suggest?
3. Why is `tool_calls[0].function.arguments` a string, and what bug class follows?
4. How does streaming bypass an output guardrail?
5. Why must retries be disabled or made idempotent for tool-calling agents?
6. Give three reasons oversized-context returning 500 instead of 400 is a defect.
7. Which parts of your API suite belong on every PR, and which belong nightly? Why?

---

**Next:** [PART-06-LLM-EVALUATION.md](PART-06-LLM-EVALUATION.md) — the evaluation chapter: every metric, defined, with worked examples and judge validation.
