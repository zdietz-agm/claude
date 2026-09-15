# Semantics and quirks — the trap list

Data pulled without knowing these is frequently wrong. One heading per trap.

## CloudQuant T+2 lag (daily), T+1 evening (intraday DB)

Daily bars (adjusted + unadjusted) publish **2 business days** after the
trading date — Friday's bars appear Tuesday. Intraday ticks/imbalances
reach the DB the **following evening**: Monday's session lands Tuesday
evening, so a Tuesday-morning query's latest loaded session is Friday
(verified 2026-07-28). Liberator serves same-day at tick grain. Volatility
trails ~2 sessions because it derives from adjusted bars. **"Yesterday's
data is missing" is usually not a gap** — say so instead of reporting
missing data.

## Adjusted vs unadjusted prices

`t_ice_daily_bars_adjusted` holds prices scaled by split/dividend factors
**as of fetch time** — they drift from actual traded prices at every
ex-div/split and do NOT match Bloomberg or the intraday tables historically.

- Actual traded prices: `get_daily_bars(..., deadjust=True)` → divides by
  `COALESCE(NULLIF(adjustment_factor,0),1)`. Self-consistent per row.
- Prev close: use the vendor `unadjusted_close` column.
- Log returns / volatility: use ADJUSTED closes — never de-adjust there.
- Do NOT switch to `t_ice_daily_bars` even though its values are correct:
  it's missing ~30-90 delisted symbols/day in 2024-2025 (survivorship trap).
- ~0.15% of rows (reverse splits / ticker reuse) disagree between the two
  tables; de-adjusted values are canonical.

## NASDAQ clearing price

NASDAQ's imbalance feed has NO generic clearing price (NYSE-only field). Its
analog is the near indicative clearing price. Use
`clearing_price_effective` (provided by `get_imbalances`) =
`COALESCE(clearing_price, near_indic_clear_price)`. The backtest tables'
`clearing_price_HHMM` already apply this.

## Timestamps and time zones

All market timestamps are **US/Eastern**, except `created_at` / `updated_at`
housekeeping columns (UTC). Liberator datetimes are interpreted in
America/New_York.

## Imbalance snap-time convention (Zach)

The 3:50 and 3:55 PM snaps in the consolidated report tables are stored at
**15:50:01 / 15:55:01** (post-publication), not :00. Every other intraday
snap uses :00. Time-equality joins at 15:50:00 silently miss these rows.

## Imbalance sign convention (consolidated report tables)

