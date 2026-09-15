---
name: spiderrock-enum-and-cancel-terminal
description: "SpiderRock SpdrCloseReason / order-status enum doc links (V7 + V8) and the \"order is done\" rule for cancel-then-resend"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 68c48a6e-de71-4a6c-8928-0ceb9992aa81
  modified: 2026-07-23T16:34:38.806Z
---

SpiderRock enum documentation:
- **V8 SpdrCloseReason enum** (public): https://docs.spiderrockconnect.com/docs/next/MessageSchemas/Schema/Enums/SpdrCloseReason/ -- 33 values (0-32): None, Cancelled, Filled, Replaced, Expired, Limit, System, LegReject, DoneForDay, IOCExpire, UserCxl, NoProgress, TooManyRej, ReplReject, AlgoClose, Restart, InvldParentLimit, FilledRepl, ForceClose, DmaReject, DmaExpire, DmaBrkrCxl, ReviewReject, MarketState, AlgoReject, ReviewTimeout, ChildReject, ChildCancel, ReviewClose, UPrcRange, LegBrkrClosed, ExchRisk, CrossFailed.
- **V7 appendix** (Confluence, LOGIN-GATED -- open in browser, not fetchable by tools): https://spiderrockplatform.atlassian.net/wiki/spaces/CD/pages/460128273/Appendix+A+Enumerated+Database+Types+Trade
- **msgSRMLegBrkrState** message doc (Confluence, login-gated): https://spiderrockplatform.atlassian.net/wiki/spaces/CD/pages/359793106/msgSRMLegBrkrState

**`SpdrOrderStatus` enum (authoritative, from V7 appendix)** -- the enum for `msgsrmlegbrkrstate.spdrOrderStatus`, exactly 6 values:
`PendNew, New, PendClose, Closed, Rejected, SendReject`.
(Do NOT confuse with the generic online "OrderStatus" enum New/PendNew/PendRpl/PendCxl/Working/Cancelled/Replaced/Filled/Expired/Terminated/Rejected -- that is a different field.)

Cancel-then-resend terminal rule (per SR support, Christie Uvodich, 2026-07-23) -- used by the `batched_fill_check_and_cancel` oversell fix in `D:/PycharmProjects/scratch/algos/spdr_rock_order_functions.py`:
- Check the **`spdrOrderStatus`** field. To be 100% sure NO more fills are coming after you cancel a ticket, wait for it to reach **`Closed`**.
- **Terminal / safe to read final fill + resize** = `{Closed, Rejected, SendReject}` (Closed = done; Rejected/SendReject = order never worked, 0 fills). For Rejected/SendReject the remainder should still be re-sent (they didn't fill), so they must count as terminal, not "still working."
- **NOT terminal (order may still fill)** = `{PendNew, New, PendClose}`. `PendClose` = SR is trying to cancel but waiting on the broker -- fills still possible; orders only stick in PendClose on a problem (then contact the broker).
- Related field `spdrBrokerStatus` enum (V7): None/Updating/Active/Closing/Closed/Rejected -- but per SR, `spdrOrderStatus` is the field to gate on.
