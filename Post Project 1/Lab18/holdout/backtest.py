"""Lab 18: frozen trading-rule development and holdout test."""

from math import prod


# Editable inputs. Returns are percentages as written in the rule card.
MONTHLY_DATA = [
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
]

LAG_MONTHS = 1
SWITCH_COST_PERCENT = 0.10
BILLS_RETURN_PERCENT = 0.3
DEVELOPMENT_MONTHS = ("2025-01", "2025-12")
HOLDOUT_MONTHS = ("2026-01", "2026-06")


def as_decimal(percent):
    """Convert a percentage input into a decimal return."""
    return percent / 100


def month_in_range(month, month_range):
    """Return whether a YYYY-MM month is inside an inclusive range."""
    return month_range[0] <= month <= month_range[1]


def position_from_signal(signal):
    """Return the position selected by the frozen rule."""
    return "equity" if signal > 0 else "bills"


def rule_results(period, starting_position="bills"):
    """Calculate gross return, net return, and switches for one period."""
    rows = [row for row in MONTHLY_DATA if month_in_range(row[0], period)]
    all_rows_by_month = {row[0]: row for row in MONTHLY_DATA}
    positions = []
    current_position = starting_position

    for month, _, _ in rows:
        month_index = next(
            index for index, row in enumerate(MONTHLY_DATA) if row[0] == month
        )
        signal_index = month_index - LAG_MONTHS
        if signal_index < 0:
            raise ValueError(f"No signal is available for {month} at the selected lag.")
        signal_month, signal, _ = MONTHLY_DATA[signal_index]
        if signal is None:
            raise ValueError(f"Signal is missing for {signal_month}.")
        current_position = position_from_signal(signal)
        positions.append((month, current_position))

    gross_factors = []
    net_factors = []
    switches = 0
    prior_position = starting_position

    for month, position in positions:
        _, _, equity_return = all_rows_by_month[month]
        if equity_return is None:
            raise ValueError(f"Equity return is missing for {month}.")
        selected_return = (
            equity_return if position == "equity" else BILLS_RETURN_PERCENT
        )
        switched = position != prior_position
        if switched:
            switches += 1
        gross_factors.append(1 + as_decimal(selected_return))
        net_factors.append(
            1
            + as_decimal(selected_return)
            - (as_decimal(SWITCH_COST_PERCENT) if switched else 0)
        )
        prior_position = position

    buy_and_hold_factors = [
        1 + as_decimal(row[2])
        for row in rows
        if row[2] is not None
    ]

    return {
        "gross": prod(gross_factors) - 1,
        "net": prod(net_factors) - 1,
        "buy_and_hold": prod(buy_and_hold_factors) - 1,
        "switches": switches,
        "ending_position": positions[-1][1],
    }


def percent(value):
    return f"{value * 100:.2f}%"


def print_results(label, results):
    print(label)
    print(f"  Rule gross:    {percent(results['gross'])}")
    print(f"  Rule net:      {percent(results['net'])}")
    print(f"  Buy-and-hold:  {percent(results['buy_and_hold'])}")
    print(f"  Switches:      {results['switches']}")
    print(f"  Ending position: {results['ending_position']}")


def main():
    development = rule_results(DEVELOPMENT_MONTHS, starting_position="bills")
    holdout = rule_results(
        HOLDOUT_MONTHS, starting_position=development["ending_position"]
    )

    print("Lab 18 — Holdout Test")
    print(f"Lag: {LAG_MONTHS} month(s)")
    print(f"Switch cost: {SWITCH_COST_PERCENT:.2f}%")
    print(f"Bills return: {BILLS_RETURN_PERCENT:.2f}%")
    print_results("Development", development)
    print_results("Holdout", holdout)

    failure_triggered = holdout["net"] < holdout["buy_and_hold"]
    if failure_triggered:
        print("Failure rule: TRIGGERED — holdout net trails buy-and-hold.")
    else:
        print("Failure rule: NOT TRIGGERED — holdout net does not trail buy-and-hold.")


if __name__ == "__main__":
    main()
