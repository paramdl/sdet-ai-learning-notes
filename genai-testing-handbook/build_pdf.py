"""Build the GenAI Testing Handbook as a single navigable PDF.

Pipeline:
  1. Concatenate the markdown chapters in reading order
  2. Convert to one styled HTML document (print CSS, A4)
  3. Render with headless Chrome  --print-to-pdf
  4. Locate each chapter's start page by extracting text
  5. Rebuild the TOC with real page numbers, re-render
  6. Stamp page numbers + add PDF bookmarks (outline)

Usage:  python build_pdf.py
"""
from __future__ import annotations

import html
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

ROOT = Path(__file__).parent
HB = ROOT / "Handbook"
OUT = ROOT / "GenAI-Testing-Handbook.pdf"
WORK = Path(tempfile.mkdtemp(prefix="hbpdf_"))

TITLE = "The GenAI Testing Handbook"
SUBTITLE = "A Self-Study Textbook, Career Roadmap and Practical Reference for AI Quality Engineers"
EDITION = "Edition 1.0 — compiled 9 September 2026"

# ---------------------------------------------------------------- chapter order
ORDER = [
    ("WHY-LEARN-THIS.md",              "What to Learn, and Why",            "Front"),
    ("WHAT-TO-DO-TOMORROW.md",         "What To Do First Tomorrow",         "Front"),
    ("LEARNING-ORDER.md",              "Learning Order — Levels 0 to 14",   "Front"),
    ("SKILL-MATRIX.md",                "Skill Matrix",                      "Front"),
    ("STUDY-PLANS.md",                 "Study Plans",                       "Front"),
    ("COMMON-MISTAKES.md",             "Common Mistakes",                   "Front"),

    ("PART-01-GENAI-FOUNDATIONS.md",      "Part 1 — GenAI Foundations",           "Part I · Foundations"),
    ("PART-02-PROGRAMMING.md",            "Part 2 — Programming",                 "Part I · Foundations"),
    ("PART-03-LLM-FUNDAMENTALS.md",       "Part 3 — LLM Fundamentals",            "Part I · Foundations"),
    ("PART-04-PROMPT-ENGINEERING.md",     "Part 4 — Prompt Engineering & Testing", "Part I · Foundations"),

    ("PART-05-LLM-API-TESTING.md",        "Part 5 — LLM API Testing",             "Part II · Core Testing"),
    ("PART-06-LLM-EVALUATION.md",         "Part 6 — LLM Evaluation",              "Part II · Core Testing"),
    ("PART-07-RAG-TESTING.md",            "Part 7 — RAG Testing",                 "Part II · Core Testing"),
    ("PART-08-VECTOR-DB-TESTING.md",      "Part 8 — Vector Database Testing",     "Part II · Core Testing"),
    ("PART-09-AGENT-TESTING.md",          "Part 9 — Agent & Tool-Calling Testing", "Part II · Core Testing"),
    ("PART-10-MULTIMODAL-TESTING.md",     "Part 10 — Multimodal Testing",         "Part II · Core Testing"),

    ("PART-11-AI-SECURITY.md",            "Part 11 — AI Security Testing",        "Part III · Security & Safety"),
    ("PART-12-RED-TEAMING.md",            "Part 12 — AI Red Teaming",             "Part III · Security & Safety"),
    ("PART-13-SAFETY-GUARDRAILS.md",      "Part 13 — Safety, Hallucination, Bias & Guardrails", "Part III · Security & Safety"),

    ("PART-14-PERFORMANCE-RELIABILITY.md", "Part 14 — Performance & Reliability", "Part IV · Operations"),
    ("PART-15-OBSERVABILITY.md",          "Part 15 — Observability",              "Part IV · Operations"),
    ("PART-16-COST-TOKEN-TESTING.md",     "Part 16 — Cost & Token Testing",       "Part IV · Operations"),
    ("PART-17-DATA-DATASET-TESTING.md",   "Part 17 — Data & Dataset Testing",     "Part IV · Operations"),
    ("PART-18-MODEL-TESTING.md",          "Part 18 — Model Testing",              "Part IV · Operations"),
    ("PART-19-REGRESSION-TESTING.md",     "Part 19 — Regression Testing",         "Part IV · Operations"),

    ("PART-20-CICD.md",                   "Part 20 — CI/CD",                      "Part V · Platform & Governance"),
    ("PART-21-DOCKER-KUBERNETES.md",      "Part 21 — Docker & Kubernetes",        "Part V · Platform & Governance"),
    ("PART-22-CLOUD-AI.md",               "Part 22 — Cloud AI Platforms",         "Part V · Platform & Governance"),
    ("PART-23-LLMOPS.md",                 "Part 23 — LLMOps / MLOps",             "Part V · Platform & Governance"),
    ("PART-24-AI-GOVERNANCE.md",          "Part 24 — AI Governance",              "Part V · Platform & Governance"),

    ("PART-25-PROJECTS.md",               "Part 25 — Real-World Projects",        "Part VI · Practice & Career"),
    ("PART-26-TEST-CASE-LIBRARY.md",      "Part 26 — Test Case Library",          "Part VI · Practice & Career"),
    ("PART-27-AUTOMATION-EXAMPLES.md",    "Part 27 — Automation Examples",        "Part VI · Practice & Career"),
    ("PART-28-INTERVIEW-PREP.md",         "Part 28 — Interview Preparation",      "Part VI · Practice & Career"),
    ("PART-29-CERTIFICATIONS.md",         "Part 29 — Certifications",             "Part VI · Practice & Career"),
    ("PART-30-CAREER-ROADMAP.md",         "Part 30 — Career Roadmap",             "Part VI · Practice & Career"),
    ("PART-31-CHEAT-SHEETS.md",           "Part 31 — Cheat Sheets",               "Part VI · Practice & Career"),

    ("APPENDIX-A-GLOSSARY.md",            "Appendix A — Glossary",                "Appendices"),
    ("APPENDIX-B-TOOL-INDEX.md",          "Appendix B — Tool Index",              "Appendices"),
    ("APPENDIX-C-RESOURCES.md",           "Appendix C — Resources",               "Appendices"),
]

