---
name: spiderrock-data
description: Pull SpiderRock options and volatility data -- live options/IV surfaces via spdr_rock_functions, historical option quotes and implied vol via the liberator API (last ~2 years, env-var auth setup required), and older history via the spdr_historical AWS S3 archive backfill. Use when the user asks for options data, implied volatility, IV surfaces, historic option quotes at any age, or hits liberator auth errors.
---

# SpiderRock Data

Two access paths, depending on live vs historical. (For choosing between data providers generally, see the `data-sources` skill.)

## Live options / volatility: spdr_rock_functions

```python
import sys
sys.path.insert(0, 'd:/PycharmProjects/utils/')
from spdr_rock_functions import *
```

Use for live SpiderRock options quotes and IV surface data. Function-call interface; real-time.

## Historical options / IV: liberator API

The user frequently pulls historical options and implied volatility data via liberator in `D:/PycharmProjects/spdr_liberator/`. `helpers_improved.py` in that directory has many useful functions for pulling historic options and IV data.

### CRITICAL: liberator auth setup

The `liberator` module requires `liberator.pfx` and `liberator.json` (auth credentials) to be in the working directory by default. When using liberator from a script **outside** `D:/PycharmProjects/spdr_liberator/`, you **must set environment variables BEFORE importing liberator**, because `liberator.py` evaluates `os.getenv('LIBERATOR_USER')` and `os.getenv('LIBERATOR_TOKEN')` at module-load time (in `_query_defaults`). Setting `liberator.auth` after import does NOT update the cached credentials.

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

### Failure signatures

- `No user arg provided` -> env vars were not set before import. Restart the process/kernel and set them first.
- `FileNotFoundError: PFX file not found` -> `liberator.pfx` path not set.

### CRITICAL: `liberator` name collision with CloudQuant

`D:/PycharmProjects/utils/liberator.py` is a DIFFERENT module (CloudQuant's client, used by `cq_helpers`) that shares the `liberator` name. `import liberator` resolves by sys.path order, so having `utils` on the path can silently import the wrong client (symptoms: `No user arg provided`, PFX/endpoint errors). Never mix SpiderRock liberator and cq_helpers pulls in one Python process; when debugging, check `liberator.__file__` first. Full details: `data-sources` skill, CloudQuant section.

## Data older than ~2 years: spdr_historical (AWS S3 archive)

Liberator only retains roughly the last 2 years. For older historical options / IV, use **`D:/PycharmProjects/spdr_historical/`** -- it pulls SpiderRock's raw archive from their AWS S3 bucket (`srdatasetarchivehist`, via boto3; creds are hardcoded in the scripts), transforms it, and upserts into `optionsResearch.t_historical_options_snaps` on VBAM dev.

Key scripts:
- `backfill_spxw_historical.py` -- main SPXW backfill (full history from Sept 2016; `SMALL_RUN` flag for testing)
- `backfill_spxw_historical_specific_dates.py` -- targeted date backfills
- `backfill_ndxp_rutw_check_and_pull.py` -- NDXP / RUTW variant
- `pull_data_spx_sql_fast.py` -- fast SQL-side pulls from the cached table (used by eod_option_algos/update_data.py)

## Historical snapshots already in SQL

Both sources (liberator for recent data, spdr_historical S3 backfill for older) land in `optionsResearch.t_historical_options_snaps` on VBAM dev (`trade_date`, `exp`, `symbol`, `strike`, `cp`, `bidPrc`, `askPrc`, plus Greeks/IV). **Check there FIRST before pulling from either source** -- the date range you need may already be cached; full table details are in the `data-sources` skill.

## Reload pattern (after editing helper files mid-session)

```python
import importlib
import spdr_rock_functions
importlib.reload(spdr_rock_functions)
from spdr_rock_functions import *
```

## Setup notes

- `liberator` is SpiderRock-distributed (lives in `D:/PycharmProjects/spdr_liberator/`), not pip-installable; credentials (`liberator.json` / `liberator.pfx`) are per-user.
- Third-party deps pinned in [requirements.txt](requirements.txt).
