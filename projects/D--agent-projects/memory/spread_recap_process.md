# Call/Put Spread Recap Process (from for_claude.xlsx style files)

When user asks for a "recap" of positions in a ticker from a file like `C:\Users\zdietz\Downloads\for_claude.xlsx` (columns include Name, Raw Position, Avg Cost, Price, NET YTD PNL):

## Process (in this exact order)

1. **Filter rows** where `Name` contains the ticker (e.g., "RKLB"). Each row is one option leg.
2. **Pair legs into spreads**: match longs (`Raw Position` > 0) with shorts (`Raw Position` < 0) by absolute position size. Same-size pair = one spread.
3. **For each spread, compute in this order:**
   - **Current mark** = `Price_long - Price_short` (use the `Price` column. IGNORE the `Avg Cost` column entirely.)
   - **MTM PNL** = `NET YTD PNL_long + NET YTD PNL_short` (just sum the two legs' YTD PnL)
   - **Avg cost** = `current_mark - MTM_PNL / contracts / 100`
4. **Life to date PnL** = sum of `NET YTD PNL` across all legs of the ticker (long and short combined).

## Output format

```
TICKER Recap (life to date pnl -X.Xk). We own

N of the [Month] LONG_STRIKE SHORT_STRIKE call spread @ AVG_COST (current mark: CURRENT_MARK, MTM PNL +/-X.Xk)

...
```

- Sort spreads by contract count, descending (largest position first).
- Round avg cost and current mark to 2 decimals.
- MTM PNL and life-to-date PNL in $k, 1 decimal (e.g., "-30.7k", "+6.4k", "-0.0k" if near zero).
- Use "+" sign for positive MTM PnL, "-" for negative.
- Blank line between each spread line (matching user's preferred format).

## Why this formula

- The Excel `Avg Cost` column is misleading and should not be used.
- `Price` column is today's current mark.
- `NET YTD PNL` is the realized + unrealized PnL year-to-date.
- Backing out: if we're up $X on N spreads, we paid (current_mark - X/N/100) per spread.

## Worked example (RKLB, 2026-05-21)

448 of June 145/185:
- Price_long=7.075, Price_short=1.750 -> current_mark = 5.325
- YTD_long=-65,477, YTD_short=+34,750 -> MTM = -30,727
- avg_cost = 5.325 - (-30727/448/100) = 5.325 - (-0.686) = 6.011

Final line: `448 of the June 145 185 call spread @ 6.01 (current mark: 5.33, MTM PNL -30.7k)`
