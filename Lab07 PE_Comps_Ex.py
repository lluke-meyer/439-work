### Define/Discover

# P/E is stock price divided by diluted EPS. It shows how much investors are willing to pay for each dollar of a company's earnings.
# It lets us compare companies of different sizes because EPS is already on a per-share basis. It gives the DCF a market-based comparison instead of only relying on my own assumptions.
# P/E is most useful when the companies have similar business models, reporting periods, and earnings quality. Negative EPS makes P/E not meaningful, while unusual earnings or different growth expectations can make the comparison less useful.

### Represent

# AutoNation (AN) and Group 1 (GPI) are candidates because they are franchised auto dealers like Asbury. Earnings come from similar areas such as vehicle sales, service, parts, and financing.
# Differences in stock, geography, scale, growth, and profitability should be qualified because they can affect the P/E.
# I would use AutoNation and qualify GPI. GPI is still a relevant dealer peer, but it has a higher P/E.

### The Real Case

# Asbury is the target, and is not included in its own peer set. The peer median P/E is applied directly to Asbury's diluted EPS to estimate a share price.
# AN and GPI imply a range of $215.81 to $246.18 for Asbury. The median estimate is $231.00, which is below Asbury's $243.03 closing price.


### Implement

"""
P/E comparable-company valuation using only editable local inputs.

Enter prices and diluted EPS on a consistent as-of date and fiscal-period basis.
P/E is an equity multiple: this script intentionally never uses cash or debt.
"""

from __future__ import annotations

from statistics import median


# ---------------------------------------------------------------------------
# EDITABLE INPUTS
# ---------------------------------------------------------------------------
# Table 1 starting inputs. Replace these values and/or add peers for CDNS.
# Prices and EPS are dollars per share.  Use None when an input is unavailable.
TARGET = {
    "ticker": "ABG",
    "name": "Asbury Automotive Group",
    "price": 243.03,
    "diluted_eps": 21.50,
}

PEERS = [
    {
        "ticker": "AN",
        "name": "AutoNation",
        "price": 169.84,
        "diluted_eps": 16.92,
    },
    {
        "ticker": "GPI",
        "name": "Group 1 Automotive",
        "price": 421.48,
        "diluted_eps": 36.81,
    },
]


def peer_key(record: dict[str, object]) -> str:
    """Return a case-insensitive identity key, preferring ticker."""
    ticker = str(record.get("ticker") or "").strip().upper()
    name = str(record.get("name") or "").strip().casefold()
    return f"ticker:{ticker}" if ticker else f"name:{name}"


