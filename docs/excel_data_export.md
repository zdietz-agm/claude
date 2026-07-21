# Excel Data Export (reference)

Rules live in CLAUDE.md ("Excel data export"). This file holds the full `export_to_excel()` template and column lists.

## Full export function template

```python
def export_to_excel(dfs_dict, base_name):
    """
    Export dataframes to formatted Excel.
    dfs_dict: {'All': combined_df, 'Strategy_A': df_a, 'Strategy_B': df_b}
    """
    from openpyxl.utils.dataframe import dataframe_to_rows
    from openpyxl.styles import Font, Alignment, PatternFill
    from openpyxl.utils import get_column_letter
    from datetime import datetime

    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filepath = f'C:/Users/zdietz/Downloads/{base_name}_{timestamp}.xlsx'

    # Columns to format as currency (red/black accounting)
    dollar_cols = ['pnl', 'gamma_pnl', 'vega_pnl', 'theta_pnl', 'opt_pnl',
                   'price', 'entry_price', 'exit_price', 'premium', 'value']

    # Columns to round to 3 decimals
    decimal_cols = ['delta', 'gamma', 'vega', 'theta', 'iv', 'payout', 'ratio']

    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        for sheet_name, df in dfs_dict.items():
            # Round decimal columns
            for col in decimal_cols:
                if col in df.columns:
                    df[col] = df[col].round(3)

            df.to_excel(writer, sheet_name=sheet_name, index=False)
            ws = writer.sheets[sheet_name]

            # Enable autofilter on header row
            ws.auto_filter.ref = ws.dimensions

            # Freeze first 2 columns (trade_date, time typically)
            ws.freeze_panes = 'C2'

            # Format dollar columns + auto-fit width
            for col_idx, col_name in enumerate(df.columns, 1):
                col_letter = get_column_letter(col_idx)

                max_len = max(len(str(col_name)), df[col_name].astype(str).str.len().max())
                ws.column_dimensions[col_letter].width = min(max_len + 2, 20)

                if col_name in dollar_cols:
                    for row in range(2, len(df) + 2):
                        ws[f'{col_letter}{row}'].number_format = '_($* #,##0.00_);[Red]_($* (#,##0.00)'

    print(f'Saved: {filepath}')
    return filepath
```

## Analysis-relevant columns (full list)

Only include columns relevant to the analysis. Common ones:

- `trade_date`, `time`, `symbol`, `pnl`, `expiry`, `strike`, `cp` (call/put)
- For spreads: `short_strike`, `long_strike`, or `put_short_strike`, `put_long_strike`, `call_short_strike`, `call_long_strike`
- `pnl`, `size`, `price`, `gamma_pnl`, `vega_pnl`, `theta_pnl`, `opt_pnl`
- `delta`, `gamma`, `vega`, `theta`, `iv`
- `underlying_price`, `entry_price`, `exit_price`

Prioritize making `pnl` or `daily_pnl` the first column after the frozen leftmost columns.
