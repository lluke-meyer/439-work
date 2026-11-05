"""Fetch SEC EDGAR 10-K facts and compute a three-investor legend panel."""

from __future__ import annotations

import argparse
import json
import os
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
DEFAULT_USER_AGENT = "Luke Meyer <lmeyer@purdue.edu>"
USER_AGENT = os.environ.get("SEC_USER_AGENT", DEFAULT_USER_AGENT)
MIN_ANNUAL_DAYS = 300
MAX_ANNUAL_DAYS = 380

METRIC_TAGS = {
    "revenue": ("RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"),
    "net_income": ("NetIncomeLoss",),
    "operating_cash_flow": ("NetCashProvidedByUsedInOperatingActivities",),
    "capital_spending": (
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets",
    ),
    "equity": ("StockholdersEquity",),
    "assets_current": ("AssetsCurrent",),
    "liabilities": ("Liabilities",),
    "liabilities_current": ("LiabilitiesCurrent",),
}


def fetch_json(url):
    request = Request(
        url,
        headers={"Accept-Encoding": "identity", "User-Agent": USER_AGENT},
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.load(response)
    except (HTTPError, URLError) as error:
        raise RuntimeError(f"SEC request failed for {url}: {error}") from error


def resolve_ticker(ticker):
    normalized = ticker.upper().strip()
    companies = fetch_json(SEC_TICKERS_URL)
    for company in companies.values():
        if company["ticker"].upper() == normalized:
            return int(company["cik_str"]), company["title"]
    raise ValueError(f"Ticker not found in SEC company ticker file: {normalized}")


def parse_date(value):
    return date.fromisoformat(value)


def annual_10k_rows(series, end=None):
    rows = []
    for row in series:
        if row.get("form") != "10-K" or not row.get("end"):
            continue
        if end is not None and row.get("end") != end:
            continue
        if row.get("start"):
            duration_days = (parse_date(row["end"]) - parse_date(row["start"])).days
            if not MIN_ANNUAL_DAYS <= duration_days <= MAX_ANNUAL_DAYS:
                continue
        rows.append(row)
    return rows


def choose_tag(us_gaap, candidates, end_dates, flow):
    end_dates = sorted(end_dates)[-5:]
    best_tag = None
    best_coverage = -1
    for tag in candidates:
        fact = us_gaap.get(tag)
        if not fact:
            continue
        coverage = 0
        for series in fact.get("units", {}).values():
            for end in end_dates:
                rows = annual_10k_rows(series, end=end)
                if flow:
                    rows = [row for row in rows if row.get("start")]
                if rows:
                    coverage += 1
        if coverage > best_coverage:
            best_tag = tag
            best_coverage = coverage
    return best_tag


def choose_flow_value(series, end):
    rows = [row for row in annual_10k_rows(series, end=end) if row.get("start")]
    if not rows:
        return None
    rows.sort(
        key=lambda row: (
            abs((parse_date(row["end"]) - parse_date(row["start"])).days - 365),
            row.get("filed", ""),
            row.get("accn", ""),
        )
    )
    best_duration = abs(
        (parse_date(rows[0]["end"]) - parse_date(rows[0]["start"])).days - 365
    )
    same_period = [
        row
        for row in rows
        if abs((parse_date(row["end"]) - parse_date(row["start"])).days - 365)
        == best_duration
    ]
    return max(same_period, key=lambda row: (row.get("filed", ""), row.get("accn", "")))


def choose_instant_value(series, end):
    rows = [row for row in annual_10k_rows(series, end=end) if not row.get("start")]
    if not rows:
        return None
    return max(rows, key=lambda row: (row.get("filed", ""), row.get("accn", "")))


def metric_series(us_gaap, tag):
    if not tag or tag not in us_gaap:
        return []
    units = us_gaap[tag].get("units", {})
    return next(iter(units.values())) if units else []


def numeric_value(row):
    return None if row is None else row.get("val") / 1_000_000


def analyze_ticker(ticker):
    cik, company_name = resolve_ticker(ticker)
    companyfacts = fetch_json(SEC_FACTS_URL.format(cik=cik))
    us_gaap = companyfacts.get("facts", {}).get("us-gaap", {})

    selected_tags = {}
    all_end_dates = set()
    for metric, candidates in METRIC_TAGS.items():
        for candidate in candidates:
            fact = us_gaap.get(candidate)
            if not fact:
                continue
            for unit_rows in fact.get("units", {}).values():
                all_end_dates.update(
                    row["end"]
                    for row in unit_rows
                    if row.get("form") == "10-K" and row.get("end")
                )
        selected_tags[metric] = choose_tag(
            us_gaap,
            candidates,
            sorted(all_end_dates),
            flow=metric in {"revenue", "net_income", "operating_cash_flow", "capital_spending"},
        )

    if not all_end_dates:
        raise ValueError(f"No 10-K fiscal-year facts found for {ticker.upper()}.")

    end_dates = sorted(all_end_dates)[-5:]
    rows = []
    for end in end_dates:
        result = {"fiscal_year_end": end}
        for metric, tag in selected_tags.items():
            series = metric_series(us_gaap, tag)
            value_row = (
                choose_flow_value(series, end)
                if metric in {"revenue", "net_income", "operating_cash_flow", "capital_spending"}
                else choose_instant_value(series, end)
            )
            result[metric] = numeric_value(value_row)

        if result["operating_cash_flow"] is not None and result["capital_spending"] is not None:
            result["owner_earnings"] = result["operating_cash_flow"] - result["capital_spending"]
        else:
            result["owner_earnings"] = None

        if result["assets_current"] is not None and result["liabilities_current"] not in (None, 0):
            result["current_ratio"] = result["assets_current"] / result["liabilities_current"]
        else:
            result["current_ratio"] = None

        if result["liabilities"] is not None and result["equity"] not in (None, 0):
            result["liabilities_to_equity"] = result["liabilities"] / result["equity"]
        else:
            result["liabilities_to_equity"] = None

        if result["net_income"] is not None and result["equity"] not in (None, 0):
            result["roe_percent"] = (
                result["net_income"] / result["equity"] * 100
                if result["equity"] > 0
                else None
            )
        else:
            result["roe_percent"] = None
        rows.append(result)

    checks = {
        "Buffett": {
            "ROE of 15% or more every year": check_all(rows, "roe_percent", lambda value: value >= 15),
            "Owner earnings positive every year": check_all(rows, "owner_earnings", lambda value: value > 0),
            "Owner earnings grew, first year to last": check_growth(rows, "owner_earnings"),
        },
        "Cathie Wood": {
            "Revenue grew, first year to last": check_growth(rows, "revenue"),
            "Net income grew, first year to last": check_growth(rows, "net_income"),
            "Operating cash flow positive every year": check_all(
                rows, "operating_cash_flow", lambda value: value > 0
            ),
        },
        "Michael Burry": {
            "Operating cash flow at least net income every year": check_pair_all(
                rows, "operating_cash_flow", "net_income", lambda cash, income: cash >= income
            ),
            "Liabilities no more than twice equity, latest year": check_latest_ratio(
                rows, "liabilities_to_equity", 2
            ),
        },
    }
    return {
        "ticker": ticker.upper().strip(),
        "company_name": company_name,
        "cik": cik,
        "rows": rows,
        "tags": selected_tags,
        "checks": checks,
        "thresholds": {"roe_percent": 15, "liabilities_to_equity": 2, "current_ratio_probe": 2},
    }


def check_all(rows, key, predicate):
    values = [row.get(key) for row in rows]
    if any(value is None for value in values):
        return "not known"
    return "pass" if all(predicate(value) for value in values) else "fail"


def check_pair_all(rows, left_key, right_key, predicate):
    pairs = [(row.get(left_key), row.get(right_key)) for row in rows]
    if any(left is None or right is None for left, right in pairs):
        return "not known"
    return "pass" if all(predicate(left, right) for left, right in pairs) else "fail"


def check_growth(rows, key):
    values = [row.get(key) for row in rows]
    if any(value is None for value in values):
        return "not known"
    return "pass" if values[-1] > values[0] else "fail"


def check_latest_ratio(rows, key, maximum):
    value = rows[-1].get(key)
    if value is None:
        return "not known"
    return "pass" if value <= maximum else "fail"


def display_value(value):
    if value is None:
        return "not found"
    if isinstance(value, float):
        return f"{value:,.0f}" if value.is_integer() else f"{value:,.2f}"
    return f"{value:,}"


def format_row(row):
    return {
        "Fiscal year end": row["fiscal_year_end"],
        "Revenue": display_value(row["revenue"]),
        "Net income": display_value(row["net_income"]),
        "Operating cash flow": display_value(row["operating_cash_flow"]),
        "Capital spending": display_value(row["capital_spending"]),
        "Owner earnings": display_value(row["owner_earnings"]),
        "Equity": display_value(row["equity"]),
        "Assets current": display_value(row["assets_current"]),
        "Liabilities": display_value(row["liabilities"]),
        "Liabilities current": display_value(row["liabilities_current"]),
        "Current ratio": display_value(row["current_ratio"]),
        "Liabilities / equity": display_value(row["liabilities_to_equity"]),
        "ROE %": display_value(row["roe_percent"]),
    }


def print_report(report):
    print(f"Ticker: {report['ticker']}")
    print(f"Company: {report['company_name']}")
    print(f"CIK: {report['cik']:010d}")
    print("Data source: SEC EDGAR companyfacts; 10-K filings only")
    print("Units: USD millions; ratios and ROE are percentages/ratios")
    print("Metric tags:")
    for metric, tag in report["tags"].items():
        print(f"  {metric}: {tag or 'not found'}")
    headers = list(format_row(report["rows"][0]).keys())
    print("\n" + " | ".join(headers))
    for row in report["rows"]:
        print(" | ".join(format_row(row).values()))
    print("\nThresholds printed for memo validation:")
    print("  Buffett ROE threshold: 15%")
    print("  Michael Burry liabilities/equity threshold: 2")
    print("  Current-ratio sensitivity thresholds: 2 and 1")
    print("\nPanel checks")
    for investor, checks in report["checks"].items():
        for label, status in checks.items():
            print(f"{investor} | {label}: {status}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticker", nargs="?", default="COST")
    args = parser.parse_args()
    print_report(analyze_ticker(args.ticker))


if __name__ == "__main__":
    main()
