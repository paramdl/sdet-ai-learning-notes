# LLM & AI Testing — Interview Questions & Answers

> These answers are written to be **said out loud**. Where an answer contains a nuance most candidates miss, it's marked 🔑 — that's the sentence that makes an interviewer lean forward.

---

# Part 1 — Fundamentals

**Q1. What is an LLM, in one minute?**
A neural network trained to predict the next token given preceding tokens. That single objective, at scale, produces the ability to summarise, translate, reason and write code. 🔑 The important consequence for testing is that it has no internal concept of truth — it generates statistically likely continuations, so hallucination is the same mechanism as a correct answer applied where the data was thin.

**Q2. What is a token?**
The unit a model reads and writes — roughly a word-piece, about four characters in English. It matters because cost, context limits, and latency are all measured in tokens. 🔑 Non-English text tokenizes far less efficiently, so the same content in an Indian language can cost two to three times more — worth testing if the product is multilingual.

**Q3. What is the context window and how does it fail?**
The maximum tokens the model can consider at once, input and output combined. Exceeding it causes errors or silent truncation. 🔑 The subtler failure is "lost in the middle" — models attend reliably to the start and end of context but degrade in the middle, so I test retrieval at different depths rather than assuming a long window means the whole document is usable.

**Q4. What does temperature do? Is temperature 0 deterministic?**
Temperature controls randomness in token selection; 0 means always take the most likely token. 🔑 But it is *not* truly deterministic — GPU floating-point non-determinism, request batching, and silent provider-side model updates all introduce variance. That's precisely why I run each eval case multiple times and assert on distributions rather than single outputs.

**Q5. What is an embedding?**
A numeric vector representing meaning, where similar meanings sit close together. Cosine similarity measures that closeness. I use embeddings for semantic assertions — instead of checking an answer equals "Paris", I check its similarity to the expected answer exceeds a threshold, which tests meaning rather than phrasing.

**Q6. Explain RAG.**
Retrieval Augmented Generation: embed the user's question, search a vector store for relevant chunks, put those in the prompt, and have the model answer from them. It gives you current and private data without retraining, plus citations. 🔑 From a testing perspective the critical point is that it has two independently failing halves — retrieval and generation — and you must test them separately or you can't tell which one broke.

**Q7. RAG vs fine-tuning?**
RAG injects knowledge; fine-tuning changes behaviour. Use RAG for facts that change, fine-tuning for consistent style, format, or tone. 🔑 A common and expensive mistake is fine-tuning to teach facts — it's slow, costly, and the facts go stale immediately.

**Q8. What is an agent?**
An LLM in a loop with tools and a goal: it decides an action, a tool executes, the result returns, and it decides again until done. 🔑 Testing an agent means testing the trajectory, not just the final answer — an agent that reaches the right result after thirty redundant tool calls has failed on cost and latency, and a final-answer assertion would score it as a pass.

**Q9. What causes hallucination?**
Sparse training data on the topic, ambiguous prompts, high temperature, long contexts, and a strong bias toward producing an answer rather than admitting ignorance. Mitigations are grounding via RAG, explicit "say I don't know" instructions, required citations, and lower temperature. 🔑 None of these eliminate it, which is why the unanswerable-question test suite matters more than another twenty happy-path cases.

---

# Part 2 — Testing LLM systems

**Q10. How is testing an LLM different from testing normal software?**
Three differences. Output is non-deterministic, so equality assertions don't work — you assert on properties and thresholds. Correctness is a spectrum rather than binary, so results are scores. And there's no single expected output, so you need golden datasets and model-graded evaluation. 🔑 The mental shift is from "is this output correct" to "what proportion of outputs meet this standard, and has that proportion moved" — it's closer to statistical process control than to traditional automation.

**Q11. How do you handle non-determinism?**
Set temperature to 0 for eval runs. Run each case three to five times. Assert on the mean with a tolerance band rather than a single result. 🔑 And critically — establish baseline variance first, so you can distinguish a real regression from sampling noise. Without a baseline, a pass rate moving from 94% to 91% is uninterpretable.

**Q12. What is a golden dataset and what goes in it?**
A curated, human-labelled set of inputs with expected properties. Mine is roughly 40% factual, 20% edge cases, 15% unanswerable, 10% ambiguous, 10% adversarial, 5% multi-turn. 🔑 The unanswerable and ambiguous categories are the ones teams skip, and they're where systems fail worst — an assistant that invents an answer rather than saying "I don't know" is a production incident waiting to happen. Fifty well-chosen cases beat five thousand generated ones.

