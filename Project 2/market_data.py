"""Small public-market data adapter for the Project 2 workbench.

Yahoo Finance's chart endpoint is public but unofficial. The app therefore keeps
the bundled CSV as the reproducible default and labels live results separately.
"""

from __future__ import annotations

import csv
import io
import json
import time
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen


YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{}"
DEFAULT_USER_AGENT = "FIN439-Project2-Student-Workbench/1.0"


class MarketDataError(ValueError):
    """Raised when a public market-data response cannot support the model."""


def _fetch_monthly_series(ticker: str, lookback_years: int, timeout: int) -> dict[str, float]:
    end = int(time.time())
    start = end - int(lookback_years * 365.25 * 24 * 60 * 60)
    query = urlencode(
        {
            "period1": start,
            "period2": end,
            "interval": "1mo",
            "events": "history",
            "includeAdjustedClose": "true",
        }
    )
    request = Request(
        YAHOO_CHART_URL.format(ticker) + "?" + query,
        headers={"User-Agent": DEFAULT_USER_AGENT},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except Exception as error:  # pragma: no cover - depends on the public endpoint
        raise MarketDataError(f"Yahoo Finance request failed for {ticker}: {error}") from error

    chart = payload.get("chart", {})
    if chart.get("error"):
        description = chart["error"].get("description", "unknown Yahoo Finance error")
        raise MarketDataError(f"Yahoo Finance rejected {ticker}: {description}")
    results = chart.get("result") or []
    if not results:
        raise MarketDataError(f"Yahoo Finance returned no history for {ticker}")
    result = results[0]
    timestamps = result.get("timestamp") or []
    indicators = result.get("indicators", {})
    adjusted = (indicators.get("adjclose") or [{}])[0].get("adjclose")
    closes = (indicators.get("quote") or [{}])[0].get("close")
    values = adjusted or closes or []
    series: dict[str, float] = {}
    for timestamp, value in zip(timestamps, values):
        if value is None:
            continue
        date = datetime.fromtimestamp(int(timestamp), tz=timezone.utc).strftime("%Y-%m-%d")
        if float(value) > 0:
            series[date] = float(value)
    if len(series) < 3:
        raise MarketDataError(f"Yahoo Finance returned fewer than three usable monthly prices for {ticker}")
    return series


def fetch_yahoo_monthly_csv(
    tickers: tuple[str, ...] | list[str], lookback_years: int = 5, timeout: int = 15
) -> str:
    """Fetch monthly adjusted close when available, otherwise close, in app CSV shape."""
    symbols = tuple(dict.fromkeys(str(ticker).strip().upper() for ticker in tickers if str(ticker).strip()))
    if not symbols:
        raise MarketDataError("Choose at least one ticker before requesting live data")
    if not 1 <= int(lookback_years) <= 20:
        raise MarketDataError("Yahoo lookback must be between 1 and 20 years")

    histories = {ticker: _fetch_monthly_series(ticker, int(lookback_years), timeout) for ticker in symbols}
    common_dates = set.intersection(*(set(history) for history in histories.values()))
    dates = sorted(common_dates)
    if len(dates) < 25:
        raise MarketDataError(
            f"Only {len(dates)} common monthly observations were returned. At least 25 are needed for a 24-month price screen."
        )

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(("Date", *symbols))
    for date in dates:
        writer.writerow((date, *(f"{histories[ticker][date]:.10f}" for ticker in symbols)))
    return output.getvalue()
