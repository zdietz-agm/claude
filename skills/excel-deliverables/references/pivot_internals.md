# Excel Native PivotTables -- COM internals

Behavioral rules live in SKILL.md (native pivot always, subprocess only, use the helper). This file holds the COM internals, constants, and code examples.

## Architecture: subprocess isolation

- **NEVER run `win32com` / COM automation in-process in Jupyter** -- it will crash the kernel. Always run it in a **subprocess**.
- Use the helper: `from excel_pivot_helper import create_pivots_subprocess` (in `D:/PycharmProjects/utils/`).
- The main notebook writes data sheets with `openpyxl`, closes the file, then the helper reopens it with `win32com` in a subprocess to add pivot tables.

## win32com essentials

- **`DispatchEx`** (not `Dispatch`): `win32com.client.DispatchEx("Excel.Application")` -- always creates a new Excel process. `Dispatch` can connect to a stale/orphaned process and crash.
- Always call `pythoncom.CoInitialize()` before and `pythoncom.CoUninitialize()` in `finally`.
- Always set `xl.Visible = False` and `xl.DisplayAlerts = False`.
- Always wrap in `try/except/finally` with `xl.Quit()` in `finally`.
- Use absolute Windows paths with backslashes: `os.path.abspath(path).replace("/", "\\")`.

## Excel constants (numeric values for COM)

```python
xlDatabase = 1
xlRowField = 1       # row field orientation
xlColumnField = 2    # column field orientation
xlSum = -4157
xlCount = -4112
xlUp = -4162         # Cells.End(xlUp)
xlToLeft = -4159     # Cells.End(xlToLeft)
```

## Creating a PivotTable

```python
src_ws = wb.Sheets("All Data")
last_row = src_ws.Cells(src_ws.Rows.Count, 1).End(xlUp).Row
last_col = src_ws.Cells(1, src_ws.Columns.Count).End(xlToLeft).Column
src_range = src_ws.Range(src_ws.Cells(1, 1), src_ws.Cells(last_row, last_col))

pc = wb.PivotCaches().Create(SourceType=xlDatabase, SourceData=src_range)
pt = pc.CreatePivotTable(TableDestination=ws.Cells(row, 1), TableName="MyPivot")

pt.PivotFields("Category").Orientation = xlRowField

df1 = pt.AddDataField(pt.PivotFields("Revenue"), "Sum of Revenue", xlSum)
df1.NumberFormat = '_($* #,##0.00_);[Red]_($* (#,##0.00)'
df2 = pt.AddDataField(pt.PivotFields("Revenue"), "Count of Revenue", xlCount)
```

## Hiding the "Values" header row

Multiple data fields create a 2-row column header (row 1 = "Values" label, row 2 = field names). Hide row 1:

```python
pt.DataPivotField.Orientation = 2  # xlColumnField
_col_rng = pt.ColumnRange
if _col_rng is not None and _col_rng.Rows.Count > 1:
    ws.Rows(_col_rng.Rows(1).Row).RowHeight = 0
    hdr_row = _col_rng.Rows(2).Row
else:
    hdr_row = pt.TableRange2.Row
```

## Determining pivot extent (for adding formulas beside the pivot)

```python
pt_range = pt.TableRange2
first_data = hdr_row + 1
grand_total = pt_range.Row + pt_range.Rows.Count - 1

for r in range(first_data, grand_total):  # exclude grand total
    ws.Cells(r, 13).Formula = f'=IF(E{r}=0,"",F{r}/E{r})'
```

## Conditional color scales ("heatmap")

When the user says "heatmap" / "apply a heatmap" to numbers in Excel, apply this 3-point conditional color scale. Default: -3 = red RGB(248,105,107), 0 = white, 3 = green RGB(99,190,123). Excel BGR = R + G*256 + B*65536.

```python
rng = ws.Range(ws.Cells(first_data, col), ws.Cells(grand_total - 1, col))
rng.FormatConditions.AddColorScale(ColorScaleType=3)
cs = rng.FormatConditions(rng.FormatConditions.Count)
cs.ColorScaleCriteria(1).Type = 0   # xlConditionValueNumber
cs.ColorScaleCriteria(1).Value = -3
cs.ColorScaleCriteria(1).FormatColor.Color = 7039480     # red (248,105,107)
cs.ColorScaleCriteria(2).Type = 0
cs.ColorScaleCriteria(2).Value = 0
cs.ColorScaleCriteria(2).FormatColor.Color = 16777215    # white
cs.ColorScaleCriteria(3).Type = 0
cs.ColorScaleCriteria(3).Value = 3
cs.ColorScaleCriteria(3).FormatColor.Color = 8109667     # green (99,190,123)
```

## Rerun safety

- Delete existing target sheet before creating: iterate `wb.Sheets` in reverse, delete by name.
- The subprocess helper is idempotent (safe to rerun).

## `create_pivots_subprocess` quick reference

Always prefer the helper over raw COM code. Write data with `openpyxl`, close the file, then call:

```python
from excel_pivot_helper import create_pivots_subprocess

pivot_defs = [
    {
        "section_title": "PnL Summary",
        "source_sheet": "All Data",
        "row_field": "Type",                          # primary row grouping
        "extra_row_fields": ["trade_date", "symbol"],  # optional nested rows
        "data_fields": [
            {"field": "pnl", "label": "Sum of PnL", "function": "sum",
             "format": '_($* #,##0.00_);[Red]_($* (#,##0.00)'},
        ],
        "extra_columns": [],       # optional computed columns beside pivot
        "color_scale_cols": [],    # optional 1-based column indices for heatmap
        "gap_rows": 2,
    }
]
create_pivots_subprocess(output_file, pivot_defs, target_sheet="Summary")
```

## Reference implementations on disk

- Helper library: `D:/PycharmProjects/utils/excel_pivot_helper.py`
- Working usage: `D:/agent_projects/month_end/create_month_end_excel.py` (subprocess call cell at bottom)
- Multi-row-field usage: `D:/agent_projects/sp500_adds/candidates_buying_vol.py` (pivot with Type/trade_date/symbol rows)
