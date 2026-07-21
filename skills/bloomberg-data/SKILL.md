---
name: bloomberg-data
description: Pull Bloomberg market data with xbbg -- bdh/bdp/bds usage, the adjust parameter rules, common fields, ticker suffixes, and dividend history. Use when the user asks for Bloomberg data, open/close prices, PX_LAST or other Bloomberg fields, dividend history, or hits blpapi errors.
---

# Bloomberg Data (xbbg)

Use `from xbbg import blp` for historical and point-in-time Bloomberg data. For **intraday prices** use `cq_helpers`; for **open/close only** use xbbg. (For choosing between data providers, see the `data-sources` skill.)

## Functions

- `bdh` -- historical time series (multiple dates).
- `bdp` -- point-in-time snapshot (single date / as-of).
- `bds` -- record-set queries (e.g. `DVD_HIST_ALL` for dividend history).

## Useful fields

| Mnemonic     | Description              |
|-------------|--------------------------|
| `PX_LAST`   | Last / close price       |
| `PX_OPEN`   | Open price               |
| `CHG_PCT_1D`| One-day percent change   |
| `VOLUME`    | Volume                   |

## bdh `adjust` parameter (rule)

- `adjust='all'` -> split/dividend adjusted. Use for continuous, comparable price/return series viewed alone.
- `adjust='-'`   -> raw, as-traded prices. Use when combining with other unadjusted sources (option prices, SpiderRock liberator data).

## Ticker suffixes

` US Equity` for US equities (e.g. `SPY US Equity`), ` Index` for indices (e.g. `SPX Index`).

## Examples

Code examples and the dividend-history pattern: [references/xbbg_examples.md](references/xbbg_examples.md).

## Setup notes (blpapi)

- xbbg depends on `blpapi`, which is **NOT on PyPI**. It must be installed from Bloomberg's own package index:

  ```
  pip install --index-url=https://blpapi.bloomberg.com/repository/releases/python/simple blpapi
  ```

- A running, logged-in **Bloomberg Terminal** on the same machine is required at runtime -- xbbg connects through it.
- xbbg itself installs normally from PyPI; pinned version in [requirements.txt](requirements.txt).