# ------------------------------------------------------------------------- CSS
CSS = """
@page { size: A4; margin: 18mm 16mm 20mm 16mm; }

* { box-sizing: border-box; }

body {
  font-family: "Segoe UI", "Calibri", system-ui, sans-serif;
  font-size: 9.6pt; line-height: 1.5; color: #1a1a1a;
  margin: 0; padding: 0;
  -webkit-font-smoothing: antialiased;
}

/* ---------- title page ---------- */
.titlepage {
  height: 252mm; display: flex; flex-direction: column;
  justify-content: center; text-align: center; page-break-after: always;
}
.titlepage h1 { font-size: 30pt; margin: 0 0 6mm; border: none; color: #111; letter-spacing: -0.5pt; }
.titlepage .sub { font-size: 12pt; color: #444; margin-bottom: 14mm; line-height: 1.5; padding: 0 12mm; }
.titlepage .rule { width: 60mm; height: 2px; background: #c8102e; margin: 0 auto 14mm; }
.titlepage .meta { font-size: 9.5pt; color: #666; line-height: 1.9; }
.titlepage .stats { margin-top: 16mm; font-size: 8.6pt; color: #888; }

/* ---------- table of contents ---------- */
.toc { page-break-after: always; }
.toc h1 { font-size: 19pt; border-bottom: 2px solid #c8102e; padding-bottom: 3mm; margin-bottom: 7mm; }
.toc .section { font-weight: 700; font-size: 10.4pt; margin: 6mm 0 2.5mm; color: #c8102e;
                text-transform: uppercase; letter-spacing: 0.6pt; }
.toc .row { display: flex; align-items: baseline; margin: 1.4mm 0; font-size: 9.6pt; }
.toc .row .t { white-space: nowrap; }
.toc .row .dots { flex: 1; border-bottom: 1px dotted #bbb; margin: 0 2mm; position: relative; top: -2px; }
.toc .row .p { color: #555; font-variant-numeric: tabular-nums; }
.toc a { color: #1a1a1a; text-decoration: none; }

/* ---------- chapters ---------- */
.chapter { page-break-before: always; }

h1 {
  font-size: 18pt; color: #111; margin: 0 0 5mm;
  padding-bottom: 2.5mm; border-bottom: 2px solid #c8102e;
  page-break-after: avoid; letter-spacing: -0.3pt;
}
h2 { font-size: 13pt; color: #111; margin: 7mm 0 2.5mm; padding-bottom: 1.2mm;
     border-bottom: 1px solid #ddd; page-break-after: avoid; }
h3 { font-size: 11pt; color: #222; margin: 5.5mm 0 2mm; page-break-after: avoid; }
h4 { font-size: 10pt; color: #333; margin: 4mm 0 1.5mm; page-break-after: avoid; }

p { margin: 0 0 2.6mm; orphans: 2; widows: 2; }
ul, ol { margin: 0 0 2.6mm; padding-left: 6mm; }
li { margin-bottom: 1mm; }

strong { color: #000; }

/* ---------- links ---------- */
a { color: #0b5cad; text-decoration: none; }

/* ---------- code ---------- */
code {
  font-family: "Cascadia Mono", "Consolas", "DejaVu Sans Mono", monospace;
  font-size: 8.4pt; background: #f4f4f6; padding: 0.5mm 1mm;
  border-radius: 2px; color: #b0004e; word-break: break-word;
}
pre {
  background: #f7f7f9; border: 1px solid #e2e2e8; border-left: 3px solid #c8102e;
  border-radius: 3px; padding: 2.5mm 3mm; margin: 0 0 3mm;
  font-size: 7.9pt; line-height: 1.42; overflow: visible;
  white-space: pre-wrap; word-break: break-word;
  page-break-inside: avoid;
}
pre code { background: none; padding: 0; color: #1a1a1a; font-size: inherit; }

/* ASCII diagrams need box-drawing glyphs and tight leading */
pre.diagram { line-height: 1.25; font-size: 7.4pt; }

/* ---------- tables ---------- */
table {
  border-collapse: collapse; width: 100%; margin: 0 0 3.5mm;
  font-size: 8.4pt; page-break-inside: auto;
}
thead { display: table-header-group; }      /* repeat header across pages */
tr { page-break-inside: avoid; }
th {
  background: #f0f0f3; border: 1px solid #d5d5dc; padding: 1.4mm 2mm;
  text-align: left; font-weight: 700; color: #111;
}
td { border: 1px solid #e0e0e6; padding: 1.4mm 2mm; vertical-align: top; }
tbody tr:nth-child(even) { background: #fafafb; }

/* ---------- blockquotes ---------- */
blockquote {
  margin: 0 0 3mm; padding: 2mm 3mm; background: #fbf7e8;
  border-left: 3px solid #e0a800; color: #3a3223;
  page-break-inside: avoid;
}
blockquote p:last-child { margin-bottom: 0; }

hr { border: none; border-top: 1px solid #ddd; margin: 5mm 0; }

/* keep a heading with the block that follows it */
h1 + *, h2 + *, h3 + * { page-break-before: avoid; }
"""

