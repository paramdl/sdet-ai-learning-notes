# PART 25 — Real-World Projects

> **Goal of this part:** eight projects of increasing difficulty. Each one produces a portfolio artefact you can show in an interview. **Build the system yourself where needed** — you cannot learn to test a RAG pipeline without one to break, and building a deliberately imperfect one teaches you more than testing a perfect one.

**How to use this part:** do them in order. Each reuses the harness from the last. By project 8 you have a reusable GenAI testing framework, which is itself the most valuable artefact.

**Cost note:** projects 1–5 can be done entirely on a local Ollama model for £0. Projects 6–8 benefit from a paid API but can be adapted.

---

## Project 1 — Simple Chatbot Test Harness
**Level:** Beginner · **Time:** 1 week · **Prereq:** Python basics, Part 3

### Description
A single-prompt chatbot with a system prompt and no memory. Build it (30 lines) and test it properly.

### Architecture
```
User → FastAPI /chat → system prompt + user message → LLM → response
```

### Test strategy
Everything deterministic first. This project teaches you that most GenAI testing is ordinary testing.

### Test plan
| Suite | Cases | Type |
|---|---|---|
| API contract | 12 | Deterministic |
| Input validation | 10 | Deterministic |
| Error handling | 8 | Mocked |
| Format constraints | 6 | Deterministic |
| Determinism baseline | 1 measurement | Statistical |
| Basic quality | 20 | Semantic |

### Key test cases
```
P1-001  200 + schema valid on a normal question
P1-002  finish_reason == "stop" on every response
P1-003  Empty input → clarification request, no API call wasted
P1-004  10,000-character input → clean 400, not 500
P1-005  Response ≤ 3 sentences across 20 runs (report the RATE)
P1-006  429 from provider → backoff, retry, eventual success (mocked)
P1-007  Timeout → friendly message within N seconds
P1-008  API key never appears in any error response
P1-009  Determinism baseline at temperature 0, N=20
P1-010  Latency p95 under SLO
```

### Test data
20 questions relevant to your chosen domain; 10 malformed inputs; 5 boundary inputs.

### Automation
`pytest` + `httpx` + Pydantic schema models. Mocked provider for error paths.

### Metrics
Pass rate, p95 latency, determinism baseline (unique outputs / 20), cost per request.

### Security
API key handling, input length limits, error message leakage.

### Performance
50 sequential requests; record TTFT and total latency distribution.

### CI/CD
GitHub Actions running the deterministic suite on every push.

### Expected result
A green suite, a published determinism baseline, and the realisation that you have written almost no AI-specific code. **That realisation is the learning objective.**

---

## Project 2 — LLM API Testing Suite (multi-provider)
**Level:** Beginner+ · **Time:** 1 week · **Prereq:** Project 1, Part 5

### Description
Test the *same* prompts across two or more model providers through one harness. Teaches provider abstraction, contract differences, and comparison methodology.

### Architecture
```
Test harness → adapter layer → { Ollama | OpenAI-compatible | Anthropic }
```

### Test strategy
One dataset, one set of assertions, N providers. Every difference you find is either a contract difference (expected) or a bug (report it).

### Key test cases
```
P2-001  Identical request shape produces valid responses on all providers
P2-002  usage fields present and arithmetically consistent on each
P2-003  Streaming works and terminates on each
P2-004  Streaming reassembly matches non-streaming semantically
P2-005  Error taxonomy mapped: each provider's 429/400/500 handled uniformly
P2-006  Response `model` field matches the requested model
P2-007  Local token count vs provider count within 15%
P2-008  Tool-calling payload shape differences documented
P2-009  max_tokens truncation surfaced identically by the adapter
P2-010  Cost calculated correctly per provider's pricing
```

### Automation
`pytest.mark.parametrize` over providers; a shared `LLMAdapter` interface.

### Expected result
A **provider comparison table** (quality, cost, latency, contract quirks) and a reusable adapter. This adapter carries through every later project.

---

## Project 3 — Customer Support Chatbot Evaluation
**Level:** Intermediate · **Time:** 2 weeks · **Prereq:** Part 6

### Description
A support bot with a real system prompt, policy constraints, and conversation memory. The first project with a genuine evaluation suite.

### Architecture
```
User → App → history window + system prompt → LLM → guardrail → response
```

### Requirements to test against
- Max 3 sentences · Never promise refunds · Escalate when unsure
- Stay on topic · Match the user's language · Never reveal instructions

### Test plan
| Suite | Cases | Frequency |
|---|---|---|
| Hard constraints | 60 × 3 runs | Every PR |
| Quality rubric | 60 × 3 runs | Nightly |
| Conversation memory | 15 | Nightly |
| Multilingual | 20 | Nightly |
| Prompt injection | 25 | Nightly |
| Cost | 1 aggregate | Every PR |

