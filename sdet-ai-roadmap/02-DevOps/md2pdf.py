"""
Minimal, purpose-built Markdown -> PDF renderer using ReportLab.

Handles the subset used in these notes:
  #/##/### headings, paragraphs, - bullets, 1. numbered lists,
  ``` fenced code, | tables |, > blockquotes, --- rules,
  **bold**, `inline code`

Usage:  python md2pdf.py input.md output.pdf "Doc Title" "Subtitle"
"""
import re
import sys
from html import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, PageBreak, Paragraph, Preformatted,
    Spacer, Table, TableStyle, HRFlowable,
)

# ------------------------------------------------- Unicode-capable fonts
# The built-in Type1 fonts mangle em dashes and bullets; real TrueType
# fonts render and extract them correctly.
_FONTS = [
    ("Body",  r"C:\Windows\Fonts\arial.ttf",    "Helvetica"),
    ("BodyB", r"C:\Windows\Fonts\arialbd.ttf",  "Helvetica-Bold"),
    ("Mono",  r"C:\Windows\Fonts\consola.ttf",  "Courier"),
    ("MonoB", r"C:\Windows\Fonts\consolab.ttf", "Courier-Bold"),
]
FONT = {}
for name, path, fallback in _FONTS:
    try:
        pdfmetrics.registerFont(TTFont(name, path))
        FONT[name] = name
    except Exception:
        FONT[name] = fallback
pdfmetrics.registerFontFamily(
    FONT["Body"], normal=FONT["Body"], bold=FONT["BodyB"],
    italic=FONT["Body"], boldItalic=FONT["BodyB"])
pdfmetrics.registerFontFamily(
    FONT["Mono"], normal=FONT["Mono"], bold=FONT["MonoB"],
    italic=FONT["Mono"], boldItalic=FONT["MonoB"])

BODY, BODYB, MONO = FONT["Body"], FONT["BodyB"], FONT["Mono"]

# ---------------------------------------------------------------- palette
INK      = colors.HexColor("#1a1a1a")
MUTED    = colors.HexColor("#5a5a5a")
ACCENT   = colors.HexColor("#0b5d8f")
RULE     = colors.HexColor("#d0d7de")
CODE_BG  = colors.HexColor("#f6f8fa")
CODE_FG  = colors.HexColor("#0b2942")
INLINE   = colors.HexColor("#a11f2c")
TH_BG    = colors.HexColor("#eef3f7")
ROW_BG   = colors.HexColor("#fafcfd")
QUOTE_BG = colors.HexColor("#fff8e6")
QUOTE_LN = colors.HexColor("#e0a800")

PAGE_W, PAGE_H = A4
LM = RM = 16 * mm
TM = 15 * mm
BM = 16 * mm
CONTENT_W = PAGE_W - LM - RM

# ---------------------------------------------------------------- styles
_ss = getSampleStyleSheet()

S = {
    "h1": ParagraphStyle(
        "h1", parent=_ss["Heading1"], fontName=BODYB, fontSize=17,
        leading=21, textColor=ACCENT, spaceBefore=16, spaceAfter=7),
    "h2": ParagraphStyle(
        "h2", parent=_ss["Heading2"], fontName=BODYB, fontSize=13,
        leading=16, textColor=INK, spaceBefore=13, spaceAfter=5),
    "h3": ParagraphStyle(
        "h3", parent=_ss["Heading3"], fontName=BODYB, fontSize=10.5,
        leading=13, textColor=colors.HexColor("#333333"),
        spaceBefore=10, spaceAfter=4),
    "body": ParagraphStyle(
        "body", parent=_ss["BodyText"], fontName=BODY, fontSize=9,
        leading=13.2, textColor=INK, alignment=TA_LEFT,
        spaceBefore=0, spaceAfter=6),
    "bullet": ParagraphStyle(
        "bullet", parent=_ss["BodyText"], fontName=BODY, fontSize=9,
        leading=13, textColor=INK, leftIndent=11, bulletIndent=2,
        spaceBefore=0, spaceAfter=2.5),
    "quote": ParagraphStyle(
        "quote", parent=_ss["BodyText"], fontName=BODY, fontSize=8.8,
        leading=12.6, textColor=colors.HexColor("#4a3c10"),
        leftIndent=6, rightIndent=4, spaceBefore=1, spaceAfter=1),
    "code": ParagraphStyle(
        "code", fontName=MONO, fontSize=7.4, leading=9.4,
        textColor=CODE_FG, spaceBefore=0, spaceAfter=0),
    "th": ParagraphStyle(
        "th", fontName=BODYB, fontSize=8.1, leading=10.3,
        textColor=INK),
    "td": ParagraphStyle(
        "td", fontName=BODY, fontSize=8.1, leading=10.3,
        textColor=INK),
    "title": ParagraphStyle(
        "title", fontName=BODYB, fontSize=27, leading=32,
        textColor=ACCENT, spaceAfter=8),
    "subtitle": ParagraphStyle(
        "subtitle", fontName=BODY, fontSize=12, leading=17,
        textColor=MUTED, spaceAfter=20),
    "meta": ParagraphStyle(
        "meta", fontName=BODY, fontSize=8.5, leading=13,
        textColor=MUTED),
}

