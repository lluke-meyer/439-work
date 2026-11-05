"""Streamlit app for the Lab 19 Cathie Wood / Michael Burry legend panel."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import streamlit as st


HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from panel_financials import analyze_ticker, display_value, format_row  # noqa: E402


st.set_page_config(page_title="Lab 19 Legend Panel", layout="wide")
st.title("Lab 19 - Legend Panel")
st.caption(
    "One SEC EDGAR facts table, three investor rules, and a visible decision about whether to trust the panel."
)
st.info(
    "Personas: Warren Buffett, Cathie Wood, and Michael Burry. The Wood checks are explicit SEC-only growth/scale proxies; innovation, TAM, adoption, and valuation remain outside this panel."
)


def report_rows(report):
    return [format_row(row) for row in report["rows"]]


def panel_rows(report):
    rows = []
    for investor, checks in report["checks"].items():
        for check, status in checks.items():
            rows.append({"Investor": investor, "Check": check, report["ticker"]: status})
    return rows


def numbers_in_report(report):
    values = set()
    for row in report["rows"]:
        values.add(row["fiscal_year_end"])
        for value in row.values():
            if isinstance(value, (int, float)) and value is not None:
                values.update({str(value), f"{value:,.0f}", f"{value:,.1f}", f"{value:,.2f}"})
    values.update({"15", "15.0", "15.0%", "2", "2.0", "1", "1.0", "10"})
    return values


def memo_number_flags(memo, report):
    printed = numbers_in_report(report)
    memo = re.sub(r"\b[0-9]{1,2}-(?:K|year)\b", "", memo, flags=re.IGNORECASE)
    tokens = re.findall(
        r"(?<![A-Za-z])\$?(?:[0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)(?:\.[0-9]+)?%?",
        memo,
    )
    flags = []
    for token in tokens:
        normalized = token.replace("$", "")
        if normalized not in printed and normalized.rstrip("%") not in printed:
            flags.append(token)
    return sorted(set(flags))


def memo_header(title, report):
    return f"# {title} memo - {report['ticker']}\n\n"


def generated_memos(report):
    first, last = report["rows"][0], report["rows"][-1]
    checks = report["checks"]
    buffett = (
        memo_header("Buffett", report)
        + f"**Verdict: {'quality case' if all(value == 'pass' for value in checks['Buffett'].values()) else 'watch / incomplete'}.**\n\n"
        + f"Revenue moved from {display_value(first['revenue'])} to {display_value(last['revenue'])}; owner earnings moved from {display_value(first['owner_earnings'])} to {display_value(last['owner_earnings'])}. "
        + f"ROE check: {checks['Buffett']['ROE of 15% or more every year']}; owner-earnings-positive check: {checks['Buffett']['Owner earnings positive every year']}; owner-earnings-growth check: {checks['Buffett']['Owner earnings grew, first year to last']}."
    )
    wood = (
        memo_header("Cathie Wood", report)
        + f"**Verdict: {'growth proxy supported' if all(value == 'pass' for value in checks['Cathie Wood'].values()) else 'growth proxy mixed / incomplete'}.**\n\n"
        + f"The SEC-only proxy shows revenue from {display_value(first['revenue'])} to {display_value(last['revenue'])}, net income from {display_value(first['net_income'])} to {display_value(last['net_income'])}, and operating cash flow from {display_value(first['operating_cash_flow'])} to {display_value(last['operating_cash_flow'])}. "
        + f"Revenue growth: {checks['Cathie Wood']['Revenue grew, first year to last']}; net-income growth: {checks['Cathie Wood']['Net income grew, first year to last']}; positive cash flow: {checks['Cathie Wood']['Operating cash flow positive every year']}. Innovation, TAM, adoption, competitive edge, and valuation are not printed here and remain not known."
    )
    burry = (
        memo_header("Michael Burry", report)
        + f"**Verdict: {'forensic checks pass' if all(value == 'pass' for value in checks['Michael Burry'].values()) else 'forensic caution / incomplete'}.**\n\n"
        + f"Operating cash flow was {display_value(last['operating_cash_flow'])} versus net income of {display_value(last['net_income'])} in the latest row; liabilities were {display_value(last['liabilities'])} against equity of {display_value(last['equity'])}, or {display_value(last['liabilities_to_equity'])} times equity. "
        + f"OCF-versus-net-income check: {checks['Michael Burry']['Operating cash flow at least net income every year']}; liabilities/equity check: {checks['Michael Burry']['Liabilities no more than twice equity, latest year']}. Footnotes, revenue recognition, leases, contingencies, insider activity, and valuation are not tested and remain not known."
    )
    return {"Buffett": buffett, "Cathie Wood": wood, "Michael Burry": burry}


def show_memo(investor, memo, report):
    edited = st.text_area(
        f"{investor} memo",
        value=memo,
        height=290,
        key=f"memo_{report['ticker']}_{investor}",
    )
    flags = memo_number_flags(edited, report)
    if flags:
        st.error(f"Numbers not printed by the script: {', '.join(flags)}")
    else:
        st.success("Every number in this memo appears in the printed SEC report.")


def panel_fingerprint(report):
    counts = {"pass": 0, "fail": 0, "not known": 0}
    next_checks = []
    for checks in report["checks"].values():
        for label, status in checks.items():
            counts[status] += 1
            if status != "pass":
                next_checks.append(f"{label}: {status}")
    if counts["not known"]:
        label = "Insufficient evidence"
        read = "Keep the gap open. A missing fact is not a pass or a fail."
    elif counts["fail"]:
        label = "Useful split"
        read = "Use the disagreement to direct the next research step before deciding."
    else:
        label = "Screen agreement"
        read = "The rules agree, but the panel is still a first screen, not a buy signal."
    return counts, label, read, next_checks


def run_panel(ticker, state_key):
    try:
        with st.spinner(f"Fetching SEC EDGAR facts for {ticker}..."):
            report = analyze_ticker(ticker)
        st.session_state[state_key] = report
    except Exception as error:  # noqa: BLE001
        st.error(str(error))


cost_col, company_col = st.columns(2)
with cost_col:
    st.subheader("Known answer: COST")
    if st.button("Run COST panel", type="primary"):
        run_panel("COST", "cost_report")
with company_col:
    st.subheader("Your fund company")
    st.caption("Current Project 2 bridge: SOXX → NVDA; verify the fund holding before submission.")
    company_ticker = st.text_input("Ticker", value="NVDA", max_chars=8).strip().upper()
    if st.button("Run selected company"):
        run_panel(company_ticker, "company_report")


def show_report(report, label):
    st.divider()
    st.header(f"{label}: {report['ticker']} - {report['company_name']}")
    st.dataframe(report_rows(report), width="stretch", hide_index=True)
    st.caption(
        "All values are USD millions except ratios and ROE. Missing facts stay not found; checks stay not known when required inputs are missing."
    )

    st.subheader("Panel table")
    st.dataframe(panel_rows(report), width="stretch", hide_index=True)
    verdicts = []
    for investor, checks in report["checks"].items():
        passed = sum(value == "pass" for value in checks.values())
        known = sum(value != "not known" for value in checks.values())
        verdicts.append(f"{investor}: {passed} of {known} known checks pass")
    st.write(" · ".join(verdicts))

    counts, fingerprint, fingerprint_read, next_checks = panel_fingerprint(report)
    st.subheader("Panel fingerprint")
    fingerprint_cols = st.columns(4)
    fingerprint_cols[0].metric("Pass", counts["pass"])
    fingerprint_cols[1].metric("Fail", counts["fail"])
    fingerprint_cols[2].metric("Not known", counts["not known"])
    fingerprint_cols[3].metric("Trust read", fingerprint)
    st.caption(fingerprint_read)
    if next_checks:
        st.warning("Next evidence: " + " · ".join(next_checks))

    st.subheader("Three memos - editable and checked")
    memos = generated_memos(report)
    columns = st.columns(3)
    for column, investor in zip(columns, memos):
        with column:
            st.markdown(f"#### {investor}")
            show_memo(investor, memos[investor], report)

    st.subheader("Threshold probe")
    latest = report["rows"][-1]
    current_ratio = latest["current_ratio"]
    if current_ratio is None:
        st.warning("Current ratio probe: not known because current assets or current liabilities is missing.")
    else:
        at_two = "pass" if current_ratio >= 2 else "fail"
        at_one = "pass" if current_ratio >= 1 else "fail"
        st.write(
            f"Latest current ratio = {display_value(current_ratio)}. At threshold 2: **{at_two}**; at threshold 1: **{at_one}**. Keep the threshold explicit because changing it changes the verdict."
        )

    st.subheader("Bull, bear, and decision")
    st.markdown(
        "**Bull:** The panel is useful when its printed checks agree and the underlying business evidence supports the operating story.\n\n"
        "**Bear:** The panel can hide what it does not measure: valuation, innovation/TAM, footnotes, accounting quality, and market expectations. A pass is a screen, not a buy signal.\n\n"
        "**Decision:** Only with a condition - use it for a repeatable first screen, then verify the filing, thesis, valuation, and every not-known field before Project 2 use."
    )

    with st.expander("Code explanation: missing-input behavior"):
        st.code(
            "if any(value is None for value in values):\n"
            "    return 'not known'\n"
            "return 'pass' if all(predicate(value) for value in values) else 'fail'",
            language="python",
        )
        st.write(
            "The functions never turn a missing fact into zero or an estimate. That is why the panel can honestly return not known."
        )


if "cost_report" not in st.session_state:
    st.caption("Start with COST to reproduce the known answer, then run the fund company.")
if "cost_report" in st.session_state:
    show_report(st.session_state["cost_report"], "Known-answer run")
if "company_report" in st.session_state:
    show_report(st.session_state["company_report"], "Fund-company run")

st.markdown(
    """\n\n\n###This report was written for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research and it is not financial advice.\n\n###AI assistance: drafted with [Codex], resumed from my Lab 03 session; sources gathered and verified by me; the judgments are mine.\n\n###Any remaining errors are my own."""
)
