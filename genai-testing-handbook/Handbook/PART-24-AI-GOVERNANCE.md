# PART 24 — AI Governance & Responsible AI

> **Goal of this part:** understand the frameworks well enough to speak the language, and — more importantly — know which parts of them a QA engineer actually delivers. Governance frameworks are mostly written for executives. Your value is translating their abstractions into **tests that produce evidence**.

⏳ Regulatory dates and framework versions in this part were verified on 8 September 2026. Legal timelines shift; verify before relying on any date.

---

## 24.1 The core principles, and the test for each

This is the translation table that makes governance concrete. Most of it is work you are already doing.

| Principle | Plain meaning | **Your test** |
|---|---|---|
| **Fairness** | Does not disadvantage groups | Counterfactual pairs; per-group precision/recall; WER by accent; refusal-rate parity by language (Part 13) |
| **Transparency** | Users know they are talking to AI | Assert AI disclosure is present and not dismissible in a way that persists |
| **Explainability** | Decisions can be accounted for | Citations verified; traces complete (Parts 7, 15) |
| **Accountability** | Someone is responsible | Audit trail: who deployed which prompt/model when |
| **Human oversight** | A human can intervene | Confirmation gates tested and un-bypassable (Part 9 §9.6) |
| **Privacy** | Data is protected | PII redaction in logs, traces, and outputs; retention enforced (Parts 11, 15) |
| **Security** | Resistant to misuse | The whole of Parts 11 and 12 |
| **Robustness** | Behaves under stress and edge cases | Parts 14, 13 |
| **Safety** | Does not cause harm | Guardrail corpora, red team |
| **Contestability** | Users can challenge a decision | A feedback and escalation path exists and works |

**Read that column again.** With one exception, you already know how to do all of it. Governance is not a new discipline for you to learn — it is a *vocabulary* for the work in Parts 11–19, plus documentation. That reframing is worth stating in interviews, and it is genuinely true.

---

## 24.2 NIST AI Risk Management Framework 🟠

A voluntary US framework, widely adopted as a structuring device. Four functions:

| Function | Meaning | Your contribution |
|---|---|---|
| **GOVERN** | Culture, policies, roles, accountability | Define what "tested" means for AI features; own the release-gate criteria |
| **MAP** | Understand context, purpose, and risk | Risk-based test planning: what is the harm if this feature is wrong? |
| **MEASURE** | Analyse, assess, benchmark, monitor | **This is your function.** Evals, metrics, red teaming, monitoring |
| **MANAGE** | Prioritise, respond, recover | Findings triage, severity, rollback drills |

There is also a **Generative AI Profile** that maps GenAI-specific risks onto the core framework. Worth skimming once — it is the clearest official statement of what "GenAI risk" means, and it maps closely to the OWASP list you already know.

**Why learn it:** enterprise and regulated clients ask about it by name. Being able to say *"our test suite covers MEASURE; here is the evidence artefact for each risk we mapped"* positions you well above a tester who only talks about test cases.

---

## 24.3 ISO/IEC standards 🟠

| Standard | What it is | Relevance to you |
|---|---|---|
| **ISO/IEC 42001** | AI Management System — the certifiable one. Requires documented processes for AI risk, lifecycle, and continuous improvement | If your employer certifies, **your test evidence becomes audit evidence**. Design your reporting to be auditable |
| **ISO/IEC 23894** | AI risk management guidance | Complements 42001 |
| **ISO/IEC 22989** | AI terminology | Useful when a contract uses precise terms |
| ISO/IEC 25000 (SQuaRE) | Software quality models | Traditional quality attributes still apply |

**The practical implication of 42001:** an auditor will ask *"how do you know this system meets its stated quality criteria?"* The answer is your eval suite, its baselines, its version history, and its results. **Retention, versioning, and traceability of test artefacts stop being hygiene and become compliance requirements.** Design for that early — retrofitting audit trails onto a year of ad-hoc test runs is painful.

---

## 24.4 EU AI Act ⏳

The most consequential AI regulation, applying to anyone placing AI systems on the EU market regardless of where they are based.

### Risk tiers
| Tier | Examples | Obligations |
|---|---|---|
| **Unacceptable** | Social scoring, certain biometric categorisation, manipulative techniques | Prohibited |
| **High-risk** | Employment screening, credit scoring, education access, critical infrastructure, certain law-enforcement uses | Heaviest: risk management, data governance, technical documentation, logging, human oversight, accuracy/robustness/cybersecurity, conformity assessment |
| **Limited risk** | Chatbots, emotion recognition, deepfakes | Transparency: users must be told they are interacting with AI; AI-generated content must be disclosed |
| **Minimal risk** | Spam filters, most productivity tools | No specific obligations |

