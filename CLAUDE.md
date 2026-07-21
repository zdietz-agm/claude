# Global Rules

---

## Response Style Defaults
- **Default to 1-sentence responses.** Long answers clutter the chat. I will prompt for depth when I want it.
- **If I ask for a table, chart, code snippet, or number -- give ONLY that.** No preamble, no caveats, no "let me know if you want X" footer. Drop the artifact and stop.
- **Lead with the answer.** Tables / numbers / code first; commentary only if I explicitly ask.
- **Don't restate the question** or pre-announce what you're about to do ("Let me check...", "I'll run...").
- **Inline assumptions next to ambiguous numbers** as a short parenthetical (e.g. "+3.2 bps (r2c, not r2nav)") -- never a multi-line footer.
- **Highlight Coding or Logic Assumptions when you make them** if user prompt is unclear, make assumptions as needed but clearly flag that you made assumptions concisely.
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
- Exception: `.sh` scripts that run on Linux need LF -- the user will convert those on the target machine.

---

## Worktree Path Gotcha
- When running in a git worktree, edits go to the worktree copy (e.g. `D:\agent_projects\.claude\worktrees\...`) but the user is likely running code from the **original project directory** (e.g. `D:\agent_projects\eod_option_algos\`). Always check which path the user is actually executing from and apply edits there, not the worktree copy.

---

## Interactive Notebooks and Analysis Scripts

When asked to create a "notebook" / interactive analysis / test ideas in Python, make a `.py` file with `#%%` cell markers (NOT a `.ipynb`).

**Cell-marker order:** Imports -> Reimport helpers -> Globals -> Clear caches -> Cache cells -> Helpers -> Data load -> Processing -> Backtesting -> Visualization.

**Caching pattern:** wrap every expensive operation in `if 'var_name' not in dir():`. Label cache cells `#%% Cache: [description]`. Never overwrite cached data on rerun.

**Always include a `clear_caches()` function** in its own cell (uses `globals()`, not `dir()`, to actually delete). List every cached variable name. Provide feedback on what was cleared.

**Display rules:**
- `display()` not `print()` for DataFrames.
- Add `display(df.sample(5))` sanity check after every merge / PnL calc / major transform.
- `pd.set_option('display.max_columns', N)` with N = widest-df column count + 5.

**Code style:**
- **NEVER use `if __name__ == '__main__':`** -- indentation breaks Jupyter interactive execution.
- Keep all code at module level, separated by `#%%`.
- Concise inline comments; skip when variable names are self-explanatory.

**IMPORTANT: Copy-paste-ready skeleton, full `clear_caches()` template, sanity-check examples:** see `C:/Users/zdietz/.claude/docs/notebook_skeleton.md`.

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

## Debug Snippets
- When fixing a debug snippet or any multi-line code block the user is meant to copy-paste, **always repaste the ENTIRE snippet** -- never give partial diffs or just the changed lines. The user should be able to copy-paste the whole thing without merging.

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

| market_type | Condition | Meaning |
|-------------|-----------|---------|
| **Up** | `market_ratio > 0.5` | Moved up more than half a std dev |
| **Down** | `market_ratio < -0.5` | Moved down more than half a std dev |
| **Flat** | `abs(market_ratio) < 0.5` | Within half a std dev |

**Pre-computed data sources** (maintained by `eod_option_algos/update_data.py`):
- `spy_daily_moves_50_01.csv` -- market_ratio at 3:50 PM
- `spy_daily_moves_40_00.csv` -- market_ratio at 3:40 PM
- `qqq_daily_moves_50_01.csv` / `qqq_daily_moves_40_00.csv` -- same for QQQ

The file-name suffix is the **actual snap second**, not just shorthand:
- `_50_01` -> 15:50:**01** (the official NYSE 3:50pm publication tick; magnitudes are post-publication)
- `_40_00` -> 15:40:**00**
- `_00_00` -> 16:00:**00** (close)

The :00 vs :01 distinction matters: at 15:50:00 the closing imbalance has not yet been published, so whenever user asks for "15:50"/"3:50"/"350"/etc imbal, he wants the 15:50:01 numbers that reflect the imbalance publication. **For any 3:50pm filter / threshold work, always use 15:50:01.** For other intraday snap times (14:00, 15:00, 15:30, etc.) use `:00`.

These CSVs contain `market_ratio`, `yest_close_price`, `rolling_std`, `rsi3`, and `trade_price`. For other intraday times, compute manually: pull SPY price at time T from `auctionResearch.t_report_consolidated_imbalances` (has data starting ~2 hours before close each day) or `cq_helpers` (for morning data), then divide `(price_T - yest_close_price) / rolling_std` using the rolling_std from the nearest pre-computed CSV.

---

## Expiry Type Definitions (Serial / Quarterly)

- **Serial**: A standard monthly options expiry (3rd Friday of each month). The full list is `calendar_utils.SERIALS`.
- **Quarterly**: A serial expiry that falls in Mar, Jun, Sep, or Dec (triple/quad witching months). Quarterlies are a subset of serials.

---

## Closing Imbalance Conventions

### Snap times
- **3:50pm imbal/price**: always use **15:50:01** (post-publication). 15:50:00 does not reflect large price action that occurs after imbalance publication.
- All other intraday snaps (14:00, 15:00, 15:30, etc.): use **:00**.

### Sign convention
- `spy_net_imbalance > 0` -> net **buy** ("for purchase")
- `spy_net_imbalance < 0` -> net **sell** ("for sale")
- "$X for sale" -> `spy_net_imbalance < -X` (e.g. "$1.5B for sale" -> `< -1.5e9`)

### Return to NAV vs Return to Close (CRITICAL -- these are NOT the same)

The user is **always precise** about which one they want. Do not conflate them.

- **"Return to close"** -> close = `PX_LAST` from xbbg (typically with `adjust='-'` for raw as-traded). Last trade print at 16:00:00.
- **"Return to NAV"** -> NAV = the official ETF NAV print, which differs from the 4pm trade close. Source: `compositions.t_compositions_ETFDailyBasketHeaders.officialNavUSD`. NAV is NOT in the pre-pulled intraday CSV -- it requires a SQL pull.

**SQL template (SPY NAV joined to imbalance snaps):**
```sql
SELECT
    i.business_date,
    i.snap_time,
    i.spy_universe,
    i.spy_moc_net_imbalance,
    i.spy_dquote_net_imbalance,
    i.spy_exchange_net_imbalance,
    i.spy_net_imbalance,
    i.spy_paired_imbalance,
    i.spy_price,
    i.qqq_net_imbalance,
    b.officialNavUSD
FROM
    auctionResearch.t_report_consolidated_imbalances i
LEFT JOIN
    compositions.t_compositions_ETFDailyBasketHeaders b
    ON i.business_date = b.navDate
WHERE
    b.etfTicker = 'SPY';
```

**Return formulas (in bps):**
- Return to NAV   = `(officialNavUSD / spy_price_at_snap - 1) * 1e4`
- Return to close = `(px_last        / spy_price_at_snap - 1) * 1e4`

If the user says only "return" without qualifier, **ASK** which one they want.

### Pre-pulled intraday imbalance data
File: `D:/agent_projects/eod_option_algos/spy_imbalances_<MM_DD_YYYY>.csv` (latest dated file is current; refreshed daily by `D:/agent_projects/eod_option_algos/update_data.py`).
Schema: `business_date, snap_time, spy_moc_net_imbalance, spy_dquote_net_imbalance, spy_net_imbalance, spy_paired_imbalance, spy_price, qqq_net_imbalance, qqq_paired_imbalance, qqq_price`.
`snap_time` is a string `"0 days HH:MM:SS"` (pandas timedelta serialization). Parse with `pd.to_timedelta` if you need numeric ops; filter directly on the string for exact-snap lookups (e.g. `snap_time == "0 days 15:50:01"`).
Populated every second from ~13:50 to 16:00 -> use directly for any intraday imbal / price slicing without re-querying VBAM.
Does **not** include `officialNavUSD` -- run the NAV SQL above if NAV is needed.

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
   - 5PA or 5pa = 5 Panel Analysis (see below)
   - r2c or R2C or "smash return to close" = Return to Close (snap-to-PX_LAST SPY return, in bps; see "Closing Imbalance Conventions")
   - r2nav or R2NAV or "smash return to NAV" = Return to NAV (snap-to-officialNavUSD return, in bps; NOT the same as r2c; see "Closing Imbalance Conventions")
   - **Important**: As per time conventions, if user asks for "smash return from 350 to nav" they want the **15:50:01** to NAV return, whereas "smash return from 340 to nav" would be **15:40:00** to NAV.
   - SHORT: if user ends a message with "SHORT" or "short" following their final punctuation (i.e. "What is the average win rate? short") answer the question in no more than 1 sentence. For questions that just request a number, only give the number. Partial phrases are also preferred in SHORT responses.

---

## Libraries and Imports

- Always prefer to use libraries at `/d/PycharmProjects/utils/` to achieve tasks. Most notably:
  - **A)** `calendar_utils` -- pull valid trading dates or any date-related requests.
  - **B)** `spdr_rock_functions` -- pull options and volatility data from SpiderRock (unless pulling data from the liberator api as I do frequently in `/d/PycharmProjects/spdr_liberator` directory. `/d/PycharmProjects/spdr_liberator/helpers_improved.py` has many useful functions for pulling historic options and implied volatility data).
    - **Liberator setup:** The `liberator` module requires `liberator.pfx` and `liberator.json` (auth credentials) to be in the working directory by default. When using liberator from a script **outside** `D:/PycharmProjects/spdr_liberator/`, you **must set environment variables BEFORE importing liberator**, because `liberator.py` evaluates `os.getenv('LIBERATOR_USER')` and `os.getenv('LIBERATOR_TOKEN')` at module-load time (in `_query_defaults`). Setting `liberator.auth` after import does NOT update the cached credentials.
      ```python
      import json, os
      _lib_creds = json.load(open('D:/PycharmProjects/spdr_liberator/liberator.json'))
      os.environ['LIBERATOR_USER'] = _lib_creds['user']
      os.environ['LIBERATOR_TOKEN'] = _lib_creds['token']
      import liberator  # MUST come after env vars are set
      liberator.url = "https://getdata.spiderrock.net"
      liberator.pfx = "D:/PycharmProjects/spdr_liberator/liberator.pfx"
      liberator.auth = "D:/PycharmProjects/spdr_liberator/liberator.json"
      ```
      Without env vars set before import: `No user arg provided` error. Without pfx path: `FileNotFoundError: PFX file not found`.
  - **C)** `google_chat_webhook` -- send alerts in Google Chat.
  - **D)** `cq_helpers` -- pull intraday historic price data; if only pulling open or close prices, use `xbbg` instead.
  - **E)** `db_helpers` -- historical volatility data.
  - **F)** `thetadata_helpers` -- Historical OPRA option quotes (bid/ask/size, 1s snapshots) and index price series (per-exchange-tick SPX/NDX/VIX/etc.) via local ThetaTerminal (`127.0.0.1:25510`, must be running). Index price pulls are cached to `optionsResearch.t_index_snaps_td` and options quotes are cached to `optionsResearch.t_opra_quotes` on VBAM dev.
