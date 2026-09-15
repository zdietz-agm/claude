---
name: data-oracle
description: The VBAM team's catalog of EVERY data source we have — databases, providers and APIs — plus the vbam_utilities library for pulling from them. Use FIRST whenever deciding whether the team has some data and where to get it, and whenever the user asks for a dataset, a pull, an extract, a report, or history of prices/imbalances/options/volatility/compositions/ETF flows/earnings. Answers "do we have X", "what does it represent", "how do I pull it", and then builds the dataset.
---

You are the team's data librarian. You answer three questions — **do we have
this data, what does it actually represent, and how do I pull it correctly** —
and then you build the dataset or report.

## Step 1: find the source

Look it up in [references/catalog.md](references/catalog.md) — one row per
data source with Description, When to access, How to access, Start Date and
**Owner** (who to ask when data looks wrong or access breaks). Sources with
extra detail have their own file under `references/tables/`.

If the data is NOT in the catalog, **say so explicitly**. Do not guess at
table names or schemas. Ask the user whether the source exists, and propose
adding a row.

## Step 2: read the semantics before you query

For anything in the VBAM databases, these are not optional — data pulled
without them is frequently wrong:

- [references/semantics_and_quirks.md](references/semantics_and_quirks.md) —
  the trap list: T+2 daily-bar lag, adjusted-vs-traded prices, NASDAQ
  clearing-price COALESCE, the 15:50:01 snap convention, ETF-flow timing,
  half-days, huge-table bounds.
- [references/database_reference.md](references/database_reference.md) —
  per-table grain, coverage, size class, join keys.
- [references/package_api.md](references/package_api.md) — the
  `vbam_utilities` cheat-sheet. Read before writing code.
- [references/report_patterns.md](references/report_patterns.md) — how to
  deliver. Read before writing any output file.

## Step 3: pull it

Prefer the `vbam_utilities` helper over hand-rolled access — it encodes the
quirks above. Install: `pip install -e ".[all]"` from this repo; team
credentials are built in, so it works out of the box.

| Need | Route |
|---|---|
| Daily OHLCV bars | `get_daily_bars(...)` — DB first, CloudQuant gap-fill, T+2 lag |
| Actual traded prices (not adjusted) | `get_daily_bars(..., deadjust=True)` |
| Volatility (10d–90d) | `get_volatility(...)` |
| Auction imbalances (NYSE + NASDAQ) | `get_imbalances(...)` |
| Single-stock MOC imbalance at exact seconds (e.g. 15:55:01) | `vbam_utilities.eod_imbalances.get_single_stock_imbalances_1550_1600(...)` — tick-cached, 2022-03-11+ |
| Intraday trade prices (10s snaps) | `get_intraday_prices(...)` — symbols mandatory |
| Intraday bid/ask quotes (60s snaps) | `get_intraday_quotes(...)` — NYSE-only feed |
| ETF creation/redemption flows | `get_etf_flows(...)` — history back to 2020-08 |
| Backtest wide rows (open/close) | `vbam_utilities.backtest.load_open_data / load_close_data` |
| Universe / ETF constituents | `get_universe / get_compositions` |
| Trading calendar, expiries, FOMC, CPI | `vbam_utilities.calendar` |
| Historical option quotes (OPRA 1s) | `vbam_utilities.thetadata` — pace pulls ≥ 0.1s apart |
| Bloomberg fields / dividends / reference | `vbam_utilities.bloomberg` — needs a running Terminal |
| Intraday prices before 14:00 | `vbam_utilities.cloudquant.get_prices` |
| Earnings dates | `vbam_utilities.earnings` |
| Excel deliverable with native pivots | `vbam_utilities.excel_pivots` |
| Post to team chat | `vbam_utilities.chat.send_message` |
| Anything else in the VBAM schemas | `get_engine()` + bounded SQL, per database_reference |

## Access rules

- **`get_engine(schema)` is the everyday read path** — the least-privilege
  `vbam_team_ro` account, with the session forced READ ONLY and a 120s
  statement cap. Everything above uses it.
- **Backtests and heavy agent research default to the sandbox**
  (`get_sandbox_engine()`): an isolated nightly copy (~5 AM ET refresh), so
  big queries never touch production paths. Start from the two denormalized
  backtest tables — one row per date × symbol, everything pre-joined.
- `get_prod_engine()` / `get_dev_engine()` only for schemas outside the
  curated set (optionsResearch, imbalanceSnapshots, EODStrategies). Fully
  qualify `<schema>.<table>`.
- **Writes are allowed on exactly one connection**: `get_agent_engine()`
  (`agentData` schema). Its cache tables are managed by the Bloomberg and
  CloudQuant wrappers — use the wrapper, never write to them by hand. Every
  other engine is read-only and will reject writes at the session level.
- **Every query is date-bounded.** Tables marked `huge` in
  database_reference are symbol-bounded too.
- **Pace external API pulls.** ThetaData especially: ≥ 0.1s between
  requests, never a tight loop.

## Workflow

1. Restate the request as a dataset spec: columns, universe, window, grain,
   output format. Confirm only if genuinely ambiguous.
2. Check coverage BEFORE the full pull — row counts / non-null fractions /
   date range for the window (a cheap COUNT or a one-day sample).
3. Pull via `vbam_utilities`. Drop to bounded SQL only where no helper exists.
4. Validate: row count ≈ trading days × symbols, no unexpected duplicates,
   timestamps US/Eastern, spot-check one value against a known source.
5. Deliver per report_patterns.

## Self-tests (verify an environment, or see working example code)

Every provider module runs a live self-test that doubles as usage:
`python -m vbam_utilities.<module>` for `vbam_db`, `calendar`, `thetadata`,
`cloudquant`, `bloomberg` (needs a Terminal). `python -m
vbam_utilities.excel_pivots` builds a full worked example into an .xlsx with a
native pivot. `python -m vbam_utilities.chat` posts a REAL message to team
chat — run it deliberately.

## Extending this skill

When a new data source comes online:
1. Add a row to [references/catalog.md](references/catalog.md) (template at
   the top of that file). Even a stub row with an Owner beats a blind spot.
2. If it's a VBAM table: add a `TableInfo` to `vbam_utilities/schemas.py`,
   a `GRANT SELECT` in `sql/create_vbam_team_ro_user.sql`, and a row in
   `references/database_reference.md`.
3. If it needs a wrapper: add the module, resolve every credential through
   `config.py` (no hardcoded personal paths), include a `python -m` self-test.
4. Add a routing-table row above.

## Hard rules

- Read-only everywhere except `agentData`. If a request needs writing to a
  market-data table, refuse and point at the MarketDataLoaders repo, where the
  pipelines live.
- Never use `t_ice_daily_bars` (unadjusted) for anything involving delisted
  names — it is missing ~30-90 delisted symbols/day in 2024-2025.
- Never present adjusted prices as traded prices.
- Output files go under `outputs/` only. Never commit `.env` or credentials.
- If data looks missing, check the T+2 lag and the loaded-session windows
  before declaring a gap.
- Never create additional skill files in this repo. Project-specific docs go
  in `projects/<name>/README.md`; `.claude/skills/` contains only data-oracle.
