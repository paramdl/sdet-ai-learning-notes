# GenAI Testing — Concepts Checklist

Tick these off as you learn them. Layer 0–1 is "understand GenAI at all". Layer 2–6 is the part that is actually *GenAI testing* — where a QA engineer adds value a developer usually does not.

---

## Layer 0 — Model mechanics (you cannot test what you cannot describe)

- [ ] **Token / tokenization** — models see tokens, not characters. Cost, limits and truncation are all token-based.
- [ ] **Context window** — total input + output budget. Overflow behaviour (silent truncation vs error) is a real bug class.
- [ ] **max_tokens / stop sequences** — output cut mid-sentence is the #1 "it broke" ticket.
- [ ] **Temperature, top_p, top_k, seed** — the knobs that make output non-deterministic. `temperature=0` is *not* fully deterministic.
- [ ] **Roles: system / developer / user / assistant** — where instructions live, and what a user can override.
- [ ] **Conversation state** — LLM APIs are stateless; the app resends history. The truncation strategy is testable behaviour.
- [ ] **Model IDs and versioning** — pinned vs floating aliases, deprecation dates, silent behaviour drift on upgrade.
- [ ] **Streaming (SSE)** — partial tokens, mid-stream errors, client abort, reconnect.
- [ ] **Token usage and cost accounting** — input vs output vs cached tokens; cost per request.
- [ ] **Rate limits (RPM / TPM), retries, backoff, timeouts** — this is ordinary API testing you already do well.
- [ ] **Embeddings and cosine similarity** — the basis of both retrieval and semantic assertions.
- [ ] **Prompting vs RAG vs fine-tuning** — know which the system under test uses; it changes the whole test strategy.

## Layer 1 — Application architectures you will be handed

- [ ] **Prompt-only app** (chatbot, rewriter, classifier)
- [ ] **RAG pipeline** — ingest → chunk → embed → store → retrieve → rerank → generate. Each stage fails differently.
- [ ] **Tool / function calling** — model emits a JSON call, app executes it. Wrong args, hallucinated tools, infinite loops.
- [ ] **Agents** — planning loop, memory, multi-step, MCP servers. Non-terminating loops and cost blowups.
- [ ] **Structured output** — JSON schema mode, parse failures, schema drift.
- [ ] **Guardrails layer** — input filter, output filter, moderation model, refusal policy.
- [ ] **Multimodal** — image/audio in and out; verification with no string to assert on.
- [ ] **Gateways / routers** — provider fallback, model aliasing, per-provider quirks (a common source of real bugs).

## Layer 2 — The core shift: how testing itself changes

- [ ] **Non-determinism** — the same input gives different output. `assertEqual` is dead; you assert on *properties*, not strings.
- [ ] **Evaluation vs testing** — a pass/fail gate becomes a *score* over a dataset, compared to a threshold.
- [ ] **Eval dataset (golden set)** — input + expected behaviour / ground truth. Building and curating this is the real job.
- [ ] **Sampling / N-runs** — run each case k times and assert on pass-rate (e.g. 9 of 10), not on one run.
- [ ] **Thresholds and flake budget** — what score ships, what blocks the build.
- [ ] **Test pyramid for GenAI** — deterministic unit tests (parsing, retrieval, schema) at the bottom; expensive model evals at the top.
- [ ] **Prompt versioning** — prompts are code. They need diffs, review, and a regression run.
- [ ] **Model-upgrade regression** — same eval suite, new model ID, compare scores. The highest-value suite you will own.

## Layer 3 — Metrics (know what each one actually measures)

**Deterministic / cheap**
- [ ] Exact match, contains, regex, is-JSON, JSON-schema validity
- [ ] Latency: **TTFT** (time to first token), tokens/sec, total latency
- [ ] Cost per request, token counts
- [ ] Refusal detection, format compliance, language / locale correctness

**Semantic**
- [ ] Embedding cosine similarity against a reference answer
- [ ] BLEU / ROUGE / METEOR (legacy translation and summarisation metrics)
- [ ] BERTScore

**LLM-as-judge**
- [ ] Rubric / criteria scoring (G-Eval style)
- [ ] Pairwise comparison (A vs B) — usually more reliable than absolute scores
- [ ] **Judge validation** — correlate judge scores with human labels *before* you trust the judge
- [ ] Judge biases: position bias, verbosity bias, self-preference, leakage of the answer into the judge prompt