MD_EXT = ["tables", "fenced_code", "sane_lists", "attr_list", "md_in_html", "footnotes"]


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def strip_nav(md: str) -> str:
    """Remove the inter-file 'Next: ...' navigation lines — meaningless in print."""
    md = re.sub(r"^\*\*Next:\*\*.*$", "", md, flags=re.M)
    md = re.sub(r"^---\s*\n\s*$", "", md, flags=re.M)
    return md


def rewrite_links(html_text: str, filemap: dict[str, str]) -> str:
    """Turn cross-file markdown links into internal anchors."""
    def repl(m):
        href = m.group(1)
        target = href.split("#")[0]
        if target in filemap:
            return f'href="#{filemap[target]}"'
        return m.group(0)
    return re.sub(r'href="([^"]+\.md[^"]*)"', repl, html_text)


def mark_diagrams(html_text: str) -> str:
    """Tag <pre> blocks containing box-drawing characters so they get tighter CSS."""
    def repl(m):
        block = m.group(0)
        if any(ch in block for ch in "┌└├─│▼►╔═╚"):
            return block.replace("<pre>", '<pre class="diagram">', 1)
        return block
    return re.sub(r"<pre>.*?</pre>", repl, html_text, flags=re.S)


def build_html(page_numbers: dict[str, int] | None = None) -> str:
    filemap = {fn: slugify(fn) for fn, _, _ in ORDER}
    body_parts: list[str] = []

    # ---- title page
    total_words = sum(len((HB / fn).read_text(encoding="utf-8").split()) for fn, _, _ in ORDER)
    body_parts.append(f"""
<div class="titlepage">
  <h1>{html.escape(TITLE)}</h1>
  <div class="rule"></div>
  <div class="sub">{html.escape(SUBTITLE)}</div>
  <div class="meta">
    {html.escape(EDITION)}<br>
    Written for an experienced manual and automation QA engineer<br>
    moving into GenAI / AI Quality Engineering<br>
    No prior AI or ML background assumed
  </div>
  <div class="stats">
    {len(ORDER)} chapters &nbsp;·&nbsp; ~{total_words // 1000}k words<br>
    Volatile facts verified 9 September 2026 and marked ⏳
  </div>
</div>""")

    # ---- table of contents
    toc = ['<div class="toc"><h1>Contents</h1>']
    last_section = None
    for fn, title, section in ORDER:
        if section != last_section:
            toc.append(f'<div class="section">{html.escape(section)}</div>')
            last_section = section
        anchor = filemap[fn]
        pno = ""
        if page_numbers and anchor in page_numbers:
            pno = str(page_numbers[anchor])
        toc.append(
            f'<div class="row"><span class="t"><a href="#{anchor}">{html.escape(title)}</a></span>'
            f'<span class="dots"></span><span class="p">{pno}</span></div>'
        )
    toc.append("</div>")
    body_parts.append("\n".join(toc))

    # ---- chapters
    for fn, title, _ in ORDER:
        raw = strip_nav((HB / fn).read_text(encoding="utf-8"))
        converted = markdown.markdown(raw, extensions=MD_EXT)
        converted = rewrite_links(converted, filemap)
        converted = mark_diagrams(converted)
        body_parts.append(
            f'<div class="chapter" id="{filemap[fn]}">\n{converted}\n</div>'
        )

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>{html.escape(TITLE)}</title>
<style>{CSS}</style>
</head><body>
{"".join(body_parts)}
</body></html>"""


def find_chrome() -> str:
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise RuntimeError("No Chrome or Edge found")


def render(html_path: Path, pdf_path: Path) -> None:
    browser = find_chrome()
    profile = WORK / "profile"
    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=30000",
        f"--user-data-dir={profile}",
        f"--print-to-pdf={pdf_path}",
        html_path.as_uri(),
    ]
    subprocess.run(cmd, check=True, capture_output=True, timeout=600)
    if not pdf_path.exists():
        raise RuntimeError("Chrome produced no PDF")


def locate_chapters(pdf_path: Path) -> dict[str, int]:
    """Find the 1-based page each chapter starts on, by matching its H1 text."""
    reader = PdfReader(str(pdf_path))
    # first distinctive line of each chapter's H1
    wanted = []
    for fn, title, _ in ORDER:
        first_line = (HB / fn).read_text(encoding="utf-8").lstrip().split("\n", 1)[0]
        h1 = re.sub(r"^#+\s*", "", first_line).strip()
        key = re.sub(r"[^a-z0-9]+", "", h1.lower())[:38]
        wanted.append((slugify(fn), key))

    found: dict[str, int] = {}
    idx = 0
    for pageno, page in enumerate(reader.pages, start=1):
        if idx >= len(wanted):
            break
        try:
            text = re.sub(r"[^a-z0-9]+", "", (page.extract_text() or "").lower())
        except Exception:
            continue
        # chapters appear in order, so only look for the next expected one
        while idx < len(wanted) and wanted[idx][1] and wanted[idx][1] in text:
            found[wanted[idx][0]] = pageno
            idx += 1
    return found


def stamp_and_bookmark(src: Path, dst: Path, chapter_pages: dict[str, int]) -> None:
    """Add page numbers to every page and a PDF outline for navigation."""
    reader = PdfReader(str(src))
    n = len(reader.pages)
    w, h = A4

    # build a one-page-per-number stamp document
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    for i in range(1, n + 1):
        if i > 2:                                  # skip title page and TOC page 1
            c.setFont("Helvetica", 7.5)
            c.setFillColorRGB(0.42, 0.42, 0.45)
            c.drawCentredString(w / 2, 10 * 2.83, str(i))
            c.setFont("Helvetica", 6.5)
            c.drawString(16 * 2.83, 10 * 2.83, "The GenAI Testing Handbook")
        c.showPage()
    c.save()
    buf.seek(0)
    stamps = PdfReader(buf)

    writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        page.merge_page(stamps.pages[i])
        writer.add_page(page)

    # outline
    pages_by_anchor = chapter_pages
    last_section = None
    section_item = None
    for fn, title, section in ORDER:
        anchor = slugify(fn)
        pno = pages_by_anchor.get(anchor)
        if pno is None:
            continue
        if section != last_section:
            section_item = writer.add_outline_item(section, pno - 1)
            last_section = section
        writer.add_outline_item(title, pno - 1, parent=section_item)

    writer.add_metadata({
        "/Title": TITLE,
        "/Subject": SUBTITLE,
        "/Author": "Compiled with Claude Code",
        "/Keywords": "GenAI testing, LLM evaluation, RAG testing, AI security, AI QA",
    })

    # Chrome embeds a font subset per page; dedupe + deflate takes ~18 MB to ~2 MB
    for page in writer.pages:
        page.compress_content_streams(level=9)
    try:
        writer.compress_identical_objects()
    except Exception:
        pass

    with open(dst, "wb") as f:
        writer.write(f)


def main() -> None:
    print(f"work dir: {WORK}")

    # pass 1 — render to discover page numbers
    print("pass 1: rendering …")
    h1 = WORK / "book1.html"
    h1.write_text(build_html(), encoding="utf-8")
    p1 = WORK / "book1.pdf"
    render(h1, p1)
    pages = len(PdfReader(str(p1)).pages)
    print(f"  {pages} pages")

    print("locating chapters …")
    chapter_pages = locate_chapters(p1)
    print(f"  located {len(chapter_pages)}/{len(ORDER)} chapters")

    # pass 2 — render with real page numbers in the TOC
    print("pass 2: rendering with TOC page numbers …")
    h2 = WORK / "book2.html"
    h2.write_text(build_html(chapter_pages), encoding="utf-8")
    p2 = WORK / "book2.pdf"
    render(h2, p2)

    # page numbers may have shifted by a page if the TOC grew; re-locate
    chapter_pages = locate_chapters(p2) or chapter_pages

    print("stamping page numbers and bookmarks …")
    stamp_and_bookmark(p2, OUT, chapter_pages)

    size_mb = OUT.stat().st_size / 1024 / 1024
    print(f"\nDONE  {OUT}")
    print(f"      {len(PdfReader(str(OUT)).pages)} pages · {size_mb:.1f} MB")
    shutil.rmtree(WORK, ignore_errors=True)


if __name__ == "__main__":
    main()
