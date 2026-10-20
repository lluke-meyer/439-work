#!/usr/bin/env python3
"""Build the two-page FIN 439 Project 1 decision memo."""

import shutil
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "decision-memo.pdf"
LEGACY_OUTPUT = ROOT / "docs" / "Decision-Memo.pdf"
SUBMISSION_OUTPUT = ROOT / "submission" / "Decision-Memo.pdf"

NAVY = colors.HexColor("#102D43")
BLUE = colors.HexColor("#176B87")
TEAL = colors.HexColor("#2A879D")
ORANGE = colors.HexColor("#D4772C")
INK = colors.HexColor("#1F2A30")
MUTED = colors.HexColor("#5E6A70")
LINE = colors.HexColor("#CBD4D8")
PALE = colors.HexColor("#EFF5F7")
PALE_ORANGE = colors.HexColor("#F9EEE5")
WHITE = colors.white


def register_fonts():
    regular = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
    bold = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("MemoSans", regular))
        pdfmetrics.registerFont(TTFont("MemoSans-Bold", bold))
        return "MemoSans", "MemoSans-Bold"
    return "Helvetica", "Helvetica-Bold"


FONT, FONT_BOLD = register_fonts()


class MemoDoc(BaseDocTemplate):
    def __init__(self, filename):
        super().__init__(
            filename,
            pagesize=letter,
            leftMargin=0.58 * inch,
            rightMargin=0.58 * inch,
            topMargin=0.50 * inch,
            bottomMargin=0.52 * inch,
            title="Cadence Design Systems Decision Memo",
            author="Luke Meyer",
            subject="FIN 43900 Project 1 investment committee decision",
        )
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="memo",
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        self.addPageTemplates(PageTemplate(id="memo", frames=[frame], onPage=self.decorate))

    def decorate(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(NAVY)
        canvas.setLineWidth(2.2)
        canvas.line(doc.leftMargin, letter[1] - 0.30 * inch, letter[0] - doc.rightMargin, letter[1] - 0.30 * inch)
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.45)
        canvas.line(doc.leftMargin, 0.36 * inch, letter[0] - doc.rightMargin, 0.36 * inch)
        canvas.setFont(FONT, 6.8)
        canvas.setFillColor(MUTED)
        canvas.drawString(doc.leftMargin, 0.19 * inch, "FIN 43900 Project 1 | Cadence Design Systems")
        canvas.drawRightString(letter[0] - doc.rightMargin, 0.19 * inch, f"Decision memo | {doc.page} of 2")
        canvas.restoreState()


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    "MemoTitle", fontName=FONT_BOLD, fontSize=20, leading=22, textColor=NAVY,
    spaceAfter=2,
))
styles.add(ParagraphStyle(
    "MemoKicker", fontName=FONT_BOLD, fontSize=8, leading=10, textColor=ORANGE,
    uppercase=True, spaceAfter=5,
))
styles.add(ParagraphStyle(
    "MemoMeta", fontName=FONT, fontSize=7.8, leading=10.4, textColor=INK,
))
styles.add(ParagraphStyle(
    "Headline", fontName=FONT_BOLD, fontSize=12.3, leading=15.2, textColor=NAVY,
    spaceBefore=4, spaceAfter=5,
))
styles.add(ParagraphStyle(
    "H1Memo", fontName=FONT_BOLD, fontSize=10.4, leading=12.5, textColor=NAVY,
    spaceBefore=6, spaceAfter=3, keepWithNext=True,
))
styles.add(ParagraphStyle(
    "H2Memo", fontName=FONT_BOLD, fontSize=8.6, leading=10.5, textColor=BLUE,
    spaceBefore=3, spaceAfter=2, keepWithNext=True,
))
styles.add(ParagraphStyle(
    "BodyMemo", fontName=FONT, fontSize=8.15, leading=10.45, textColor=INK,
    spaceAfter=4.2,
))
styles.add(ParagraphStyle(
    "BodyTight", fontName=FONT, fontSize=7.75, leading=9.8, textColor=INK,
    spaceAfter=3,
))
styles.add(ParagraphStyle(
    "Small", fontName=FONT, fontSize=6.7, leading=8.3, textColor=INK,
))
styles.add(ParagraphStyle(
    "SmallBold", fontName=FONT_BOLD, fontSize=6.7, leading=8.3, textColor=INK,
))
styles.add(ParagraphStyle(
    "TableHead", fontName=FONT_BOLD, fontSize=6.6, leading=8.0, textColor=WHITE,
))
styles.add(ParagraphStyle(
    "Metric", fontName=FONT_BOLD, fontSize=13.5, leading=15, textColor=NAVY,
    alignment=TA_RIGHT,
))
styles.add(ParagraphStyle(
    "MetricLabel", fontName=FONT_BOLD, fontSize=6.4, leading=7.5, textColor=MUTED,
))
styles.add(ParagraphStyle(
    "Formula", fontName="Courier", fontSize=6.6, leading=8.3, textColor=INK,
    leftIndent=7, rightIndent=4, borderColor=LINE, borderWidth=0.5,
    borderPadding=(4, 5, 4, 5), backColor=PALE, spaceBefore=2, spaceAfter=4,
))
styles.add(ParagraphStyle(
    "Fine", fontName=FONT, fontSize=6.2, leading=7.7, textColor=MUTED,
    spaceAfter=2,
))


