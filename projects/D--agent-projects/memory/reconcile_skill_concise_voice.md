---
name: reconcile-skill-concise-voice
description: "Verbatim example explanations (user-approved voice) for the future reconcile-backtests skill; state values each side saw, then the rule, no arrow-chains"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b1d80b02-df68-4ce9-bb7d-d4c47c037528
  modified: 2026-07-22T19:19:25.801Z
---

User wants backtest-vs-prod discrepancy explanations in a concise voice: state the values each side saw, then the trigger rule and outcome, in plain sentences. No arrow chains, no bold jargon labels, no source-table names unless essential.

**Why:** Verbose cause-chains with arrows/tables names are hard to scan; the reader only needs what each side saw and which rule flipped.

**How to apply:** When writing the reconcile-backtests skill, include these two examples VERBATIM as the required style:

Example 1 (signal-source divergence):
"Prod live 350 imbal = -3.35B and 340 imbal = +0.87B while backtest sees 350 imbal = -0.86B and no 340 imbal is visible to backtest. Grows requires 350<-2B, |340|<=1B and shrink requires 340>800M, 350<200M, so neither fire in backtest."

Example 2 (min_price knife-edge):
"Backtest sees credit price of .30 which does not qualify it for bumped strategy (parent would fire)."

Context: from the 2026-07-22 bumped_spread_backtest vs PNL LOG NEW reconciliation chat.
