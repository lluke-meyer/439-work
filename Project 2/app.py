"""Streamlit interface for the FIN 439 Project 2 portfolio prototype."""

from __future__ import annotations

import io
from pathlib import Path

import streamlit as st

from backtest import (
    DEFAULT_BILLS_RETURN_PERCENT,
    DEFAULT_LAG_MONTHS,
    DEFAULT_SWITCH_COST_PERCENT,
    run_backtest,
)
from market_data import MarketDataError, fetch_yahoo_monthly_csv
from mandate_finder import mandate_boundaries, numerical_mandate_pass
from auto_pass import best_numerical_mix, usable_return_target
from process_audit import full_process_pass_report
from portfolio import (
    ASSETS,
    audit_theme_portfolios,
    CORRELATIONS,
    EXPECTED_RETURNS,
    MAX_DRAWDOWN,
    MAX_BITCOIN_WEIGHT,
    MAX_GROSS_EXPOSURE,
    MAX_OVERLAP_WEIGHT,
    MAX_PAIRWISE_OVERLAP_WEIGHT,
    MAX_SHORT_WEIGHT,
    MAX_TICKER_WEIGHT,
    OVERLAP_CORRELATION_THRESHOLD,
    OBJECTIVE_RETURN,
    RESERVE_ELIGIBLE,
    RESERVE_MINIMUM,
    SCENARIO_EXPECTED_RETURNS,
    TURNOVER_LIMIT,
    VOLATILITIES,
    THEME_DESCRIPTIONS,
    THEME_PORTFOLIOS,
    available_assets,
    covariance_matrix,
    equal_weight,
    estimate_from_prices,
    extend_estimate_with_candidates,
    inverse_volatility,
    overlap_bucket_weights,
    overlap_groups_for_assets,
    overlap_notes_for_groups,
    pairwise_overlap_rows,
    portfolio_max_drawdown,
    portfolio_result,
    risk_level_portfolios,
    search_lowest_risk_mix,
)


@st.cache_data(ttl=3600, show_spinner=False)
def cached_yahoo_monthly_csv(tickers: tuple[str, ...], lookback_years: int) -> str:
    return fetch_yahoo_monthly_csv(tickers, lookback_years=lookback_years)


@st.cache_data(show_spinner=False)
def cached_theme_audit(
    themes: tuple[tuple[str, tuple[str, ...]], ...],
    assets: tuple[str, ...],
    expected_returns: tuple[float, ...],
    volatilities: tuple[float, ...],
    correlation: tuple[tuple[float, ...], ...],
    objective: float,
    reserve_minimum: float,
    max_overlap_weight: float,
    max_asset_weight: float,
    max_pairwise_overlap_weight: float,
    correlation_threshold: float,
    allow_shorting: bool,
    max_short_weight: float,
    max_gross_exposure: float,
    step: float,
    max_bitcoin_weight: float,
) -> tuple[dict[str, object], ...]:
    return audit_theme_portfolios(
        themes,
        assets,
        expected_returns,
        volatilities,
        correlation,
        objective,
        reserve_minimum,
        max_overlap_weight,
        max_asset_weight,
        max_pairwise_overlap_weight,
        correlation_threshold,
        allow_shorting,
        max_short_weight,
        max_gross_exposure,
        step,
        max_bitcoin_weight,
    )


st.set_page_config(page_title="Project 2 | Portfolio Decision", layout="wide")
st.markdown(
    """
    <style>
    .block-container { max-width: 1240px; padding-top: 2.5rem; padding-bottom: 7rem; }
    .p2-hero { background: linear-gradient(125deg, #112739, #173c49 65%, #255b59);
        border-radius: 18px; color: #fff; padding: 2.2rem 2.5rem; margin-bottom: 1rem; }
    .p2-eyebrow { color: #9cd9cc; font-size: .76rem; font-weight: 700;
        letter-spacing: .16em; text-transform: uppercase; margin-bottom: .7rem; }
    .p2-hero h1 { color: #fff; font-size: clamp(2rem, 4vw, 3.2rem);
        line-height: 1.1; letter-spacing: -.035em; margin: 0 0 .7rem; }
    .p2-hero p { color: #d6e7e6; font-size: 1rem; line-height: 1.55;
        max-width: 780px; margin: 0; }
    .p2-summary-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: .75rem; margin-bottom: .8rem; }
    .p2-summary-card { min-width: 0; min-height: 6.5rem; padding: .95rem 1.05rem;
        border: 1px solid #dce7e5; border-radius: 14px; background: #f8fbfa; }
    .p2-summary-card span { display: block; color: #41535a; font-size: .84rem;
        font-weight: 600; margin-bottom: .4rem; }
    .p2-summary-card strong { display: block; color: #183343; font-size: 1.28rem;
        line-height: 1.2; overflow-wrap: anywhere; }
    [data-testid="stLayoutWrapper"]:has(> * > .st-key-committee_verdict),
    [data-testid="stLayoutWrapper"]:has(> .st-key-committee_verdict) {
        position: fixed; bottom: 1rem; right: 1.25rem; z-index: 999;
        width: min(34rem, calc(100vw - 2.5rem)); }
    .st-key-committee_verdict { background: #fff; border: 1px solid #ccd9d7;
        border-radius: 12px; box-shadow: 0 6px 20px rgba(17, 39, 57, .13);
        padding: .7rem .9rem; min-height: 3.4rem; overflow: visible; }
    .p2-verdict-bar { display: flex; flex-wrap: wrap; align-items: center;
        gap: .5rem 1.2rem; min-height: 2rem; line-height: 1.2; }
    .p2-verdict-item { display: inline-flex; align-items: center; gap: .45rem; }
    .p2-verdict-label { color: #41535a; font-size: .83rem; font-weight: 600; }
    .p2-verdict-value { border-radius: 999px; padding: .22rem .65rem;
        font-size: .82rem; font-weight: 750; white-space: nowrap; }
    .p2-verdict-value.pass { background: #d9f3e8; color: #135d40; }
    .p2-verdict-value.fail { background: #fbe7e5; color: #93342c; }
    .p2-verdict-value.review { background: #fff1d7; color: #80570d; }
    @media (max-width: 900px) { .p2-summary-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
    @media (max-width: 640px) {
        .p2-summary-grid { grid-template-columns: 1fr; }
        [data-testid="stLayoutWrapper"]:has(> * > .st-key-committee_verdict),
        [data-testid="stLayoutWrapper"]:has(> .st-key-committee_verdict) {
            bottom: .65rem; right: .65rem; width: calc(100vw - 1.3rem); }
    }
    .p2-section-label { color: #2d7770; font-size: .76rem; font-weight: 700;
        letter-spacing: .14em; text-transform: uppercase; margin: .2rem 0 .15rem; }
    </style>
    """,
    unsafe_allow_html=True,
)
# The container is placed first and populated after the controls and calculations run.
hero = st.container(border=True)
verdict_strip = st.container(key="committee_verdict")
pending_auto_pass = st.session_state.pop("auto_pass_pending", None)
if pending_auto_pass is not None:
    restoring = pending_auto_pass.get("action") == "restore"
    st.session_state["p2_objective_pct"] = (
        pending_auto_pass["previous_target_pct"] if restoring else pending_auto_pass["target_pct"]
    )
    weights_to_apply = pending_auto_pass["previous_weight_pct"] if restoring else pending_auto_pass["weight_pct"]
    for asset, weight_pct in weights_to_apply.items():
        st.session_state[f"mandate_weight_{pending_auto_pass['universe_key']}_{asset}"] = weight_pct
    if restoring:
        st.session_state.pop("auto_pass_active", None)
    else:
        st.session_state["auto_pass_active"] = pending_auto_pass
