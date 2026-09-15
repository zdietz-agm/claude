# Explanation and Citation Examples -- WRONG vs CORRECTED

All examples below are real pairs from the 2026-07-22 bumped-spread reconciliation chat: what Claude first wrote (WRONG) and what the user corrected it to (CORRECTED). Match the CORRECTED style exactly.

---

## Example 1 -- Explanation conciseness: state values each side saw, then the rule

Lesson: no arrow chains, no bold jargon labels, no source-table names inside the explanation. Plain sentences: the two values, the trigger rules, the outcome.

WRONG:

> Imbal signal-source divergence. Prod live 350 imbal = SPX basket -3.35B (t_imbal_1550_BasketSnapshots), 340 = +0.87B -> GROWS call (350<-2B, |340|<=1B) AND SHRINKS call (340>800M, 350<200M) both fired. Backtest's SPY-ETF consolidated shows 350 = -0.86B (misses the -2B bar) and the 15:40:00 snap is entirely missing from t_report_consolidated_imbalances -> neither fires.

CORRECTED:

> Prod live 350 imbal = -3.35B and 340 imbal = +0.87B while backtest sees 350 imbal = -0.86B and no 340 imbal is visible to backtest. Grows requires 350<-2B, |340|<=1B and shrink requires 340>800M, 350<200M, so neither fire in backtest.

---

## Example 2 -- 100% certainty: never state an unverified prod-side claim

Lesson: with no log and no db entry, "prod credit was under .30" is a pure guess. In trading reconciliation we need 100% certainty to make conclusions. State only the verified side.

WRONG:

> min_price knife-edge. Both parents fired the put (350 buy ~2.4-2.6B, 340 ~410M). Backtest OPRA credit = exactly $0.30 = min_price -> passed the gate -> parent sized 264 lots, no 1-lot, no bump. Prod live credit was a hair under $0.30 -> parent floored to 1 lot -> bumped fired.

CORRECTED:

> Backtest sees credit price of .30 which does not qualify it for bumped strategy (parent would fire).

---

## Example 3 -- Omission beats hedging: don't append "unverified / not recoverable" clauses

Lesson: after fixing Example 2 for certainty, the hedging clause about prod still had to go. Keep it short and sweet; the user will ask for more detail when they want it. Simply say nothing about what you can't verify.

WRONG:

> Backtest sees credit price of .30 which does not qualify it for bumped strategy (parent would fire). Prod's credit is not recoverable (no log or db entry for this date), so why prod 1-lotted is unverified.

CORRECTED:

> Backtest sees credit price of .30 which does not qualify it for bumped strategy (parent would fire).

---

## Example 4 -- Citation conciseness: one sentence pointing at the exact evidence

Lesson: the Citation column answers "How do you know this?" with file path + line (or schema.table + date, workbook + sheet + row). No corroboration chains, no certainty commentary.

WRONG:

> From the comment in prod's bumped_spread_config.py: "Re-added 2026-05-06 at quarter-size ($2.5k/5) in new account EOD28_C42 after retiring on 2026-04-23" -- corroborated by the prod PnL log showing zero VS_MARKET BUMPED trades between 4/23 and 5/14. But the exact 5/6 date rests on that comment (git can't pin it -- the file was only committed 5/13), so by our own certainty standard it's config-comment evidence, not log evidence.

CORRECTED:

> Comment in D:\PycharmProjects\scratch\algos\configs_bumped_spreads\bumped_spread_config.py line 12 states that IMBAL_VS_MARKET was re-added on 5/6/26, implying it was deactivated in prod on 5/5/26.

---

## Example 5 -- Citations use full file names and say what the row records

Lesson: "prod PnL log row for 6/1 (+6,023)" is not readable on the first pass. Cite the full file name (PNL LOG NEW.xlsx, not "prod PnL log") and state what the row records.

WRONG:

> CLOSER fills in optionsResearch.algo_trade_log for 6/15, 6/29, 7/21 and prod PnL log row for 6/1 (+6,023); skip logic at bumped_spread_trader.py line 36 (closer_applied).

CORRECTED:

> CLOSER fills in optionsResearch.algo_trade_log for 6/15, 6/29, 7/21 and PNL LOG NEW.xlsx for 6/1 (GROWS CLOSER recorded +6,023 on 6/1); skip logic at bumped_spread_trader.py line 36 (closer_applied).

---

## Example 6 -- Explanation scope: driver facts only; confirming detail goes nowhere

Lesson: the prod fill legs merely CONFIRM the understanding on a day where the driver is a signal-source divergence. Confirmation detail does not belong in the explanation, and not in the citation either -- the citation cites only evidence for the critical driver. (When the fills themselves ARE the driver -- fill-credit sign flip, strike-selection divergence, size-era magnitude -- they DO belong in the explanation.)

WRONG:

> Prod live 350 imbal = -3.35B and 340 imbal = +0.87B while backtest sees 350 imbal = -0.86B and no 340 imbal is visible to backtest. Grows requires 350<-2B, |340|<=1B and shrink requires 340>800M, 350<200M, so neither fire in backtest. Prod sold the 7205/7220 call spread @ 0.55 (30 lots GROWS, 20 lots SHRINKS).

CORRECTED:

> Prod live 350 imbal = -3.35B and 340 imbal = +0.87B while backtest sees 350 imbal = -0.86B and no 340 imbal is visible to backtest. Grows requires 350<-2B, |340|<=1B and shrink requires 340>800M, 350<200M, so neither fire in backtest.