def p(text, style="BodyMemo"):
    return Paragraph(text, styles[style])


def heading(text):
    return Paragraph(text, styles["H1Memo"])


def subheading(text):
    return Paragraph(text, styles["H2Memo"])


class ValuationScale(Flowable):
    """Compact valuation ladder comparing model evidence with market price."""

    def __init__(self, width=7.34 * inch, height=0.74 * inch):
        super().__init__()
        self.width = width
        self.height = height

    def draw(self):
        c = self.canv
        x0 = 0.22 * inch
        x1 = self.width - 0.20 * inch
        y = 0.29 * inch
        max_value = 330.0

        def xpos(value):
            return x0 + (value / max_value) * (x1 - x0)

        c.setStrokeColor(LINE)
        c.setLineWidth(1)
        c.line(x0, y, x1, y)
        for tick in (0, 100, 200, 300):
            x = xpos(tick)
            c.setStrokeColor(LINE)
            c.line(x, y - 3, x, y + 3)
            c.setFont(FONT, 5.8)
            c.setFillColor(MUTED)
            c.drawCentredString(x, y - 12, f"${tick}")

        # DCF range
        c.setStrokeColor(TEAL)
        c.setLineWidth(6)
        c.line(xpos(57.20), y, xpos(111.52), y)
        c.setFillColor(TEAL)
        c.circle(xpos(83.34), y, 3.3, fill=1, stroke=0)
        c.setFont(FONT_BOLD, 6.2)
        c.drawString(xpos(57.20), y + 10, "DCF $57-$112 | base $83")

        for value, label, color, dy in (
            (189.64, "EV/revenue $190", BLUE, 10),
            (209.47, "P/E $209", BLUE, 22),
            (313.04, "Market $313", ORANGE, 10),
        ):
            x = xpos(value)
            c.setStrokeColor(color)
            c.setLineWidth(1.6)
            c.line(x, y - 5, x, y + 7)
            c.setFont(FONT_BOLD, 6.0)
            c.setFillColor(color)
            if value > 280:
                c.drawRightString(x, y + dy, label)
            else:
                c.drawCentredString(x, y + dy, label)


def metric_strip():
    data = [
        [p("ACTION", "MetricLabel"), p("MARKET PRICE", "MetricLabel"), p("BASE DCF", "MetricLabel"), p("HIGHEST CROSS-CHECK", "MetricLabel")],
        [p("WATCH / DEFER", "Headline"), p("$313.04", "Metric"), p("$83.34", "Metric"), p("$209.47", "Metric")],
    ]
    table = Table(data, colWidths=[2.02 * inch, 1.52 * inch, 1.52 * inch, 2.18 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("LINEABOVE", (0, 0), (-1, 0), 0.8, LINE),
        ("LINEBELOW", (0, -1), (-1, -1), 0.8, LINE),
        ("LINEAFTER", (0, 0), (-2, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, 0), 5),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 0),
        ("TOPPADDING", (0, 1), (-1, 1), 0),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 5),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
    ]))
    return table


