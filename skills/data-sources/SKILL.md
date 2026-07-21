---
name: data-sources
description: Directory of all market data sources and which to use for what -- Bloomberg (xbbg), SpiderRock (live + liberator historical), ThetaData OPRA quotes, cq_helpers intraday prices, VBAM SQL tables (imbalances, ETF NAV, price/index snaps, options), algo trade logs (algo_trade_log + raw script logs), and pre-pulled local CSVs. Use FIRST whenever deciding where to pull any market, imbalance, options, NAV, or price data, and when investigating prod algo trades or fills, before writing SQL or a data pull.
---

# Data Sources (router)

This skill is the expert on WHERE to get data. Pull mechanics live in the provider skills: `bloomberg-data` (xbbg) and `spiderrock-data` (spdr_rock_functions + liberator). Load those for how-to once the source is chosen.

Note that the user has access to many data providers. If data is needed that is not catalouged in this skill, prompt the user and ask about adding it to this skill.

## Routing table: task -> source

| Need | Use | Interface / skill |
|---|---|---|
| Open/close prices, daily history, Bloomberg fields, dividends | Bloomberg | `xbbg` -- see `bloomberg-data` skill |
| Live options quotes / live IV surface | SpiderRock | `spdr_rock_functions` -- see `spiderrock-data` skill |
| Historical options / IV | Check `optionsResearch.t_historical_options_snaps` first (both sources cache there); else SpiderRock liberator (last ~2 years) or `spdr_historical` AWS S3 backfill (older than ~2 years) | see `spiderrock-data` skill |
| Historical OPRA option quotes (1s bid/ask/size), per-tick index series (SPX/NDX/VIX) | ThetaData | `thetadata_helpers` (below) |
| Intraday historic prices (snaps, not bars) | CloudQuant | `cq_helpers` (T+1; see CloudQuant section below) |
| Live/historic closing imbalances, intraday price snaps, index level snaps | VBAM SQL | [references/alpine_tables.md](references/alpine_tables.md) |
| Official ETF NAV (return-to-NAV calcs) | VBAM `compositions.t_compositions_ETFDailyBasketHeaders` | NAV SQL template in [references/alpine_tables.md](references/alpine_tables.md) |
| Pre-pulled daily research data (imbalances, market_ratio, RSI3, VIX snaps, realized vol, 0DTE panels) | Local CSVs | [references/local_csvs.md](references/local_csvs.md) |
| Algo trade logs: per-algo attempts/fills + factor snapshot | VBAM dev `optionsResearch.algo_trade_log` | see Trade logs section below + [references/alpine_tables.md](references/alpine_tables.md) |
| Raw prod script run logs (full stdout, per script per day) | Local text files | `D:/PycharmProjects/scratch/algos/logs/<YYYY-MM-DD>_<script_name>.txt` |
| Dates / trading calendar | `calendar_utils` | `from calendar_utils import *` (`SERIALS`, `FEDS`, `is_month_end`, `month_ends`, `trading_range`, `next_trade_day`, `x_days_ago`) |

Utils library path: `d:/PycharmProjects/utils/` (add via `sys.path.insert(0, ...)`).

## ThetaData

`thetadata_helpers` (`from thetadata_helpers import *`) -- historical OPRA option quotes (bid/ask/size, 1s snapshots) and index price series (per-exchange-tick SPX/NDX/VIX/etc.). Two generations wrapped side by side; **prefer v3 for new code**:

- **v3 (preferred)** -- official `thetadata` pip library, gRPC direct to Theta servers. **NO local terminal needed.** Creds: `THETADATA_API_KEY` env var or `thetadata_creds.json` next to the helpers file. Functions carry a `_v3` suffix: `check_v3_connection`, `list_expirations_v3`, `list_strikes_v3`, `get_bulk_chain_v3`, `get_option_quotes_v3`, `get_index_price_v3`.
- **v2 (legacy)** -- local ThetaTerminal HTTP API; requires the terminal running on `127.0.0.1:25510` (`java -jar ThetaTerminal.jar <user> <password>`). Still used by older code. Raw columns: `ms_of_day`, `bid`, `ask`, `bid_size`, `ask_size`.

Quote helpers in BOTH generations return the canonical `optionsResearch.t_opra_quotes` schema (`symbol, trade_date, exp, strike, cp, timestmp, bidPrc, askPrc, bidSize, askSize`). Index price pulls are cached to `optionsResearch.t_index_snaps_td` and options quotes to `optionsResearch.t_opra_quotes` on VBAM dev.

## CloudQuant (cq_helpers)

`cq_helpers` (`from cq_helpers import *`, in `D:/PycharmProjects/utils/`) -- T+1 intraday historic prices via CloudQuant's liberator API. Key functions: `get_close_prices(symbols, start, end)` (official closes), `get_prices(symbol, datetime)` (trade price nearest a given intraday timestamp; backed by a local pickle cache at `D:/PycharmProjects/utils/intraday_prices.pkl`). Data sets are ICE XNYS trade quotes. Good for before 2pm EST / any-intraday-time prices where the VBAM snap tables have no coverage.

