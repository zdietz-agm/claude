# sp500_cand_prediction

Predicts S&P 500 inclusion candidates from the Russell 1000 universe using
S&P Dow Jones Indices' official methodology. The output is a shortlist of
US-incorporated, large-cap, profitable, sufficiently-liquid names that are
NOT currently in the S&P 500 or S&P 400.

## How to regenerate the list

```
python D:/agent_projects/sp500_cand_prediction/sp500_candidates.py
```

Bloomberg must be running (xbbg connects to the local terminal). The full
run takes ~1-2 minutes — most of that is the 12-month daily price + volume
pull for the ~30 names that survive the cheap filters.

The script prints a step-by-step funnel so you can see exactly where each
name was cut. Final output is sorted by unadjusted market cap.

## What to verify / update before each rerun

The methodology thresholds are not constants — S&P updates them
periodically, and the universe definitions drift over time. Before
regenerating the list:

1. **Check the size threshold**. As of July 2025, the S&P 500 minimum
   unadjusted market cap is **$22.7B**. S&P typically updates this once a
   year. Source: `methodology-sp-us-indices.pdf` on
   spglobal.com/spdji. The constant `MIN_MARKET_CAP` at the top of the
   script encodes this — `MIN_FLOAT_MARKET_CAP` is automatically half of
   it (the methodology requires float-adjusted mcap >= 50% of size
   threshold), so updating one cascades.

2. **Russell 1000 reconstitutes annually in late June**. If running shortly
   after reconstitution day, the universe will shift. The `INDX_MEMBERS`
   call on `RIY Index` always returns the current membership, so the
   script picks up the new universe automatically — but be aware that
   year-over-year comparisons of the candidate list aren't strictly
   apples-to-apples across the reconstitution boundary.

3. **Russell 1000 vs alternatives**. `RIY Index` (Russell 1000) is a
   convenient large-cap universe, but it can miss recent IPOs and a
   handful of names whose Russell classification lags their market cap.
   For a more exhaustive screen, consider unioning RIY with `SP15 Index`
   (S&P 1500) or screening all US Equity by size directly. The default
   keeps RIY for query-size practicality.

4. **No further code changes should be needed** for a routine rerun —
   the script pulls all underlying data live from Bloomberg.

## Bloomberg field gotchas (do not re-derive these from scratch)

A previous chat probed many fields and validated which actually populate
on this terminal. The current script reflects those choices. Notes for
anyone tempted to swap fields:

- **`blp.index('SPX Index')` does NOT exist** in xbbg. Use
  `blp.bds('SPX Index', 'INDX_MEMBERS')`. The result is a column
  `member_ticker_and_exchange_code` containing strings like `'AAPL UW'`;
  reformat to `'AAPL US Equity'` (the helper `index_members()` does this).

- **Quarterly fundamentals**: the override params
  `Fundamental_Analysis_Period_Type` / `Fundamental_Analysis_Period_Offset`
  are NOT real Bloomberg overrides. They silently return empty data. For
  a quarterly time series use `blp.bdh(..., 'NET_INCOME', start, end, Per='Q')`
  and take the last 4 non-NaN values per ticker (fiscal calendars
  differ, so a single `tail(4)` on the merged frame would lose rows).

- **Net income field**: `IS_NET_INCOME` returns empty on this terminal.
  Use `NET_INCOME`. This is GAAP net income — slightly different from
  the methodology's "net income from continuing operations" but the
  closest reliable field. `IS_INC_BEF_XO_ITEM` is a closer match if you
  want to be stricter, but `NET_INCOME` is what the script uses.

- **Market cap units**: `CUR_MKT_CAP` is in **raw USD**, not millions
  (AAPL ~3.97e12). Earlier draft of the script assumed millions and
  filtered everything out.

