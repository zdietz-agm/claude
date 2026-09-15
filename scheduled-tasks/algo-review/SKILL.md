---
name: algo-review
description: Weekdays 8:25 AM: review the prior trade date's EOD algos, write the review file, send to Google Chat
---

You are reviewing yesterday's end-of-day algo trading (option AND stock scripts) for Zach. This is a trading review that can drive a real sizing or config change, so a wrong conclusion is worse than no conclusion. Work only from verified evidence.

STEP 0 -- TRADE-DATE GATE (do this first)
Run on the global python:
  python -c "import sys; sys.path.insert(1,'D:/PycharmProjects/utils'); import calendar_utils as c, datetime as dt; t=dt.date.today(); w=c._trading_range(t-dt.timedelta(days=10), t); print('TODAY_IS_TRADING_DAY', t in w); print('REVIEW_DATE', max(x for x in w if x < t))"
If TODAY_IS_TRADING_DAY is False, STOP immediately: no pack, no review file, no Google Chat. Your final message is just "Not a trading day -- skipped." If the import itself fails, continue but state prominently that the gate could not be checked.
REVIEW_DATE printed above is the trade date you are reviewing. Everything below refers to it.

STEP 1 -- BUILD THE REVIEW PACK
  cd D:/agent_projects/algo_daily_review
  python build_review_pack.py <REVIEW_DATE>
This takes ~20s and writes packs/<YYYY_MM_DD>/digest.txt plus one <script>_clean.txt per prod log. It computes everything; it interprets nothing.

STEP 2 -- INPUT FRESHNESS (self-heal, then escalate)
Read the INPUT FRESHNESS section of digest.txt. If every input is OK, go to Step 3.
If any backtest workbook is STALE or MISSING, T+1 backtest generation failed. Try to fix it:
  python build_review_pack.py <REVIEW_DATE> --regen
You are authorized to run this even though it can take a while (each extra-layer backtest ~2.5 min; if update_data must re-run, up to ~50 min). It probes connections first and will not thrash against a down one.
  - If regen succeeds, continue with the rebuilt numbers and note in the review that the workbook had to be rebuilt and why.
  - If regen reports REGEN BLOCKED, do NOT keep retrying. The blocked connection is Zach's to fix. Still write the full review for everything else, but make the FIRST line of both the review file and the Google Chat message the blocked-input warning naming the exact connection and the commands from the digest's REGEN ATTEMPT section. Also read the relevant D:/agent_projects/scheduled_tasks/logs/<today>_*_run_backtests_*.txt and quote the actual failure line, since it usually names the cause outright.
