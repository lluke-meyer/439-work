"""Fetch SEC EDGAR 10-K facts and compute Buffett-style business checks."""

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
    "revenue": (
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
    ),
    "net_income": ("NetIncomeLoss",),
    "operating_cash_flow": ("NetCashProvidedByUsedInOperatingActivities",),
    "capital_spending": (
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets",
    ),
    "equity": ("StockholdersEquity",),
}


def fetch_json(url):
    request = Request(
        url,
        headers={
            "Accept-Encoding": "identity",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.load(response)
    except (HTTPError, URLError) as error:
        raise RuntimeError(f"SEC request failed for {url}: {error}") from error


def resolve_ticker(ticker):
    ticker = ticker.upper().strip()
    companies = fetch_json(SEC_TICKERS_URL)
    for company in companies.values():
        if company["ticker"].upper() == ticker:
            return int(company["cik_str"]), company["title"]
    raise ValueError(f"Ticker not found in SEC company ticker file: {ticker}")


def parse_date(value):
    return date.fromisoformat(value)


def annual_10k_rows(series, end=None):
    rows = []
    for row in series:
        if row.get("form") != "10-K":
            continue
        if end is not None and row.get("end") != end:
            continue
        if not row.get("end"):
            continue
        if row.get("start"):
            duration_days = (parse_date(row["end"]) - parse_date(row["start"])).days
            if not MIN_ANNUAL_DAYS <= duration_days <= MAX_ANNUAL_DAYS:
                continue
        rows.append(row)
    return rows


def choose_tag(us_gaap, candidates, end_dates, flow):
    for tag in candidates:
        fact = us_gaap.get(tag)
        if not fact:
            continue
        units = fact.get("units", {})
        if not units:
            continue
        series = next(iter(units.values()))
        for end in end_dates:
            rows = annual_10k_rows(series, end=end)
            if flow:
                rows = [row for row in rows if row.get("start")]
            if rows:
                return tag
    return None


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
    rows = annual_10k_rows(series, end=end)
    rows = [row for row in rows if not row.get("start")]
    if not rows:
        return None
    return max(rows, key=lambda row: (row.get("filed", ""), row.get("accn", "")))


def metric_series(us_gaap, tag):
    if not tag or tag not in us_gaap:
        return []
    units = us_gaap[tag].get("units", {})
    if not units:
        return []
    return next(iter(units.values()))


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
            flow=metric != "equity",
        )

    if not all_end_dates:
        raise ValueError(f"No 10-K fiscal-year facts found for {ticker.upper()}.")

    end_dates = sorted(all_end_dates)[-5:]
    rows = []
    for end in end_dates:
        result = {"fiscal_year_end": end}
        for metric, tag in selected_tags.items():
            series = metric_series(us_gaap, tag)
            if metric == "equity":
                value_row = choose_instant_value(series, end)
            else:
                value_row = choose_flow_value(series, end)
            result[metric] = numeric_value(value_row)

        if (
            result["operating_cash_flow"] is not None
            and result["capital_spending"] is not None
        ):
            result["owner_earnings"] = (
                result["operating_cash_flow"] - result["capital_spending"]
            )
        else:
            result["owner_earnings"] = None

        if result["net_income"] is not None and result["equity"] not in (None, 0):
            if result["equity"] > 0:
                result["roe_percent"] = result["net_income"] / result["equity"] * 100
            else:
                result["roe_percent"] = None
        else:
            result["roe_percent"] = None
        rows.append(result)

    checks = {
        "roe_15_every_year": check_roe(rows),
        "owner_earnings_positive_every_year": check_owner_earnings_positive(rows),
        "owner_earnings_grew": check_owner_earnings_growth(rows),
    }
    return {
        "ticker": ticker.upper(),
        "company_name": company_name,
        "cik": cik,
        "rows": rows,
        "tags": selected_tags,
        "checks": checks,
    }


def check_roe(rows):
    values = [row["roe_percent"] for row in rows]
    if any(value is None for value in values):
        return "not known"
    return "pass" if all(value >= 15 for value in values) else "fail"


def check_owner_earnings_positive(rows):
    values = [row["owner_earnings"] for row in rows]
    if any(value is None for value in values):
        return "not known"
    return "pass" if all(value > 0 for value in values) else "fail"


def check_owner_earnings_growth(rows):
    values = [row["owner_earnings"] for row in rows]
    if any(value is None for value in values):
        return "not known"
    return "pass" if values[-1] > values[0] else "fail"


def display_value(value):
    if value is None:
        return "not found"
    if isinstance(value, float):
        return f"{value:,.0f}" if value.is_integer() else f"{value:,.1f}"
    return f"{value:,}"


def print_report(report):
    print(f"Ticker: {report['ticker']}")
    print(f"Company: {report['company_name']}")
    print(f"CIK: {report['cik']:010d}")
    print("Data source: SEC EDGAR companyfacts; 10-K filings only")
    print("Units: USD millions, except ROE percentage")
    print("Metric tags:")
    for metric, tag in report["tags"].items():
        print(f"  {metric}: {tag or 'not found'}")
    print("\nFiscal year end | Revenue | Net income | Operating cash flow | Capital spending | Equity | ROE % | Owner earnings")
    for row in report["rows"]:
        values = [
            row["fiscal_year_end"],
            display_value(row["revenue"]),
            display_value(row["net_income"]),
            display_value(row["operating_cash_flow"]),
            display_value(row["capital_spending"]),
            display_value(row["equity"]),
            display_value(row["roe_percent"]),
            display_value(row["owner_earnings"]),
        ]
        print(" | ".join(values))
    print("\nBuffett's checks")
    print(
        "ROE of 15% or more every year: "
        f"{report['checks']['roe_15_every_year']}"
    )
    print(
        "Owner earnings positive every year: "
        f"{report['checks']['owner_earnings_positive_every_year']}"
    )
    print(
        "Owner earnings grew, first year to last: "
        f"{report['checks']['owner_earnings_grew']}"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticker", nargs="?", default="COST")
    args = parser.parse_args()
    report = analyze_ticker(args.ticker)
    print_report(report)


if __name__ == "__main__":
    main()
