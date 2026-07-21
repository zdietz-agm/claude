---
name: Never suppress call outputs
description: Never redirect or suppress stdout/stderr from library calls
type: feedback
---

Never suppress a library call's outputs (e.g. with redirect_stdout or similar). Let them print naturally.

**Why:** The user wants full visibility into what's happening. Suppressing output hides potential issues and makes debugging harder.

**How to apply:** If a library is noisy, leave it as-is. Do not wrap calls in redirect_stdout, contextlib suppression, or /dev/null redirects.