def valuation_table():
    data = [
        [p("Evidence route", "TableHead"), p("Implied value", "TableHead"), p("Discount", "TableHead"), p("Decision use", "TableHead")],
        [p("Integrated FCFF DCF", "SmallBold"), p("$57.20-$111.52", "Small"), p("64.4%-81.7%", "Small"), p("Primary intrinsic-value range", "Small")],
        [p("Synopsys EV/TTM revenue", "SmallBold"), p("$189.64", "Small"), p("39.4%", "Small"), p("Operating-value cross-check", "Small")],
        [p("Synopsys P/E", "SmallBold"), p("$209.47", "Small"), p("33.1%", "Small"), p("Equity-value cross-check", "Small")],
    ]
    table = Table(data, colWidths=[2.05 * inch, 1.25 * inch, 0.88 * inch, 3.06 * inch], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE]),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 1), (2, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def external_valuation_table():
    data = [
        [p("Post-date benchmark", "TableHead"), p("Value", "TableHead"), p("Method and main driver", "TableHead"), p("Use", "TableHead")],
        [p("ValueInvesting.io | Sep. 11", "SmallBold"), p("$137.37", "Small"), p("Five-year growth-exit DCF", "Small"), p("Lower outside DCF", "Small")],
        [p("Fair Value Calculator | Sep. 17", "SmallBold"), p("$224.24", "Small"), p("Weighted blend of 26 models", "Small"), p("Broad-method check", "Small")],
        [p("Alpha Spread | retrieved Oct. 18", "SmallBold"), p("$272.92", "Small"), p("Seven-year FCFE; 34.0% terminal net margin; 29.1x terminal P/E", "Small"), p("Optimistic boundary", "Small")],
    ]
    table = Table(data, colWidths=[1.72 * inch, 0.72 * inch, 3.31 * inch, 1.49 * inch], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ORANGE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE_ORANGE]),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 1), (1, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    return table


def expectations_table():
    data = [
        [p("Market-price test", "TableHead"), p("Result", "TableHead"), p("Interpretation", "TableHead")],
        [p("Growth only", "SmallBold"), p("+32.215 points/year", "Small"), p("FY2026/FY2030 growth becomes 46.2%/37.2% at 10% WACC.", "Small")],
        [p("Discount rate only", "SmallBold"), p("4.871% WACC", "Small"), p("Base operations require a rate 513 bp below the sourced 10.0%.", "Small")],
        [p("Bounded challenge", "SmallBold"), p("$203.95/share", "Small"), p("Still $109.09 below market despite aggressive combined assumptions.", "Small")],
        [p("Gross margin only", "SmallBold"), p("No solution below 99%", "Small"), p("Margin expansion alone cannot reconcile the price.", "Small")],
    ]
    table = Table(data, colWidths=[1.45 * inch, 1.45 * inch, 4.34 * inch], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE]),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    return table


def regime_overlay_table():
    data = [
        [p("Decision lens", "TableHead"), p("Operating/risk link", "TableHead"), p("Value and action", "TableHead")],
        [p("AI buildout extends", "SmallBold"), p("+3-point growth shift; 87.0% margin; beta 1.35; WACC 10.319%", "Small"), p("$93.48 | watch/defer", "Small")],
        [p("Orderly normalization", "SmallBold"), p("Base operations; beta 1.2751; WACC 10.011%", "Small"), p("$83.20 | watch/defer", "Small")],
        [p("Cycle reversal", "SmallBold"), p("-5-point growth shift; 84.5% margin; beta 1.50; WACC 10.936%", "Small"), p("$54.69 | do not initiate", "Small")],
        [p("Hexagon D&amp;E overlay", "SmallBold"), p("$440M starting revenue; margin/synergy ramp; 10.5% deal WACC", "Small"), p("$1.095B acquired EV; combined $78.93/share", "Small")],
    ]
    table = Table(data, colWidths=[1.55 * inch, 3.91 * inch, 1.78 * inch], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE]),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    return table


