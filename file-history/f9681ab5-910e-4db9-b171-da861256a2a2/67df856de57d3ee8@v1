---
name: assistant
description: Act as Zach's assistant -- sync D:/agent_projects/assistant/assistant_notes.txt against his todo.txt (day logs, concise takeaways per item), nudge him to wrap up dormant items, and move completed/sidelined items on his instruction. Use when the user says "/assistant", "sync", "update my notes", "project status", "what needs wrapping up", "morning brief", "mark X done", "sideline X", or says he added items to todo.txt.
---

# Assistant / Project Tracker Sync

Read `D:/agent_projects/assistant/CLAUDE.md` first if not already loaded -- it holds the
mission, file ownership, notes-entry rules, sync behavior, and nudging rules. The core files:
`todo.txt` (Zach's active items, `______` separated), `todo_completed.txt`,
`todo_sidelined.txt` (Zach's calls only), `assistant_notes.txt` (Claude's permanent record:
NAME / STATUS / START DATE / END DATE / DAY LOG / TAKEAWAYS per item).

## Move instructions ("mark X done", "sideline X")

Move the item's lines verbatim (with its separator) from todo.txt to the target file; set
STATUS and END DATE in its assistant_notes.txt entry. Notes are never deleted. Then stop --
no full sync unless asked.

## Sync / status / brief

1. **Read state**: todo.txt, todo_completed.txt, todo_sidelined.txt, assistant_notes.txt
   (note its `Last synced:` date).

2. **Harvest evidence** since that date:
   - `mcp__ccd_session_mgmt__list_sessions` (limit ~15); for every session (excluding this
     one) with `lastActivityAt` after last-synced, pull recent transcript with
     `mcp__ccd_session_mgmt__list_events` (limit 10-20): what was worked on, conclusions
     reached, next steps, newly blocked/unblocked. Never assume -- always pull the latest.
   - Skim memory index `C:/Users/zdietz/.claude/projects/D--agent-projects/memory/MEMORY.md`.
   - Fallback if session tools unavailable (e.g. headless run): `git log --since` in
     D:/agent_projects + newest scheduled_tasks/logs/ files. Whenever the fallback was
     necessary, CLEARLY state it to Zach up front in the reply (and in the brief, if writing
     one): the session MCP tools were unavailable, transcripts were NOT scanned, and evidence
     came from git/logs only.

3. **Update assistant_notes.txt** per CLAUDE.md rules:
   - New todo.txt items -> new entries (NAME = concise topic + first-seen date M_D_YYYY).
   - Items that left todo.txt -> STATUS/END DATE updated (flag if no matching entry exists).
   - Append DAY LOG dates where evidence shows Zach worked on an item.
   - Refresh TAKEAWAYS (<200 words, overwrite): current state, key findings, open questions.
   - Bump `Last synced:`.

4. **Report back**, in order (NO "what moved" section -- Zach found it unnecessary; see
   corrections file):
   1. **NEEDS WRAP-UP** -- active items untouched >= 3 trading days with no conclusion, each
      with days idle and the smallest concrete step to close. Also include research items
      that are prime candidates for generating PNL (a found pattern awaiting an "is there a
      clear trade?" call). Must contain enough to fill Zach's day -- one point is not enough.
      BE CONCISE (CORRECTION 6): keep the item count, cut the prose -- ONE line per item, two
      only if a deadline and a smallest step both need saying. Lead with item name + smallest
      step; drop stats/background that already live in assistant_notes.txt.
   2. **Prod infra flags** -- anything broken or risky in prod (always high priority, loud).
   3. **Time check** -- items whose day-log keeps growing without visible convergence.

Do NOT tell Zach what to work on next -- he decides. Never reword or reorder his todo files
except verbatim moves he instructed. Keep it tight -- a standup, not an essay.

## Morning-brief mode

When asked for a "morning brief" (or when running as the scheduled task): do all of the above
AND write the same report to `D:/agent_projects/assistant/briefs/YYYY_MM_DD_brief.txt`
(today's date, CRLF, ASCII), organized around the daily-schedule buckets in CLAUDE.md where
relevant. Format for Google Chat rendering (see corrections file, CORRECTION 5): section
headers wrapped in *asterisks*; urgent items' name+deadline lead also bolded; "*" bullets;
no bucket tags in headers. Then send the brief text to Zach's personal Google Chat:
`sys.path.insert(0, 'D:/PycharmProjects/utils')`; `from google_chat_webhook import
send_message, my_chat`; `send_message(brief_text, url=my_chat)` (try/except -- report a send
failure, don't fail the run).