**Q13. Explain LLM-as-judge and its problems.**
Using a model to score another model's output against a rubric. It scales in a way human review can't. 🔑 But it has known biases: position bias in pairwise comparison, verbosity bias toward longer answers, self-preference for its own model family, and poor calibration — it clusters around 4 out of 5. So before trusting a judge I hand-label 50 to 100 examples and measure Cohen's kappa against it. Below about 0.6, I rewrite the rubric instead of reporting the numbers. Most teams skip that validation and end up making decisions on scores that don't correlate with anything.

**Q14. How do you evaluate a RAG system?**
Separately at each stage. Retrieval: context precision — are the retrieved chunks relevant — and context recall — did we find everything needed. Generation: faithfulness — is the answer supported by the retrieved context — and answer relevancy — does it actually address the question. 🔑 Testing only the final answer is the most common mistake: when it's wrong you can't tell whether the retriever missed the document or the generator ignored it, and those are different bugs with different owners.

**Q15. A RAG chatbot gives a wrong answer. Debug it.**
Four steps. First, check whether the correct document exists in the knowledge base at all — if not, it's a content gap, not a model bug. Second, run retrieval alone and see whether the right chunk is in the top-k; if it isn't, the problem is chunking, embedding, or ranking. Third, if the right chunk *was* retrieved, the generator ignored it — that's a prompt or grounding problem. Fourth, check chunk boundaries: a frequent cause is the answer being split across two chunks so neither is individually sufficient.

**Q16. What metrics do you track?**
Quality: faithfulness, answer relevancy, context precision and recall, and task-specific rubric scores. Safety: refusal rate on unanswerable questions, red-team pass rate, toxicity. Operational: p95 latency, cost per query, token usage. 🔑 I gate safety metrics absolutely at 100% and quality metrics statistically at around 90% — a jailbreak that works one time in twenty is a working jailbreak, not a flaky test.

**Q17. How do you test an agent?**
Trajectory assertions: which tools were called, in what order, with what arguments, how many steps, and total cost. Plus negative assertions that destructive tools weren't touched. And a failure-injection test — mock a tool to throw, and assert the agent degrades honestly rather than looping forever or claiming success it didn't achieve. 🔑 That last one catches the worst production behaviour: an agent that reports "booking confirmed" when the booking call failed.

**Q18. How would you put LLM evaluation in CI?**
Trigger on changes to prompts, retrieval code, or the golden dataset, plus a nightly full run. Each case runs three times. Results are compared against thresholds in a checked-in config, and the build fails on breach. The report is published as an artefact and summarised as a PR comment. 🔑 The key design decision is treating prompts as code — a one-word system-prompt change can shift behaviour across hundreds of cases, so it must trigger a full eval exactly like a code change triggers a regression run.

**Q19. How do you test for prompt injection?**
Direct attempts — "ignore previous instructions", system-prompt extraction, role-play jailbreaks, encoding bypasses in base64 or another language. And indirect injection, which matters more: plant an instruction inside a document that goes into the RAG knowledge base, then ask an ordinary question and see whether the model obeys the planted instruction. 🔑 Prompt injection is not a solved problem — there's no complete defence, only layered mitigation: input filtering, privilege separation, output validation, and human approval for consequential actions. Anyone who tells you their product is immune hasn't tested it properly.

**Q20. What is insecure output handling?**
Treating model output as trusted. If it's rendered as HTML you get XSS; passed to a shell, command injection; into a query, SQL injection. 🔑 It's the classic injection class with a new, very persuasive source of untrusted input — and it's the one where ordinary application security testing transfers directly.

---

# Part 3 — Scenario & design

**Q21. Design a test strategy for a customer support chatbot.**
Layered. Unit level: prompt template rendering, retrieval function, output parsers — fast and deterministic. Integration: RAG pipeline end to end with context precision and recall. Behaviour: golden dataset across factual, edge, unanswerable, ambiguous, and adversarial categories, run multiple times with threshold assertions. Security: red-team suite including indirect injection, run with zero tolerance. Operational: latency and cost budgets. Production: trace every call, sample outputs for human review, and feed failures back into the golden set. 🔑 That last loop is what keeps the suite relevant — every production failure becomes a permanent regression case.

