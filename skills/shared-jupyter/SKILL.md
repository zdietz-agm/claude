---
name: shared-jupyter
description: Attach to the user's live shared Jupyter kernel on localhost:9500 and run code there so variables appear in their VS Code Interactive Window. Use whenever the user pastes a kernel UUID or says "connect to kernel", "attach to", or "use kernel", and for shared-kernel RAM, stale-helper reload, or kernel troubleshooting issues.
---

# Shared Jupyter Workflow (VS Code + Claude Code)

A persistent JupyterLab server runs on `localhost:9500` so VS Code's Interactive Window and Claude Code can share a live Python kernel within a chat. **VS Code spawns the kernel, Claude attaches via `kernel_id`** -- never the other way around (VS Code's picker can't see Claude-spawned kernels).

**If the server isn't up on `localhost:9500`** (attach/list calls error with connection refused, or `mcp__jupyter__list_kernels` returns nothing), do NOT try to start it yourself or spin up a different server. Tell the user the `:9500` JupyterLab server isn't running and ask them to start it, then wait. Everything below assumes that server is live.

## Trigger phrases (attach-to-kernel intent)

Treat ANY of these as a request to attach to the user's live kernel and run subsequent code there:

- "connect to kernel with UUID '<uuid>'", "connect to kernel '<uuid>'", "connect to '<uuid>'", "connect to notebook '<uuid>'", "attach to '<uuid>'", "use kernel '<uuid>'", or any message that pastes a bare kernel UUID and asks to run/create something.

A "UUID" here is the 8-4-4-4-12 hex string (e.g. `7043d46c-341c-45d8-ba2b-2b8c388d6fd9`). When you see one, run the **Attach procedure** below BEFORE writing any variables. Do not answer or run code until the attach is verified.

## CRITICAL: how kernel targeting actually works (read before touching Jupyter)

- **`use_notebook` is the ONLY correct way to bind to the user's kernel.** It is what makes the user's Interactive Window and your `execute_code` calls share one live kernel.
- **NEVER attach to a kernel, or create/assign variables the user needs to see, by passing `kernel_id` to `mcp__jupyter__execute_code`.** That argument does NOT reliably target the kernel you name -- when the kernel isn't the currently-activated notebook, the call silently routes to a different default kernel. Code "succeeds" (prints the right answer) but lands in the wrong process, and the user's variable comes back `NameError`. This is a silent footgun; it has burned us. Bare-`kernel_id` `execute_code` is ONLY acceptable for throwaway inspection of a kernel you have already separately confirmed -- never for the user's working state.
- After a successful `use_notebook`, call `execute_code` with **no `kernel_id`** -- it targets the bound kernel, which is the user's kernel.

## Attach procedure (run on every trigger)

1. **Ensure the notebook file exists.** `use_notebook` needs a real `.ipynb` on the server. If unsure it exists, create it first (Bash): `python D:/agent_projects/shared_jupyter/new_notebook.py <name>` (e.g. `<name>` = `shared`). The server root maps to the notebooks dir, so `notebook_path` is just the bare filename `<name>.ipynb` (NOT `shared_jupyter/notebooks/<name>.ipynb`). If a path errors with "not found", `mcp__jupyter__list_files` with pattern `*.ipynb` to see the real relative paths.
2. **Bind:** `mcp__jupyter__use_notebook` with `mode="connect"`, `notebook_path="<name>.ipynb"`, `kernel_id="<the UUID>"`.
3. **MANDATORY post-attach verify** (skipping this can silently corrupt cross-chat state or write to the wrong kernel):
   ```python
   import os
   kid = get_kernel()
   assert kid == "<UUID the user pasted>", f"WRONG KERNEL: attached to {kid}, user asked for <UUID>"
   print("kernel:", kid, "| pid:", os.getpid(), "| check_ram:", callable(check_ram))
   ```
   Only proceed past a passing assert. If it fires: stop, `unuse_notebook`, re-`use_notebook` with the correct ID, re-verify.
4. **Tag the kernel** for `ram_snapshot()` / cleanup visibility:
   ```python
   tag_kernel("<short topical name e.g. vol_surface_explore>")
   ```
5. **Now run the user's request** via `execute_code` with NO `kernel_id`. Confirm back to the user which kernel/pid you're on so they know it's the same one as their Interactive Window.

## Critical RAM rules

All kernels on `:9500` share physical RAM. Before allocating >500MB, call `check_ram(int(<bytes>))` -- it refuses if the allocation would exceed 50% of free RAM. Never `display(df)` on huge DataFrames without sampling (`df.head(100)`, `df.sample(1000)`). `del` large intermediates when done. If the user asks "what's eating memory?", call `ram_snapshot()` via `execute_code`; for stale kernels point them at `python D:/agent_projects/shared_jupyter/cleanup_kernels.py --min-idle 30`.

## One kernel per chat / restarts

Each chat owns one kernel UUID. Don't switch kernels mid-chat without the user's say-so; if unsure which kernel belongs to this chat, ask for a fresh ID rather than guessing from `list_kernels`. If the kernel is restarted (by either side), its UUID is gone -- the user must spawn a new kernel in VS Code and share the new ID. Flag this whenever you restart.

## When to use

Use the shared kernel for expensive-to-load data + multi-step work (Bloomberg, SQL, OPRA panels, SpiderRock queries; user will inspect intermediate variables). Use one-off Bash `python` calls for quick sanity checks with no reusable state.

## Stale helpers mid-chat

If the user edits `jupyter_helpers.py` or `calendar_utils.py` mid-chat, the running kernel holds stale bytecode. Run `reload_helpers()` then `from jupyter_helpers import *; from calendar_utils import *` -- no kernel restart needed.

## More

Executing-code MCP variants, manual fallback when the IPython startup file fails, VS Code extension troubleshooting, and server management: [references/troubleshooting.md](references/troubleshooting.md). Architecture rationale: `D:/agent_projects/shared_jupyter/README.md`.