if "p2_objective_pct" not in st.session_state:
    st.session_state["p2_objective_pct"] = OBJECTIVE_RETURN * 100

with st.sidebar:
    st.header("Controls")
    st.caption("Changes here update the decision above.")
    with st.expander("Portfolio mandate", expanded=True):
        objective = st.number_input(
            "Objective return (%)", min_value=-25.0, max_value=50.0, step=0.1,
            key="p2_objective_pct",
        ) / 100
        reserve_minimum = st.number_input(
            "Reserve minimum (%)", min_value=0.0, max_value=100.0, value=RESERVE_MINIMUM * 100, step=1.0
        ) / 100
        portfolio_value_millions = st.number_input(
            "Portfolio size ($ millions)", min_value=1.0, max_value=10000.0, value=100.0, step=1.0
        )
        max_ticker_weight = st.number_input(
            "Maximum ticker weight (%)", min_value=5.0, max_value=100.0,
            value=MAX_TICKER_WEIGHT * 100, step=5.0
        ) / 100
        max_bitcoin_weight = st.number_input(
            "Maximum FBTC weight (%)", min_value=0.0, max_value=40.0,
            value=MAX_BITCOIN_WEIGHT * 100, step=5.0,
            help="A separate concentration screen for the single-asset bitcoin ETP."
        ) / 100
        exposure_policy = st.selectbox(
            "Exposure policy",
            options=("Bounded shorting + 10% gross leverage", "No shorts / 100% gross ETF implementation"),
            index=0,
            help="The bounded policy permits short positions up to 10% per ticker and gross exposure up to 110%.",
        )
        allow_shorting = exposure_policy.startswith("Bounded")
        max_short_weight = st.number_input(
            "Maximum short weight (%)", min_value=0.0, max_value=50.0,
            value=MAX_SHORT_WEIGHT * 100, step=5.0, disabled=not allow_shorting
        ) / 100
        max_gross_exposure = st.number_input(
            "Maximum gross exposure (%)", min_value=100.0, max_value=300.0,
            value=(MAX_GROSS_EXPOSURE if allow_shorting else 1.0) * 100, step=5.0,
            disabled=not allow_shorting,
        ) / 100
    with st.expander("Risk and governance limits", expanded=False):
        derivative_policy = st.selectbox(
            "Derivative policy",
            options=(
                "Permitted for hedging; contracts not priced in this app",
                "Not permitted",
            ),
            index=0,
            help="The price-only engine does not model contract selection, margin, Greeks, or counterparty exposure.",
        )
        max_overlap_weight = st.number_input(
            "Maximum overlap bucket (%)", min_value=10.0, max_value=100.0,
            value=MAX_OVERLAP_WEIGHT * 100, step=5.0
        ) / 100
        max_pairwise_overlap_weight = st.number_input(
            "Maximum high-correlation pair (%)", min_value=10.0, max_value=100.0,
            value=MAX_PAIRWISE_OVERLAP_WEIGHT * 100, step=5.0
        ) / 100
        overlap_correlation_threshold = st.number_input(
            "High-correlation threshold (%)", min_value=50.0, max_value=100.0,
            value=OVERLAP_CORRELATION_THRESHOLD * 100, step=5.0
        ) / 100
        max_drawdown = st.number_input(
            "Drawdown review trigger (%)", min_value=5.0, max_value=60.0,
            value=MAX_DRAWDOWN * 100, step=1.0
        ) / 100
        liquidity_floor = st.number_input(
            "Liquidity floor within 10 business days (%)", min_value=0.0, max_value=100.0,
            value=75.0, step=5.0
        ) / 100
        turnover_limit = st.number_input(
            "Annual one-way turnover limit (%)", min_value=5.0, max_value=100.0,
            value=TURNOVER_LIMIT * 100, step=5.0
        ) / 100
    with st.expander("Price data", expanded=False):
        uploaded = st.file_uploader("Upload prices.csv", type="csv")
        data_source = st.radio(
            "Price source",
            options=("Bundled CSV", "Yahoo Finance (live)"),
            index=0,
            disabled=uploaded is not None,
            help="Bundled Close/Last is reproducible. Yahoo uses adjusted close when available, otherwise close; verify the source before relying on it.",
        )
        yahoo_lookback_years = st.selectbox(
            "Yahoo lookback (years)", options=(3, 5, 10), index=1, disabled=data_source != "Yahoo Finance (live)"
        )
        classroom_inputs = st.checkbox(
            "Use Meridian classroom inputs instead of bundled prices",
            value=False,
            disabled=uploaded is not None,
        )
        window_options = (
            ("Full available history", "Last 24 monthly returns", "Last 36 monthly returns")
            if uploaded is not None or data_source == "Yahoo Finance (live)"
            else ("Full available history", "Last 24 monthly returns")
        )
        window_choice = st.selectbox(
            "Estimation window",
            options=window_options,
            disabled=classroom_inputs and uploaded is None,
            help="Changes the price-based volatility, correlation, and drawdown screens. Expected returns remain editable scenario assumptions.",
        )
        return_window = {"Last 24 monthly returns": 24, "Last 36 monthly returns": 36}.get(window_choice)
    with st.expander("Signal sensitivity", expanded=False):
        st.subheader("Signal controls")
        signal_lag = st.number_input(
            "Signal lag (months)", min_value=0, max_value=1, value=DEFAULT_LAG_MONTHS, step=1
        )
        switch_cost = st.number_input(
            "Switch cost (%)", min_value=0.0, max_value=5.0, value=DEFAULT_SWITCH_COST_PERCENT, step=0.05
        )
        bills_return = st.number_input(
            "Bills return (%)", min_value=-10.0, max_value=10.0,
            value=DEFAULT_BILLS_RETURN_PERCENT, step=0.05
        )

if uploaded is None and classroom_inputs:
    assets = ASSETS
    loaded_expected = EXPECTED_RETURNS
    loaded_volatility = VOLATILITIES
    loaded_correlation = CORRELATIONS
    current_expected_defaults = EXPECTED_RETURNS
    current_volatility = VOLATILITIES
    current_correlation = CORRELATIONS
    loaded_monthly_returns = None
    current_monthly_returns = None
    default_reserve = RESERVE_ELIGIBLE
    source_label = "Meridian training inputs"
    observation_label = "Course-authored inputs"
