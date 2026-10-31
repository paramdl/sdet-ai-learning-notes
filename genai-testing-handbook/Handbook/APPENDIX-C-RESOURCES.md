# APPENDIX C — Resources

> **Primary sources only.** Every fast-moving fact in this book should be re-verified here rather than from a blog post or a course. Verified 8 September 2026.

---

## C.1 Security frameworks — the authoritative sources

| Resource | URL | Use for |
|---|---|---|
| **OWASP GenAI Security Project** | https://genai.owasp.org/ | The hub. LLM Top 10, Agentic Top 10, and supporting guidance |
| OWASP Top 10 for LLM Applications 2026 | https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/ | ⏳ Current edition (Aug 2026) |
| OWASP Top 10 for LLM Applications 2025 | https://genai.owasp.org/llm-top-10/ | Still widely referenced; know both numberings |
| OWASP Top 10 for Agentic Applications 2026 | https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ | ASI01–ASI10; the agent security reference |
| OWASP Agentic Security Initiative | https://genai.owasp.org/initiatives/agentic-security-initiative/ | Ongoing agent security work |

**Read the LLM Top 10 end to end, once.** It is the shared vocabulary of this field, and it takes an afternoon.

---

## C.2 Governance and standards

| Resource | Use for |
|---|---|
| **NIST AI Risk Management Framework** (nist.gov) | The Govern/Map/Measure/Manage structure; the Generative AI Profile |
| **EU AI Act** — official text and the Commission's AI Act service desk (`ai-act-service-desk.ec.europa.eu`) | Obligations and current timeline. ⏳ Dates have shifted; use the official source, not summaries |
| **ISO/IEC 42001** (iso.org) | AI management systems; the certifiable standard |
| ISO/IEC 23894 | AI risk management guidance |
| Your model provider's usage policy | A contractual obligation you can test compliance against |

---

## C.3 Tool documentation

Always the project's own docs, never a tutorial:

| Tool | Docs |
|---|---|
| promptfoo | promptfoo.dev/docs — see *Assertions & metrics* and *Red teaming* |
| DeepEval | deepeval.com — metric catalogue and changelog |
| Ragas | docs.ragas.io — each metric page explains the failure mode it detects |
| TruLens | trulens.org — ⏳ note the `trulens_eval` → `trulens` migration guide |
| Langfuse | langfuse.com/docs |
| Arize Phoenix | docs.arize.com/phoenix |
| garak | The project repository and `garak --list_probes` |
| PyRIT | The Microsoft repository — ⏳ verify the current package name |
| pgvector | The pgvector repository README — operators and index tuning |
| Qdrant | qdrant.tech/documentation |
| Ollama | ollama.com |
| OpenTelemetry GenAI conventions | opentelemetry.io — ⏳ still evolving |
| pytest | docs.pytest.org |
| Playwright | playwright.dev |
| k6 | grafana.com/docs/k6 |

---

## C.4 Provider documentation

Read the primary provider docs for whichever model you use — specifically these sections, which are where testable behaviour is defined:

- **Prompting guide** — how the provider expects its models to be instructed
- **Tool / function calling** — the exact payload contract
- **Structured outputs** — schema enforcement and its failure modes
- **Streaming** — event format and error semantics
- **Rate limits and errors** — the taxonomy your retry logic must handle
- **Pricing** — including reasoning and cached tokens
- **Model deprecations** — ⏳ **put these dates in your calendar**
- **Usage policies** — what your product may and may not do

---

## C.5 Benchmarks and datasets

| Resource | Use |
|---|---|
| **Hugging Face Hub** (huggingface.co/datasets) | Ready-made eval and adversarial datasets — so you never hand-write 500 jailbreak prompts |
| HELM (Stanford CRFM) | Multi-dimensional standardised evaluation methodology |
| MMLU / GSM8K / HumanEval / TruthfulQA | Standard capability benchmarks — for shortlisting only |
| HaluEval | Hallucination evaluation dataset |
| AdvBench / JailbreakBench | Adversarial prompt datasets — use for authorised testing only |

**Reminder from Part 18:** benchmarks shortlist; your own eval set decides.

---

## C.6 Reading order for a new learner

1. **This handbook, Parts 1–3** — fundamentals
2. **OWASP LLM Top 10 (2026)** — end to end, once
3. **Your provider's prompting and tool-calling docs** — the primary source
4. **promptfoo docs: Assertions** — then build something
5. **Ragas metric definitions** — each one names a failure mode
6. **This handbook, Parts 6, 7, 11** — the three that carry the most weight
7. **NIST AI RMF Core** — skim the four functions

**What to skip:** "build an AI SaaS in 10 minutes" video content, prompt-engineering listicles, and anything promising a job guarantee. They teach building, not testing.

---

## C.7 Staying current without drowning

| Cadence | Activity |
|---|---|
| Weekly | Release notes for the 2–3 tools you actually use |
| Monthly | Re-verify one ⏳ fact in this handbook against its primary source |
| Quarterly | OWASP GenAI project updates; golden-set representativeness test on your own projects |
| On notice | Provider deprecation announcements → run the upgrade suite early |
| Annually | Re-read Parts 1–3 |

**The discipline that matters:** when a fact in this book conflicts with a primary source, **the primary source wins.** This handbook was accurate on 8 September 2026 and will decay from that date. The concepts will not.

---

## C.8 Communities worth a look

- The OWASP GenAI Security Project working groups — open, and the fastest way into the security side
- Your tool's GitHub Discussions/Issues — where the real limitations are documented
- Local testing meetups — the ISTQB/testing community is increasingly covering AI

**A note on advice quality:** this field has a very high ratio of confident content to verified content. When you read a claim about how models behave — including in this handbook — the correct response is to test it on your own system and record the number. That habit is, ultimately, the entire skill.
