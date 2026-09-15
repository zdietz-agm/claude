---
name: feedback-gated-link-stop-and-ask
description: "When a user-shared link is auth/login-gated and can't be fetched, STOP and ask the user to paste the contents"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 68c48a6e-de71-4a6c-8928-0ceb9992aa81
  modified: 2026-07-23T16:34:51.192Z
---

When the user shares a link to read and it is gated (login/auth redirect, private Confluence/Atlassian wiki, etc.) so the fetch fails, **stop all tasks and clearly state you need the user to share the contents** -- do not work around it, guess, or proceed on partial/assumed content.

**Why:** the user has access to these gated resources and will paste them; proceeding without the real contents risks acting on wrong assumptions (e.g. guessing an enum's values).

**How to apply:** attempt the fetch once; if it returns an auth/login redirect or otherwise can't read the real page, halt and say plainly "that link is gated -- please paste its contents" before continuing the task. (Example: the SpiderRock V7 Confluence appendix in [[spiderrock-enum-and-cancel-terminal]] was login-gated; the right move was to ask the user to paste it, which gave the authoritative SpdrOrderStatus enum.)
