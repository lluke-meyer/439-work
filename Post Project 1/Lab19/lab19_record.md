# Lab 19 - Legend Panel

## D - Define

Can three investor personas read the same SEC facts, apply different rules,
and still produce a useful first screen? The panel uses Warren Buffett, Cathie
Wood, and Michael Burry on the same five annual 10-K rows.

## R - Represent

The data layer keeps missing facts as `not found` and checks as `not known`.
It reports USD millions and computes owner earnings, ROE, current ratio, and
liabilities/equity.

| Investor | Checks |
|---|---|
| Buffett | ROE at least 15% every year; owner earnings positive every year; owner earnings grew |
| Cathie Wood | Revenue grew; net income grew; operating cash flow positive every year |
| Michael Burry | Operating cash flow at least net income every year; liabilities no more than twice equity |

Wood's checks are SEC-only growth proxies. Innovation, TAM, adoption,
competitive advantage, footnotes, and valuation stay outside the panel.

## I - Implement

- [`panel_financials.py`](panel_financials.py) - SEC facts, annual selection, ratios, and checks.
- [`app.py`](app.py) - Streamlit panel, editable memos, number flags, and trust calibration.
- [`cathie-wood-expert/SKILL.md`](cathie-wood-expert/SKILL.md) - Wood rules and limits.
- [`michael-burry-expert/SKILL.md`](michael-burry-expert/SKILL.md) - Burry rules and limits.

The app's unique feature is the **Panel fingerprint**. It counts pass, fail,
and not-known results, labels the read as Screen agreement, Useful split, or
Insufficient evidence, and points to the next evidence to inspect.

Run from the FIN 439 folder:

```bash
SEC_USER_AGENT='Luke Meyer <lmeyer@purdue.edu>' \
"Project 1/.venv/bin/python" \
"Post Project 1/Lab19/panel_financials.py" COST

SEC_USER_AGENT='Luke Meyer <lmeyer@purdue.edu>' \
"Project 1/.venv/bin/streamlit" run "Post Project 1/Lab19/app.py"
```

The fund-company bridge is SOXX -> NVDA. Verify the current holding before
submission using the [iShares SOXX holdings page](https://www.ishares.com/us/products/239705/ishares-semiconductor-etf).

## V - Validate

### COST

| Result | Outcome |
|---|---|
| Buffett | 3 of 3 pass |
| Cathie Wood | 3 of 3 pass |
| Michael Burry | 2 of 2 pass |
| Current-ratio probe | 1.06 fails at threshold 2 and passes at threshold 1 |

The run reproduced the lesson's current ratios of 1.02, 1.07, 0.97, 1.03,
and 1.06 and liabilities/equity ratios of 2.11, 1.75, 1.96, 1.64, and 1.49.

### NVDA

| Investor | Outcome |
|---|---|
| Buffett | 3 of 3 pass |
| Cathie Wood | 3 of 3 pass |
| Michael Burry | 1 of 2; OCF versus net income fails |

Revenue rose from 26,914 to 215,938 and net income rose from 9,752 to 120,067.
The panel keeps Burry's failed cash-quality check visible instead of averaging
it away.

### Checks

- `py_compile` passed for both Python files.
- One Streamlit `AppTest` session rendered both COST and NVDA panels with 0 exceptions and 0 displayed errors.
- Six editable memos rendered with ticker-specific widget keys.
- Adding `999.0` to a memo produced the unprinted-number error.
- `git diff --check` passed.

## E - Evolve

The coverage-based tag selector handles issuers whose first candidate tag does
not cover the latest five annual periods. Future extensions should add separate,
source-linked innovation and footnote evidence instead of estimating it from
the current table.

## R - Reflect

The panel agrees on COST because all narrow rules pass. NVDA is more useful:
Buffett and Wood pass, while Burry identifies a cash-flow problem. I would use
the panel for Project 2 only with a condition: verify the fund holding, read the
10-K and footnotes, and resolve valuation and every not-known field first.

Completed during class.



###This report was written for FIN 43900 (AI Finance Applications, Purdue) as a learning exercise. It is not investment research and it is not financial advice.

###AI assistance: drafted with [Codex], resumed from my Lab 03 session; sources gathered and verified by me; the judgments are mine.

###Any remaining errors are my own.
