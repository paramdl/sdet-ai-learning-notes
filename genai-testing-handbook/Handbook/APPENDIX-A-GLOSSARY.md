# APPENDIX A — Glossary

> Terms you will meet in design reviews, job descriptions, and vendor documentation. Definitions are written for a tester, with the testing consequence where there is one.

---

**Abstention** — A system declining to answer because it lacks grounds to. The desired behaviour on unanswerable questions; measured as abstention rate.

**ACL (Access Control List)** — Per-document permissions. In RAG, must be enforced in the retrieval query, not by filtering results afterwards.

**Agent** — An LLM in a loop with tools, able to take actions. See Part 9.

**Agentic** — Adjective for systems that act autonomously. OWASP's ASI list covers agentic-specific risks.

**Alignment** — Training that makes a model helpful, harmless, and honest (RLHF/DPO). Source of refusal behaviour; can be weakened by fine-tuning.

**Anchor set** — A frozen set of test cases with recorded scores, re-run periodically to detect provider-side model drift.

**ANN (Approximate Nearest Neighbour)** — Index that trades recall for speed. **Quality parameter, not just a performance one.**

**Attention** — Transformer mechanism letting each token weigh all others. Cause of quadratic cost with sequence length.

**Autoregressive** — Generating one token at a time, each conditioned on all previous.

**Baseline** — Recorded metrics from a known version, used for delta gates in regression testing.

**BERTScore** — Embedding-based text similarity metric; more robust than ROUGE.

**BLEU** — N-gram overlap metric for translation. Rewards string overlap, not correctness.

**BM25** — Classic keyword ranking function. Complements vector search on exact identifiers.

**Canary** — A unique string planted in a hidden surface (system prompt, tool description, document) so leakage becomes an exact string match.

**Catastrophic forgetting** — A fine-tuned model losing general or safety capability. Requires full regression after any tuning.

**Chunking** — Splitting documents for embedding and retrieval. Size, overlap, and strategy are all testable parameters.

**Cohen's kappa** — Agreement between two raters, corrected for chance. The statistic used to validate an LLM judge.

**Context window** — Maximum tokens per request, covering input *and* output.

**Contextual hallucination** — Output contradicting or exceeding the provided context. The primary RAG failure mode.

**Cosine similarity** — Angle-based similarity between vectors; the standard text similarity measure. Handles negation poorly.

**Cross-encoder** — Model scoring a query and document together; used for reranking. Slower and more accurate than bi-encoder embeddings.

**Cross-modal injection** — Instructions hidden in an image, audio, or video that the model reads and a human reviewer does not see.

**DCG / NDCG** — Discounted Cumulative Gain and its normalised form; ranking metrics for graded relevance.

**Delta gate** — A CI rule expressed as change from baseline rather than an absolute threshold. More defensible.

**Denial of wallet** — Resource exhaustion where the resource is money. OWASP LLM06.

**Determinism baseline** — Measured variation across N identical requests at temperature 0. Publish it.

**Distillation** — Training a small model to imitate a larger one.

**DPO (Direct Preference Optimisation)** — A simpler alternative to PPO for preference training.

**Drift** — Change over time in inputs, corpus, model behaviour, or quality.

**Embedding** — A dense vector representing text meaning; the basis of semantic search and semantic assertions.

**Embedding inversion** — Partially reconstructing source text from its vector. Why raw embeddings must not be exposed.

**Eval / evaluation** — Scoring outputs against criteria over a dataset. The GenAI replacement for equality assertions.

**Excessive agency** — An AI system having more capability, permission, or autonomy than needed. OWASP LLM03 (2026).

**Faithfulness / groundedness** — Fraction of an answer's claims supported by the retrieved context.

**Few-shot** — Prompting with worked examples. Examples anchor format more strongly than instructions do.

**Fine-tuning** — Continuing training on domain data. Teaches behaviour, not durable updatable facts.

**finish_reason** — Why generation stopped: `stop`, `length` (truncated), `tool_calls`, `content_filter`.

**Flat index** — Exhaustive vector search; exact and slow. The reference point for measuring ANN recall.

**GEval** — A rubric-based LLM-as-judge metric pattern.

**GGUF / AWQ / GPTQ** — Quantized model weight formats.

**Golden set / golden dataset** — Curated inputs with expected behaviour. The core artefact of an eval programme.

**Guardrail** — A control around the model (input or output filter). A prompt instruction is *not* a guardrail.

**Hallucination** — Output not grounded in context or reality. Seven types in Part 13.

**Held-out set** — Dataset never used during development; detects overfitting to your own tests.

**Hidden Context Exposure** — OWASP LLM08 (2026); leakage of system prompts, tool definitions, retrieved context, or config. Formerly System Prompt Leakage.

