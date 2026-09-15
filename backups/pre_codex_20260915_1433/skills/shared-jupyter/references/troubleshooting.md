# Shared Jupyter -- Troubleshooting and Details

Core flow (attach procedure, mandatory verify, kernel-targeting rules, RAM rules) lives in SKILL.md. This file holds everything else.

## Executing code (which MCP call)

- `mcp__jupyter__execute_code` -- runs in the kernel without writing to any notebook file. Default choice for most work.
- `mcp__jupyter__execute_cell` / `insert_execute_code_cell` / `read_notebook` -- only work when `jupyter-collaboration` is installed on the server. Use only when the user wants cells persisted to the `.ipynb`.

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

## Troubleshooting (VS Code-side issues)

- **"Create Interactive Window" missing from the command palette** -> MS Jupyter extension isn't installed. Direct the user: Ctrl+Shift+X -> search `@id:ms-toolsai.jupyter` -> Install -> `Developer: Reload Window`. Also install `ms-python.python`, `ms-toolsai.jupyter-keymap`, `ms-toolsai.jupyter-renderers`.
- **`# %%` CodeLens buttons ("Run Cell | Run Below | Debug Cell") not rendering** -> same fix (install MS Jupyter extension, reload). `Shift+Enter` with cursor in the cell still runs it as a workaround.
- **MCP cell-level tools return 404 at `/api/collaboration/session/...`** -> `jupyter-collaboration` missing on the server. Tell the user to `Ctrl+C` the `setup_shared_jupyter.py` terminal, `pip install jupyter-collaboration`, restart.

## Server management

- Server runs from `python D:/agent_projects/shared_jupyter/setup_shared_jupyter.py` (user keeps a terminal open).
- Token lives in `D:/agent_projects/shared_jupyter/.jupyter_token`.
- If the MCP can't connect, the server isn't running -- tell the user to restart the setup script. Don't try to start it yourself (it's blocking and needs its own terminal).

## Safety extras

- If the user explicitly asks for a giant allocation, quote the rough memory footprint first, then proceed.
- Avoid undoing `display.max_rows=100`.