**Q22. The team wants to change the system prompt. What do you do?**
Treat it as a code change. Run the full eval on both versions side by side — promptfoo handles A/B natively. Compare pass rate, per-category breakdown, cost, and latency. 🔑 I'd specifically look for regressions in categories nobody was thinking about: a prompt tuned to be more helpful very often degrades refusal behaviour, so the unanswerable and adversarial categories are where I'd expect the damage.

**Q23. Your eval pass rate dropped from 94% to 89%. Is that a bug?**
Not necessarily — first I'd check whether it's outside baseline variance. If the per-case standard deviation explains it, it's noise. If it's a genuine shift, I'd identify which cases flipped and look for a common category. Then check what changed: prompt, retrieval config, knowledge base content, or 🔑 the provider silently updating the model behind the same version string — which is a real failure mode and an argument for pinning model versions and monitoring for drift even when you changed nothing.

**Q24. How do you control eval costs?**
Cheapest adequate model for the judge, prompt caching for the repeated system prompt, disk caching during development so re-runs are free, running the full suite nightly while PRs run a smoke subset, and a hard spend cap at the provider. 🔑 And I'd track cost as a metric in the suite itself — a prompt change that gains two points of accuracy while tripling cost per query is usually a regression, and only the harness surfaces that trade-off.

**Q25. What would you do in the first month on an AI product with no testing?**
Week one: instrument. Trace every LLM call — prompt, context, output, tokens, latency, cost. You can't improve what you can't see. Week two: build a fifty-case golden dataset from real production queries and support tickets, weighted toward what users actually ask. Week three: an automated eval with a calibrated judge, and report the honest baseline. Week four: wire it into CI with thresholds, and a red-team suite. 🔑 I'd resist writing tests before instrumenting — without production traces you end up testing an imagined distribution of queries rather than the real one.

**Q26. How does your QA background help here?**
Directly. Risk-based prioritisation, boundary and negative testing, and the instinct to ask "what happens when this fails" all transfer. 🔑 The specific edge is that traditional QA people are trained to look for the case that breaks things — and LLM teams are usually staffed by ML engineers who evaluate on benchmarks and happy paths. The unanswerable-question suite and the indirect-injection test both come from a tester's mindset, not a researcher's.

**Q27. Should AI features be tested differently across risk levels?**
Yes. A content-suggestion feature failing is an annoyance; a system that quotes prices, gives medical guidance, or takes financial action failing is a liability. 🔑 I'd tier it: low-risk features get automated eval with statistical thresholds; high-risk features get that plus human review of a sample, mandatory citations, confidence-based escalation to a human, and no autonomous consequential action. The test strategy should follow the blast radius, not the technology.

**Q28. Can AI replace testers?**
It replaces test *execution* and a lot of test *authoring*, and it's already doing so. It doesn't replace deciding what's worth testing, interpreting an ambiguous failure, judging product risk, or arguing that a release shouldn't ship. 🔑 The roles that shrink are scripted manual regression; the roles that grow are people who can validate systems, design coverage, and — increasingly — test the AI systems themselves, which is a skill almost nobody has yet.

---

# Part 4 — Questions to ask them

Asking good questions is half the interview. These signal seniority:

1. "How do you currently measure whether a prompt change improved things, or is it vibes-based?"
2. "Do you have a golden dataset? Who labels it, and how often is it refreshed?"
3. "Have you validated your LLM judge against human labels? What agreement do you get?"
4. "Do you test retrieval separately from generation, or only the final answer?"
5. "What's your policy on model version pinning? Have you been bitten by silent provider updates?"
6. "Have you tested for indirect prompt injection through your knowledge base?"
7. "What's the blast radius if the model gets something wrong in production — who finds out first?"
8. "Is there a human in the loop for consequential actions, and how was that threshold chosen?"

🔑 Question 3 and question 6 in particular will tell you a lot about how mature the team really is — and asking them tells the interviewer you've done this rather than read about it.

---

## Preparation checklist

- [ ] Can explain tokens, context window, temperature, embeddings without notes
- [ ] Can draw the RAG pipeline on a whiteboard and name the failure mode at each stage
- [ ] Can explain LLM-as-judge biases **and** the calibration step
- [ ] Have actually measured Cohen's kappa on a real judge at least once
- [ ] Have a working red-team suite to point to, including indirect injection
- [ ] Can tell the story of one real finding from your own eval work
- [ ] Have your golden-dataset composition ratios memorised
- [ ] Have answers to Q10, Q13, Q14, Q19, Q25 polished — these are the ones that come up most

---

**Next:** `../04-Project/capstone-project.md`
