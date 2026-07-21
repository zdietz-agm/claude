# XBBG (Bloomberg) Reference

Behavioral rules and field table live in CLAUDE.md ("Libraries and Imports" -> XBBG subsection). This file holds the examples.

## Basic usage

```python
from xbbg import blp

# Single ticker, close and open, as-traded (no adjustment)
df = blp.bdh('SPY US Equity', ['PX_LAST', 'PX_OPEN'], '2024-01-01', '2024-12-31', adjust='-')

# Multiple tickers, close and 1d % change, adjusted for comparability
df = blp.bdh(['SPY US Equity', 'QQQ US Equity'], ['PX_LAST', 'CHG_PCT_1D'], '2024-01-01', '2024-12-31', adjust='all')

# Point-in-time snapshot (single date)
snap = blp.bdp('SPY US Equity', ['PX_LAST', 'PX_OPEN', 'CHG_PCT_1D'])
```

## Ticker suffixes

- US equities: ` US Equity` suffix (e.g. `SPY US Equity`).
- Indices: ` Index` suffix (e.g. `SPX Index`).

## Dividend history

Use `blp.bds` (not `bdh`) with the `DVD_HIST_ALL` field:

```python
dvd = blp.bds("SPY US Equity", "DVD_HIST_ALL")
# Returns: ex_date, dividend_amount, dividend_type
# Types seen: "Regular Cash", "Income", "Special Cash", "Long Term Cap Gain", "Stock Split"
```

## `adjust` parameter (recap of the rule in CLAUDE.md)

- `adjust='all'` -> split/dividend adjusted. Use for continuous, comparable return/price series viewed alone.
- `adjust='-'`   -> raw, as-traded. Use when combining with other unadjusted sources (option prices, SpiderRock liberator data).