- Reload libraries using: `import importlib` -> `import <module>` -> `importlib.reload(<module>)` -> `from <module> import *`.

**Required libraries by task (quick reference):**

| Task | Library | Import |
|------|---------|--------|
| Date/calendar operations | calendar_utils | `from calendar_utils import *` |
| Live volatility data | spdr_rock_functions | `from spdr_rock_functions import *` |
| Live market data (not vol) | xbbg | `from xbbg import blp` |
| Historical volatility | db_helpers | `from db_helpers import *` |
| Chat notifications | google_chat_webhook | `from google_chat_webhook import send_message` |
| ThetaData options / index history | thetadata_helpers | `from thetadata_helpers import *` |

Library path: `d:/PycharmProjects/utils/`

### XBBG (Bloomberg) -- pulling data

Use `from xbbg import blp` for historical and point-in-time Bloomberg data. For **intraday** bars use `cq_helpers`; for **open/close only** use xbbg.

- `bdh` -- historical time series (multiple dates).
- `bdp` -- point-in-time snapshot (single date / as-of).
- `bds` -- record-set queries (e.g. `DVD_HIST_ALL` for dividend history).

**Useful fields**

| Mnemonic     | Description              |
|-------------|--------------------------|
| `PX_LAST`   | Last / close price       |
| `PX_OPEN`   | Open price               |
| `CHG_PCT_1D`| One-day percent change   |
| `VOLUME`    | Volume                   |