def monitoring_table():
    data = [
        [p("What could change", "TableHead"), p("Monitor and frequency", "TableHead"), p("Committee response", "TableHead")],
        [p("Hexagon integration lifts durable cash flow", "SmallBold"), p("Update organic growth, margins, FCFF, cash, debt, and shares within five trading days of each filing.", "Small"), p("Rebuild all scenarios and the bridge before reconsidering.", "Small")],
        [p("Semiconductor and AI demand accelerates or cools", "SmallBold"), p("Track SIA sales, backlog, RPO, guidance, customer R&amp;D commentary, and the industry beta each quarter.", "Small"), p("Give the boom credit only when growth converts to FCFF; move toward downside if growth weakens while beta or WACC rises.", "Small")],
        [p("Downside becomes more likely", "SmallBold"), p("Compare reported growth and gross margin with the 11%-to-2% path and 84.5% downside margin.", "Small"), p("Move to do not initiate if weakness persists for two filings.", "Small")],
        [p("Model or evidence loses integrity", "SmallBold"), p("Re-run statement ties, cash-flow ties, scenario order, source dates, and the terminal-growth test after each update.", "Small"), p("Stop if statements do not tie, a bridge is incomplete, or terminal growth reaches WACC.", "Small")],
    ]
    table = Table(data, colWidths=[1.78 * inch, 3.00 * inch, 2.46 * inch], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE]),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def proof_table():
    data = [
        [p("Evidence I trust now", "TableHead"), p("Remaining uncertainty", "TableHead"), p("Evidence required to reverse", "TableHead")],
        [p("Statements articulate; cash flow ties; scenario order and rate direction pass; the 10.0% WACC is sourced. The separate Hexagon overlay is reproducible.", "Small"), p("The overlay is not a full post-acquisition statement rebuild and its operating inputs are analyst assumptions.", "Small"), p("Two filings separating acquired and organic growth, margins, integration cash costs, and reinvestment.", "Small")],
        [p("Both peer methods remain below market even though they value different claims.", "Small"), p("Synopsys is a single peer and its Ansys acquisition changes the comparison.", "Small"), p("At least two qualified peers admitted under the same predeclared policy and definitions.", "Small")],
        [p("Price requires a 32.215-point annual growth shift or a 4.871% WACC; the bounded challenge reaches only $203.95.", "Small"), p("Market-implied tests reveal the burden of proof; they do not prove the required outcomes are impossible.", "Small"), p("Two filings showing durable organic growth, margin realization, and cash conversion sufficient to support a revised forecast.", "Small")],
    ]
    table = Table(data, colWidths=[2.36 * inch, 2.34 * inch, 2.54 * inch], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE]),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def memo_header():
    meta = Table([
        [p("TO", "MemoKicker"), p("Buy-Side Investment Committee", "MemoMeta"), p("VALUATION DATE", "MemoKicker"), p("September 1, 2026", "MemoMeta")],
        [p("FROM", "MemoKicker"), p("Luke Meyer, Junior Financial Analyst", "MemoMeta"), p("SUBJECT", "MemoKicker"), p("Defer a CDNS position at $313.04", "MemoMeta")],
    ], colWidths=[0.45 * inch, 2.85 * inch, 0.95 * inch, 2.99 * inch])
    meta.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return [
        p("INVESTMENT COMMITTEE DECISION", "MemoKicker"),
        p("Cadence Design Systems Decision Memo", "MemoTitle"),
        meta,
        Spacer(1, 4),
    ]


