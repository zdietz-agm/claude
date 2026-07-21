---
name: analysis-notebook
description: Scaffold interactive Python analysis as a .py file with cell markers, cached data loads guarded by "if var not in dir()", a clear_caches() cell, and display() sanity checks. Use when the user asks to create a notebook, an interactive analysis, or a Python script to test ideas on data.
---

# Interactive Analysis Notebooks

When asked to create a "notebook" / interactive analysis / test ideas in Python, make a `.py` file with `#%%` cell markers (NOT a `.ipynb`).

## Cell-marker order

Imports -> Reimport helpers -> Globals -> Clear caches -> Cache cells -> Helpers -> Data load -> Processing -> Backtesting -> Visualization.

## Caching pattern

Wrap every expensive operation (Bloomberg pulls, SQL queries, OPRA panels, SpiderRock queries) in:

```python
if 'var_name' not in dir():
    var_name = expensive_load(...)
```

- Label cache cells `#%% Cache: [description]`.
- Never overwrite cached data on rerun.

## clear_caches() function (always include, own cell)

- Uses `globals()`, not `dir()`, to actually delete (dir() only sees local scope).
- List every cached variable name in `cache_vars`.
- Print feedback on what was cleared.

## Display rules

- `display()` not `print()` for DataFrames.
- Add `display(df.sample(5))` sanity check after every merge / PnL calc / major transform.
- `pd.set_option('display.max_columns', N)` with N = widest-df column count + 5.

## Code style

- **NEVER use `if __name__ == '__main__':`** -- indentation breaks Jupyter interactive execution.
- Keep all code at module level, separated by `#%%`.
- Concise inline comments; skip when variable names are self-explanatory.

## Templates

Copy-paste-ready full skeleton, complete `clear_caches()` template, and sanity-check examples: [references/skeleton.md](references/skeleton.md).

## Requirements

Typical deps pinned in [requirements.txt](requirements.txt) (pandas, numpy, matplotlib). Domain libraries (calendar_utils, spdr_rock_functions, etc.) come from `D:/PycharmProjects/utils/` via `sys.path.insert`.
