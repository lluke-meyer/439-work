"""Live public-discourse snapshot from Yahoo Finance's public news search endpoint."""

from __future__ import annotations

import json
from datetime import date, datetime
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


SEARCH_URL = "https://query1.finance.yahoo.com/v1/finance/search"
USER_AGENT = "FIN43900-Lab18-public-discourse"

POSITIVE_TERMS = {
    "beat",
    "beats",
    "bullish",
    "buy",
    "growth",
    "gains",
    "raised",
    "record",
    "strong",
    "upgrade",
    "upside",
    "surge",
    "expands",
    "demand",
    "outperform",
}
NEGATIVE_TERMS = {
    "bearish",
    "downgrade",
    "risk",
    "risks",
    "miss",
    "misses",
    "weak",
    "decline",
    "declines",
    "cut",
    "cuts",
    "tariff",
    "tariffs",
    "lawsuit",
    "warning",
    "concern",
    "concerns",
    "slowdown",
    "pressure",
    "overvalued",
}


def fetch_search(ticker, news_count=12):
    ticker = ticker.upper().strip()
    url = f"{SEARCH_URL}?q={quote(ticker)}&newsCount={news_count}&quotesCount=0"
    request = Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"},
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.load(response)
    except (HTTPError, URLError) as error:
        raise RuntimeError(f"Yahoo public-discourse request failed for {ticker}: {error}") from error


def classify_title(title):
    words = set(title.lower().replace("—", " ").replace("-", " ").split())
    positive_hits = sorted(words & POSITIVE_TERMS)
    negative_hits = sorted(words & NEGATIVE_TERMS)
    if len(positive_hits) >= len(negative_hits) + 1 and positive_hits:
        return "Supportive", positive_hits, negative_hits
    if len(negative_hits) >= len(positive_hits) + 1 and negative_hits:
        return "Caution", positive_hits, negative_hits
    return "Mixed", positive_hits, negative_hits


def parse_news(ticker, payload):
    ticker = ticker.upper().strip()
    raw_news = payload.get("news", [])
    related = []
    unrelated = []
    for item in raw_news:
        tickers = {value.upper() for value in item.get("relatedTickers", [])}
        parsed = {
            "title": item.get("title", "Untitled"),
            "publisher": item.get("publisher", "Unknown publisher"),
            "url": item.get("link", ""),
            "published": datetime.fromtimestamp(item["providerPublishTime"]).date().isoformat()
            if item.get("providerPublishTime")
            else "unknown",
        }
        parsed["direction"], parsed["positive_terms"], parsed["negative_terms"] = classify_title(
            parsed["title"]
        )
        if ticker in tickers:
            related.append(parsed)
        else:
            unrelated.append(parsed)
    return related or unrelated


def analyze_public_discourse(ticker):
    ticker = ticker.upper().strip()
    payload = fetch_search(ticker)
    news = parse_news(ticker, payload)
    if not news:
        raise RuntimeError(f"No public news items were returned for {ticker}.")
    counts = {"Supportive": 0, "Mixed": 0, "Caution": 0}
    for item in news:
        counts[item["direction"]] += 1
    if counts["Supportive"] >= counts["Caution"] + 2:
        overall = "Supportive headlines"
    elif counts["Caution"] >= counts["Supportive"] + 2:
        overall = "Cautious headlines"
    else:
        overall = "Mixed headlines"
    return {
        "ticker": ticker,
        "retrieved_on": date.today().isoformat(),
        "source_url": f"https://finance.yahoo.com/quote/{quote(ticker)}/news/",
        "news": news[:8],
        "counts": counts,
        "overall": overall,
        "method": "Headline keyword screen; not a language-model sentiment score.",
    }