### Key test cases
```
P3-001  ≤3 sentences: pass RATE over 3 runs ≥ 95%
P3-002  Never contains refund promises (hard, 100%)
P3-003  Escalates when the answer is unknown
P3-004  Turn-40 guardrail persistence (system prompt not evicted)
P3-005  Canary never emitted under 8 extraction attacks
P3-006  Responds in the user's language (6 languages)
P3-007  Guardrail holds in all 6 languages (the parity test)
P3-008  False premise rejected (sycophancy)
P3-009  Conversation cost curve bounded over 30 turns
P3-010  Client-supplied assistant turn is ignored by the server
```

### Evaluation metrics
Instruction-following rate per constraint (the conflict table from Part 4 §4.3), rubric score via LLM-as-judge, **judge validated with kappa on 40 hand labels**, refusal rate, cost per conversation.

### Automation
promptfoo for the prompt suite; pytest + DeepEval for the judged metrics.

### Expected result
A working eval suite **with a published judge-agreement number**. If you produce nothing else from this book, produce this — it is the artefact that demonstrates you understand evaluation rather than just running it.

---

## Project 4 — RAG Document Assistant
**Level:** Intermediate+ · **Time:** 3 weeks · **Prereq:** Parts 7, 8

### Description
Build a RAG system over a document set you own (product docs, a public dataset, your own notes), then test every stage.

### Architecture
```
PDFs → parse → chunk → embed → Chroma/pgvector → retrieve → rerank → LLM → answer + citations
```

### Test strategy
**Stage isolation.** Every failure must be attributable to a specific stage. This is the core skill the project teaches.

### Test plan
| Stage | Tests |
|---|---|
| Ingestion | Extraction fidelity, table integrity, metadata completeness |
| Chunking | Size/overlap sweep producing a decision table |
| Embedding | Model/dimension parity, coverage, reproducibility |
| Retrieval | Precision@5, Recall@5, MRR, NDCG on a 50-query golden set |
| Reranking | With/without comparison |
| Assembly | Position sensitivity ("lost in the middle") |
| Generation | Faithfulness, relevancy, citation validation |
| Security | Indirect injection, no-answer behaviour |

### Key test cases
```
P4-001  Chunking sweep: 4 configs × 50 queries → recall/precision table
P4-002  Recall@5 ≥ 0.85 on the golden set
P4-003  Exact identifier retrieval ("ERR-5521") — demonstrates hybrid need
P4-004  No-answer questions → abstention, never a parametric guess
P4-005  Faithfulness ≥ 0.85 with claim decomposition
P4-006  Zero fabricated citations (hard constraint)
P4-007  Lost-in-the-middle: fact at 5% / 50% / 95% of context
P4-008  Indirect injection via a planted corpus document
P4-009  Contradictory documents → conflict flagged, not silently resolved
P4-010  Corpus freshness: updated doc retrievable within SLA
```

### Test data
50-query golden set with labelled relevant chunk IDs; 15 unanswerable questions; 3 planted injection documents; 2 deliberately contradictory documents.

### Automation
Custom retrieval evaluator + Ragas for generation metrics.

### Expected result
A **chunking decision table**, a retrieval metrics dashboard, and a demonstrated indirect-injection finding. The chunking table is the single most interview-impressive artefact in this book — it shows you turn a config argument into data.

---

## Project 5 — Enterprise Knowledge Assistant (multi-tenant)
**Level:** Advanced · **Time:** 3 weeks · **Prereq:** Project 4, Part 11

### Description
Extend Project 4 with multi-tenancy, document-level permissions, and access control. The security-focused project.

### Architecture
```
User (tenant, groups) → auth → retrieval WITH tenant + ACL filter → LLM → answer
```

### Test strategy
Assume the isolation is broken until proven otherwise. Every test is an attempt to cross a boundary.

### Key test cases
```
P5-001  Tenant A canary never retrievable by tenant B (25 query variants)
P5-002  ACL enforced at the DATABASE query, not post-filtered in code
P5-003  Filtered search returns full K when K results exist (pre-filter proof)
P5-004  User without HR access gets abstention, not a summary
P5-005  Conversation history isolated across users
P5-006  Traces do not leak cross-tenant content
P5-007  Chunk metadata: zero NULL tenant_id
P5-008  Embedding API does not expose raw vectors
P5-009  Permission change takes effect within SLA (revoke → not retrievable)
P5-010  Tenant enumeration via error messages or timing not possible
```

### Security testing
Full Part 11 catalogue: cross-user, ACL, indirect injection, hidden-context leakage, output handling.

### Expected result
A tenant-isolation test suite and a security report in the format from Part 11 §11.5. **P5-003 and P5-009 are the two that most real systems fail.**

---

## Project 6 — AI Agent with Tools
**Level:** Advanced · **Time:** 3 weeks · **Prereq:** Part 9

### Description
An agent with 4–6 tools (lookup, calculation, a write action, an external API) and a confirmation gate on the write action.

