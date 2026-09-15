---
name: shared-agent-config-codex
description: "Claude Code + Codex share one rules/skills setup (set up 2026-09-15): ~/.codex/AGENTS.md is canonical, CLAUDE.md files are @import wrappers, ~/.agents/skills is a junction to ~/.claude/skills, Claude-only mechanics live in ~/.claude/rules/claude-only.md"
metadata: 
  node_type: memory
  type: project
  originSessionId: f9681ab5-910e-4db9-b171-da861256a2a2
  modified: 2026-09-15T18:38:54.726Z
---

Zach runs Codex (desktop app, CODEX_HOME=C:/Users/zdietz/.codex, codex.exe under
AppData/Local/OpenAI/Codex/bin/<hash>/, NOT on PATH) and Claude Code on the same repos at
different times. Set up 2026-09-15:

- **Rules**: `~/.codex/AGENTS.md` is the ONLY real global rules file. `~/.claude/CLAUDE.md` is a
  one-line `@C:/Users/zdietz/.codex/AGENTS.md` wrapper. Project rules: `assistant/AGENTS.md` and
  `sp500_cand_prediction/AGENTS.md` are real; their `CLAUDE.md` is `@AGENTS.md`. No symlinks.
- **Claude-only mechanics** (mcp__jupyter__ names, 60s MCP cap, show_widget rules, .claude/worktrees
  path, ccd_session_mgmt tools for the assistant skill) live in `~/.claude/rules/claude-only.md`.
- **Skills**: `C:/Users/zdietz/.agents/skills` is a directory junction to `~/.claude/skills`; Codex
  0.154 scans both `.agents/skills` and `.codex/skills`, and `~/.codex/skills/.system` holds its
  bundled skills (leave alone). shared-jupyter and assistant skills were rewritten tool-neutral.
- **Codex config.toml**: sandbox_mode workspace-write, writable_roots = Downloads only
  (D:/PycharmProjects deliberately excluded so edits prompt), network_access on, D:/agent_projects
  trusted, project_doc_max_bytes 65536, `[mcp_servers.jupyter]` mirrors ~/.claude.json.
- **Not shared**: Claude scheduled tasks, settings.local.json allowlist, auto-memory (Codex reads
  memory only when Zach asks "read my Claude memories"; never writes there).
- Backups of the pre-port files: `~/.claude/backups/pre_codex_20260915_1433/`.
- D:/vbam-data-oracle was intentionally left out (own CLAUDE.md, untouched).

**Why:** one edit point, zero drift between tools; Zach did not want the word "Claude" in shared
rules confusing Codex.

**How to apply:** when asked to change a global rule, edit `~/.codex/AGENTS.md` (never the CLAUDE.md
wrapper). Tool-specific text goes in claude-only.md. Verify Codex loading with
`codex.exe debug prompt-input` from the project dir (`--print-instructions` / `--list-skills` do
not exist in this build). Keep shared files free of "Claude"/"Codex" as an addressee; say "the agent".