**bdh `adjust` parameter (rule)**

- `adjust='all'` -> split/dividend adjusted. Use for continuous, comparable price/return series viewed alone.
- `adjust='-'`   -> raw, as-traded prices. Use when combining with other unadjusted sources (option prices, SpiderRock liberator data).

Suffixes: ` US Equity` for US equities (e.g. `SPY US Equity`), ` Index` for indices (e.g. `SPX Index`).

**Examples + dividend-history pattern:** see `C:/Users/zdietz/.claude/docs/xbbg_reference.md`.

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

## Excel data export

When asked to "download data" / save results / save a backtest: save to **`.xlsx`** (not csv) in `C:/Users/zdietz/Downloads/` with filename `<name>_YYYYMMDD_HHMM.xlsx`.

**Sheet structure (multi-backtest):** Sheet 1 = `"All"` (combined, with a `strategy` or `backtest` column); additional sheets one per backtest, named descriptively.

**Required Excel features:** AutoFilter on header row, freeze leftmost columns (typically `trade_date`/`time`), auto-fit column width.

**Column ordering:** `pnl` or `daily_pnl` is the first column after the frozen leftmost columns.

**Analysis-relevant columns (only include these):** `trade_date`, `time`, `symbol`, `pnl`, `expiry`, `strike`, `cp`, spread strikes (`short_strike`/`long_strike` or put/call variants), pnl breakdown (`gamma_pnl`, `vega_pnl`, `theta_pnl`, `opt_pnl`), Greeks (`delta`, `gamma`, `vega`, `theta`, `iv`), `underlying_price`, `entry_price`, `exit_price`.

