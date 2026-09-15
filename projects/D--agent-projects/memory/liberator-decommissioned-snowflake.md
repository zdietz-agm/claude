---
name: liberator-decommissioned-snowflake
description: SpiderRock Liberator API is dead (9/2026); helpers_improved now pulls via snowflake_helpers; known V8 0DTE atmVol divergence vs stored Liberator data
metadata: 
  node_type: memory
  type: project
  originSessionId: b6e869fd-f3fe-4a23-ad79-4465e854791f
  modified: 2026-09-08T15:58:12.243Z
---

SpiderRock decommissioned the Liberator API in Sept 2026 (NotEntitled errors). On 2026-09-08
`D:/PycharmProjects/spdr_liberator/helpers_improved.py` dropped `import liberator`;
`get_options_data_from_liberator()` was RENAMED to `get_options_data_from_snowflake()`
(thin wrapper on `snowflake_helpers.pull_from_snowflake`). `get_options_data()` keeps the
`pull_from_liberator` kwarg name for caller compatibility. sachin_portfolio.py and the two
pre_earnings_options_volume_analysis*.py scripts are left broken with a comment.

**Why:** Zach wanted the bandaid ripped off (no alias) so future editors do not reintroduce liberator.

**How to apply:**
- Never suggest liberator for SpiderRock options history; use snowflake_helpers (HIST_DATA_PROD.V8_US).
- Parity (MRVL 2026-06-05): rows identical in shared windows, NBBO/srPrc/greeks match, atmVol within
  ~0.5 vol pt for all expiries EXCEPT 0DTE (V8 3.08 vs Liberator 4.69 at 15:30). Announcement-day
  ranking sorts on 0DTE atmVol, so v7-stored vs v8-pulled cycles are not directly comparable.
- Snowflake snap labels run ~40s earlier than Liberator's (15:30:01 vs 15:30:43) and keep an extra
  10:33-14:55 window. Related: [[v7-v8-spx-price-divergence]].
- CloudQuant ICE equity ticks (fed_day_chart.py, eff_day_chart.py, cq_helpers) still use the liberator
  client pointed at api.cloudquant.ai -- separate vendor, status unknown.
- bloomberg_helpers.my_bdh spawns a child process: run `#%%` scripts standalone via
  `python -c "exec(open(f).read())"`, not `python f.py`, or the spawn re-executes the module.
