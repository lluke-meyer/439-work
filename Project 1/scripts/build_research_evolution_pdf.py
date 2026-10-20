#!/usr/bin/env python3
"""Build the working Research-Evolution PDF for FIN 439 Project 1."""

import shutil
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "research-evolution.pdf"
LEGACY_OUTPUT = ROOT / "docs" / "Research-Evolution.pdf"
SUBMISSION_OUTPUT = ROOT / "submission" / "Research-Evolution.pdf"
RECEIPT_IMAGE = ROOT / "docs" / "evidence" / "edition-a-brightspace-attempt-1.png"

NAVY = colors.HexColor("#102D43")
BLUE = colors.HexColor("#176B87")
ORANGE = colors.HexColor("#D4772C")
PALE_BLUE = colors.HexColor("#EFF5F7")
PALE_ORANGE = colors.HexColor("#F9EEE5")
INK = colors.HexColor("#1F2A30")
MUTED = colors.HexColor("#5E6A70")
LINE = colors.HexColor("#CBD4D8")
LIGHT = colors.HexColor("#EFF5F7")


def register_fonts():
    regular = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
    bold = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("CourseSans", regular))
        pdfmetrics.registerFont(TTFont("CourseSans-Bold", bold))
        return "CourseSans", "CourseSans-Bold"
    return "Helvetica", "Helvetica-Bold"


FONT, FONT_BOLD = register_fonts()


class ResearchDoc(BaseDocTemplate):
    def __init__(self, filename):
        super().__init__(
            filename,
            pagesize=letter,
            leftMargin=0.58 * inch,
            rightMargin=0.58 * inch,
            topMargin=0.52 * inch,
            bottomMargin=0.52 * inch,
            title="Research Evolution - Cadence Design Systems",
            author="Luke Meyer",
            subject="FIN 43900 Project 1",
        )
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="main",
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        self.addPageTemplates(PageTemplate(id="content", frames=[frame], onPage=self.decorate))

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
        canvas.line(doc.leftMargin, 0.36 * inch, letter[0] - doc.rightMargin, 0.36 * inch)
        canvas.setFont(FONT, 6.7)
        canvas.setFillColor(MUTED)
        canvas.drawString(doc.leftMargin, 0.19 * inch, "FIN 43900 Project 1 | Cadence Design Systems")
        canvas.drawRightString(letter[0] - doc.rightMargin, 0.19 * inch, f"Research Evolution | {doc.page} of 5")
        canvas.restoreState()


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        "Kicker",
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
        "DocTitle",
        fontName=FONT_BOLD,
        fontSize=20,
        leading=23,
        textColor=NAVY,
        spaceAfter=5,
    )
)
styles.add(
    ParagraphStyle(
        "Subtitle",
        fontName=FONT,
        fontSize=10.5,
        leading=14,
        textColor=MUTED,
        spaceAfter=10,
    )
)
styles.add(
    ParagraphStyle(
        "H1x",
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
        "H2x",
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
        "Bodyx",
        fontName=FONT,
        fontSize=8.35,
        leading=10.8,
        textColor=INK,
        spaceAfter=4,
    )
)
styles.add(
    ParagraphStyle(
        "Smallx",
        fontName=FONT,
        fontSize=7.4,
        leading=9.7,
        textColor=INK,
    )
)
styles.add(
    ParagraphStyle(
        "SmallBold",
        fontName=FONT_BOLD,
        fontSize=7.4,
        leading=9.7,
        textColor=INK,
    )
)
styles.add(
    ParagraphStyle(
        "TableHeader",
        fontName=FONT_BOLD,
        fontSize=7.4,
        leading=9.7,
        textColor=colors.white,
    )
)
styles.add(
    ParagraphStyle(
        "Bulletx",
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
        "Callout",
        fontName=FONT_BOLD,
        fontSize=10.5,
        leading=14,
        textColor=NAVY,
        alignment=TA_CENTER,
    )
)
styles.add(
    ParagraphStyle(
        "Fine",
        fontName=FONT,
        fontSize=6.9,
        leading=8.8,
        textColor=MUTED,
    )
)


def p(text, style="Bodyx"):
    return Paragraph(text, styles[style])


def bullet(text):
    return Paragraph(f"- {text}", styles["Bulletx"])


def section(title):
    return Paragraph(title, styles["H1x"])


def subsection(title):
    return Paragraph(title, styles["H2x"])


def callout(text, background=PALE_BLUE, border=BLUE):
    table = Table([[p(text, "Callout")]], colWidths=[7.34 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), background),
                ("BOX", (0, 0), (-1, -1), 1, border),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    return table


