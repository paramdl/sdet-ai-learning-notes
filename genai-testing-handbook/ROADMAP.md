# GenAI Testing — 8-Week Learning Path

Built for someone who already has strong manual + automation QA (Playwright, API testing, security-flavoured audits). You are not starting from zero — you are adding a layer on top.

Roughly 8–10 hours a week. Every week ends with something in `labs/` you can show.

---

## Week 1 — Talk to a model like an engineer, not a user

**Learn:** tokens, context window, temperature/top_p, roles, streaming, token cost, model IDs and deprecation.

**Do:**
- Call an LLM API by raw HTTP first (Postman or `curl`) — no SDK. See the JSON request/response shape, the `usage` block, the SSE stream frames.
- Then the same call with the Python SDK.
- Run one prompt 10 times at `temperature=0` and again at `1.0`. Diff the outputs. Write down what you observe — that observation *is* the whole reason GenAI testing exists.
- Send an input deliberately larger than the context window. Record what the API does.

**Output:** `labs/week1-notes.md` with your temperature-variance findings.

## Week 2 — Prompt engineering, from a tester's angle

**Learn:** system vs user prompt, few-shot, chain-of-thought, structured/JSON output, prompt injection basics.

**Do:**
- Write a prompt that must return strict JSON. Then try to break your own prompt: emoji, other languages, a 5000-word input, an input that says "ignore the above".
- Log every input that broke the JSON contract. That list is your first golden dataset.

**Output:** `labs/week2-jsonbreakers.csv` — inputs that broke format.

## Week 3 — First real eval suite (promptfoo)

**Learn:** eval dataset, assertions, thresholds, pass-rate over N runs, model comparison.

**Do:**
- `npx promptfoo@latest init` in `labs/promptfoo/` (a starter config is already there).
- Build 20 test cases against one real prompt — ideally a prompt from a system you already test (companion chat, AI tutoring, support replies).
- Mix assertion types: `contains`, `is-json`, `javascript`, `similar` (embeddings), `llm-rubric`.
- Run the same suite against two different models. Compare the grid.

**Output:** a promptfoo HTML report showing model A vs model B.

## Week 4 — Evals as code (DeepEval + pytest)

**Learn:** LLM-as-judge, G-Eval rubrics, judge bias, metric thresholds, CI wiring.

**Do:**
- Rewrite five of your Week-3 cases as `pytest` tests using DeepEval.
- Add answer-relevancy and a custom G-Eval rubric metric.
- Validate the judge: hand-label 20 outputs yourself, then check how often the judge agrees. If it agrees under ~80%, fix the rubric.

**Output:** `labs/deepeval/test_*.py` running green, plus your judge-agreement number.

## Week 5 — RAG testing

**Learn:** chunking, embeddings, vector store, retrieval @k, reranking; faithfulness, answer relevancy, context precision/recall, hallucination.

**Do:**
- Build a tiny RAG over documents you already own (product docs, specs or a public knowledge base).
- Deliberately break it: shrink chunk size to 50 tokens, set k=1, remove the reranker. Watch which metric moves.
- Ask questions the documents cannot answer. Does it hallucinate or say "I don't know"?

**Output:** a Ragas score table across three retrieval configurations.

## Week 6 — Security and red teaming

**Learn:** OWASP Top 10 for LLM Apps, direct vs indirect injection, system-prompt leakage, excessive agency, insecure output handling, denial of wallet.

**Do:**
- Run `promptfoo redteam` against one of your own targets — with written permission, on a demo/staging host, exactly as you already scope your security audits.
- Try `garak` against a local Ollama model so you can experiment freely.
- Plant an injection payload inside a document your Week-5 RAG ingests. That is indirect injection — the finding that carries real weight in a report.

**Output:** a red-team findings report in your usual facts-only bug format.

## Week 7 — Agents, tools, and observability

**Learn:** tool-call correctness, trajectory eval, loop termination, cost per task; tracing with Langfuse or LangSmith.

**Do:**
- Take an agent (an MCP server, or a small tool-calling script) and test: unavailable tool, tool returns an error, tool returns a hostile string, ambiguous request.
- Wire tracing in and inspect a full trace: spans, token counts, latency per step.

**Output:** a tool-call test matrix.

## Week 8 — Make it a deliverable

**Learn:** CI integration, cost caps, reporting scores to non-engineers, NIST AI RMF / EU AI Act vocabulary.

**Do:**
- Put the eval suite in GitHub Actions: fast deterministic checks on every PR, the expensive judge suite nightly.
- Extend your existing `QA-Framework-Template` with a `genai/` module so the next client project starts pre-wired.
- Write a one-page "GenAI test strategy" for one real product you test.

**Output:** a reusable GenAI eval module inside `<project-dir>`.

---

## Practice targets you already have

Use real systems instead of toy examples — you own access to these:

| System | What to practise on it |
|---|---|
| **AI companion chat** | persona consistency, NSFW guardrails, over-refusal, injection, credit/cost abuse |
| **AI gateway / model router** | provider fallback, model aliasing, streaming, error mapping, rate limits |
| **Product knowledge base** | RAG corpus for Week 5 |
| **AI tutoring features** | tutoring-domain accuracy, hallucination in subject answers |
| **Local Ollama model** | free, unlimited red-teaming sandbox |

Scope rule stays the same as your other audits: staging/demo hosts, written permission, no destructive payloads.

---

## Reading list (short, high signal)

- OWASP Top 10 for LLM Applications — read it end to end, once.
- Your model provider's own docs on prompting, tool use and streaming — the primary source, not a blog.
- promptfoo docs → "Assertions & metrics" and "Red teaming".
- DeepEval docs → the metrics catalogue.
- Ragas docs → metric definitions (each explains the failure mode it detects).
- NIST AI RMF Core — skim the four functions: Govern, Map, Measure, Manage.

Skip the YouTube "build an AI SaaS in 10 minutes" genre entirely. It teaches building, not testing.
