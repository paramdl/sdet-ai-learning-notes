# GenAI Testing — Tools You Need to Learn

There are ~40 tools in this space and most are noise for a tester. This ranks them by whether you actually need to *learn* them, *try* them once, or just *recognise the name* in a JD or a design review.

---

## Tier 1 — Learn properly (5 tools, this is the real list)

| Tool | Type | Why it earns the slot |
|---|---|---|
| **Ollama** | Local model runtime | Free, unlimited, offline. Every lab and every red-team payload runs here at zero cost. Install this first, before any eval tool. |
| **promptfoo** | Eval + red team (Node, YAML) | Fastest path from nothing to a results grid. Declarative YAML, 30+ built-in assertion types, side-by-side model comparison, and a genuinely good `redteam` mode. Closest thing to "Postman for LLM evals". |
| **DeepEval** | Eval as code (Python, pytest) | Metrics expressed as `pytest` tests, so it drops into CI exactly like the suites you already run. This is where promptfoo YAML stops scaling. |
| **Ragas** | RAG metrics (Python) | The standard vocabulary for RAG quality: faithfulness, answer relevancy, context precision, context recall. If the product has a knowledge base, you will be asked for these numbers by name. |
| **Langfuse** | Tracing + datasets + online eval | Traces, spans, token/cost per step, prompt versioning, and datasets that feed back into evals. Learn one observability tool; this one is open-source and self-hostable. |

Those five cover offline eval, RAG eval, CI, and production monitoring. Everything below is depth on top.

---

## Tier 2 — Learn one from each row

### Model access
| Tool | Note |
|---|---|
| **Provider SDKs** (`anthropic`, `openai`) | Already installed on your machine. Know the raw HTTP shape too, not just the SDK. |
| **LiteLLM** | One OpenAI-compatible interface over 100+ providers. Lets one eval suite hit every model. Conceptually the same job as any in-house AI gateway. |
| **OpenRouter** | Hosted multi-model access from one key — handy when you need to compare models you have no accounts for. |
| LM Studio | GUI alternative to Ollama. Pick one, not both. |

### Security / red teaming
| Tool | Note |
|---|---|
| **promptfoo redteam** | Already in Tier 1. Generates attacks from a plugin catalogue (injection, PII, jailbreak, excessive agency) and reports by severity. Start here. |
| **garak** | NVIDIA's LLM vulnerability scanner — probe-based, closest thing to `nmap` for models. Point it at Ollama and let it run. |
| **PyRIT** | Microsoft's red-teaming automation framework. More of a construction kit than a scanner; heavier, more powerful. Check the repo for the current package name. |
| **Giskard** | Automated scan for hallucination, bias, injection, and robustness. Good for a fast first pass on a new target. |
| **Burp Suite** | Not GenAI-specific — but the app *around* the model (auth, IDOR, rate limits, output rendering) is still the biggest attack surface, and you already know this tool. |

### Observability
| Tool | Note |
|---|---|
| **Langfuse** | Tier 1 pick. Self-host needs Docker; cloud free tier does not. |
| **Arize Phoenix** | Open source, runs locally in a notebook, strong on RAG trace inspection. Good if you want tracing without a server. |
| LangSmith | Excellent, but LangChain-centric and closed. Know it by name. |
| Helicone | Proxy-based logging — one line of config, minimal code change. |

### Building targets to test
You cannot learn RAG testing without a RAG to break. Enough to build a small one:

| Tool | Note |
|---|---|
| **LlamaIndex** or **LangChain** | Learn just enough to assemble a pipeline. You are testing them, not becoming a developer in them. |
| **ChromaDB** | Simplest local vector store; runs in-process, no server. FAISS or Qdrant if you need more later. |
| **sentence-transformers** | Local embeddings, free, no API key. |
| **FastAPI** | Wrap the model in an HTTP API so you can test it the way you test everything else. |

---

## Tier 3 — Your existing tools, re-pointed

The most underrated part of the answer. You do not replace these; you aim them at a new target.

| Tool | New job in GenAI testing |
|---|---|
| **pytest** | Host for DeepEval metrics, parameterised eval datasets, N-run sampling |
| **Postman / Bruno** | LLM API contract testing, SSE stream inspection, tool-call payload validation |
| **Playwright** | E2E through the chat UI: streaming render, stop button, retry, message history, markdown/HTML injection in output |
| **k6 / JMeter** | Concurrency and TTFT under load, rate-limit behaviour, streaming stability |
| **GitHub Actions** | Cheap deterministic evals per PR, expensive judge evals nightly, with a cost cap |
| **pandas + Jupyter** | Analysing eval results — score distributions, run-to-run variance, regression deltas |
| **Excel/CSV reporting** | Same as your current audit reports; the deliverable format barely changes |

---

## Tier 4 — Recognise the name, do not spend a weekend

- **Inspect AI** (UK AI Safety Institute) — rigorous eval framework, research-flavoured
- **MLflow LLM Evaluate**, **W&B Weave** — eval inside an ML experiment-tracking platform
- **TruLens** — RAG feedback functions, overlaps heavily with Ragas
- **OpenAI Evals** — the original registry-based framework
- **Guardrails AI**, **NeMo Guardrails**, **Llama Guard** — guardrail *implementations*; you test these rather than use them
- **Helm / MMLU / TruthfulQA / HaluEval / AdvBench / JailbreakBench** — public benchmarks and attack datasets. Know they exist and where to pull them (Hugging Face) so you never hand-write 500 jailbreak prompts.
- **Hugging Face Hub / `datasets`** — source of ready-made eval and adversarial datasets

---

## Install order

Already on your machine: `anthropic`, `openai`, `python-dotenv`, `deepeval`, `pytest`, Node 24 / npx.

**Today:**

```powershell
# 1. Local model runtime - install from ollama.com, then:
ollama pull llama3.1:8b

# 2. Finish the Python eval stack
pip install tiktoken ragas litellm

# 3. promptfoo needs no install
npx promptfoo@latest --version
```

**Week 5, when you build the RAG lab:**

```powershell
pip install chromadb sentence-transformers llama-index
```

**Week 6, red teaming:**

```powershell
pip install garak giskard
```

**Week 7, tracing:**

```powershell
pip install langfuse
```

---

## How to judge a new tool

The space churns fast; half of Tier 4 will be renamed within a year. Three questions that survive:

1. **Does it produce a score against a dataset, or just a nice demo?** Demos do not gate a release.
2. **Can it run in CI without a human?** If not, it is an exploration tool, not a test tool.
3. **Does it tell you *why* a case failed?** A number with no failing trace attached generates no bug report.

Anything that fails all three is a dashboard, not a testing tool.
