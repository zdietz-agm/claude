---
name: w2-nbbo-anchor-todo
description: "Open to-do (8/5/2026) - W2 NBBO-anchor fix for 350PM/355PM spread sales, proposed but deliberately NOT implemented"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9b123413-a3a0-4b05-9a8f-ba4474cb0b9e
  modified: 2026-08-06T21:53:30.579Z
---

Open to-do as of 2026-08-05: the "W2 NBBO-anchor" fix for spread SALES in 350PM/355PM
(orchestrate_batched_send path in D:/PycharmProjects/scratch/algos/spdr_rock_order_functions.py)
is proposed and user-reviewed but deliberately NOT implemented.

**Why:** sprc-anchored W1/W2 limits fail when SR's surface dislocates from the NBBO in fast
post-imbalance markets. Evidence: 8/4/2026 (7760C sprc 1.667 vs real NBBO ~0.95-1.10 -> ALL call
spreads 0-filled, 260+ contracts) and 7/23/2026 (7380P, W2 refresh moved sprc UP 1.108->1.178
while market collapsed -> all put spreads 0-filled). 7/16/2026 = opposite mode (sprc cheap ->
filled instantly ~20c under target).

**Proposal (reviewed by user):** keep W1 as-is. At W2 refresh, compute spread-level dislocation
D = (sprc - clamp(sprc, obid, oask)) short leg minus long leg. If |D| > ~$0.05: rich side ->
limit2 = (short.obid - long.oask) - 1 tick, floored at max(min_price, 60% x prep price); cheap
side -> lift credit floor up to NBBO. Mechanically: widen takesurfPrcoffset to ET2+|D| so the
Prc limit binds (confirm with SR support).

**Known flaw:** SR's own obid/oask lag the tape ~2-3s in fast markets (proven vs OPRA on both
incident days), so an SR-live NBBO anchor may not have fixed 8/4. Blockers before implementing:
1. SR quote latency in fast markets -- ask Saurav (SpiderRock support); he also owes answers on
   the Market limit type, "market order with hard max price", and v8 collar adjustability.
2. Optional: month-long srPrc-vs-bid/ask study from optionsResearch.t_historical_options_snaps
   at ~15:50 to size how often the surface is outside the NBBO.

Diagnostic prints already live (8/5): [quotes W1/W2] lines with sprc, NBBO, and row_ts on every
wave fire -- future incidents are measurable from logs alone.
