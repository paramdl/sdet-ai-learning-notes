# PART 28 — Interview Preparation

> **Goal of this part:** answer the questions you will be asked, and understand *why* the answer is right — so you can handle the follow-up rather than reciting.

**The meta-point:** most candidates for GenAI QA roles talk about tools. The ones who get hired talk about **method** — how they decided what to measure, how they validated the measurement, and what they did when the numbers were ambiguous. Every answer below is written to demonstrate method.

---

## Beginner

**Q1. What is the difference between traditional testing and GenAI testing?**

> Traditional testing asserts that output equals an expected value. Generative systems produce different output for the same input, so equality assertions do not work. Instead you assert on *properties* — schema validity, forbidden terms, semantic similarity, groundedness — and you measure them across a dataset with repeated runs, producing a score compared to a threshold rather than a pass/fail on one case.
>
> The part people miss: most of an AI application is still deterministic. Auth, rate limits, streaming, parsing, permissions, cost accounting — all of that is ordinary testing, and it is where most production incidents actually come from.

**Why this is right:** it states the core shift *and* corrects the common over-correction. Interviewers notice when a candidate does not treat GenAI as entirely magic.

---

**Q2. What is a token and why does it matter to a tester?**

> A token is a chunk of text from the model's vocabulary — roughly four characters in English. Every limit, price, and truncation is counted in tokens.
>
> It matters practically because token efficiency varies enormously by language. The same paragraph in Tamil or Hindi can use two to four times the tokens of English. So a per-message character limit tuned for English silently truncates non-Latin-script users. That is a high-severity, reproducible bug that almost nobody tests.

**Why:** it moves immediately from definition to a concrete, testable consequence with a real user impact.

---

**Q3. Does `temperature=0` make the output deterministic?**

> No. It makes sampling greedy, but floating-point non-associativity in parallel GPU execution, batching, and provider-side infrastructure changes still produce variation. I measure it at the start of every project — 20 identical requests, record the number of unique outputs and the mean pairwise similarity — and publish that number. It ends the argument permanently and gives me the threshold for every semantic assertion I write afterwards.

**Why:** correct fact, plus a repeatable method, plus a reason the method is useful.

---

**Q4. What is RAG and why is it used?**

> Retrieval-Augmented Generation: search a corpus at query time and put the relevant passages into the prompt, so the model answers from those rather than from training data. It solves stale knowledge, private data, and unverifiable claims — because you can cite sources.
>
> For testing, the important consequence is that RAG has two independent failure modes. When an answer is wrong, my first question is always: was the correct information in the retrieved context? If no, it is a retrieval bug and the generator never had a chance. If yes, it is a generation bug. Roughly three-quarters of the time it is retrieval, and teams almost always blame the model first.

---

**Q5. What is prompt injection?**

> Input the model interprets as an instruction rather than as data. It works because instructions and data share one token stream — the model has no structural guarantee about which part is trusted, so it is architectural rather than a bug you can patch.
>
> Direct injection comes from the user. Indirect injection comes from content the model retrieves — a document, a web page, a tool result — and it is more dangerous because the victim is a *different* user, and it scales. The mitigation is containment: limit what the model can *do*, since you cannot fully stop it being persuaded.

---

## Intermediate

**Q6. How do you test something with no single correct answer?**

> Three layers. First, deterministic constraints that must hold every time — valid JSON, under three sentences, no forbidden terms, no canary leakage. Those are free and I assert them at 100%. Second, semantic similarity against reference answers, with a threshold I calibrate on labelled good and bad pairs rather than guessing. Third, an LLM judge with a rubric, for the genuinely subjective parts.
>
> Then I run each case several times and assert on a pass-rate, not a single result, and I report the minimum as well as the mean — because users experience one sample at a time, and a mean of 0.88 with a minimum of 0.2 has a failure someone will hit.

---

**Q7. What is LLM-as-a-judge, and how do you know you can trust it?**

> Using a model to score another model's output against a rubric. You trust it by validating it: I hand-label 30–50 outputs myself before seeing the judge's answers, run the judge on the same cases, and compute Cohen's kappa — agreement corrected for chance. Below about 0.6 I do not gate releases on it. Then I read every disagreement, because the problem is almost always an ambiguous rubric rather than a bad judge.
>
> I publish that kappa next to every score the judge produces. When I say quality is 87%, the honest follow-up is "according to whom?", and the kappa is the answer.
>
> The biases I control for are position bias — so pairwise comparisons run twice with the order swapped — verbosity bias, and self-preference, which is why the judge is always a different model family from the system under test.

