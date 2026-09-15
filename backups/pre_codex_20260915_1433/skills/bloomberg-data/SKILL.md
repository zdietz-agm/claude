---
name: bloomberg-data
description: Pull Bloomberg market data with xbbg -- bdh/bdp/bds usage, the adjust parameter rules, common fields, ticker suffixes, dividend history, and the bloomberg_helpers wrappers (timeout-safe, budget-counted, with a persistent my_bdh parquet cache so repeat daily-history pulls are free). Use when the user asks for Bloomberg data, open/close prices, PX_LAST or other Bloomberg fields, dividend history, hits blpapi errors, needs a timeout/kill around a hanging bdh, wants the daily API-hit counter, or before writing ANY bdh pull (the cache changes how to pull).
---

# Bloomberg Data (xbbg)

Use `from xbbg import blp` for historical and point-in-time Bloomberg data. For **intraday prices** use `cq_helpers`; for **open/close only** use xbbg. (For choosing between data providers, see the `data-sources` skill.)

**Team-library note (2026-07)**: `vbam_utilities.bloomberg` (D:/vbam-data-oracle) supersedes `bloomberg_helpers` for NEW work -- same `my_bdh/my_bdp/my_bds` API, but the bdh cache is the TEAM-SHARED `agentData.bloomberg_bdh_cache` DB table (one teammate's pull serves everyone) and the counter is per-machine at `~/.vbam` (cap 250k). Also check `vbam_utilities.get_daily_bars(deadjust=True)` first for daily OHLCV -- zero BBG budget (see `data-oracle` skill). Everything below still applies to the legacy local wrapper.

## Functions

- `bdh` -- historical time series (multiple dates).
- `bdp` -- point-in-time snapshot (single date / as-of).
- `bds` -- record-set queries (e.g. `DVD_HIST_ALL` for dividend history).

## Timeout-safe wrappers + daily API budget (`bloomberg_helpers`)

For **unattended / scheduled** contexts (i.e. EOD `update_data.py`, cron-style jobs), do NOT call `blp.bdh/bdp/bds` directly -- a stale Bloomberg terminal makes a `bdh` block forever. Instead, use `D:/PycharmProjects/utils/bloomberg_helpers.py`:

```python
import bloomberg_helpers as bbg
df = bbg.my_bdh("SPY US Equity", "PX_LAST", "2026-07-01", "2026-07-10", timeout=60, verbose=True)
px = bbg.my_bdp("SPX INDEX", "PX_LAST", timeout=30)
n  = bbg.get_bloomberg_count()   # today's total data-point count so far
```

- `my_bdh` / `my_bdp` / `my_bds` mirror `blp.bdh/bdp/bds` (the `my_` prefix makes the guarded wrapper obvious at the call site) plus keyword-only `timeout=` (sec), `retries=` (N attempts; on timeout it sleeps 1s and retries, default 1 = no retry), and `verbose=`. `get_bloomberg_count()` returns today's running total.
- **Timeout + kill:** each call runs in a child PROCESS; if it exceeds `timeout` it is `terminate()`d and the wrapper raises `TimeoutError` (a hung blpapi call can't be killed in-thread). It spawns a process per call (~2-5s: xbbg import + blpapi connect), so use it for a MODEST number of pulls, not tight loops.
- **Daily API-hit counter:** every successful call adds its data-point count (date x ticker x field cells of the returned frame) to `utils/.bloomberg/bloomberg_counter.csv` (`date, api_hit_count`), keyed on `getNowEst().date()`, under a cross-process msvcrt lock. `MAX_API_HITS = 450_000` caps the day -- once reached, every new request raises `AssertionError` before hitting Bloomberg. `verbose=True` prints `[<today_total>] ~~~ BBG (+<pts>): bdh PX_LAST bulk 1 tickers`. Cache hits add nothing to the counter.
- `python bloomberg_helpers.py` runs a self-test.

## Persistent my_bdh cache (repeat raw daily-history pulls are FREE)

`my_bdh` transparently caches **raw (`adjust='-'`) daily-history** data points in `utils/.bloomberg/bdh_cache.parquet`, keyed by **(ticker, field, date)** -- same philosophy as the CloudQuant intraday pickle cache. Rules that follow:

- **Always prefer `my_bdh` with `adjust='-'` over raw `blp.bdh`** for daily history, interactive or not -- a repeated query costs ZERO API hits and zero counter budget. Only genuinely missing (ticker, field, date) cells are pulled from Bloomberg, then upserted into the parquet (cross-process locked, safe from parallel scripts).
- **RAW ONLY, by design**: `adjust='all'`/omitted-adjust calls always hit Bloomberg fresh and are never cached, because adjusted history is restated retroactively whenever a split occurs -- a cached copy would silently go stale. Raw as-traded prints never change, so the cache needs no invalidation, ever. Every cache read/write asserts `adjust == '-'`. Workflow implication: pull raw via the cache and apply split/div adjustments yourself (splits + divs from `DVD_HIST_ALL`), rather than pulling `adjust='all'` repeatedly.
- Trading days Bloomberg returns no row for are stored as NaN sentinels so they are never re-requested. Expected days come from `calendar_utils.trading_range` (US equity calendar) -- non-US tickers re-pull on US-holiday gaps (harmless, slightly wasteful).
- The cache is BYPASSED automatically (plain counted pull, nothing stored) when the call has kwargs beyond `adjust` (`Per=`, `currency=`, ...) or the field returns non-numeric values (e.g. `NAME`). Opt out per call with `use_cache=False` (e.g. when today's partial-day value may have been cached and you need a fresh print -- values already cached are NEVER refreshed automatically).
- `repull_nans=True` treats cached NaN sentinels ("BBG had no data that day") as missing and re-asks Bloomberg for those (ticker, field) combos -- use when a sentinel might be stale (late-published data, halted names) rather than a true no-data day.
- Field names are case-normalized: stored/matched UPPERCASE in the cache, so `px_last` and `PX_LAST` share one entry; the returned frame keeps the caller's casing. Reads use pyarrow predicate pushdown on the requested tickers, so per-call load stays fast as the file grows.
- `bdh_cache_stats()` returns `{rows, tickers, fields, file_mb}`; `bbg.BDH_CACHE_PARQUET` holds the path.
- `verbose=True` shows the split: `BBG (+40, 200 from cache): bdh PX_LAST bulk 3 tickers`.

Interactive/notebook use can still call `blp.*` directly for quick one-offs (you'll see a hang and can Ctrl-C), but bulk daily history should go through `my_bdh` to build up the shared cache.

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
