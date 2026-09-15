---
name: algos-venv-migration
description: "Prod EOD algo launchers + test harness now run on scratch/.venv, NOT global Python (Aug 2026 initiative)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3fd77820-2f9e-4251-b6cc-8ab04a314a88
  modified: 2026-08-06T19:10:13.025Z
---

As of 2026-08-06, all four prod launchers in D:/PycharmProjects/scratch/algos (run_algos.sh, run_algos_fed.sh, run_algos_monthend.sh, run_algos_no_340.sh) and test_run_algos.sh launch via D:/PycharmProjects/scratch/.venv/Scripts/python.exe, not the global install. This supersedes the global CLAUDE.md note that everything runs on global Python -- for scratch/algos work, target the venv.

**Why:** user initiative to move algos off global Python. Venv is isolated (include-system-site-packages=false) with package versions matching global at migration time.

**How to apply:**
- Never `source scratch/.venv/Scripts/activate` blindly after a machine migration -- activate scripts hardcode VIRTUAL_ENV at creation. This venv was created at C:/Users/zdietz/Desktop/PycharmProjects and silently fell through to global Python until the activate/activate.bat/activate.fish files were byte-patched (2026-08-06). The launchers instead export VIRTUAL_ENV/PATH themselves and invoke $PYTHON explicitly, with a bare-python-resolves-to-venv guard.
- Most .exe console shims in the venv's Scripts/ still embed the dead Desktop path (only pip's were regenerated). Use `python.exe -m <tool>`, not the shims. Regenerate per-package with `pip install --force-reinstall --no-deps <pkg>==<same version>` if needed.
- pyvenv.cfg line 5 (`command = ...Desktop...`) intentionally left stale; Python never reads it.