### Timeline as of September 2026 ⏳
| Date | Status |
|---|---|
| 2 Feb 2025 | Prohibited practices and AI-literacy obligations applied |
| 2 Aug 2025 | GPAI (general-purpose AI) model obligations applied |
| **2 Aug 2026** | **Transparency obligations (Art. 50) applied; the AI Office's enforcement powers over GPAI providers became exercisable** |
| **2 Dec 2027** | High-risk obligations for standalone Annex III systems — **deferred** from the original August 2026 date |
| 2 Aug 2028 | High-risk AI embedded in already-regulated products |

⏳ The deferral came via the Digital Omnibus (Regulation (EU) 2026/1744, in force 27 July 2026). This is exactly the kind of fact that changes — verify before quoting it in a document that matters.

### What this means for you *today*

**Transparency obligations are live now.** If your product serves EU users:

```
TC-GOV-001  AI disclosure
Expected:   Users are informed they are interacting with an AI system,
            clearly, before or at the start of interaction. Verify it is
            present on every entry point — including deep links, embedded
            widgets, mobile, and API-driven integrations.
Priority:   High (compliance)
```

```
TC-GOV-002  AI-generated content disclosure
Expected:   AI-generated or manipulated image, audio, video, and text
            content is marked as such, in a machine-readable form where
            required. Verify provenance metadata survives the pipeline
            (compression, resizing, format conversion, CDN).
Priority:   High (compliance)
Note:       Metadata stripping during image processing is a real and
            easily-missed defect
```

**If your system is or may become high-risk**, the obligations that translate directly into test work are: logging and traceability (Part 15), accuracy and robustness (Parts 6, 14), human oversight (Part 9 §9.6), data governance (Part 17), and cybersecurity (Part 11). You have a two-year runway; teams that start their evidence trail now will not be scrambling in 2027.

---

## 24.5 Other regimes worth knowing by name

| Regime | Relevance |
|---|---|
| **GDPR / DPDP Act (India)** | Applies to personal data in prompts, outputs, logs, and traces. Right to erasure includes trace stores (Part 15 §15.8) |
| Sector regulation | Finance, health, and legal each have their own AI expectations layered on top |
| US state AI laws | Fragmented and evolving; check per jurisdiction |
| Model provider terms | Usage policies are contractual obligations you can test compliance against |

**The DPDP Act point is directly relevant to your context**, given India-based work: personal data flowing into a third-party LLM provider or tracing SaaS raises consent, purpose-limitation, and cross-border questions. "We send every user prompt to a US-based tracing vendor" is a finding worth raising even when nobody asked you to look.

---

## 24.6 The governance evidence pack

What a QA engineer can produce, and what makes you valuable in a regulated organisation:

```
AI QUALITY EVIDENCE PACK — Acme Assistant v4.2

1. SYSTEM DESCRIPTION      purpose, users, model(s), data sources,
                           tools, decision autonomy
2. RISK ASSESSMENT         identified harms, likelihood, severity,
                           mitigations, residual risk
3. TEST STRATEGY           what is tested, how, at what frequency,
                           what is explicitly NOT tested
4. EVALUATION RESULTS      dataset version, metrics, thresholds, scores,
                           judge validation (kappa), per-category detail
5. SECURITY ASSESSMENT     red-team scope, objectives, findings by
                           severity, controls that held, retest results
6. FAIRNESS ASSESSMENT     method, groups tested, results, limitations
7. ROBUSTNESS              performance under load, degradation ladder,
                           failure-mode behaviour
8. HUMAN OVERSIGHT         where confirmation is required, evidence it
                           cannot be bypassed
9. MONITORING PLAN         production metrics, alerts, online eval,
                           drift detection
10. KNOWN LIMITATIONS      what the system cannot do; where it fails;
                           what was out of test scope
11. CHANGE LOG             model, prompt, corpus, and dataset versions
                           with dates and approvers
```

**Section 10 is the one that distinguishes a professional.** Every AI system has failure modes. Documenting them honestly — *"the assistant is unreliable on multi-hop questions spanning more than two documents; measured 61% accuracy on that category"* — is more valuable than a report claiming everything passed, and it is what an auditor, a regulator, and a serious customer all actually want to see.

---

## 24.7 What NOT to spend time on ⚪

- Reading regulations end to end — read the summaries and the obligations that map to tests
- Becoming a compliance officer — know the vocabulary, own the evidence
- Legal interpretation — flag questions to legal; do not answer them
- Certification schemes for their own sake — unless your employer is certifying

**Your lane:** produce the evidence, name the limitations, and make the test artefacts auditable. That is a well-defined, high-value contribution that most testers cannot make.

---

## 24.8 Self-check

1. Which NIST AI RMF function is yours, and what do you contribute to the other three?
2. Why does ISO/IEC 42001 change how you retain test artefacts?
3. Which EU AI Act obligations are in force today, and which are deferred?
4. What is the AI-generated content disclosure test, and what commonly breaks it?
5. Why is section 10 of the evidence pack the most professionally valuable?
6. Why is sending prompts to a third-party tracing service a governance question?

---

**Next:** [PART-25-PROJECTS.md](PART-25-PROJECTS.md) — eight progressive projects that turn all of this into a portfolio.