**Why this answer works:** almost nobody validates their judge. Saying you do, with the specific statistic, immediately separates you.

---

**Q8. Retrieval metrics: what are they and which matters most?**

> Precision@K is how much of what came back is relevant — it measures noise. Recall@K is how much of what is relevant came back — it measures completeness. MRR is how high the first relevant result ranked. NDCG@K handles graded relevance and discounts lower positions.
>
> Recall matters most in RAG, because a document that was not retrieved cannot possibly be used — nothing downstream can fix it. And the combination is diagnostic: high precision with low recall means chunking or K is wrong; low precision with high recall means you need a reranker; both low means something fundamental, like the query and documents being embedded with different models.

---

**Q9. A stakeholder says "the AI is inconsistent." What do you do?**

> First I measure it: same input, twenty runs, cluster the outputs semantically. If there is one dominant behavioural cluster with wording variation, that is normal sampling variance and I show them the number. If there are two or more distinct behavioural clusters, the prompt is ambiguous — the model is being asked something that can reasonably be read two ways.
>
> That reframing matters because "the AI is inconsistent" is unactionable, while "this instruction admits two readings, and here are the two behaviours it produces" is a prompt fix someone can make this afternoon.

---

**Q10. How do you test a guardrail?**

> As a classifier, with four corpora. Allowed content that must pass — that gives me the false-positive rate. Blocked content that must be stopped — false negatives. Borderline content, where I check for consistency rather than a specific verdict. And adversarial content: blocked material disguised with encoding, another language, or fragmentation.
>
> I report precision and recall, not accuracy. A team reporting only recall is hiding an over-refusal problem, and over-refusal is a revenue problem — a medical product that refuses to define "dosage" is broken. Building the allowed corpus is the part people skip, and it is where the business value is.
>
> The highest-yield single test is language parity: the same policy-violating request in every supported language. Filters are very often tuned on English only.

---

**Q11. How do you decide which model to use?**

> Public benchmarks shortlist; they do not decide. They suffer from contamination, they measure tasks unlike mine, and aggregate scores hide category-level collapse.
>
> I run my own golden set against each candidate with identical prompts and parameters, and report per category — because two models can be equivalent overall while one fails multilingual and the other fails policy. Then I add cost per *resolved task* rather than cost per request, p95 TTFT, and red-team pass rate. That produces a table the product owner can decide from. Frequently the mid-tier model wins on cost-per-outcome, and that decision belongs to them, not to me.

---

**Q12. What is the most common mistake teams make with AI evaluation?**

> Two, and they compound. First, building the golden dataset from documentation instead of from real user queries — so it tests the docs and passes forever while production fails. Second, tuning the prompt until the eval passes, which turns the eval into a measure of how hard you tuned. I keep a held-out set that I never look at during development, and I treat a gap between the two sets as evidence of overfitting to my own tests.

---

## Advanced

**Q13. Design a test strategy for a customer-facing RAG chatbot from scratch.**

> I would start by drawing the request path and testing layer by layer, because nine of the twelve layers are deterministic and that is where most incidents come from.
>
> Week one, before any evaluation: intercept a real request to see the actual assembled prompt, model, and parameters — that alone usually produces findings. Check test/production config parity. Measure the determinism baseline. Assert `finish_reason` everywhere. Test whether the client can supply assistant turns. Run a sixty-turn conversation and check the guardrails still hold, because history truncation can evict the system prompt. Test token parity across languages. Fault-inject 429 and 500. Check whether streaming bypasses the output filter. Reconcile app-reported cost against provider usage.
>
> Then evaluation: build a fifty-query golden set from production logs, weighted toward unanswerable and adjacent-but-wrong questions, with labelled relevant chunks. Measure retrieval separately from generation so failures localise. Faithfulness with claim decomposition, and citation validation — existence first, because that is deterministic and free.
>
> Then security: indirect injection through every write path into the corpus, hidden-context extraction with canaries, tenant isolation, and output handling including markdown image exfiltration.
>
> In CI: deterministic checks and a forty-case smoke on every PR under fifteen minutes, full evaluation and security nightly with a budget cap, anchor set weekly to catch provider-side model drift.