**HNSW** — Graph-based ANN index. Tunable via `m`, `ef_construction`, `ef_search`.

**Hybrid search** — Combining vector and keyword retrieval. Needed for exact identifiers.

**Idempotency key** — Client-supplied identifier making a repeated request produce one effect. Essential for agent tools.

**Indirect prompt injection** — Payload delivered through content the model retrieves. Victim is a different user; scales.

**Inference** — Running a trained model on an input. Splits into prefill (TTFT) and decode (tokens/sec).

**Instruction hallucination** — Claiming to have performed an action that did not occur.

**IVF / IVFFlat** — Cluster-based ANN index; tuned via `lists` and `probes`.

**Jailbreak** — Bypassing a model's safety alignment (as opposed to the application's instructions).

**Judge (LLM-as-judge)** — Using a model to score outputs against a rubric. Must be validated.

**Knowledge cutoff** — The date beyond which a model has no training knowledge.

**LLMOps** — Operational discipline for LLM applications: prompt management, eval infrastructure, tracing, routing.

**LoRA** — Low-Rank Adaptation; cheap fine-tuning via small adapter matrices.

**Lost in the middle** — Reduced reliability of information placed in the middle of a long context.

**MCP (Model Context Protocol)** — A protocol for connecting models to tools and data sources. Runtime tool loading is a supply-chain surface (ASI04).

**MRR (Mean Reciprocal Rank)** — Average of 1/rank of the first relevant result.

**Multimodal** — Handling more than one modality (text, image, audio, video).

**Non-determinism** — Different output for identical input. The defining property that reshapes GenAI testing.

**Online evaluation** — Scoring sampled production traffic, as opposed to offline dataset evaluation.

**OpenTelemetry (OTel)** — Vendor-neutral observability standard, with GenAI semantic conventions.

**Over-refusal** — Blocking legitimate requests. The false-positive side of safety; a business defect.

**Pairwise comparison** — Judging which of two outputs is better. More reliable than absolute scoring; requires order swapping.

**Parametric knowledge** — What the model knows from training, as opposed to retrieved context.

**pgvector** — PostgreSQL extension adding vector types and similarity operators.

**Position bias** — A judge favouring whichever candidate appears first (or last).

**Precision@K** — Fraction of the top-K results that are relevant. Measures noise.

**Prefill** — The phase processing the input prompt; determines TTFT.

**Prompt injection** — Input treated as instruction rather than data. OWASP LLM01.

**Prompt template** — A parameterised prompt. Every variable is a test surface.

**Quantization** — Reducing weight precision to save memory and increase speed. Produces a *different* model requiring re-evaluation.

**RAG** — Retrieval-Augmented Generation.

**Recall@K** — Fraction of all relevant documents appearing in the top K. The metric that matters most in RAG.

**Reranking** — Rescoring retrieved candidates with a more accurate model.

**RLHF / RLAIF** — Reinforcement Learning from Human / AI Feedback. Source of alignment, and of sycophancy.

**ROUGE** — Recall-oriented overlap metric for summarisation.

**Sampling parameters** — Temperature, top-p, top-k; control output randomness.

**Self-preference bias** — A judge rating its own model family's output higher. Fixed by cross-family judging.

**Semantic assertion** — Asserting on embedding similarity rather than string equality.

**Shadow deployment** — Mirroring production traffic to a candidate version without exposing users to it.

**SSE (Server-Sent Events)** — The transport for streaming responses.

**Structured output** — Model output constrained to a schema, by prompting or by a provider mode.

**Sycophancy** — Agreeing with a user's stated premise or pushback rather than maintaining a correct answer.

**System prompt** — Developer instructions preceding the conversation. Not a security boundary.

**Temperature** — Sampling randomness control. `0` is greedy, **not deterministic**.

**Token** — A unit of text from the model's vocabulary. The unit of limits, cost, and truncation.

**Tokenizer** — Maps text to token IDs. Efficiency varies dramatically by language.

**Tool calling / function calling** — The model emitting a structured request for the application to execute.

**Top-K (retrieval)** — Number of results returned. **Top-k (sampling)** — number of candidate tokens considered. Two different things sharing a name.

**Top-p (nucleus sampling)** — Sample from the smallest token set whose cumulative probability exceeds p.

**Trajectory** — The sequence of steps an agent took. Must be asserted on, not just the final outcome.

**Transformer** — The neural architecture underlying modern LLMs.

**TTFT (Time To First Token)** — The latency metric users actually feel in a streaming interface.

**Unbounded consumption** — OWASP LLM06 (2026); resource and cost exhaustion.

**Vector database** — Storage optimised for similarity search over embeddings.

**WER (Word Error Rate)** — Speech-to-text accuracy metric. Report per accent group.

**Zero-shot** — Prompting with instructions only, no examples.
