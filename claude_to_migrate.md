# Global Rules

---

## Response Style Defaults
- **Default to 1-sentence responses.** Long answers clutter the chat. I will prompt for depth when I want it.
- **If I ask for a table, chart, code snippet, or number -- give ONLY that.** No preamble, no caveats, no "let me know if you want X" footer. Drop the artifact and stop.
- **Lead with the answer.** Tables / numbers / code first; commentary only if I explicitly ask.
- **Don't restate the question** or pre-announce what you're about to do ("Let me check...", "I'll run...").
- **Inline assumptions next to ambiguous numbers** as a short parenthetical (e.g. "+3.2 bps (r2c, not r2nav)") -- never a multi-line footer.
- **Highlight Coding or Logic Assumptions when you make them** if user prompt is unclear, make assumptions as needed but clearly flag that you made assumptions concisely.
- **SHORT**: if user ends a message with "SHORT" or "short" following their final punctuation (i.e. "What is the average win rate? short") answer the question in no more than 1 sentence. For questions that just request a number, only give the number. Partial phrases are also preferred in SHORT responses.
- Exceptions: if I ask "explain X" / "walk me through Y" / "5pa this", give a full answer.

---

## Restating the prompt
- Whenever I give you a prompt that is unclear or a prompt that has 3 or more requests/steps to it, restate back to me concisely what your plan is and I will review and approve (or correct if necessary).
- For minor prompts where 1-2 requests/steps are asked, you can go ahead and make the changes as you best interpret them.

---

## Respecting existing code
- Ask me before editing any files in `D:/PycharmProjects`.

---

## CLI Path Format (Git Bash)
- The user runs CLI commands in **Git Bash**, which expects Unix-style paths with a lowercased drive letter: `/d/agent_projects/...`, not `D:/agent_projects/...` or `D:\agent_projects\...`.
- Whenever you give the user a command they will copy-paste and run (`cd`, `python`, `ls`, etc.), use the Git Bash format.
  - Right: `cd /d/agent_projects/eod_option_algos/`
  - Wrong: `cd D:/agent_projects/eod_option_algos`, `cd D:\agent_projects\eod_option_algos`