`spy_net_imbalance` / `qqq_net_imbalance` **> 0 = net BUY** imbalance ("for
purchase"); **< 0 = net SELL** ("for sale"). "$1.5B for sale" means
`< -1.5e9`. Applies to all `t_report_*` imbalance columns and the
`imbal_340/350/355` factor snapshots in `algo_trade_log`.

## imbal(t), not imbal(t-1)

When aligning imbalance snapshots to decisions, use the snapshot AT the
decision time. The old t-1 offset (assuming ~1s polling latency) measurably
degrades accuracy (mean abs error $6.6M vs $34.4M on 40 samples).

## ETF flows: use navDate, not compositionDate

`get_etf_flows` differences shares outstanding between consecutive basket
rows. Baskets are forward-dated, so the row stamped `compositionDate = T`
carries `navDate = T-1` — the flow happened on **navDate**. Treating
`compositionDate` as the flow date puts a one-session look-ahead into any
backtest. `days_elapsed` shows the gap to the previous observation (3 over a
weekend); pass `min_days_elapsed=1` to keep only clean consecutive-session
flows.

Shares outstanding is stored directly only from 2026-07-31; before that it is
recovered as `shareClassAUMUSD / officialNavUSD`, which reproduces the vendor
figure exactly (validated: derived `creation_units` land on whole numbers,
which only happens if the share count is exact). The `source` column says
which path produced each row. `premium_discount_bps` needs
`lastTradedPriceUSD` and is therefore NULL before 2026-07-31.

## ETF baskets: creation is physical, tracking includes synthetics

The saved basket types answer different questions and are NOT
interchangeable:

- **creation / redemption** — what the fund delivers or receives in kind.
  100% physical equity, no derivatives. Use for deliverability, in-kind
  baskets, and what actually trades in the auction.
- **tracking** — the fund's full economic portfolio. iShares holds part of
  IJR/IJH synthetically, so this basket also carries CFD lines (assetClass
  `CFD`, `status = OTC`, no price/GICS/MIC) and occasionally `DER`. Use for
  weights, exposure and attribution.

**Duplicate-line history (fixed 2026-07-31).** The vendor lists a
synthetically-held name TWICE in the tracking basket — once physical
(`EQU`), once `CFD` — under the SAME componentBBGTicker. The loader keyed
components on that ticker, so the second line overwrote the first: 41 IJR
names stored ~20% of their true position and the basket summed to 93.3%
rather than 100%. IJH was affected on 3 names (0.4%).

From 2026-07-31 duplicate lines merge — quantities sum, metadata comes from
the physical line — and IJR tracking sums to 100.000% again. **Rows before
that date still carry the bad weights.** For historical IJR/IJH tracking
weights either restrict to `compositionDate >= '2026-07-31'` or use the
creation basket, which was always correct. Only IJR and IJH are affected;
the other 72 ETFs never had duplicates.

## Swap-based funds have empty creation/tracking baskets

Inverse and some levered ETFs (SQQQ, SPXU, TZA, SDOW, SPXS) hold swaps, not
equities, so their creation and tracking baskets are legitimately empty —
the swaps sit under `holdings`, which we do not store. Their HEADER rows are
complete (AUM, NAV, sharesOutstanding), which is all a flow or levered-
rebalance calculation needs. An empty basket for one of these is not a load
failure.

## Expense ratio: use `ocf`, not `expenseRatio`

Two fund-fee columns on `t_compositions_ETFDailyBasketHeaders`, in different
units and different states of repair (measured on the 74-ETF run of
2026-07-31):

- **`ocf`** — decimal fraction, **100% populated**. QQQ `0.0020` = 20 bp,
  IJR `0.0006` = 6 bp. Vendor rounds it to 4 dp, so sub-basis-point fees lose
  precision (XLI stores `0.0009` for a true 8 bp fee).
- **`expenseRatio`** — **percent**, only 66% populated, and `0.00` for every
  DTCC-sourced fund. All 25 iShares/Invesco funds missing it still have `ocf`.

So `ocf` for coverage, `expenseRatio / 100` when present for precision:
`COALESCE(NULLIF(expenseRatio, 0) / 100, ocf)`. Comparing the two raw is a
100× unit error.

## ragStatus is the vendor's quality flag, rolled up over stored baskets

Ultumus sends a per-basket-type dict, not a scalar:
`{"creation": "GREEN", "tracking": "AMBER", "redemption": "AMBER"}` — with
the optional keys varying by fund (`holdings` or `enhanced` appear for some).
The loader stores the **worst of `creation` and `tracking`** only, because
those are the two baskets it persists; a RED on `holdings` says nothing about
the rows we stored and would be a false alarm. The full dict is kept in
`t_ultumus_payload_archive` if you need the per-basket detail.

A non-GREEN value is the vendor's opinion, not a structural defect — on
2026-07-31 ARKF was RED and ARKK AMBER while both loaded complete baskets
summing to 1.0. Treat it as a reason to look, not as "the data is broken."

**Column was 100% NULL before 2026-07-31**: the first version read a
non-existent `status` key. Do not read pre-2026-07-31 NULLs as GREEN.

## trackedIndexRIC / trackedIndexName are always NULL

The basket endpoint returns `trackedIndex` as an empty object `{}` for every
fund (verified across all 74 on 2026-07-31). The columns exist for the day
the vendor populates it. NULL here means "vendor did not send it", never
"this ETF tracks no index".

## Intraday price tables: three sources, none complete

Picking the wrong one silently returns nothing for part of the universe.

| table | live? | covers |
|---|---|---|
| `t_prices_daily_price_capture` | **yes**, ~1s cadence to 15:59:59 | IWV constituents ONLY — US common stock. **No ETFs, no ADRs** (QQQ, SPY, SMH, TSM, NBIS all absent). Carries `yest_trade_close` on every row, so a same-day return needs no prior-session join. |
| `t_ice_intraday_prices` | no — nightly loader | full universe **including** ETFs. 10-second grid, 09:30–16:00. Column is `capture_timestamp` (DATETIME), **not** `snap_time`. `SOXX` has no rows — use `SMH` for semis. |
| `t_exchange_detail` | yes | S&P 500 constituents only (`universe='SPY'`, 502 tickers). Snaps run 15:50:01→16:00:00 — there is **no 15:50:00 row**. |

So there is no single table with live prices for both single stocks and index
ETFs. A page needing both is either a session behind or must blend sources and
say which is which.

Query these by exact `(business_date, symbol, capture_timestamp)` equality —
that uses the unique key and returns in ~0.1s even on the 167 GB table. A
`TIME(capture_timestamp) = ...` wrapper defeats the index.

## NAV return vs close return

Never interchangeable. NAV: `(officialNavUSD / price_at_snap - 1) * 1e4`
(requires a join to compositions basket headers); close:
`(px_last / price_at_snap - 1) * 1e4`.

## Half days

Detected by data predicate, not the calendar: afternoon columns NULL in the
close backtest table; `load_close_data(require_afternoon=True)` (default)
filters `price_1500 IS NOT NULL`. Half days: day after Thanksgiving,
Christmas Eve, ~July 3.

## MOC xtime gotcha

`t_moc_symboldata.xtime` is a MySQL TIME column. Read into Python it becomes
a `timedelta`; a naive round-trip writes `00:00:00` and breaks
`xtime BETWEEN '14:00:00' AND '15:55:00'` filters. Compare as strings/TIME
in SQL.

## Exchange MOC snapshot eras

In t_backtest_close_strategies, the 1550 exchange snap is empty before
2026-07-08 (capture started at 15:51); 1551+ columns are always ~92% filled
(the residual is delisted-symbol survivorship, not a gap).

## Single-name closing imbalance: which source, when

Four sources, disjoint sweet spots (all publish nothing before 15:50 ET --
exchanges disseminate MOC imbalances at 3:50; pre-15:50 exists only in the
NYSE-only broker feed and in the index/ETF consolidated table):

| Source | Granularity | Coverage | Universe |
|---|---|---|---|
| `t_ice_intraday_imbalances` (sandbox) | per-sec 15:50:01-15:50:30 burst, then 1-min | 2024-01-02+ | NYSE + NASDAQ |
| `t_moc_symboldata` (sandbox) | tick, 14:00-15:55 (broker feed) | 2024-01-02+ | NYSE-only |
| `auctionResearch.t_prices_daily_price_capture` (prod) | ~1-sec near close, jittered timestamps | 2026-01-13+ | full universe |
| `get_single_stock_imbalances_1550_1600` (CloudQuant + agentData cache) | raw ticks, any snap via as-of | 2022-03-11+ | any US name |

When to use what data source: date >= 2026-01-13 and jittered timestamps are fine ->
query `t_prices_daily_price_capture` directly (run_date + ticker bounded,
as-of matching). Need clean repeatable 1-sec snaps, or anything older
(2022-03-11 to 2026-01) -> `vbam_utilities.eod_imbalances.
get_single_stock_imbalances_1550_1600` -- it caches raw ticks per
(symbol, date) in agentData so each symbol-day costs one CloudQuant call
ever, team-wide. Post-2026 dates through the helper spend CloudQuant calls
the capture table would answer free; per-day cost, paid once, accepted for
one code path. `get_single_stock_imbalances_1550_1600` does NOT cover half days (1:00 PM
close, ~3/year): the auction runs ~12:50-13:00, outside its fixed window, so
those dates return nothing and are cached as no-data sentinels -- "not
available here", not "no imbalance". Identify them with
`calendar.get_half_days`. A dedicated half-day helper is a TODO.

The helper's `order_imbalance_vol` is SIGNED buy-positive
(matching `spy_net_imbalance`); the raw tables carry unsigned vol + side.

## ETF-level MOC imbalances don't exist

Both closing-imbalance sources are single-stock only: ETF tickers (SPY,
QQQ, ...) are absent from t_ice_intraday_imbalances and t_moc_symboldata,
and their rows in t_backtest_close_strategies have prices but all-NULL
imbalance columns. To answer "SPY vs QQQ imbalance", aggregate
constituent-level exchange imbalances in dollars over the basket
(`get_compositions`) — worked example in `docs/team_onboarding.md`.

## Broker MOC feed is NYSE-only

t_moc_symboldata — and the moc_* / dquote_* / total_* columns derived from
it in t_backtest_close_strategies — covers NYSE-listed names only; NASDAQ
symbols are all-NULL there (verified 2026-07-24: 0 of 103 QQQ members).
For NASDAQ closing imbalances use the exchange snap columns (1552+) or
t_ice_intraday_imbalances.

## Clearing-price sentinels in the close backtest table

`clearing_price_HHMM` carries two garbage patterns: a **214748.36**
INT32-overflow sentinel on some NYSE rows, and **0.00** placeholders on
NASDAQ rows before ~15:56 (NASDAQ publishes late). Never dollarize
`imbalance_vol` with `clearing_price` — use `price_HHMM` (last trade).
`imbalance_vol_HHMM` is already signed via `imbalance_side` (1=buy → +,
2=sell → −); do not re-sign it.

## Non-US ticker collisions in the backtest tables

A few non-US listings share tickers with US names (exchange = PARIS,
TEL AVIV, TORONTO, JOHANNESBU — e.g. an ADP row tagged PARIS). When
joining by ticker (basket membership etc.), dedupe preferring
`exchange IN ('NYSE','NASDAQ')`.

## NASDAQ pre-open source eras

`t_ice_intraday_imbalances` only gained NASDAQ near/far/ref fields ~2026-03;
pre-open rows for 2024-01→2026-02 were re-loaded 2026-07-27+. If a NASDAQ
clearing column is unexpectedly NULL for an era, check the SOURCE
near_indic fill first.

## EXCLUDED_SYMBOLS

12 tickers (GOLD/B Barrick rename pair, etc., ~0.06% of rows) are excluded
by default in the backtest loaders (`include_bad_tickers=False`). Mention
this when universe completeness matters.

## Huge-table bounds

`t_ice_intraday_prices` (1.7B rows), `t_ice_intraday_quotes`,
`t_prices_daily_price_capture` (319 GB): date AND symbol bounds are
mandatory. vbam_utilities enforces this; ad-hoc SQL must too. The DB intraday
tables hold only the loaded session windows (9:30–10:00, 15:00–16:00
prices; 9:00–9:30 quotes/pre-open imbalances; 15:40–16:00 MOC imbalances) —
for other windows use `source='api'` (tick grain).