The most common cause: the SpiderRock VPN is down, which kills every backtest generator at import time (create_backtests.py -> scratch/algos/helpers.py -> spdr_rock_functions -> getVols) even when the morning update_data ran green. Second most common: the Bloomberg terminal is not logged in.
Also check whether PNL LOG NEW.xlsx had rows for the review date. If it did not, say so plainly on line 1 rather than estimating prod PnL.
The freshness list includes the 355 HACKER backtest workbook (hacking_355_backtest_cap*_last5_*.xlsx, written 8:19 by CreateBacktestsHacker via scheduled_tasks/run_backtest_hacker.py at prod's HACK_MAX_PRICE, --all-parents, --last-days 5). --regen covers it like the others. If it is STALE and regen is blocked, the hacker check in Step 4 question 7 is unavailable -- say so in the 355 blocks only if prod has HACK_ rows that day.

STEP 3 -- READ
In this order: (a) D:/agent_projects/algo_daily_review/REVIEW_GUIDE.txt, (b) D:/agent_projects/algo_daily_review/review_corrections.txt -- Zach's corrections, which override the guide and override anything in this prompt, (c) the whole digest.txt, (d) packs/<date>/350pm_script_clean.txt and 355pm_script_clean.txt in full, (e) any other <script>_clean.txt the digest flagged (error lines, an unexplained gap, an order that tried and did not fill, a missing or truncated log). Skim the remaining cleaned logs.
For reference on the two lead scripts' design: D:/agent_projects/eod_option_algos/README.md and D:/agent_projects/eod_355_option_algos/README.md. For the equity stock strategies (EQUITY_ALGO_42 names, backtest source "equity" in the digest): D:/agent_projects/eod_equity_algos/README.md. Read the seed reviews 08_17_2026.txt and 08_18_2026.txt in the output folder to calibrate voice.

STEP 4 -- ANSWER THESE SIX QUESTIONS, per script that traded
1. What wave were we filled on, and was anything underfilled? Name the option and the numbers. Then say what it implies about dynamic edge sizing being too tight or too loose.
2. Does prod reconcile with the backtest, per strategy? Explain every gap with a verified mechanism. Load the reconcile-backtests skill when a discrepancy needs real chasing; its known-divergence checklist covers most daily gaps.
3. Is a strategy running a streak of same-sign days, or did it have an outsized day? A 3+ day run is a size-up (positive) or size-down (negative) candidate -- but read D:/agent_projects/eod_option_algos/prod_change_logs/ first so you never propose reverting a deliberate change.
4. Any unusual slowness pulling SpiderRock, Bloomberg, or VBAM data, or any odd pause? Check the digest's UNEXPLAINED gaps against the cleaned log before reporting one -- most turn out to be designed waits the parser did not recognize, and when that happens say so, because build_review_pack.py should learn the pattern.
5. Did an option's sprc sitting outside its NBBO cost us fills? The digest computes net sprc vs net cross vs net mid per order and flags every leg whose surface price was outside its own NBBO. Prod wave limits are surface-anchored, so a surface far from the book is a real no-fill mechanism, not a curiosity.
6. Anything else unusual? Errors, loss-cap pro-rata, min_price clamps, the V8 size-ratio check, month-end or MOC behavior, a script that did not run, a near-miss that would have fired on a slightly different market.
7. 355 hacker (only when the digest's 355pm_script / 355pm_script_v8 block contains a "355 HACKER -- prod vs hacker backtest" sub-block; otherwise write nothing about hacking). Give that script ONE hacker line: what prod sent and filled at what debit vs the model's exit, plus any "HACKER FLAGS" line. The four flag types are the only discrepancies (trigger mismatch outside the 0.9-1.1B buffer, cap violation, size relation, POSSIBLE WAVE-3 MALFUNCTION -- the last gets "THIS SHOULD BE REVIEWED.", see REVIEW_GUIDE section 8 watch item 3). Fill price/timing, half-of-model vs half-of-filled sizing, v8 ratio sizing and unfilled-parent differences are by design (REVIEW_GUIDE section 7) -- never flag them.
Scripts other than 350pm/355pm get real but brief coverage: slowness, errors, tried-but-unfilled, anything odd. Only genuinely quiet scripts go on the "didn't trade" line.

STEP 5 -- WRITE THE REVIEW
Write D:/PycharmProjects/scratch/algos/automated_algo_reviews/<MM_DD_YYYY>.txt using the REVIEW DATE (e.g. trade date 2026-08-19 -> 08_19_2026.txt). ASCII only, CRLF line endings, overwrite if it exists. Follow REVIEW_GUIDE.txt section 3 for structure and section 4 for voice: line 1 is "PROD PNL <x>k, Backtest PNL <y>k", then one block per script, then the "Didn't trade/does not need human review:" line. Short declarative bullets, numbers inline, no preamble, no markdown, no em-dashes or other non-ASCII, target under ~40 lines.
Omit anything you could not verify -- no speculation and no hedge labels either.

STEP 6 -- SEND TO GOOGLE CHAT
Send the review text to Zach's personal chat:
  python -c "import sys; sys.path.insert(0,'D:/PycharmProjects/utils'); from google_chat_webhook import send_message, my_chat; send_message(open(r'<path to the review file>').read(), url=my_chat)"
Prefix the message with a bold header line: *Algo Review MM/DD/YYYY*. Wrap in try/except -- if the send fails, report that in your final message but do not fail the run.

STEP 7 -- FINAL MESSAGE
End your final message with the full review text so the notification is readable on its own, followed by one line naming the review file path and one line listing any input that was stale, blocked, or unavailable.

Guardrails: do not edit any prod script in D:/PycharmProjects/scratch/algos. Do not run a full backtest, rebuild combined data, or start any multi-minute job other than the Step 2 regen. fill_price_review.py (D:/agent_projects/fill_price_review/) is available for second-by-second fill forensics on a specific unexplained order and needs the SpiderRock VPN -- use it only for a specific unexplained fact, and if the VPN is down say the check was unavailable rather than speculating.