# Notebook Skeleton (reference)

Behavioral rules (caching pattern, `#%%` markers, `display()` over `print()`, no `if __name__`, sanity-check samples) live in SKILL.md. This file holds the verbose templates / examples.

## Full skeleton (copy-paste starting point)

```python
#%% Imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys
from IPython.display import display

sys.path.insert(0, 'd:/PycharmProjects/utils/')
from calendar_utils import *
from spdr_rock_functions import *

# Set display options (adjust max_columns based on your data + 5)
pd.set_option('display.max_columns', 50)

#%% Reimport helpers (run after making changes to helper files)
import importlib
import calendar_utils
importlib.reload(calendar_utils)
from calendar_utils import *

#%% Global Variables
SYMBOL = 'SPY'
START_DATE = '2024-01-01'
END_DATE = '2024-12-31'
LOOKBACK_DAYS = 20

#%% Clear caches (run this cell to force re-pull of data)
def clear_caches():
    """Clear all cached data to force fresh pull on next run."""
    cache_vars = ['price_data']
    cleared = []
    for var in cache_vars:
        if var in globals():
            del globals()[var]
            cleared.append(var)
    if cleared:
        print(f"Cleared caches: {', '.join(cleared)}")
    else:
        print("No caches to clear")

# Uncomment to clear: clear_caches()

#%% Cache: Historical price data
if 'price_data' not in dir():
    price_data = get_historical_prices(SYMBOL, START_DATE, END_DATE)

print("Sanity check - sample of price data:")
display(price_data.sample(5))

#%% Helper Functions
def calculate_returns(prices):
    """Calculate daily returns from price series."""
    return prices.pct_change().dropna()

#%% Data Processing
returns = calculate_returns(price_data['close'])
rolling_vol = returns.rolling(LOOKBACK_DAYS).std() * np.sqrt(252)

#%% Visualization
fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor('#f5f5f5')
ax.set_facecolor('#f5f5f5')

ax.plot(rolling_vol.index, rolling_vol.values, linewidth=1.5)
ax.set_title(f'{SYMBOL} {LOOKBACK_DAYS}-Day Rolling Volatility | N={len(rolling_vol):,}')
ax.set_ylabel('Annualized Volatility')
ax.grid(True, alpha=0.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.show()
```

## File-structure cell order

```python
#%% Imports
#%% Reimport helpers (run this cell to reload after changes)
#%% Global Variables & Configuration
#%% Clear caches (run this cell to force re-pull of data)
#%% Cache Setup
#%% Helper Functions
#%% Data Loading / Preparation
#%% Data Processing
#%% Backtesting / iterating (as necessary)
#%% Visualization / Output
```

## clear_caches() template (full version)

```python
#%% Clear caches (run this cell to force re-pull of data)
def clear_caches():
    """Clear all cached data to force fresh pull on next run."""
    cache_vars = ['price_data', 'other_cached_var']  # List all cached variable names
    cleared = []
    for var in cache_vars:
        if var in globals():
            del globals()[var]
            cleared.append(var)
    if cleared:
        print(f"Cleared caches: {', '.join(cleared)}")
    else:
        print("No caches to clear")

# Uncomment to clear: clear_caches()
```

- Update `cache_vars` to include all cached variable names in the notebook.
- Use `globals()` to check/delete (not `dir()` which only sees local scope).
- Provide feedback on what was cleared.

## Sanity-check sample pattern

```python
# After merging data sources
print("Sanity check - merged data:")
display(merged_df.sample(5))

# After PnL calculation
print("Sanity check - PnL results:")
display(results_df.sample(5))
```
