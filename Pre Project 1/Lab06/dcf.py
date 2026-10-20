"""Five-year DCF valuation"""

# Editable inputs (USD millions, except percentages and per-share value).
# Cadence Design Systems inputs (USD millions, except percentages and shares).
# 2025 FCFF = operating cash flow + after-tax cash interest - PP&E purchases.
STARTING_FCFF = 1728.781 + 111.951 * (1.0 - 413.155 / 1522.043) - 141.871
GROWTH_RATES = [0.14, 0.12, 0.10, 0.08, 0.05]
WACC = 0.09  # actual
TERMINAL_GROWTH = 0.03
NON_OPERATING_CASH = 3001.317
DEBT = 2480.150
DILUTED_SHARES = 273.312


def main():
    if TERMINAL_GROWTH >= WACC:
        print("Error: terminal growth must be less than WACC.")
        return

    fcff = []
    current_fcff = STARTING_FCFF
    for growth_rate in GROWTH_RATES:
        current_fcff *= 1.0 + growth_rate
        fcff.append(current_fcff)

    explicit_pv = sum(
        cash_flow / (1.0 + WACC) ** year
        for year, cash_flow in enumerate(fcff, start=1)
    )
    terminal_value = fcff[-1] * (1.0 + TERMINAL_GROWTH) / (WACC - TERMINAL_GROWTH)
    terminal_pv = terminal_value / (1.0 + WACC) ** len(fcff)
    enterprise_value = explicit_pv + terminal_pv
    equity_value = enterprise_value + NON_OPERATING_CASH - DEBT
    value_per_share = equity_value / DILUTED_SHARES
    terminal_share = terminal_pv / enterprise_value

    for year, cash_flow in enumerate(fcff, start=1):
        print(f"FCFF Year {year}: {cash_flow:.4f}")
    print(f"Present Value of Explicit FCFF: {explicit_pv:.4f}")
    print(f"Terminal Value at Year 5: {terminal_value:.4f}")
    print(f"Present Value of Terminal Value: {terminal_pv:.4f}")
    print(f"Enterprise Value: {enterprise_value:.4f}")
    print(f"Equity Value: {equity_value:.4f}")
    print(f"Value per Diluted Share: {value_per_share:.4f}")
    print(f"PV of Terminal Value as Share of Enterprise Value: {terminal_share:.4f}")


"""Actual CDNS WACC"""

#(78.38/(78.38/2.48))*0.095+(2.48/(2.48/78.38))*0.034*(1-0.21)=0.0915

"""VPS Test"""

#Intrinsic value per share: $142.8296"
#Current price: $284.60"
#Ratio: $142.8296 ÷ $284.60 = 0.5018×"

#VPS is within 0.5-2 range. No complaints.


###Sensitivity and reverse-DCF controls###

WACC_VALUES = [0.09, 0.10, 0.11]
TERMINAL_GROWTH_VALUES = [0.02, 0.03, 0.04]
TARGET_PRICE = 284.60
LOWER_SHIFT = -0.05
UPPER_SHIFT = 0.10


def value_per_share(wacc, terminal_growth, growth_shift=0.0):
    projected_fcff = []
    current_fcff = STARTING_FCFF
    for growth_rate in GROWTH_RATES:
        current_fcff *= 1.0 + growth_rate + growth_shift
        projected_fcff.append(current_fcff)

    explicit_pv = sum(
        cash_flow / (1.0 + wacc) ** year
        for year, cash_flow in enumerate(projected_fcff, start=1)
    )
    terminal_value = projected_fcff[-1] * (1.0 + terminal_growth) / (wacc - terminal_growth)
    terminal_pv = terminal_value / (1.0 + wacc) ** len(projected_fcff)
    enterprise_value = explicit_pv + terminal_pv
    equity_value = enterprise_value + NON_OPERATING_CASH - DEBT
    return equity_value / DILUTED_SHARES


def print_sensitivity_grid():
    print("\nSensitivity Grid: Value per Diluted Share")
    print("WACC \\ Terminal Growth | " + " | ".join(f"{growth:.2%}" for growth in TERMINAL_GROWTH_VALUES))
    for wacc in WACC_VALUES:
        cells = []
        for terminal_growth in TERMINAL_GROWTH_VALUES:
            if terminal_growth >= wacc:
                cells.append("Invalid")
            else:
                cells.append(f"${value_per_share(wacc, terminal_growth):.4f}")
        print(f"{wacc:.2%}                  | " + " | ".join(cells))


def reverse_dcf():
    if any(growth_rate + LOWER_SHIFT <= -1.0 for growth_rate in GROWTH_RATES):
        print("\nReverse DCF: no solution — lower bound pushes annual growth to -100% or below.")
        return

    lower_value = value_per_share(WACC, TERMINAL_GROWTH, LOWER_SHIFT)
    upper_value = value_per_share(WACC, TERMINAL_GROWTH, UPPER_SHIFT)
    if not min(lower_value, upper_value) <= TARGET_PRICE <= max(lower_value, upper_value):
        print("\nReverse DCF: no solution in the selected bracket.")
        return

    lower = LOWER_SHIFT
    upper = UPPER_SHIFT
    for _ in range(100):
        midpoint = (lower + upper) / 2.0
        midpoint_value = value_per_share(WACC, TERMINAL_GROWTH, midpoint)
        if midpoint_value < TARGET_PRICE:
            lower = midpoint
        else:
            upper = midpoint

    solved_shift = (lower + upper) / 2.0
    print("\nReverse DCF")
    print(f"Solved uniform growth shift: {solved_shift:.6%}")
    print(f"Target price: ${TARGET_PRICE:.4f}")
    print("Held fixed: starting FCFF, WACC, terminal growth, cash, debt, diluted shares, and the five base growth rates.")


if __name__ == "__main__":
    main()
    print_sensitivity_grid()
    reverse_dcf()
