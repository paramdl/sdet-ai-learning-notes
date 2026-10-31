# LLM Concepts — Theory & Study Notes

> These are notes to **understand**, not memorise. An interviewer can tell the difference in about thirty seconds. Where a concept has a testing implication, it's marked **→ Testing implication** — that's the part most candidates can't supply, and the part you can.

---

## 1. What an LLM actually is

A Large Language Model is a neural network trained to predict the next token given previous tokens. That's the entire objective. Everything else — reasoning, translation, coding — is emergent behaviour from doing that prediction well at scale.

**Key consequence:** the model has no notion of truth. It produces statistically likely continuations. "Hallucination" isn't a malfunction — it's the same mechanism that produces correct answers, applied where the training data was thin or the prompt was ambiguous.

**→ Testing implication:** you cannot test an LLM with `assertEquals`. There is no single correct output. Your assertions must be about *properties* of the output — relevance, groundedness, format, safety — not exact strings.

---

## 2. Tokens

Text is split into tokens before the model sees it. A token is roughly a word-piece.

```
"Testing is important"  →  ["Testing", " is", " important"]     3 tokens
"Bengaluru"             →  ["Beng", "aluru"]                    2 tokens
"antidisestablishment"  →  ["anti", "dis", "establish", "ment"] 4 tokens
```

Rules of thumb (English): **1 token ≈ 4 characters ≈ 0.75 words.** 1,000 tokens ≈ 750 words. Non-English text, code, and rare words tokenize less efficiently — Indian language text can cost 2–3× more tokens for the same meaning.

**Why it matters:**
- **Cost** is per token, input and output priced separately
- **Context window** limits are counted in tokens
- **Latency** scales with output tokens — the model generates one at a time

**→ Testing implication:** token count is a test assertion. A prompt change that quietly doubles token usage is a cost regression. Track tokens per request in your eval suite the way you'd track response time in a performance test.

---

## 3. Context window

The maximum tokens a model can consider at once — **input + output combined**.

| Model class | Typical window |
|---|---|
| Older / small | 4K–16K |
| Current standard | 128K |
| Extended | 200K–1M+ |

When you exceed it, you get an error or silent truncation. In a long chat, early messages fall out of the window — which is why a chatbot "forgets" what you said twenty turns ago.

**"Lost in the middle":** models attend most reliably to the beginning and end of their context. Information buried in the middle of a long document gets missed. This is measurable and repeatable.

**→ Testing implication:** two tests most teams skip —
1. **Long-conversation test:** does the system still honour a constraint stated 30 turns ago?
2. **Needle-in-a-haystack:** place a fact at position 10%, 50%, 90% of a long context and check retrieval at each. You will find the middle performs worst.

---

## 4. Temperature and sampling

The model outputs a probability distribution over the next token. Sampling parameters decide how you pick from it.

| Parameter | Effect |
|---|---|
| `temperature` (0–2) | 0 = pick the most likely token, near-deterministic. Higher = flatter distribution, more varied and more creative/erratic |
| `top_p` (0–1) | Nucleus sampling — consider only tokens in the top P cumulative probability mass |
| `top_k` | Consider only the K most likely tokens |
| `frequency_penalty` | Discourage repeating tokens already used |
| `presence_penalty` | Discourage repeating topics already mentioned |
| `seed` | Attempts reproducibility — best-effort, not guaranteed |
| `stop` | Sequences that end generation |

**Important honesty:** `temperature=0` is *not* fully deterministic. Floating-point non-determinism on GPUs, batching, and provider-side model updates all introduce variance. Same prompt, same settings, different day — you can get a different answer.

**→ Testing implication:** this is the single biggest difference from ordinary QA. You must:
- Set `temperature=0` for eval runs to minimise variance
- **Run each case N times** (3–5) and assert on the distribution, not one sample
- Use threshold-based assertions (`score >= 0.8`), never equality
- Distinguish genuine regression from sampling noise — if your pass rate moves from 94% to 91%, is that a bug or variance? You need a baseline variance measurement to answer

---

## 5. Embeddings and vector search

An embedding is a list of numbers (a vector, typically 384–3072 dimensions) representing meaning. Similar meanings land close together in that space.

```
"How do I reset my password?"     → [0.21, -0.43, 0.88, ...]
"I forgot my login credentials"   → [0.19, -0.41, 0.85, ...]   ← close
"What is the capital of France?"  → [-0.62, 0.11, -0.30, ...]  ← far
```

