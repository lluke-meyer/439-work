"""Curated public-source snapshot used by the Lab 18 Buffett Test Plus panel.

The original Buffett test is live SEC EDGAR data. This overlay is deliberately kept as a dated,
source-linked snapshot because analyst targets, valuation models, and news interpretations change.
It is not averaged into the SEC checks.
"""

from __future__ import annotations


RETRIEVED_ON = "2026-11-03"

PUBLIC_RESEARCH = {
    "COST": {
        "retrieved_on": RETRIEVED_ON,
        "analyst": {
            "source": "StockAnalysis / S&P Global consensus",
            "url": "https://stockanalysis.com/stocks/cost/forecast/",
            "consensus": "Buy",
            "analyst_count": 41,
            "current_price": 1021.50,
            "target_low": 770.00,
            "target_average": 1068.00,
            "target_median": 1065.00,
            "target_high": 1315.00,
            "upside_percent": 4.51,
            "read": "Positive analyst consensus, but only modest average upside at the snapshot price.",
        },
        "rating_mix": {
            "source": "MarketBeat",
            "url": "https://www.marketbeat.com/stocks/NASDAQ/COST/forecast/",
            "as_of": "2026-11-01",
            "counts": {"Strong Buy": 1, "Buy": 24, "Hold": 8, "Sell": 1},
            "read": "A separate 34-rating snapshot is also positive, but its provider count differs from the 41-analyst consensus above.",
        },
        "intrinsic_value": [
            {
                "source": "StocksXray",
                "url": "https://www.stocksxray.com/us/cost",
                "as_of": "2026-11-02",
                "method": "Composite of 15 valuation models",
                "value": 801.00,
                "range_low": 666.00,
                "range_high": 955.00,
                "read": "Below the snapshot price; the site labels the shares overvalued by its models.",
            },
            {
                "source": "MiniValuator",
                "url": "https://minivaluator.com/dcf/cost",
                "as_of": "2026-11-02",
                "method": "Base-case DCF",
                "value": 718.93,
                "range_low": 603.05,
                "range_high": 850.48,
                "read": "Below the snapshot price; the source emphasizes sensitivity to growth and discount-rate assumptions.",
            },
            {
                "source": "ValueInvesting.io",
                "url": "https://valueinvesting.io/COST/valuation/intrinsic-value",
                "as_of": "2026-10-16",
                "method": "Published intrinsic-value model",
                "value": 1800.81,
                "range_low": None,
                "range_high": None,
                "read": "A high outlier above the snapshot price; it demonstrates model dependence rather than consensus.",
            },
        ],
        "news": [
            {
                "source": "Costco Investor Relations",
                "date": "2026-09-24",
                "title": "Fiscal 2026 operating results",
                "url": "https://investor.costco.com/news/news-details/2026/Costco-Wholesale-Corporation-Reports-Fourth-Quarter-and-Fiscal-Year-2026-Operating-Results/default.aspx",
                "direction": "Supports",
                "takeaway": "Fiscal-year net sales rose 10.1%; digital comparable sales rose 20.7%; membership-fee income rose to $5.907 billion from $5.323 billion.",
                "economic_read": "Demand, digital engagement, and recurring membership economics remain strong.",
            },
            {
                "source": "S&P Global Market Intelligence",
                "date": "2026-09-29",
                "title": "Behind the Earnings Call: Costco Q4 2026",
                "url": "https://www.spglobal.com/market-intelligence/en/news-insights/research/2026/10/behind-the-earnings-call-costco-q4-2026",
                "direction": "Supports",
                "takeaway": "Paid members reached 84.1 million, renewal rates were 92.3% in the U.S. and Canada and 89.8% worldwide, and Costco opened 25 net new warehouses in fiscal 2026.",
                "economic_read": "Scale and renewal behavior support a durable membership moat, while expansion requires continued execution.",
            },
            {
                "source": "Axios",
                "date": "2026-03-05",
                "title": "Costco says it will pass on tariff recoveries to members",
                "url": "https://www.axios.com/2026/03/05/costco-earnings-tariff-refunds",
                "direction": "Watch",
                "takeaway": "Costco said it absorbed some tariff costs and planned to return recovered tariff charges through member value, while management described the future tariff impact as fluid.",
                "economic_read": "The value proposition is a moat, but absorbing or rebating trade costs can pressure merchandise economics.",
            },
        ],
        "plus_read": {
            "label": "Quality confirmed; valuation caution",
            "summary": "The SEC-only Buffett test supports Costco as a high-quality business. Analyst sentiment is positive, but the average target implies only modest upside and two of three public valuation snapshots sit below the market price. News supports membership economics and demand while leaving tariff-related margin risk open.",
            "decision": "Keep the business-quality verdict, but require a better price or stronger valuation evidence before turning it into a purchase decision.",
        },
    }
}


def get_public_research(ticker):
    """Return a dated public-source overlay, or None when no snapshot is curated."""
    return PUBLIC_RESEARCH.get(ticker.upper().strip())