else:
    try:
        bundled_path = Path(__file__).with_name("prices.csv")
        if uploaded is not None:
            price_source = uploaded
            source_label_override = "Uploaded fund universe"
        elif data_source == "Yahoo Finance (live)":
            bundled_assets = estimate_from_prices(bundled_path)["assets"]
            live_tickers = available_assets(bundled_assets)
            try:
                live_csv = cached_yahoo_monthly_csv(tuple(live_tickers), int(yahoo_lookback_years))
                price_source = io.StringIO(live_csv)
                source_label_override = f"Yahoo Finance live universe ({yahoo_lookback_years}-year lookback)"
            except MarketDataError as error:
                st.warning(
                    f"Live retrieval was unavailable, so the app is using the bundled CSV instead: {error}"
                )
                price_source = bundled_path
                source_label_override = "Bundled ten-fund universe (live fallback)"
        else:
            price_source = bundled_path
            source_label_override = "Bundled ten-fund universe"
        loaded_estimate = extend_estimate_with_candidates(estimate_from_prices(price_source))
        if return_window is not None and loaded_estimate["return_observations"] < return_window:
            st.warning(
                f"This source has fewer than {return_window} monthly returns. "
                "Showing the full available window instead."
            )
            return_window = None
        current_estimate = extend_estimate_with_candidates(
            estimate_from_prices(price_source, return_window=return_window)
        )
    except (OSError, ValueError) as error:
        st.error(str(error))
        st.stop()
    assets = loaded_estimate["assets"]
    loaded_expected = tuple(SCENARIO_EXPECTED_RETURNS.get(asset, 0.0) for asset in assets)
    loaded_volatility = loaded_estimate["volatilities"]
    loaded_correlation = loaded_estimate["correlations"]
    current_expected_defaults = tuple(SCENARIO_EXPECTED_RETURNS.get(asset, 0.0) for asset in assets)
    current_volatility = current_estimate["volatilities"]
    current_correlation = current_estimate["correlations"]
    loaded_monthly_returns = loaded_estimate["monthly_returns"]
    current_monthly_returns = current_estimate["monthly_returns"]
    # Only the short Treasury-bill sleeve counts as the working reserve.
    default_reserve = tuple(asset.upper() == "SGOV" for asset in assets)
    source_label = source_label_override
    source_caveat = (
        "uploaded prices require independent adjustment and provenance review"
        if uploaded is not None
        else "Yahoo adjusted-close availability and fallback require review"
        if source_label_override.startswith("Yahoo Finance live")
        else "bundled Close/Last excludes cash distributions"
    )
    observation_label = (
        f"{current_estimate['return_observations']} monthly price changes, "
        f"{current_estimate['start_date']} through {current_estimate['end_date']}; "
        f"{source_caveat}. Expected returns are editable scenario assumptions."
    )
    missing_assumptions = [asset for asset in assets if asset not in SCENARIO_EXPECTED_RETURNS]
    if missing_assumptions:
        st.warning(
            f"No default scenario return is defined for {', '.join(missing_assumptions)}. "
            "Those inputs start at 0% and must be reviewed before using the result."
        )

with st.container(border=True):
    st.markdown('<div class="p2-section-label">01 / Set the scenario</div>', unsafe_allow_html=True)
    st.header("Build the portfolio")
    st.caption("Choose up to ten funds, then adjust return assumptions. The mandate finder below tests your own weight mix; policy and signal controls are in the sidebar.")
    st.subheader(source_label)
    st.write(observation_label)
    if not classroom_inputs or uploaded is not None:
        st.warning(
            f"The {objective:.1%} return objective and {reserve_minimum:.0%} reserve threshold are the current displayed controls. "
            "Only SGOV counts as reserve. TLT is optional long-duration risk exposure."
        )

    st.subheader("Funds and starting theme")
    theme_options = ("Custom / current", *THEME_PORTFOLIOS.keys())
    theme_name = st.selectbox(
        "Starting six-fund theme",
        options=theme_options,
        key="project2_theme",
        help="Each theme is a six-fund starting universe. Selecting one replaces the current fund selection; you can edit it afterward.",
    )
    if st.session_state.get("project2_last_theme") != theme_name:
        if theme_name != "Custom / current":
            st.session_state["project2_selected_assets"] = [
                asset for asset in THEME_PORTFOLIOS[theme_name] if asset in assets
            ]
            st.session_state["project2_fund_count"] = 6
            st.session_state["project2_last_fund_count"] = 6
        st.session_state["project2_last_theme"] = theme_name
    if theme_name != "Custom / current":
        st.caption(THEME_DESCRIPTIONS[theme_name])

    if classroom_inputs:
        fund_count_options = (len(assets),)
    else:
        fund_count_options = tuple(range(3, 11))
    default_fund_count = len(assets) if classroom_inputs else 10
    if st.session_state.get("project2_fund_count") not in fund_count_options:
        st.session_state["project2_fund_count"] = default_fund_count
    fund_count = st.selectbox(
        "Fund slots",
        options=fund_count_options,
        key="project2_fund_count",
        help="Choose a portfolio size from 3 through 10. A theme starts with six funds, but the portfolio can be expanded or trimmed afterward.",
    )
    selection_key = "project2_selected_assets"
    if st.session_state.get("project2_last_fund_count") != fund_count:
        st.session_state[selection_key] = list(assets[:fund_count])
        st.session_state["project2_last_fund_count"] = fund_count
    selected_assets = st.multiselect(
        "Funds in the portfolio universe",
        options=list(assets),
        max_selections=fund_count,
        key=selection_key,
        help="Remove a fund or add another available ticker when the selected fund-slot count allows it.",
    )
    if not selected_assets:
        st.error("Select at least one ticker.")
        st.stop()

    full_assets = tuple(assets)
    full_current_expected_defaults = tuple(current_expected_defaults)
    full_current_volatility = tuple(current_volatility)
    full_current_correlation = tuple(tuple(row) for row in current_correlation)
    selected_indices = [assets.index(asset) for asset in selected_assets]
    assets = tuple(selected_assets)
    loaded_expected = tuple(loaded_expected[index] for index in selected_indices)
    loaded_volatility = tuple(loaded_volatility[index] for index in selected_indices)
    loaded_correlation = tuple(
        tuple(loaded_correlation[row][column] for column in selected_indices)
        for row in selected_indices
    )
    current_expected_defaults = tuple(current_expected_defaults[index] for index in selected_indices)
    current_volatility = tuple(current_volatility[index] for index in selected_indices)
    current_correlation = tuple(
        tuple(current_correlation[row][column] for column in selected_indices)
        for row in selected_indices
    )
    default_reserve = tuple(default_reserve[index] for index in selected_indices)
    if loaded_monthly_returns is not None:
        loaded_history_available = all(asset in loaded_monthly_returns for asset in assets)
        loaded_monthly_returns = (
            {asset: loaded_monthly_returns[asset] for asset in assets}
            if loaded_history_available else None
        )
    if current_monthly_returns is not None:
        current_history_available = all(asset in current_monthly_returns for asset in assets)
        current_monthly_returns = (
            {asset: current_monthly_returns[asset] for asset in assets}
            if current_history_available else None
        )
    overlap_groups = overlap_groups_for_assets(assets)
    allocation_step = 0.10 if allow_shorting or len(assets) > 6 else 0.05

    with st.expander("Edit fund estimates and reserve flags", expanded=False):
        st.write(
            "Edit an expected-return scenario or SGOV reserve flag below. These are illustrative assumptions, not forecasts derived from Close/Last prices. "
            f"Allocation grid: {allocation_step:.0%} steps for this universe; exposure policy: {exposure_policy}."
        )

        header = st.columns([1.7, 1.2, 1.2, 1.3])
        header[0].markdown("**Asset**")
        header[1].markdown("**Expected return**")
        header[2].markdown("**Volatility**")
        header[3].markdown("**Reserve eligible**")

        edited_expected: list[float] = []
        reserve_flags: list[bool] = []
        universe_key = "_".join(assets)
        for index, asset in enumerate(assets):
            columns = st.columns([1.7, 1.2, 1.2, 1.3])
            columns[0].write(asset)
            edited_expected.append(
                columns[1].number_input(
                    f"{asset} expected return (%)",
                    min_value=-100.0,
                    max_value=200.0,
                    value=float(current_expected_defaults[index] * 100),
                    step=0.1,
                    format="%.2f",
                    key=f"return_{universe_key}_{asset}",
                    label_visibility="collapsed",
                )
                / 100
            )
            columns[2].write(f"{current_volatility[index]:.2%}")
            selected_reserve = columns[3].checkbox(
                    f"{asset} is reserve eligible",
                    value=default_reserve[index],
                    key=f"reserve_{universe_key}_{asset}",
                    disabled=asset != "SGOV",
                    label_visibility="collapsed",
                )
            reserve_flags.append(asset == "SGOV" and selected_reserve)


