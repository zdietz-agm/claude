---
name: 355pm-grouping-code-collision-bug
description: 2026-07-17 355PM no-fill investigation -- resolved as user reading wrong logfile; gc-collision theory retracted; open Q on 7/16 CLOSER filled>attempted
metadata: 
  node_type: memory
  type: project
  originSessionId: e4570c49-5c36-4380-96f1-5f85ce69a98f
---

2026-07-17 investigation of 355PM algo "phantom fills" -- RESOLVED. User was reading the 7/16 logfile while asking about 7/17; no bug in the fill-check.

Facts (verified vs srtrade.msgsrmlegbrkrstate and optionsResearch.algo_trade_log):
- 7/17 regular run (gcs 748-784): 0 fills, "4 of 4 need wave-2", everything expired unfilled. Cause was price: wave-1 limit 1.18 / wave-2 0.97 credit while market moved through those levels.
- 7/17 manual rerun ~55s later (gcs 2189-2212): repriced (0.44/1.42 wave-1, 1.2 wave-2) and filled everything (8/24/18/55). Its output appears BOTH in 2026-07-17_355pm_script.txt (natural append) and pasted by user into the 7/16 file.
- 7/16 regular run (gcs 7076-7103): fills were real (MAINTAINS 42/42, VS_MKT_LOW_VOL 125/125 in wave-1; CLOSERs partial 18/206) -- "2 of 4 need wave-2" was correct.
- No grouping-code collision. brkrstate retention ~24h+; its timestamps are CT (1h behind ET).

Structural weaknesses noted (real but not the cause): gc seed = `microseconds % 10000` (355pm_script.py:22) not run-unique; batched_fill_check_and_cancel SELECTs msgsrmlegbrkrstate by groupingcode alone, no date/run scoping (spdr_rock_order_functions.py:345).

OPEN QUESTION: 7/16 algo_trade_log shows CLOSER filled > attempted (MAINTAINS_CLOSER 176 vs 97; VS_MKT_LOW_VOL_CLOSER 378 vs 292), each over by exactly the wave-2 size (79, 86). Either wave-1 cancel failed and both waves filled fully (real oversell of 165 spreads), or algo_trade_logger double-counts wave-1 final qty + wave-2. Needs reconciliation vs clearing/positions.

**How to apply:** When analyzing 355PM logs, date each run by its internal hacker-query line ("algo_trade_log for YYYY-MM-DD"), not the filename -- files can contain pasted runs from other days.
