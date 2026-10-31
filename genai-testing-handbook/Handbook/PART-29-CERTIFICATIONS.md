# PART 29 — Certifications

> **Goal of this part:** an honest assessment. Most certifications in this space are worth less than a public repository containing a working eval suite. A few are genuinely useful, usually because an employer or a client asks for them by name.

⏳ Verified 8 September 2026. Certification schemes change; check the awarding body's current syllabus and prerequisites before paying.

---

## 29.1 The honest framing

**What actually gets you hired in GenAI QA, in order:**
1. A public repository with a real eval suite, a validated judge, and a README explaining the *decisions*
2. Demonstrated security findings you can talk through (from authorised testing)
3. Ability to answer Part 28's questions with method rather than tool names
4. Relevant experience, even adjacent
5. Certifications

Certifications move you *past a filter*; they do not win the interview. Buy them when a filter exists — enterprise procurement, consultancy panels, some regulated industries, and visa/immigration points systems — not to learn.

---

## 29.2 Highly valuable

### ISTQB® Certified Tester AI Testing (CT-AI) ⏳
| | |
|---|---|
| **What** | Testing AI-based systems: ML systems and generative AI, including probabilistic behaviour, non-determinism, and data dependence |
| **Version** | ⏳ Syllabus v2.0 released, with a stronger practical focus and explicit generative-AI coverage; v1.0 is retiring |
| **Prerequisite** | ISTQB Foundation Level (CTFL) |
| **Why it is worth it** | The only widely-recognised *testing-specific* AI certification. Enterprise QA managers know the ISTQB brand, and it appears in job descriptions and tender requirements |
| **Limitation** | Broader than GenAI — significant ML/data coverage. It will not teach you to run an eval suite |
| **Verdict** | **Worth it** if you work in or want enterprise/regulated QA. The v2.0 update makes it substantially more relevant than v1.0 was |

### ISTQB® Certified Tester — Testing with Generative AI (CT-GenAI) ⏳
| | |
|---|---|
| **What** | Using LLMs to *support testing* — prompt engineering for test work, risk management, AI-assisted test infrastructure |
| **Note** | This is the mirror image of CT-AI. CT-AI is *testing AI*; CT-GenAI is *testing with AI* |
| **Verdict** | **Worth it as a complement**, not a substitute. Do not confuse the two — a hiring manager who wants an AI Quality Engineer wants CT-AI |

**Take CT-AI first.** If you only take one, take CT-AI.

---

## 29.3 Useful

### A cloud AI certification for the cloud your employer uses
Azure, AWS, and Google each offer AI/ML-focused certifications at fundamentals and associate level.

| | |
|---|---|
| **Why useful** | Cloud platform knowledge is a real gap for most testers, and these force you through the console and the services |
| **Which** | Only the one matching your employer's stack. Learning all three is waste |
| **Level** | Fundamentals is enough for a tester; associate-level engineer certifications are for builders |
| **Verdict** | **Useful**, especially if your CV has no cloud on it at all |

### A security certification, if you specialise in AI red teaming
Foundational security certifications (or their AI-specific successors) help if you want to be hired specifically for AI security work, because security teams screen for them.

| | |
|---|---|
| **Caveat** | ⏳ AI-security-specific certifications are new and their market recognition is unproven. A demonstrated red-team report is currently worth more |
| **Verdict** | **Useful** for a security-specialist path; skip for a general AI QA path |

### ISTQB Foundation Level (CTFL)
Only relevant as a **prerequisite for CT-AI**. If you already have years of QA experience, it teaches you nothing — but you may need it to sit CT-AI.

---

## 29.4 Optional

| Certification | Note |
|---|---|
| **Vendor prompt-engineering certificates** | Free or cheap, a few hours, minor CV value. Do them for the learning if you have gaps; do not expect them to move a hiring decision |
| **Deep learning / ML specialisations (Coursera etc.)** | Genuinely educational, but they teach you to *build* models. Time-expensive for the return in a QA role. Do the first course or two for concepts if §Part 1 left you wanting more; do not complete the full track |
| **Kubernetes (CKA/CKAD)** | Far more than a tester needs (Part 21). Only if you are moving toward platform work |
| **Cloud architect certifications** | Wrong role |

---

## 29.5 Not worth prioritising

| Certification | Why |
|---|---|
| Bootcamp "AI Tester" certificates from unrecognised providers | No employer recognition; the market is full of these |
| Tool-vendor certifications for eval tools | The tools change faster than the certificate stays valid |
| "Prompt engineer" certifications from content mills | Actively negative signal in a technical interview |
| Anything promising a job guarantee | — |
| Multiple cloud certifications | Diminishing returns; depth in one beats breadth in three |

---

## 29.6 The better investment

For the cost of two certifications and the time they take, you could instead produce:

| Artefact | Signal it sends |
|---|---|
| A public repo with Projects 3, 4, and 6 from Part 25 | You can actually do the work |
| A written case study of your judge validation, with the kappa | You understand evaluation, not just tooling |
| A red-team report (on your own system) in the Part 12 format | You can produce a professional security deliverable |
| A conference talk or a detailed blog post on one specific finding | Communication, plus discoverability |
| A contribution to an open-source eval tool | Verifiable, credible, and it gets you known |

**The strongest single artefact** is a repository with a README that explains *why* you chose each metric and threshold. Anyone can wire up promptfoo. Very few people can explain why their threshold is 0.85.

---

## 29.7 Recommended sequence

If you want certifications, this order:

1. **CTFL** — only if you need it as a prerequisite and do not already hold it
2. **CT-AI (v2.0)** — the one that matters
3. **A cloud AI fundamentals certification** — for whichever cloud your employer uses
4. **CT-GenAI** — as a complement, once the above are done
5. Anything security-specific — only if you are going down the red-team path

Total: two certifications for most people. Spend the remaining time on Part 25.

---

**Next:** [PART-30-CAREER-ROADMAP.md](PART-30-CAREER-ROADMAP.md)