current_covariance = covariance_matrix(current_volatility, current_correlation)
loaded_covariance = covariance_matrix(loaded_volatility, loaded_correlation)
current_risk_levels = risk_level_portfolios(
    edited_expected,
    current_covariance,
    objective,
    reserve_flags,
    reserve_minimum,
    overlap_groups=overlap_groups,
    max_overlap_weight=max_overlap_weight,
    max_asset_weight=max_ticker_weight,
    max_pairwise_overlap_weight=max_pairwise_overlap_weight,
    correlation_threshold=overlap_correlation_threshold,
    step=allocation_step,
    allow_shorting=allow_shorting,
    max_short_weight=max_short_weight,
    max_gross_exposure=max_gross_exposure,
    asset_caps=tuple(max_bitcoin_weight if asset == "FBTC" else 1.0 for asset in assets),
)
current_result = current_risk_levels[0] if current_risk_levels else None
loaded_result = search_lowest_risk_mix(
    loaded_expected,
    loaded_covariance,
    objective,
    reserve_flags,
    reserve_minimum,
    overlap_groups=overlap_groups,
    max_overlap_weight=max_overlap_weight,
    max_asset_weight=max_ticker_weight,
    max_pairwise_overlap_weight=max_pairwise_overlap_weight,
    correlation_threshold=overlap_correlation_threshold,
    step=allocation_step,
    allow_shorting=allow_shorting,
    max_short_weight=max_short_weight,
    max_gross_exposure=max_gross_exposure,
    asset_caps=tuple(max_bitcoin_weight if asset == "FBTC" else 1.0 for asset in assets),
)


def mandate_verdict(result: dict[str, object]) -> str:
    return "PASS" if (
        result["expected_return"] >= objective - 1e-12
        and result["reserve_weight"] >= reserve_minimum - 1e-12
        and max(result["weights"]) <= max_ticker_weight + 1e-12
        and all(weight <= max_bitcoin_weight + 1e-12 for asset, weight in zip(assets, result["weights"]) if asset == "FBTC")
        and max(overlap_bucket_weights(result["weights"], overlap_groups, gross=True).values())
        <= max_overlap_weight + 1e-12
        and min(result["weights"]) >= (-max_short_weight if allow_shorting else 0.0) - 1e-12
        and sum(abs(weight) for weight in result["weights"]) <= max_gross_exposure + 1e-12
        and all(
            float(row["Combined weight"]) <= max_pairwise_overlap_weight + 1e-12
            for row in pairwise_overlap_rows(
                result["weights"], assets, current_correlation, overlap_correlation_threshold
            )
        )
    ) else "FAIL"


baseline_results = [
    ("Equal weight", portfolio_result(equal_weight(len(assets)), edited_expected, current_covariance, reserve_flags)),
    ("Inverse volatility", portfolio_result(inverse_volatility(current_volatility), edited_expected, current_covariance, reserve_flags)),
]
if current_result is not None:
    baseline_results.insert(0, ("Constrained search", current_result))


locked_backtest = run_backtest()
adjusted_backtest = run_backtest(
    lag_months=int(signal_lag),
    switch_cost_percent=float(switch_cost),
    bills_return_percent=float(bills_return),
)
leakage_diagnostic = run_backtest(
    lag_months=0,
    switch_cost_percent=DEFAULT_SWITCH_COST_PERCENT,
    bills_return_percent=DEFAULT_BILLS_RETURN_PERCENT,
)


def gate_status(condition: bool | None) -> str:
    if condition is None:
        return "REVIEW"
    return "PASS" if condition else "FAIL"


if current_result is None:
    current_overlap = None
    current_pairwise_overlap = None
    current_drawdown = None
else:
    current_overlap = max(overlap_bucket_weights(current_result["weights"], overlap_groups, gross=True).values())
    pairwise_rows = pairwise_overlap_rows(
        current_result["weights"], assets, current_correlation, overlap_correlation_threshold
    )
    current_pairwise_overlap = max(
        (float(row["Combined weight"]) for row in pairwise_rows), default=0.0
    )
    current_drawdown = (
        portfolio_max_drawdown(current_result["weights"], current_monthly_returns)
        if current_monthly_returns is not None
        else None
    )

sgov_is_reserve = any(asset == "SGOV" and eligible for asset, eligible in zip(assets, reserve_flags))
sgov_history_observed = current_monthly_returns is not None and "SGOV" in current_monthly_returns
reserve_evidence_status = (
    "PASS" if sgov_is_reserve and sgov_history_observed
    else "REVIEW" if sgov_is_reserve
    else gate_status(any(reserve_flags))
)
reserve_evidence_text = (
    "Observed SGOV history selected as reserve evidence"
    if sgov_is_reserve and sgov_history_observed
    else "SGOV candidate selected; upload observed history before relying on it"
    if sgov_is_reserve
    else "Select a reserve-eligible fund"
)
gate_rows = [
    {"Gate": "Return data quality", "Result": "REVIEW", "Evidence": source_caveat + "; return inputs are illustrative scenarios" if not classroom_inputs else "Course-authored training inputs"},
    {"Gate": "Return target", "Result": gate_status(current_result is not None and current_result["expected_return"] >= objective), "Evidence": f"{objective:.1%} minimum"},
    {"Gate": "Reserve floor", "Result": gate_status(current_result is not None and current_result["reserve_weight"] >= reserve_minimum), "Evidence": f"{reserve_minimum:.1%} minimum = ${portfolio_value_millions * reserve_minimum:.2f}m"},
    {"Gate": "Reserve eligibility", "Result": reserve_evidence_status, "Evidence": reserve_evidence_text},
    {"Gate": "Maximum ticker weight", "Result": gate_status(current_result is not None and max(current_result["weights"]) <= max_ticker_weight), "Evidence": f"{max_ticker_weight:.0%} cap"},
    {"Gate": "Bitcoin concentration", "Result": gate_status(current_result is not None and all(weight <= max_bitcoin_weight for asset, weight in zip(assets, current_result["weights"]) if asset == "FBTC")), "Evidence": f"FBTC <= {max_bitcoin_weight:.0%}"},
    {"Gate": "Short and gross exposure", "Result": gate_status(current_result is not None and min(current_result["weights"]) >= (-max_short_weight if allow_shorting else 0.0) - 1e-12 and sum(abs(weight) for weight in current_result["weights"]) <= max_gross_exposure + 1e-12), "Evidence": f"short floor {-max_short_weight:.0%}; gross <= {max_gross_exposure:.0%}" if allow_shorting else "No shorting; gross = 100%"},
    {"Gate": "Overlap proxy", "Result": gate_status(current_overlap is not None and current_overlap <= max_overlap_weight), "Evidence": f"{current_overlap:.1%} / {max_overlap_weight:.0%}" if current_overlap is not None else "No feasible portfolio"},
    {"Gate": "High-correlation pair", "Result": gate_status(current_pairwise_overlap is not None and current_pairwise_overlap <= max_pairwise_overlap_weight), "Evidence": f"{current_pairwise_overlap:.1%} / {max_pairwise_overlap_weight:.0%} at {overlap_correlation_threshold:.0%}+ correlation" if current_pairwise_overlap is not None else "No feasible portfolio"},
    {"Gate": "Historical drawdown", "Result": gate_status(current_drawdown is not None and current_drawdown <= max_drawdown), "Evidence": f"{current_drawdown:.1%} / {max_drawdown:.0%}" if current_drawdown is not None else "No feasible portfolio"},
    {"Gate": "Liquidity", "Result": "REVIEW", "Evidence": f"At least {liquidity_floor:.0%} within 10 business days"},
    {"Gate": "Issuer concentration", "Result": "REVIEW", "Evidence": "Needs holdings-level look-through"},
    {"Gate": "Derivative governance", "Result": "REVIEW" if derivative_policy.startswith("Permitted") else "PASS", "Evidence": derivative_policy},
    {"Gate": "Annual turnover", "Result": gate_status(locked_backtest["development"]["switches"] <= turnover_limit), "Evidence": f"{locked_backtest['development']['switches'] * 100:.0f}% / {turnover_limit:.0%} one-way"},
    {"Gate": "Frozen holdout", "Result": gate_status(not locked_backtest["failure_triggered"]), "Evidence": "Net result versus buy-and-hold"},
]
hard_fail = any(row["Result"] == "FAIL" for row in gate_rows)
needs_review = any(row["Result"] == "REVIEW" for row in gate_rows)
if hard_fail:
    gate_decision = "REJECT / REDESIGN"
