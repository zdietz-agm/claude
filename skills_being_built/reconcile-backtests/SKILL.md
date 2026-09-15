---
name: reconcile-backtests
description: Reconcile a strategy backtest export against prod PnL (what we actually traded) -- classify per-date discrepancies, chase root causes with verified evidence only, and present a Reconciliation Table with citations. Use whenever the user asks to reconcile or compare a backtest vs prod/actual/realized PnL, asks "why did prod trade when backtest didn't" (or vice versa), questions a PnL sign or magnitude mismatch on specific dates, or mentions PNL LOG NEW.xlsx / spdr_trades in a backtest-comparison context. Not for building or running backtests themselves.
---

# Reconcile Backtests vs Prod

Compare a backtest export against the prod PnL log and explain every discrepancy with **verified evidence only**. This is a trading reconciliation: a wrong conclusion is worse than no conclusion, because it can drive a bad sizing or config decision.

## Inputs

- **Backtest Excel**: usually in `C:/Users/zdietz/Downloads/` (e.g. `bumped_spread_backtest_YYYYMMDD_HHMM.xlsx`, `EOD_OPTION_ALGOS_*.xlsx`). Per-strategy sheets have columns like `trade_date, put_size, call_size, put_price, call_price, sh_strike, lg_strike, total_pnl`.
- **Prod PnL log**: `C:\Users\zdietz\White Bay Dropbox\Zach Dietz\VBAM Options\PNL LOG NEW.xlsx` (desktop shortcut "PNL LOG NEW - Shortcut.lnk"), tab `by_strategy`, columns `trade_date, strategy, account, acc_code, pnl, notes`. READ THE NOTES COLUMN -- it often contains the explanation already.
- Strategy name mapping: backtest uses underscores (`IMBAL_GROWS BUMP`), prod log uses spaces and slightly different suffixes (`ALGO_42 350PM SPREAD SALES SPX IMBAL GROWS BUMPED`). Build an explicit map -- a silent fuzzy-match mismatch produces a false "prod didn't trade" row, the worst error class in this workflow.
- **SpiderRock trade CSVs** (`C:\Users\zdietz\Desktop\spdr_trades\`): per-leg prod fills for all SpiderRock-executed trades (the majority of algo trading), one file per date named `MM_DD_YYYY.csv`. **File selection when suffixed versions exist**: prefer a non-numeric suffix (e.g. `07_22_2026_FIXED.csv`); else the HIGHEST numeric suffix (e.g. `07_22_2026_20.csv`); else the plain file. No header row; columns: instrument (e.g. `SPXW US 5/8/2026 P7390.0 Index`), side (`B`=buy, `H`=sell short), qty, avg fill price, account, strategy (prod space-separated name), broker, settlement date. This is the **best evidence for prod strikes, size, and fill price on any date** -- net spread credit = short-leg price minus long-leg price, and `credit x qty x 100` should reconcile to the PnL-log row on full-win days. Prefer it over config-comment sizing inference.

## Scripts

`scripts/compare_backtest_vs_prod.py` -- starter harness: loads the prod PnL log and a backtest Excel, outer-joins per strategy over a date window, prints the Cat 1/2/3 classification, and includes `load_spdr_trades(date)` implementing the suffix rule plus per-leg net-credit computation. Start from it instead of rewriting the merge each time.

## Workflow

1. **Window**: restrict comparison to the prod deployment window per strategy (first prod trade date, or deployment date from config comments / prod_change_logs). Backtest history before deployment is expected to be backtest-only -- not a discrepancy.
2. **Outer-join** backtest and prod rows on `(trade_date)` per strategy. Classify each mismatch:
   - **Cat 1** (most important): one side traded, other did not (both directions).
   - **Cat 2**: both traded, PnL sign disagrees.
   - **Cat 3**: both traded, sign agrees, magnitude is off (e.g. 1k vs 10k).
3. **Build the sizing-era timeline BEFORE investigating Cat 3.** Sources:
   - `git log -p` on the strategy config files in `D:/PycharmProjects/scratch/algos/configs*/`
   - `SIZE_KNOB` history: `git log -p -- algo_globals.py` in `D:/PycharmProjects/scratch/algos/` (knob multiplies scaled() dollar_targets and max_sizes; it has changed many times)
   - `D:/agent_projects/eod_option_algos/prod_change_logs/` and inline config comments
   - Backtests often auto-sync sizing from TODAY's prod config and apply it to all history -- this alone guarantees magnitude diffs on older dates.
4. **Check layer precedence before flagging backtest-only days as signal misses.** E.g. prod skips the bumped layer whenever CLOSER fired on the same parent (`closer_applied` flag, `bumped_spread_trader.py`); the bumped backtest does not model this. A backtest-only day where CLOSER shows up in the prod log or algo_trade_log is explained.
5. **Pull prod fills from spdr_trades for every discrepancy date.** Strikes, size, and net credit per strategy resolve most Cat 2/3 rows outright (fill-credit sign flips, strike-selection divergence, exact lot counts).
6. **Normalize to per-lot PnL** when comparing magnitudes: `pnl / lots / 100`. Sizing-era noise separates from real fill/signal differences.
7. **Diff the signal-source pair on trigger-mismatch days.** Prod and backtest read DIFFERENT imbalance sources:
   - Prod live sources: **read `D:\PycharmProjects\scratch\algos\imbalance_sources_note.txt`** -- the maintained note with the exact SQL (primary + fallback) for each live imbalance the prod scripts consume. As of 7/22/26 it covers: 340pm SPY (`imbalanceSnapshots.t_imbal_BasketSnapshots`, fallback `EODStrategies.t_Monitor_ImbalanceMonitorSnaps`), 350pm SPY (`imbalanceSnapshots.t_imbal_1550_BasketSnapshots`, fallback `EODStrategies.t_strat_FuturesStrategyCKSmash1550_Summary`), 355pm SPY (`auctionResearch.t_imbalance_basket_detail`), and single-stock EOD (`auctionResearch.t_prices_daily_price_capture`). Use the note's queries verbatim (userName / seenPct / time-window filters matter).
   - Backtest: SPY-ETF `auctionResearch.t_report_consolidated_imbalances` (T+1) via the local imbalance CSV.
   These can diverge hugely (observed 5/4/26: basket -3.35B vs ETF -0.86B) and the consolidated table can have missing snap rows. Query both sides before assuming a bug.
8. **Check knife-edges**: credits at exactly `min_price`, settles within a few dollars of the short strike, strike selection one index apart (live uPrc vs backtest cross-ratio index estimate). Near a boundary, tiny quote differences flip fire/no-fire or win/lose.

## Evidence sources and their availability boundaries

| Source | What it proves | Available |
|---|---|---|
| SpiderRock trade CSVs `C:\Users\zdietz\Desktop\spdr_trades\MM_DD_YYYY.csv` | prod per-leg fills: strikes, size, avg price, account, strategy | full history |
| `optionsResearch.algo_trade_log` (VBAM dev) | prod strikes, size_attempted/filled, prices, factor snapshot | from **2026-06-15** |
| Raw script logs `D:/PycharmProjects/scratch/algos/logs/<date>_<script>.txt` | everything the script printed (authoritative) | local from **2026-07-16**; older on old PC (pending recovery) |
| PNL LOG NEW.xlsx `by_strategy` | that prod traded, realized pnl, notes | full history |
| Prod SQL live-source tables (step 7 above) | what data prod's query WOULD have returned | full history |
| Config git history + prod_change_logs | sizing/trigger definitions in force on a date | full history |
| Full parent backtest Excel (`EOD_OPTION_ALGOS_*.xlsx`) | what the backtest parent did (fired? size? credit?) | regenerate anytime |

## The 100% certainty rule (CRITICAL)

Only state as fact what is directly observed in a log, DB row, file, or code path. Unverified claims are simply **omitted** from the table -- no speculation, and no hedging labels either ("unverified", "not recoverable" appear only if the user explicitly asks about the unknown detail). In trading reconciliation we need 100% certainty to make conclusions; stating only the verified side and stopping is always acceptable.

A clean arithmetic fit (pnl divides exactly into N lots at backtest per-lot pnl) is "consistent with", never "was" -- unless the size is then confirmed in spdr_trades or a log, at which point state it plainly.

## Output format: the Reconciliation Table

One table, ordered by category importance (1, 2, 3, then healthy baseline rows). Columns: `Date | Strategy | Backtest | Prod | Explanation | Citation`.

**REQUIRED READING before writing any explanation or citation: [references/explanation_examples.md](references/explanation_examples.md)** -- six real WRONG vs CORRECTED pairs from the reconciliation chat that defined this skill. Match the CORRECTED style exactly. The rules they encode:

1. **Explanation voice**: state the values each side saw, then the trigger rule and outcome, in plain sentences. No arrow chains, no bold jargon labels, no source-table names unless essential. 1-2 sentences of decisive verified facts per row; the user will ask for more detail when they want it.
2. **Omission beats hedging**: never state unverified claims, and never append "unverified / not recoverable" clauses -- just say nothing about what you can't verify.
3. **Explanation scope**: only the facts that DRIVE the discrepancy. Detail that merely confirms the understanding (e.g. fill legs on a signal-divergence day) goes nowhere -- not in the explanation, not in the citation. When the fills ARE the driver (fill-credit sign flip, strike divergence, size-era magnitude), they belong.
4. **Citation column**: answers "How do you know this?" in one sentence pointing at the exact evidence -- file path + line, schema.table + date, workbook + sheet + row. No corroboration chains, no certainty commentary.
5. **Full file names in citations** (PNL LOG NEW.xlsx, not "prod PnL log"), and say what the cited row records.

Reference explanations (final approved versions):

> Prod live 350 imbal = -3.35B and 340 imbal = +0.87B while backtest sees 350 imbal = -0.86B and no 340 imbal is visible to backtest. Grows requires 350<-2B, |340|<=1B and shrink requires 340>800M, 350<200M, so neither fire in backtest.

> Backtest sees credit price of .30 which does not qualify it for bumped strategy (parent would fire).

> Prod CLOSER fired on these days and prod skips bumped when CLOSER trades. Backtest does not model CLOSER precedence.

> Identical trade (7590/7575 puts @ 0.55 credit, -$514/lot); prod 66 lots vs backtest 96.

> Sign and per-lot magnitude agree within ~4-15% (prod fills: 66 @ 0.75, 72 @ 1.38).
