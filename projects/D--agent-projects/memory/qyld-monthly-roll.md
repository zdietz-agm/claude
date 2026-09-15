---
name: qyld-monthly-roll
description: QYLD strike analysis is touched monthly around each serial expiry; next expected ~2026-09-17 when QYLD rolls to the Sept strike
metadata: 
  node_type: memory
  type: project
  originSessionId: d55422a6-b307-4681-9412-a60688d5abe2
  modified: 2026-08-21T16:11:05.203Z
---

The QYLD NDX flag analysis (`D:/agent_projects/qyld/`) gets updated once a month around the serial expiry: Zach supplies the new QYLD call strike (format "NDX US MM/DD/YY C##### Index"), it gets appended to `LISTED` in `qyld_analysis.py` (parked as a comment until the expiry's prior-day data exists), then the script is rerun end-to-end (`python qyld_analysis.py` works standalone) and the Excel lands in Downloads. Next expected request: ~2026-09-17, when QYLD rolls into the 2026-09-18 serial. As of 2026-08-21 the last entry is ("2026-08-21", 28550). Process details and gotchas (Thursday expiries valid, TWAP columns required) are in the directory's README.