def build_story():
    story = []
    story.extend(memo_header())
    story.extend([
        metric_strip(),
        heading("Decision and committee ask"),
        p("I recommend <b>watch/defer with no position</b> in Cadence Design Systems at the September 1, 2026 closing price of <b>$313.04 per share</b>. The integrated FCFF DCF supports <b>$57.20-$111.52</b>, including a base value of <b>$83.34</b>. Synopsys cross-checks are higher at <b>$189.64</b> from EV/TTM revenue and <b>$209.47</b> from P/E, but both remain below the market. The methods disagree on the size of the overvaluation, not on the action."),
        p("Reopen the decision only when an acquisition-aware DCF and at least two qualified peer observations independently support value at least <b>15% above the then-current market price</b>. A lower price alone is not enough; the operating evidence must also survive the next two quarterly filings."),
        heading("Evidence and as-of date"),
        subheading("Internal valuation map: three methods, one conclusion"),
        ValuationScale(),
        valuation_table(),
        Spacer(1, 3),
        p("I do not average the spread. The DCF prices Cadence's forecast cash flows; the peer methods show what one qualified comparable commands in the market. Synopsys remains imperfect after its Ansys acquisition, so the multiples corroborate the DCF instead of replacing it. All three methods still point to <b>no current entry</b>."),
        p("Cadence has real momentum behind it. Recurring revenue represented <b>80% of FY2025 revenue</b>. In Q2 2026, revenue reached <b>$1.584 billion</b>, backlog hit a record <b>$8.1 billion</b>, and management raised its full-year revenue-growth outlook to roughly <b>19%</b>. The Semiconductor Industry Association also reported that global semiconductor sales increased <b>35.1% from Q1 to Q2 2026</b>. These results support near-term demand for Cadence's design software, hardware, and IP. They do not justify carrying boom-level growth into perpetuity."),
        p("The base forecast grows revenue from <b>$5.30 billion to $8.44 billion</b> by FY2030, but <b>74.1%</b> of base enterprise value comes from terminal value. Price requires either a uniform <b>32.215-point annual growth increase</b> or a <b>4.871% WACC</b> with base operations. Even an aggressive bounded challenge reaches only <b>$203.95</b>. I do not believe the current boom closes that gap."),
        subheading("External valuation reconciliation: post-date audit only"),
        external_valuation_table(),
        Spacer(1, 3),
        p("These later estimates do not enter the September 1 recommendation. Alpha Spread is the optimistic boundary: roughly <b>10.3% seven-year growth</b>, net margin moving from <b>35.4% to 34.0%</b>, <b>101% cash conversion</b>, a <b>9.3% discount rate</b>, and a <b>29.1x terminal P/E</b>. Applying those inputs to about <b>$5.838B</b> of starting revenue reproduces <b>$277.46</b>, close to its published $272.92. My five-year, accounting-linked FCFF case uses a 10.0% WACC, 3.0% perpetual growth, and net margins reaching roughly 20%. The gap is mainly optimism about margins and terminal value, not hidden arithmetic."),
        heading("How WACC and enterprise value were built"),
        p("The sourced WACC is <b>10.0%</b>, rounded from <b>10.0115%</b>. A 4.79% ten-year Treasury yield, 4.23% implied equity risk premium, and 1.2482 industry unlevered beta produce a <b>1.2751 relevered beta</b> and <b>10.1837% cost of equity</b>. With <b>97.2013% equity</b>, <b>2.7987% debt</b>, a 5.3804% pre-tax debt cost, and a 25.1084% tax rate:"),
        p("WACC = 97.2013% x 10.1837% + 2.7987% x 5.3804% x (1 - 25.1084%) = 10.0115%", "Formula"),
        p("The peer bridge is equally reproducible: Synopsys's <b>$85.924B EV</b> divided by <b>$9.416B TTM revenue</b> gives <b>9.1249x</b>. Applied to Cadence's <b>$5.838B</b> TTM revenue, then bridged through cash, debt, and 275.393M shares, it produces <b>$189.64</b>."),
        PageBreak(),
        p("DECISION DISCIPLINE", "MemoKicker"),
        p("What must be true before capital moves", "MemoTitle"),
        heading("Material assumptions and sensitivities"),
        p("<b>Operating path.</b> Base revenue growth fades from 14% to 5%, gross margin is 86.5%, and operating expenses decline from 67% to 65% of gross profit. These are my analyst assumptions, not company guidance.", "BodyTight"),
        p("<b>Boundaries.</b> Downside and upside remain accounting-linked. The DCF retains FY2025 opening balances; the peer bridge uses June 2026 values. Synopsys remains one qualified peer. The Hexagon layer is separate so filing facts are not blended with assumptions.", "BodyTight"),
        subheading("Market-price burden of proof"),
        expectations_table(),
        Spacer(1, 3),
        subheading("Cycle regimes and acquisition economics"),
        regime_overlay_table(),
        p("The boom case deliberately raises both cash-flow expectations and beta. Hexagon closed February 23, 2026 for <b>$3.101B</b>, including <b>$2.2B cash</b> and <b>3.224M shares</b>; net consideration after acquired cash was <b>$2.946B</b>. The default overlay values the acquired operation at <b>$1.095B</b> and lowers the combined illustration to <b>$78.93 per share</b>. That result is assumption-dependent, not a purchase-accounting restatement.", "BodyTight"),
        heading("The burden of proof"),
        p("The strongest evidence is not any single target. Rather, it is the consistency across the DCF, peer checks, market-implied dashboard, cycle regimes, and acquisition overlay. For $313.04 to work, several checks would need to be wrong in the same direction.", "BodyTight"),
        proof_table(),
        heading("Principal risks, failure conditions, and monitoring triggers"),
        monitoring_table(),
        heading("Action requested and next review point"),
        p("Approve <b>watch/defer and zero allocation</b> at $313.04. Assign the analyst to refresh the DCF, peer set, and bridge after the next two quarterly filings, with an immediate recheck after a material acquisition update, financing change, or a <b>100-basis-point move in WACC</b>. Return to committee only with reconciled acquisition-aware cash flows, current peer evidence, and a price that passes the 15% margin-of-safety rule."),
        p("<b>Source and validation note.</b> Decision inputs are dated through September 1, 2026. Sources include Cadence and Synopsys filings, Cadence's July 27 release, SIA, dated prices, U.S. Treasury rates, and Damodaran datasets. The later Alpha Spread, ValueInvesting.io, and Fair Value Calculator estimates are a labeled post-date audit, not decision inputs. Full tests and named AI uses appear in <b>Validation and AI Use</b>.", "Fine"),
        p("This memo was prepared for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research or financial advice. The judgments and recommendation remain mine.", "Fine"),
    ])
    return story


def main():
    if LEGACY_OUTPUT.exists():
        case_staging = ROOT / "docs" / ".decision-memo-case-normalization.pdf"
        LEGACY_OUTPUT.rename(case_staging)
        case_staging.rename(OUTPUT)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = MemoDoc(str(OUTPUT))
    doc.build(build_story())
    SUBMISSION_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(OUTPUT, SUBMISSION_OUTPUT)
    print(OUTPUT)
    print(SUBMISSION_OUTPUT)


if __name__ == "__main__":
    main()