### CRITICAL: CloudQuant vs SpiderRock `liberator` module conflict

There are TWO different local files named `liberator.py` -- they are unrelated clients that share a module name, and there is no installed `liberator` pip package (resolution is purely sys.path order):

- `D:/PycharmProjects/utils/liberator.py` -- **CloudQuant** client. Used by `cq_helpers`; pfx at `D:/PycharmProjects/utils/liberator.pfx`, creds passed per-query (plus `cq_liberator.json`).
- `D:/PycharmProjects/spdr_liberator/liberator.py` -- **SpiderRock** Data Liberator client. pfx/json in `D:/PycharmProjects/spdr_liberator/`, url `https://getdata.spiderrock.net`, creds read from `LIBERATOR_USER`/`LIBERATOR_TOKEN` env vars at import time.

Failure modes:
- `import liberator` grabs whichever directory appears first on `sys.path` -- e.g. inserting `D:/PycharmProjects/utils/` (for calendar_utils/cq_helpers) and then importing liberator for SpiderRock work silently gets the CloudQuant client (or vice versa). Symptoms: `No user arg provided`, PFX errors, wrong endpoint, queries that return nothing.
- Python caches the first import in `sys.modules`, and both usages configure module-level globals (`liberator.pfx`, `liberator.auth`, `liberator.url`) -- so even with correct path order, mixing CloudQuant and SpiderRock pulls in ONE Python session/kernel means the second consumer inherits or overwrites the first's config.

Rules:
- **Do not mix cq_helpers and SpiderRock liberator pulls in the same Python process/kernel.** Use separate processes.
- When either client misbehaves, check `liberator.__file__` FIRST to confirm which file actually got imported.
- Keep only the intended directory on sys.path before the import.

## Trade logs

- **`optionsResearch.algo_trade_log`** (VBAM dev) -- one row per 2-leg vertical spread attempt per algo from the prod EOD scripts (350PM/355PM etc.). Logs both credit and debit spreads (`direction` = "Sell" for spread sales, "Buy" for debit trades like hacker); the row shape assumes exactly one short leg + one long leg. Populated by `D:/PycharmProjects/scratch/algos/algo_trade_logger.py` (waits ~60s post-trade, looks up SR fills in `srtrade.msgsrmlegbrkrstate` by grouping_code, then UPSERTs). **PK:** `trade_date, script_name, algo_name, symbol, cp`. **Cols:** strikes/direction (`short_strike`, `long_strike`, `direction`), execution (`size_attempted`, `size_filled`, `price_attempted`, `avg_fill_price`, wave1/wave2 limit/qty/time), and the factor snapshot at trade time (`spx_price`, `vix`, `atm_vol`, `market_ratio`, `rsi`, `high_low_ratio`, `realized_3m_chg`, `imbal_340/350/355`, `qqq_imbal`, `paired_imbal`, edge targets).
- **`D:/PycharmProjects/scratch/algos/logs/`** -- raw per-run stdout logs, one file per prod script per day: `<YYYY-MM-DD>_<script_name>.txt` (e.g. `2026-07-17_350pm_script.txt`, `..._355pm_script.txt`, `..._btic_and_imbal_script.txt`). Authoritative record of what a script actually did intraday (fills, retries, errors) -- match the script name suffix carefully; reading the wrong script's logfile has caused false conclusions before.

## Live imbalance helper wrappers (prefer over raw SQL -- LIVE pulls only)

`D:/PycharmProjects/scratch/algos/helpers.py`: `get_340_imbal`, `get_350_imbal`, `get_355_imbal`, `get_recreated_paired_imbal`, `get_qqq_net_imbal`, `get_fast_imbal`. All retry up to 7x with timeouts; return `NO_IMBAL_VAL` on failure; accept `is_test=True, test_imbal=<num>` for dry runs.

**Scope: real-time / live-trading pulls of TODAY's imbalance only.** Do NOT use these for historical backtesting -- historical work pulls from the T+1 sources instead (`auctionResearch.t_report_consolidated_imbalances`, the pre-pulled `spy_imbalances_<date>.csv`, other local CSVs in [references/local_csvs.md](references/local_csvs.md)), etc.

## Hosts

- **VBAM prod**: `alpine-vbam-prod.c7wvpkbyvjzb.us-east-1.rds.amazonaws.com`
- **VBAM dev**: `alpine-vbam-dev.c7wvpkbyvjzb.us-east-1.rds.amazonaws.com` (the `optionsResearch` tables)

Full table-by-table catalog with columns and latency (real-time vs T+1): [references/alpine_tables.md](references/alpine_tables.md).
Local CSV catalog with schemas: [references/local_csvs.md](references/local_csvs.md).

## Adding a new provider

When a new data provider comes online, add a row to the routing table above and a section (or references entry) describing tables/latency/interface -- this skill stays the single source of truth for "where do I get X".
