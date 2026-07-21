---
name: pycharm-version-2024-2
description: User deliberately runs PyCharm 2024.2.6 (not 2026.x) due to a Jupyter display() rendering bug; may upgrade later
metadata: 
  node_type: memory
  type: project
  originSessionId: 3b26dcf8-62f7-4f14-9d38-5dbc0a0f88a1
  modified: 2026-07-21T14:45:49.038Z
---

As of July 21, 2026 the user runs **PyCharm 2024.2.6** (standalone install, `C:\Program Files\JetBrains\PyCharm 2024.2.6`) on the new PC, deliberately rolled back from 2026.1.3.

**Why:** PyCharm 2026.1.x has a Jupyter output bug: `display()` of a pandas Series/DataFrame inside a `for` loop renders nothing inline (only interleaved `print()` output shows). Root cause found by inspecting the IDE jars: the interactive-tables pipeline (`PythonTableDataTypeDetector` regex-detects pandas reprs in `text/plain` display_data) claims those outputs and fails to build the table for mid-cell displays, with no settings/registry off-switch. The kernel outputs were fine (present in the .ipynb JSON). Bug was NOT reported to YouTrack (user's choice).

**How to apply:**
- Don't suggest updating PyCharm as a fix for issues; 2024.2 is intentional, not stale.
- 2026.1.3 was uninstalled (caches deleted, `AppData\Roaming\JetBrains\PyCharm2026.1` settings folder kept for a possible future reinstall).
- If a future upgrade comes up, first verify the fix: run a cell with `for` loop containing `print(i)` + `display(pd.Series(...))` and confirm the Series renders between the prints.
- User declines in-app update prompts to stay on 2024.2.