**Why this works:** it is ordered by value, it leads with the cheap deterministic work, and it names specific tests rather than categories.

---

**Q14. How do you test an AI agent, and what is different about it?**

> The difference is that agents *act*, so a wrong answer becomes a deleted record or a sent email. That means outcome testing is insufficient — an agent that reaches the right result by calling a destructive tool has "passed". I assert on the trajectory: which tools, in what order, within a step cap, with a forbidden list.
>
> The most productive technique is fault injection. Wrap each tool so it can return an error, a timeout, an empty result, malformed data, or hostile text, and assert four things: it terminates, it does not claim success it did not achieve, it does not loop, and hostile tool output does not redirect it. That last one is indirect injection through the tool boundary, and it is a critical finding.
>
> On permissions, the key point is *where* enforcement lives. A model attempting a forbidden tool call is normal — models are persuadable. The bug exists only if the runtime executes it. Testing the model's refusal is testing the wrong layer, and it is the most common mistake in agent security testing.
>
> And retries: standard HTTP retry logic applied to a non-idempotent tool is how you double-book a customer. I check for an idempotency key on every side-effecting call.

---

**Q15. Your eval suite passes but users complain. What is happening?**

> Most likely the dataset no longer represents reality. I test that directly: embed the golden set and a sample of last month's production queries, and check what fraction of production queries have a close neighbour in the golden set. Below about 80%, the suite is measuring a product that no longer exists.
>
> Other candidates: the suite runs at different parameters than production; I am only measuring the mean and users are hitting the tail, so I check the minimum and p10; quality degrades under load through a silent fallback that my idle-state tests never see; or the provider changed the model behind an alias, which is what the weekly anchor set exists to catch.

---

**Q16. How do you handle flaky tests in a probabilistic system?**

> First, separate hard from soft. Hard constraints — schema, canary leakage, permission enforcement — must be 100% and genuinely block. Soft quality uses a delta gate against a baseline rather than an absolute threshold, because "must not drop more than three points" is unarguable while "must score 0.90" is a negotiation.
>
> When a gate fails, I confirm before failing the build: re-run the case at N=5 and compare the rate against the baseline's confidence interval. If the intervals overlap, I cannot claim a regression from that evidence, and saying so honestly is important — a suite that cries wolf gets ignored, and then it protects nothing.
>
> Newly flaky cases go into a quarantine suite that reports but does not block, with an expiry date so quarantine does not become a graveyard. And baselines are never auto-updated; updating one is a separate reviewed PR, because otherwise the easiest way to go green is to move the goalposts.

---

**Q17. How do you test for bias without producing a contestable opinion?**

> Counterfactual pairs. Identical prompts differing in exactly one attribute — a name, a pronoun, a stated location. Generate N outputs per variant, score them on a neutral rubric, and compare distributions. The finding becomes a measured difference in scores with a sample size, not a reading of one output.
>
> I state the limitation explicitly: it shows the system produces measurably different outcomes for these variants; it does not establish the mechanism and does not generalise beyond the variants tested. That sentence is what makes it a credible finding rather than an accusation.
>
> The most under-measured version is refusal-rate parity across languages. If the same benign request is refused three percent of the time in English and nineteen percent in Tamil, that is arithmetic, and it is a defect.

---

**Q18. What is denial of wallet and how do you report it?**

> Resource exhaustion where the resource is money. Long-input flooding, output amplification, agent loops, forcing the expensive model, reasoning-token abuse, or one user exhausting a shared key's quota and denying service to everyone.
>
> I report it as a rate of spend: "one free-tier account can sustain fourteen dollars an hour within the documented usage rules." Expressing it as a business number rather than a vulnerability class is what gets it prioritised. It maps to OWASP LLM06, which rose four places in the 2026 list precisely because this became common.

---

## Scenario questions

**Q19. A model upgrade is required because the provider is deprecating yours in six weeks. Walk me through it.**

