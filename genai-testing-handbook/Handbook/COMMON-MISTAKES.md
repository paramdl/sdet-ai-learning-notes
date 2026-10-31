# COMMON MISTAKES

## Things Traditional QA Engineers Get Wrong When Testing GenAI

> Each entry: the mistake, why it is tempting, what it costs, and the fix. These are ordered roughly by how often they occur and how much damage they do.

---

## 1. Exact string matching

**The mistake.** `assert response == "Your password can be reset in Account Settings."`

**Why it is tempting.** It is what testing has always been. It passes the first time you run it.

**What it costs.** The suite is red every second run. The team concludes "AI can't be tested", disables the suite, and ships blind.

**The fix.** Assert on *properties*: schema validity, required elements, forbidden terms, semantic similarity above a calibrated threshold, judge verdicts. Reserve exact match for genuinely deterministic outputs — extracted IDs, classification labels, enum values.

---

## 2. Treating LLM output as deterministic

**The mistake.** Running each case once and reporting pass/fail.

**Why it is tempting.** One run is fast and cheap, and `temperature=0` sounds like it should be deterministic.

**What it costs.** Both error directions. A case that fails 20% of the time passes your single run four times in five — you ship a defect affecting a fifth of users. And a genuinely healthy system produces a red build that everyone learns to ignore.

**The fix.** Run at N≥3 (N≥5 for release gates), assert on the pass-rate, and **measure your determinism baseline once and publish it** so nobody re-litigates the assumption.

---

## 3. Testing only the happy path

**The mistake.** A suite of well-formed questions with clear answers.

**Why it is tempting.** They are the easiest cases to write, and the ones that come to mind from the documentation.

**What it costs.** You test the cases the system handles well and none of the cases it handles badly. The suite passes forever while users complain.

**The fix.** Weight the dataset toward the difficult slices: unanswerable questions, ambiguous questions, adversarial phrasing, edge cases, and known past failures. **The unanswerable cases are the most valuable and the most commonly omitted.**

---

## 4. Ignoring hallucination as a system property

**The mistake.** Treating each fabrication as an individual bug to be fixed.

**Why it is tempting.** It looks like a bug: wrong output, file a ticket.

**What it costs.** An endless ticket queue that never converges, and a team that thinks the model is "getting worse".

**The fix.** Hallucination is a property to be *measured and contained*, not eliminated. Measure a hallucination rate by type. Contain with retrieval, groundedness checks, citations, and abstention behaviour. Report rates and trends, not individual instances.

---

## 5. Blaming the model when retrieval is at fault

**The mistake.** "The chatbot gave a wrong answer — the model is bad."

**Why it is tempting.** The model produced the visible output, so it looks responsible.

**What it costs.** Weeks of prompt tuning and model swapping on a problem that was a chunking configuration.

**The fix.** Always ask first: **was the correct information in the retrieved context?** No → retrieval bug. Yes → generation bug. Retrieval is the cause roughly three-quarters of the time.

---

## 6. Ignoring model variance in reporting

**The mistake.** Reporting the mean score.

**Why it is tempting.** Means are what dashboards want.

**What it costs.** A feature with a mean of 0.88 and a minimum of 0.20 has a failure that a user *will* hit. The mean hides it completely.

**The fix.** Report mean, **minimum, and p10**. Users experience one sample at a time, not an average.

---

## 7. Ignoring prompt injection

**The mistake.** Testing quality and functionality; leaving security to "the security team".

**Why it is tempting.** It feels like someone else's job, and it sounds exotic.

**What it costs.** The highest-severity findings in the product go untested. Nobody else is testing them either — the security team is testing the web app, not the model.

**The fix.** Injection testing is largely deterministic and takes a day to set up with canaries. It produces your most valuable findings. Do it in week one, not month six.

---

## 8. Testing the model's refusal instead of the runtime's enforcement

**The mistake.** "I asked the agent to do something it shouldn't and it refused — permissions work."

**Why it is tempting.** The observable behaviour was correct.

**What it costs.** You certified a control that does not exist. The model refused *this time*; models are persuadable, and the runtime may execute the call the moment one does not.

**The fix.** Check the enforcement layer. It is normal and expected for the model to attempt a forbidden call; the bug exists only if the runtime executes it. Test at the runtime, not the model.

---

## 9. Ignoring cost

**The mistake.** Cost is finance's problem.

**Why it is tempting.** No other software category has made cost a quality attribute.

**What it costs.** A prompt edit multiplies the bill tenfold with no functional symptom. Nobody notices until the invoice arrives, and then nobody knows which change caused it.

**The fix.** Cost regression gate in CI. Prompt token budgets asserted. Cost per resolved task reported per model. Denial-of-wallet expressed as a spend rate. **Nobody else in the team is doing this — it is the fastest way to demonstrate business value.**

---

## 10. Ignoring token behaviour, especially multilingual

**The mistake.** Enforcing a character limit and assuming it protects a token limit.

**Why it is tempting.** Characters are what the UI counts.

**What it costs.** Non-Latin-script users are silently truncated. It is a real, high-severity, reproducible defect that discriminates against a specific user population — and almost nobody tests it.

**The fix.** Count tokens with the model's own tokenizer. Test parity across every language you support.

