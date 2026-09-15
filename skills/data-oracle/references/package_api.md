# vbam_utilities cheat-sheet

Install: `pip install -e ".[all]"` (repo root) or
`pip install git+https://github.com/AlpineGlobalMgmt/vbam-data-oracle`.
Credentials are built in (`config.py`) — nothing to configure. Override any
key via env var or `~/.vbam/credentials.json`.

Provider modules (`thetadata`, `bloomberg`, `cloudquant`, `earnings`,
`excel_pivots`, `chat`) are reached as `vbam_utilities.<module>`; they are not
re-exported at package level so an optional dependency can't break the import.

All functions accept `start=`/`end=` (inclusive; str `'YYYY-MM-DD'` or
date-like) or `date=` for a single day. Unbounded queries raise.

## Market data

```python
import vbam_utilities as vbam

# Daily OHLCV (canonical adjusted table; DB first, Liberator gap-fill)
bars = vbam.get_daily_bars(["SPY", "AAPL"], "2026-06-01", "2026-06-30")
# Actual traded prices (divide by adjustment_factor):
traded = vbam.get_daily_bars(["KO"], date="2026-03-14", deadjust=True)

# Rolling volatility (vol_10d..vol_90d); trails ~2 sessions — expected
vol = vbam.get_volatility(["NVDA"], "2026-06-01", "2026-06-30")

# 1-min auction imbalances (NYSE+NASDAQ) with clearing_price_effective
imb = vbam.get_imbalances(["NVDA", "NXT"], date="2026-07-17",
                              window=("15:50:00", "16:00:00"))

# Single-stock MOC imbalance at exact seconds -- raw ICE ticks via CloudQuant,
# cached per (symbol, date) in agentData. Signed buy-positive shares.
from vbam_utilities.eod_imbalances import get_single_stock_imbalances_1550_1600
snaps = get_single_stock_imbalances_1550_1600(["NVDA"], "2026-07-01", "2026-07-17",
                                              snap_times=["15:55:01"])

# 10-sec intraday trade prices — symbols mandatory (119 GB table)
px = vbam.get_intraday_prices(["AAPL"], date="2026-07-17",
                                  window=("15:00:00", "16:00:00"))

# 60-sec bid/ask/mid quotes (NYSE-only feed, pre-market 9:00-9:30)
q = vbam.get_intraday_quotes(["KO"], date="2026-07-17")

# ETF creation/redemption flows (history back to 2020-08)
flows = vbam.get_etf_flows(["SPY", "QQQ"], "2026-01-01", "2026-07-30",
                               min_days_elapsed=1)   # 1 = consecutive sessions only
```

`get_etf_flows` returns `flow_usd` (+ creation / - redemption), `flow_pct_aum`,
`creation_units`, `shares_change`, `premium_discount_bps` and `days_elapsed`.
**Use `navDate`, not `compositionDate`, as the flow date** — see the timing
note in `semantics_and_quirks.md`.

`source=` on bars/imbalances/prices: `'auto'` (default; DB + gap awareness),
`'db'`, `'api'` (Liberator only — TICK grain for intraday datasets, different
shape than DB snapshots). Mixed frames carry a `source` column.

## Backtest wide tables

```python
from vbam_utilities.backtest import load_open_data, load_close_data
opens = load_open_data("2026-01-01", "2026-06-30",
                       columns=["business_date", "symbol", "overnight_change_pct",
                                "imbalance_ratio_0928", "price_0930", "price_1000"],
                       exchanges=["NYSE"], min_price=5, min_volume=1_000_000)
closes = load_close_data("2026-06-01", "2026-06-30")   # require_afternoon=True default
```

## Universe / compositions

```python
vbam.get_universe()                      # latest composition date
vbam.get_compositions("SPY", date="2026-03-31")
vbam.get_all_etfs(); vbam.get_symbols_by_exchange()
```

## Calendar

```python
vbam.trading_days("2026-01-01", "2026-06-30")   # DatetimeIndex
vbam.is_trading_day("2026-07-03")               # False (July 4th observed)
vbam.next_trading_day("2026-07-02")             # date(2026, 7, 6)
vbam.prev_trading_day("2026-07-06", n=2)
```

## Snapshot resampling (ticks -> grid)

```python
grid = vbam.build_snapshot_grid(run_date, "15:50:00", "16:00:00", interval_seconds=60)
snaps = vbam.resample_to_snapshots(raw_ticks, grid, symbols, ["trade_price"])
```

## Escape hatch (still read-only)

```python
from sqlalchemy import text
eng = vbam.get_engine()                  # or get_engine('compositions')
df = pd.read_sql(text("""
    SELECT business_date, symbol, moc_net_imbalance_1550
    FROM auctionResearch.t_backtest_close_strategies
    WHERE business_date BETWEEN :s AND :e AND symbol IN ('SPY')
"""), eng, params={'s': '2026-06-01', 'e': '2026-06-30'})
```

Session is forced `transaction_read_only = ON` with a 120s query cap —
writes fail even if you try.
