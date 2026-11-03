"""Streamlit front end for the Lab 18 SEC EDGAR Buffett skill."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import streamlit as st


SKILL_DIR = Path(__file__).parent / "warren-buffett-expert"
sys.path.insert(0, str(SKILL_DIR))
from scripts.sec_buffett_financials import analyze_ticker, display_value  # noqa: E402
from public_research import get_public_research  # noqa: E402
from public_discourse import analyze_public_discourse  # noqa: E402
from technical_analysis import analyze_ticker as analyze_technical  # noqa: E402


st.set_page_config(page_title="Legend Investor as Skill", layout="wide")
st.title("Legend Investor as Skill")
st.caption(
    "Data from SEC EDGAR; built with AI help, a learning demonstration, not investment advice."
)
st.caption("Financial values are shown in USD millions; ROE is a percentage.")
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 88% 5%, #d9f4ef 0, #f7fbfa 34%, #f6f3ed 100%);
    }
    .plus-banner {
        border: 1px solid #0f766e;
        border-left: 8px solid #0f766e;
        border-radius: 14px;
        padding: 1rem 1.25rem;
        margin: 1.1rem 0 0.8rem;
        background: linear-gradient(110deg, rgba(15,118,110,.12), rgba(255,255,255,.78));
    }
    .plus-kicker {
        color: #0f766e;
        font-size: .78rem;
        font-weight: 800;
        letter-spacing: .12em;
        text-transform: uppercase;
    }
    .plus-title {
        color: #12312f;
        font-size: 1.75rem;
        font-weight: 800;
        margin: .15rem 0 .35rem;
    }
    .source-pill {
        border: 1px solid #d6e7e3;
        border-radius: 999px;
        color: #0f766e;
        display: inline-block;
        font-size: .78rem;
        margin: .15rem .3rem .15rem 0;
        padding: .2rem .55rem;
    }
    .technical-banner {
        border-left-color: #7c3aed;
        background: linear-gradient(110deg, rgba(124,58,237,.10), rgba(255,255,255,.78));
    }
    .technical-banner .plus-kicker {
        color: #6d28d9;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def format_row(row):
    return {
        "Fiscal year end": row["fiscal_year_end"],
        "Revenue": display_value(row["revenue"]),
        "Net income": display_value(row["net_income"]),
        "Operating cash flow": display_value(row["operating_cash_flow"]),
        "Capital spending": display_value(row["capital_spending"]),
        "Equity": display_value(row["equity"]),
        "ROE %": display_value(row["roe_percent"]),
        "Owner earnings": display_value(row["owner_earnings"]),
    }


def numbers_in_report(report):
    values = set()
    for row in report["rows"]:
        values.add(row["fiscal_year_end"])
        for key in (
            "revenue",
            "net_income",
            "operating_cash_flow",
            "capital_spending",
            "equity",
            "roe_percent",
            "owner_earnings",
        ):
            value = row[key]
            if value is not None:
                values.add(str(value))
                values.add(f"{value:,.1f}")
                values.add(f"{value:,.0f}")
    values.update({"15", "15.0", "15.0%"})
    return values


def memo_number_flags(memo, report):
    printed = numbers_in_report(report)
    memo = re.sub(r"\b[0-9]{1,2}-[A-Z]\b", "", memo)
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


def generated_memo(report):
    rows = report["rows"]
    first = rows[0]
    last = rows[-1]
    checks = report["checks"]
    passed = all(value == "pass" for value in checks.values())
    verdict = "own the business" if passed else "watch it"
    check_sentence = (
        f"ROE check: {checks['roe_15_every_year']}; owner-earnings-positive check: "
        f"{checks['owner_earnings_positive_every_year']}; owner-earnings-growth check: "
        f"{checks['owner_earnings_grew']}."
    )
    return (
        f"# Buffett memo — {report['ticker']}\n\n"
        f"**Verdict: {verdict}.**\n\n"
        f"The five-year SEC 10-K table shows revenue rising from "
        f"{display_value(first['revenue'])} to {display_value(last['revenue'])}, "
        f"net income rising from {display_value(first['net_income'])} to "
        f"{display_value(last['net_income'])}, and owner earnings moving from "
        f"{display_value(first['owner_earnings'])} to {display_value(last['owner_earnings'])}. "
        f"{check_sentence}\n\n"
        "Those checks support a business-quality verdict, subject to the limits of the reported "
        "10-K facts. This week's analysis does not judge the stock price or estimate intrinsic value."
    )


def generated_plus_memo(report, plus, discourse, technical):
    """Create a revised memo from the visible SEC, public-source, and technical evidence."""
    checks = report["checks"]
    quality_verdict = "own the business" if all(value == "pass" for value in checks.values()) else "watch it"
    lines = [
        f"# Buffett Test Plus memo — {report['ticker']}",
        "",
        f"**Revised verdict: {quality_verdict}, but with context.**",
        "",
        "The original SEC-only Buffett test is the foundation of this memo. "
        f"Its checks are ROE: {checks['roe_15_every_year']}; owner earnings positive: "
        f"{checks['owner_earnings_positive_every_year']}; and owner earnings growth: "
        f"{checks['owner_earnings_grew']}.",
    ]
    if plus is not None:
        analyst = plus["analyst"]
        lines.extend(
            [
                "",
                f"The public analyst snapshot is {analyst['consensus']} from {analyst['analyst_count']} analysts, "
                f"with an average target of ${analyst['target_average']:,.0f} and {analyst['upside_percent']:.2f}% implied upside.",
                "Public intrinsic-value models disagree materially: two displayed estimates are below the "
                "snapshot price and one is a high outlier. I treat that disagreement as valuation uncertainty, "
                "not as a reason to average incompatible models.",
            ]
        )
    if discourse is not None:
        counts = discourse["counts"]
        lines.extend(
            [
                "",
                f"The live public-discourse screen reads {discourse['overall'].lower()} "
                f"({counts['Supportive']} supportive, {counts['Mixed']} mixed, {counts['Caution']} caution) "
                f"across {len(discourse['news'])} Yahoo Finance-linked headlines. "
                f"This is a headline keyword screen, not a claim that headlines measure intrinsic value.",
            ]
        )
    if technical is not None:
        lines.extend(
            [
                "",
                f"Technical context is {technical['trend'].lower()}: the latest close is "
                f"${technical['current_price']:,.2f}, versus a 30-day SMA of ${technical['sma30']:,.2f} "
                f"and a 60-day SMA of ${technical['sma60']:,.2f}; RSI(14) is {technical['rsi14']:.1f}.",
            ]
        )
    lines.extend(
        [
            "",
            "**Decision bridge:** the business-quality evidence may support further research, but the "
            "public valuation disagreement and technical/public-discourse context should keep the decision "
            "bounded. Strong business evidence is not the same thing as a margin of safety or a buy signal.",
        ]
    )
    return "\n".join(lines)


@st.cache_data(ttl=900, show_spinner=False)
def load_technical_snapshot(ticker):
    return analyze_technical(ticker)


@st.cache_data(ttl=900, show_spinner=False)
def load_public_discourse(ticker):
    return analyze_public_discourse(ticker)


ticker = st.text_input("Ticker", value="COST", max_chars=8).strip().upper()
if st.button("Run SEC EDGAR analysis", type="primary"):
    try:
        with st.spinner(f"Fetching SEC EDGAR facts for {ticker}..."):
            report = analyze_ticker(ticker)
        st.session_state["report"] = report
    except Exception as error:  # noqa: BLE001
        st.error(str(error))


report = st.session_state.get("report")
if report:
    plus = get_public_research(report["ticker"])
    discourse = None
    technical = None
    st.subheader(f"{report['ticker']} — {report['company_name']}")
    st.dataframe([format_row(row) for row in report["rows"]], width="stretch")

    st.subheader("XBRL tags used")
    st.json(report["tags"])

    st.subheader("Buffett's checks")
    for label, key in (
        ("ROE of 15% or more every year", "roe_15_every_year"),
        ("Owner earnings positive every year", "owner_earnings_positive_every_year"),
        ("Owner earnings grew, first year to last", "owner_earnings_grew"),
    ):
        st.write(f"{label}: **{report['checks'][key]}**")

    st.markdown(
        """
        <div class="plus-banner">
            <div class="plus-kicker">Research overlay · separate from the SEC-only test</div>
            <div class="plus-title">Buffett Test Plus</div>
            <div>Analyst expectations, public valuation models, and economic/news evidence are
            weighed against the original business-quality checks. The extra sources are not averaged
            into the Buffett test.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="plus-banner technical-banner">
            <div class="plus-kicker">Market-context overlay · live daily history</div>
            <div class="plus-title">Technical 30/60-Day Checks</div>
            <div>Start with the latest close and recent trend. These checks describe market context;
            they do not override the Buffett business-quality test or create an intrinsic-value estimate.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    try:
        technical = load_technical_snapshot(report["ticker"])
    except Exception as error:  # noqa: BLE001
        st.warning(f"Technical overlay unavailable: {error}")
    else:
        technical_cols = st.columns(4)
        technical_cols[0].metric("Latest close", f"${technical['current_price']:,.2f}")
        technical_cols[1].metric("30-day SMA", f"${technical['sma30']:,.2f}")
        technical_cols[2].metric("60-day SMA", f"${technical['sma60']:,.2f}")
        technical_cols[3].metric("RSI (14)", f"{technical['rsi14']:.1f}")
        st.caption(
            f"{technical['observation_count']} daily observations retrieved {technical['retrieved_on']} · "
            f"[Yahoo Finance history]({technical['source_url']}) · data cached for 15 minutes."
        )
        if technical["trend"] == "Bullish trend":
            st.success(f"Technical read: {technical['trend']}")
        elif technical["trend"] == "Bearish trend":
            st.error(f"Technical read: {technical['trend']}")
        else:
            st.warning(f"Technical read: {technical['trend']}")
        st.dataframe(technical["checks"], width="stretch", hide_index=True)
        chart_data = {
            row["Date"]: {
                "Close": row["Close"],
                "30-day SMA": row["30-day SMA"],
                "60-day SMA": row["60-day SMA"],
            }
            for row in technical["chart_rows"]
        }
        st.line_chart(chart_data)
        with st.expander("How the technical checks work"):
            st.markdown(
                "- **30-day SMA / 60-day SMA:** average closing price over the last 30 or 60 trading sessions.\n"
                "- **Momentum:** percentage price change over the last 30 or 60 trading sessions.\n"
                "- **RSI (14):** a momentum oscillator; readings near 70 or above are commonly called overbought, while readings near 30 or below are commonly called oversold.\n"
                "- **Trend label:** requires price, SMA alignment, and both momentum windows to point in the same direction; otherwise it stays mixed."
            )

    if plus is None:
        st.info(
            "No curated analyst/valuation snapshot is bundled for this ticker. "
            "Live public discourse and the technical checks are still active in this overlay."
        )
    else:
        st.caption(
            f"Public-source snapshot retrieved {plus['retrieved_on']}. "
            "Analyst and valuation figures are model-dependent and can change."
        )
        analyst = plus["analyst"]
        analyst_cols = st.columns(4)
        analyst_cols[0].metric("Analyst consensus", analyst["consensus"])
        analyst_cols[1].metric("Analysts", f"{analyst['analyst_count']}")
        analyst_cols[2].metric("Average target", f"${analyst['target_average']:,.0f}")
        analyst_cols[3].metric("Implied upside", f"{analyst['upside_percent']:.2f}%")
        st.markdown(
            f"<span class='source-pill'><a href='{analyst['url']}' target='_blank'>"
            f"{analyst['source']}</a></span> {analyst['read']}",
            unsafe_allow_html=True,
        )
        rating_mix = plus["rating_mix"]
        st.markdown("#### Analyst rating mix")
        st.dataframe(
            [{"Rating": label, "Count": count} for label, count in rating_mix["counts"].items()],
            width="stretch",
            hide_index=True,
        )
        st.markdown(
            f"[{rating_mix['source']} snapshot]({rating_mix['url']}) · {rating_mix['as_of']} · "
            f"{rating_mix['read']}"
        )

        st.markdown("#### Public intrinsic-value snapshots")
        st.caption(
            "These estimates use different assumptions and are shown side by side, not averaged."
        )
        valuation_rows = []
        for item in plus["intrinsic_value"]:
            value = item["value"]
            gap = value / analyst["current_price"] - 1
            valuation_rows.append(
                {
                    "Source": item["source"],
                    "As of": item["as_of"],
                    "Method": item["method"],
                    "Published value": f"${value:,.2f}",
                    "vs. snapshot price": f"{gap:+.1%}",
                }
            )
        st.dataframe(valuation_rows, width="stretch", hide_index=True)
        for item in plus["intrinsic_value"]:
            range_text = ""
            if item["range_low"] is not None:
                range_text = (
                    f" Range: ${item['range_low']:,.2f}–${item['range_high']:,.2f}."
                )
            st.markdown(
                f"- [{item['source']}]({item['url']}) — {item['read']}{range_text}"
            )

        st.markdown("#### Economic and news read")
        for item in plus["news"]:
            label = f"{item['direction']} · {item['source']} · {item['date']}"
            with st.expander(label):
                st.markdown(f"**[{item['title']}]({item['url']})**")
                st.write(item["takeaway"])
                st.info(item["economic_read"])

        original_checks_pass = all(value == "pass" for value in report["checks"].values())
        original_read = (
            "All three original Buffett checks pass."
            if original_checks_pass
            else "The original Buffett checks are mixed or incomplete."
        )
        st.markdown("#### Weighed against the original Buffett test")
        st.markdown(
            f"**Original test:** {original_read}  \n"
            f"**Plus read:** {plus['plus_read']['label']}  \n"
            f"{plus['plus_read']['summary']}"
        )
        st.success(f"Decision bridge: {plus['plus_read']['decision']}")

    st.markdown("#### Live public discourse")
    try:
        discourse = load_public_discourse(report["ticker"])
    except Exception as error:  # noqa: BLE001
        st.warning(f"Public-discourse overlay unavailable: {error}")
    else:
        discourse_cols = st.columns(4)
        discourse_cols[0].metric("Overall read", discourse["overall"])
        discourse_cols[1].metric("Supportive", discourse["counts"]["Supportive"])
        discourse_cols[2].metric("Mixed", discourse["counts"]["Mixed"])
        discourse_cols[3].metric("Caution", discourse["counts"]["Caution"])
        st.caption(
            f"{len(discourse['news'])} headlines retrieved {discourse['retrieved_on']} from "
            f"[Yahoo Finance public news search]({discourse['source_url']}). {discourse['method']}"
        )
        for item in discourse["news"]:
            label = f"{item['direction']} · {item['publisher']} · {item['published']}"
            with st.expander(label):
                st.markdown(f"**[{item['title']}]({item['url']})**")
                if item["positive_terms"] or item["negative_terms"]:
                    st.write(
                        f"Keyword screen: positive={', '.join(item['positive_terms']) or 'none'}; "
                        f"caution={', '.join(item['negative_terms']) or 'none'}."
                    )

    st.subheader("Owner earnings and net income")
    st.line_chart(
        {
            row["fiscal_year_end"]: {
                "Owner earnings": row["owner_earnings"],
                "Net income": row["net_income"],
            }
            for row in report["rows"]
            if row["owner_earnings"] is not None and row["net_income"] is not None
        }
    )

    st.subheader("Two memos: original versus revised")
    memo_cols = st.columns(2)
    with memo_cols[0]:
        st.markdown("#### Original Buffett memo")
        memo = st.text_area(
            "SEC-only memo",
            value=generated_memo(report),
            height=300,
            help="This memo uses only the SEC EDGAR report.",
            key="original_memo",
        )
        flags = memo_number_flags(memo, report)
        if flags:
            st.error(f"Numbers not printed by the script: {', '.join(flags)}")
        else:
            st.success("Every number in the original memo appears in the SEC report.")
    with memo_cols[1]:
        st.markdown("#### Revised Buffett Test Plus memo")
        st.text_area(
            "SEC + Plus memo",
            value=generated_plus_memo(report, plus, discourse, technical),
            height=300,
            help="This memo combines the original test with public research, discourse, and technical context.",
            key="plus_memo",
        )
        st.caption(
            "This revised memo is a research synthesis. Its additional facts come from the visible "
            "Plus, public-discourse, and technical panels above."
        )