- This rule applies **only to shell commands pasted to user**. Inside Python code, string literals, and other "internal" path references, keep using `D:/...` (which Python handles fine on Windows and matches the rest of this file's conventions).

---

## No Unicode Symbols in Code
- **NEVER use non-ASCII characters ANYWHERE in any code file** -- includes strings, prints, f-strings, docstrings, AND comments. Applies to prod and non-prod alike. Windows cp1252 encoding fails on non-ASCII causing `UnicodeEncodeError` at runtime; comments-only Unicode also breaks downstream tooling and file reads under non-UTF-8 encodings.
- Common offenders -> ASCII replacements: em-dash (U+2014) -> `--`, en-dash (U+2013) -> `-`, right arrow (U+2192) -> `->`, bullet (U+2022) -> `-` or `*`, smart quotes (U+2018/U+2019/U+201C/U+201D) -> `'` and `"`, ellipsis (U+2026) -> `...`, star (U+2605) -> `*`.
- **Before considering any code edit complete**, mentally scan the diff for non-ASCII -- especially em-dashes, which auto-substitute when typing markdown-style prose. If uncertain, grep `[^\x00-\x7F]` over the touched files.

---

## Line Endings
- Author all new files with CRLF (`\r\n`) line endings by default (Windows preference); do not pin files to LF via `.gitattributes`.
- Exception: `.sh` scripts always get LF (bash -- including Git Bash on this machine -- errors on CRLF).

---

## Worktree Path Gotcha
- When running in a git worktree, edits go to the worktree copy (e.g. `D:\agent_projects\.claude\worktrees\...`) but the user is likely running code from the **original project directory** (e.g. `D:\agent_projects\eod_option_algos\`). Always check which path the user is actually executing from and apply edits there, not the worktree copy.

---

## Interactive Notebooks and Analysis Scripts

When asked to create a "notebook" / interactive analysis / test ideas in Python: make a `.py` file with `#%%` cell markers (NOT a `.ipynb`), and **load the `analysis-notebook` skill first** -- it has the required cell order, caching pattern, `clear_caches()` rules, display rules, and the full skeleton.

---

## Cache-Aware Fixes
- When implementing a fix and user is running code in a interactive notebook, **think carefully about which cached variables are actually affected** and minimize what needs to re-run. Never force the user to re-execute expensive steps (OPRA queries, Bloomberg pulls, SQL queries, panel generation) when the fix doesn't touch that data.
- If only a loading/parsing step needs fixing (e.g. snap_time format), apply the transformation **in-place on the already-cached variable** (e.g. `imbal_data["snap_time"] = imbal_data["snap_time"].str.replace(...)`) and then re-run only the cheap downstream steps (merges, renames, Excel export). Don't put the fix only in the loader function and tell the user to clear cache.
- If only column selection or formatting is wrong (e.g. missing columns in a rename dict), the fix should only require re-running the rename/export cell -- not any upstream data loading or querying.
- **Rule of thumb**: A fix should require re-running the minimum number of cells. Identify exactly which cells are affected and tell the user which specific cells to re-run.

## Using Cached Data in Snippets
- When writing new snippets or analysis code, **always use cached variables directly** (e.g. `combined_data_dict['NDXP']`, `apply_config(combined_data_dict[...], cfg)`).
- **NEVER call wrapper functions** (e.g. `test_strategy()`, `ensure_data()`) that may trigger a data rebuild. Use the underlying functions (`apply_config`, `load_single_config`) with the already-cached data passed in explicitly.
- Assume data is already loaded in the interactive session unless the user says otherwise.

---

## Debug Snippets and Copy-Paste Blocks
- When fixing or editing ANY copy-pasteable block -- code snippet, prompt text, SQL, config, etc. -- **always repaste the ENTIRE block** -- never give partial diffs or just the changed lines. The user should be able to copy-paste the whole thing from the chat without merging.

---

## Function Documentation
- All new functions must have a 1-2 line description of what they do. Conciseness is appreciated. Exceptions:
  - **A)** If the function name is non-explanatory (e.g. `get_df` vs `get_corporate_actions_from_spiderrock`), the description must explain what data is returned.
  - **B)** If the function takes more than 3 arguments, list each argument in order with a 3-8 word explanation of what the argument is.

---

## Sharpe Ratio
- Do not annualize Sharpe (no `* sqrt(252)`) unless user explicitly asks for it. Report raw `mean / std` over the observations.

---

## Market Type Definitions (Up / Down / Flat)

**`market_ratio`** = `(spy_price_at_time_T - yesterday_close) / rolling_90day_std_of_daily_moves`

Normalizes the day's move by recent volatility. The reference time T is context-dependent (commonly 3:40 PM or 3:50 PM, but any intraday time is valid).

- **Numerator**: today's return from yesterday's close to the price at time T (the only intraday input).
- **Denominator (`rolling_std`)**: trailing 90-day std of **daily close-to-close returns** (xbbg `PX_LAST`, `adjust='all'`), excluding today. NOT computed from intraday snaps.

| market_type | Condition | Meaning |
|-------------|-----------|---------|
| **Up** | `market_ratio > 0.5` | Moved up more than half a std dev |
| **Down** | `market_ratio < -0.5` | Moved down more than half a std dev |
| **Flat** | `abs(market_ratio) < 0.5` | Within half a std dev |

**Pre-computed data sources**: `spy_daily_moves_<HH_MM>.csv` / `qqq_daily_moves_<HH_MM>.csv` with `market_ratio`, `yest_close_price`, `rolling_std`, `rsi3`, `trade_price`, in `D:/PycharmProjects/scratch/imbal_research/data/`. The file-name suffix is the **actual snap second**. Updated by `python D:/agent_projects/eod_option_algos/update_data.py` -- steps `3a` (writes the `_50_01` files) and `3b` (writes the `_40_00` files); both run in a default full run, or target them with `--steps 3a,3b`. For ANY other snap time, use `python D:/agent_projects/eod_option_algos/build_daily_moves.py <HH:MM:SS>` (e.g. `build_daily_moves.py 15:55:01`, `build_daily_moves.py 14:00`) -- same market_ratio/RSI3 logic, writes the matching `spy/qqq_daily_moves_<suffix>.csv`.

