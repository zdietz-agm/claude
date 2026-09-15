# Alpine VBAM SQL Tables

Hosts:
- **VBAM prod** ("VBAM") = `alpine-vbam-prod.c7wvpkbyvjzb.us-east-1.rds.amazonaws.com`
- **VBAM dev** = `alpine-vbam-dev.c7wvpkbyvjzb.us-east-1.rds.amazonaws.com`

## Connecting -- use `vbam_helpers` (`D:/PycharmProjects/utils/vbam_helpers.py`)

Two connection strings, pick by the schema you need:

| Need | Connection | User | Reachable schemas |
|---|---|---|---|
| `optionsResearch` (`algo_trade_log`, options/index snaps) | `vbam_helpers.dev_connection_string` (== legacy `.connection_string`) | `options_research_user` | `optionsResearch` (dev) |
| **Historical imbalances / NAV / BTIC / ICE bars** (the "VBAM prod tables" below) | `vbam_helpers.prod_connection_string` | `VBAM_Read` (read-only) | `auctionResearch`, `EODStrategies`, `compositions`, `imbalanceSnapshots`, `backtest_sandbox` |

```python
import sys; sys.path.insert(0, "D:/PycharmProjects/utils")
import vbam_helpers, pandas as pd
from sqlalchemy import create_engine, text
eng = create_engine(vbam_helpers.prod_connection_string)          # historical imbal/NAV
df  = pd.read_sql(text("SELECT ... FROM auctionResearch.t_report_consolidated_imbalances WHERE ..."), eng)
```

**Access rules (else you waste cycles):**
- **Always fully-qualify `<schema>.<table>`** on both connections -- explicit, portable, and copy-paste-safe between dev/prod. On prod it's *mandatory*: `VBAM_Read` has no default database (`USE` -> `1044`), so unqualified names fail. On dev it's recommended style (the connection defaults to `optionsResearch`, so unqualified also resolves).
- Prod user (`VBAM_Read`) has read-only SELECT across `auctionResearch`, `EODStrategies`, `compositions`, `imbalanceSnapshots`, `backtest_sandbox`.
- Dev user (`options_research_user`) has only `optionsResearch` -- SELECT-denied on all prod schemas, so never query historical imbal/NAV on the dev connection.

## VBAM prod tables

(Reachable via `prod_connection_string` as `<schema>.<table>` -- schema names as written below.)

- **`imbalanceSnapshots.t_imbal_1550_BasketSnapshots`** (*Real-time*) -- Basket-level real-time SPX/NDX imbal for post 350pm trading. **Cols:** `runDate`, `basket` (`.SPX`/`.NDX`), `snapTimestamp`, `exchNetImbalTotal`, `exchPairedImbalTotal`, `seenPct`.
- **`EODStrategies.t_Monitor_ImbalanceMonitorSnaps`** (*Real-time*) -- 3:40pm SPX imbalance monitor snaps. **Cols:** `runDate`, `tsSnapTime`, `netImbalance`, `period`, `offset`.
- **`EODStrategies.t_strat_FuturesStrategyCKSmash1550_Summary`** (*Real-time*) -- Legacy way of pulling SPX 350pm imbal (used as fallback for t_imbal_1550_BasketSnapshots now).
- **`auctionResearch.t_imbalance_basket_detail`** (*Real-time*) -- 3:55pm basket imbal with sub-second capture timestamps. **Cols:** `run_date`, `basket_name`, `capture_time`, `exch_net_notional`.
- **`auctionResearch.t_report_consolidated_imbalances`** (*T+1*) -- Consolidated SPY/QQQ imbal + intraday prices every second 14:00 - 16:00. 15:50:01 timestamp is the historical source of truth for 3:50pm values of SPX imbal / NDX imbal / SPX paired imbalance; source for `spy_imbalances_<date>.csv`. **This is the go-to table for any historical SPX/NDX net-imbalance question at a given snap time.** `spy_*`/`qqq_*` cols ARE the SPX/NDX imbal (see CLAUDE.md "Imbalance Universe Definitions"). **Cols:** `business_date`, `snap_time`, `spy_net_imbalance`, `spy_paired_imbalance`, `spy_price` (also `qqq_*`).
- **`auctionResearch.t_cme_btic_emini_sp500`** / **`t_cme_btic_emini_nasdaq100`** (*T+1*) -- CME BTIC (basis trade at index close) e-mini trade tape, one row per trade, 2022-08-22 -> present; mirrored in `backtest_sandbox`. ES outright ticks in `auctionResearch.t_cme_emini_sp500`. **Cols:** `transaction_date`, `transaction_time`, `sequence_number`, `instrument_symbol`, `trade_price_decimal`, `trade_quantity`, `trade_aggressor`, `close_open_type`. **Contract selection:** quarterly contracts (Mar/Jun/Sep/Dec); always use the front quarterly -- on roll-overlap dates (~last week before expiry) take the further contract and tell user what you are doing. Likely, the user will want to approve/deny your roll methodology; filter by `instrument_symbol`. **Bloomberg codes:** BTIC = `STE<M><Y> Index`, ES = `ES<M><Y> Index` (e.g. STEZ25/ESZ25 -> STEH26/ESH26 -> STEM26/ESM26); xbbg quirk: past-calendar-year contracts need the 2-digit year (`STEZ25 Index`), current-year contracts the 1-digit (`STEH6 Index`). Full usage docs + backtest conventions: `D:/agent_projects/btic_eod_backtest/README.md`.
- **`auctionResearch.t_trade_price_snaps`** (*T+1*) -- Equity/ETF intraday trade prices at specific snap times. **Cols:** `business_date`, `ticker`, `snap_time`, `trade_price`.
- **`auctionResearch.t_index_level_snaps`** (*T+1*) -- Index levels (VIX etc.) at intraday snap times. **Cols:** `business_date`, `ticker` (e.g. `I:VIX`), `snap_time`, `index_level`.
- **`compositions.t_compositions_ETFDailyBasketHeaders`** (*T+1*) -- Official ETF NAV published end-of-day; required for any Return-to-NAV calc. **Cols:** `navDate`, `etfTicker`, `officialNavUSD`.