**Cosine similarity** measures the angle between two vectors: 1 = identical meaning, 0 = unrelated, -1 = opposite.

A **vector database** (Pinecone, Weaviate, Chroma, pgvector, FAISS) stores embeddings and finds the nearest neighbours to a query vector fast.

**→ Testing implication:** embeddings power semantic assertions. Instead of `expect(answer).toBe("Paris")`, you compute the similarity between the answer and the expected answer and assert `similarity > 0.85`. This is how you test meaning rather than wording. It's also how retrieval quality is measured in RAG.

---

## 6. Prompting

### Structure of a good prompt

```
[Role]        You are a senior QA engineer reviewing test plans.
[Task]        Identify missing negative test cases.
[Context]     The feature is a payment checkout supporting card, UPI, and wallet.
[Constraints] Return at most 5 cases. Do not repeat cases already listed.
[Format]      Return JSON: {"cases": [{"id": 1, "title": "...", "steps": [...]}]}
[Examples]    <one or two worked examples>
```

### Techniques

| Technique | What it is |
|---|---|
| **Zero-shot** | Just ask |
| **Few-shot** | Include 2–5 input/output examples. Usually the highest-value single improvement |
| **Chain-of-thought** | "Think step by step" — improves multi-step reasoning, costs more tokens |
| **Self-consistency** | Sample N answers, take the majority. Expensive but more reliable |
| **ReAct** | Reason → Act (call a tool) → Observe → repeat. The basis of agents |
| **Structured output** | Force JSON via schema/response_format. Essential for anything programmatic |

**→ Testing implication:** prompts are code and must be version-controlled and regression-tested. A one-word change to a system prompt can shift behaviour across hundreds of cases. Every prompt change should trigger a full eval run — this is exactly the CI gate you're going to build.

---

## 7. RAG — Retrieval Augmented Generation

The dominant production pattern. Instead of relying on training data, retrieve relevant documents and put them in the prompt.

```
User question
     ↓
[1] Embed the question
     ↓
[2] Vector search → top-k relevant chunks
     ↓
[3] (optional) Rerank the chunks
     ↓
[4] Build prompt: question + retrieved context
     ↓
[5] LLM generates an answer grounded in that context
     ↓
[6] Return answer + citations
```

**Why teams use it:** private/current data without retraining, citations for verifiability, cheaper than fine-tuning, easy to update (change the documents).

### Where RAG breaks — the test surface

| Stage | Failure mode |
|---|---|
| **Chunking** | Chunks too big (noise dilutes the signal) or too small (context severed mid-sentence) |
| **Embedding** | Query and documents embedded with different models, or a domain mismatch |
| **Retrieval** | Right answer exists but isn't in the top-k. **The most common RAG bug.** |
| **Reranking** | Relevant chunk retrieved but ranked below noise |
| **Generation** | Correct context retrieved, model ignores it and answers from parametric memory |
| **Citation** | Answer is right but cites the wrong source |

**→ Testing implication: you must test retrieval and generation separately.** If an answer is wrong, you need to know whether the retriever failed to find the document or the generator ignored it. Those are different bugs with different owners. Teams that only test the final answer cannot tell them apart — and this is a genuinely strong thing to say in an interview.

Metrics: **context precision** (are retrieved chunks relevant?), **context recall** (did we get everything needed?), **faithfulness** (is the answer supported by the context?), **answer relevancy** (does it address the question?).

---

## 8. Fine-tuning vs RAG vs prompting

| Approach | Best for | Cost | Update speed |
|---|---|---|---|
| **Prompting** | Behaviour and format changes | Near zero | Instant |
| **RAG** | Injecting knowledge, private/current data | Low–medium | Instant (reindex) |
| **Fine-tuning** | Consistent style, output format, domain tone, latency/cost reduction | High | Days |

**The rule:** prompt first, then RAG, then fine-tune. Fine-tuning teaches *behaviour*, not *facts* — using it to inject knowledge is a common and expensive mistake.

Related terms worth knowing: **LoRA** (parameter-efficient fine-tuning — trains small adapter matrices instead of all weights), **RLHF** (reinforcement learning from human feedback — how models are aligned to be helpful and harmless), **distillation** (training a small model to mimic a big one).

---

## 9. Agents and tool use

An agent is an LLM in a loop with tools and a goal.

