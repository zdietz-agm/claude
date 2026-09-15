# Database reference (condensed)

Three schemas on one RDS instance
(`alpine-vbam-prod.c7wvpkbyvjzb.us-east-1.rds.amazonaws.com`), read via the
`vbam_team_ro` user. Full inventory: `docs/vbam_database_guide.md`
(regenerable via `docs/generate_db_inventory.py`).

Size classes: **small** (config), **medium** (date-bound required), **huge**
(date AND symbol bounds required — enforced by vbam_utilities).

## auctionResearch (market data)

| Table | Grain | Size | Key columns | Notes |
|---|---|---|---|---|
| t_backtest_open_strategies | 1 row/symbol/day | medium | business_date, symbol, exchange, prev_close, open_price, overnight_change_pct, OHLCV, vol_10d..90d, clearing_price/imbalance_side/imbalance_vol/auction_vol/imbalance_ratio at 0920–0930, mid_price_0925–0930, price_0930–1000, twap_open_0935–1000 | Denormalized open-auction table. Prices are DE-ADJUSTED (actual traded). Coverage 2022+. NASDAQ mid_price_* mostly NULL (NYSE-only quote feed). |
| t_daily_twap_levels | 1 row/symbol/day | small (~0.5M rows) | business_date, symbol, is_etf, n_marks, 25 twap_START_END columns: exit-to-close (twap_0930_1600 … twap_1530_1600, every 30 min) + from-open (twap_0930_1000 … twap_0930_1530). Means of 1-MINUTE last-trade marks; both window ends in the name | SPX members (point-in-time SPY basket) + 14 index/sector ETFs (SPY/QQQ/IWM/DIA + 11 SPDRs). 2022-03-11 →. NULL TWAPs when a symbol's last trade < 15:30 (n_marks still set); half-days skipped entirely. For "exit over the day" counterfactuals. Loader: MarketDataLoaders loaders/daily_twap_levels.py; sandbox copy maintained nightly. |
| t_backtest_close_strategies | 1 row/symbol/day | medium | business_date, symbol, MOC snaps (buy/sell/paired/net/ratio/price at 1500–1550), dquote_net_imbalance_*, total_net_imbalance_*, exchange imbalance snaps 1550–1600, price_1500–1600, twap_1500_HHMM (BACKWARD mean 15:00→HH:MM — context, NOT an entry price; named twap_close_* until 2026-08-21), twap_HHMM_1600 for HH:MM=1550..1559 (FORWARD mean HH:MM→16:00 = the executable entry for an order evaluated at HH:MM — use these for P&L), close_vs_1500_pct | Half days: afternoon columns NULL — filter with price_1500 IS NOT NULL (load_close_data does this by default). TWAP trap: any P&L priced on the old twap_close_1550/1555 used a 15:00-anchored backward mean (INTC 2026-05-29: 118.52 vs forward 115.33). Exchange snap era: 1550/1551 sparse before 2026-07-08; 1551+ always ~92% filled. |
| t_ice_daily_bars_adjusted | 1 row/symbol/day | medium | OHLCV, unadjusted_close, adjustment_factor, dividend_*, split_ratio | CANONICAL daily bars. Adjusted as-of-fetch-time — see quirks. T+2 lag. |
| t_ice_daily_bars | 1 row/symbol/day | medium | OHLCV | Unadjusted values correct BUT missing ~30-90 delisted symbols/day 2024-2025. Avoid. |
| t_volatility_ticker | 1 row/symbol/day | medium | vol_10d..vol_90d, daily_return, close | From adjusted closes (correct — do not de-adjust). Trails ~2 sessions. |
| t_ice_intraday_prices | 10-sec snaps | **huge** (119 GB) | business_date, symbol, capture_timestamp, trade_price | Only loaded sessions: 9:30–10:00 and 15:00–16:00. Coverage 2022-03-11+. |
| t_ice_intraday_quotes | 60-sec snaps | huge | bid/ask price+size, mid_price, spread_pct | NYSE-only source feed; pre-market window 9:00–9:30. |
| t_ice_intraday_imbalances | per-sec 15:50:01-15:50:30, then 1-min to 16:00 (pre-open 1-min) | medium (85M rows) | imbalance_side, order_imbalance_vol, auction_vol, clearing_price, near/far_indic_clear_price, ref_price, auction_price, imbalance_ratio | NYSE + NASDAQ. Use clearing_price_effective from vbam_utilities (NASDAQ COALESCE). Windows: pre-open 9:00–9:30 + MOC 15:50–16:00 (nothing 15:40-15:50 -- exchanges publish at 3:50). MOC grain NOT uniform 1-min: per-second burst 15:50:01-15:50:30. |
| t_moc_symboldata | snaps 14:00–15:55 | medium | xdate, symbol, buyImbalance, sellImbalance, paired, price, xtime | External MOC feed. xtime is a TIME column — see quirks. |
| t_prices_daily_price_capture (auctionResearch, prod -- NOT sandbox) | ~1-sec near close, 10-sec earlier | huge (11-18M rows/day) | run_date, capture_timestamp, ticker, imbalance_side, order_imbalance_vol, auction_vol, clearing prices, bid/ask, price | Full universe ~2,584 tickers, 2026-01-13+ (partial first day). Jittered sub-second timestamps -- as-of, never equality. ALWAYS bound by run_date AND ticker; unbounded ticker scans time out. |
| t_prices_daily_price_capture | 1–5 sec capture | **huge** (319 GB) | run_date, ticker, price/bid/ask, clearing prices, imbalance fields | Production capture platform (separate codebase). Query ONLY by (run_date, ticker) — indexed. Served externally via the VBAMDataLens REST API. |