elif needs_review:
    gate_decision = "PILOT ONLY"
else:
    gate_decision = "ADOPT CANDIDATE"

# Keep the allocation decision separate from process evidence. The optimizer can
# satisfy the displayed portfolio mandate while the frozen signal, turnover, or
# holdings-level evidence still prevents adoption.
allocation_passes = (
    current_result is not None
    and mandate_verdict(current_result) == "PASS"
    and current_drawdown is not None
    and current_drawdown <= max_drawdown + 1e-12
)
allocation_decision = "PASS" if allocation_passes else "NO FEASIBLE MIX"


if allocation_decision == "NO FEASIBLE MIX":
    hero_summary = "No allocation meets the current mandate. Review the assumptions and limits below."
elif gate_decision == "REJECT / REDESIGN":
    hero_summary = "The allocation meets its numerical limits. The tested process still fails the committee checks."
elif gate_decision == "PILOT ONLY":
    hero_summary = "The allocation meets its numerical limits. Review items remain before an adoption decision."
else:
    hero_summary = "The displayed allocation and process checks pass. Review the supporting evidence before voting."
estimated_return_label = f"{current_result['expected_return']:.2%}" if current_result else "—"
with hero:
    st.markdown(
        f"""<div class="p2-hero">
        <div class="p2-eyebrow">FIN 439 / Project 2 / Investment committee</div>
        <h1>Portfolio review</h1>
        <p>{hero_summary}</p>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="p2-summary-grid">'
        f'<div class="p2-summary-card"><span>Allocation mandate</span><strong>{allocation_decision}</strong></div>'
        f'<div class="p2-summary-card"><span>Full process gate</span><strong>{gate_decision}</strong></div>'
        f'<div class="p2-summary-card"><span>Estimated return</span><strong>{estimated_return_label}</strong></div>'
        f'<div class="p2-summary-card"><span>Frozen holdout net</span><strong>{locked_backtest["holdout"]["net"]:.2%}</strong></div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        f"{len(assets)} selected funds · {source_label} · Holdout buy-and-hold "
        f"{locked_backtest['holdout']['buy_and_hold']:.2%} · Built with AI help; a learning demonstration, not investment advice."
    )
    with st.expander("Committee walkthrough: how to assess this portfolio"):
        st.markdown(
            """1. **Set the mandate.** Confirm the return target, SGOV reserve floor, risk limits, and investment horizon in the sidebar.
2. **Check the funds and inputs.** Review the ten selected funds, editable return assumptions, and price-source limitations in **Set the scenario**.
3. **Compare allocations.** Read the constrained mix and the equal-weight and inverse-volatility baselines in **Allocation**.
4. **Test your own mix.** Enter weights totaling 100% in **Your mandate question**, or use Auto-Pass to find the strongest scenario return under the existing risk limits. Inspect each mandate boundary.
5. **Check the decision gates.** Review reserve, overlap, drawdown, liquidity, and governance in **Decision evidence**. A numerical PASS alone does not approve the process.
6. **Challenge the process.** Compare gross and net results, turnover, and the frozen holdout in **Out-of-sample check**.
7. **Record the call.** Use the visible allocation and full-process verdicts with the memo's reversal conditions before any committee decision."""
        )