CODE_WRAP = 108   # chars before a code line is soft-wrapped


# ------------------------------------------------------------ inline spans
def inline(text: str) -> str:
    """Convert **bold** and `code` to ReportLab markup, escaping the rest."""
    out, i, n = [], 0, len(text)
    while i < n:
        # `inline code`
        if text[i] == "`":
            j = text.find("`", i + 1)
            if j != -1:
                out.append(
                    f'<font face="{MONO}" size="8" color="#a11f2c">'
                    + escape(text[i + 1:j]) + "</font>")
                i = j + 1
                continue
        # **bold**
        if text.startswith("**", i):
            j = text.find("**", i + 2)
            if j != -1:
                out.append("<b>" + inline(text[i + 2:j]) + "</b>")
                i = j + 2
                continue
        out.append(escape(text[i]))
        i += 1
    return "".join(out)


def wrap_code(lines):
    """Soft-wrap over-long code lines so nothing runs off the page."""
    result = []
    for ln in lines:
        ln = ln.replace("\t", "    ")
        while len(ln) > CODE_WRAP:
            cut = ln.rfind(" ", 0, CODE_WRAP)
            if cut < CODE_WRAP * 0.55:
                cut = CODE_WRAP
            result.append(ln[:cut])
            ln = "    " + ln[cut:].lstrip()
        result.append(ln)
    return result


def code_block(lines):
    body = "\n".join(wrap_code(lines)) or " "
    inner = Preformatted(body, S["code"])
    t = Table([[inner]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), CODE_BG),
        ("BOX",          (0, 0), (-1, -1), 0.5, RULE),
        ("LEFTPADDING",  (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
    ]))
    return t


def md_table(rows):
    header, body = rows[0], rows[1:]
    ncols = len(header)

    # weight columns by content length, clamped so no column is unusable
    weights = []
    for c in range(ncols):
        cells = [header[c]] + [r[c] for r in body if c < len(r)]
        weights.append(max(6, max(len(x) for x in cells) if cells else 6))
    total = sum(weights)
    widths = [max(CONTENT_W * 0.09, CONTENT_W * w / total) for w in weights]
    scale = CONTENT_W / sum(widths)
    widths = [w * scale for w in widths]

    data = [[Paragraph(inline(c), S["th"]) for c in header]]
    for r in body:
        r = (r + [""] * ncols)[:ncols]
        data.append([Paragraph(inline(c), S["td"]) for c in r])

    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND",   (0, 0), (-1, 0), TH_BG),
        ("LINEBELOW",    (0, 0), (-1, 0), 0.8, ACCENT),
        ("GRID",         (0, 0), (-1, -1), 0.4, RULE),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
    ]
    for i in range(2, len(data), 2):
        style.append(("BACKGROUND", (0, i), (-1, i), ROW_BG))
    t.setStyle(TableStyle(style))
    return t


def quote_block(lines):
    txt = " ".join(lines).strip()
    t = Table([[Paragraph(inline(txt), S["quote"])]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), QUOTE_BG),
        ("LINEBEFORE",   (0, 0), (0, -1), 2.2, QUOTE_LN),
        ("LEFTPADDING",  (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
    ]))
    return t


