"""Starter harness for the reconcile-backtests skill.

Loads the prod PnL log (by_strategy) and a backtest Excel, outer-joins them per
strategy over a date window, and prints the Cat 1/2/3 discrepancy classification.
Also provides load_spdr_trades() for per-leg prod fills (suffix selection rule).

Usage:
    python compare_backtest_vs_prod.py <backtest_xlsx> [--start YYYY-MM-DD] [--end YYYY-MM-DD]

Edit SHEET_TO_PROD_NAME below to map backtest sheet names to prod strategy names
for the strategies being reconciled. Do not fuzzy-match names.
"""
import argparse
import datetime as dt
import glob
import os
import re

import pandas as pd

PROD_PNL_LOG = r"C:\Users\zdietz\White Bay Dropbox\Zach Dietz\VBAM Options\PNL LOG NEW.xlsx"
SPDR_TRADES_DIR = r"C:\Users\zdietz\Desktop\spdr_trades"

# Backtest sheet name -> prod strategy name (PNL LOG NEW by_strategy column).
# EDIT PER RECONCILIATION. Explicit mapping only -- a silent mismatch creates a
# false "prod didn't trade" row, the worst error class in this workflow.
SHEET_TO_PROD_NAME = {
    "IMBAL_GROWS BUMP": "ALGO_42 350PM SPREAD SALES SPX IMBAL GROWS BUMPED",
    "IMBAL_VS_MARKET BUMP": "ALGO_42 350PM SPREAD SALES SPX IMBAL VS MARKET BUMPED",
    "IMBAL_SHRINKS BUMP": "ALGO_42 350PM SPREAD SALES SPX IMBAL SHRINKS BUMPED",
}

SPDR_COLS = ["instrument", "side", "qty", "avg_price", "account", "strategy", "broker", "settle_date"]


def load_prod_log():
    """Return the by_strategy tab of PNL LOG NEW.xlsx with trade_date as date."""
    df = pd.read_excel(PROD_PNL_LOG, sheet_name="by_strategy")
    df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.date
    return df


def pick_spdr_file(trade_date):
    """Return the correct spdr_trades CSV path for a date.

    Rule: prefer a non-numeric suffix (e.g. _FIXED); else the highest numeric
    suffix (e.g. _20); else the plain MM_DD_YYYY.csv. Returns None if no file.
    """
    base = trade_date.strftime("%m_%d_%Y")
    paths = glob.glob(os.path.join(SPDR_TRADES_DIR, base + "*.csv"))
    plain, numeric, non_numeric = None, [], []
    for p in paths:
        stem = os.path.splitext(os.path.basename(p))[0]
        suffix = stem[len(base):]
        if suffix == "":
            plain = p
        elif re.fullmatch(r"_\d+", suffix):
            numeric.append((int(suffix[1:]), p))
        else:
            non_numeric.append(p)
    if non_numeric:
        return sorted(non_numeric)[0]
    if numeric:
        return max(numeric)[1]
    return plain


def load_spdr_trades(trade_date, strategy_contains=None):
    """Return per-leg prod fills for a date as a DataFrame (SPDR_COLS schema).

    trade_date: dt.date of the trades.
    strategy_contains: optional substring filter on the strategy column.
    Side codes: B = buy, H = sell short. Net spread credit = short price - long price.
    """
    path = pick_spdr_file(trade_date)
    if path is None:
        return pd.DataFrame(columns=SPDR_COLS)
    df = pd.read_csv(path, header=None, names=SPDR_COLS)
    if strategy_contains:
        df = df[df["strategy"].str.contains(strategy_contains, case=False, na=False)]
    return df


def classify(bt, prod):
    """Classify one strategy's merged backtest/prod rows into Cat 1/2/3 buckets."""
    m = bt.merge(prod, on="trade_date", how="outer", indicator=True).sort_values("trade_date")
    cat1_bt_only = m[m["_merge"] == "left_only"]
    cat1_prod_only = m[m["_merge"] == "right_only"]
    both = m[m["_merge"] == "both"].copy()
    cat2 = both[(both["total_pnl"] * both["pnl"]) < 0]
    agree = both[(both["total_pnl"] * both["pnl"]) >= 0].copy()
    ratio = (agree["total_pnl"] / agree["pnl"]).abs()
    cat3 = agree[(ratio > 3) | (ratio < 1 / 3)]
    ok = agree[(ratio <= 3) & (ratio >= 1 / 3)]
    return cat1_bt_only, cat1_prod_only, cat2, cat3, ok


def compare(backtest_path, start=None, end=None):
    """Print Cat 1/2/3 classification per strategy in SHEET_TO_PROD_NAME.

    backtest_path: path to the backtest Excel.
    start/end: optional dt.date bounds; default = prod first/last trade per strategy.
    """
    prod_all = load_prod_log()
    for sheet, prod_name in SHEET_TO_PROD_NAME.items():
        bt = pd.read_excel(backtest_path, sheet_name=sheet)
        bt["trade_date"] = pd.to_datetime(bt["trade_date"]).dt.date
        bt = bt[bt["total_pnl"].notna() & (bt["total_pnl"] != 0)]
        prod = prod_all[prod_all["strategy"] == prod_name]
        lo = start or (prod["trade_date"].min() if len(prod) else None)
        hi = end or prod_all["trade_date"].max()
        if lo is None:
            print(f"\n=== {sheet}: no prod trades found for '{prod_name}' -- check the name map")
            continue
        bt = bt[(bt["trade_date"] >= lo) & (bt["trade_date"] <= hi)]
        prod = prod[(prod["trade_date"] >= lo) & (prod["trade_date"] <= hi)]
        c1b, c1p, c2, c3, ok = classify(bt, prod[["trade_date", "pnl", "notes"]])
        print(f"\n=== {sheet} vs {prod_name}  ({lo} to {hi})")
        print(f"BT days: {len(bt)} | PROD days: {len(prod)}")
        for label, d in [("Cat1 BT-only", c1b), ("Cat1 PROD-only", c1p),
                         ("Cat2 sign flip", c2), ("Cat3 magnitude (>3x)", c3), ("OK", ok)]:
            print(f"\n-- {label}: {len(d)}")
            if len(d):
                cols = [c for c in ["trade_date", "total_pnl", "pnl", "notes"] if c in d.columns]
                print(d[cols].to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("backtest_xlsx")
    ap.add_argument("--start", type=dt.date.fromisoformat, default=None)
    ap.add_argument("--end", type=dt.date.fromisoformat, default=None)
    args = ap.parse_args()
    compare(args.backtest_xlsx, args.start, args.end)