with verdict_strip:
    allocation_style = "pass" if allocation_decision == "PASS" else "fail"
    process_style = "fail" if gate_decision == "REJECT / REDESIGN" else "review" if gate_decision == "PILOT ONLY" else "pass"
    st.markdown(
        f'<div class="p2-verdict-bar" role="status" aria-live="polite">'
        f'<span class="p2-verdict-item"><span class="p2-verdict-label">Allocation</span>'
        f'<span class="p2-verdict-value {allocation_style}">{allocation_decision}</span></span>'
        f'<span class="p2-verdict-item"><span class="p2-verdict-label">Full process</span>'
        f'<span class="p2-verdict-value {process_style}">{gate_decision}</span></span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def show_result(container: st.delta_generator.DeltaGenerator, title: str, result: dict[str, object] | None) -> None:
    container.markdown(f"### {title}")
    if result is None:
        container.warning("No mix meets the current mandate and overlap limits.")
        return
    container.dataframe(
        [
            {"Asset": asset, "Weight": f"{weight:.2%}"}
            for asset, weight in zip(assets, result["weights"])
        ],
        hide_index=True,
        width="stretch",
    )
    metrics = container.columns(3)
    metrics[0].metric("Return", f"{result['expected_return']:.2%}")
    metrics[1].metric("Volatility", f"{result['volatility']:.2%}")
    metrics[2].metric("Reserve", f"{result['reserve_weight']:.2%}")
    weights = result["weights"]
    largest_index = max(range(len(weights)), key=weights.__getitem__)
    active_assets = [asset for asset, weight in zip(assets, weights) if weight > 0.001]
    return_cushion = result["expected_return"] - objective
    reserve_cushion = result["reserve_weight"] - reserve_minimum
    with container.expander("What this result means"):
        st.write(
            f"**Main holding:** {assets[largest_index]} at {weights[largest_index]:.0%}. "
            f"The optimizer uses {len(active_assets)} of {len(assets)} available funds: "
            f"{', '.join(active_assets)}."
        )
        st.write(
            f"**Constraint cushion:** expected return is {return_cushion:.2%} above the objective, "
            f"and reserve weight is {reserve_cushion:.2%} above the minimum."
        )
        st.caption(
            "Volatility is an annualized estimate from monthly returns. A zero weight does not "
            "mean a fund is bad; it means that fund did not improve the lowest-risk feasible mix "
            "under these estimates and the displayed allocation grid."
        )


with st.container(border=True):
    st.markdown('<div class="p2-section-label">02 / Allocation</div>', unsafe_allow_html=True)
    st.header("The proposed mix")
    st.caption("The current column uses editable return assumptions. The loaded column keeps the initial scenario assumptions before your edits; risk estimates use the frozen price-only panel.")
    current_column, loaded_column = st.columns(2)
    show_result(current_column, "Current estimates", current_result)
    show_result(loaded_column, "Inputs as loaded", loaded_result)

    st.subheader("Baseline and mandate verdicts")
    st.caption("PASS means the numerical scenario clears the displayed return, reserve, bitcoin, ticker, and overlap controls. It does not certify the data or process.")
    st.dataframe(
        [
            {
                "Portfolio": name,
                "Return": f"{result['expected_return']:.2%}",
                "Volatility": f"{result['volatility']:.2%}",
                "Reserve": f"{result['reserve_weight']:.2%}",
                "Max overlap": f"{max(overlap_bucket_weights(result['weights'], overlap_groups, gross=True).values()):.2%}",
                "Mandate verdict": mandate_verdict(result),
            }
            for name, result in baseline_results
        ],
        hide_index=True,
        width="stretch",
    )


with st.container(border=True):
    st.markdown('<div class="p2-section-label">02a / Your mandate question</div>', unsafe_allow_html=True)
    st.header("What mandate would accept this mix?")
    st.caption(
        "Choose weights across the selected funds to see the limits those exact weights require. "
        "Numerical Auto-Pass searches these funds and, if needed, lowers only the return target. "
        "The full-process button audits every gate without changing evidence or policy."
    )
    auto_pass_context = (
        assets, tuple(edited_expected), current_covariance, tuple(reserve_flags),
        overlap_groups, current_correlation, current_monthly_returns, observation_label,
        reserve_minimum, max_ticker_weight, max_bitcoin_weight, max_overlap_weight,
        max_pairwise_overlap_weight, overlap_correlation_threshold, max_drawdown,
        allow_shorting, max_short_weight, max_gross_exposure, allocation_step,
    )
    numerical_button_col, process_button_col = st.columns(2)
    numerical_clicked = numerical_button_col.button(
        'Auto-Pass numerical mandate',
        help="Find the highest scenario return on this allocation grid while preserving the current reserve and risk controls. If necessary, lower only the return target. The process gate cannot be auto-passed.",
        type="primary",
    )
    process_clicked = process_button_col.button(
        "Auto full-process pass check",
        help="Recheck all displayed gates and show exactly what blocks a real full-process PASS. This cannot waive failed holdout, turnover, or missing evidence.",
    )
    gate_signature = tuple((row["Gate"], row["Result"], row["Evidence"]) for row in gate_rows)
    if process_clicked:
        st.session_state["full_process_audit"] = {
            "signature": gate_signature,
            "report": full_process_pass_report(gate_rows),
        }
    saved_audit = st.session_state.get("full_process_audit")
    if saved_audit is not None:
        if saved_audit["signature"] == gate_signature:
            process_report = saved_audit["report"]
            if process_report["ready"]:
                st.success("All displayed allocation and process gates pass. Committee review of the evidence is still required.")
            else:
                st.warning(
                    f"Full-process Auto-Pass unavailable: {process_report['fail_count']} FAIL and "
                    f"{process_report['review_count']} REVIEW gates. No threshold, test result, or "
                    "evidence status was changed."
                )
                with st.expander("See blockers and actions", expanded=process_clicked):
                    st.dataframe(process_report["blockers"], hide_index=True, width="stretch")
                    st.caption(
                        "A redesigned timing rule needs a new, genuinely out-of-sample test. "
                        "Changing the mandate or retuning the existing holdout cannot create that evidence."
                    )
        else:
            st.info("The gate inputs changed since the full-process check. Click it again for a current audit.")
    if numerical_clicked:
        try:
            auto_result = best_numerical_mix(
                assets=assets, expected_returns=edited_expected, covariance=current_covariance,
                reserve_eligible=reserve_flags, overlap_groups=overlap_groups,
                correlation=current_correlation, monthly_returns=current_monthly_returns,
                reserve_floor=reserve_minimum, ticker_cap=max_ticker_weight,
                bitcoin_cap=max_bitcoin_weight, bucket_cap=max_overlap_weight,
                pair_cap=max_pairwise_overlap_weight,
                correlation_threshold=overlap_correlation_threshold,
                drawdown_tolerance=max_drawdown, allow_shorting=allow_shorting,
                short_allowance=max_short_weight if allow_shorting else 0.0,
                gross_cap=max_gross_exposure if allow_shorting else 1.0,
                step=allocation_step,
            )
        except ValueError as error:
            st.warning(f"Auto-Pass cannot run: {error}")
        else:
            if auto_result is None:
                st.warning(
                    "No allocation passes the reserve and risk controls for these selected funds. "
                    "Auto-Pass will not silently remove the reserve or raise a risk cap."
                )
            else:
                target = usable_return_target(objective, float(auto_result["expected_return"]))
                if target < -0.25:
                    st.warning("The compatible return target is below the control's -25% lower bound.")
                else:
                    st.session_state["auto_pass_pending"] = {
                        "universe_key": universe_key,
                        "target_pct": round(target * 100, 1),
                        "weight_pct": {
                            asset: round(weight * 100, 1)
                            for asset, weight in zip(assets, auto_result["weights"])
                        },
                        "previous_target_pct": round(objective * 100, 1),
                        "previous_weight_pct": {
                            asset: float(st.session_state[f"mandate_weight_{universe_key}_{asset}"])
                            for asset in assets
                        },
                        "old_target": objective,
                        "expected_return": float(auto_result["expected_return"]),
                        "volatility": float(auto_result["volatility"]),
                        "drawdown": float(auto_result["drawdown"]),
                        "context": auto_pass_context,
                    }
                    st.rerun()
    weight_units, weight_remainder = divmod(1000, len(assets))
    chosen_weight_points: list[float] = []
    weight_columns = st.columns(2)
    for index, asset in enumerate(assets):
        default_points = (weight_units + (1 if index < weight_remainder else 0)) / 10
        weight_key = f"mandate_weight_{universe_key}_{asset}"
        if weight_key not in st.session_state:
            st.session_state[weight_key] = default_points
        chosen_weight_points.append(weight_columns[index % 2].number_input(
            f"{asset} chosen weight (%)",
            min_value=-10.0 if allow_shorting else 0.0,
            max_value=100.0,
            step=0.1,
            format="%.1f",
            key=weight_key,
        ))
    weight_total = sum(chosen_weight_points)
    st.caption(f"Chosen weights total: {weight_total:.1f}%. Equal weights are an illustrative starting point, not a recommendation.")
    if abs(weight_total - 100.0) > 0.01:
        st.warning("Enter weights totaling exactly 100% to calculate mandate boundaries.")
    else:
        chosen_weights = tuple(point / 100 for point in chosen_weight_points)
        boundaries = mandate_boundaries(
            chosen_weights, assets, edited_expected, current_covariance, reserve_flags,
            overlap_groups, current_correlation, current_monthly_returns,
            overlap_correlation_threshold,
        )
        current_limits = {
            "return_target": objective,
            "reserve_floor": reserve_minimum,
            "ticker_cap": max_ticker_weight,
            "bitcoin_cap": max_bitcoin_weight,
            "short_allowance": max_short_weight if allow_shorting else 0.0,
            "gross_cap": max_gross_exposure if allow_shorting else 1.0,
            "bucket_cap": max_overlap_weight,
            "pair_cap": max_pairwise_overlap_weight,
            "drawdown_tolerance": max_drawdown,
        }
        bound_specs = (
            ("Return target", "At most", "maximum_return_target", objective),
            ("Reserve floor", "At most", "maximum_reserve_floor", reserve_minimum),
            ("Ticker cap", "At least", "minimum_ticker_cap", max_ticker_weight),
            ("Bitcoin cap", "At least", "minimum_bitcoin_cap", max_bitcoin_weight),
            ("Short allowance", "At least", "minimum_short_allowance", current_limits["short_allowance"]),
            ("Gross exposure cap", "At least", "minimum_gross_cap", current_limits["gross_cap"]),
            ("Broad-bucket cap", "At least", "minimum_bucket_cap", max_overlap_weight),
            ("High-correlation pair cap", "At least", "minimum_pair_cap", max_pairwise_overlap_weight),
            ("Drawdown tolerance", "At least", "minimum_drawdown_tolerance", max_drawdown),
        )
        bound_rows = []
        for name, direction, key, current_limit in bound_specs:
            boundary = boundaries[key]
            passes = boundary is not None and (
                current_limit <= boundary + 1e-12 if direction == "At most"
                else current_limit + 1e-12 >= boundary
            )
            bound_rows.append({
                "Mandate control": name,
                "Chosen mix requires": f"{direction} {boundary:.2%}" if boundary is not None else "Observed history required",
                "Current mandate": f"{current_limit:.2%}",
                "Current check": "PASS" if passes else "FAIL" if boundary is not None else "REVIEW",
            })
        st.dataframe(bound_rows, hide_index=True, width="stretch")
        auto_pass_active = st.session_state.get("auto_pass_active")
        if auto_pass_active is not None:
            auto_weights_match = all(
                abs(point - auto_pass_active["weight_pct"].get(asset, float("nan"))) < 0.01
                for asset, point in zip(assets, chosen_weight_points)
            )
            if (
                auto_pass_active["context"] == auto_pass_context
                and abs(objective * 100 - auto_pass_active["target_pct"]) < 0.01
                and auto_weights_match
            ):
                old_target = auto_pass_active["old_target"]
                st.success(
                    f"Auto-Pass applied: return target {old_target:.2%} → {objective:.2%}; "
                    f"selected weights yield {auto_pass_active['expected_return']:.2%} scenario return. "
                    "Reserve and risk controls were kept."
                )
                st.caption(
                    f"Optimization: highest scenario return on the {allocation_step:.0%} weight grid, "
                    f"then lowest volatility among ties. Estimated volatility "
                    f"{auto_pass_active['volatility']:.2%}; historical price drawdown "
                    f"{auto_pass_active['drawdown']:.2%}. Selected funds may receive zero weight. "
                    "This is a scenario screen, not an investable forecast."
                )
                if st.button("Restore inputs before Auto-Pass"):
                    st.session_state["auto_pass_pending"] = {
                        **auto_pass_active, "action": "restore"
                    }
                    st.rerun()
            else:
                st.info("The current inputs differ from the last Auto-Pass run. Run it again to refresh the proposal.")
        st.caption(
            f"Binding broad bucket: {boundaries['binding_bucket']}. "
            f"Binding correlated pair: {boundaries['binding_pair']}. "
            "The drawdown screen uses price-only closes; cash distributions are excluded."
        )
        fixed_allocation_pass = numerical_mandate_pass(boundaries, current_limits)
        process_checks = [row for row in gate_rows if row["Gate"] in {
            "Return data quality",
            "Reserve eligibility", "Liquidity", "Issuer concentration", "Derivative governance",
            "Annual turnover", "Frozen holdout",
        }]
        process_failures = [row["Gate"] for row in process_checks if row["Result"] == "FAIL"]
        process_reviews = [row["Gate"] for row in process_checks if row["Result"] == "REVIEW"]
        st.metric("Chosen mix / numerical mandate", "PASS" if fixed_allocation_pass else "FAIL")
        if process_failures or process_reviews:
            st.warning(
                "Both gates: NO. No change to the numerical mandate can clear the current process "
                f"evidence. Failed: {', '.join(process_failures) or 'none'}. "
                f"Review: {', '.join(process_reviews) or 'none'}."
            )
        elif fixed_allocation_pass:
            st.success("Both displayed gates pass for this fixed mix, subject to committee review of assumptions and source quality.")
        else:
            st.warning("The process checks pass, but the chosen mix misses at least one current numerical mandate limit.")


with st.container(border=True):
    st.markdown('<div class="p2-section-label">03 / Decision evidence</div>', unsafe_allow_html=True)
    st.header("Why the committee call holds")
    st.caption(
        "Working policy: five-year horizon, quarterly committee review, annual core-portfolio "
        "rebalance. The monthly classroom timing signal is a separate test, not realized "
        "performance of this ETF mix."
    )
    st.caption("A hard failure means reject/redesign; a review item means the evidence is incomplete.")
    st.caption(
        "Allocation PASS means the selected weights satisfy the displayed return, reserve, bitcoin, ticker, "
        "exposure, overlap, and drawdown controls. The full process gate also requires the frozen "
        "signal, turnover, liquidity, issuer, reserve, derivative, and holdout evidence."
    )
    st.dataframe(gate_rows, hide_index=True, width="stretch")
    st.info(
        "[SGOV](https://www.ishares.com/us/products/314116/ishares-03-month-treasury-bond-etf) holds "
        "0–3 month Treasury bills and is the only working reserve candidate. "
        "[TLT](https://www.ishares.com/us/products/239454/ishares-20-plus-year-treasury-bond-etf) "
        "is optional long-duration Treasury exposure and never counts toward the reserve floor. "
        "The committee still needs to approve the final reserve and liquidity policy."
    )
    st.info(
        f"Exposure disclosure: {exposure_policy}. Derivative disclosure: {derivative_policy}. "
        "This app can screen bounded portfolio weights, but it does not price derivative contracts or model margin, Greeks, financing spreads, or counterparty exposure."
    )


with st.container(border=True):
    st.markdown('<div class="p2-section-label">04 / Out-of-sample check</div>', unsafe_allow_html=True)
    st.header("The frozen signal and its holdout")
    st.caption(
        "The frozen result uses the one-month lag, 0.10% switch cost, and 0.30% bills return. "
        "Sidebar controls run bounded sensitivity scenarios; they do not retune the holdout."
    )
    backtest_columns = st.columns(2)
    for container, title, result in (
        (backtest_columns[0], "Frozen classroom rule", locked_backtest),
        (backtest_columns[1], "Adjusted sensitivity", adjusted_backtest),
    ):
        container.markdown(f"### {title}")
        development = result["development"]
        holdout = result["holdout"]
        container.dataframe(
            [
                {
                    "Period": "Development",
                    "Rule gross": f"{development['gross']:.2%}",
                    "Rule net": f"{development['net']:.2%}",
                    "Buy-and-hold": f"{development['buy_and_hold']:.2%}",
                    "Switches": development["switches"],
                },
                {
                    "Period": "Holdout",
                    "Rule gross": f"{holdout['gross']:.2%}",
                    "Rule net": f"{holdout['net']:.2%}",
                    "Buy-and-hold": f"{holdout['buy_and_hold']:.2%}",
                    "Switches": holdout["switches"],
                },
            ],
            hide_index=True,
            width="stretch",
        )
        if result["failure_triggered"]:
            container.warning("Failure rule triggered: holdout net trails buy-and-hold.")
        else:
            container.success("Failure rule not triggered.")

    if current_result is not None:
        holdout_passes = not adjusted_backtest["failure_triggered"]
        if allocation_passes and holdout_passes and gate_decision != "REJECT / REDESIGN":
            st.success("Current process verdict: pilot candidate, subject to final mandate and evidence review.")
        else:
            st.warning(
                f"Allocation mandate: {allocation_decision}. Full process verdict: {gate_decision}; "
                "turnover, reserve/liquidity/issuer evidence, derivative governance, or the holdout "
                "still needs resolution before adoption."
            )

    st.subheader("Leakage falsification check")
    st.caption(
        "This diagnostic intentionally removes the one-month availability lag. It is not a candidate "
        "strategy or a retuned holdout; the jump in development performance is evidence that the lag "
        "is necessary."
    )
    st.dataframe(
        [
            {
                "Run": "Frozen one-month lag",
                "Development net": f"{locked_backtest['development']['net']:.2%}",
                "Use": "Frozen evidence",
            },
            {
                "Run": "Zero-lag diagnostic",
                "Development net": f"{leakage_diagnostic['development']['net']:.2%}",
                "Use": "Rejected leakage diagnostic",
            },
        ],
        hide_index=True,
        width="stretch",
    )
    st.warning(
        f"The zero-lag diagnostic rises to {leakage_diagnostic['development']['net']:.2%} development net. "
        "That is a look-ahead warning, so the one-month lag stays frozen."
    )


with st.container(border=True):
    st.markdown('<div class="p2-section-label">05 / Exposure detail</div>', unsafe_allow_html=True)
    st.header("Overlap review")
    st.caption(
        "The first screen groups funds by broad exposure. The second screen flags selected pairs at or above "
        f"{overlap_correlation_threshold:.0%} estimated correlation and caps their combined weight. "
        "These are screening tests, not holdings-level look-through."
    )
    if current_result is None:
        st.warning("No feasible portfolio is available for overlap review.")
    else:
        group_weights = overlap_bucket_weights(current_result["weights"], overlap_groups, gross=True)
        group_members: dict[str, list[str]] = {}
        for asset, group in zip(assets, overlap_groups):
            group_members.setdefault(group, []).append(asset)
        st.dataframe(
            [
                {
                    "Exposure bucket": group,
                    "Funds": ", ".join(group_members[group]),
                    "Combined weight": f"{weight:.2%}",
                    "Bucket cap": f"{max_overlap_weight:.0%}",
                    "Status": "PASS" if weight <= max_overlap_weight else "FAIL",
                    "What it captures": overlap_notes_for_groups((group,))[0],
                }
                for group, weight in sorted(group_weights.items(), key=lambda item: -item[1])
            ],
            hide_index=True,
            width="stretch",
        )
        pairwise_display = [
            {
                **row,
                "Correlation": f"{row['Correlation']:.2f}",
                "Combined weight": f"{row['Combined weight']:.2%}",
                "Left weight": f"{row['Left weight']:.2%}",
                "Right weight": f"{row['Right weight']:.2%}",
                "Status": "PASS" if row["Combined weight"] <= max_pairwise_overlap_weight else "FAIL",
            }
            for row in pairwise_overlap_rows(
                current_result["weights"], assets, current_correlation, overlap_correlation_threshold
            )
        ]
        if pairwise_display:
            st.dataframe(pairwise_display, hide_index=True, width="stretch")
        else:
            st.success("No selected pair reaches the high-correlation threshold.")


with st.container(border=True):
    st.markdown('<div class="p2-section-label">06 / Alternatives</div>', unsafe_allow_html=True)
    st.header("Ten starting themes")
    st.caption(
        "This audit runs the same allocation controls across all ten starting themes using the stated scenario returns, before manual return edits. "
        f"The full process gate remains **{gate_decision}** until its evidence checks pass."
    )
    if classroom_inputs:
        st.info("Theme presets use the ETF universe and are not available in Meridian classroom-input mode.")
    else:
        theme_audit = cached_theme_audit(
            tuple((name, tuple(theme)) for name, theme in THEME_PORTFOLIOS.items()),
            full_assets,
            full_current_expected_defaults,
            full_current_volatility,
            full_current_correlation,
            objective,
            reserve_minimum,
            max_overlap_weight,
            max_ticker_weight,
            max_pairwise_overlap_weight,
            overlap_correlation_threshold,
            allow_shorting,
            max_short_weight,
            max_gross_exposure,
            allocation_step,
            max_bitcoin_weight,
        )
        theme_display = []
        for row in theme_audit:
            result = row["Result"]
            if result is None:
                theme_display.append(
                    {
                        "Theme": row["Theme"],
                        "Starting funds": row["Assets"],
                        "Allocation verdict": "NO FEASIBLE MIX",
                        "Return": "-",
                        "Volatility": "-",
                        "Reserve": "-",
                        "Reason": row["Reason"],
                        "Full process gate": gate_decision,
                    }
                )
                continue
            groups = overlap_groups_for_assets(tuple(row["Assets"].split(", ")))
            theme_assets = tuple(row["Assets"].split(", "))
            theme_indices = [full_assets.index(asset) for asset in theme_assets]
            theme_correlation = tuple(
                tuple(full_current_correlation[left][right] for right in theme_indices)
                for left in theme_indices
            )
            pair_rows = pairwise_overlap_rows(
                result["weights"], theme_assets, theme_correlation, overlap_correlation_threshold
            )
            theme_display.append(
                {
                    "Theme": row["Theme"],
                    "Starting funds": row["Assets"],
                    "Allocation verdict": "PASS",
                    "Return": f"{result['expected_return']:.2%}",
                    "Volatility": f"{result['volatility']:.2%}",
                    "Reserve": f"{result['reserve_weight']:.2%}",
                    "Max bucket": f"{max(overlap_bucket_weights(result['weights'], groups, gross=True).values()):.0%}",
                    "Max pair": f"{max((float(pair['Combined weight']) for pair in pair_rows), default=0.0):.0%}",
                    "Reason": row["Reason"],
                    "Full process gate": gate_decision,
                }
            )
        st.dataframe(theme_display, hide_index=True, width="stretch")
        st.caption(
            "A theme can pass the allocation controls while the overall process still rejects or limits adoption because of turnover, holdout, liquidity, issuer, or point-in-time evidence."
        )


with st.container(border=True):
    st.markdown('<div class="p2-section-label">07 / Risk profiles</div>', unsafe_allow_html=True)
    st.header("Risk levels when feasible")
    universe_notes = {
        "TLT": "TLT holds long-duration U.S. Treasuries, so it can move sharply when rates change; it is not a cash substitute.",
        "VOO": "VOO and VTI substantially overlap. The pairwise screen is a correlation proxy, not holdings-level look-through.",
        "FBTC": "FBTC is a spot-bitcoin ETP, not a diversified equity ETF. The working mandate caps it at 10%.",
        "VNQ": "VNQ adds listed real estate but also overlaps broad U.S. equity ownership.",
    }
    relevant_notes = [note for asset, note in universe_notes.items() if asset in assets]
    if relevant_notes:
        with st.expander("Risk notes for this fund universe"):
            for note in relevant_notes:
                st.write(f"- {note}")

    st.subheader("Risk portfolio allocations: Levels 1–5")
    st.caption(
        "These use the current estimates and controls. Every displayed portfolio meets the return "
        "objective and reserve minimum."
    )
    if not current_risk_levels:
        st.warning("No risk-level portfolios meet the current mandate.")
    else:
        profile_names = (
            "Lowest feasible risk",
            "Lower-middle risk",
            "Middle risk",
            "Higher risk",
            "Highest-return efficient",
        )
        st.dataframe(
            [
                {
                    "Risk level": level,
                    "Profile": profile_names[level - 1],
                    "Allocation": " · ".join(
                        f"{asset} {weight:.0%}"
                        for asset, weight in zip(assets, result["weights"])
                        if abs(weight) > 0.001
                    ),
                    "Return": f"{result['expected_return']:.2%}",
                    "Volatility": f"{result['volatility']:.2%}",
                    "Reserve": f"{result['reserve_weight']:.2%}",
                }
                for level, result in enumerate(current_risk_levels, start=1)
            ],
            hide_index=True,
            width="stretch",
        )
        with st.expander("How the five risk levels are selected"):
            st.write(
                f"The engine tests bounded allocations in {allocation_step:.0%} steps under the displayed "
                "short and gross-exposure policy, removes portfolios that miss the return objective or reserve minimum, and keeps only efficient choices - ones "
                "not beaten by another mix with lower risk and equal or higher return. Levels 1–5 are "
                "evenly sampled along that efficient frontier."
            )

    if current_result is not None and loaded_result is not None:
        changes = [
            abs(current - loaded) * 100
            for current, loaded in zip(current_result["weights"], loaded_result["weights"])
        ]
        largest_index = max(range(len(changes)), key=changes.__getitem__)
        st.metric("Largest weight change", f"{changes[largest_index]:.0f} points", assets[largest_index])
        with st.expander("Why the two allocations can differ"):
            st.write(
                "The left result uses the currently selected return window and any estimates you "
                "edited. The right result keeps the full-history estimates that were loaded from the "
                "CSV. A large weight change shows that the decision is sensitive to the changed "
                "assumptions, not that either estimate is certain."
            )





###This report was written for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research and it is not financial advice.

###AI assistance: drafted with [Codex], resumed from my Lab 03 session; sources gathered and verified by me; the judgments are mine.

###Any remaining errors are my own.
