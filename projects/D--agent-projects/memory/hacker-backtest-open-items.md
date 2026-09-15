---
name: hacker-backtest-open-items
description: "OPEN to-dos on the 355PM hacker limit-price research (all-parents scope, worse-fill assumption, confirm 1.60 cap) + key findings from the 8/31/26 session"
metadata: 
  node_type: memory
  type: project
  originSessionId: a9eb4848-e972-4876-ab7c-4ba98f8dd103
  modified: 2026-09-03T15:03:42.925Z
---

PROD IMPLEMENTED 2026-08-31 (Zach owns risk checks + live testing before relying on it):
hacker_trades.py TARGET_NAMES 5 -> 15 (10 SPX parents >$10 wide added; NDX + BASE + LOW_VIX
excluded), HACK_MAX_PRICE 2.00 -> 1.70, edges raised to 0.06/0.12 + 0.08/0.16 (DELIBERATELY
over-aggressive to get fills -- re-evaluate after several prod fill days), new WAVE-3: unfilled
remainder rests at exactly -1.70 until 16:00 (orderDuration-based, self-expires), and
refresh_hacker_fills() re-upserts algo_trade_log rows at ~16:00:30 (wired into both 355pm
scripts). 355pm_script_v8 V8_ACCOUNT_MAP + startup assert extended to all 15 source accounts.

Zach's three open items to revisit (stated 2026-08-31):
1. Should the hacker script run across ALL 350PM credit-spread algos (not just 2 CLOSER + 3 BUMPED)?
2. Redo the backtest assuming fills at a WORSE price than the OPRA cross (fast-market slippage).
3. Confirm 1.60 is the best limit price.

Context from the 8/31/26 session (see [[hack-max-price-over-2-backtest]] for the older $2-cap table):
- hacking_355_backtest.py now supports: --uncapped (legacy fill-at-15:55:03-cross), --max-cost X
  (default 2.10; resting-limit model: 15:55:03 fill at cross if <= cap, later per-second fills at
  exactly the cap through 16:00), --all-parents (all 12 prod 350PM_SPREAD_SALES_SPX* configs).
  CLOSER precedence (parent size decrement) is now modeled; output filename carries _capNNN tag.
- Sensitivity sweep (adhoc/hack_limit_price_sensitivity.py): optimum 1.40 (+$752k), plateau
  1.40-1.60 (~$650-750k), 2.10 = +$385k, monotone decline above 1.50. Thin sample: caps differ
  on only ~20 late-fill legs of 131 triggered.
- At cap 1.60: 95% of fills in the 15:55 minute; 14.3% (18/126) fill after the first attempt;
  late fills net negative for the VS_MARKET parent.
- Prod hacker reality check (all logs ever): fired only 7/21/26 + 8/27/26. Wave 1 filled ZERO
  all 4 times. 7/21: GROWS_CLOSER 79/79 filled wave2 @1.00, VS_MARKET_CLOSER 4/211 @1.03
  (backtest said hack both in full at 1.25, delta -$27k/-$75k -- non-fill was lucky).
  8/27: 0/298 (v7) and 0/59 (v8) -- natural 3.0-3.4 vs 2.00 clamp; backtest hacked at 3.50 for
  +$89.5k -- the only missed PROFITABLE hack needed a HIGHER cap, not lower.
- 5PA flagged: adverse selection in resting-limit model, in-sample cap selection, full-size
  top-of-book fill optimism, and recommended v7/v8 A/B before prod changes.

DAILY TASK ADDED 2026-09-03 (Zach approved the plan): scheduled_tasks/run_backtest_hacker.py runs
`hacking_355_backtest.py --max-cost <cap> --all-parents --last-days 5` with the cap regex-read from
prod hacker_trades.py HACK_MAX_PRICE (never hardcode 1.70; script defaults 2.10/2 parents do NOT
match prod). Windows task CreateBacktestsHacker 8:19 weekdays, timeout 600 -- Zach must run
algo_daily_review/register_hacker_backtest_task.ps1 himself (password prompt). Gates: UpdateDataEOD
+ yesterday in t_report_consolidated_imbalances 15:55:01, t_opra_quotes SPXW, opra panel 15:50:07.
Digest: NO standalone hacker section (Zach rejected it) -- a "355 HACKER" sub-block inside the
355pm_script / 355pm_script_v8 blocks, printed only when prod has HACK_ rows or the model
attempted a hack. Flags only: trigger mismatch outside 0.9-1.1B, cap violation, size != floor(parent
filled/2), POSSIBLE WAVE-3 MALFUNCTION (prod attempted, filled 0, model filled). Hack PnL is NOT in
the reconciliation table (PNL LOG blends it into the parent row). Open item 1 above is CLOSED
(TARGET_NAMES = 15). Never run hacking_355_backtest.py with --help or bare: it has no argparse and
executes the full history (~15-25 min, writes a cap210 workbook).
