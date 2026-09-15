---
name: spiderrock-locate-upload
description: How to bulk-upload stock locates into SpiderRock via SRSE (v8 works; v7 SQL writes land but do NOT show in the SV GUI -- Zach does v7 manually)
metadata: 
  node_type: memory
  type: project
  originSessionId: 4ce018fa-1661-453f-8a41-2d28642b61f8
  modified: 2026-08-31T12:51:35.991Z
---

Bulk stock-locate upload into SpiderRock (no SV GUI multi-paste exists; SR UK support (James, 2026-08-31) gave the SRSE query):

```sql
REPLACE INTO SRControl.msgawaystocklocategateway
  (ticker_at, ticker_ts, ticker_tk, coreClientFirm, locateFirm, locatePool, locateQuan)
VALUES ('EQT', 'NMS', '<TICKER>', 'AGM', 'BAML', 'AGM', <QTY>);
```

Working script: `D:/agent_projects/adhoc/upload_stock_locates.py` -- edit the LOCATES list and rerun.

Key gotchas (all verified 2026-08-31):
- **Column name differs by env**: v8 = `coreClientFirm`, v7 = `clientFirm`. Everything else identical.
- **`agm.zdietz` cannot CONNECT with `srcontrol` as default schema** (1044) -- connect to `sranalytics` and use the fully qualified table name.
- Write permission (INSERT/DELETE on `srcontrol.msgawaystocklocategateway`) had to be granted by SR support; initial attempts got 1142 on both envs until they added it.
- Verify with `SELECT * FROM srcontrol.msgavailablestocklocates` (shows locateQuan / locateQuanUsed / availableLocateQuan / engineName).

- **locateFirm differs by env**: v7 = `'ML'`, v8 = `'BAML'`. Root cause (per Zach, 2026-08-31) of the initial v7 confusion: rows written with locateFirm='BAML' landed in `msgavailablestocklocates` but did NOT show in the SV GUI -- the SV/engines on v7 expect 'ML'. Zach uploaded the 8/31 v7 batch manually via SV; the script now uses ML on v7 / BAML on v8 but the v7 path is untested end-to-end -- verify in SV after the next programmatic v7 run.

Hosts (from [[spiderrock-v8-migration]] / spdr_rock_functions.py): v7 = 198.102.4.63:3307 (fallbacks .55/.56), v8 = 192.81.231.66:3700, same creds.
