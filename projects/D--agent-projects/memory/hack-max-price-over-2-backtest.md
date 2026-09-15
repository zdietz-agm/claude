---
name: hack-max-price-over-2-backtest
description: "355PM hacker backtest days where uncapped hack exit debit > $2.00 (HACK_MAX_PRICE): 14 days / 17 legs, pooled delta -$1.04M -- the $2 cap is protective"
metadata: 
  node_type: memory
  type: project
  originSessionId: a9eb4848-e972-4876-ab7c-4ba98f8dd103
  modified: 2026-08-27T20:08:48.747Z
---

From hacking_355_backtest_20260827_1042.xlsx (most recent run, 8/27/2026; all 7 detail
sheets pooled, `actually_hacked` legs only, filter `hack_exit_cost > 2.00`). The backtest
models UNCAPPED exits (OPRA cross at 15:55:03); prod clamps the debit at HACK_MAX_PRICE=2.00
in hacker_trades.py, so these are the days where prod's cap binds. PnL in dollars.

Of 129 hacked legs on 78 days total: **17 legs on 14 days pay > $2.00**.

| trade_date | n_legs | max_debit | original_pnl | pnl_with_hacking | delta_pnl |
|------------|--------|-----------|--------------|------------------|-----------|
| 2022-01-18 | 1 | 3.80 | 49,840 | -85,440 | -135,280 |
| 2022-05-18 | 1 | 2.45 | 28,480 | -58,740 | -87,220 |
| 2023-10-04 | 1 | 4.05 | -112,275 | -127,245 | -14,970 |
| 2024-06-05 | 2 | 7.35 | -26,547 | -20,895 | +5,652 |
| 2024-07-11 | 1 | 2.85 | -179,640 | -72,355 | +107,285 |
| 2024-07-24 | 1 | 8.90 | -70,132 | -284,800 | -214,668 |
| 2024-09-06 | 1 | 7.25 | -152,368 | -176,220 | -23,852 |
| 2025-03-07 | 1 | 8.40 | 83,660 | -208,260 | -291,920 |
| 2025-04-10 | 1 | 2.30 | 114,450 | 39,240 | -75,210 |
| 2025-10-30 | 1 | 3.10 | -35,956 | -51,620 | -15,664 |
| 2025-11-24 | 1 | 6.05 | 24,920 | -190,460 | -215,380 |
| 2026-03-26 | 1 | 2.15 | 32,040 | -44,500 | -76,540 |
| 2026-04-28 | 2 | 2.15 | 5,880 | -8,085 | -13,965 |
| 2026-08-18 | 2 | 2.25 | -41,013 | -26,460 | +14,553 |
| **Total** | **17** | | **-278,661** | **-1,315,840** | **-1,037,179** |

Key takeaway: hacking at an uncapped price on these days is -$1.04M vs just holding
(only 3 of 14 days had positive delta). The $2.00 cap in [[hacker_trades]] prod code is
strongly protective -- above $2 the unwind is on average far worse than settlement.
Rationale for the 2.00 constant itself was previously undocumented anywhere (README,
backtest, change logs); this analysis is the first quantification.
