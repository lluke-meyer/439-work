### Record of Discussion

# Peyton and I started off discussing what makes CDNS attractive being the revenue and gross margin as they also tied in to my value drivers. 
# He suggested I focus my value drivers on what makes CDNS unique and I agreed so I'll do research to find better value drivers in the future.
# We then moved on to disscssing his company, Rocketlab's, recent performance and what made him choose it.

# I attached an AI's review of who CDNS is through the lens of what I've done since Week 1.



"""
Lab 12 presentation table for Cadence Design Systems (NASDAQ: CDNS) via AI.

The answers below distinguish sourced facts from analyst assumptions. Dollar
amounts are USD millions unless otherwise stated. The project valuation date is
September 1, 2026.
"""

from textwrap import fill


PRESENTATION_ROWS = [
    (
        "Target selection",
        "I selected Cadence because it is a focused electronic-design automation "
        "company with attractive recurring revenue, strong growth, and valuation "
        "tension worth testing. In FY2025, 80% of revenue was recurring, revenue "
        "grew 14.1%, and remaining performance obligations were $7.8 billion. It "
        "is suitable for analysis because the business has visible contract revenue "
        "but also meaningful judgment around up-front hardware and IP revenue, R&D, "
        "acquisitions, and terminal value. My initial view was 'initiate further "
        "research': the business looked strong, but I had not yet established that "
        "the stock price was justified.",
    ),
    (
        "Company and evidence",
        "Cadence earns money by licensing software and semiconductor IP, selling or "
        "leasing verification hardware, providing maintenance, engineering and cloud "
        "services, and earning IP royalties. FY2025 product and maintenance revenue "
        "was $4,821.6 million, about 91% of $5,296.8 million total revenue; services "
        "were $475.2 million. Revenue was 80% recurring and 20% up-front, so product "
        "delivery and mix affect period-to-period results. My historical base is the "
        "FY2025 10-K covering FY2023-FY2025, reported in USD thousands and converted "
        "to USD millions. I use the Q1 and Q2 2026 10-Qs only as update evidence. The "
        "September 1, 2026 closing share price was $313.04 per share.",
    ),
    (
        "Your pro-forma",
        "History became assumptions as follows: revenue growth fades from 14% in "
        "FY2026 to 5% in FY2030; gross margin is 86.5%; operating expenses decline "
        "from 67% to 65% of gross profit; depreciation is 21.5% of opening PP&E; "
        "annual capex is $142 million; tax is 27%; inventory is 153.5 days; and "
        "deferred revenue is 17.64% of revenue. Revenue drives gross profit and "
        "operating expenses; PP&E drives depreciation; operating income, interest, "
        "and tax drive net income; inventory, deferred revenue, capex, and debt "
        "repayment bridge net income to FCFE; FCFE and the $900 million annual "
        "buyback drive cash and equity. Every forecast balance sheet balances to "
        "$0.0, cash stays above the $500 million floor, and no revolver is drawn. "
        "The major limitations are flat other assets/liabilities and the lack of a "
        "full Hexagon acquisition update.",
    ),
    (
        "Valuation",
        "My primary FCFF DCF starts with $1,668.5 million of FY2025 FCFF, applies "
        "14%, 12%, 10%, 8%, and 5% growth, a 9% WACC, and 3% terminal growth. It "
        "produces enterprise value of $38,515.9 million. Adding $3,001.3 million of "
        "cash and subtracting $2,480.2 million of debt gives $39,037.1 million of "
        "equity value, or $142.83 per diluted share; 77.0% of enterprise value is "
        "terminal value. A separate Lab 10 FCFE model at a 10% cost of equity gives "
        "$77.40 per share, illustrating how cash-flow definition and assumptions "
        "matter. The one-peer P/E check uses Synopsys at 51.595x FY2025 GAAP EPS and "
        "implies $209.47 for CDNS; Siemens is excluded because EDA is not separately "
        "traded. The project-date market close was $313.04. The saved reverse DCF "
        "instead targets the September 9 close of $284.60: no solution exists inside "
        "the tested -5 to +10 percentage-point growth shift because even +10 points "
        "gives only $212.01. Extending the range requires a +17.884-point uniform "
        "shift, or growth of about 31.9%, 29.9%, 27.9%, 25.9%, and 22.9%, while "
        "holding starting FCFF, 9% WACC, 3% terminal growth, cash, debt, shares, and "
        "the base growth path fixed. That is a mechanical result, not a realistic "
        "forecast, because it ignores changing margins, reinvestment, acquisitions, "
        "and risk.",
    ),
    (
        "Sensitivity and drivers",
        "Lab 11 changes one input at a time. Revenue growth is tested at base 14%, "
        "12%, 10%, 8%, 5%, with lower and higher paths two percentage points below "
        "or above each year. The operating-expense ratio is tested at base 67.0% to "
        "65.0%, with paths 0.5 point lower or higher. Across the revenue-growth range, "
        "FY2030 operating profit spans $465.9 million, FY2030 FCFE spans $385.6 "
        "million, and value per share spans $15.71 ($69.84-$85.55). Across the "
        "expense-ratio range, the spans are $73.0 million, $53.3 million, and $2.41 "
        "($76.20-$78.61). Revenue changes sales, gross profit, operating income, net "
        "income, FCFE, and terminal value; the expense ratio begins at gross profit. "
        "Revenue ranks first only over my selected ranges. The ranking does not prove "
        "universal economic importance, assign probabilities, capture interactions, "
        "or show causation outside the model.",
    ),
    (
        "Interpretation",
        "My conditional recommendation is to keep CDNS on the research watchlist, "
        "but not support a purchase at the saved market prices with this evidence. "
        "The $142.83 FCFF DCF and $209.47 single-peer reference are both below the "
        "$313.04 project-date price, and the reverse DCF requires exceptionally high "
        "growth. I would change the recommendation if updated, acquisition-aware cash "
        "flows supported materially higher durable growth and margins, or if the "
        "market price fell enough to create a margin of safety. My view changed from "
        "an open-ended 'initiate research' thesis to 'strong company, unsupported "
        "valuation under the current model.' Next I would investigate organic versus "
        "acquired growth after Hexagon, renewal and up-front revenue mix, the $8.1 "
        "billion Q2 backlog and $4.2 billion next-12-month RPO, acquisition integration "
        "and amortization, an updated June 2026 cash/debt/share bridge, a sourced WACC, "
        "and a broader peer set.",
    ),
]


