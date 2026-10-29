"""FIN 439 Lab 17: point-in-time audit."""

import calendar
import csv
from collections import defaultdict
from datetime import date
from pathlib import Path


DECISION_DATE = date(2026, 3, 31)
DECISION_DATES = [
    date(2026, 2, 28),
    date(2026, 3, 31),
    date(2026, 4, 30),
]
OWN_CSV = Path(__file__).with_name("m2sl_vintages.csv")
OWN_HEADERS = ["series name", "month measured", "published on", "value"]

ROWS = [
    {"row": 1, "ticker": "AAA", "month": "2026-01", "published": "2026-02-10", "index": 101.0},
    {"row": 2, "ticker": "AAA", "month": "2026-02", "published": "2026-03-10", "index": 104.0},
    {"row": 3, "ticker": "AAA", "month": "2026-03", "published": "2026-04-10", "index": 109.0},
    {"row": 4, "ticker": "AAA", "month": "2026-02", "published": "2026-03-25", "index": 103.0},
    {"row": 5, "ticker": "BBB", "month": "2026-01", "published": "2026-02-10", "index": 98.0},
    {"row": 6, "ticker": "BBB", "month": "2026-02", "published": "2026-03-10", "index": 97.0},
    {"row": 7, "ticker": "BBB", "month": "2026-02", "published": "2026-03-10", "index": 97.0},
    {"row": 8, "ticker": "BBB", "month": "2026-03", "published": "2026-04-10", "index": 92.0},
    {"row": 9, "ticker": "CCC", "month": "2026-01", "published": "2026-02-10", "index": 110.0},
    {"row": 10, "ticker": "CCC", "month": "2026-02", "published": "2026-04-05", "index": 112.0},
    {"row": 11, "ticker": "", "month": "2026-02", "published": "2026-03-10", "index": 99.0},
    {"row": 12, "ticker": "CCC", "month": "2026-02", "published": "2026-03-10", "index": 111.0},
]


def published_date(row):
    return date.fromisoformat(row["published"])


def exact_key(row):
    return row["ticker"], row["month"], row["published"], row["index"]


def remove_exact_duplicates(rows):
    seen = set()
    kept = []
    removed = []
    for row in rows:
        key = exact_key(row)
        if key in seen:
            removed.append(row)
        else:
            seen.add(key)
            kept.append(row)
    return kept, removed


def apply_provenance_gate(rows, decision_date):
    """Apply the four Lab 16 rules in the required order."""
    funnel = []

    working = [row for row in rows if row["ticker"].strip()]
    funnel.append(("Quarantined: no ticker", [row for row in rows if not row["ticker"].strip()]))

    working, removed = remove_exact_duplicates(working)
    funnel.append(("Exact duplicate", removed))

    knowable = [row for row in working if published_date(row) <= decision_date]
    funnel.append(("Published after decision date", [row for row in working if published_date(row) > decision_date]))

    by_series_month = defaultdict(list)
    for row in knowable:
        by_series_month[(row["ticker"], row["month"])].append(row)

    revisions_removed = []
    selected = set()
    for candidates in by_series_month.values():
        latest = max(candidates, key=lambda row: (published_date(row), row["row"]))
        selected.add(latest["row"])
        revisions_removed.extend(row for row in candidates if row["row"] != latest["row"])

    panel = [row for row in knowable if row["row"] in selected]
    funnel.append(("Older vintage replaced by a revision", revisions_removed))
    return funnel, panel


def latest_vintage_panel(rows):
    """Build the naive panel: latest publication, with no as-of cutoff."""
    working, _ = remove_exact_duplicates(row for row in rows if row["ticker"].strip())
    by_series_month = defaultdict(list)
    for row in working:
        by_series_month[(row["ticker"], row["month"])].append(row)
    return [
        max(candidates, key=lambda row: (published_date(row), row["row"]))
        for candidates in by_series_month.values()
    ]


def signals(panel):
    """Return latest-month percent changes by ticker from a panel."""
    by_ticker = defaultdict(list)
    for row in panel:
        by_ticker[row["ticker"]].append(row)

    results = {}
    for ticker, rows in sorted(by_ticker.items()):
        by_month = {row["month"]: row for row in rows}
        months = sorted(by_month)
        if len(months) < 2:
            results[ticker] = None
            continue
        previous, latest = (by_month[month] for month in months[-2:])
        change = (latest["index"] / previous["index"] - 1) * 100
        results[ticker] = {
            "month": latest["month"],
            "change": change,
            "previous_row": previous["row"],
            "latest_row": latest["row"],
        }
    return results


def print_funnel(funnel, panel):
    print("\nRow funnel:")
    for name, removed in funnel:
        rows = ", ".join(str(row["row"]) for row in removed) or "none"
        print(f"- {name}: removed {len(removed)} row(s): {rows}")
    print("- As-of panel: " + ", ".join(str(row["row"]) for row in panel))


