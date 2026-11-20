"""Explain why the full committee process can or cannot pass."""

from __future__ import annotations

from typing import Iterable, Mapping


NEXT_ACTION = {
    "Return data quality": "Verify distribution-adjusted total returns and independently justify the expected-return inputs.",
    "Return target": "Review the numerical Auto-Pass sensitivity or propose a new, committee-approved return objective.",
    "Reserve floor": "Include enough eligible SGOV exposure or revise the reserve policy with committee approval.",
    "Reserve eligibility": "Document why the selected reserve is eligible and confirm its liquidity under the mandate.",
    "Maximum ticker weight": "Change the allocation or seek an explicit concentration-policy decision.",
    "Bitcoin concentration": "Reduce FBTC weight or seek an explicit bitcoin concentration-policy decision.",
    "Short and gross exposure": "Reduce leverage or shorts to the approved limits.",
    "Overlap proxy": "Reduce broad-bucket concentration and check holdings-level overlap.",
    "High-correlation pair": "Reduce the correlated pair or document a committee-approved exception.",
    "Historical drawdown": "Reduce price-path drawdown and recheck using verified total-return data.",
    "Liquidity": "Document fund-level liquidity and a ten-business-day cash plan.",
    "Issuer concentration": "Perform holdings-level issuer look-through and document concentration.",
    "Derivative governance": "Document contract, margin, counterparty, and hedge controls, or adopt a no-derivatives policy.",
    "Annual turnover": "Redesign and freeze a lower-turnover rule; test it against the unchanged limit.",
    "Frozen holdout": "Freeze a redesigned rule before a genuinely new out-of-sample period; compare net to buy-and-hold.",
}


def full_process_pass_report(gate_rows: Iterable[Mapping[str, str]]) -> dict[str, object]:
    """Return the blockers; no status or threshold is rewritten."""
    rows = tuple(gate_rows)
    if not rows:
        raise ValueError("Full-process audit needs displayed gate results")
    blockers: list[dict[str, str]] = []
    for row in rows:
        name, status = row["Gate"], row["Result"]
        if status not in {"PASS", "FAIL", "REVIEW"}:
            raise ValueError(f"Unknown gate status: {status}")
        if status != "PASS":
            blockers.append({
                "Gate": name,
                "Status": status,
                "Current evidence": row["Evidence"],
                "Needed for a real pass": NEXT_ACTION.get(name, "Supply independent evidence and obtain committee review."),
            })
    return {
        "ready": not blockers,
        "fail_count": sum(row["Status"] == "FAIL" for row in blockers),
        "review_count": sum(row["Status"] == "REVIEW" for row in blockers),
        "blockers": tuple(blockers),
    }
