# APPENDIX B — Tool Index

> Every tool worth knowing, with purpose, level, installation, first use, limitations, alternatives, and — importantly — **deprecation status**.

⏳ **All version-specific details verified 8 September 2026.** Package names and CLI flags change; always check the project's own current documentation before copying commands from any book, including this one.

---

## B.1 Deprecation and rename watch ⏳

**Check this list before following any tutorial written before 2026.**

| Old | Status | Use instead |
|---|---|---|
| `trulens_eval` (Python package) | **Deprecated and removed.** Renamed at v1.0; the old package errors on install | `trulens` plus its modular packages (`trulens-core`, `trulens-dashboard`) |
| **AutoGen** | **Maintenance mode** since late 2025 | **Microsoft Agent Framework** (1.0, April 2026) — merges AutoGen and Semantic Kernel |
| **Semantic Kernel** | **Maintenance mode** since late 2025 | Microsoft Agent Framework |
| OWASP LLM Top 10 **2025** | Superseded, but still widely referenced | **2026 edition** (Aug 2026) — know both numberings |
| Model IDs generally | Providers deprecate on published schedules | Track deprecation dates; test the successor before the deadline |

**A team building new agent work on AutoGen or Semantic Kernel today is accruing maintenance risk.** That is a legitimate design-review observation.

---

## B.2 Evaluation frameworks

### promptfoo 🔴 **learn first**
| | |
|---|---|
| **Category** | Evaluation + red teaming |
| **Purpose** | YAML-driven prompt and model evaluation with 30+ assertion types; side-by-side model comparison; a red-team mode with an attack plugin catalogue |
| **Why QA uses it** | Fastest path from nothing to a severity-ranked results grid. Declarative, so non-programmers can read the suite. Can target an HTTP endpoint, not just a raw model |
| **Level** | Beginner |
| **Install** | `npx promptfoo@latest --version` (no install needed) |
| **First use** | `npx promptfoo@latest init` → edit `promptfooconfig.yaml` → `eval` → `view` |
| **Key flags** | `--repeat N` (rate-based testing), `redteam init/generate/run/report` |
| **Advantages** | Zero-setup; excellent report; OWASP mapping in red-team mode; free local-model support |
| **Limitations** | YAML gets unwieldy past a few hundred cases; complex custom logic wants code |
| **Alternatives** | DeepEval (code-first), custom harness |
| **Verdict** | **Start here.** Then graduate the complex parts to DeepEval |

### DeepEval 🔴 **learn second**
| | |
|---|---|
| **Category** | Evaluation as code |
| **Purpose** | LLM metrics expressed as `pytest` tests — RAG, conversational, agentic, and custom rubric (G-Eval) metrics |
| **Why QA uses it** | Drops into an existing pytest suite and CI exactly like the tests you already run |
| **Level** | Intermediate |
| **Install** | `pip install deepeval` |
| **First use** | Write an `LLMTestCase`, pick metrics, `assert_test(case, [metrics])`, run with `pytest` |
| **Advantages** | Large metric catalogue; pytest-native; ⏳ a TypeScript SDK now exists alongside Python |
| **Limitations** | Metric API surface moves between versions; judge costs add up without caching |
| **Alternatives** | Ragas (RAG-specific), custom |
| **Companion** | **DeepTeam** — the red-teaming framework from the same team |

### Ragas 🔴 (if you have RAG)
| | |
|---|---|
| **Purpose** | RAG-specific metrics: faithfulness, answer relevancy, context precision, context recall |
| **Why QA uses it** | These four are the industry vocabulary; stakeholders ask for them by name |
| **Install** | `pip install ragas datasets` |
| **Limitations** | ⏳ API and metric names have changed across versions — check current docs; judge-model cost |
| **Note** | The *metric definitions* are stable and will outlast the library |

### TruLens 🟡
| | |
|---|---|
| **Status** | ⏳ **Package renamed** — `trulens_eval` is dead, use `trulens` |
| **Purpose** | Feedback functions plus tracing for RAG and agents |
| **Verdict** | Overlaps heavily with Ragas and Phoenix. Know the name; pick it only if you meet it in an existing codebase |

