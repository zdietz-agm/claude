---
name: spiderrock-v8-migration
description: "SpiderRock v7->v8 migration for the 3 EOD algos: v8 conn, table renames, empirical breakage, and the two grant-gap blockers (on hold pending SR grants)"
metadata:
  node_type: memory
  type: project
  originSessionId: 68c48a6e-de71-4a6c-8928-0ceb9992aa81
  modified: 2026-07-27T18:17:21.167Z
---

SpiderRock is sunsetting v7; migrating 3 EOD algos (`340PM_script.py`, `350PM_script_fast.py`, `350PM_stock_script_fast.py` in `D:/PycharmProjects/scratch/algos/`) to v8. Going **script by script, one at a time, user tests each** before moving on.

**STATUS (2026-07-27): 340PM_script IMPLEMENTED + validated against v8 (awaiting user's live IS_TEST send). 350PM_script_fast + 350PM_stock_script_fast NOT yet done.**

**v8 connection** (confirmed working): host/port `192.81.231.66:3700`, SAME creds as v7 (`agm.zdietz` / `sranalytics`). v7 was `198.102.4.63:3307`.

**srlive access GRANTED (2026-07-27):** the stock-print blocker is resolved but the table/schema differs from the old note -- v8 stock prices live in **`srlive.msgstockprint`** (a per-print STREAM, many rows/ticker), NOT `sranalytics.msgstockprintset` (which stays denied/absent). Columns remap: v7 `bidPrice/askPrice/bidSize/askSize` -> v8 `ebid/eask/ebsz/easz`; `ticker_tk/prtSize/prtPrice/TIMESTAMP` unchanged. Must dedupe to latest-per-ticker (stream, not a set). Connect to `database='srlive'`.

**Table changes (empirically confirmed on v8):**
- `sranalytics.msgoptionimpliedquote` / `msgoptionimpliedquoteadj` -> DENIED (tables present, ungranted). Switch to granted `sranalytics.msgliveimpliedquoteadj` -- columns identical (`uprc`,`sprc`,`obid`,`oask`,`satm` all present; no `uPrc`/`atmVol`). Used by `spdr_rock_order_functions` get_closest_*_sql x6 + refresh_legs + batched_refresh_legs_deduped. NOT a blocker (granted replacement exists).
- Option order path `srtrade.msgparentordergatewayext` / `msgsrmlegbrkrstate` / `msgsrparentcancel` -> all OK on v8. So 340PM + 350PM_fast (options) are fully migratable.
- Unchanged + OK on v8: `msglivesurfaceatm`, `msgoptionprintset`, `msgstockearningscalendar`.

**Remaining blocker (STOCK script only, `350PM_stock_script_fast.py`):**
- `srtrade.msgsrstkbrkrstate` -- stock fills/status (queried in `spdr_rock_stock_order_functions.py`). DENIED on v8. **SR (2026-07-23): "The individual brkrState tables have been rolled into msgSrParentBrkrState."** -> when migrating the stock script, switch stock fill/status reads from `srtrade.msgsrstkbrkrstate` to `srtrade.msgsrparentbrkrstate` (accessible on v8). Stock SUBMIT `srtrade.msgStkOrderGateway` already works. (SPY-price blocker now resolved via srlive grant above.)

**IMPLEMENTED design (as of 340, 2026-07-27):** all v8 logic in the libraries; each script flips with a `USE_V8` toggle. Per-script change is 2-3 lines but must call `use_v8(True)` BEFORE `from spdr_rock_order_functions import *` (import * copies the get_closest_* SQL string values, so a post-import flip leaves stale v7 SQL bound).
- `spdr_rock_functions.py`: `V8_HOSTNAME/V8_PORT/V7_PORT` + module state `ACTIVE_HOSTNAME/ACTIVE_PORT/USING_V8` + `use_v8_connection(enable)`. `run_query` default `hostname=None` -> resolves to `ACTIVE_HOSTNAME` (kept 7 defaults, fast-script `assert len==7` safe); `_run_query_legacy` uses `ACTIVE_PORT`. `getCashIndex` -> `msgliveimpliedquoteadj` when `USING_V8`. `get_prints` -> `srlive.msgstockprint` v8 branch (aliased cols + latest-per-ticker dedupe, `database='srlive'`); `get_prints`/`getLivePrices` default `hostname=None`. NOTE: pooled path + `ConnPool._open_conn` + `getVols`/`getResVol` still hardcode `port=3307` -- fine for 340 (uses `_run_query_legacy` only) but MUST switch to `ACTIVE_PORT` before migrating the fast scripts (they use the srtrade pool). Also `getVols` runs on v7 at IMPORT time (builds smart_expiries) before use_v8 fires -- fine while v7 lives, breaks once v7 is sunset.
- `spdr_rock_order_functions.py`: `IMPLIED_QUOTE_TABLE` (v7 default) + `_build_quote_sql()` (rebuilds get_closest_* x6) + `use_v8(enable)` that flips the table, rebuilds SQL, and calls `spdr_rock_functions.use_v8_connection(enable)`. `refresh_legs` + `batched_refresh_legs_deduped` reference `IMPLIED_QUOTE_TABLE` at call-time.
- `340PM_script.py`: `USE_V8 = True` then `if USE_V8: from spdr_rock_order_functions import use_v8 as _use_v8; _use_v8(True)` BEFORE the `import *`. 340 uses the LEGACY `send_complex_two_waves` path (not the orchestrator). Validated live: getCashIndex/getLivePrices/getSpyEquivalents + get_closest query all work on v8; recap equivalents pull from srlive.msgstockprint.

**Column diff (v7 `msgoptionimpliedquote` vs v8 `msgliveimpliedquoteadj`):** every column the algos READ (okey_*, uprc, satm, sprc, obid, oask, svol) is identical-named on v8. 3 v7-only cols dropped (`calcType`, `veSlope`, `timestamp_us`) but NONE are referenced in code -> pure table-name swap is safe, no aliasing needed.

**Accounts each script trades into** (Task 2 answer): 340PM -> A.340.SO_C42/A.340.BS_C42/A.340.SS_C42 (test T.AGM/T.AGM1/T.AGM2); 350PM_script_fast -> EOD26_C42/EOD27_C42 (test both T.AGM); 350PM_stock_script_fast -> EOD13_C42 (test T.AGM).

See [[spiderrock-enum-and-cancel-terminal]] for the SpdrOrderStatus/brkrState field context.