> I would run the upgrade suite well before the deadline, not during the cut-over. Full golden set on both models, compared per category, with the list of newly-failing cases by name. Then the two suites teams skip: the full security suite, because alignment differs between versions and an injection that failed before may now succeed; and the guardrail corpora, because refusal behaviour is the characteristic that changes most between versions — in both directions, so I check over-refusal too.
>
> Then structured output reliability, tool-calling argument formats, cost, latency, the determinism baseline, and parameter support, since newer models sometimes restrict sampling parameters. If the judge model also changed, I revalidate the judge.
>
> The output is an upgrade report with a recommendation and a rollback plan. And I would put every provider deprecation date in the team calendar, because this is a scheduled risk, not a surprise.

---

**Q20. Users report the chatbot ignored its safety rules on turn forty of a long conversation. First hypothesis?**

> System prompt eviction. If the application trims conversation history from the top to fit the context window, and the system prompt sits at the top, the guardrails leave the context partway through a long conversation.
>
> I would test it directly: hash the system prompt at deploy time and assert that hash is present in the assembled payload at turn one and turn sixty, then run a sixty-turn conversation of filler and re-ask the policy question at the end. It is a critical security finding, it lives at the context-assembly layer rather than in the model, and it is completely deterministic to reproduce.

---

**Q21. Your RAG assistant confidently answered a question about a policy that does not exist. Diagnose it.**

> First question: what was in the retrieved context? If retrieval returned nothing or returned only low-similarity chunks, then the system fell back to the model's parametric knowledge and presented it as if it came from company documents. That is the single most dangerous RAG failure mode, because the answer is indistinguishable from a grounded one.
>
> The tests are the zero-retrieval path and the low-similarity path — separately, because the second is worse: the model receives irrelevant text and tries to use it. And I would check whether the golden set contains unanswerable questions at all, because if it does not, this failure mode was never being tested.

---

## Coding questions

**Q22. Write a function that asserts an LLM response is semantically similar to a reference.**

```python
def assert_semantically_similar(output: str, reference: str,
                                threshold: float = 0.85, embed=None):
    """Threshold must be CALIBRATED on labelled good/bad pairs, not guessed.
    The error message includes both texts because reproducing a
    non-deterministic failure later may be impossible."""
    a, b = np.array(embed(output)), np.array(embed(reference))
    score = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    assert score >= threshold, (
        f"Semantic similarity {score:.3f} < {threshold}\n"
        f"REFERENCE: {reference}\nOUTPUT:    {output}"
    )
```
**Say out loud while writing it:** the threshold is calibrated, not guessed; and cosine similarity handles negation poorly, so for anything where correctness inverts I add an explicit polarity check.

---

**Q23. Write a test that asserts a pass-rate rather than a single result.**

```python
def test_constraint_pass_rate(llm, n=10, min_rate=0.9):
    """Single-run assertions on a probabilistic system are the classic
    mistake: they are flaky when the system is fine, and they miss a
    5% failure rate entirely."""
    results = [satisfies_constraints(llm.ask(PROMPT)) for _ in range(n)]
    rate = sum(results) / n
    assert rate >= min_rate, (
        f"Pass rate {rate:.0%} over {n} runs (minimum {min_rate:.0%}). "
        f"Failing runs: {[i for i, r in enumerate(results) if not r]}"
    )
```

---

**Q24. Write a prompt injection test.**

See Part 27 §27.10. **The points to make aloud:** use a canary so the assertion is an exact string match rather than a judgement; sweep payload families against obfuscation transforms; run each variant several times and report the *rate*, because a 20% success rate is a real vulnerability that a single run misses four times in five.

---

## Questions to ask them

Asking these signals seniority, and the answers tell you whether the role is real:

1. Where do prompts live, and are they version-controlled?
2. Do you have a golden evaluation dataset? Where did it come from?
3. Do you have tracing? Can you retrieve the exact prompt that produced a given production response?
4. Has anyone validated your LLM judge against human labels?
5. What happens when the provider deprecates your model?
6. Who can write into the RAG corpus?
7. Is there a cost gate in CI?
8. Has the fallback model's quality ever been measured?
9. What is the team's process when an eval regresses — who decides to ship anyway?

Question 3 is the one that reveals the team's real maturity in a single answer.

---

**Next:** [PART-29-CERTIFICATIONS.md](PART-29-CERTIFICATIONS.md)