```
Goal → LLM decides which tool to call → Tool executes → Result back to LLM
     → LLM decides next action → ... → Final answer
```

**Components:** tools (functions with described schemas), memory (short and long term), planning, and a termination condition.

**Where agents fail:**
- Wrong tool selected for the task
- Correct tool, malformed arguments
- Infinite loops — calling the same tool forever
- Doesn't recover from a tool error
- Cascading errors — step 3 is wrong because step 2 was slightly off
- Runaway cost — 40 tool calls for a task that needed 3

**→ Testing implication:** you test the **trajectory**, not just the final answer. Assert on: which tools were called, in what order, with what arguments, how many steps, total cost, and behaviour when a tool returns an error. An agent that reaches the right answer after 30 redundant calls has failed — and a final-answer-only test would score it as a pass.

**MCP (Model Context Protocol)** is a standard for exposing tools and data to models — which you already have hands-on with, via your QA MCP stack. That's a genuine talking point.

---

## 10. Hallucination

The model produces fluent, confident, false output.

**Types:**
- **Intrinsic** — contradicts the provided context (RAG-specific, and the most testable)
- **Extrinsic** — unsupported by context, may or may not be true
- **Factual** — contradicts reality
- **Citation** — invents a source, or cites a real source that doesn't say that

**Causes:** thin training data on the topic, ambiguous prompts, high temperature, long context (lost in the middle), and a strong tendency to answer rather than admit ignorance.

**Mitigations:** RAG with grounding, "say 'I don't know' if the context doesn't contain the answer" instructions, requiring citations, self-verification passes, lower temperature, and structured output constraints.

**→ Testing implication:** the highest-value test most teams don't write is the **"unanswerable question"** suite. Feed questions the knowledge base genuinely cannot answer and assert the system refuses rather than invents. Most RAG systems fail this badly, and it's a finding you can demonstrate in an interview.

---

## 11. Evaluation — the core of your specialisation

### Three families

**1. Reference-based** — compare against a known-correct answer
- Exact match, F1 — only work for short factual answers
- BLEU, ROUGE — n-gram overlap, from translation/summarisation. Weak for open-ended text
- Semantic similarity — cosine similarity of embeddings. Much better
- Requires a golden dataset

**2. Reference-free** — judge the output on its own properties
- Relevance, coherence, fluency, toxicity, format compliance
- Usually LLM-as-judge
- No golden answer needed, so it scales