SOURCES = {
    "FY2025 10-K": (
        "https://www.sec.gov/Archives/edgar/data/813672/"
        "000081367226000016/cdns-20251231.htm"
    ),
    "Q1 2026 10-Q": (
        "https://www.sec.gov/Archives/edgar/data/813672/"
        "000081367226000047/cdns-20260331.htm"
    ),
    "Q2 2026 10-Q": (
        "https://www.sec.gov/Archives/edgar/data/813672/"
        "000081367226000092/cdns-20260630.htm"
    ),
    "Historical price": (
        "https://www.investing.com/equities/"
        "cadence-design-system-inc-historical-data"
    ),
}


def print_table() -> None:
    """Print a readable two-column version of the presentation table."""
    stop_width = max(len(stop) for stop, _ in PRESENTATION_ROWS)
    answer_width = 100
    print(f"{'Stop':<{stop_width}} | Presenter explains and shows")
    print(f"{'-' * stop_width}-+-{'-' * answer_width}")
    for stop, answer in PRESENTATION_ROWS:
        wrapped = fill(answer, width=answer_width).splitlines()
        print(f"{stop:<{stop_width}} | {wrapped[0]}")
        for line in wrapped[1:]:
            print(f"{'':<{stop_width}} | {line}")
        print(f"{'-' * stop_width}-+-{'-' * answer_width}")


if __name__ == "__main__":
    print_table()



# This report was prepared for FIN 43900 as a learning exercise. It is not
# investment research or financial advice. AI assistance was used to draft and
# check the presentation language; the student remains responsible for sources,
# assumptions, judgments, and any remaining errors.
