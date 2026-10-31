# WHAT TO LEARN, AND WHY

> **Read this chapter first.** It answers one question for every topic in this handbook: *why does a GenAI tester need this, and what happens if I skip it?*
>
> Nothing here is padding. If a topic is in this table, it is because skipping it produces a specific, nameable failure in your work — and that failure is stated.

---

## The one-minute version

| | |
|---|---|
| **What the job is** | Producing evidence that an AI system works, and evidence of how it fails |
| **Why it is a new skill** | The same input produces different output, so you cannot assert equality. You measure distributions instead of checking values |
| **What transfers from your QA career** | ~60%. Test design, API testing, pytest, CI, security thinking, fault injection, reporting |
| **What is genuinely new** | ~40%. Evaluation design, judge validation, retrieval metrics, trajectory testing, prompt/model/corpus regression, token economics |
| **The skill that matters most** | Evaluation design (Part 6). Everything else is application |
| **The skill in shortest supply** | AI security testing (Parts 11–12). Highest pay, lowest competition |
| **The fastest way to be useful in week one** | The ten deterministic checks in Part 3 §3.9. No eval framework required |

---

## PRIORITY KEY

| | |
|---|---|
| 🔴 **MUST** | You cannot do the job without it. Skipping it means you cannot answer basic questions in an interview or a design review |
| 🟠 **SHOULD** | Expected of an advanced practitioner. Skipping it caps you at mid-level |
| 🟡 **OPTIONAL** | Useful in some roles. Learn when a specific job needs it |
| ⚪ **SKIP** | Belongs to another role. Learning it is a waste of your time |

---

# 1 · FOUNDATIONS — why before how

| Topic | Why you need it | If you skip it | Pri | Part |
|---|---|---|---|---|
| **AI / ML / DL / GenAI distinction** | Determines your entire test method. A classifier is tested against labels; a generator is tested against criteria | You build the wrong suite and waste a sprint | 🔴 | 1 |
| **Discriminative vs generative** | The boundary where exact-match assertions stop working | Every test you write is flaky | 🔴 | 1 |
| **Tokens & tokenization** | Every limit, price, and truncation is counted in tokens — and token efficiency varies 2–4× by language | You miss the silent-truncation bug that hits non-English users first | 🔴 | 1, 3 |
| **Context window** | Input + history + retrieved context + output must all fit. Overflow behaviour is a design decision | You miss system-prompt eviction, which is a *security* failure | 🔴 | 1, 3 |
| **Embeddings & cosine similarity** | The replacement for `==`, and the engine of all retrieval | You have no way to assert on free text | 🔴 | 1 |
| **Temperature / top-p / top-k** | Controls variance; `temperature=0` is **not** deterministic | You build a suite on a false assumption and the team blames your tests | 🔴 | 1 |
| **Inference: prefill vs decode** | Explains why latency has two independent components | You report one averaged latency number and hide the metric users feel | 🔴 | 1, 14 |
| **Transformer & attention (concept only)** | Explains quadratic cost, "lost in the middle", and why injection is architectural | You promise a fix for injection that cannot exist | 🟠 | 1 |
| **Fine-tuning vs RAG vs prompting** | The most common architectural mistake is using the wrong one | You do not catch "let's fine-tune to stop hallucinating facts" in review | 🟠 | 1 |
| **LoRA / quantization / distillation** | Each produces a **different model** requiring full re-evaluation | You certify a quantized model on a smoke test and miss a reasoning collapse | 🟡 | 1, 18 |
| **RLHF / RLAIF** | Source of refusal behaviour, and of **sycophancy** | You never test whether the model caves to a confident wrong user | 🟠 | 1 |
| **Reasoning models** | Hidden billed tokens; different latency profile | Your cost reporting is wrong by an order of magnitude | 🟠 | 1 |
| **Multimodal models** | Every modality is a new injection channel | Image and audio paths bypass your text-only filters | 🟠 | 1, 10 |
| ML mathematics, backpropagation, training loops | — | — | ⚪ | — |

---

# 2 · PROGRAMMING — what to learn and how deep