### Giskard 🟡
| | |
|---|---|
| **Purpose** | Automated scanning for hallucination, bias, injection, and robustness |
| **Why QA uses it** | Fast first-pass assessment of an unfamiliar system |
| **Install** | `pip install giskard` (LLM extras may be a separate install) |
| **Verdict** | Useful for a quick sweep; not a replacement for a designed suite |

### Inspect AI 🟡
Rigorous, research-oriented evaluation framework from the UK AI Safety Institute. `pip install inspect-ai`. Worth knowing by name; heavier than most product teams need.

### MLflow / Weights & Biases (Weave) 🟡
Experiment-tracking platforms with LLM evaluation features. Adopt if your organisation already uses them for ML — the integration value outweighs a better standalone tool.

---

## B.3 Observability

### Langfuse 🔴 recommended for real projects
| | |
|---|---|
| **Purpose** | Tracing, prompt management with versioning, datasets, online evaluation |
| **Why QA uses it** | The one tool that covers tracing *and* prompt versioning *and* datasets — three of your requirements in one |
| **Install** | `pip install langfuse`; self-host with Docker, or use the cloud tier |
| **Limitations** | Self-hosting needs infrastructure; sending prompts to the cloud tier is a privacy decision |

### Arize Phoenix 🔴 recommended for learning
| | |
|---|---|
| **Purpose** | Open-source tracing and evaluation, runs locally |
| **Why QA uses it** | No server required; excellent RAG trace inspection; notebook-friendly |
| **Install** | `pip install arize-phoenix` |
| **Verdict** | **Start here** — you can be looking at traces in ten minutes |

### LangSmith 🟠
Strong commercial platform; LangChain-centric and closed. Know it by name; you will meet it.

### Helicone 🟡
Proxy-based logging: change the base URL and you have traces. Lowest-effort adoption; less depth.

### OpenTelemetry 🟠
| | |
|---|---|
| **Purpose** | Vendor-neutral tracing standard with GenAI semantic conventions |
| **Why it matters** | Portability. A team locked into one vendor's SDK cannot move |
| **Install** | `pip install opentelemetry-api opentelemetry-sdk` |
| **Note** | ⏳ GenAI semantic conventions are still evolving — check current attribute names |

---

## B.4 Security and red teaming

### promptfoo redteam 🔴
Covered above. **Start here** — produces a severity-ranked, OWASP-mapped report out of the box.

### garak 🟠
| | |
|---|---|
| **Purpose** | LLM vulnerability scanner; probe-based, the `nmap` of models |
| **Install** | `pip install garak` |
| **First use** | `garak --model_type ollama --model_name llama3.1:8b --probes promptinject,leakreplay,encoding` |
| **Best for** | Model comparison during selection; safe unlimited practice against a local model |
| **Limitation** | Targets the model interface, not your full application stack |

### DeepTeam 🟠
⏳ Confident AI's red-teaming framework, companion to DeepEval. Natural fit if your evals are already DeepEval.

### Microsoft PyRIT 🟡
| | |
|---|---|
| **Purpose** | Red-teaming automation framework: orchestrators, converters (obfuscation), targets, scorers |
| **Best for** | Multi-turn adaptive attacks, where an attacker model adjusts based on responses |
| **Limitation** | A construction kit, not a scanner — steeper learning curve |
| **Note** | ⏳ Verify the current PyPI package name from the repository |

### Burp Suite 🟠
Not AI-specific — but the application *around* the model (auth, IDOR, rate limits, output rendering) remains the largest attack surface, and you already know this tool.

### OWASP GenAI Security Project 🔴 (resource, not a tool)
`genai.owasp.org` — the LLM Top 10, the Agentic Top 10 (ASI), and supporting guidance. **The authoritative reference for this domain.**

---

## B.5 Test automation

| Tool | Role in GenAI QA |
|---|---|
| **pytest** 🔴 | Host for everything. `parametrize`, fixtures, markers, xdist |
| **Playwright** 🟠 | AI UI testing: streaming render, stop button, markdown safety. Stub the SSE stream for determinism |
| Selenium 🟡 | Only if it is already the team's standard |
| **Postman / Bruno** 🟠 | Exploration and contract tests; limited SSE support; cannot express rate-based assertions |
| Newman 🟡 | Runs Postman collections in CI; a bridge, not a destination |
| REST Assured 🟡 | Java teams only |
| **httpx** 🔴 | Async + streaming HTTP; the right Python client for this domain |
| **respx** 🟠 | Mocking httpx — free, deterministic error-path testing |
| **Pydantic** 🔴 | Structured-output validation; the cleanest LLM JSON assertion |
| **tiktoken** 🟠 | Token counting for OpenAI-family models |

