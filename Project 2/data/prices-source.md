# My Ten-Fund Price Panel and Scenario Inputs

I froze ten funds and 33 common month-end trading closes in `prices.csv`, from January
31, 2024, through September 30, 2026. That gives me 32 monthly price changes. I used
Nasdaq's public historical `Close/Last` responses on November 19, 2026. For each fund,
the source URL is
`https://api.nasdaq.com/api/quote/TICKER/historical?assetclass=etf&limit=5000&fromdate=2024-01-01&todate=2026-09-30`,
with `TICKER` replaced by the symbol. My `prepare_nasdaq_monthly.py` script takes the
last common trading close each month, orders the dates, checks positive prices and a
common window, and writes `prices.csv`.

| Role | Fund | Raw JSON SHA-256 |
|---|---|---|
| U.S. large cap | VOO | `e5dbec0aad1855d328ca660a847602e290acb718c0278f28b1d1f2ab4cf0b197` |
| U.S. total market | VTI | `797810f0464c19ae26e4966a6f1caca071b5caf414a9a92ced555b9981726672` |
| Listed real estate | VNQ | `e2a1b2bcfc03eaa6e22d8ff9d1fc4cfcc931b89b5958f84ce6202b96fce03e4` |
| Emerging markets | VWO | `1a3372f4d30f8d652d91d60a19ff16fee55fc3095abb7571967edf62c34756c0` |
| Spot bitcoin ETP | FBTC | `57b6f5eb79a11b8ae5adc7d4e11241f6dadf8977e499587b3c55d31e3f7e272c` |
| Core bonds | FBND | `65190ffa157ddb4c10692ba4cdfed1b8b12703277b803c62e452266c602758bc` |
| Non-U.S. value | FIVA | `325e8eb00ae4e63fab8a3dea8ec52bbbda08b4f11a8ba16ec2a98935cd59eb61` |
| Short Treasury reserve | SGOV | `bc0b45a32db40a64c32474b92e89f01efbe2823fd328d43a2a8ed5592d2e13e4` |
| Optional long Treasury | TLT | `d3c312802c599db1c7095d8a7194b23c856e782b46a5e8dbe27ffd4609eb0a1c` |
| Inflation-protected bonds | TIP | `a457a886d8c20138736da301fcaf286700e65a93889256ff50279c00663ed892` |

I recorded the transformed `prices.csv` SHA-256 as
`9df2314009b913bc2968a1908c3ce52f51dda80b8123c3fa05d16b3534376316`.
I do not redistribute the raw JSON in the repository. To reproduce the panel, download
each ticker's response, save it as lowercase `ticker.json`, and run the transform.

**My data limit:** `Close/Last` excludes dividends and other cash distributions. It is
not a total-return series and understates economic returns for distributing funds,
especially FBND, SGOV, TLT, TIP, and VNQ. I use it only for price volatility,
correlation, and drawdown screens. The editable annual return inputs in `portfolio.py`
are **illustrative scenario assumptions**, not forecasts supported by this panel. A
numerical PASS or mandate boundary is not an investable recommendation. Before adoption,
I need verified total-return history and independent reasons for the return assumptions.
I can compare all 32 returns with the latest 24 for price-risk estimates. The FBTC
history does not support a 36-return window.

I use issuer pages for fund descriptions: [Vanguard VOO](https://investor.vanguard.com/investment-products/etfs/profile/voo),
[VTI](https://investor.vanguard.com/investment-products/etfs/profile/vti),
[VNQ](https://investor.vanguard.com/investment-products/etfs/profile/vnq),
[VWO](https://investor.vanguard.com/investment-products/etfs/profile/vwo),
[Fidelity FBTC](https://www.fidelity.com/etfs/crypto-funds),
[FBND](https://digital.fidelity.com/prgw/digital/research/quote/dashboard/summary?symbol=FBND),
[FIVA](https://digital.fidelity.com/prgw/digital/research/quote/dashboard/summary?symbol=FIVA),
[iShares SGOV](https://www.ishares.com/us/products/314116/ishares-03-month-treasury-bond-etf),
[TLT](https://www.ishares.com/us/products/239454/ishares-20-plus-year-treasury-bond-etf), and
[TIP](https://www.ishares.com/us/products/239467/ishares-tips-bond-etf).
