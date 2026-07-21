---
name: excel-deliverables
description: Export analysis results and backtests to formatted .xlsx workbooks and build native Excel PivotTables with heatmap color scales. Use when the user asks to save or download data to Excel, export a backtest, add a pivot table to a workbook, or apply a heatmap in a spreadsheet.
---

# Excel Deliverables

Two workflows: (1) exporting data to a formatted .xlsx, (2) adding native Excel PivotTables to a workbook.

## Excel data export

When asked to "download data" / save results / save a backtest: save to **.xlsx** (not csv) in the user's Downloads folder with filename `<name>_YYYYMMDD_HHMM.xlsx`. Resolve Downloads portably:

```python
from pathlib import Path
downloads = Path.home() / 'Downloads'
```

**Sheet structure (multi-backtest):** Sheet 1 = `"All"` (combined, with a `strategy` or `backtest` column); additional sheets one per backtest, named descriptively.

**Required Excel features:** AutoFilter on header row, freeze leftmost columns (typically `trade_date`/`time`), auto-fit column width.

**Column ordering:** `pnl` or `daily_pnl` is the first column after the frozen leftmost columns.

**Analysis-relevant columns (only include these):** `trade_date`, `time`, `symbol`, `pnl`, `expiry`, `strike`, `cp`, spread strikes (`short_strike`/`long_strike` or put/call variants), pnl breakdown (`gamma_pnl`, `vega_pnl`, `theta_pnl`, `opt_pnl`), Greeks (`delta`, `gamma`, `vega`, `theta`, `iv`), `underlying_price`, `entry_price`, `exit_price`.

**Formatting:**

| Column type | Format |
|---|---|
| Dollar values (pnl, price, premium) | Accounting, 2dp, red negative (`_($* #,##0.00_);[Red]_($* (#,##0.00)`) |
| Greeks (delta, gamma, vega, theta, iv) | Round to 3 decimals |
| Long decimals (payout, ratio) | Round to 3 decimals |
| Percentages | 2 decimals with `%` |

Full copy-paste `export_to_excel()` template and column lists: [references/export_template.md](references/export_template.md).

## Native Excel PivotTables

When the user asks for a pivot table in Excel, **always create a native Excel PivotTable** (not static cells that look like a pivot). Only use static cells if the user explicitly says so.

**Hard rules:**
- **NEVER run `win32com` / COM automation in-process in Jupyter** -- it will crash the kernel. Always run it via a **subprocess**.
- Use the helper: `from excel_pivot_helper import create_pivots_subprocess` (lives in `D:/PycharmProjects/utils/excel_pivot_helper.py`, which is on the standard utils path).
- Pattern: write data sheets with `openpyxl`, close the file, then call the helper.
- "Heatmap" = 3-point conditional color scale, -3 red / 0 white / 3 green (defined in the helper).

COM internals, Excel constants, `create_pivots_subprocess` signature, and heatmap code: [references/pivot_internals.md](references/pivot_internals.md).

**Reference implementations on disk:**
- `D:/agent_projects/month_end/create_month_end_excel.py` (basic usage)
- `D:/agent_projects/sp500_adds/candidates_buying_vol.py` (multi-row-field pivot)

## Environment notes

- Native pivots require Windows with Excel installed (COM automation). The export workflow works anywhere openpyxl does.
- Third-party deps are pinned in [requirements.txt](requirements.txt) (pandas, openpyxl, pywin32). Install manually if missing.
