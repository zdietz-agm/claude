---
name: reconcile-size-diff-losscap-first
description: "When reconciling backtest vs prod size differences, check the LossCap pro-rata line before blaming config max_size or v8 splits"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9b123413-a3a0-4b05-9a8f-ba4474cb0b9e
  modified: 2026-08-19T16:46:15.830Z
---

When a reconciliation shows prod trading a smaller size than the backtest, read the
`[LossCap]` line in the prod script log BEFORE attributing the difference to config
`max_size` or to a v7/v8 parallel-run split.

Prod applies sizing in stages, and the log prints each one:
1. Config cap -- "sized down to N due to config max size" (e.g. 355 CLOSER: parent
   `scaled_355(120)` = 1056 x RATIO_TO_PARENT 0.7 = 739).
2. CLOSER Resize -- parent's size decremented by the CLOSER's size.
3. **LossCap pro-rata** -- if summed demand exceeds script_cap or global_cap, ALL trades
   on that side are scaled proportionally. This is usually the binding constraint and the
   number that actually gets sent.

Example that burned me (8/18/2026 355PM): I reported CLOSER as 739 backtest vs "557 v7 +
55 v8 split". Wrong. The log showed
`[LossCap] side=C script_avail=$440,000 demand=$584,515 > $440,000; PRO-RATA:
trade[0]: 352 -> 265, trade[1]: 317 -> 238, trade[2]: 739 -> 557`
-- the loss cap took 739 -> 557. The v8 lots were a separate parallel run on top, not a
split of the 739.

**Why it matters:** the backtest does not model the script/global loss caps at all, so
"prod smaller than backtest" on a multi-trade day is very often a LossCap explanation --
a portfolio-level constraint, not a strategy or attribution difference. Grep the log for
`LossCap` on every size-mismatch row. Related: [[w2-nbbo-anchor-todo]].