---

## 11. Ignoring tool calls and trajectories

**The mistake.** Testing an agent by checking its final answer.

**Why it is tempting.** The answer is the deliverable.

**What it costs.** An agent that reaches the right answer via a destructive path "passes". You have certified a system whose blast radius you never examined.

**The fix.** Assert on the trajectory: which tools, in what order, within what caps, with a forbidden list. And cross-check claimed actions against the trace — models claim to have done things they did not.

---

## 12. Ignoring data leakage paths

**The mistake.** Testing that user A cannot see user B's data in the UI.

**Why it is tempting.** That is where leakage has traditionally happened.

**What it costs.** The leak is elsewhere: in the retrieval layer without a tenant filter, in a shared cache, in the trace platform, in the model's context from a previous turn, or in an error message.

**The fix.** Enumerate every path data can take: retrieval, conversation history, tool results, logs, traces, error responses, and third-party processors. Canary each one.

---

## 13. Ignoring observability

**The mistake.** Treating tracing as an ops concern.

**Why it is tempting.** Traces have historically been for debugging production, not for testing.

**What it costs.** In a non-deterministic system, an incident you cannot reproduce can only be debugged from its trace. No trace means no investigation. It also means you cannot test RAG or agents properly at all.

**The fix.** Treat trace completeness as a testable requirement. "There is no trace for this request" is a defect, and a high-priority one.

---

## 14. Building the golden set from documentation

**The mistake.** Generating test questions from the corpus you already have.

**Why it is tempting.** The documents are right there, and an LLM will generate 200 questions in a minute.

**What it costs.** You test the documentation. The suite passes indefinitely while production fails on the questions users actually ask.

**The fix.** Source from production logs, especially failures. Run the golden-set representativeness test quarterly. And verify every synthetic case by hand before it enters the set.

---

## 15. Tuning the prompt until the eval passes

**The mistake.** Iterating on the prompt against the same dataset until it goes green.

**Why it is tempting.** It is the obvious workflow, and it produces a satisfying number.

**What it costs.** The eval stops measuring quality and starts measuring how hard you tuned. You are marking your own homework.

**The fix.** Keep a held-out set you never look at during development. Open it at release. Treat a gap between the two sets as evidence of overfitting.

---

## 16. Using an unvalidated LLM judge

**The mistake.** Writing a rubric, running it, reporting the score.

**Why it is tempting.** The tool makes it a one-liner, and the number looks authoritative.

**What it costs.** The number is an opinion generator's output. When someone asks "according to whom?", you have no answer — and if the judge is the same model family as the system under test, you have been flattering your own product.

**The fix.** Hand-label 30–50 cases, compute Cohen's kappa, read every disagreement, fix the rubric, and publish the kappa next to every score. Use a different model family as judge.

---

## 17. Editing a test case to make it pass

**The mistake.** Softening the expected behaviour when a case fails under deadline pressure.

**Why it is tempting.** It is the fastest route to green, and GenAI's fuzziness makes it feel defensible.

**What it costs.** You deleted the bug rather than fixing it, and the same failure returns to production.

**The fix.** Make it a written team rule *before* the pressure arrives: baselines and expected behaviour change only in a separate, reviewed PR that states why. Never in the same commit as the change that moved them.

---

## 18. Running everything through the LLM judge

**The mistake.** Every check is a judge call, because judges can evaluate anything.

**Why it is tempting.** One mechanism handles all cases.

**What it costs.** A suite that is slow, expensive, and noisy — and gets cancelled when the bill arrives.

**The fix.** Push every check as far down the pyramid as it will go: deterministic → embedding → judge → human. If a requirement can be a regex or a schema, never spend a judge call on it.

---

## 19. Treating the whole system as non-deterministic

**The mistake.** The opposite over-correction: "it's all probabilistic, we can only measure trends."

**Why it is tempting.** It follows logically from mistake #1's lesson.

**What it costs.** Nine of the twelve layers in the request lifecycle are perfectly deterministic — auth, validation, context assembly, streaming, parsing, permissions, cost accounting — and that is where most production incidents actually originate. Abandoning them leaves the biggest gap unguarded.

**The fix.** Test the deterministic layers with the skills you already have, on every PR, for free. Reserve probabilistic methods for the model layer alone.

---

## 20. Not testing over-refusal

**The mistake.** Measuring only whether harmful content gets through.

**Why it is tempting.** Safety failures are the visible risk. Nobody files a bug saying "it refused too much."

**What it costs.** A product that blocks legitimate users. A medical product that will not define "dosage"; a security product that will not discuss vulnerabilities; a filter that blocks ordinary words in another language. It is a revenue problem that nobody measures.

**The fix.** Build the ALLOWED corpus. Report guardrail precision alongside recall. Report the over-refusal rate as a first-class number.

---

## The meta-mistake

**Learning tools instead of method.**

Every tool in this book will be renamed, superseded, or deprecated. Two already were while it was being written. What survives is the method: build a representative dataset, choose a metric that measures the thing that matters, validate that the metric is trustworthy, set a threshold you can defend, run it enough times to see the distribution, and report the result honestly — including what you did not test.

Anyone can wire up promptfoo. Very few people can explain why their threshold is 0.85.
