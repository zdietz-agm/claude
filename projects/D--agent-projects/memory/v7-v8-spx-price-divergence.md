---
name: v7-v8-spx-price-divergence
description: SR v7 vs v8 report DIFFERENT SPX prices/vols from their quote tables ($3 apart at 15:55 on 8/24/2026); comparison scripts exist for both
metadata: 
  node_type: memory
  type: project
  originSessionId: 68c48a6e-de71-4a6c-8928-0ceb9992aa81
  modified: 2026-08-24T20:39:51.624Z
---

SpiderRock v7 and v8 are separate surface/pricing engines and report DIFFERENT values for the
same instrument at the same instant. Observed 2026-08-24:

- SPX (uprc of closest put, exactly how the 355 scripts read it): prod logs at 15:55:01.5 ET
  showed v7 355pm_script.py = 7,652.84 vs v8 355pm_script_v8.py = 7,655.83 -- ~$3 apart.
  A quieter 15:58 snapshot showed -$0.52 (v8 lower), so the gap widens when the market moves.
  Consequence: the v7 and v8 books can pick DIFFERENT STRIKES for the same strategy at 3:55.
- ATM vol differs too (0.0845 v7 vs 0.0819 v8 for tomorrow's expiry on the same day, via
  getVols/msglivesurfaceatm) -- likely the same root cause. Shifts 4pm_script_v3's implied_move.

Tables: v7 SPX/quotes = sranalytics.msgoptionimpliedquote; v8 = sranalytics.msgliveimpliedquoteadj.

Comparison scripts (run in Git Bash):
- SPX side-by-side (barrier-synced simultaneous pulls, built in this chat 8/24):
  `python /d/PycharmProjects/scratch/daily_scripts/compare_spx_v7_v8.py`
- ATM vol side-by-side (built by another chat):
  `python /d/agent_projects/adhoc/v8_atm_vol_compare.py`
