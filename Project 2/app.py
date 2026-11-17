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
from portfolio import (
    ASSETS,
    audit_theme_portfolios,
    CORRELATIONS,
    EXPECTED_RETURNS,
    MAX_DRAWDOWN,
    MAX_GROSS_EXPOSURE,
    MAX_OVERLAP_WEIGHT,
    MAX_PAIRWISE_OVERLAP_WEIGHT,
    MAX_SHORT_WEIGHT,
    MAX_TICKER_WEIGHT,
    OVERLAP_CORRELATION_THRESHOLD,
    OBJECTIVE_RETURN,
    RESERVE_ELIGIBLE,
    RESERVE_MINIMUM,
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
    )


st.set_page_config(page_title="Project 2 | Portfolio Decision", layout="wide")
st.markdown(
    """
    <style>
    .block-container { max-width: 1240px; padding-top: 1.6rem; padding-bottom: 4rem; }
    .p2-hero { background: linear-gradient(125deg, #112739, #173c49 65%, #255b59);
        border-radius: 18px; color: #fff; padding: 2.2rem 2.5rem; margin-bottom: 1rem; }
    .p2-eyebrow { color: #9cd9cc; font-size: .76rem; font-weight: 700;
        letter-spacing: .16em; text-transform: uppercase; margin-bottom: .7rem; }
    .p2-hero h1 { color: #fff; font-size: clamp(2rem, 4vw, 3.2rem);
        line-height: 1.1; letter-spacing: -.035em; margin: 0 0 .7rem; }
    .p2-hero p { color: #d6e7e6; font-size: 1rem; line-height: 1.55;
        max-width: 780px; margin: 0; }
    .p2-section-label { color: #2d7770; font-size: .76rem; font-weight: 700;
        letter-spacing: .14em; text-transform: uppercase; margin: .2rem 0 .15rem; }
    div[data-testid="stMetric"] { border: 1px solid #dce7e5; border-radius: 12px;
        background: #f8fbfa; padding: .85rem 1rem; }
    div[data-testid="stMetric"] * { color: #183343 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)
# The container is placed first and populated after the controls and calculations run.
hero = st.container(border=True)

with st.sidebar:
    st.header("Controls")
    st.caption("Changes here update the decision above.")
    with st.expander("Portfolio mandate", expanded=True):
        objective = st.number_input(
            "Objective return (%)", min_value=-25.0, max_value=50.0, value=OBJECTIVE_RETURN * 100, step=0.1
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
            help="Bundled CSV is reproducible. Yahoo Finance pulls public monthly adjusted-close history and is cached for one hour.",
        )
        yahoo_lookback_years = st.selectbox(
            "Yahoo lookback (years)", options=(3, 5, 10), index=1, disabled=data_source != "Yahoo Finance (live)"
        )
        classroom_inputs = st.checkbox(
            "Use Meridian classroom inputs instead of bundled prices",
            value=False,
            disabled=uploaded is not None,
        )
        last_36 = st.toggle(
            "Use last 36 monthly returns",
            value=False,
            disabled=uploaded is None and classroom_inputs,
        )
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
                source_label_override = "Bundled six-fund universe (live fallback)"
        else:
            price_source = bundled_path
            source_label_override = "Bundled six-fund universe"
        loaded_estimate = extend_estimate_with_candidates(estimate_from_prices(price_source, last_36=False))
        current_estimate = extend_estimate_with_candidates(estimate_from_prices(price_source, last_36=last_36))
    except (OSError, ValueError) as error:
        st.error(str(error))
        st.stop()
    assets = loaded_estimate["assets"]
    loaded_expected = loaded_estimate["expected_returns"]
    loaded_volatility = loaded_estimate["volatilities"]
    loaded_correlation = loaded_estimate["correlations"]
    current_expected_defaults = current_estimate["expected_returns"]
    current_volatility = current_estimate["volatilities"]
    current_correlation = current_estimate["correlations"]
    loaded_monthly_returns = loaded_estimate["monthly_returns"]
    current_monthly_returns = current_estimate["monthly_returns"]
    # Both TLT and SGOV can be selected as reserve candidates. The gate distinguishes
    # the short Treasury reserve from TLT's long-duration proxy risk.
    default_reserve = tuple(asset.upper() in {"TLT", "SGOV"} for asset in assets)
    source_label = source_label_override
    observation_label = (
        f"{current_estimate['return_observations']} monthly returns, "
        f"{current_estimate['start_date']} through {current_estimate['end_date']}; "
        f"modeled candidates: {', '.join(current_estimate['modeled_assets']) or 'none'}"
    )

with st.container(border=True):
    st.markdown('<div class="p2-section-label">01 / Set the scenario</div>', unsafe_allow_html=True)
    st.header("Build the portfolio")
    st.caption("Choose a starting theme, then adjust the funds and assumptions. Mandate and signal controls are in the sidebar.")
    st.subheader(source_label)
    st.write(observation_label)
    if not classroom_inputs or uploaded is not None:
        st.warning(
            f"The {objective:.1%} return objective and {reserve_minimum:.0%} reserve threshold are the current displayed controls. "
            "SGOV is the preferred reserve candidate; TLT remains an allowed long-duration proxy subject to review."
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
    default_fund_count = len(assets) if classroom_inputs else 6
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
            "Edit an expected-return estimate or reserve flag below. The app rebuilds the portfolio when funds are removed or added. "
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
                    key=f"return_{universe_key}_{asset}_{'36' if last_36 else 'all'}",
                    label_visibility="collapsed",
                )
                / 100
            )
            columns[2].write(f"{current_volatility[index]:.2%}")
            reserve_flags.append(
                columns[3].checkbox(
                    f"{asset} is reserve eligible",
                    value=default_reserve[index],
                    key=f"reserve_{universe_key}_{asset}",
                    label_visibility="collapsed",
                )
            )


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
)


def mandate_verdict(result: dict[str, object]) -> str:
    return "PASS" if (
        result["expected_return"] >= objective - 1e-12
        and result["reserve_weight"] >= reserve_minimum - 1e-12
        and max(result["weights"]) <= max_ticker_weight + 1e-12
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
    ("Equal weight", portfolio_result(equal_weight(len(assets)), current_expected_defaults, current_covariance, reserve_flags)),
    ("Inverse volatility", portfolio_result(inverse_volatility(current_volatility), current_expected_defaults, current_covariance, reserve_flags)),
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
tlt_is_reserve = any(asset == "TLT" and eligible for asset, eligible in zip(assets, reserve_flags))
sgov_history_observed = current_monthly_returns is not None and "SGOV" in current_monthly_returns
reserve_evidence_status = (
    "PASS" if sgov_is_reserve and sgov_history_observed
    else "REVIEW" if sgov_is_reserve or tlt_is_reserve
    else gate_status(any(reserve_flags))
)
reserve_evidence_text = (
    "Observed SGOV history selected as reserve evidence"
    if sgov_is_reserve and sgov_history_observed
    else "SGOV candidate selected; upload observed history before relying on it"
    if sgov_is_reserve
    else "TLT is a long-duration proxy only; short Treasury evidence is preferred"
    if tlt_is_reserve
    else "Select a reserve-eligible fund"
)
gate_rows = [
    {"Gate": "Return target", "Result": gate_status(current_result is not None and current_result["expected_return"] >= objective), "Evidence": f"{objective:.1%} minimum"},
    {"Gate": "Reserve floor", "Result": gate_status(current_result is not None and current_result["reserve_weight"] >= reserve_minimum), "Evidence": f"{reserve_minimum:.1%} minimum = ${portfolio_value_millions * reserve_minimum:.2f}m"},
    {"Gate": "Reserve eligibility", "Result": reserve_evidence_status, "Evidence": reserve_evidence_text},
    {"Gate": "Maximum ticker weight", "Result": gate_status(current_result is not None and max(current_result["weights"]) <= max_ticker_weight), "Evidence": f"{max_ticker_weight:.0%} cap"},
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
    hero_summary = "The current inputs do not produce a feasible allocation. Adjust the scenario below to see which mandate controls drive the result."
elif gate_decision == "REJECT / REDESIGN":
    hero_summary = "The allocation clears its displayed controls, but process evidence still blocks adoption. Review the failed gates and frozen holdout below."
elif gate_decision == "PILOT ONLY":
    hero_summary = "The allocation clears its displayed controls. Open review items still need evidence before an adoption decision."
else:
    hero_summary = "The allocation and process gates clear the displayed checks. Review the supporting evidence before a committee decision."
with hero:
    st.markdown(
        f"""<div class="p2-hero">
        <div class="p2-eyebrow">FIN 439 / Project 2 / Investment committee</div>
        <h1>Make the portfolio call.</h1>
        <p>{hero_summary}</p>
        </div>""",
        unsafe_allow_html=True,
    )
    # Give the full-process verdict enough room to remain readable during screen sharing.
    hero_metrics = st.columns([1.1, 1.8, 1, 1])
    hero_metrics[0].metric("Allocation mandate", allocation_decision)
    hero_metrics[1].metric("Full process gate", gate_decision)
    hero_metrics[2].metric("Estimated return", f"{current_result['expected_return']:.2%}" if current_result else "—")
    hero_metrics[3].metric("Frozen holdout net", f"{locked_backtest['holdout']['net']:.2%}")
    st.caption(
        f"{len(assets)} selected funds · {source_label} · Holdout buy-and-hold "
        f"{locked_backtest['holdout']['buy_and_hold']:.2%} · Built with AI help; a learning demonstration, not investment advice."
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
    st.caption("The current column uses the editable assumptions. The loaded column uses the source estimates before your edits.")
    current_column, loaded_column = st.columns(2)
    show_result(current_column, "Current estimates", current_result)
    show_result(loaded_column, "Inputs as loaded", loaded_result)

    st.subheader("Baseline and mandate verdicts")
    st.caption("PASS means the displayed portfolio meets the return, reserve, ticker, and overlap controls.")
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
    st.markdown('<div class="p2-section-label">03 / Decision evidence</div>', unsafe_allow_html=True)
    st.header("Why the committee call holds")
    st.caption("A hard failure means reject/redesign; a review item means the evidence is incomplete.")
    st.caption(
        "Allocation PASS means the selected weights satisfy the displayed return, reserve, ticker, "
        "exposure, overlap, and drawdown controls. The full process gate also requires the frozen "
        "signal, turnover, liquidity, issuer, reserve, derivative, and holdout evidence."
    )
    st.dataframe(gate_rows, hide_index=True, width="stretch")
    st.info(
        "[TLT](https://www.ishares.com/us/products/239454/ishares-20-plus-year-treasury-bond-etf) holds long-duration U.S. Treasury bonds. It is highly credit quality, but its price can "
        f"fall when interest rates rise. Treating TLT as the ${portfolio_value_millions * reserve_minimum:.2f} million reserve is a provisional proxy, not a "
        "cash-equivalent calculation. A short Treasury-bill fund such as [SGOV](https://www.ishares.com/us/products/314116/ishares-03-month-treasury-bond-etf) "
        "would be a cleaner reserve candidate. SGOV is available as a modeled candidate unless it is included in an uploaded price file."
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
        "This audit runs the same allocation controls across all ten starting themes using the source estimates, before manual return edits. "
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
    st.header("Five efficient risk levels")
    universe_notes = {
        "TLT": "TLT holds long-duration U.S. Treasuries, so it can move sharply when interest-rate expectations change; it is not a cash substitute.",
        "SOXX": "SOXX concentrates on semiconductor companies, adding sector and technology-cycle risk beyond a broad stock-market fund.",
        "GBTC": "GBTC provides spot-Bitcoin exposure and can be highly volatile; its presence in the universe does not require the optimizer to hold it.",
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