**Snap-time rule for market type at time T:**
- When user says 3:50pm (or 350, 350pm, "15:50", etc), he wants **15:50:01**. If he says 3:55pm (or 355, 355pm, "15:55", etc), he wants **15:55:01**. These are the ONLY timestamps that should be treated this way. Rationale: the :00 tick at these times does not reflect the large price action that occurs right after imbalance publication -- the :01 snap does.
- ALL other timestamps -> the exact minute at :00 (2pm -> 14:00:00, 3pm -> 15:00:00, 3:40pm -> 15:40:00, close -> 16:00:00)

Full schemas, file locations, and how to compute market_ratio at other intraday times: `data-sources` skill.

---

## Expiry Type Definitions (Serial / Quarterly)

- **Serial**: A standard monthly options expiry (3rd Friday of each month). The full list is `calendar_utils.SERIALS`. Can also be called "monthly expiry".
- **Quarterly**: A serial expiry that falls in Mar, Jun, Sep, or Dec (triple/quad witching months). Quarterlies are a subset of serials.

---

## Closing Imbalance Conventions

### Snap times
Same rule as "Market Type Definitions -> Snap-time rule" and it applies equally to imbal and price snaps: 3:50pm -> **15:50:01**, 3:55pm -> **15:55:01** (post-publication); all other intraday snaps (14:00, 15:00, 15:30, etc.) use **:00**.

### Sign convention
- `spy_net_imbalance > 0` -> net **buy** ("for purchase")
- `spy_net_imbalance < 0` -> net **sell** ("for sale")
- "\$X for sale" means `spy_net_imbalance < -X` (e.g. "\$1.5B for sale" means `< -1.5e9`)

### Return to NAV vs Return to Close (CRITICAL -- these are NOT the same)

The user is **always precise** about which one they want. Do not conflate them.

- **"Return to close"** -> close = `PX_LAST` from xbbg (typically with `adjust='-'` for raw as-traded). Last trade print at 16:00:00.
- **"Return to NAV"** -> NAV = the official ETF NAV print, which differs from the 4pm trade close. Source: `compositions.t_compositions_ETFDailyBasketHeaders.officialNavUSD`. NAV is NOT in the pre-pulled intraday CSV -- it requires a SQL pull (template in the `data-sources` skill, references/alpine_tables.md).

**Return formulas (in bps):**
- Return to NAV   = `(officialNavUSD / spy_price_at_snap - 1) * 1e4`
- Return to close = `(px_last        / spy_price_at_snap - 1) * 1e4`

If the user says only "return" without qualifier, **ASK** which one they want.

### Pre-pulled intraday imbalance data
`D:/agent_projects/eod_option_algos/spy_imbalances_<MM_DD_YYYY>.csv` (latest dated file is current; refreshed daily). Per-second SPY/QQQ imbal + price 14:00 to 16:00 -- use directly for intraday imbal/price slicing without re-querying VBAM. Full schema and `snap_time` parsing notes: `data-sources` skill.

### Day-type bucketing for imbal stats
When breaking imbal results out by day type, default to these mutually exclusive buckets:
**Month End | Fed Day | Serial | Regular**

- `Month End` = last trading day of each calendar month. Use `calendar_utils.is_month_end(trade_date)` or `calendar_utils.month_ends(start, end)`.
- `Fed Day` = `trade_date in calendar_utils.FEDS`.
- `Serial` = `trade_date in calendar_utils.SERIALS`.
- `Regular` = everything else.

Always report the **bucket-total denominator** (e.g. "4 hits out of 65 month-ends") so the user can see how thin the sample is.

---

