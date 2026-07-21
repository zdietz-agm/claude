# Shared Jupyter Workflow -- Details

CLAUDE.md keeps the core handoff flow (Cursor spawns, Claude attaches, MANDATORY post-attach verify, tag the kernel). This file holds everything else: troubleshooting, server management, executing-code variants, safety details, kernel-restart handling.

## Executing code (which MCP call)

- `mcp__jupyter__execute_code` -- runs in the kernel without writing to any notebook file. Default choice for most work.
- `mcp__jupyter__execute_cell` / `insert_execute_code_cell` / `read_notebook` -- only work when `jupyter-collaboration` is installed on the server. Use only when the user wants cells persisted to the `.ipynb`.

## When to use the shared kernel vs ad-hoc Bash python

Use the shared kernel when:
- The task involves iterating on data that's expensive to load (Bloomberg, SQL, OPRA panels, SpiderRock queries).
- The user will want to inspect intermediate variables themselves from their `.py` scratchpad.
- Work will span many steps / more than a few minutes.

Stick with one-off `python` Bash calls for quick sanity checks with no reusable state.

## Safety rules (kernel-shared RAM)

All kernels on `:9500` share physical RAM. A runaway allocation in one chat can degrade every other chat.

- **Before allocating anything large** (>500MB estimated), call `check_ram(int(<bytes>))` first. It refuses if the allocation would exceed 50% of free RAM.
- **Never `display(df)` or print a huge DataFrame** without first truncating or sampling (`df.head(100)`, `df.sample(1000)`). Avoid undoing `display.max_rows=100`.
- **`del` large intermediates when done** so RAM frees up for other chats.
- If the user explicitly asks for a giant allocation, quote the rough memory footprint first, then proceed.
- **If the user asks "what's eating memory?" or the machine feels heavy**, call `ram_snapshot()` via `execute_code`. Shows RSS per kernel joined with `tag_kernel` names. If stale kernels are the problem, point them at `python D:/agent_projects/shared_jupyter/cleanup_kernels.py --min-idle 30`.
- **If the user edits `jupyter_helpers.py` or `calendar_utils.py` mid-chat**, the running kernel holds stale bytecode. Run `reload_helpers()` then `from jupyter_helpers import *; from calendar_utils import *` to pick up the changes -- no kernel restart needed.

## One kernel per chat

Each chat owns one kernel UUID. Don't switch kernels mid-chat without the user's say-so. If unsure which kernel belongs to this chat, ask for a fresh ID rather than guessing from `list_kernels`.

## Kernel restarts

If the kernel is restarted (by either side), its UUID is gone. The user must spawn a new kernel in Cursor (same flow as the core handoff in CLAUDE.md) and share the new ID. Flag this whenever you restart.

## Manual fallback if the IPython startup file fails to load

If `NameError` on `get_kernel` / `check_ram` after attach, the startup file (`C:\Users\zdietz\.ipython\profile_default\startup\00-shared-jupyter.py`) failed. Look at the kernel's stderr for `[startup 00-shared-jupyter] ... FAILED: [...]` -- that tells you which module broke (usually a bug in `jupyter_helpers.py` or `calendar_utils.py`). Fall back to manual seeding:

```python
import sys
if 'D:/PycharmProjects/utils/' not in sys.path:
    sys.path.insert(0, 'D:/PycharmProjects/utils/')
from jupyter_helpers import *
import pandas as pd
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 50)
```

Then tell the user the startup file is broken so they can fix the underlying module.

## Troubleshooting (Cursor-side issues)

- **"Create Interactive Window" missing from the command palette** -> MS Jupyter extension isn't installed. Direct the user: Ctrl+Shift+X -> search `@id:ms-toolsai.jupyter` -> Install -> `Developer: Reload Window`. Also install `ms-python.python`, `ms-toolsai.jupyter-keymap`, `ms-toolsai.jupyter-renderers`.
- **`# %%` CodeLens buttons ("Run Cell | Run Below | Debug Cell") not rendering** -> same fix (install MS Jupyter extension, reload). `Shift+Enter` with cursor in the cell still runs it as a workaround.
- **MCP cell-level tools return 404 at `/api/collaboration/session/...`** -> `jupyter-collaboration` missing on the server. Tell the user to `Ctrl+C` the `setup_shared_jupyter.py` terminal, `pip install jupyter-collaboration`, restart.

## Server management

- Server runs from `python D:/agent_projects/shared_jupyter/setup_shared_jupyter.py` (user keeps a terminal open).
- Token lives in `D:/agent_projects/shared_jupyter/.jupyter_token`.
- If the MCP can't connect, the server isn't running -- tell the user to restart the setup script. Don't try to start it yourself (it's blocking and needs its own terminal).