- **Domicile**: `CNTRY_OF_DOMICILE` and `ULT_PARENT_CNTRY_DOMICILE` are
  both too generous — they return `'US'` for ADRs / foreign-incorporated
  entities (e.g. AngloGold Ashanti, Restaurant Brands, Brookfield AM).
  The right field is **`CNTRY_OF_INCORPORATION`**, which correctly
  returns `'GB'` for AU, `'CA'` for BAM/QSR, etc. Note this still doesn't
  check headquarters city — Bloomberg's `STATE_CODE` and
  `CITY_OF_DOMICILE` are unreliable for that purpose, and the
  S&P-methodology HQ test isn't fully replicable from BBG alone.

- **Float**: `EQY_FREE_FLOAT_PCT` works (returns a percent, 0-100).
  `EQY_FLOAT` is in millions of shares.

- **Exchange**: `EQY_PRIM_EXCH` returns human labels (`'NASDAQ GS'`,
  `'New York'`, etc.) — see `ELIGIBLE_EXCHANGES` set at top of script
  for the full list of S&P-eligible labels. `EXCH_CODE` is the country
  code (`'US'`), not what you want.

- **xbbg date index**: `bdh` returns a `datetime.date` index, not a
  `DatetimeIndex`. Comparing it to a `pd.Timestamp` raises
  `TypeError: Cannot compare Timestamp with datetime.date`. Convert with
  `df.index = pd.to_datetime(df.index)` before any date filtering.

- **Volume aggregation**: `PX_VOLUME` with `Per='M'` returns the LAST
  daily volume of the month, not the sum. To get monthly share volume,
  pull daily and `.resample('ME').sum()`.

## Methodology choices encoded in the script

These are interpretive decisions where reasonable analysts could
disagree. Documented here so they can be adjusted intentionally rather
than by accident.

- **Universe = Russell 1000 minus SPX/MID**. Could be widened to
  S&P 1500 union or an unrestricted size screen. RIY balances coverage
  vs. query size.

- **Domicile = `CNTRY_OF_INCORPORATION == 'US'` only**. Methodology also
  requires US headquarters and US primary listing. The script enforces
  the listing test via `EQY_PRIM_EXCH`, but no HQ test (Bloomberg fields
  are unreliable for HQ). In practice, `CNTRY_OF_INCORPORATION`
  catches the obvious cases (AU/BAM/QSR/etc.).

- **Profitability = strict reading of methodology**: most recent
  quarter's `NET_INCOME` > 0 AND sum of last 4 quarters > 0. This
  excludes names practitioners often *do* consider eligible — e.g.
  Coupang (CPNG), where Q4 2025 GAAP NI was -$26M (FX/tax noise on top
  of +$8M operating income) but LTM NI was +$208M. The committee uses
  discretion on small Q_0 losses; the script does not. If you want a
  "practitioner" reading, swap to `LTM > 0` only, or add an
  operating-income fallback for the Q_0 test.

- **Liquidity ratio formula**: `avg_close × sum(daily_volume)` over
  trailing 12 months, divided by float-adjusted mcap. This matches the
  S&P methodology wording. Some practitioners use `sum(daily_close ×
  daily_volume)` instead — slightly different in volatile periods,
  usually negligible for large caps.

- **6-month minimum monthly volume**: drops the current incomplete
  month, takes the last 6 complete months. If running near a
  month-boundary the answer can shift by one month — fine for an
  approximate screen.

- **Multiple share classes**: HEI and HEI/A are evaluated independently
  and can both appear in the candidate list. The S&P committee picks
  one class per company; the script does not dedupe.

## Files

- `sp500_candidates.py` — the screen. Self-contained; no helper modules.

## What the output is NOT

- A prediction of which names will actually be added at the next
  rebalance. The committee uses discretion on sector representation,
  IPO seasoning (informally 6-12 months), turnover minimization, and
  qualitative factors. The numerical screen is necessary but not
  sufficient.

- A backtestable signal. The list is a current-state snapshot; running
  it 6 months from now will reflect the universe AND the methodology
  thresholds AS OF that date.
