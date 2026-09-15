---
name: jpm-quarterly-collar-research
description: "JPM quarterly collar (JHEQX-style) research -- partially lost in D-drive migration, recovered files in Dropbox, strike-inference analysis to redo before Sept 2026 quarterly month-end"
metadata: 
  node_type: memory
  type: project
  originSessionId: 2a0a0dff-6cfc-4b92-bc90-d5820b614e59
  modified: 2026-08-03T18:51:24.850Z
---

User has prior research on the JPM quarterly collar (JHEQX-style: 3 SPXW legs rolled at quarter-end -- long put, short put, short call) and its relation to month-end SPY performance. Much of it was lost in the old-machine -> new-machine D-drive transfer (~Aug 2026). No project directory for this exists in D:/agent_projects yet.

- **Recovered files**: `C:/Users/zdietz/White Bay Dropbox/Zach Dietz/Transferred from old C Drive/collar_recovery_files`
- **Analysis to redo** (planned ~late Aug / early Sept 2026, before the Sept 2026 quarterly month-end): infer each quarter's collar strikes from volume data in `t_historical_options_snaps` -- the roll prints in huge size on exactly 3 SPXW strikes on the quarter-end roll date, so volume outliers identify the legs. Verify the table actually carries a volume/OI column first.
- Downstream goal: use the recorded collar strikes to backtest month-end SPY performance.