**3. Human evaluation**
- The gold standard, and the bottleneck
- Used to calibrate and validate automated metrics
- Needs inter-annotator agreement measurement (Cohen's kappa) to be trustworthy

### LLM-as-judge

Use a model to score another model's output against a rubric.

```
You are evaluating an answer for faithfulness to the provided context.

Context: {context}
Question: {question}
Answer: {answer}

Score 1–5:
5 = every claim is directly supported by the context
3 = mostly supported, minor unsupported details
1 = contradicts the context or is entirely unsupported

Return JSON: {"score": <1-5>, "reasoning": "<one sentence>", "unsupported_claims": [...]}
```

**Known biases — state these in an interview:**
- **Position bias** — in pairwise comparison, prefers whichever came first. Mitigate by running both orders and averaging
- **Verbosity bias** — prefers longer answers regardless of quality
- **Self-preference** — a model rates its own family's output higher
- **Poor calibration** — clusters around 4 out of 5, rarely uses the full range

**The discipline that makes it valid:** label 50–100 examples by hand, run the judge on the same set, and measure agreement. If the judge doesn't agree with you, the judge is broken, and every number it produces downstream is noise. **Most teams skip this step.** Doing it is what makes you credible.

### Golden dataset

Your source of truth. Properties of a good one:

- **Representative** — mirrors real production query distribution, not just happy paths
- **Includes hard cases** — ambiguous, adversarial, out-of-scope, unanswerable
- **Versioned** — in git, with a changelog
- **Sized** — 50 well-chosen cases beats 5,000 generated ones
- **Labelled by a human** — at least for the seed set

---

## 12. LLM security — OWASP LLM Top 10

Know these ten by name. Your existing security instinct transfers directly here.

| # | Risk | Testing angle |
|---|---|---|
| **LLM01** | Prompt injection | Direct ("ignore previous instructions") and indirect (malicious text in a retrieved document or webpage) |
| **LLM02** | Insecure output handling | Model output rendered as HTML → XSS; passed to a shell → RCE; into SQL → injection |
| **LLM03** | Training data poisoning | Tainted fine-tuning or RAG corpus |
| **LLM04** | Model denial of service | Prompts engineered to maximise cost or compute |
| **LLM05** | Supply chain | Compromised models, plugins, or datasets |
| **LLM06** | Sensitive information disclosure | System prompt leakage, PII from training data or other users' context |
| **LLM07** | Insecure plugin design | Tools with excessive permissions or unvalidated arguments |
| **LLM08** | Excessive agency | Agent can take actions beyond what's needed — delete, send, purchase |
| **LLM09** | Overreliance | Users trusting unverified output |
| **LLM10** | Model theft | Extraction via systematic querying |

**Prompt injection is unsolved.** There is no complete defence — only layered mitigation: input filtering, privilege separation, output validation, human approval for consequential actions. Saying this plainly signals you actually understand the field rather than having read a vendor blog post.

**→ Testing implication:** an LLM red-team suite is a real deliverable. Jailbreak attempts, system-prompt extraction, indirect injection via a poisoned document in the knowledge base, PII leakage probes, and tool-abuse attempts. This is where web security findings and LLM knowledge combine into something almost nobody else has.

---

## 13. Guardrails

Controls applied around the model.

**Input guardrails:** PII detection and redaction, injection-pattern detection, topic restriction, rate and cost limits.
**Output guardrails:** toxicity and safety filters, PII scrubbing, format/schema validation, groundedness checks, refusal handling.

**The trade-off you must be able to discuss:** guardrails add latency and cost, and produce false positives. Too strict and the product refuses legitimate requests — which users experience as broken. Measure both false positive and false negative rates; reporting only one is meaningless.

---

## 14. Cost and latency

**Cost drivers:** input tokens, output tokens (usually 3–5× the input price), model tier, and retries.

**Optimisations:** prompt caching (big savings on a repeated system prompt), smaller model for simpler tasks, capping `max_tokens`, semantic caching of similar queries, and batching.

**Latency:** TTFT (time to first token) and TPOT (time per output token). Streaming improves *perceived* latency without changing total time. RAG adds retrieval latency; agents multiply latency by step count.

**→ Testing implication:** cost and latency are first-class assertions in an LLM eval suite. `p95 latency < 3s` and `average cost per query < ₹X` belong in CI alongside quality thresholds. A prompt change that improves accuracy 2% while tripling cost is usually a regression, and only your harness can reveal that trade-off.

---

## 15. Quick revision sheet

| Term | One line |
|---|---|
| Token | Word-piece; the unit of input, output, cost, and context |
| Context window | Max tokens the model sees at once (input + output) |
| Temperature | Randomness control; 0 = most likely token, still not fully deterministic |
| Embedding | Numeric vector representing meaning |
| Cosine similarity | Angle between vectors; 1 = same meaning |
| RAG | Retrieve relevant docs, put them in the prompt, generate a grounded answer |
| Chunking | Splitting documents before embedding |
| Top-k | How many chunks retrieval returns |
| Reranking | Reordering retrieved chunks by true relevance |
| Faithfulness | Is the answer supported by the provided context? |
| Answer relevancy | Does the answer address the question? |
| Context precision | Are the retrieved chunks relevant? |
| Context recall | Did retrieval find everything needed? |
| Hallucination | Fluent, confident, false output |
| Grounding | Tying output to verifiable source material |
| LLM-as-judge | Using a model to score outputs against a rubric |
| Golden dataset | Curated, human-labelled reference cases |
| Few-shot | Examples included in the prompt |
| Chain-of-thought | Prompting for step-by-step reasoning |
| Agent | LLM in a loop with tools and a goal |
| Trajectory | The sequence of agent steps — the thing you test |
| Function/tool calling | Model emits a structured request to invoke a function |
| MCP | Standard protocol for exposing tools and data to models |
| Prompt injection | Untrusted input hijacking model instructions |
| Guardrail | Input/output filter around the model |
| Fine-tuning | Further training to change behaviour, not to add facts |
| LoRA | Parameter-efficient fine-tuning via small adapters |
| RLHF | Alignment training from human preference data |
| Quantization | Reducing weight precision to shrink and speed up a model |
| Distillation | Training a small model to imitate a larger one |
| TTFT / TPOT | Time to first token / time per output token |

---

**Next:** `03-llm-testing-evaluation.md`
