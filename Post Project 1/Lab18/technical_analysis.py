"""Public daily-price technical checks for the Lab 18 research overlay."""

from __future__ import annotations

import json
from datetime import date, datetime
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
YAHOO_HISTORY_URL = "https://finance.yahoo.com/quote/{ticker}/history/"
USER_AGENT = "FIN43900-Lab18-technical-overlay"


def fetch_daily_history(ticker):
    """Fetch one year of daily closes and volumes from Yahoo Finance's public chart endpoint."""
    url = YAHOO_CHART_URL.format(ticker=quote(ticker.upper().strip()))
    request = Request(
        f"{url}?range=1y&interval=1d&events=div%2Csplits",
        headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"},
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except (HTTPError, URLError) as error:
        raise RuntimeError(f"Yahoo Finance request failed for {ticker.upper()}: {error}") from error

    chart = payload.get("chart", {})
    if chart.get("error"):
        raise RuntimeError(f"Yahoo Finance returned an error for {ticker.upper()}: {chart['error']}")
    results = chart.get("result") or []
    if not results:
        raise RuntimeError(f"Yahoo Finance returned no daily history for {ticker.upper()}.")

    result = results[0]
    timestamps = result.get("timestamp", [])
    quote_rows = (result.get("indicators", {}).get("quote") or [{}])[0]
    closes = quote_rows.get("close", [])
    volumes = quote_rows.get("volume", [])
    rows = []
    for timestamp, close, volume in zip(timestamps, closes, volumes):
        if close is None:
            continue
        rows.append(
            {
                "date": datetime.fromtimestamp(timestamp).date().isoformat(),
                "close": float(close),
                "volume": int(volume) if volume is not None else None,
            }
        )
    if len(rows) < 61:
        raise RuntimeError(f"Only {len(rows)} daily closes were available; 61 are required.")
    return rows


def simple_average(values):
    return sum(values) / len(values)


def moving_average(values, window):
    if len(values) < window:
        return None
    return simple_average(values[-window:])


def percent_change(values, lookback):
    if len(values) <= lookback:
        return None
    return (values[-1] / values[-lookback - 1] - 1) * 100


def rsi(values, window=14):
    if len(values) <= window:
        return None
    changes = [values[index] - values[index - 1] for index in range(1, len(values))]
    recent = changes[-window:]
    gains = [change for change in recent if change > 0]
    losses = [-change for change in recent if change < 0]
    average_gain = sum(gains) / window
    average_loss = sum(losses) / window
    if average_loss == 0:
        return 100.0
    relative_strength = average_gain / average_loss
    return 100 - (100 / (1 + relative_strength))


def trend_label(current_price, sma30, sma60, momentum30, momentum60):
    bullish = (
        current_price > sma30
        and sma30 > sma60
        and momentum30 > 0
        and momentum60 > 0
    )
    bearish = (
        current_price < sma30
        and sma30 < sma60
        and momentum30 < 0
        and momentum60 < 0
    )
    if bullish:
        return "Bullish trend"
    if bearish:
        return "Bearish trend"
    return "Mixed trend"


def signal_for_distance(distance_percent):
    return "Above" if distance_percent >= 0 else "Below"


def build_technical_snapshot(ticker, rows):
    closes = [row["close"] for row in rows]
    current_price = closes[-1]
    sma30 = moving_average(closes, 30)
    sma60 = moving_average(closes, 60)
    momentum30 = percent_change(closes, 30)
    momentum60 = percent_change(closes, 60)
    rsi14 = rsi(closes)
    distance30 = (current_price / sma30 - 1) * 100
    distance60 = (current_price / sma60 - 1) * 100
    rsi_signal = "Overbought" if rsi14 >= 70 else "Oversold" if rsi14 <= 30 else "Neutral"

    chart_rows = []
    for index, row in enumerate(rows):
        close_history = closes[: index + 1]
        chart_rows.append(
            {
                "Date": row["date"],
                "Close": row["close"],
                "30-day SMA": moving_average(close_history, 30),
                "60-day SMA": moving_average(close_history, 60),
            }
        )

    checks = [
        {
            "Check": "Price vs. 30-day SMA",
            "Reading": f"${current_price:,.2f} vs. ${sma30:,.2f}",
            "Signal": signal_for_distance(distance30),
            "Detail": f"{distance30:+.2f}% from the 30-day average",
        },
        {
            "Check": "Price vs. 60-day SMA",
            "Reading": f"${current_price:,.2f} vs. ${sma60:,.2f}",
            "Signal": signal_for_distance(distance60),
            "Detail": f"{distance60:+.2f}% from the 60-day average",
        },
        {
            "Check": "30-day SMA vs. 60-day SMA",
            "Reading": f"${sma30:,.2f} vs. ${sma60:,.2f}",
            "Signal": "Positive alignment" if sma30 >= sma60 else "Negative alignment",
            "Detail": "Shorter trend is above longer trend" if sma30 >= sma60 else "Shorter trend is below longer trend",
        },
        {
            "Check": "30-day momentum",
            "Reading": f"{momentum30:+.2f}%",
            "Signal": "Positive" if momentum30 >= 0 else "Negative",
            "Detail": "Price change over the last 30 trading sessions",
        },
        {
            "Check": "60-day momentum",
            "Reading": f"{momentum60:+.2f}%",
            "Signal": "Positive" if momentum60 >= 0 else "Negative",
            "Detail": "Price change over the last 60 trading sessions",
        },
        {
            "Check": "RSI (14-day)",
            "Reading": f"{rsi14:.1f}",
            "Signal": rsi_signal,
            "Detail": "Momentum oscillator; not a valuation measure",
        },
    ]
    return {
        "ticker": ticker.upper(),
        "retrieved_on": date.today().isoformat(),
        "source_url": YAHOO_HISTORY_URL.format(ticker=quote(ticker.upper())),
        "current_price": current_price,
        "sma30": sma30,
        "sma60": sma60,
        "momentum30": momentum30,
        "momentum60": momentum60,
        "rsi14": rsi14,
        "rsi_signal": rsi_signal,
        "trend": trend_label(current_price, sma30, sma60, momentum30, momentum60),
        "checks": checks,
        "chart_rows": chart_rows[-180:],
        "observation_count": len(rows),
    }


def analyze_ticker(ticker):
    """Fetch history and return the technical snapshot used by the app."""
    rows = fetch_daily_history(ticker)
    return build_technical_snapshot(ticker, rows)