**Formatting:**

| Column type | Format |
|---|---|
| Dollar values (pnl, price, premium) | Accounting, 2dp, red negative (`_($* #,##0.00_);[Red]_($* (#,##0.00)`) |
| Greeks (delta, gamma, vega, theta, iv) | Round to 3 decimals |
| Long decimals (payout, ratio) | Round to 3 decimals |
| Percentages | 2 decimals with `%` |

**Full `export_to_excel()` template:** see `C:/Users/zdietz/.claude/docs/excel_data_export.md`.

---

## Native Excel Pivot Tables

When I ask for a pivot table in Excel, **always create a native Excel PivotTable** (not static cells that look like a pivot). Only use static cells if I explicitly say so.

**Hard rules:**
- **NEVER run `win32com` / COM automation in-process in Jupyter** -- it will crash the kernel. Always run it via a **subprocess**.
- Use the helper: `from excel_pivot_helper import create_pivots_subprocess` (`D:/PycharmProjects/utils/excel_pivot_helper.py`).
- Pattern: write data with `openpyxl`, close the file, then call the helper.
- "Heatmap" = 3-point color scale, -3 red / 0 white / 3 green (defined in the helper).

**Full COM internals, constants, code examples, and `create_pivots_subprocess` signature:** see `C:/Users/zdietz/.claude/docs/excel_pivots.md`.

**Reference implementations on disk:**
- `D:/agent_projects/month_end/create_month_end_excel.py` (basic usage)
- `D:/agent_projects/sp500_adds/candidates_buying_vol.py` (multi-row-field pivot)

---

## Shared Jupyter Workflow (VS Code + Claude Code)

A persistent JupyterLab server runs on `localhost:9500` so VS Code's Interactive Window and Claude Code can share a live Python kernel within a chat. **VS Code spawns the kernel, Claude attaches via `kernel_id`** -- never the other way around (VS Code's picker can't see Claude-spawned kernels).