Other groups (report tables t_report_*, S3 short interest t_s3_*, BTIC
futures, DQuote, CME) exist — see the full guide; query via `get_engine()`
with bounds.

## backtest_sandbox

Read-only nightly copy (~5 AM ET refresh) of the curated tables for AI
agents; 2024+ trailing window on date-keyed tables. Same table names. Use
prod (above) unless specifically working in the sandbox context.

## compositions (universe / config)

| Table | Notes |
|---|---|
| t_compositions_ETFDailyBaskets | ETF constituents per compositionDate: ticker, ETFTicker, BBGExchange, shares, weight, sedol, gicsCode, basketTypeId. **TWO basketTypeId rows per name — always DISTINCT** (vbam_utilities.symbols does this). Forward-dated: max date = next session. 2020-05+. Since the 2026-07 field expansion also carries per-name `adv30d`/`adv180d` (vendor ADV), `officialClosePrice`/`officialCloseCCY`/`priceDate`, `calculationPrice`, `cashInLieu`, `assetClass` (EQU vs cash lines), `securityStatus`, `delistingDate`, `ultID` — all NULL for dates before the migration. |
| t_compositions_ETFDailyBasketHeaders | One row per (compositionDate, ETFTicker): CRSize, creation/tracking cash, shareClassAUMUSD, navDate, officialNavUSD; plus (2026-07+) `sharesOutstanding`, `fundAUMUSD`, `navChange`, `expenseRatio`, `ocf`, `ragStatus` (vendor data-quality flag), `referenceDate`, `ultShareClassID`, `trackedIndexRIC`, `creation/trackingNumberOfAssets` vs `creation/trackingRowsLoaded` (load-integrity check), `payloadVersion`. |
| t_reference_UltumusSecurity | Slowly-changing security master keyed on componentBBGTicker (~15K rows): RIC, ISIN, CUSIP, SEDOL, FIGI, CompositeFIGI, securityName, assetType, bbgSecurityType/MarketSector, cfiCode, **countryOfIncorporation / domicility / msciCountry** (explains why a name is or is not in a domicile-restricted index), exchange shortName/fullName/micCode/operatingMic/country, primaryListing, lotSize, listingDate, firstSeen/lastSeen. |
| t_config_DailyBasketImport | Driver for which baskets the Ultumus loader pulls: basketTicker, basketTypeId, ultumusID, outputShared, `isActive` (0 = staged/disabled), `inMarketDataUniverse` (0 = compositions only; does not expand the nightly market-data symbol universe). |
| t_ultumus_payload_archive | Fund-level Ultumus payloads as JSON with `assets` stripped, keyed (compositionDate, ETFTicker). Insurance for fund-level fields not yet columnized. |
| t_ops_basket_load_status | Per-ETF load outcome per run: status, rows loaded vs expected, duration, HTTP attempts, error. Query this instead of reading the loader emails. |
| t_config_nyse_holidays | holiday_date, description. Backs vbam_utilities.calendars. |

**View `v_compositions_ETFBasketsEnriched`** — basket rows LEFT JOINed to the
security reference, so identifiers / domicile / exchange codes are available
flat without writing the join yourself.

> Universe semantics: `vbam_utilities.get_all_symbols` and `get_symbols_by_exchange`
> honour `inMarketDataUniverse` (they answer "what does the nightly pipeline
> load?"). `get_universe`, `get_compositions` and `get_all_etfs` do not — asking
> what is inside a basket always answers, flagged or not.