## Chat Short Hand (common abbreviations)
   - jsq or JSQ = Jane Street Quant
   - ge or GE = Google Engineer
   - sp or SP = MIT Statistics Professor
   - 5PA or 5pa = 5 Panel Analysis -> run the `expert-panel-5pa` skill
   - r2c or R2C or "smash return to close" = Return to Close (snap-to-PX_LAST SPY return, in bps; see "Closing Imbalance Conventions")
   - r2nav or R2NAV or "smash return to NAV" = Return to NAV (snap-to-officialNavUSD return, in bps; NOT the same as r2c; see "Closing Imbalance Conventions")
   - **Important**: As per time conventions, if user asks for "smash return from 350 to nav" they want the **15:50:01** to NAV return, whereas "smash return from 340 to nav" would be **15:40:00** to NAV.

---

## Data Pulls and Libraries

- **Before pulling ANY market / imbalance / options / NAV / price data, load the `data-sources` skill** -- it is the router for which source to use (Bloomberg, SpiderRock, ThetaData, cq_helpers, VBAM SQL tables, local CSVs) and holds the full table/CSV catalogs.
- Pull mechanics live in dedicated skills: **`bloomberg-data`** (xbbg: bdh/bdp/bds, adjust rules, blpapi setup) and **`spiderrock-data`** (spdr_rock_functions live data; liberator historical options/IV incl. the env-vars-before-import auth gotcha).
- Always prefer libraries at `/d/PycharmProjects/utils/`: `calendar_utils` (dates/trading calendar), `spdr_rock_functions` (live options/vol), `cq_helpers` (intraday historic prices), `db_helpers` (historical vol), `thetadata_helpers` (OPRA quotes/index ticks), `google_chat_webhook` (chat alerts). For open/close only, use `xbbg`.
- Reload libraries using: `import importlib` -> `import <module>` -> `importlib.reload(<module>)` -> `from <module> import *`.

---

## Charts and Visualizations

### Precedence
1. **If I provide a reference image**, match its style (colors, layout, axis treatment). My screenshot wins over defaults.
2. **Otherwise**, apply the defaults below.

### Defaults
- Senior data scientist quality. Clean, professional, interpretable.
- Background: `facecolor='#f5f5f5'` on both `fig.patch` and `ax`.
- Legend (when applicable): outside the chart on the right (`bbox_to_anchor=(1.02, 1), loc='upper left'`).
- Hide top + right spines, light grid (`alpha=0.3`).
- Clear axis labels with units.

### Title content (include the relevant ones)
- Sharpe (2dp): `Sharpe: 1.45` -- raw `mean/std`, NOT annualized (per Sharpe Ratio rule).
- Mean / median return: `Mean: 0.12%` or in bps where appropriate.
- Observations: `N=1,234`.
- Max DD: `Max DD: -15.2%`.
- Date range / period if not obvious.

### Escape `$` in titles/labels
Matplotlib reads `$` as LaTeX math. Always escape:
```python
ax.set_title(f'Mean: \${value:,.0f}')   # right
ax.set_title(f'Mean: ${value:,.0f}')    # wrong -- parse error
```

### Saving / output
- **Do NOT save** figures, csvs, xlsx, etc. unless I explicitly ask.
- When I do ask to save: destination is **`C:/Users/zdietz/Downloads/`** with a `descriptive_name_YYYYMMDD_HHMM` filename.

### Inline Charts vs Interactive Widgets

When user asks for a line chart (i.e. cumulative pnl vs time or some other factor) in the desktop app, prefer an interactive widget over a static png. To correctly render the image without hallucination: **NEVER** hand-type data arrays into widget code. Instead: generate the data with Python, dump to a file via `json.dumps`, template-substitute into a widget HTML file via `str.replace`, then pass the file content to `show_widget`. The widget's data literal must be byte-identical to Python's `json.dumps` output. For cumulative PNL charts, forward-fill in Python before passing to the widget so lines stay flat between trade dates. Chart.js `spanGaps: true` is NOT equivalent to ffill (it interpolates diagonally across nulls).

