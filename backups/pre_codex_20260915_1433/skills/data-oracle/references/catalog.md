# Data Catalog

One row per data source. Row template:

```
| Data Name | Description (what it represents conceptually -- this is the MOST IMPORTANT part -- granularity, latency) | When to access | How to access | Start Date | Owner |
```

Entries marked `[FILL IN]` need confirmation from the listed or prospective owner.

Databases (all via `vbam_utilities.vbam_db`): `backtest_sandbox` is an isolated
read-only nightly copy (~5 AM ET refresh) and the DEFAULT for backtests --
`get_sandbox_engine()`, tables unqualified. VBAM prod (`get_prod_engine()`) and
VBAM dev (`get_dev_engine()`) are read-only; fully qualify `schema.table`. The
agent db (`get_agent_engine()`, `agentData` schema) is the only read-write
connection. NOT in the sandbox (too big -- query prod if truly needed): raw
10-second tick prices, raw DQuote orders.

When a source has extra detail (column definitions etc.) it lives in its own
sub-file under `references/tables/` and the row points to it.

| Data Name | Description | When to access | How to access | Start Date | Owner |
|---|---|---|---|---|---|
| ThetaData | Historical OPRA option quotes (1s bid/ask/size) for index options (SPX/SPXW, NDX/NDXP) and equity options (NVDA, SPY, ...). Updated T+1 | Historical option quotes. Importantly, this does not have greeks, implied value, or fair values. It only has raw bid/ask data. So, use this if you want to recreate what an options market looked like. | `vbam_utilities.thetadata`: `get_option_quotes`, `get_bulk_chain`, `get_index_price`, `list_expirations`, `list_strikes`. Team API key built in -- zero setup. PACE PULLS: >= 0.1s between requests, never a tight loop | End of 2019 for most symbols | Zach Dietz |
| Bloomberg | Daily open/close prices, any BBG field, dividends, corporate actions. Requires running Bloomberg Terminal | Daily-frequency price history (not intraday prices), summary data (i.e. high, low, volume), reference data (i.e. primary exchange of a security), dividends | `vbam_utilities.bloomberg`: `my_bdh`/`my_bdp`/`my_bds` (timeout-guarded, per-machine budget-counted). Raw adjust='-' bdh pulls cache to `agentData.bloomberg_bdh_cache`, and static bdp reference fields to `agentData.bloomberg_bdp_cache` -- one teammate's pull serves everyone. Pass `timeout=None` in a hot loop to run in-process and skip the ~2-5s child-process spawn (no hang guard, so opt in deliberately). blpapi installs from Bloomberg's index (see repo README) | Decades (varies by field) | Zach Dietz |
| CloudQuant | Intraday historic equity/ETF trade prices (tick-level, ICE XNYS) plus official open and close prints. T+1 | Intraday prices at arbitrary times (i.e. what did NVDA trade at 10:30 AM last Tuesday), esp. before 14:00 where VBAM snap tables have no coverage. Also official open/close when you want them without a Bloomberg terminal. | `vbam_utilities.cloudquant`: `get_close_prices(symbols, start, end)`, `get_prices(symbol, datetime)`, `get_prices_batch(symbols, datetime)` (one query for many symbols -- always prefer it over looping get_prices; both auto-cache to agentData on VBAM Dev DB). Official open lives in the same dataset (OPEN_FIELD) -- ask Zach or add a get_open_prices wrapper. Team creds + certificate ship inside the library -- zero setup | mid 2022 | Zach Dietz |
| SpiderRock (live) | Live options quotes, IV surfaces, index prints | Live/current options and vol data | `spdr_rock_functions` (not yet in vbam_utilities; lives on Zach's computer since a VPN is needed to access. I am thinking about ways to share this if others want it.) | live only | Zach Dietz |
| SpiderRock (historical) | Historical option/IV snapshots every 5 minutes intraday via SpiderRock. | Historical options/IV when not already cached in t_historical_options_snaps | Ask Zach (needs to be added to vbam_utilities) | 2019 for most symbols | Zach Dietz |
| ETF creation/redemption flows | Daily fund flows per ETF: shares-outstanding change x NAV. Derived from the Ultumus basket headers, so it covers every configured ETF. Also exposes premium/discount (2026-07-31+), creation units, and flow as a share of AUM. | Estimating in-kind creation/redemption activity, and the mechanical basket buying/selling an AP must do as a result. Use `navDate` as the flow date, not `compositionDate`. | `vbam_utilities.get_etf_flows(etfs, start, end, min_days_elapsed=1)` | 2020-08-28 | James Cahill |
| `t_backtest_open_strategies` | One row per (date, symbol) with everything for the OPENING auction: prev close, official open, overnight gap %, 9:20-9:30 exchange imbalances, NBBO mids, 9:30-10:00 prices + TWAPs, 10-90d vol. Prices are actual traded (de-adjusted) prices matching Bloomberg. | The go-to table for open backtests -- pre-joined, no joins needed | `vbam_db.get_sandbox_engine()` -- SQL, table unqualified | 2024-01-02 | James Cahill |
| `t_backtest_close_strategies` | Same shape for the CLOSE: broker MOC + DQuote imbalances (3:00-3:50), combined net imbalance, official exchange MOC imbalance (3:50-4:00, 1-min), afternoon prices + TWAPs, daily bars & vol. 150 cols. Prices are actual traded (de-adjusted) prices matching Bloomberg. | The go-to table for close / MOC backtests | `vbam_db.get_sandbox_engine()` -- SQL, table unqualified | 2024-01-02 | James Cahill |
| `t_ice_daily_bars_adjusted` | Split/dividend-adjusted daily OHLCV + adjustment factors. Return/vol math ONLY -- never for entry/exit P&L (adjusted prices drift from traded prices) | Return and volatility calculations | `vbam_db.get_sandbox_engine()` -- SQL, table unqualified | 2022-12-28 | James Cahill |
| `t_ice_daily_bars` | Unadjusted daily OHLCV (actual traded prices) | Cross-check / reference | `vbam_db.get_sandbox_engine()` -- SQL, table unqualified | 2023-12-28 | James Cahill |
| `t_volatility_ticker` | Rolling realized annualized vol (vol_10d...vol_90d) + daily log returns per symbol/day | Filter or rank names by vol regime | `vbam_db.get_sandbox_engine()` -- SQL, table unqualified | 2023-01-12 | James Cahill |
| `t_ice_nyse_bqt_headers` | NYSE official open/close prints + instrument reference (ISIN/SEDOL/CUSIP, lot size) | Official auction prices, security IDs | `vbam_db.get_sandbox_engine()` -- SQL, table unqualified | 2023-12-28 | James Cahill |
| `t_ice_intraday_imbalances` | Exchange auction imbalance snapshots, NYSE + NASDAQ incl. indicative clearing prices: pre-open (9:00-9:30, NASDAQ from ~9:25) and MOC window. MOC grain is NOT uniform 1-min: per-SECOND during the 15:50:01-15:50:30 publication burst, then 1-min 15:51-16:00 (verified NVDA 2026-07-17). No rows before 15:50 (exchanges publish MOC imbalance at 3:50). For true 1-sec at any post-15:50 time this table is NOT the route -- use the Python helper `vbam_utilities.eod_imbalances.get_single_stock_imbalances_1550_1600` (CloudQuant pull + agentData cache, NOT a sandbox table) | Finer imbalance detail than the backtest columns | `vbam_db.get_sandbox_engine()` -- SQL, table unqualified | 2024-01-02 | James Cahill |
| `t_ice_intraday_quotes` | 60s NBBO bid/ask/mid + spread, pre-market 9:00-9:30, NYSE-only (NASDAQ absent) | Finer pre-open quote path | `vbam_db.get_sandbox_engine()` -- SQL, table unqualified | 2024-01-02 | James Cahill |
| `t_moc_symboldata` | Broker MOC feed at tick level: buy/sell imbalance, paired shares, indicative price through the afternoon | Custom MOC-timing analysis | `vbam_db.get_sandbox_engine()` -- SQL, table unqualified | 2024-01-02 | James Cahill |
| `agentData.eod_imbalance_ticks_1550_1600` | Team cache of single-stock MOC imbalance TICKS 15:50-16:00 (raw ICE exchange feeds via CloudQuant; signed buy-positive shares). Grows as helpers pull; each (symbol, date) hits CloudQuant once ever. **HALF DAYS ABSENT** -- their auction runs ~12:50-13:00, outside the window, so those dates carry a no_data sentinel meaning "not available here", NOT "no imbalance". `venue_source` records how the listing venue was chosen: `composition` (the t_compositions_ETFDailyBaskets default), `inferred` (from volume, after a listing move -- verify before trusting), `pinned`, `*_unvalidated`, `no_data` | NEVER query or write directly -- use `vbam_utilities.eod_imbalances.get_single_stock_imbalances_1550_1600`, which reads/writes it automatically | `vbam_utilities.eod_imbalances` | 2022-03-11 (CloudQuant floor) | Zach Dietz |
| `auctionResearch.t_prices_daily_price_capture` | Full-universe (~2,584 tickers) price + imbalance capture: ~1-SECOND rows near the close (10-sec earlier in day), 11-18M rows/day. Cols incl. imbalance_side, order_imbalance_vol, auction_vol, clearing prices, bid/ask. Timestamps are jittered sub-second (e.g. 15:55:01.667) -- use as-of logic, not equality. HUGE: always bound by run_date AND ticker | Recent (2026+) single-name imbalance/price at ~1-sec grain, full universe, no API budget. For older history use `eod_imbalances.get_single_stock_imbalances_1550_1600` | `vbam_db.get_prod_engine()` -- SQL, fully qualified | 2026-01-13 (partial first day) | James Cahill |
| `t_compositions_ETFDailyBaskets` | Daily ETF basket membership, weights, shares, GICS. Dedupe the 2 basketTypeId rows; baskets are forward-dated | Sector/basket studies | `vbam_db.get_sandbox_engine()` -- SQL, table unqualified | 2024-01-02 | James Cahill |
| `t_cme_btic_emini_sp500` / `t_cme_btic_emini_nasdaq100` | CME BTIC basis-over-cash trades around the close (ES / NQ) | Market-level close context, hedging signal | `vbam_db.get_sandbox_engine()` -- SQL, table unqualified | 2022-08-22 | James Cahill |
| `t_report_consolidated_imbalances` (sandbox copy) | Sandbox copy of prod `auctionResearch.t_report_consolidated_imbalances` (see that row below) -- prefer this copy for research | Historical index-ETF imbalances via the sandbox | `vbam_db.get_sandbox_engine()` -- SQL, table unqualified | 2021-01-04 | James Cahill |
| `t_daily_twap_levels` (sandbox copy) | Daily TWAP levels per (date, symbol): 25 `twap_START_END` columns on a 30-min grid — exit-from-X-to-close (`twap_0930_1600`..`twap_1530_1600`) + from-open (`twap_0930_1000`..`twap_0930_1530`). Means of 1-MINUTE last-trade marks; `is_etf`, `n_marks`. SPX members (point-in-time) + SPY/QQQ/IWM/DIA + 11 sector SPDRs. Half-days ABSENT by design (tape carries after-hours prints); last-trade<15:30 names carry NULL TWAPs | "What if I exited this position over the (rest of the) day" counterfactuals; full-day/partial-day exit marks; sector-ETF vs name intraday relative strength | `vbam_db.get_sandbox_engine()` -- SQL, table unqualified | 2022-03-11 | James Cahill |
| `t_report_consolidated_imbalances_summary` | Trimmed summary: SPY/QQQ/SPY-NAS net imbalance + price by snap_time, bucket, post-15:50 cps, VIX level | Quick index-imbalance + VIX context | `vbam_db.get_sandbox_engine()` -- SQL, table unqualified | 2021-01-04 | James Cahill |
| `t_report_twap_imbalance_analysis` | Per-(date, ticker) close-auction analysis: TWAP windows into the close, official NAV & close, imbalances at each snap, NAV moves, VIX | Rich close-auction / return-to-NAV studies | `vbam_db.get_sandbox_engine()` -- SQL, table unqualified | 2022-03-15 | James Cahill |
| `t_open_imbal_analysis` | Per-day per-universe open-imbalance + price-path summary (9:27:30 imbal, 5-min marks 9:35-10:00) | Open-imbalance studies | `vbam_db.get_sandbox_engine()` -- SQL, table unqualified | 2022-01-03 | James Cahill |
| `t_report_aggregated_imbalances` | Per (date, time bucket) SPY/QQQ universe avg net imbalance + avg price | Index imbalance time series | `vbam_db.get_sandbox_engine()` -- SQL, table unqualified | 2021-01-04 | James Cahill |
| `t_report_aggregated_differences` | Per-day SPY/QQQ imbalance-change metrics across late-day windows | Imbalance drift/divergence | `vbam_db.get_sandbox_engine()` -- SQL, table unqualified | 2021-01-04 | James Cahill |
| `auctionResearch.t_report_consolidated_imbalances` | Consolidated SPY/QQQ (+ select other ETFs) closing-auction imbalances + intraday prices, one row per second 14:00-16:00 (net/paired/MOC/d-quote imbalance, price). T+1. Mirrored nightly into the Backtest Sandbox -- prefer the sandbox copy for research | Any historical imbalance or late-day price-action question (i.e. avg SPY return 3pm->close when imbal > $1B to buy). 15:50:01 row = source of truth for 3:50pm values | `vbam_db.get_prod_engine()` -- SQL. Key cols: `business_date`, `snap_time`, `spy_net_imbalance`, `spy_paired_imbalance`, `spy_price`, `qqq_*` | 2021-01-04 | James Cahill |
| `auctionResearch.t_trade_price_snaps` | Equity/ETF trade prices at specific intraday snap times. T+1 | Historical price at a standard snap time | `vbam_db.get_prod_engine()` -- SQL. Cols: `business_date`, `ticker`, `snap_time`, `trade_price` | [FILL IN] | [FILL IN] |
| `auctionResearch.t_index_level_snaps` | Index levels (VIX etc.) at intraday snap times. T+1 | Historical VIX/index level at a snap time | `vbam_db.get_prod_engine()` -- SQL. Cols: `business_date`, `ticker` (i.e. `I:VIX`), `snap_time`, `index_level` | [FILL IN] | [FILL IN] |
| `auctionResearch.t_imbalance_basket_detail` | 3:55pm basket imbal with sub-second capture timestamps. Real-time | Same-day 3:55 imbalance detail | `vbam_db.get_prod_engine()` -- SQL. Cols: `run_date`, `basket_name`, `capture_time`, `exch_net_notional` | [FILL IN] | [FILL IN] |
| `imbalanceSnapshots.t_imbal_1550_BasketSnapshots` | Basket-level real-time SPX/NDX imbalance for post-3:50pm trading | Live intraday imbalance | `vbam_db.get_prod_engine()` -- SQL. Cols: `runDate`, `basket` (`.SPX`/`.NDX`), `snapTimestamp`, `exchNetImbalTotal`, `exchPairedImbalTotal`, `seenPct` | [FILL IN] | [FILL IN] |
| `compositions.t_compositions_ETFDailyBasketHeaders` | Official ETF NAV published end-of-day. T+1 | Any Return-to-NAV calculation (NAV differs from the 4pm trade close) | `vbam_db.get_prod_engine()` -- SQL. Cols: `navDate`, `etfTicker`, `officialNavUSD` | [FILL IN] | [FILL IN] |
| `optionsResearch.t_historical_options_snaps` | Historical SpiderRock option snapshots (quotes + Greeks/IV). T+1 | Historical options/IV -- CHECK HERE FIRST before pulling from SpiderRock (historical) | `vbam_db.get_dev_engine()` -- SQL. Cols: `trade_date`, `exp`, `symbol`, `strike`, `cp`, `bidPrc`, `askPrc`, Greeks/IV | Sept 2016 (SPXW) | Zach Dietz |
| `optionsResearch.t_opra_quotes` | 1-second OPRA quote history. Mainly populated for 0DTE SPX strikes. Populated via ThetaData. T+1 | Options quote research without re-pulling ThetaData | `vbam_db.get_dev_engine()` -- SQL. Cols: `trade_date`, `exp`, `strike`, `cp`, `timestmp`, `bidPrc`, `askPrc` | 2019 | Zach Dietz |
| `optionsResearch.t_index_snaps_td` | Per-second index price series (SPX, NDX, VIX, ...) cached from ThetaData pulls. ~30M rows. T+1 | Index price series already pulled once -- check before re-pulling ThetaData | `vbam_db.get_dev_engine()` -- SQL. Cols: `symbol`, `trade_date`, `timestmp`, `price` | 2021-01-04 | Zach Dietz |
| `optionsResearch.t_volume_data` | Daily per-symbol option flow aggregates: call/put contract volume, delta-weighted volume (share-equivalents), and $ premium -- each bucketed by expiry window (all / 5D / 22D / 33D) and by "large" (> 10 delta) contracts -- plus interpolated ATM vol (22D/66D) and a has_weeklies flag. ~120 liquid names. Updated daily | Option flow studies (i.e. was yesterday's NVDA call buying unusually large, premium spent in short-dated puts), vol screening via atmVol columns | `vbam_db.get_dev_engine()` -- SQL. One row per (symbol, trade_date). Full column definitions: [tables/t_volume_data.md](tables/t_volume_data.md) | 2025-01-02 | Zach Dietz |
| `optionsResearch.t_resvol` / `v_resvol` | Residual vol time series per (timestamp, symbol, expiry) for ~119 liquid names, from the beta-vol-spreading pipeline. Raw table stores symbol_id + integer resVol; the `v_resvol` view joins symbol names and scales to decimal -- use the view. ~141M rows. [FILL IN -- Zach: confirm definition/units and update cadence] | Single-stock vol richness/cheapness vs the beta-implied level | `vbam_db.get_dev_engine()` -- SQL against `v_resvol`. Cols: `dt`, `symbol`, `exp`, `resVol` | [FILL IN] | Zach Dietz |
| `optionsResearch.t_top_strike` | Per-snapshot top-of-book quotes + greeks (delta/vega/theta, bid/ask IV, SR price) for the most active strikes across the whole listed universe. ONE-OFF COLLECTION: December 2024 only -- not updating | Only if researching that December 2024 window | `vbam_db.get_dev_engine()` -- SQL. Cols: `symbol`, `trade_date`, `TIMESTMP`, `exp`, `strike`, `cp`, greeks, bid/ask, IVs | 2024-12-02 (ends 2024-12-31) | Zach Dietz |
| `optionsResearch.t_index_snaps_bbg` | Index level ticks captured from Bloomberg (i.e. VIX INDEX). ~21M rows. Last row 2026-04-29 -- Zach maintains this manually by scraping the last 140 trading days (what Bloomberg gives access to) so ask him for updates to this. | Index tick history for the 2025-05 to 2026-04 window if data is not available in `optionsResearch.t_index_snaps_td` or via ThetaData | `vbam_db.get_dev_engine()` -- SQL. Cols: `symbol`, `trade_date`, `TIMESTMP`, `uPrc`, `qty` | 2025-05-08 | Zach Dietz |
| `agentData.bloomberg_bdh_cache` | Team-shared cache of raw (adjust='-') daily Bloomberg bdh pulls: (ticker, field, date) -> value; NULL = "BBG had no data" sentinel. Tickers/fields stored UPPERCASE | Never query directly for research -- use `vbam_utilities.bloomberg.my_bdh`, which reads/writes it automatically | `vbam_db.get_agent_engine()` | 2020-01-02 (seeded from Zach's cache) | James Cahill |
| `agentData.bloomberg_bdp_cache` | Team-shared cache of STATIC Bloomberg bdp reference fields: (ticker, field) -> value_num/value_str; both NULL = "BBG had no value" sentinel. Tickers/fields stored UPPERCASE. Only fields in `bloomberg.BDP_CACHE_FIELDS` are cached -- bdp is a point-in-time snapshot, so fields that change over time (PX_CLOSE_DT etc.) must never be added | Never query directly for research -- use `vbam_utilities.bloomberg.my_bdp`, which reads/writes it automatically | `vbam_db.get_agent_engine()` | 2026-08 | Zach Dietz |
| `agentData.cloudquant_intraday_prices` | Cached CloudQuant intraday price lookups: (symbol, price_datetime) -> price; NULL price = "CloudQuant had no prints" sentinel | Never query directly -- `vbam_utilities.cloudquant.get_prices` / `get_prices_batch` read/write it automatically | `vbam_db.get_agent_engine()` | 2026 | James Cahill |
| Trading calendar | NYSE trading days, half days, monthly/quarterly expiries, Fed days, CPI dates | Any date math or day-type bucketing | `vbam_utilities.calendar`: `trading_range`, `x_days_ago`, `EXPIRIES`, `QUARTERLIES`, `FEDS`, `CPI`, `HALF_DAYS`, `is_month_end` | 2020+ (lists) | Zach Dietz |
| Earnings dates | Hand-maintained per-symbol historical earnings dates | Filtering/bucketing by earnings proximity | `vbam_utilities.earnings.EARNINGS` | 2014+ | Zach Dietz |

## Access examples

```python
# Backtest sandbox (default engine for run_query -- tables unqualified)
from vbam_utilities import vbam_db
df = vbam_db.run_query("""
    SELECT business_date, snap_time, spy_net_imbalance, spy_price
    FROM t_report_consolidated_imbalances
    WHERE snap_time = '15:50:01' AND business_date >= '2025-01-01'
""")

# Prod research schemas (only when not in the sandbox -- fully qualified)
df = vbam_db.run_query(
    "SELECT navDate, officialNavUSD FROM compositions.t_compositions_ETFDailyBasketHeaders "
    "WHERE etfTicker = 'SPY' ORDER BY navDate DESC LIMIT 5",
    engine=vbam_db.get_prod_engine())

# ThetaData: 1s bid/ask for one contract on one day
import datetime as dt
from vbam_utilities.thetadata import get_option_quotes
q = get_option_quotes(root='SPXW', strike=6000, cp='Call',
                      exp=dt.date(2025, 1, 17), trade_date=dt.date(2025, 1, 15),
                      start_time='15:40:00', end_time='16:00:00', interval='1s')

# Bloomberg: cached raw daily closes (zero API hits once cached)
from vbam_utilities.bloomberg import my_bdh
px = my_bdh(['SPY US Equity', 'QQQ US Equity'], 'PX_LAST',
            '2024-01-01', '2024-12-31', adjust='-')

# CloudQuant: intraday price nearest a timestamp
from vbam_utilities.cloudquant import get_prices
p = get_prices('NVDA', dt.datetime(2025, 6, 10, 10, 30))
```