| Language | Why | If you skip it | Pri |
|---|---|---|---|
| **Python** | The entire GenAI ecosystem is Python-first. Every eval framework, provider SDK, and red-team tool | You cannot participate at all | 🔴 |
| **Bash / Linux** | Every model server, container, and CI runner is Linux | You cannot debug a deployment or read a production log | 🔴 |
| **SQL** | Eval results, traces, cost records, ground truth, and pgvector all live in databases | You cannot answer "has quality dropped since the upgrade?" with data | 🔴 |
| **JavaScript / TypeScript** | Playwright for AI UI testing; promptfoo config; reading product front-ends | You cannot test streaming UIs, where real user-visible bugs live | 🟠 |
| Go / Java / C# | Only if your employer's stack requires in-repo tests | Nothing | 🟡 |
| C++ / Rust | You consume these tools; you never modify them | Nothing | ⚪ |

### Python, by topic — the part that saves you months

| Tier | Topics | Why these specifically |
|---|---|---|
| **Beginner 🔴** | strings/f-strings, collections, comprehensions, JSON, file I/O **with encoding**, exceptions, venv, env vars | Prompts are strings; datasets are lists of dicts; API responses are nested dicts; keys must never be in code |
| **Intermediate 🔴** | **pytest** (fixtures, parametrize, markers), `httpx`, **Pydantic**, regex, logging, config management, pandas, percentiles | `parametrize` turns a dataset into a suite; Pydantic is the cleanest LLM-JSON assertion; you need p95, not averages |
| **Advanced 🟠** | decorators, generators, `async`/`asyncio`, rate-limit handling, NumPy, `unittest.mock` | 200 sequential eval calls take 15 minutes; async takes 40 seconds. Streaming responses *are* generators |
| **Skip ⚪** | metaclasses, GUI, Django, PyTorch training, algorithm puzzles | Not used in this role |

---

# 3 · THE TESTING DISCIPLINE — the 40% that is new