def metric_cards():
    data = [
        [p("MARKET PRICE", "SmallBold"), p("DCF RANGE", "SmallBold"), p("BASE VALUE", "SmallBold")],
        [p("<b>$313.04</b>", "Callout"), p("<b>$57.20-$111.52</b>", "Callout"), p("<b>$83.34</b>", "Callout")],
        [p("September 1, 2026", "Fine"), p("Low to high", "Fine"), p("Per share", "Fine")],
    ]
    table = Table(data, colWidths=[2.446 * inch] * 3, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, LINE),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def evidence_table():
    header = [
        p("Item", "TableHeader"),
        p("Edition A", "TableHeader"),
        p("Edition B", "TableHeader"),
        p("Primary driver", "TableHeader"),
        p("Evidence or test", "TableHeader"),
    ]
    rows = [
        [
            p("Thesis / recommendation", "SmallBold"),
            p('"Initiate valuation procedures" because Cadence was likely to pass the screens.', "Smallx"),
            p("<b>Watch/defer.</b> Do not buy at $313.04.", "Smallx"),
            p("<b>Mixed:</b> own analysis, course instruction, and AI-assisted model development.", "Smallx"),
            p("DCF range $57.20-$111.52; base $83.34; P/E reference $209.47; EV/revenue reference $189.64; reverse DCF requires +32.215 percentage points of annual revenue growth.", "Smallx"),
        ],
        [
            p("Data / source choice", "SmallBold"),
            p("FY2025 10-K evidence for shares, cash, debt, revenue, and EPS.", "Smallx"),
            p("FY2025 10-K inputs plus September 1 price, operating evidence, frozen output, and validation results.", "Smallx"),
            p("<b>Mixed:</b> own analysis and course instruction.", "Smallx"),
            p("Base year reconciled; price is dated to the valuation boundary; material inputs and limits are disclosed.", "Smallx"),
        ],
        [
            p("Assumption / model design", "SmallBold"),
            p('"CDS\'s business model is not imitable" and a plan to review FCF, EPS, and other metrics.', "Smallx"),
            p("Five-year three-statement pro-forma linked to FCFF DCF, calculated decision rules, market-implied tests, cycle regimes, acquisition overlay, sensitivity, and bridge.", "Smallx"),
            p("<b>Mixed:</b> course instruction, own analysis, peer challenge, and disclosed AI assistance.", "Smallx"),
            p("Statements tied; decision thresholds, price reconciliation, regime ordering, acquisition monotonicity, bridge, and fail-loud tests passed.", "Smallx"),
        ],
        [
            p("Risk / limitation / uncertainty", "SmallBold"),
            p("No inside information; partner asked whether the business model would remain sustainable if the AI bubble popped.", "Smallx"),
            p("Operationally resilient but valuation-fragile. Hexagon is a separate overlay, not a full statement rebuild; Synopsys remains one qualified peer.", "Smallx"),
            p("<b>Mixed:</b> own economic interpretation, peer challenge, and disclosed AI assistance.", "Smallx"),
            p("74.1% terminal-value share; price requires +32.215 growth points or 4.871% WACC; bounded value $203.95; cycle reversal $54.69; Hexagon combined illustration $78.93.", "Smallx"),
        ],
    ]
    table = Table(
        [header] + rows,
        colWidths=[0.96 * inch, 1.33 * inch, 1.42 * inch, 1.26 * inch, 2.37 * inch],
        repeatRows=1,
        hAlign="LEFT",
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.45, LINE),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def build_story():
    story = [
        p("RESEARCH OWNERSHIP", "Kicker"),
        p("Research Evolution", "DocTitle"),
        p("Cadence Design Systems (NASDAQ: CDNS) | Valuation date: September 1, 2026", "Subtitle"),
        callout("EDITION A PRESERVED FROM THE BRIGHTSPACE TEXT-ENTRY CHECKPOINT", PALE_BLUE, BLUE),
        Spacer(1, 8),
        section("Brightspace checkpoint evidence"),
        p("Brightspace did not provide a PDF-upload option. The baseline of record was submitted as a timed text entry, so this document preserves the result screen and the original response wording. The supervised attempt is recorded as observed pre-AI evidence.", "Bodyx"),
        Spacer(1, 5),
        Table(
            [
                [p("Brightspace object", "SmallBold"), p("Lab 03 - Project 1 Valuation Edition A - Results", "Smallx")],
                [p("Receipt or attempt identifier", "SmallBold"), p("Attempt 1 of 3", "Smallx")],
                [p("Attempt window", "SmallBold"), p("September 1, 2026, 2:34 PM-2:37 PM EDT", "Smallx")],
                [p("Completion timestamp", "SmallBold"), p("September 1, 2026, 2:37 PM EDT", "Smallx")],
                [p("Result", "SmallBold"), p("25/25 - 100%", "Smallx")],
                [p("Submission format", "SmallBold"), p("Brightspace text entry; no PDF upload was available", "Smallx")],
            ],
            colWidths=[2.6 * inch, 4.55 * inch],
            style=TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, LINE),
                    ("BACKGROUND", (0, 0), (0, -1), LIGHT),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ]
            ),
        ),
        Spacer(1, 12),
        Image(str(RECEIPT_IMAGE), width=7.34 * inch, height=2.66 * inch),
        Spacer(1, 7),
        p("Evidence image preserved at docs/evidence/edition-a-brightspace-attempt-1.png.", "Fine"),
        PageBreak(),
        p("EDITION A BASELINE", "Kicker"),
        p("Edition A", "DocTitle"),
        p("Preserved Brightspace text-entry baseline", "Subtitle"),
        p("The wording below is preserved from the original Lab 03 response supplied by the student on October 17, 2026. No spelling, grammar, or analytical revisions have been made inside Edition A.", "Fine"),
        Spacer(1, 6),
        subsection("Project 1 Edition A"),
        p("<b>Decision and intended user</b>", "SmallBold"),
        p("Based on Cadence Design Systems' (CDS in text) valuation, we, being junior financial analyst's, will discover whether Cadence is a good investment, or not.", "Smallx"),
        p("<b>Company and valuation date</b>", "SmallBold"),
        p("- Company: Cadence Design Systems<br/>- Ticker: CDNS<br/>- Valuation date: 09-01-2026<br/>- Intended output unit: $", "Smallx"),
        p("<b>Initial thesis</b>", "SmallBold"),
        p("Initiate valuation procedures and Cadence is likely to pass my screens. Cadence was selected as the valuation target; it was not selected because it passed a valuation screen as we did not complete this in Week 1.", "Smallx"),
        p("<b>Known evidence and sources</b>", "SmallBold"),
        p("- Entity: Cadence Design Systems, Inc.<br/>- Filing/form and accession number: Form 10-K<br/>- Reporting period: FY ended 12-31-2025<br/>- Filing date: 02-19-2026<br/>- Currency and units: US dollars, financial statements in thousands.<br/>- Diluted share evidence: Weighted-average common shares used to calculate diluted net income per share were 273,312 thousand. Diluted net income per share was $4.06. Source: Note 13, Net Income Per Share, and Consolidated Income Statements.<br/>- Cash: Cash and cash equivalents were $3,001.317 million. Source: Consolidated Balance Sheets<br/>- Debt: Long-term debt had a carrying value of $2,480.150 million. Source: Consolidated Balance Sheets and Note 5, Debt.<br/>- Operating-value driver: Total revenue was $5,296.759 million, consisting of $4,821.589 million of product and maintenance revenue and $475.170 million of services revenue. Source: Consolidated Income Statements.", "Smallx"),
        p("<b>Consequential assumptions</b>", "SmallBold"),
        p("The assumptions most capable of changing the decision below:<br/>- CDS's business model is not imitable.", "Smallx"),
        p("<b>Unknowns</b>", "SmallBold"),
        p("I do not have inside information that could help predict future performance of CDS.", "Smallx"),
        p("<b>Research plan</b>", "SmallBold"),
        p("I want to go more in-depth and assess CDS's FCF, EPS, and a wide swath of metrics to see if the valuation passes.", "Smallx"),
        p("<b>Partner falsification question</b>", "SmallBold"),
        p("Is CDS's business model sustainable if the AI bubble were to pop?", "Smallx"),
        subsection("Dated correction addendum"),
        p("<b>October 17, 2026:</b> \"CDS\" in Edition A referred to Cadence Design Systems. The company's ticker is <b>CDNS</b>. Edition B also clarifies that the intended output is <b>U.S. dollars per diluted share</b>, rather than dollars generally. Source: the ticker field in Edition A, the cover page of Cadence's FY2025 Form 10-K, and the final model's per-share convention. These corrections clarify the company identifier and unit; they do not change the original thesis or any valuation result.", "Smallx"),
        Spacer(1, 6),
        callout("I, Luke Meyer, can attest that Edition A was completed without the help of AI.", PALE_ORANGE, ORANGE),
        PageBreak(),
        p("CURRENT POSITION", "Kicker"),
        p("Edition B", "DocTitle"),
        p("After project-specific research and disclosed AI assistance", "Subtitle"),
        section("Current decision and intended user"),
        callout("WATCH / DEFER - DO NOT BUY CDNS AT THE SEPTEMBER 1, 2026 MARKET PRICE", PALE_BLUE, BLUE),
        Spacer(1, 9),
        p("My recommendation is <b>watch/defer</b> for a buy-side investment committee that does not currently own CDNS. I would not initiate a position at the September 1, 2026 market price of <b>$313.04</b>."),
        metric_cards(),
        Spacer(1, 8),
        p("The integrated FCFF DCF produced a range of <b>$57.20 to $111.52 per share</b>, with a base value of <b>$83.34</b> after replacing the unsupported 9% WACC with a sourced 10% estimate. Synopsys evidence implied <b>$209.47 per share</b> from P/E and <b>$189.64 per share</b> from EV/TTM revenue. Both cross-checks remain below the market price."),
        section("What the research now says"),
        bullet("<b>Strong business, unsupported price:</b> Neither the DCF nor the current P/E cross-check supports the market price."),
        bullet("<b>Operationally resilient:</b> Recurring revenue was 80% of FY2025 revenue, which should soften short-run demand shocks."),
        bullet("<b>Valuation-fragile:</b> 74.1% of base enterprise value comes from terminal value. Raising WACC from 10% to 11% lowered value per share from $83.34 to $72.90, or 12.5%, with no operating change."),
        bullet("<b>Economically exposed:</b> Demand still depends on customer chip-design activity and R&amp;D spending. Cadence's R&amp;D expense was 33% of FY2025 revenue, so costs may not fall as quickly as revenue in a downturn."),
        bullet("<b>Demanding expectations:</b> Price requires +32.215 growth points or a 4.871% WACC. Even the bounded challenge reaches only $203.95. CDNS also traded at a 63.8% EV/revenue premium to Synopsys."),
        bullet("<b>Cycle and acquisition discipline:</b> Joint operating/beta regimes produce $93.48, $83.20, and $54.69. A separate default Hexagon overlay values the acquired operation at $1.095B and the combined illustration at $78.93 per share."),
        PageBreak(),
        p("CHANGE EVIDENCE", "Kicker"),
        p("A-to-B Evidence", "DocTitle"),
        p("Changes must be tied to observable evidence, not change for its own sake.", "Subtitle"),
        evidence_table(),
        Spacer(1, 8),
        p("Edition A wording is drawn directly from the original Lab 03 text supplied by the student. The Brightspace result screen and Attempt 1 timing provide the available baseline evidence of record.", "Fine"),
        PageBreak(),
        p("FINAL RECONCILIATION", "Kicker"),
        p("Decision Reconciliation", "DocTitle"),
        subsection("What changed from Edition A to Edition B, and why?"),
        p("My view changed from an initial <b>initiate</b> research thesis to <b>watch/defer</b>. The company still looks operationally strong, but the valuation work did not support the September 1 market price. The biggest change was moving from a filing-based research plan to an integrated decision system with a defendable range, calculated committee rules, market-implied tests, correlated cycle regimes, a separate acquisition overlay, and visible accounting checks."),
        p("The economics changed how I describe the risk, not the valuation method. CDNS has recurring revenue and sustained customer R&amp;D demand, but most DCF value sits far in the future. The new regimes show that a boom can raise cash flows and beta together, while the Hexagon overlay shows that strategic fit does not automatically establish value creation. I would reconsider only if rebuilt acquisition-aware cash flows and stronger peer evidence support a value range near the market price with a margin of safety."),
        subsection("Remaining analytical boundary before final submission"),
        bullet("Preserve the boundary between the FY2025-based DCF, the Hexagon overlay, and the 2026 peer bridge; do not silently mix facts and assumptions."),
        subsection("Evidence locations"),
        p("Repository: outputs/visible-output.txt; outputs/validation-evidence.txt; docs/validation-and-ai-use.md; docs/wacc-and-ev.md; project1_model.py; tests/test_model.py.", "Smallx"),
        p("Cadence FY2025 Form 10-K: https://www.sec.gov/Archives/edgar/data/813672/000081367226000016/cdns-20251231.htm", "Smallx"),
        p("September 1, 2026 price history: https://chartexchange.com/symbol/nasdaq-cdns/historical/", "Smallx"),
        Spacer(1, 12),
        p("This report was prepared for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research or financial advice. Material AI assistance and its independent checks are disclosed in docs/validation-and-ai-use.md. The judgment remains mine.", "Fine"),
    ]
    return story


def main():
    if LEGACY_OUTPUT.exists():
        case_staging = ROOT / "docs" / ".research-evolution-case-normalization.pdf"
        LEGACY_OUTPUT.rename(case_staging)
        case_staging.rename(OUTPUT)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = ResearchDoc(str(OUTPUT))
    doc.build(build_story())
    SUBMISSION_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(OUTPUT, SUBMISSION_OUTPUT)
    print(OUTPUT)
    print(SUBMISSION_OUTPUT)


if __name__ == "__main__":
    main()