def print_panel(title, panel):
    print(f"\n{title}:")
    print("row | ticker | month   | published  | index")
    print("----|--------|---------|------------|------")
    for row in sorted(panel, key=lambda item: item["row"]):
        print(
            f"{row['row']:>3} | {row['ticker']:<6} | {row['month']} | "
            f"{row['published']} | {row['index']:.1f}"
        )


def print_signals(title, result):
    print(f"\n{title}:")
    for ticker, signal in result.items():
        if signal is None:
            print(f"- {ticker}: not enough monthly observations")
        else:
            direction = "+" if signal["change"] >= 0 else ""
            print(f"- {ticker}: {direction}{signal['change']:.2f}% ({signal['month']})")


def run(decision_date=DECISION_DATE):
    funnel, panel = apply_provenance_gate(ROWS, decision_date)
    naive_panel = latest_vintage_panel(ROWS)
    asof_signals = signals(panel)
    naive_signals = signals(naive_panel)

    print(f"Decision date: {decision_date.isoformat()}")
    print_funnel(funnel, panel)
    print_panel("As-of panel", panel)
    print_signals("As-of signals", asof_signals)
    print_signals("Naive signals (latest publication, ignoring decision date)", naive_signals)
    return {
        "funnel": funnel,
        "panel": panel,
        "naive_panel": naive_panel,
        "asof_signals": asof_signals,
        "naive_signals": naive_signals,
    }


def load_own_rows(path):
    """Read the student's four-column ALFRED vintage table."""
    rows = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != OWN_HEADERS:
            raise ValueError(f"Expected CSV columns {OWN_HEADERS}; found {reader.fieldnames}")
        for row_number, source_row in enumerate(reader, start=1):
            if not source_row["value"].strip():
                continue
            rows.append(
                {
                    "row": row_number,
                    "ticker": source_row["series name"].strip(),
                    "month": source_row["month measured"].strip(),
                    "published": source_row["published on"].strip(),
                    "index": float(source_row["value"]),
                }
            )
    return rows


def month_end(month_text):
    year, month = (int(part) for part in month_text.split("-"))
    return date(year, month, calendar.monthrange(year, month)[1])


def add_months(month_end_date, offset):
    month_index = month_end_date.year * 12 + month_end_date.month - 1 + offset
    year, month_index = divmod(month_index, 12)
    month = month_index + 1
    return date(year, month, calendar.monthrange(year, month)[1])


def last_24_month_ends(rows):
    latest_month = max(row["month"] for row in rows)
    latest_end = month_end(latest_month)
    return [add_months(latest_end, offset) for offset in range(-23, 1)]


def naive_future_rows(rows, decision_date):
    """Return naive rows for already-measured months that were not yet knowable."""
    cutoff_month = decision_date.strftime("%Y-%m")
    naive_panel = latest_vintage_panel(rows)
    return [
        row for row in naive_panel
        if row["month"] <= cutoff_month and published_date(row) > decision_date
    ]


def signal_text(result):
    if not result:
        return "not enough knowable months"
    signal = next(iter(result.values()))
    if signal is None:
        return "not enough knowable months"
    direction = "+" if signal["change"] >= 0 else ""
    return f"{direction}{signal['change']:.2f}% ({signal['month']})"


def print_training_date_report():
    print("\nTraining table: multiple decision dates")
    for decision_date in DECISION_DATES:
        funnel, panel = apply_provenance_gate(ROWS, decision_date)
        result = signals(panel)
        leaked = naive_future_rows(ROWS, decision_date)
        leaked_rows = ", ".join(str(row["row"]) for row in leaked) or "none"
        print(
            f"- {decision_date.isoformat()}: as-of signal {signal_text(result)}; "
            f"naive rows not yet published {leaked_rows}"
        )


def print_own_series_report(rows):
    dates = last_24_month_ends(rows)
    print(f"\nOwn series: {OWN_CSV.name}")
    print(f"- admitted data rows: {len(rows)} across {dates[0]} through {dates[-1]}")
    print("- monthly report: decision date | as-of signal | funnel counts | naive future rows")
    for decision_date in dates:
        funnel, panel = apply_provenance_gate(rows, decision_date)
        result = signals(panel)
        counts = "; ".join(f"{name}={len(removed)}" for name, removed in funnel)
        leaked = naive_future_rows(rows, decision_date)
        print(
            f"- {decision_date.isoformat()} | {signal_text(result)} | {counts}; "
            f"panel={len(panel)} | naive future rows={len(leaked)}"
        )


if __name__ == "__main__":
    run()
    print_training_date_report()
    print_own_series_report(load_own_rows(OWN_CSV))


###This report was written for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research and it is not financial advice.

###AI assistance: drafted with [Codex], resumed from my Lab 03 session; sources gathered and verified by me; the judgments are mine.

###Any remaining errors are my own.
