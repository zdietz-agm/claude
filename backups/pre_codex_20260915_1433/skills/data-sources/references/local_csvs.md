# Local Pre-Pulled CSVs (T+1)

## `D:/agent_projects/eod_option_algos/`

- **`spy_imbalances_<MM_DD_YYYY>.csv`** -- Daily snapshot of `auctionResearch.t_report_consolidated_imbalances`. Latest dated file is current; refreshed daily by `D:/agent_projects/eod_option_algos/update_data.py`.
  - **Schema:** `business_date, snap_time, spy_moc_net_imbalance, spy_dquote_net_imbalance, spy_net_imbalance, spy_paired_imbalance, spy_price, qqq_net_imbalance, qqq_paired_imbalance, qqq_price`.
  - `snap_time` is a string `"0 days HH:MM:SS"` (pandas timedelta serialization). Parse with `pd.to_timedelta` if you need numeric ops; filter directly on the string for exact-snap lookups (e.g. `snap_time == "0 days 15:50:01"`).
  - Populated every second from 14:00 to 16:00 -> use directly for any intraday imbal / price slicing without re-querying VBAM.
  - Does **not** include `officialNavUSD` -- run the NAV SQL in [alpine_tables.md](alpine_tables.md) if NAV is needed.
- **`SPXW_0DTE_opra_panel.csv`** / **`NDXP_0DTE_opra_panel.csv`** -- 0DTE option quotes panel for backtests. **Cols:** `trade_date`, `exp`, `strike`, `cp`, time-bucketed bid/ask. Only includes strikes that were close to at the money (for further strikes, pull from t_opra_quotes in VBAM Dev).

## `D:/PycharmProjects/scratch/imbal_research/data/`

- **`spy_daily_moves_<HH_MM>.csv`** / **`qqq_daily_moves_<HH_MM>.csv`** -- Per-day market_ratio + RSI3 at the snap time encoded in the filename. **Cols:** `date`, `trade_price`, `yest_close_price`, `rolling_std`, `market_ratio`, `rsi3`. Updated by `python D:/agent_projects/eod_option_algos/update_data.py` -- step `3a` writes the `_50_01` files, step `3b` the `_40_00` files (both included in a default run; target with `--steps 3a,3b`). For any OTHER snap time, use `python D:/agent_projects/eod_option_algos/build_daily_moves.py <HH:MM:SS>` (e.g. `15:55:01`, `14:00`) -- same logic, writes `spy/qqq_daily_moves_<suffix>.csv` (suffix: `MM_SS` for 15:xx times, `HH_MM_SS` otherwise, `00_00` for 16:00:00 close).
  - Filename suffix is the **actual snap second**: 3:50pm -> `_50_01` (15:50:**01**) and 3:55pm -> `_55_01` (15:55:**01**) -- the post-imbalance-publication ticks; all other timestamps use the exact minute at :00 (`_40_00` -> 15:40:00, `_00_00` -> 16:00:00 close).
  - For any 3:50pm filter / threshold work, always use the `_50_01` file (see "Closing Imbalance Conventions" in CLAUDE.md).
  - For other intraday times, compute market_ratio manually: pull the price at time T from `auctionResearch.t_report_consolidated_imbalances` (has data starting 2 hours before close) or `cq_helpers` (for morning data), then `(price_T - yest_close_price) / rolling_std` using the rolling_std from the nearest pre-computed CSV.
- **`spy_high_low_<HH_MM>.csv`** -- Intraday SPY high/low up to snap time + range-to-vol ratio. **Cols:** `business_date`, `highest_trade_price`, `lowest_trade_price`, `diff_pct_ratio`.
- **`vix_<HH_MM>.csv`** -- VIX level at snap time + intraday return. **Cols:** `business_date`, `index_level`, `yest_close`, `ret`.
- **`rolling_realized.csv`** -- Rolling 3-month annualized realized vol for SPY + day-over-day change. **Cols:** `trade_date`, `3m`, `3m_change`.
