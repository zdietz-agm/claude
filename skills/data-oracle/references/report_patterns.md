# Deliverable contract

Every dataset or report you produce follows this pattern.

## Location and naming

- Everything goes under `outputs/` (gitignored). One directory per
  deliverable: `outputs/YYYY-MM-DD_<slug>/` (e.g.
  `outputs/2026-07-28_nasdaq_close_imbalances_q2/`).
- Never write outside `outputs/`; never commit outputs.

## Contents of a dataset deliverable

1. The data: CSV by default; xlsx on request (one sheet per logical table).
2. `README.md` — short, always present:
   - the dataset spec (columns, universe, window, grain, filters)
   - row count and coverage notes (missing days/symbols and WHY — T+2 lag,
     session windows, half days, delisted names)
   - any quirks applied (de-adjustment, clearing_price_effective, snap-time
     conventions)
   - how to regenerate
3. `generate.py` — the exact script that produced the data, runnable from
   the repo root with `.venv\Scripts\python.exe`. Reproducibility is part of
   the deliverable, not optional.

## Reports (analysis on top of data)

- Same directory pattern; report as markdown (or xlsx if tabular).
- Separate FINDINGS (what the data says) from CAVEATS (coverage, lag,
  survivorship). Never bury caveats.
- Round for presentation, never in intermediate computation.

## Day-type bucketing (default for imbalance statistics)

When breaking imbalance results out by day type, use four mutually exclusive
buckets, assigned in this precedence order:

1. **Month End** — last trading day of the calendar month
   (`calendar.is_month_end`)
2. **Fed Day** — FOMC decision date (`calendar.FEDS`)
3. **Expiry** — monthly options expiry (`calendar.EXPIRIES`)
4. **Regular** — everything else

Always report the bucket-total denominator ("4 hits out of 65 month-ends")
so thin samples are visible.

## Communication

- Lead with what was delivered and where; then coverage caveats; then usage
  notes. Keep it short — the per-dataset README carries the detail.
