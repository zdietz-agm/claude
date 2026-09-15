---
name: bbcomm-session0-16s-lag
description: Root cause + repro of the 16s first-Bloomberg-call lag in prod algos (blpapi Session.start stalls when bbcomm was spawned by a Session-0 scheduled task); test script and warm-up fix pattern
metadata: 
  node_type: memory
  type: project
  originSessionId: 65147abd-b96a-4502-94e6-f48b91a9c92c
  modified: 2026-09-14T19:33:14.759Z
---

**Finding (2026-09-14):** every fresh process's FIRST xbbg call pays ~16.3s inside `blpapi.Session.start()` (blpapi trace: 16s gap between "blpapidapisup dll loaded" and "bbcomm started"; TCP connect itself is instant, `openService` 11ms, bdp ~180ms). Hit save_spy_prices.py at 15:49:58 on 9/11 (16464ms), plus 340PM_script get_market_measurements (16.5s) and 350pm_stock_script get_change_in_realized (blew the 15:50:03 gate) the same day.

**Cause (PROVEN 9/14/26: killed the Session-0 bbcomm via elevated Stop-Process -- plain taskkill is Access Denied -- and a fresh process's Session.start dropped 16.3s -> 12ms; new bbcomm spawned in Session 1):** the bbcomm.exe owning 127.0.0.1:8194 was running in Windows **Session 0** -- spawned at 07:16:03 by the `UpdateDataEOD` scheduled task (logon type Password = non-interactive) when no interactive bbcomm existed (after the 9/10 20:00 Bloomberg Updater run, and after the 9/11 17:28 reboot). Session-1 blpapi clients then stall ~16s trying to launch/handshake their own bbcomm before falling back to the existing listener. Days with a live Session-1 bbcomm at 07:16 (9/3-9/10) showed ~200ms first calls.

**Repro / test script:** `D:/agent_projects/adhoc/spy_price_first_call_lag_test.py` (run on scratch/.venv python; imports getSPY/SCHEDULE from prod module, writes only to %TEMP%). Flags: `--split` (session/service/bdp breakdown), `--runs N`, `--idle S`, `--warm` (fix). Diag: scratchpad blp_session_start_diag.py (blpapi.Logger TRACE callback).

**Fix (DEPLOYED 9/14/26):** `helpers.warm_up_bloomberg_connection()` in scratch/algos/helpers.py (opens session + refdata service + dummy SPY bdp, never raises, prints in pretty_time log style, hints at Session-0 bbcomm if >5s). Called ~30-50s BEFORE each script's first real Bloomberg call, after a `wait_until(..., poll_interval=1)`, staggered 3s apart so bbcomm never sees simultaneous session starts (15:39:15 355pm, :18 355pm_v8, :21 340PM, :24 350PM, :27 350PM_fast, :30 350pm_v8; 15:47:16 350pm_ss; 15:49:05 350pm_stock, :08 save_spy_prices, :11 355pm_stock; btic + 4pm_v3 warm at startup right before their startup calls). Zach explicitly did NOT want the warm-up at script launch. Covers all 12 Bloomberg-using run_algos.sh scripts (340PM, 350PM, 350PM_fast, 350pm_v8, 350pm_ss, 350pm_stock, 355pm, 355pm_v8, 355pm_stock, 4pm_v3, btic_and_imbal, save_spy_prices; 350PM_stock_script_fast has no Bloomberg). Session survives >=9 min idle; scheduled bdp then ~180ms. Look for "Bloomberg connection warm in Nms" near the top of each prod log. Check: `Get-Process bbcomm | select Id,SessionId` -- SessionId 0 = problem state (interactive should be 1).

**How to apply:** if a prod log shows a one-off ~16s Bloomberg call, check bbcomm's SessionId first; warm the session at launch in any timing-critical script rather than at the fire time. See [[algos-venv-migration]].