### Architecture
```
Goal → planner loop → tool selection → permission check → execution → observation → ... → response
```

### Test plan
| Suite | Focus |
|---|---|
| Tool calling | Selection, arguments, types, ambiguity |
| Trajectory | Path, order, step count |
| Failure injection | 8 fault modes per tool |
| Loops & caps | Step, cost, time |
| Permissions | Runtime enforcement, confirmation bypass |
| Memory | Poisoning, isolation |

### Key test cases
```
P6-001  Ambiguous request → asks, does not guess
P6-002  Missing required parameter → asks, does not invent
P6-003  Arguments parse and schema-validate across 20 runs
P6-004  Unit handling: "$25" → 2500 cents
P6-005  Trajectory order: lookup → eligibility → action
P6-006  Forbidden tool never executed (runtime, not model, enforcement)
P6-007  Confirmation cannot be bypassed (6 persuasion attempts + a tool
        result claiming pre-approval)
P6-008  Hostile tool output does not redirect the agent
P6-009  Step cap, cost cap, and time cap all enforced
P6-010  Retry does not duplicate a side effect (idempotency key present)
P6-011  Memory poisoning does not persist across sessions or users
P6-012  Agent reports honest failure; never claims an unperformed action
```

### Automation
Custom `FaultyTool` harness (Part 9 §9.4) + trajectory assertions + tracing.

### Expected result
A trajectory test framework and a **tool inventory audit** table (tool × necessity × blast radius × reversibility). The audit is a two-hour exercise that consistently finds something.

---

## Project 7 — Multimodal Application
**Level:** Advanced · **Time:** 2 weeks · **Prereq:** Part 10

### Description
A document-understanding application: upload an invoice or receipt image, extract structured fields, answer questions about it.

### Architecture
```
Image upload → validation → vision model → structured extraction → validation → answer
```

### Key test cases
```
P7-001  Field extraction accuracy on 30 labelled documents
P7-002  NUMERIC fields exact-match (amounts, dates, IDs) — reported
        separately from prose fields
P7-003  Table structure preserved (row/column association)
P7-004  Object hallucination: leading question about an absent element
P7-005  Blank/corrupt image → honest error, not a fabricated description
P7-006  Rotated, low-contrast, and low-resolution variants
P7-007  Cross-modal injection: instruction text rendered in the image
P7-008  Metadata/filename injection
P7-009  Guardrail parity: same policy-violating request as text vs image
P7-010  File size, format, and count limits enforced before processing
P7-011  Multiple images: correct attribution ("in the first image…")
P7-012  Non-Latin script documents
```

### Expected result
A CER/accuracy report split by field type, and a **demonstrated cross-modal injection finding** — currently one of the most valuable things to have in a portfolio.

---

## Project 8 — Production-Grade AI Platform
**Level:** Expert · **Time:** 4–6 weeks · **Prereq:** all previous

### Description
Bring everything together: RAG + agent + multimodal + multi-tenant, with full CI/CD, observability, cost control, and a governance evidence pack.

### Architecture
```
Clients → Gateway (auth, rate limit, quota)
        → Router (model selection by task)
        → { RAG service | Agent service | Vision service }
        → Guardrails (in/out)
        → Observability (traces, metrics, cost)
        → Fallback chain
```

### Deliverables
```
□ Full test pyramid: contract → integration → eval → security → performance
□ CI/CD pipeline with quality gates and budget caps (Part 20)
□ Golden datasets, versioned, with a changelog (Part 17)
□ Validated judge with a published kappa (Part 6)
□ Baselines committed, with a documented update process (Part 19)
□ Full trace instrumentation via OpenTelemetry (Part 15)
□ Cost dashboard: per request, per user, per resolved task (Part 16)
□ Red-team report with objectives and chains (Part 12)
□ Load test with quality-under-load measurement (Part 14)
□ Degradation ladder tested at every rung (Part 14 §14.10)
□ Rollback drill executed and timed (Part 23)
□ Governance evidence pack (Part 24 §24.6)
```

### Expected result
A complete, portfolio-grade AI quality system. **This is the artefact that gets you hired as a senior or lead.** Put the repository on GitHub with a README explaining the *decisions*, not just the code — why these metrics, why these thresholds, why this pipeline shape.

---

## The portfolio pitch

When you present this work, lead with judgement rather than volume:

> "I built an eval suite for a RAG assistant. The interesting part was the judge: my first rubric had a Cohen's kappa of 0.42 against my own labels, which meant the scores were noise. Rewriting it to a binary verdict with a required reason got it to 0.78. I publish that number next to every score, so people know what the number is worth."

That paragraph demonstrates evaluation design, statistical honesty, and communication. It is worth more than a list of ten tools.

---

**Next:** [PART-26-TEST-CASE-LIBRARY.md](PART-26-TEST-CASE-LIBRARY.md) — the reusable test case library.
