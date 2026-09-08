"""Five-year discounted cash flow valuation."""

# Editable inputs (USD millions, except percentages and per-share value).
STARTING_FCFF = 100.0
GROWTH_RATES = [0.08, 0.06, 0.05, 0.04, 0.03]
WACC = 0.10
TERMINAL_GROWTH = 0.03
NON_OPERATING_CASH = 50.0
DEBT = 300.0
DILUTED_SHARES = 50.0


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


if __name__ == "__main__":
    main()



***This report was written for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research and it is not financial advice.

***AI assistance: drafted with [Codex], resumed from my Lab 03 session; sources gathered and verified by me; the judgments are mine.

***Any remaining errors are my own.
