---
name: feedback-concise-comments
description: "User wants concise, to-the-point code comments -- flagged my tendency to write long comments"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: db0f235d-ee82-4238-9c61-d36acea0c951
  modified: 2026-07-28T19:35:45.293Z
---

While porting utils to vbam_utilities (2026-07-28), user said: "i have noticed that you have a tendency to write long comments. try to make comments concise and to the point for easy human readability."

**Why:** Long explanatory comments hurt human readability of code files.

**How to apply:** Keep comments short; state the constraint or gotcha in one line. Docstrings 1-2 lines per the existing [[function-documentation]] rule in CLAUDE.md. Don't narrate history or justify changes in comments.
