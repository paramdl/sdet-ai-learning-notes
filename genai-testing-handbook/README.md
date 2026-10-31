# GenAI Learning & Testing

Personal learning track: understand GenAI well enough to test it professionally.

## PDF

**[GenAI-Testing-Handbook.pdf](GenAI-Testing-Handbook.pdf)** — the whole handbook as one 299-page document: title page, linked contents with page numbers, PDF bookmarks, page numbering. 2.4 MB.

Rebuild after editing any chapter:

```powershell
python build_pdf.py
```

## Start here
**[Handbook/WHAT-TO-DO-TOMORROW.md](Handbook/WHAT-TO-DO-TOMORROW.md)** — one page, one task, 90 minutes.

## The Handbook

A complete self-study textbook, career roadmap, and practical testing reference: **31 parts + 3 appendices + 6 front-matter guides**, ~96,000 words across 40 chapters.

| | |
|---|---|
| [Handbook/WHY-LEARN-THIS.md](Handbook/WHY-LEARN-THIS.md) | **What to learn and why** — every topic, its reason, and what breaks if you skip it |
| [Handbook/00-README-AND-TOC.md](Handbook/00-README-AND-TOC.md) | Title page and full table of contents |
| [Handbook/LEARNING-ORDER.md](Handbook/LEARNING-ORDER.md) | Levels 0–14 with prerequisites and interview questions |
| [Handbook/STUDY-PLANS.md](Handbook/STUDY-PLANS.md) | 30 / 60 / 90-day, 6-month, 12-month daily plans |
| [Handbook/SKILL-MATRIX.md](Handbook/SKILL-MATRIX.md) | Beginner → Expert across 16 skills, with scoring |
| [Handbook/COMMON-MISTAKES.md](Handbook/COMMON-MISTAKES.md) | The 20 traps traditional QA engineers fall into |
| [Handbook/PART-31-CHEAT-SHEETS.md](Handbook/PART-31-CHEAT-SHEETS.md) | 17 printable references |
| [Handbook/APPENDIX-B-TOOL-INDEX.md](Handbook/APPENDIX-B-TOOL-INDEX.md) | Every tool, with deprecation status |

## Quick-reference files (pre-handbook)

| File | What it is |
|---|---|
| [CONCEPTS.md](CONCEPTS.md) | The 7-layer concept checklist |
| [TOOLS.md](TOOLS.md) | Tools ranked: learn / try once / recognise |
| [ROADMAP.md](ROADMAP.md) | The original 8-week plan |
| [SETUP.md](SETUP.md) | Install steps verified against this machine |
| `labs/verify_setup.py` | Tells you what is still missing |
| `labs/promptfoo/`, `labs/deepeval/` | Starter suites, runnable against local Ollama |

## Setup

```powershell
cd <project-dir>
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install openai numpy pytest httpx respx pydantic python-dotenv tiktoken ragas
python labs\verify_setup.py
```

Plus Ollama from ollama.com, then `ollama pull llama3.1:8b` and `ollama pull nomic-embed-text`. That covers every lab in the handbook at zero cost.

## The one paragraph that matters

Traditional testing asserts that output **equals** something. GenAI testing measures whether output **scores above a threshold** on a dataset, run repeatedly, because the same input does not give the same output twice. Everything else — golden datasets, LLM-as-judge, faithfulness, red teaming, tracing, cost gates — follows from that single change.

---

⏳ Volatile facts in the handbook were verified **8 September 2026** and are marked. Primary sources are listed in [Handbook/APPENDIX-C-RESOURCES.md](Handbook/APPENDIX-C-RESOURCES.md). When a primary source disagrees with the handbook, the source wins.
