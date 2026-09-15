# optionsResearch.t_volume_data -- column definitions

Daily per-symbol option flow aggregates. One row per (symbol, trade_date).

| Column | Definition |
|---|---|
| symbol | underlying ticker |
| trade_date | date of the snap |
| call_volume | total call contract volume across all expiries |
| put_volume | total put contract volume across all expiries |
| call_volume_5D | call volume in contracts expiring within 5 trading days |
| put_volume_5D | put volume in contracts expiring within 5 trading days |
| call_volume_22D | call volume in contracts expiring within 22 trading days (~1 month) |
| put_volume_22D | put volume in contracts expiring within 22 trading days (~1 month) |
| call_volume_33D | call volume in contracts expiring within 33 trading days (~1.5 months) |
| put_volume_33D | put volume in contracts expiring within 33 trading days (~1.5 months) |
| call_large_volume_5D | call volume in contracts that were > 10 delta and expiring within 5 trading days |
| put_large_volume_5D | put volume in contracts that were > 10 delta and expiring within 5 trading days |
| call_large_volume_22D | call volume in contracts that were > 10 delta and expiring within 22 trading days |
| put_large_volume_22D | put volume in contracts that were > 10 delta and expiring within 22 trading days |
| call_large_volume_33D | call volume in contracts that were > 10 delta and expiring within 33 trading days |
| put_large_volume_33D | put volume in contracts that were > 10 delta and expiring within 33 trading days |
| call_delta | delta-weighted call volume across all expiries (\|delta\| * contracts * 100, share-equivalents) |
| put_delta | delta-weighted put volume across all expiries (\|delta\| * contracts * 100, share-equivalents) |
| call_delta_5D | delta-weighted call volume in contracts expiring within 5 trading days |
| put_delta_5D | delta-weighted put volume in contracts expiring within 5 trading days |
| call_delta_22D | delta-weighted call volume in contracts expiring within 22 trading days |
| put_delta_22D | delta-weighted put volume in contracts expiring within 22 trading days |
| call_delta_33D | delta-weighted call volume in contracts expiring within 33 trading days |
| put_delta_33D | delta-weighted put volume in contracts expiring within 33 trading days |
| call_large_delta | delta-weighted call volume in contracts that were > 10 delta, all expiries |
| put_large_delta | delta-weighted put volume in contracts that were > 10 delta, all expiries |
| call_large_delta_5D | delta-weighted call volume in contracts that were > 10 delta and expiring within 5 trading days |
| put_large_delta_5D | delta-weighted put volume in contracts that were > 10 delta and expiring within 5 trading days |
| call_large_delta_22D | delta-weighted call volume in contracts that were > 10 delta and expiring within 22 trading days |
| put_large_delta_22D | delta-weighted put volume in contracts that were > 10 delta and expiring within 22 trading days |
| call_large_delta_33D | delta-weighted call volume in contracts that were > 10 delta and expiring within 33 trading days |
| put_large_delta_33D | delta-weighted put volume in contracts that were > 10 delta and expiring within 33 trading days |
| call_premium | total $ call premium traded across all expiries (price * contracts * 100) |
| put_premium | total $ put premium traded across all expiries (price * contracts * 100) |
| call_premium_5D | $ call premium in contracts expiring within 5 trading days |
| put_premium_5D | $ put premium in contracts expiring within 5 trading days |
| call_premium_22D | $ call premium in contracts expiring within 22 trading days |
| put_premium_22D | $ put premium in contracts expiring within 22 trading days |
| call_premium_33D | $ call premium in contracts expiring within 33 trading days |
| put_premium_33D | $ put premium in contracts expiring within 33 trading days |
| call_large_premium | $ call premium in contracts that were > 10 delta, all expiries |
| put_large_premium | $ put premium in contracts that were > 10 delta, all expiries |
| call_large_premium_5D | $ call premium in contracts that were > 10 delta and expiring within 5 trading days |
| put_large_premium_5D | $ put premium in contracts that were > 10 delta and expiring within 5 trading days |
| call_large_premium_22D | $ call premium in contracts that were > 10 delta and expiring within 22 trading days |
| put_large_premium_22D | $ put premium in contracts that were > 10 delta and expiring within 22 trading days |
| call_large_premium_33D | $ call premium in contracts that were > 10 delta and expiring within 33 trading days |
| put_large_premium_33D | $ put premium in contracts that were > 10 delta and expiring within 33 trading days |
| atmVol_22D | ATM implied vol interpolated to 22 trading days (avg of two nearest listed expiries on the years axis; clamped at endpoints) |
| atmVol_66D | ATM implied vol interpolated to 66 trading days (same method) |
| has_weeklies | True if the ticker has >= 2 expiries that are not 3rd-Friday serials (i.e. weekly options are listed) |