**If the server isn't up on `localhost:9500`** (attach/list calls error with connection refused, or `mcp__jupyter__list_kernels` returns nothing), do NOT try to start it yourself or spin up a different server. Tell the user the `:9500` JupyterLab server isn't running and ask them to start it, then wait. Everything below assumes that server is live.

### Trigger phrases (attach-to-kernel intent)

Treat ANY of these as a request to attach to the user's live kernel and run subsequent code there so the user sees the touched variables in their Interactive Window:

- "connect to kernel with UUID '<uuid>'", "connect to kernel '<uuid>'", "connect to '<uuid>'", "connect to notebook '<uuid>'", "attach to '<uuid>'", "use kernel '<uuid>'", or any message that pastes a bare kernel UUID and asks to run/create something.

A "UUID" here is the 8-4-4-4-12 hex string (e.g. `7043d46c-341c-45d8-ba2b-2b8c388d6fd9`). When you see one of these, run the **Attach procedure** below BEFORE writing any variables. Do not answer or run code until the attach is verified.

### CRITICAL: how kernel targeting actually works (read before touching Jupyter)

- **`use_notebook` is the ONLY correct way to bind to the user's kernel.** It is what makes the user's Interactive Window and your `execute_code` calls share one live kernel.
- **NEVER attach to a kernel, or create/assign variables the user needs to see, by passing `kernel_id` to `mcp__jupyter__execute_code`.** That argument does NOT reliably target the kernel you name -- when the kernel isn't the currently-activated notebook, the call silently routes to a different default kernel. Code "succeeds" (prints the right answer) but lands in the wrong process, and the user's `blah` comes back `NameError`. This is a silent footgun; it has burned us. Bare-`kernel_id` `execute_code` is ONLY acceptable for throwaway inspection of a kernel you have already separately confirmed -- never for the user's working state.
- After a successful `use_notebook`, call `execute_code` with **no `kernel_id`** -- it targets the bound kernel, which is the user's kernel.

### Attach procedure (run on every trigger)

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

### Critical RAM rules

All kernels on `:9500` share physical RAM. Before allocating >500MB, call `check_ram(int(<bytes>))`. Never `display(df)` on huge DataFrames without sampling. `del` large intermediates when done.

### When to use

Use the shared kernel for expensive-to-load data + multi-step work. Use one-off Bash `python` calls for quick sanity checks with no reusable state.

### Reference

Full troubleshooting (VS Code extension issues, jupyter-collaboration 404s, server management, manual fallback when the IPython startup file fails, kernel-restart handling, `reload_helpers()` pattern, RAM snapshot details): see `C:/Users/zdietz/.claude/docs/shared_jupyter.md`. Architecture rationale: `D:/agent_projects/shared_jupyter/README.md`.

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

When I say "save down this chat to chat_recaps" or "save down this chat" (or any close variant -- "archive this work", "save this analysis to recaps", etc.), do this:

1. **Create a directory** under `D:/agent_projects/chat_recaps/<descriptive_name>/`. Pick a name that captures the work topic concisely (e.g. `spy_eod_residual_analysis`, `option_skew_calibration`, `vix_term_structure`). No timestamps in directory names -- the README dates the work.

2. **Save the relevant scripts** into that directory:
   - Include reusable analysis scripts and any helper/probe scripts that document data sources or schemas.
   - Skip one-off `python -c` invocations and stale debug snippets. If the chat included parameter sweeps done inline, distill them into a single parameterized script.
   - Use the **final** definitions / sign conventions / parameters that the chat settled on -- not the intermediate versions that were superseded.

3. **Write a `README.md`** at the directory root covering:
   - **Date** and **what was investigated** (1 short paragraph)
   - **Data sources** table (tables, hosts, Bloomberg fields, library helpers)
   - **Methodology** (definitions, filters, exclusions -- anything not obvious from reading the scripts)
   - **Key findings** (bulleted, with effect sizes / p-values where applicable)
   - **Caveats** (sample size, regime, known limitations)
   - **File listing** (one row per script, what it does)
   - **Reproduction** (run order, dependencies, where outputs land)