Widget size: canvas height 300-360px, one visible chart per widget. Stat cards below for totals/Sharpe/win rate/drawdown (max 1 day)/trade count.

### Rendering / size limit (inline charts must stay under the MCP token cap)

Inline charts are returned through the Jupyter MCP tool as a base64 PNG. Claude Code truncates any MCP tool response over `MAX_MCP_OUTPUT_TOKENS` (default 25,000), so an oversized chart is silently dropped -- I still receive the image and may report "rendered above," but user sees nothing. A default `figsize=(13,6)` at `dpi=100` encodes to ~24,600 tokens, right at the cap, so it renders only intermittently.

**Rules for every inline chart:**
- Default to `figsize <= (11, 5)` and `dpi <= 80`.
- Data density matters as much as dpi: for dense time series (thousands of points) where only the shape matters, thin the line first (resample / every Nth point, ~300-500 pts). However, if user asks you to download the image, do NOT resample in that downloaded version.
- Do not pack multiple dense panels or a `barh` of many categories into ONE image -- split into separate figures or simplify.
- When unsure, measure before `plt.show()` and keep the estimate under 22,000 tokens for margin:
  ```python
  import io, base64
  b = io.BytesIO(); fig.savefig(b, format='png', dpi=D, facecolor='#f5f5f5')
  est_tokens = len(base64.b64encode(b.getvalue())) / 3.5   # keep < 22000
  ```

### Backtests / model fits
- Primary goals: not overfitting, simplicity, interpretability. We must understand the model and trust it out of sample.

---

## Excel Deliverables

When asked to "download data" / save results / save a backtest / build an Excel pivot table or heatmap: **load the `excel-deliverables` skill first.** Core rules: save as **.xlsx** (not csv) to `C:/Users/zdietz/Downloads/` as `<name>_YYYYMMDD_HHMM.xlsx`; pivot tables are ALWAYS native Excel PivotTables via `create_pivots_subprocess` (never raw win32com in-process in Jupyter -- it crashes the kernel).

---

## Shared Jupyter Workflow (VS Code + Claude Code)

A persistent JupyterLab server on `localhost:9500` lets VS Code's Interactive Window and Claude Code share a live kernel. **Whenever the user pastes a kernel UUID or says "connect to kernel" / "attach to" / "use kernel": load the `shared-jupyter` skill and follow its attach procedure BEFORE running any code or writing any variables.**

Two rules that must hold even before the skill loads:
- **NEVER pass `kernel_id` to `mcp__jupyter__execute_code`** to target the user's kernel -- it silently routes to the wrong kernel. Bind with `use_notebook` (mode="connect") per the skill.
- If the `:9500` server isn't up, don't start one yourself -- tell the user and wait.

---

## MCP Execute Timeout vs Slow Kernel Work

`mcp__jupyter__execute_code` has a hard 60-second cap. If a kernel operation will take longer (combined_data rebuild ~150s in eod_option_algos, eod_355_option_algos, big SQL pull, large file load, full backtest sweep, etc.), do NOT try to run it via MCP -- the cell gets interrupted at 60s and the kernel state is left in a partial/broken spot.

Also do NOT spin up a parallel subprocess to do the work outside the kernel just because the kernel can't fit it in 60s -- the user did not ask for a 3-minute background task and won't expect one.

Correct pattern:

Recognize the work is too slow for MCP.
Tell the user: "this will exceed MCP's 60s timeout -- can you run `<exact snippet>` in your kernel and ping me when done?"
Wait. Do not start parallel rebuilds, subprocess pickles, scheduled wakeups, or anything else.
When the user confirms "done", continue from the now-populated kernel state via MCP.
Default to asking, not doing, whenever the task plausibly crosses the 60s line.

---

## Saving Chat Recaps

When I say "save down this chat" / "save down this chat to chat_recaps" (or any close variant -- "archive this work", "save this analysis to recaps", etc.): **run the `chat-recap` skill** (creates a self-contained directory under `D:/agent_projects/chat_recaps/<descriptive_name>/` with final scripts + structured README, and confirms the path back to me).
