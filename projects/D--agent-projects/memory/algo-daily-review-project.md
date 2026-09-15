---
name: algo-daily-review-project
description: Automated daily EOD algo review (built 8/19/2026) -- how it runs and the two-week correction loop Zach planned
metadata: 
  node_type: memory
  type: project
  originSessionId: 8623b7c8-b4ff-4e32-b7c4-642d72f30a5e
  modified: 2026-08-19T18:46:24.464Z
---

Automated replacement for Zach's manual daily EOD algo review, built 2026-08-19. Claude
scheduled task `algo-review` (weekdays 8:25 ET + jitter) reads a deterministic pack from
`D:/agent_projects/algo_daily_review/build_review_pack.py`, writes
`D:/PycharmProjects/scratch/algos/automated_algo_reviews/<MM_DD_YYYY>.txt` for the prior
trade date, and sends it to Zach's Google Chat.

**The plan Zach stated:** for the first couple of weeks he reads each automated review and
adds edits -- more concise, things missed, things misinterpreted. Those corrections go into
`D:/agent_projects/algo_daily_review/review_corrections.txt`, which the task reads every run
and which overrides both REVIEW_GUIDE.txt and the task prompt. When he corrects a review in
chat, append the correction to that file (keep his wording) so the next run inherits it.
First automated review: 2026-08-20, covering trade date 2026-08-19.

Seed examples he wrote by hand: `automated_algo_reviews/08_17_2026.txt` and `08_18_2026.txt`.
Six questions the review must answer, project layout, and known gaps are in
`D:/agent_projects/algo_daily_review/README.txt`.

Related: [[spiderrock-v8-migration]] (the V8 size-ratio check in the digest exists because
350pm_script_v8 traded 100% instead of 10% size on 8/18), [[w2-nbbo-anchor-todo]] (the
sprc-vs-NBBO section feeds that open question daily).