---

## B.6 Performance

| Tool | Notes |
|---|---|
| **k6** 🟠 | JS; excellent CI story and thresholds; SSE needs extra work |
| **Locust** 🟠 | Python-native; easiest if the team is Python; handles streaming well with async workers |
| JMeter 🟡 | Enterprise standard; poor fit for streaming |
| Artillery 🟡 | Good SSE/WebSocket support |
| **Custom async Python** 🔴 | Usually the right answer for accurate TTFT, cost tracking, and quality-under-load |

---

## B.7 AI frameworks (systems you will test, not build)

| Framework | Status | Note |
|---|---|---|
| **LangChain** 🟠 | Active | Widely used; know enough to read a pipeline |
| **LangGraph** 🟠 | Active | Graph-based agent orchestration; explicit state makes trajectory testing easier |
| **LlamaIndex** 🟠 | Active | RAG-focused; good for building your Part 25 lab |
| **OpenAI Agents SDK** 🟠 | Active | Lightweight agent framework |
| **Microsoft Agent Framework** 🟠 | ⏳ **Current** (1.0, April 2026) | The merged successor to AutoGen + Semantic Kernel; Python and .NET |
| AutoGen | ⏳ **Maintenance mode** | Migrate to Agent Framework |
| Semantic Kernel | ⏳ **Maintenance mode** | Migrate to Agent Framework |
| CrewAI 🟡 | Active | Role-based multi-agent |
| **LiteLLM** 🟠 | Active | One OpenAI-compatible interface over many providers; makes one eval suite hit every model |

---

## B.8 Vector databases

| Option | Testing notes |
|---|---|
| **pgvector** 🔴 | Easiest to test — SQL, transactions, `EXPLAIN`. Most common enterprise choice |
| **Qdrant** 🟠 | Rust; strong filtering semantics; trivial local Docker instance |
| **Chroma** 🟠 | Simplest for local labs; in-process, no server |
| Weaviate 🟡 | Built-in hybrid search; more concepts |
| Milvus 🟡 | Very large scale; heavier to operate |
| Pinecone 🟡 | Managed; less to operate, less to inspect — black-box testing only |

---

## B.9 Local models

| Tool | Notes |
|---|---|
| **Ollama** 🔴 | **Install this first.** Free, offline, OpenAI-compatible at `localhost:11434/v1`. `ollama pull llama3.1:8b` |
| LM Studio 🟡 | GUI alternative. Pick one, not both |
| llama.cpp 🟡 | The engine underneath; you rarely touch it directly |

**A 7–8B model needs ~8 GB free RAM. Use `llama3.2:3b` if that is tight.**

---

## B.10 Cloud platforms

| Platform | Key services for a tester |
|---|---|
| **Azure** | Azure OpenAI / AI Foundry (deployments), AI Content Safety, AI Search, Document Intelligence |
| **AWS** | Bedrock (model access is opt-in per region), Bedrock Guardrails, Knowledge Bases, Bedrock Agents, OpenSearch |
| **Google Cloud** | Vertex AI, Gemini via Vertex, Vertex AI Search, safety threshold settings |

⏳ Product names in this space change frequently. Learn **one** cloud properly — the one your employer uses.

---

## B.11 What to install today

```powershell
# Free local model — do this first
# (installer from ollama.com)
ollama pull llama3.1:8b

# Python eval stack
pip install pytest httpx respx pydantic python-dotenv tiktoken
pip install deepeval ragas
pip install arize-phoenix          # tracing, runs locally

# No install needed
npx promptfoo@latest --version

# Later: RAG lab
pip install chromadb sentence-transformers llama-index

# Later: red teaming
pip install garak giskard
```

---

## B.12 The filter for new tools

The space churns. Three questions that outlast any specific tool:

1. **Does it produce a score against a dataset, or just a demo?**
2. **Can it run in CI unattended?**
3. **Does it show you *why* a case failed?**

Anything failing all three is a dashboard, not a testing tool.
