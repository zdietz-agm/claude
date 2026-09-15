# Claude Code Only

Mechanics specific to Claude Code (tool names, caps, paths). The shared rules are in
`C:/Users/zdietz/.codex/AGENTS.md`, imported by `~/.claude/CLAUDE.md`.

---

## Worktree path
- Claude Code worktrees live under `D:\agent_projects\.claude\worktrees\...`. Per the shared "Worktree Path Gotcha" rule, edit the path the user is actually executing from, not the worktree copy.

---

## Skills
- Skills are invoked with the `Skill` tool or by slash name (e.g. `/assistant`). "Use the `<name>` skill" in the shared rules means call the `Skill` tool with that name.

---

## Inline Charts vs Interactive Widgets

When user asks for a line chart (i.e. cumulative pnl vs time or some other factor) in the desktop app, prefer an interactive widget over a static png. To correctly render the image without hallucination: **NEVER** hand-type data arrays into widget code. Instead: generate the data with Python, dump to a file via `json.dumps`, template-substitute into a widget HTML file via `str.replace`, then pass the file content to `show_widget`. The widget's data literal must be byte-identical to Python's `json.dumps` output. For cumulative PNL charts, forward-fill in Python before passing to the widget so lines stay flat between trade dates. Chart.js `spanGaps: true` is NOT equivalent to ffill (it interpolates diagonally across nulls).

Widget size: canvas height 300-360px, one visible chart per widget. Stat cards below for totals/Sharpe/win rate/drawdown (max 1 day)/trade count.

## Inline chart rendering cap (MCP token limit)

Inline charts are returned through the Jupyter MCP tool as a base64 PNG. Claude Code truncates any MCP tool response over `MAX_MCP_OUTPUT_TOKENS` (default 25,000), so an oversized chart is silently dropped -- I still receive the image and may report "rendered above," but user sees nothing. A default `figsize=(13,6)` at `dpi=100` encodes to ~24,600 tokens, right at the cap, so it renders only intermittently. The shared `figsize <= (11, 5)`, `dpi <= 80` defaults exist for this reason.

When unsure, measure before `plt.show()` and keep the estimate under 22,000 tokens for margin:
```python
import io, base64
b = io.BytesIO(); fig.savefig(b, format='png', dpi=D, facecolor='#f5f5f5')
est_tokens = len(base64.b64encode(b.getvalue())) / 3.5   # keep < 22000
```

---

## Shared Jupyter: Claude Code tool names

- The Jupyter MCP tools are `mcp__jupyter__*` (`use_notebook`, `execute_code`, `list_kernels`, `list_files`, `unuse_notebook`, ...).
- **NEVER pass `kernel_id` to `mcp__jupyter__execute_code`** to target the user's kernel -- it silently routes to the wrong kernel. Bind with `mcp__jupyter__use_notebook` (mode="connect") per the `shared-jupyter` skill, then call `execute_code` with NO `kernel_id`.
- **If the `mcp__jupyter__*` tools disappear mid-chat** ("MCP server disconnected"): the `uvx jupyter-mcp-server` bridge child process died, NOT the `:9500` server or kernel. Continue in the SAME kernel via the WebSocket fallback (`D:/agent_projects/shared_jupyter/kernel_exec.py`). Don't ask the user to restart MCP mid-session (no reliable control exists; it respawns next session).
- The server token for the fallback is in `~/.claude.json` under `mcpServers.jupyter.env` -- read it, never print it.

## MCP execute timeout

`mcp__jupyter__execute_code` has a hard 60-second cap. This is the concrete value behind the shared "Tool Timeouts vs Slow Kernel Work" rule: anything that may exceed 60s is handed to the user to run in their kernel.

---

## Assistant skill: session evidence tools

When running the `assistant` skill, harvest evidence from other sessions with the session-management MCP tools: `mcp__ccd_session_mgmt__list_sessions` (limit ~15) and `mcp__ccd_session_mgmt__list_events` (limit 10-20) for every session with `lastActivityAt` after the last sync. If these tools are unavailable (headless run), fall back to `git log --since` + newest scheduled_tasks/logs/ files and CLEARLY say so in the reply and brief.
