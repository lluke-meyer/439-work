"""Reusable Lab 18 signal backtest for the Project 2 prototype."""

from __future__ import annotations

from math import prod


# Frozen classroom timing component. It is evaluated separately from the ETF allocator;
# its generic equity-fund returns are not the selected portfolio's realized returns.
MONTHLY_DATA = (
    ("2024-12", 0.8, None),
    ("2025-01", 1.2, 2.0),
    ("2025-02", 0.9, 1.5),
    ("2025-03", 1.5, 3.0),
    ("2025-04", -1.0, -2.5),
    ("2025-05", -0.7, -1.5),
    ("2025-06", -1.4, -3.0),
    ("2025-07", 1.1, 2.5),
    ("2025-08", 0.6, 1.0),
    ("2025-09", 0.9, 2.0),
    ("2025-10", -0.9, -2.0),
    ("2025-11", -0.5, -1.0),
    ("2025-12", 1.6, 3.5),
    ("2026-01", -1.1, -2.0),
    ("2026-02", 0.7, 1.5),
    ("2026-03", -1.3, -3.0),
    ("2026-04", 0.8, 2.0),
    ("2026-05", -0.6, -1.5),
    ("2026-06", 0.5, 1.0),
)

DEFAULT_LAG_MONTHS = 1
DEFAULT_SWITCH_COST_PERCENT = 0.10
DEFAULT_BILLS_RETURN_PERCENT = 0.30
DEVELOPMENT_MONTHS = ("2025-01", "2025-12")
HOLDOUT_MONTHS = ("2026-01", "2026-06")


def _month_in_range(month: str, month_range: tuple[str, str]) -> bool:
    return month_range[0] <= month <= month_range[1]


def _position_from_signal(signal: float) -> str:
    return "equity" if signal > 0 else "bills"


def _period_result(
    period: tuple[str, str],
    *,
    lag_months: int,
    switch_cost_percent: float,
    bills_return_percent: float,
    starting_position: str,
) -> dict[str, object]:
    rows = [row for row in MONTHLY_DATA if _month_in_range(row[0], period)]
    row_by_month = {row[0]: row for row in MONTHLY_DATA}
    index_by_month = {row[0]: index for index, row in enumerate(MONTHLY_DATA)}
    positions: list[tuple[str, str]] = []

    for month, _, _ in rows:
        signal_index = index_by_month[month] - lag_months
        if signal_index < 0:
            raise ValueError(f"No signal is available for {month} at the selected lag.")
        signal_month, signal, _ = MONTHLY_DATA[signal_index]
        if signal is None:
            raise ValueError(f"Signal is missing for {signal_month}.")
        positions.append((month, _position_from_signal(signal)))

    gross_factors: list[float] = []
    net_factors: list[float] = []
    switches = 0
    prior_position = starting_position
    for month, position in positions:
        _, _, equity_return = row_by_month[month]
        if equity_return is None:
            raise ValueError(f"Equity return is missing for {month}.")
        selected_return = equity_return if position == "equity" else bills_return_percent
        switched = position != prior_position
        switches += int(switched)
        gross_factors.append(1 + selected_return / 100)
        net_factors.append(
            1 + selected_return / 100 - (switch_cost_percent / 100 if switched else 0)
        )
        prior_position = position

    buy_and_hold_factors = [1 + row[2] / 100 for row in rows if row[2] is not None]
    return {
        "gross": prod(gross_factors) - 1,
        "net": prod(net_factors) - 1,
        "buy_and_hold": prod(buy_and_hold_factors) - 1,
        "switches": switches,
        "ending_position": positions[-1][1],
    }


def run_backtest(
    lag_months: int = DEFAULT_LAG_MONTHS,
    switch_cost_percent: float = DEFAULT_SWITCH_COST_PERCENT,
    bills_return_percent: float = DEFAULT_BILLS_RETURN_PERCENT,
) -> dict[str, object]:
    """Run the classroom development and holdout test with bounded controls."""
    if not 0 <= lag_months <= 1:
        raise ValueError("Signal lag must be between 0 and 1 month for the bundled data")
    if not 0 <= switch_cost_percent <= 5:
        raise ValueError("Switch cost must be between 0% and 5%")
    if -10 <= bills_return_percent <= 10:
        development = _period_result(
            DEVELOPMENT_MONTHS,
            lag_months=lag_months,
            switch_cost_percent=switch_cost_percent,
            bills_return_percent=bills_return_percent,
            starting_position="bills",
        )
        holdout = _period_result(
            HOLDOUT_MONTHS,
            lag_months=lag_months,
            switch_cost_percent=switch_cost_percent,
            bills_return_percent=bills_return_percent,
            starting_position=development["ending_position"],
        )
    else:
        raise ValueError("Bills return must be between -10% and 10%")
    return {
        "lag_months": lag_months,
        "switch_cost_percent": switch_cost_percent,
        "bills_return_percent": bills_return_percent,
        "development": development,
        "holdout": holdout,
        "failure_triggered": holdout["net"] < holdout["buy_and_hold"],
    }
