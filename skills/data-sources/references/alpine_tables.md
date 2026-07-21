# Alpine VBAM SQL Tables

Hosts:
- **VBAM prod** ("VBAM") = `alpine-vbam-prod.c7wvpkbyvjzb.us-east-1.rds.amazonaws.com`
- **VBAM dev** = `alpine-vbam-dev.c7wvpkbyvjzb.us-east-1.rds.amazonaws.com`

## VBAM prod tables

- **`imbalanceSnapshots.t_imbal_1550_BasketSnapshots`** (*Real-time*) -- Basket-level real-time SPX/NDX imbal for post 350pm trading. **Cols:** `runDate`, `basket` (`.SPX`/`.NDX`), `snapTimestamp`, `exchNetImbalTotal`, `exchPairedImbalTotal`, `seenPct`.
- **`EODStrategies.t_Monitor_ImbalanceMonitorSnaps`** (*Real-time*) -- 3:40pm SPX imbalance monitor snaps. **Cols:** `runDate`, `tsSnapTime`, `netImbalance`, `period`, `offset`.
- **`EODStrategies.t_strat_FuturesStrategyCKSmash1550_Summary`** (*Real-time*) -- Legacy way of pulling SPX 350pm imbal (used as fallback for t_imbal_1550_BasketSnapshots now).
- **`auctionResearch.t_imbalance_basket_detail`** (*Real-time*) -- 3:55pm basket imbal with sub-second capture timestamps. **Cols:** `run_date`, `basket_name`, `capture_time`, `exch_net_notional`.
- **`auctionResearch.t_report_consolidated_imbalances`** (*T+1*) -- Consolidated SPY/QQQ ETF imbal + intraday prices every second 14:00 - 16:00. 15:50:01 timestamp is the historical source of truth for 3:50pm values of SPX imbal / NDX imbal / SPX paired imbalance; source for `spy_imbalances_<date>.csv`. **Cols:** `business_date`, `snap_time`, `spy_net_imbalance`, `spy_paired_imbalance`, `spy_price` (also `qqq_*`).
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
