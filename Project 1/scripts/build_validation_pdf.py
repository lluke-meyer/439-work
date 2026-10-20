#!/usr/bin/env python3
"""Build the FIN 439 Validation and AI Use PDF from its Markdown source."""

from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "validation-and-ai-use.md"
OUTPUT = ROOT / "docs" / "validation-and-ai-use.pdf"

NAVY = colors.HexColor("#102D43")
BLUE = colors.HexColor("#176B87")
ORANGE = colors.HexColor("#D4772C")
INK = colors.HexColor("#1F2A30")
MUTED = colors.HexColor("#5E6A70")
LINE = colors.HexColor("#CBD4D8")
PALE = colors.HexColor("#EFF5F7")
WHITE = colors.white


def register_fonts() -> tuple[str, str]:
    regular = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
    bold = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("ValidationSans", regular))
        pdfmetrics.registerFont(TTFont("ValidationSans-Bold", bold))
        return "ValidationSans", "ValidationSans-Bold"
    return "Helvetica", "Helvetica-Bold"


FONT, FONT_BOLD = register_fonts()


class ValidationDoc(BaseDocTemplate):
    def __init__(self, filename: str):
        super().__init__(
            filename,
            pagesize=letter,
            leftMargin=0.58 * inch,
            rightMargin=0.58 * inch,
            topMargin=0.52 * inch,
            bottomMargin=0.52 * inch,
            title="Validation and AI Use - Cadence Design Systems",
            author="Luke Meyer",
            subject="FIN 43900 Project 1 validation and AI-use record",
        )
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
            id="validation",
        )
        self.addPageTemplates(
            PageTemplate(id="validation", frames=[frame], onPage=self.decorate)
        )

    def decorate(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(NAVY)
        canvas.setLineWidth(2.0)
        canvas.line(
            doc.leftMargin,
            letter[1] - 0.30 * inch,
            letter[0] - doc.rightMargin,
            letter[1] - 0.30 * inch,
        )
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.45)
        canvas.line(
            doc.leftMargin,
            0.36 * inch,
            letter[0] - doc.rightMargin,
            0.36 * inch,
        )
        canvas.setFont(FONT, 6.7)
        canvas.setFillColor(MUTED)
        canvas.drawString(
            doc.leftMargin, 0.19 * inch, "FIN 43900 Project 1 | Cadence Design Systems"
        )
        canvas.drawRightString(
            letter[0] - doc.rightMargin,
            0.19 * inch,
            f"Validation and AI Use | {doc.page} of 4",
        )
        canvas.restoreState()


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        "VKicker",
        fontName=FONT_BOLD,
        fontSize=8,
        leading=10,
        textColor=ORANGE,
        uppercase=True,
        spaceAfter=4,
    )
)
styles.add(
    ParagraphStyle(
        "VTitle",
        fontName=FONT_BOLD,
        fontSize=20,
        leading=23,
        textColor=NAVY,
        spaceAfter=7,
    )
)
styles.add(
    ParagraphStyle(
        "VH1",
        fontName=FONT_BOLD,
        fontSize=12.5,
        leading=15,
        textColor=NAVY,
        spaceBefore=7,
        spaceAfter=4,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        "VH2",
        fontName=FONT_BOLD,
        fontSize=9.4,
        leading=11.5,
        textColor=BLUE,
        spaceBefore=5,
        spaceAfter=3,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        "VBody",
        fontName=FONT,
        fontSize=8.35,
        leading=10.8,
        textColor=INK,
        spaceAfter=4,
    )
)
styles.add(
    ParagraphStyle(
        "VBullet",
        fontName=FONT,
        fontSize=8.1,
        leading=10.5,
        textColor=INK,
        leftIndent=13,
        firstLineIndent=-8,
        bulletIndent=2,
        spaceAfter=2.4,
    )
)
styles.add(
    ParagraphStyle(
        "VSubBullet",
        fontName=FONT,
        fontSize=7.85,
        leading=10.1,
        textColor=INK,
        leftIndent=25,
        firstLineIndent=-8,
        bulletIndent=14,
        spaceAfter=2.1,
    )
)
styles.add(
    ParagraphStyle(
        "VTable",
        fontName=FONT,
        fontSize=6.0,
        leading=7.4,
        textColor=INK,
    )
)
styles.add(
    ParagraphStyle(
        "VTableHead",
        fontName=FONT_BOLD,
        fontSize=6.0,
        leading=7.4,
        textColor=WHITE,
    )
)


def inline_markup(text: str) -> str:
    rendered = html.escape(text.strip())
    rendered = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2" color="#176B87"><u>\1</u></a>',
        rendered,
    )
    rendered = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", rendered)
    rendered = re.sub(
        r"`([^`]+)`", r'<font name="Courier" color="#6B562F">\1</font>', rendered
    )
    return rendered


def markdown_table(rows: list[list[str]]) -> Table:
    column_count = len(rows[0])
    width = 7.34 * inch
    if column_count == 2:
        widths = [2.05 * inch, width - 2.05 * inch]
    else:
        widths = [width / column_count] * column_count
    data = []
    for row_index, row in enumerate(rows):
        style = "VTableHead" if row_index == 0 else "VTable"
        cells = [Paragraph(inline_markup(cell), styles[style]) for cell in row]
        data.append(cells)
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE]),
                ("GRID", (0, 0), (-1, -1), 0.4, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def parse_markdown(source: str) -> list[object]:
    lines = source.splitlines()
    story: list[object] = []
    index = 0
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            story.append(
                Paragraph(inline_markup(" ".join(paragraph)), styles["VBody"])
            )
            paragraph.clear()

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            index += 1
            continue
        if stripped == "---":
            flush_paragraph()
            story.append(Spacer(1, 4))
            index += 1
            continue
        if stripped.startswith("|") and index + 1 < len(lines):
            separator = lines[index + 1].strip()
            if separator.startswith("|") and set(separator.replace("|", "").replace("-", "").replace(":", "").replace(" ", "")) == set():
                flush_paragraph()
                raw_rows: list[list[str]] = []
                while index < len(lines) and lines[index].strip().startswith("|"):
                    parts = [part.strip() for part in lines[index].strip().strip("|").split("|")]
                    if index != len(lines) and not all(
                        re.fullmatch(r":?-+:?", part.replace(" ", "")) for part in parts
                    ):
                        raw_rows.append(parts)
                    index += 1
                story.append(markdown_table(raw_rows))
                story.append(Spacer(1, 4))
                continue
        if stripped.startswith("# "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[2:]), styles["VTitle"]))
        elif stripped.startswith("## "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[3:]), styles["VH1"]))
        elif stripped.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[4:]), styles["VH2"]))
        elif re.match(r"^\s*-\s+", line):
            flush_paragraph()
            indent = len(line) - len(line.lstrip())
            body = re.sub(r"^\s*-\s+", "", line)
            style = styles["VSubBullet"] if indent else styles["VBullet"]
            story.append(Paragraph(f"- {inline_markup(body)}", style))
        else:
            paragraph.append(stripped)
        index += 1
    flush_paragraph()
    return story


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = ValidationDoc(str(OUTPUT))
    story = parse_markdown(SOURCE.read_text(encoding="utf-8"))
    story.insert(0, Paragraph("MODEL ASSURANCE", styles["VKicker"]))
    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    main()
