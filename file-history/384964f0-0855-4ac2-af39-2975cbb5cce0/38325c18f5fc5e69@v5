---
name: large-index-flows-project
description: "large_index_flows project (started 2026-09-10) -- >$7B single-name index flow events, next step ThetaData 0DTE strangle test at 3pm on eff date"
metadata: 
  node_type: memory
  type: project
  originSessionId: 384964f0-0855-4ac2-af39-2975cbb5cce0
  modified: 2026-09-14T21:23:19.659Z
---

Project dir: `D:/agent_projects/large_index_flows/`. Step 1 done 2026-09-10: `build_flow_list.py` -> `large_flow_events.csv`
(18 regular-cycle S&P adds from sp500_helpers.INDIVIDUAL_ADDS + manual AVGO sell 12/19/25 = $16B and AAPL buy 9/20/24 = $30B per Zach; flow proxy = 12% x CUR_MKT_CAP on annc date). Working cut is >= $10B (`passes_10b`, 13 events); $7B keeps all 20.

Progress 2026-09-14: 0DTE quotes for 19 events + 91 baseline Fridays in t_opra_quotes; closest-OTM strangle workbook
(5 entry tabs + baseline/realized-vol richness cols), top-4 + cum-PnL charts, richness tables. Zach's conclusion: N=19
cannot show richness predicts payoff. Half-day bug found (UBER 11/24/23): scrubbed 11.0M stale post-close rows from
t_opra_quotes (scrub_half_days.py, log in project) and added a HALF_DAYS guard to thetadata_helpers.get_option_quotes_v3
+ pull_options_single (Zach approved). Full running notes: D:/agent_projects/large_index_flows/README.md.

**Why:** Zach wants to know if buying 0DTE OTM call + OTM put (~10-20 bps of spot) at ~3pm on the effective date pays off when index flow is huge.

**How to apply:** Step 2 = pull 0DTE options via ThetaData (`thetadata_helpers`, see `data-sources` skill) around 15:00 on each eff date, price the strangle, test payoff into close. Reuse sp500_adds conventions (AST-read of sp500_helpers, my_bdh raw cached). Related: [[hacker-backtest-open-items]].