## VBAM dev tables (`optionsResearch`)

- **`optionsResearch.t_historical_options_snaps`** (*T+1*) -- Historical SpiderRock option snapshots. Populated via Liberator (recent ~2 years) and via `D:/PycharmProjects/spdr_historical/` S3-archive backfills (older data; SpiderRock AWS bucket `srdatasetarchivehist`). **Cols:** `trade_date`, `exp`, `symbol`, `strike`, `cp`, `bidPrc`, `askPrc`, plus Greeks/IV.
- **`optionsResearch.t_opra_quotes`** (*T+1*) -- 1-second OPRA quote history for 0DTE strikes near SPX close; populated via ThetaData. **Cols:** `trade_date`, `exp`, `strike`, `cp`, `timestmp`, `bidPrc`, `askPrc`.
- **`optionsResearch.t_index_snaps_td`** (*T+1*) -- Index price series cache populated via ThetaData.
- **`optionsResearch.algo_trade_log`** (*same-day, ~60s after trade*) -- Per-algo 2-leg vertical spread attempts/fills (credit AND debit; `direction` = Sell/Buy) from prod EOD scripts (350PM/355PM etc.), written by `D:/PycharmProjects/scratch/algos/algo_trade_logger.py`; fills resolved from `srtrade.msgsrmlegbrkrstate` by grouping_code. Row shape assumes one short + one long leg -- no naked legs or 4-leg structures. **PK:** `trade_date, script_name, algo_name, symbol, cp`. **Cols:** `short_strike`, `long_strike`, `direction`, `size_attempted`, `size_filled`, `price_attempted`, `avg_fill_price`, `wave1_*`/`wave2_*` (limit/filled_qty/fill_time), plus factor snapshot (`spx_price`, `vix`, `atm_vol`, `market_ratio`, `rsi`, `high_low_ratio`, `realized_3m_chg`, `imbal_340`, `imbal_350`, `imbal_355`, `qqq_imbal`, `paired_imbal`, `edge_target_1/2`, `max_edge_1/2`).

## NAV SQL template (SPY NAV joined to imbalance snaps)

Return-to-NAV requires this join -- NAV is NOT in the pre-pulled intraday CSV.

```sql
SELECT
    i.business_date,
    i.snap_time,
    i.spy_universe,
    i.spy_moc_net_imbalance,
    i.spy_dquote_net_imbalance,
    i.spy_exchange_net_imbalance,
    i.spy_net_imbalance,
    i.spy_paired_imbalance,
    i.spy_price,
    i.qqq_net_imbalance,
    b.officialNavUSD
FROM
    auctionResearch.t_report_consolidated_imbalances i
LEFT JOIN
    compositions.t_compositions_ETFDailyBasketHeaders b
    ON i.business_date = b.navDate
WHERE
    b.etfTicker = 'SPY';
```

Return formulas (in bps) -- definitions and conventions live in CLAUDE.md ("Closing Imbalance Conventions"):
- Return to NAV   = `(officialNavUSD / spy_price_at_snap - 1) * 1e4`
- Return to close = `(px_last        / spy_price_at_snap - 1) * 1e4`