**RAG-specific**
- [ ] **Faithfulness / groundedness** — is the answer supported by the retrieved context?
- [ ] **Answer relevancy** — does it answer the question that was asked?
- [ ] **Context precision / context recall** — did retrieval fetch the right chunks, and all of them?
- [ ] **Hallucination rate** — claims not present in context or in reality
- [ ] Chunk size / overlap effects, retrieval @k, reranker impact

**Agent / tool-use**
- [ ] Tool-selection correctness, argument correctness
- [ ] Task completion rate, step efficiency, loop termination
- [ ] Trajectory evaluation — was the *path* right, not just the final answer

## Layer 4 — Safety and security testing (the highest-demand skill right now)

- [ ] **OWASP Top 10 for LLM Applications** — learn the list cold; it is the shared vocabulary in bug reports.
- [ ] **Direct prompt injection / jailbreaks** — role-play, encoding, many-shot, language switching, instruction override.
- [ ] **Indirect prompt injection** — malicious instructions hidden inside retrieved docs, web pages, filenames, emails. The dangerous one for RAG and agents.
- [ ] **System-prompt leakage** — extracting the hidden prompt, keys, or internal policy.
- [ ] **Excessive agency** — the agent holds a tool it should not, or acts without confirmation.
- [ ] **Data exfiltration** — model persuaded to send data to an attacker URL or tool.
- [ ] **PII and secret leakage** — in outputs, logs, traces, and prompts.
- [ ] **Insecure output handling** — model output rendered as HTML / SQL / shell → XSS, injection, RCE.
- [ ] **Denial of wallet** — unbounded loops, huge inputs, token flooding, cost DoS.
- [ ] **Toxicity, bias, fairness** — demographic prompt sets, counterfactual pairs (same prompt, one attribute swapped).
- [ ] **Over-refusal** — the false-positive side of guardrails. Blocking legitimate use is also a bug.
- [ ] **Red teaming as a discipline** — attack taxonomies, automated attack generation, severity rating.

## Layer 5 — Operations

- [ ] **Tracing / observability** — traces and spans per request, prompt + response logging, PII scrubbing in logs.
- [ ] **Offline vs online eval** — pre-release eval suite vs monitoring on live production traffic.
- [ ] **Feedback loops** — thumbs up/down, and feeding real failures back into the golden set.
- [ ] **Drift monitoring** — the provider silently changes the model behind an alias.
- [ ] **CI integration** — eval suite in the pipeline, cost caps, response caching, nightly vs per-PR split.
- [ ] **Human-in-the-loop review** — annotation workflow, inter-rater agreement.
- [ ] **Load and concurrency** — streaming under load, queueing, provider rate-limit behaviour.

## Layer 6 — Governance (awareness level, but it wins interviews)

- [ ] **NIST AI Risk Management Framework**
- [ ] **ISO/IEC 42001** (AI management systems)
- [ ] **EU AI Act** risk tiers and what "high-risk" obliges
- [ ] Model cards / system cards; documented eval evidence
- [ ] Data residency, consent, and retention for prompts and outputs

---

## Tool landscape — learn three, know the rest by name

| Tool | What it is | Learn it? |
|---|---|---|
| **promptfoo** (Node) | YAML-driven prompt/model eval + red team. Lowest barrier for a QA engineer. | **Yes — start here** |
| **DeepEval** (Python) | Eval metrics written as `pytest` tests. Feels like normal test automation. | **Yes — second** |
| **Ragas** (Python) | RAG-specific metrics: faithfulness, context precision/recall. | **Yes, if RAG** |
| Giskard | Automated quality/vulnerability scanning of LLM apps | Know it |
| Langfuse / LangSmith | Tracing, datasets, online eval, prompt versioning | Know one |
| garak | LLM vulnerability scanner (jailbreak and leakage probes) | Try it |
| Microsoft PyRIT | Red-teaming automation framework | Know it |
| MLflow / W&B Weave | Experiment tracking plus eval | Know by name |
| Ollama / LM Studio | Run models locally, free — build labs without burning API credit | **Yes** |

---

## What "GenAI testing" actually is as a job

You will be asked to do four things. Map every concept above onto one of them:

1. **Own the eval suite** — golden dataset, metrics, thresholds, CI wiring.
2. **Red team it** — injection, jailbreak, leakage, excessive agency, cost abuse.
3. **Test the plumbing** — API contracts, streaming, tool calls, RAG stages, rate limits. Ordinary API and automation work, where you are already strong.
4. **Report so a PM can act** — score deltas per prompt version and per model version, not "it sometimes says weird things".
