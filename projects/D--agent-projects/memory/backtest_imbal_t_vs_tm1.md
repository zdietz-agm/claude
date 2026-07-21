---
name: backtest-imbal-t-vs-tm1
description: "BTIC backtest gate should use imbal(t), not imbal(t-1). Empirically verified."
metadata: 
  node_type: memory
  type: project
  originSessionId: eaa668df-221d-4f03-9f05-a1beadedd311
---

For the BTIC options backtest signal gate (`_make_imbal_cont_100_gate` in
`D:/agent_projects/btic_eod_backtest/signals.py`), imbal source is
`t_report_consolidated_imbalances.spy_net_imbalance`. The original code used
`imbal(t-1)` under the assumption that prod's live poll had ~1s latency, so
t-1 in the backtest DB would compensate.

**7/15/26 empirical test disproved this.** Ran 40 samples across 8 prod-log
days, comparing prod's live-polled Imbal value (from log lines
`Imbal=+/-NNNM cap=HH:MM:SS`) against the backtest DB at both the exact
`cap_time` (bt(t)) and one second earlier (bt(t-1)):

- **mean abs error |prod - bt(t)| = $6.6M**  vs  |prod - bt(t-1)| = $34.4M
- **median abs error bt(t) = $0.5M**  vs  bt(t-1) = $5.6M
- Per-sample: bt(t) wins on 28/40 samples (70%), bt(t-1) wins on 12/40

Why: prod's `poll_latest_imbal` returns a snapshot with a `cap_time` timestamp
that already reflects the moment the DB feed captured it -- there's no
additional latency to compensate for. Prod's cap_time and the backtest DB's
snap_time line up sub-$1M on median.

**Why:** the t-1 offset was a well-intentioned latency hack that empirically
introduces MORE error than removing it. On days where imbal has a 1-second
spike (e.g. 7/8/26 imbal briefly hit +70M at 15:57:59 then bounced back
above 100M), the t-1 lookup shifts that value out of the poll's view and
the backtest misses the fire that prod caught.

**How to apply:** if editing the gate, use `t_sec` directly (drop the `-1`).
Same in `derive_triggers`' asof lookups. Ad-hoc test script that verified
this lives at `.../scratchpad/imbal_offset_test.py`; adapt or rerun for
future verification.

Related work: prod switched from latched-breach to simultaneous-breach on
7/15/26; the imbal-timing question is orthogonal to that and applies to
both modes.
