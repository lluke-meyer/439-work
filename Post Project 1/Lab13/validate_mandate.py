"""Validate the reconstructed Lab 13 mandate without choosing an optimizer."""

from __future__ import annotations

import json
from pathlib import Path


REQUIRED = {
    "decision_user",
    "decision",
    "objective",
    "horizon_years",
    "benchmark",
    "risk_measure",
    "constraints",
    "validation_tests",
    "unresolved_ambiguity",
}


def load_mandate(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        record = json.load(stream)
    missing = REQUIRED.difference(record)
    if missing:
        raise ValueError(f"Missing mandate fields: {sorted(missing)}")
    return record


def completeness_gaps(record: dict) -> list[str]:
    gaps = []
    for field in REQUIRED:
        value = record[field]
        if value in ("", None, []):
            gaps.append(field)
    if len(record["constraints"]) < 4:
        gaps.append("constraints")
    return sorted(set(gaps))


if __name__ == "__main__":
    mandate = load_mandate(Path(__file__).with_name("mandate.json"))
    gaps = completeness_gaps(mandate)
    print("Incomplete fields:", ", ".join(gaps) if gaps else "none")
    print("At least four constraints:", "PASS" if len(mandate["constraints"]) >= 4 else "FAIL")
    decision_ok = "do not execute trades" in mandate["decision"].lower()
    print("Decision boundary preserved:", "PASS" if decision_ok else "FAIL")
    ambiguity_ok = "unresolved" in mandate["objective"].lower()
    print("Unresolved objective preserved:", "PASS" if ambiguity_ok else "FAIL")



###This report was written for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research and it is not financial advice.

###AI assistance: drafted with [Codex], resumed from my Lab 03 session; sources gathered and verified by me; the judgments are mine.

###Any remaining errors are my own.
