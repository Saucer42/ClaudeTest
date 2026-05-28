"""Convert a Markdown resume to a clean PDF using ReportLab."""

import sys
import re
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

BLUE = colors.HexColor("#1e50a0")
DARK = colors.HexColor("#141414")
MID = colors.HexColor("#444444")
LIGHT = colors.HexColor("#888888")

MARGIN = 0.65 * inch


def clean(text):
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"^[-*]\s+", "", text.strip())
    return text.strip()


def bold_clean(text):
    """Preserve ** as ReportLab <b> tags."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(r"^[-*]\s+", "", text.strip())
    return text.strip()


def build_styles():
    s = getSampleStyleSheet()

    def ps(name, **kw):
        base = kw.pop("parent", "Normal")
        return ParagraphStyle(name, parent=s[base], **kw)

    return {
        "name": ps("name", fontSize=18, fontName="Helvetica-Bold",
                   textColor=DARK, alignment=TA_CENTER, spaceAfter=2),
        "contact": ps("contact", fontSize=8.5, fontName="Helvetica",
                      textColor=LIGHT, alignment=TA_CENTER, spaceAfter=6),
        "h2": ps("h2", fontSize=10, fontName="Helvetica-Bold",
                 textColor=BLUE, spaceBefore=8, spaceAfter=1),
        "h3": ps("h3", fontSize=10, fontName="Helvetica-Bold",
                 textColor=DARK, spaceBefore=6, spaceAfter=1),
        "h4": ps("h4", fontSize=9, fontName="Helvetica-Oblique",
                 textColor=MID, spaceAfter=2),
        "sublabel": ps("sublabel", fontSize=9, fontName="Helvetica-Bold",
                       textColor=MID, spaceBefore=4, spaceAfter=1),
        "bullet": ps("bullet", fontSize=9, fontName="Helvetica",
                     textColor=DARK, leftIndent=12, firstLineIndent=-8,
                     spaceAfter=1.5, leading=13),
        "body": ps("body", fontSize=9.5, fontName="Helvetica",
                   textColor=DARK, spaceAfter=4, leading=14),
        "table_key": ps("table_key", fontSize=9, fontName="Helvetica-Bold",
                        textColor=DARK),
        "table_val": ps("table_val", fontSize=9, fontName="Helvetica",
                        textColor=DARK),
    }


def render(md_path, pdf_path):
    with open(md_path, encoding="utf-8") as f:
        lines = [l.rstrip("\n") for l in f.readlines()]

    st = build_styles()
    story = []

    def hr():
        story.append(Spacer(1, 2))
        story.append(HRFlowable(width="100%", thickness=0.4,
                                color=colors.HexColor("#b0b0b0")))
        story.append(Spacer(1, 4))

    def section_hr():
        story.append(HRFlowable(width="100%", thickness=0.5, color=BLUE))
        story.append(Spacer(1, 3))

    i = 0
    table_rows = []

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        i += 1

        # Flush any accumulated table rows
        if table_rows and not stripped.startswith("|"):
            col_w = [1.3 * inch, 4.5 * inch]
            t = Table(table_rows, colWidths=col_w)
            t.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TEXTCOLOR", (0, 0), (-1, -1), DARK),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1),
                 [colors.HexColor("#f5f7fc"), colors.white]),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(t)
            table_rows = []

        if not stripped:
            story.append(Spacer(1, 3))
            continue

        if stripped == "---":
            hr()
            continue

        # H1 name
        if re.match(r"^# [^#]", stripped):
            story.append(Paragraph(clean(stripped[2:]), st["name"]))
            continue

        # Contact line
        if "|" in stripped and "@" in stripped and not stripped.startswith("#"):
            story.append(Paragraph(clean(stripped), st["contact"]))
            continue

        # H2 section
        if stripped.startswith("## "):
            story.append(Paragraph(clean(stripped[3:]).upper(), st["h2"]))
            section_hr()
            continue

        # H3 company
        if stripped.startswith("### "):
            story.append(Paragraph(clean(stripped[4:]), st["h3"]))
            continue

        # H4 role
        if stripped.startswith("#### "):
            story.append(Paragraph(clean(stripped[5:]), st["h4"]))
            continue

        # Bold sub-label **...**
        if re.match(r"^\*\*.+\*\*$", stripped):
            story.append(Paragraph(clean(stripped), st["sublabel"]))
            continue

        # Bullet
        if stripped.startswith("- "):
            txt = bold_clean(stripped[2:])
            story.append(Paragraph(f"• {txt}", st["bullet"]))
            continue

        # Table row
        if stripped.startswith("|"):
            if re.match(r"^\|[-| :]+\|$", stripped):
                continue  # separator
            cols = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cols) >= 2:
                table_rows.append([
                    Paragraph(clean(cols[0]), st["table_key"]),
                    Paragraph(clean(cols[1]), st["table_val"]),
                ])
            continue

        # Plain paragraph
        story.append(Paragraph(bold_clean(stripped), st["body"]))

    # Flush trailing table
    if table_rows:
        col_w = [1.3 * inch, 4.5 * inch]
        t = Table(table_rows, colWidths=col_w)
        t.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 0), (-1, -1), DARK),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1),
             [colors.HexColor("#f5f7fc"), colors.white]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(t)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=LETTER,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
    )
    doc.build(story)
    print(f"Saved: {pdf_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 md_to_pdf.py input.md output.pdf")
        sys.exit(1)
    render(sys.argv[1], sys.argv[2])