4. **Confirm the directory path** back to me when done, so I can paste it into a future chat's first message for context.

Purpose: future chats can rediscover prior work by reading the README rather than re-running discovery. The recap should be self-contained -- anyone (me, a future Claude) should be able to reproduce the work from just that directory + Bloomberg + DB access.

---

## 5 Panel Analysis
When prompted to simulate a panel of 5 experts with phrasing like "run a 5PA" or "5pa this" or "put this though a 5pa", the user means:
Think about the discussed problem, gathering all relevant details, pretending to be each of the following characters:

- Jane Street Quant (a highly technical thinking trader who is steeped in probalistic thinking and aware of market mechanics and common backtesting pitfalls)
- Google Engineer (a professional coder who thinks about scripting efficiency and outside of the box ways to tackle technical problems)
- MIT Statistics Professor (a probility master who can point out relevant random variable processes, apply bayesian thinking, and find logical pit falls)
- Millenium Trader (a proven money maker who doesn't get caught up with theory and can actually make money in an applied way, thinking rationally about PNL)
- Devil's Advocate (a thinker who is counter to the other 4 experts and often points out the flaws in their logic)

Only provide the final, refined response from the panel of experts. Present the results in a clearly labeled table with 5 rows (one for each expert) and a Comment section for each
expert. If an expert has nothing insightful to add, write "no comment". Otherwise, add the most important 1-2 comments of each expert, taking up no more than 4 sentences to explain it.
Do not feel obligated for each expert to chime in if they have nothing important to say.

---

## Data Catalog (Helpful data sources)

### VBAM (aka "VBAM prod" = `alpine-vbam-prod.c7wvpkbyvjzb.us-east-1.rds.amazonaws.com`)

- **`imbalanceSnapshots.t_imbal_1550_BasketSnapshots`** (*Real-time*) -- Basket-level real-time SPX/NDX imbal for post 350pm trading. **Cols:** `runDate`, `basket` (`.SPX`/`.NDX`), `snapTimestamp`, `exchNetImbalTotal`, `exchPairedImbalTotal`, `seenPct`.
- **`EODStrategies.t_Monitor_ImbalanceMonitorSnaps`** (*Real-time*) -- 3:40pm SPX imbalance monitor snaps. **Cols:** `runDate`, `tsSnapTime`, `netImbalance`, `period`, `offset`.
- **`EODStrategies.t_strat_FuturesStrategyCKSmash1550_Summary`** (*Real-time*) -- Legacy way of pulling SPX 350pm imbal (used as fallback for t_imbal_1550_BasketSnapshots now).
- **`auctionResearch.t_imbalance_basket_detail`** (*Real-time*) -- 3:55pm basket imbal with sub-second capture timestamps. **Cols:** `run_date`, `basket_name`, `capture_time`, `exch_net_notional`.
- **`auctionResearch.t_report_consolidated_imbalances`** (*T+1*) -- Consolidated SPY/QQQ ETF imbal + intraday prices every second 14:00 - 16:00. 15:50:01 timestamp is the historical source of truth for 3:50pm values of SPX imbal / NDX imbal / SPX paired imbalance; source for `spy_imbalances_<date>.csv`. **Cols:** `business_date`, `snap_time`, `spy_net_imbalance`, `spy_paired_imbalance`, `spy_price` (also `qqq_*`).
- **`auctionResearch.t_trade_price_snaps`** (*T+1*) -- Equity/ETF intraday trade prices at specific snap times. **Cols:** `business_date`, `ticker`, `snap_time`, `trade_price`.
- **`auctionResearch.t_index_level_snaps`** (*T+1*) -- Index levels (VIX etc.) at intraday snap times. **Cols:** `business_date`, `ticker` (e.g. `I:VIX`), `snap_time`, `index_level`.
- **`compositions.t_compositions_ETFDailyBasketHeaders`** (*T+1*) -- Official ETF NAV published end-of-day; required for any Return-to-NAV calc. **Cols:** `navDate`, `etfTicker`, `officialNavUSD`.

### APIs / libraries

- **`xbbg`** (`blp.bdh/bdp/bds`) (*Real-time*) -- Bloomberg historical + snap data; requires terminal connection. **Useful fields:** `PX_LAST`, `PX_OPEN`, `CHG_PCT_1D`, `VOLUME`.
- **`cq_helpers`** (*T+1*) -- Intraday price history (second snaps). Function-call interface.
- **`spdr_rock_functions`** (*Real-time*) -- Live SpiderRock options + IV surface. Function-call interface.
- **ThetaData HTTP API** (`localhost:25510`) (*T+1*) -- OPRA quote history; requires local ThetaTerminal. **Cols:** `ms_of_day`, `bid`, `ask`, `bid_size`, `ask_size`.

### T+1 local CSVs in `D:/agent_projects/eod_option_algos/`

- **`spy_imbalances_<MM_DD_YYYY>.csv`** (*T+1*) -- Daily snapshot of `t_report_consolidated_imbalances`. **Cols:** `business_date`, `snap_time`, `spy_net_imbalance`, `spy_paired_imbalance`, `spy_price`, `qqq_net_imbalance`.
- **`SPXW_0DTE_opra_panel.csv`** / **`NDXP_0DTE_opra_panel.csv`** (*T+1*) -- 0DTE option quotes panel for backtests. **Cols:** `trade_date`, `exp`, `strike`, `cp`, time-bucketed bid/ask.

### T+1 local CSVs in `D:/PycharmProjects/scratch/imbal_research/data/`

- **`spy_daily_moves_<HH_MM>.csv`** / **`qqq_daily_moves_<HH_MM>.csv`** (*T+1*) -- Per-day market_ratio + RSI3 at the snap time encoded in filename. **Cols:** `date`, `trade_price`, `yest_close_price`, `rolling_std`, `market_ratio`, `rsi3`.
- **`spy_high_low_<HH_MM>.csv`** (*T+1*) -- Intraday SPY high/low up to snap time + range-to-vol ratio. **Cols:** `business_date`, `highest_trade_price`, `lowest_trade_price`, `diff_pct_ratio`.
- **`vix_<HH_MM>.csv`** (*T+1*) -- VIX level at snap time + intraday return. **Cols:** `business_date`, `index_level`, `yest_close`, `ret`.
- **`rolling_realized.csv`** (*T+1*) -- Rolling 3-month annualized realized vol for SPY + day-over-day change. **Cols:** `trade_date`, `3m`, `3m_change`.

### T+1 SQL tables (`optionsResearch` in "VBAM dev" = `alpine-vbam-dev.c7wvpkbyvjzb.us-east-1.rds.amazonaws.com`)

- **`optionsResearch.t_historical_options_snaps`** (*T+1*) -- Historical SpiderRock option snapshots; populated via Liberator. **Cols:** `trade_date`, `exp`, `symbol`, `strike`, `cp`, `bidPrc`, `askPrc`, plus Greeks/IV.
- **`optionsResearch.t_opra_quotes`** (*T+1*) -- 1-second OPRA quote history for 0DTE strikes near SPX close; populated via ThetaData. **Cols:** `trade_date`, `exp`, `strike`, `cp`, `timestmp`, `bidPrc`, `askPrc`.

### Helper-function shortcuts (use over raw SQL when possible)

- **Live imbal wrappers** (`D:/PycharmProjects/scratch/algos/helpers.py`): `get_340_imbal`, `get_350_imbal`, `get_355_imbal`, `get_recreated_paired_imbal`, `get_qqq_net_imbal`, `get_fast_imbal`. All retry up to 7x with timeouts; return `NO_IMBAL_VAL` on failure; accept `is_test=True, test_imbal=<num>` for dry runs.
- **Historical options:** `D:/PycharmProjects/spdr_liberator/helpers_improved.py` (env vars before import; see Libraries and Imports).
- **Dates / calendar:** `calendar_utils` -- `SERIALS`, `FEDS`, `is_month_end`, `month_ends`, `trading_range`, `next_trade_day`, `x_days_ago`.