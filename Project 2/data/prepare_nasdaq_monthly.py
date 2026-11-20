"""Convert downloaded Nasdaq daily Close/Last JSON files to a common monthly panel.

Usage: python data/prepare_nasdaq_monthly.py RAW_DIR prices.csv
RAW_DIR contains <ticker>.json files downloaded from the URLs in data/prices-source.md.
The output is price-only: Close/Last is not adjusted for cash distributions.
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path


TICKERS = ("VOO", "VTI", "VNQ", "VWO", "FBTC", "FBND", "FIVA", "SGOV", "TLT", "TIP")


def monthly_panel(raw_dir: Path) -> list[dict[str, str]]:
    by_ticker: dict[str, dict[str, tuple[str, float]]] = {}
    for ticker in TICKERS:
        payload = json.loads((raw_dir / f"{ticker.lower()}.json").read_text())
        if payload.get("data", {}).get("symbol") != ticker:
            raise ValueError(f"Unexpected symbol in {ticker} response")
        rows = payload["data"]["tradesTable"]["rows"]
        months: dict[str, tuple[str, float]] = {}
        for row in rows:
            day = datetime.strptime(row["date"], "%m/%d/%Y").date().isoformat()
            month = day[:7]
            close = float(str(row["close"]).replace("$", "").replace(",", ""))
            if close <= 0:
                raise ValueError(f"Bad {ticker} close for {day}")
            if month not in months or day > months[month][0]:
                months[month] = (day, close)
        by_ticker[ticker] = months

    common = sorted(set.intersection(*(set(months) for months in by_ticker.values())))
    if len(common) < 24:
        raise ValueError(f"Only {len(common)} common months; at least 24 are required")
    if common != [f"{year}-{month:02d}" for year in range(2024, 2027) for month in range(1, 13) if f"{year}-{month:02d}" <= "2026-09"]:
        raise ValueError("Common monthly window differs from the frozen January 2024–September 2026 window")
    output: list[dict[str, str]] = []
    for month in common:
        days = {by_ticker[ticker][month][0] for ticker in TICKERS}
        if len(days) != 1:
            raise ValueError(f"Funds have different final trading days in {month}: {days}")
        output.append({
            "Date": days.pop(),
            **{ticker: f"{by_ticker[ticker][month][1]:.6f}" for ticker in TICKERS},
        })
    return output


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python data/prepare_nasdaq_monthly.py RAW_DIR OUTPUT_CSV")
    rows = monthly_panel(Path(sys.argv[1]))
    with Path(sys.argv[2]).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("Date", *TICKERS), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} monthly closes, {rows[0]['Date']} through {rows[-1]['Date']}")


if __name__ == "__main__":
    main()
