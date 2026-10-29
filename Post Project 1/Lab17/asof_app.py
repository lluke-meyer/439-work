"""FIN 439 Lab 17: FRED and ALFRED point-in-time comparison app."""

from datetime import date
from io import StringIO
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd
import streamlit as st
import altair as alt


FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
ALFRED_URL = "https://alfred.stlouisfed.org/graph/alfredgraph.csv?id={series_id}&vintage_date={vintage_date}"
CORE_SERIES = {
    "BAA": "Moody's Baa corporate bond yield",
    "FEDFUNDS": "Federal funds effective rate",
    "DGS10": "10-year Treasury constant maturity rate",
    "MORTGAGE30US": "30-year fixed mortgage rate",
}
SECONDARY_SERIES = {
    "M2SL": "M2 money stock, seasonally adjusted",
}


def _download_text(url):
    request = Request(url, headers={"User-Agent": "FIN439-Lab17/1.0"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


@st.cache_data(ttl=3600, show_spinner=False)
def download_fred_csv(series_id):
    """Download one current FRED CSV, with no API key."""
    return _download_text(FRED_URL.format(series_id=series_id))


@st.cache_data(ttl=3600, show_spinner=False)
def download_alfred_csv(series_id, vintage_date):
    """Download one ALFRED vintage snapshot, with no API key."""
    return _download_text(
        ALFRED_URL.format(series_id=series_id, vintage_date=vintage_date)
    )


def parse_csv(text, series_id):
    """Convert a FRED/ALFRED CSV response to date/value columns."""
    frame = pd.read_csv(StringIO(text))
    if frame.empty or "observation_date" not in frame.columns:
        raise ValueError("The response did not contain observation_date data")
    value_columns = [column for column in frame.columns if column != "observation_date"]
    if not value_columns:
        raise ValueError("The response did not contain a value column")
    frame = frame.rename(
        columns={"observation_date": "date", value_columns[0]: "value"}
    )
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    frame = frame.dropna(subset=["date", "value"]).drop_duplicates("date")
    if frame.empty:
        raise ValueError(f"{series_id} returned no numeric observations")
    return frame.sort_values("date").reset_index(drop=True)


def get_series(series_id, vintage_date):
    """Return current and as-known data, or a readable error."""
    try:
        current = parse_csv(download_fred_csv(series_id), series_id)
        known = parse_csv(download_alfred_csv(series_id, vintage_date), series_id)
        return current, known, None
    except (HTTPError, URLError, TimeoutError, ValueError, UnicodeError) as error:
        return None, None, f"{type(error).__name__}: {error}"


def as_date(value):
    return pd.Timestamp(value).date()


def restrict(frame, start_date):
    return frame[frame["date"].dt.date >= start_date].copy()


def comparison_row(series_id, current, known, start_date):
    current = restrict(current, start_date)
    known = restrict(known, start_date)
    known_last = known.iloc[-1]
    current_last = current.iloc[-1]
    merged = known.merge(current, on="date", suffixes=("_known", "_current"))
    revised = (merged["value_known"] - merged["value_current"]).abs() > 1e-9
    future_values = current[current["date"] > known_last["date"]]
    return {
        "Series": series_id,
        "FRED page": f"https://fred.stlouisfed.org/series/{series_id}",
        "Last measured known then": as_date(known_last["date"]),
        "Value known then": known_last["value"],
        "Last measured today": as_date(current_last["date"]),
        "Value today": current_last["value"],
        "New values after known date": len(future_values),
        "Revised dates since then": int(revised.sum()),
    }


def series_label(series_id):
    return f"{series_id}: {CORE_SERIES.get(series_id, SECONDARY_SERIES.get(series_id, 'Custom FRED series'))}"


def index_frame(frame):
    """Rebase one series to 100 at its first displayed observation."""
    if frame.empty or frame.iloc[0]["value"] == 0:
        return pd.DataFrame(columns=["date", "value"])
    indexed = frame[["date", "value"]].copy()
    indexed["value"] = indexed["value"] / indexed.iloc[0]["value"] * 100
    return indexed


def build_chart(current_frames, known_frames, focus_id, vintage_date, overlay, show_vintage):
    """Build the single explanatory chart shown by the app."""
    if overlay:
        chart_rows = []
        for series_id, current in current_frames.items():
            indexed = index_frame(current)
            indexed["series"] = series_id
            indexed["line"] = "Current FRED"
            chart_rows.append(indexed)
            if series_id == focus_id and show_vintage:
                known = index_frame(known_frames[series_id])
                known["series"] = series_id
                known["line"] = f"ALFRED known on {vintage_date}"
                chart_rows.append(known)
        data = pd.concat(chart_rows, ignore_index=True)
        y_title = "Indexed value, first displayed observation = 100"
        title = "Selected histories on one comparable scale"
    else:
        current = current_frames[focus_id].copy()
        current["line"] = "Current FRED"
        current = current.rename(columns={"value": "chart_value"})
        chart_rows = [current[["date", "chart_value", "line"]]]
        if show_vintage:
            known = known_frames[focus_id].copy()
            known["line"] = f"ALFRED known on {vintage_date}"
            known = known.rename(columns={"value": "chart_value"})
            chart_rows.append(known[["date", "chart_value", "line"]])
        data = pd.concat(chart_rows, ignore_index=True).rename(
            columns={"chart_value": "value"}
        )
        y_title = "Value in the series' original units"
        title = f"{focus_id}: current history and point-in-time history"

    line = (
        alt.Chart(data)
        .mark_line(interpolate="monotone", strokeWidth=2.5)
        .encode(
            x=alt.X("date:T", title="Measured date"),
            y=alt.Y("value:Q", title=y_title),
            color=alt.Color("series:N" if overlay else "line:N", title="Series"),
            strokeDash=alt.StrokeDash("line:N", title="Version"),
            tooltip=[
                alt.Tooltip("date:T", title="Measured date"),
                alt.Tooltip("value:Q", title="Value", format=",.2f"),
                alt.Tooltip("series:N", title="Series") if overlay else alt.Tooltip("line:N", title="Version"),
            ],
        )
        .properties(title=title, height=470)
        .interactive()
    )
    return line


def main():
    today = date.today()
    st.set_page_config(
        page_title="Signal Canvas | FRED and ALFRED",
        page_icon="📈",
        layout="wide",
    )
    st.markdown(
        """
        <style>
        :root {
            --background-color: #f7f8fc !important;
            --secondary-background-color: #eef2ff !important;
            --text-color: #172033 !important;
        }
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {
            background: #f7f8fc !important;
            color: #172033 !important;
        }
        [data-testid="stHeader"] { background: rgba(247,248,252,0.9) !important; }
        [data-testid="stMain"] h1,
        [data-testid="stMain"] h2,
        [data-testid="stMain"] h3,
        [data-testid="stMain"] h4,
        [data-testid="stMain"] p,
        [data-testid="stMain"] label,
        [data-testid="stMain"] [data-testid="stWidgetLabel"],
        [data-testid="stMain"] [data-testid="stMarkdownContainer"],
        [data-testid="stMain"] [data-testid="stMarkdownContainer"] *,
        [data-testid="stMain"] [data-testid="stCaptionContainer"],
        [data-testid="stMain"] [data-testid="stCaptionContainer"] *,
        [data-testid="stMain"] [data-testid="stMetricLabel"],
        [data-testid="stMain"] [data-testid="stMetricLabel"] *,
        [data-testid="stMain"] [data-testid="stMetricValue"],
        [data-testid="stMain"] [data-testid="stMetricValue"] * {
            color: #172033 !important;
        }
        .hero {
            background: linear-gradient(120deg, #172554 0%, #312e81 52%, #0f766e 100%);
            border-radius: 22px; padding: 2rem 2.2rem; color: white;
            box-shadow: 0 14px 32px rgba(30,41,59,0.18); margin-bottom: 1.2rem;
        }
        .hero h1 { color: white !important; margin: 0; font-size: 2.35rem; }
        .hero p { color: #dbeafe !important; margin: .45rem 0 0; font-size: 1.05rem; }
        .eyebrow { color: #99f6e4; font-size: .78rem; font-weight: 700;
                   letter-spacing: .12em; text-transform: uppercase; }
        [data-testid="stMetric"] { background: white; border: 1px solid #e2e8f0;
            border-radius: 14px; padding: .65rem .85rem; }
        </style>
        <div class="hero">
            <div class="eyebrow">FIN 439 | point in time lab</div>
            <h1>Signal Canvas</h1>
            <p>See what a series looked like then, what it looks like now, and where revisions entered the picture.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "Data from FRED and ALFRED, Federal Reserve Bank of St. Louis, "
        f"downloaded {today.isoformat()}; built with AI help, a learning demonstration, not investment advice."
    )

    with st.sidebar:
        st.header("Build your view")
        st.write("Choose a focus series. Add other series only when you want to compare their paths on the same indexed chart.")
        selected_core = st.multiselect(
            "Interest rate series",
            options=list(CORE_SERIES),
            default=list(CORE_SERIES),
            format_func=series_label,
        )
        selected_secondary = st.multiselect(
            "Secondary series",
            options=list(SECONDARY_SERIES),
            default=["M2SL"],
            format_func=series_label,
        )
        custom_id = st.text_input("Add another FRED series ID", value="").strip().upper()
        start_date = st.date_input("Start date", value=date(2020, 1, 1), max_value=today)
        vintage_date = st.date_input("As known on", value=today, max_value=today)

    selected = list(dict.fromkeys(selected_core + selected_secondary))
    if custom_id and custom_id not in selected:
        selected.append(custom_id)
    if not selected:
        st.warning("Select at least one series.")
        return
    if start_date > vintage_date:
        st.error("Start date must be on or before the as-known-on date.")
        return

    default_focus = "DGS10" if "DGS10" in selected else selected[0]
    focus_id = st.selectbox(
        "Focus series",
        options=selected,
        index=selected.index(default_focus),
        format_func=series_label,
        help="The focus series is shown in its original units when overlay mode is off.",
    )
    overlay = st.checkbox(
        "Overlay the other selected series",
        value=False,
        help="Overlay mode rebases every selected current history to 100 so unlike units can share one chart.",
    )
    show_vintage = st.checkbox(
        f"Show the ALFRED version known on {vintage_date.isoformat()}",
        value=True,
    )

    st.subheader("One chart, two points in time")
    st.write(
        f"The focus is {focus_id}. Current FRED data show the latest downloadable history. "
        f"The ALFRED line shows only information available on {vintage_date.isoformat()}."
    )

    current_frames = {}
    known_frames = {}
    rows = []
    errors = []
    for series_id in selected:
        current, known, error = get_series(series_id, vintage_date.isoformat())
        if error:
            errors.append((series_id, error))
            continue
        current = restrict(current, start_date)
        known = restrict(known, start_date)
        if current.empty or known.empty:
            errors.append((series_id, "No observations remain after the start date."))
            continue
        current_frames[series_id] = current
        known_frames[series_id] = known
        rows.append(comparison_row(series_id, current, known, start_date))

    for series_id, error in errors:
        st.error(f"{series_id}: {error}")

    if focus_id not in current_frames:
        st.error(f"The focus series {focus_id} could not be loaded. Choose another series.")
        return

    if current_frames:
        st.altair_chart(
            build_chart(
                current_frames,
                known_frames,
                focus_id,
                vintage_date.isoformat(),
                overlay,
                show_vintage,
            ),
            width="stretch",
        )
        if overlay:
            st.info(
                "Overlay mode uses an index: every line begins at 100. This highlights direction and timing, not the size of the underlying units."
            )
        else:
            st.info(
                "Read the solid line as the current history. The dashed line is the history available on the selected as-known date. A gap means later data had not been published yet."
            )

    metric_one, metric_two, metric_three = st.columns(3)
    focus_row = next(row for row in rows if row["Series"] == focus_id)
    metric_one.metric("Focus series", focus_id)
    metric_two.metric("Last known value", f"{focus_row['Value known then']:.2f}")
    metric_three.metric("Revised dates", f"{focus_row['Revised dates since then']}")

    if rows:
        st.subheader("Comparison table")
        st.caption("This table makes the point-in-time test explicit: what was known then, what is available now, and how much changed.")
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


if __name__ == "__main__":
    main()


###This report was written for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research and it is not financial advice.

###AI assistance: drafted with [Codex], resumed from my Lab 03 session; sources gathered and verified by me; the judgments are mine.

###Any remaining errors are my own.