| Topic | Why you need it | If you skip it | Pri | Part |
|---|---|---|---|---|
| **The 12-layer request lifecycle** | Converts any architecture into a test plan. **9 of 12 layers are deterministic** | You over-focus on the scary model layer and ignore where incidents actually originate | 🔴 | 3 |
| **Prompt testing** | Prompts are the least-governed artefact in most AI products — often edited in a console with no review, version, or test | The highest-leverage process improvement available to you goes unmade | 🔴 | 4 |
| **Canary technique** | Turns fuzzy leakage judgement into an exact string match | Your leakage tests are unreliable and arguable | 🔴 | 4, 11 |
| **LLM API testing** | Streaming, `finish_reason`, usage reconciliation, tool-call payloads, 429 handling | You miss silent model substitution, unmetered streaming cost, and truncation presented as complete | 🔴 | 5 |
| **Evaluation design** | **The core competency.** Datasets, metrics, thresholds, N-run sampling | You can run someone else's eval but cannot design or defend one. This is the ceiling on your career | 🔴 | 6 |
| **Golden datasets** | The dataset *is* the test suite. A mediocre metric on a great dataset beats the reverse | Your suite passes forever while production fails | 🔴 | 6, 17 |
| **Threshold calibration** | A threshold chosen by intuition is an unfalsifiable magic number | Endless argument; no defensible gate | 🔴 | 6 |
| **LLM-as-judge** | The only scalable way to score subjective quality | You cannot test anything open-ended | 🔴 | 6 |
| **Judge validation (Cohen's kappa)** | Without it your scores are an opinion generator's output | When asked "according to whom?", you have no answer. **This single practice separates you from most candidates** | 🔴 | 6 |
| **Judge bias control** | Position, verbosity, and **self-preference** bias. A same-family judge flatters your own product | Your evaluation systematically lies in your favour | 🔴 | 6 |
| **N-run sampling / pass-rates** | A 20%-failure case passes a single run 4 times in 5 | You ship defects affecting a fifth of users, and your suite is flaky besides | 🔴 | 6 |
| **Reporting min and p10** | Users experience one sample, not an average | A mean of 0.88 with a min of 0.20 hides a failure someone will hit | 🔴 | 6, 14 |

---

# 4 · RAG — the most common production architecture

| Topic | Why you need it | If you skip it | Pri | Part |
|---|---|---|---|---|
| **The pipeline & stage isolation** | Lets you localise a failure to one stage instead of guessing | You report "wrong answer" instead of "Recall@5 is 0.42 because chunking splits the table" | 🔴 | 7 |
| **The retrieval-vs-generation question** | Retrieval causes ~75% of RAG failures; teams blame the model first | Weeks of prompt tuning on a chunking problem | 🔴 | 7 |
| **Precision@K / Recall@K / MRR / NDCG** | The shared vocabulary, and diagnostic in combination | You cannot quantify or direct a retrieval fix | 🔴 | 7 |
| **Chunking sweeps** | Turns "what chunk size?" from an argument into a decision table | The team argues from intuition forever | 🔴 | 7 |
| **Faithfulness with claim decomposition** | Produces "*these two sentences* are unsupported" instead of a score | Your hallucination findings are unactionable | 🔴 | 6, 7 |
| **Citation validation** | Fabricated citations are high-severity and **deterministically detectable** | You leave the cheapest critical finding on the table | 🔴 | 7 |
| **No-answer / abstention testing** | The most dangerous RAG failure is a confident answer from parametric knowledge dressed as a document answer | Untested, and indistinguishable from a correct answer | 🔴 | 7 |
| **Hybrid search necessity** | Vector search fails on exact identifiers ("ERR-5521") | You never discover why product-code queries fail | 🟠 | 7 |
| **Lost in the middle** | Justifies a reranker with evidence | You cannot defend an architectural recommendation | 🟠 | 7 |
| **Vector DB testing** | Wrong distance operator, unused index, post-filtering — all produce **wrong results with no error** | Silent quality loss that no exception reveals | 🔴 | 8 |
| **ANN recall vs exact** | An approximate index is a *quality* setting, not just a speed setting | A latency optimisation silently degrades every answer | 🟠 | 8 |

---

# 5 · AGENTS — where a wrong answer becomes a wrong action

| Topic | Why you need it | If you skip it | Pri | Part |
|---|---|---|---|---|
| **Tool/function calling** | Arguments are model-generated *text* that may not parse, and types drift | Unit confusion ($25 → 25 instead of 2500) reaches production | 🔴 | 5, 9 |
| **Trajectory testing** | An agent reaching the right answer via a destructive path "passes" outcome testing | You certify a system whose blast radius you never examined | 🔴 | 9 |
| **Fault injection** | Agents are tested on happy paths where every tool works. Production is not like that | You never see what happens when a tool errors, hangs, or returns hostile text | 🔴 | 9 |
| **Runtime permission enforcement** | A prompt instruction is not a control. The model attempting a forbidden call is normal | You test the model's refusal and certify a control that does not exist | 🔴 | 9 |
| **Caps: step / cost / time / depth** | The failure that makes the news is an agent looping until the bill arrives | Unbounded cost exposure with no guard | 🔴 | 9, 16 |
| **Idempotency** | Ordinary HTTP retry logic applied to a non-idempotent tool double-books customers | A real financial defect shipped | 🔴 | 9 |
| **Memory poisoning** | Persistent memory means the payload persists too, across sessions and users | A cross-session, cross-user control vector untested | 🟠 | 9 |
| **Multi-agent trust boundaries** | A parent trusting a child agent's output inherits its attacks | Injection one layer further from scrutiny | 🟠 | 9 |

---

# 6 · SECURITY — highest demand, lowest supply

| Topic | Why you need it | If you skip it | Pri | Part |
|---|---|---|---|---|
| **OWASP LLM Top 10** | The shared vocabulary of this field. Learn it cold | You cannot write a finding anyone will prioritise | 🔴 | 11 |
| **OWASP Agentic Top 10 (ASI)** | The agent-specific reference | Agent security findings have no framework to anchor to | 🟠 | 9, 11 |
| **Direct prompt injection** | Largely deterministic, fast to set up, produces critical findings | You leave your highest-value output untested | 🔴 | 11 |
| **Indirect prompt injection** | The victim is a *different* user, and it scales. Anyone who can upload a document may control the assistant | The single most impactful attack class goes untested | 🔴 | 11 |
| **Hidden context exposure** | Leaked prompts reveal the guardrails and the tool surface | You do not know what an attacker can learn | 🔴 | 11 |
| **Improper output handling** | Model output rendered as HTML/SQL/shell. The easiest critical finding, because teams trust model output | XSS and exfiltration chains shipped | 🔴 | 11 |
| **Markdown image exfiltration** | Zero-click data loss: the victim's browser sends data out on render | A complete exfiltration chain missed | 🔴 | 11 |
| **Cross-user / cross-tenant leakage** | Shared caches, missing tenant filters, ID enumeration | Customer data exposure | 🔴 | 5, 7, 11 |
| **Denial of wallet** | Expressed as "$X/hour from one free account", it gets management attention immediately | Unbounded cost abuse | 🔴 | 11, 16 |
| **Reporting success rates** | A probabilistic finding reported once gets closed as "cannot reproduce" | Your real findings are dismissed | 🔴 | 11 |
| **Red team method** | Objectives, scope, chaining, severity, "controls that held" | You produce a list of jailbreak curiosities instead of a prioritised report | 🟠 | 12 |
| **garak / PyRIT / promptfoo redteam** | Automated sweeps before manual chaining | You hand-write payloads and cover a fraction of the space | 🟠 | 12 |

---

# 7 · SAFETY & QUALITY DIMENSIONS

| Topic | Why you need it | If you skip it | Pri | Part |
|---|---|---|---|---|
| **Seven hallucination types** | Each has a different cheapest test; numeric and citation are deterministic | You treat hallucination as one unfixable blob | 🔴 | 13 |
| **Hallucination as a rate, not a ticket** | It is a property to contain, not a bug to eliminate | An endless non-converging ticket queue | 🔴 | 13 |
| **Guardrail four-corpus method** | A guardrail is a classifier; test it like one | You measure only one error direction | 🔴 | 13 |
| **Over-refusal** | Blocking legitimate users is a revenue problem nobody measures, because nobody files that bug | A product that refuses real customers, shipped | 🔴 | 13 |
| **Guardrail language parity** | Filters are routinely tuned on English only | A trivially-found critical gap left open | 🔴 | 13 |
| **Counterfactual bias method** | Produces arithmetic instead of a contestable opinion | Your fairness findings get argued away | 🟠 | 13 |
| **Refusal-rate parity** | The most measurable and least-measured fairness metric | Systematic discrimination by language, unmeasured | 🟠 | 13 |
| **Multimodal testing** | Vision hallucination, OCR on numeric fields, WER by accent, cross-modal injection | Whole input channels untested, including a guardrail bypass | 🟠 | 10 |

---

# 8 · OPERATIONS — what makes the work permanent

| Topic | Why you need it | If you skip it | Pri | Part |
|---|---|---|---|---|
| **Performance: TTFT vs total** | TTFT is the metric users feel in a streaming UI | You report a number that does not match user experience | 🔴 | 14 |
| **Realistic load profiles** | Latency depends on input *and* output length | Load-testing with "hi" measures nothing | 🔴 | 14 |
| **Quality under load** | Systems silently fall back to smaller models or less context under pressure | You certify a system that has degraded | 🟠 | 14 |
| **Fallback model quality** | The fallback is used during an incident — the worst time to discover it is bad | Quality drops by a third during outages with no signal | 🟠 | 14 |
| **Observability / tracing** | In a non-deterministic system, **an unreproducible incident can only be debugged from its trace** | No investigation is possible; and RAG/agent testing is guesswork | 🔴 | 15 |
| **Cost & token testing** | A code change can multiply the bill tenfold with no functional symptom. **Nobody else is testing this** | Silent cost regressions, and you miss the fastest route to visible business value | 🔴 | 16 |
| **Cost per resolved task** | Reframes model choice from "cheaper per call" to "cheaper per outcome", often reversing the answer | The team picks the wrong model for sound-looking reasons | 🟠 | 16, 18 |
| **Dataset discipline** | Versioning, held-out sets, never editing a case to pass | Your eval measures how hard you tuned, not quality | 🔴 | 17 |
| **Model upgrade regression** | Forced upgrades are routine; alignment changes as much as capability | A deprecation deadline becomes an outage | 🔴 | 18 |
| **Anchor-set drift detection** | The **only** way to catch a provider changing the model behind an alias | Inexplicable production regressions you cannot diagnose | 🟠 | 18 |
| **The seven regression suites** | Turns investigation into a permanent quality system | Every release is a fresh manual effort | 🔴 | 19 |
| **Delta gates & baseline discipline** | A delta is defensible; an absolute threshold is a negotiation | Your gates get argued down, then removed | 🔴 | 19 |
| **CI/CD design for cost and speed** | Most GenAI eval pipelines are switched off within two months for being slow and expensive | You build a suite nobody runs | 🔴 | 20 |
| **Docker** | Run your own test stack; reproduce CI locally | You depend on others for every environment | 🔴 | 21 |
| **Kubernetes (narrow slice)** | Read pod logs, spot OOMKills, check probe timeouts against LLM latency | You cannot investigate a staging failure yourself | 🟠 | 21 |
| **One cloud platform** | Deployments, quotas, regions, managed guardrails, residency | You mis-attribute platform refusals to the model | 🔴 | 22 |
| **LLMOps lifecycles** | Four artefacts version independently; each needs its own trigger | CI runs on code commits and misses three of the four | 🟠 | 23 |
| **Governance (NIST / ISO 42001 / EU AI Act)** | Your test evidence becomes audit evidence. Mostly vocabulary for work you already do | You cannot serve regulated or enterprise clients | 🟠 | 24 |

---

# 9 · WHAT NOT TO LEARN ⚪

Explicitly skip these. Each is a real time sink that does not pay back in this role.

| Topic | Why not |
|---|---|
| ML mathematics, backprop, optimisers | Teaches you to build models, not test them |
| PyTorch / TensorFlow training loops | Same |
| Model architecture design | Same |
| Prompt-engineering listicles and "AI SaaS in 10 minutes" content | Teaches building, not testing |
| Helm charts, operators, cluster networking, RBAC design | Platform engineering |
| Cloud architect certifications | Wrong role |
| Multiple clouds | Depth in one beats breadth in three |
| Java / C# / Go / Rust / C++ pre-emptively | Learn only when a specific job demands it |
| Reading regulations end to end | Read the obligations that map to tests |
| Algorithm-interview practice | Unless a specific employer screens on it |
| Every new eval tool that launches | Apply the three-question filter instead |

**The three-question filter for any new tool:** does it produce a score against a dataset? Can it run in CI unattended? Does it show you *why* a case failed? Anything failing all three is a dashboard, not a testing tool.

---

# 10 · THE HONEST SUMMARY

**If you learn only five things**, learn these, in this order:

| # | Skill | Why this one |
|---|---|---|
| 1 | **LLM fundamentals** (Parts 1, 3) | You cannot test what you cannot describe, and you cannot contribute in a design review |
| 2 | **Evaluation design + judge validation** (Part 6) | The core competency. It is the ceiling on your career level |
| 3 | **AI security testing** (Part 11) | Highest demand, lowest supply, largely deterministic, fastest to produce findings |
| 4 | **RAG testing** (Part 7) | The most common production architecture |
| 5 | **Observability** (Part 15) | The prerequisite that makes 2, 3, and 4 actually possible |

**The one sentence to carry:** traditional testing asks *"does output equal the expected value?"*; GenAI testing asks *"does output score above a defensible threshold, across a representative dataset, over repeated runs, on metrics I have validated?"* — and every topic in this handbook is downstream of that change.

**The one habit to build:** when you read a claim about how models behave — including every claim in this handbook — test it on your own system and write down the number. That habit *is* the skill.

---

**Next:** [WHAT-TO-DO-TOMORROW.md](WHAT-TO-DO-TOMORROW.md) — one task, ninety minutes, starting now.