# ---------------------------------------------------------------- parser
def parse(md: str):
    flow = []
    lines = md.split("\n")
    i, n = 0, len(lines)
    para, bullets = [], []

    def flush_para():
        if para:
            flow.append(Paragraph(inline(" ".join(para).strip()), S["body"]))
            para.clear()

    def flush_bullets():
        if bullets:
            for mark, txt in bullets:
                flow.append(Paragraph(inline(txt), S["bullet"],
                                      bulletText=mark))
            flow.append(Spacer(1, 5))
            bullets.clear()

    def flush_all():
        flush_para()
        flush_bullets()

    while i < n:
        ln = lines[i]
        stripped = ln.strip()

        # fenced code
        if stripped.startswith("```"):
            flush_all()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            flow.append(code_block(buf))
            flow.append(Spacer(1, 7))
            continue

        # table
        if stripped.startswith("|") and stripped.endswith("|"):
            flush_all()
            raw = []
            while i < n:
                s = lines[i].strip()
                if not (s.startswith("|") and s.endswith("|")):
                    break
                raw.append([c.strip() for c in s.strip("|").split("|")])
                i += 1
            rows = [r for r in raw
                    if not all(re.fullmatch(r":?-{2,}:?", c or "-")
                               for c in r)]
            if rows:
                flow.append(md_table(rows))
                flow.append(Spacer(1, 8))
            continue

        # blockquote
        if stripped.startswith(">"):
            flush_all()
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            flow.append(quote_block(buf))
            flow.append(Spacer(1, 8))
            continue

        # horizontal rule
        if re.fullmatch(r"-{3,}", stripped):
            flush_all()
            flow.append(Spacer(1, 3))
            flow.append(HRFlowable(width="100%", thickness=0.6, color=RULE))
            flow.append(Spacer(1, 5))
            i += 1
            continue

        # headings
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            flush_all()
            level = len(m.group(1))
            key = "h1" if level == 1 else ("h2" if level == 2 else "h3")
            flow.append(Paragraph(inline(m.group(2)), S[key]))
            if level == 1:
                flow.append(HRFlowable(width="100%", thickness=1.1,
                                       color=ACCENT, spaceAfter=7))
            i += 1
            continue

        # bullets
        m = re.match(r"^[-*]\s+(.*)$", stripped)
        if m:
            flush_para()
            bullets.append(("•", m.group(1)))
            i += 1
            continue

        # numbered
        m = re.match(r"^(\d+)[.)]\s+(.*)$", stripped)
        if m:
            flush_para()
            bullets.append((m.group(1) + ".", m.group(2)))
            i += 1
            continue

        # blank line
        if not stripped:
            flush_all()
            i += 1
            continue

        # plain paragraph text
        flush_bullets()
        para.append(stripped)
        i += 1

    flush_all()
    return flow


# ------------------------------------------------------------ page chrome
def make_chrome(title):
    def draw(canvas, doc):
        canvas.saveState()
        page = canvas.getPageNumber()
        if page > 1:
            canvas.setStrokeColor(RULE)
            canvas.setLineWidth(0.4)
            canvas.line(LM, PAGE_H - TM + 5, PAGE_W - RM, PAGE_H - TM + 5)
            canvas.setFont(BODY, 7.5)
            canvas.setFillColor(MUTED)
            canvas.drawString(LM, PAGE_H - TM + 9, title)
            canvas.line(LM, BM - 5, PAGE_W - RM, BM - 5)
            canvas.drawCentredString(PAGE_W / 2.0, BM - 13, str(page))
        canvas.restoreState()
    return draw


def build(md_path, pdf_path, title, subtitle, meta_lines):
    with open(md_path, encoding="utf-8") as f:
        md = f.read()

    # drop the leading H1/H2 — the cover page carries them
    body = re.sub(r"\A(?:\s*#{1,2} .*\n)+", "", md, count=1)

    doc = BaseDocTemplate(
        pdf_path, pagesize=A4,
        leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM,
        title=title, author="SDET notes", subject=subtitle,
    )
    frame = Frame(LM, BM, CONTENT_W, PAGE_H - TM - BM, id="main",
                  leftPadding=0, rightPadding=0,
                  topPadding=0, bottomPadding=0)
    doc.addPageTemplates([
        PageTemplate(id="all", frames=[frame], onPage=make_chrome(title))
    ])

    story = [
        Spacer(1, 38 * mm),
        Paragraph(escape(title), S["title"]),
        HRFlowable(width="42%", thickness=2.5, color=ACCENT,
                   hAlign="LEFT", spaceAfter=12),
        Paragraph(escape(subtitle), S["subtitle"]),
    ]
    for line in meta_lines:
        story.append(Paragraph(inline(line), S["meta"]))
    story.append(PageBreak())
    story += parse(body)

    doc.build(story)
    return pdf_path


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    ttl = sys.argv[3] if len(sys.argv) > 3 else "Notes"
    sub = sys.argv[4] if len(sys.argv) > 4 else ""
    extra = sys.argv[5:] if len(sys.argv) > 5 else []
    print("written:", build(src, dst, ttl, sub, extra))
