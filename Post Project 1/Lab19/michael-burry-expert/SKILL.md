---
name: michael-burry-expert
description: Analyze a public company using Michael Burry's forensic cash-flow and balance-sheet checks in Lab 19.
---

# Michael Burry panel skill

Use the same five annual SEC 10-K rows as the other panel members. Keep missing
facts as `not found` and return `not known` when a check cannot be computed.

Checks:

1. Operating cash flow was at least net income in every selected fiscal year.
2. Total liabilities were no more than twice equity in the latest selected year.

Write a skeptical memo from the printed numbers only. A pass is not a clean
bill of health: the narrow panel does not inspect footnotes, revenue
recognition, leases, contingencies, insider activity, or valuation.