def valid_number(value: object) -> bool:
    """True only for numeric, positive values (excluding bool)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def format_price(value: float | None) -> str:
    return "not meaningful" if value is None else f"${value:,.2f}"


def implied_price(multiple: float, target_eps: object) -> float | None:
    """Apply an equity multiple directly to EPS; no EV-to-equity bridge exists here."""
    if not valid_number(target_eps):
        return None
    return multiple * float(target_eps)


def usable_peers() -> list[dict[str, object]]:
    """Deduplicate peers, exclude the target, and attach valid P/E calculations."""
    target_key = peer_key(TARGET)
    seen: set[str] = set()
    usable: list[dict[str, object]] = []

    print("Peer screening and P/E calculations")
    for peer in PEERS:
        label = f"{peer.get('ticker', '')} — {peer.get('name', '')}".strip(" —")
        key = peer_key(peer)
        if key == target_key:
            print(f"  {label}: excluded (target)")
            continue
        if key in seen:
            print(f"  {label}: excluded (duplicate peer)")
            continue
        seen.add(key)

        price = peer.get("price")
        eps = peer.get("diluted_eps")
        if not valid_number(price) or not valid_number(eps):
            problems = []
            if not valid_number(price):
                problems.append("price missing or nonpositive")
            if not valid_number(eps):
                problems.append("diluted EPS missing or nonpositive")
            print(f"  {label}: P/E not meaningful ({'; '.join(problems)})")
            continue

        multiple = float(price) / float(eps)
        usable.append({**peer, "pe": multiple})
        print(f"  {label}: P/E = {multiple:.6f}x")
    return usable


def print_full_peer_estimate(peers: list[dict[str, object]]) -> float | None:
    """Print min/median/max P/E outputs and return the unrounded median estimate."""
    if not peers:
        print("\nNo usable peers: no P/E estimate.")
        return None

    multiples = [float(peer["pe"]) for peer in peers]
    low, middle, high = min(multiples), float(median(multiples)), max(multiples)
    target_eps = TARGET.get("diluted_eps")

    print("\nFull-peer P/E valuation")
    if not valid_number(target_eps):
        print("  Target diluted EPS is missing or nonpositive: implied prices are not meaningful.")
        return None

    if len(peers) == 1:
        print(f"  Reference P/E: {middle:.6f}x")
        print(f"  Reference implied price: {format_price(implied_price(middle, target_eps))}")
        print("  One valid peer: reference estimate only; no range.")
    else:
        print(f"  Minimum P/E: {low:.6f}x  ->  {format_price(implied_price(low, target_eps))}")
        print(f"  Median P/E:  {middle:.6f}x  ->  {format_price(implied_price(middle, target_eps))}")
        print(f"  Maximum P/E: {high:.6f}x  ->  {format_price(implied_price(high, target_eps))}")

    return implied_price(middle, target_eps)


def print_peer_removal_test(peers: list[dict[str, object]], full_estimate: float | None) -> None:
    print("\nPeer-removal test (median P/E implied price)")
    if not peers:
        print("  No usable peers: no removal estimates.")
        return
    if full_estimate is None:
        print("  Target diluted EPS is missing or nonpositive: removal estimates are not meaningful.")
        return

    for removed in peers:
        remaining = [peer for peer in peers if peer is not removed]
        label = f"{removed.get('ticker', '')} — {removed.get('name', '')}".strip(" —")
        if not remaining:
            print(f"  Remove {label}: no estimate (no usable peers remain)")
            continue
        remaining_median = float(median([float(peer["pe"]) for peer in remaining]))
        remaining_estimate = implied_price(remaining_median, TARGET.get("diluted_eps"))
        # Both values are unrounded here; only display formatting rounds to cents.
        change = remaining_estimate - full_estimate  # type: ignore[operator]
        print(
            f"  Remove {label}: {format_price(remaining_estimate)} "
            f"(change from full-peer estimate: ${change:+,.2f})"
        )


def main() -> None:
    print(f"Target: {TARGET.get('ticker', '')} — {TARGET.get('name', '')}")
    if not valid_number(TARGET.get("diluted_eps")):
        print("Target diluted EPS: missing or nonpositive; implied prices will not be meaningful.")
    else:
        print(f"Target diluted EPS: ${float(TARGET['diluted_eps']):.6f}")

    peers = usable_peers()
    full_estimate = print_full_peer_estimate(peers)
    print_peer_removal_test(peers, full_estimate)


if __name__ == "__main__":
    main()



### Validate

# Can confirm that after running cd "/Users/lukemeyer/Documents/Year 4/FA 26/FIN 439/CDNS Research" ->
#python3 PE_Comps_Ex.py we get the expected results seen in the 'Validate' table.

### Evolve

# If we remove GPI, I expect median P/E to fall as G1 has the highest P/E.
# Removing GP1 resulted in the -$15.81 decrease. The price change comes from the removal of the highest P/E peer which understandably lowers the range and the median.
# Using just one peer provides an estimate since there is no other peer to compare to.



###This report was written for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research and it is not financial advice.

###AI assistance: drafted with [Codex], resumed from my Lab 03 session; sources gathered and verified by me; the judgments are mine.

###Any remaining errors are my own.
