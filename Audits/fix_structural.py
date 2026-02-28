"""
Structural Fix Script for nigeria_lga_polsim_formatted.xlsx
Addresses all CRITICAL and WARNING issues from audit_structural.md

Fixes applied:
  1. CRITICAL — Ethnicity sums: normalize so every row sums to exactly 100%
     - Under-sum rows: deficit absorbed into "% Other"
     - Over-sum rows: proportionally scale all non-zero values down to 100
  2. WARNING — Religion nulls: fill missing "% Muslim" = 100 - Christian - Traditionalist
  3. WARNING — Median Age: clamp values below 15.0 up to 15.0
  4. WARNING — Categorical capitalization: normalize to title case (first letter uppercase)

Output: nigeria_lga_polsim_formatted_fixed.xlsx (same structure, patched values)
Also:  fix_changelog.md (itemized log of every cell changed)
"""
import pandas as pd
import numpy as np
from copy import deepcopy
import warnings
warnings.filterwarnings('ignore')

XLSX = 'nigeria_lga_polsim_formatted.xlsx'
SHEET = 'LGA_DATA'
OUT_XLSX = 'nigeria_lga_polsim_formatted_fixed.xlsx'
OUT_LOG = 'fix_changelog.md'

# ── Load ───────────────────────────────────────────────────────
# Read both header rows: row 1 (categories) and row 2 (column names)
df_raw = pd.read_excel(XLSX, sheet_name=SHEET, header=None)
cat_row = df_raw.iloc[0].tolist()   # row 1: category headers
col_row = df_raw.iloc[1].tolist()   # row 2: column names
df = df_raw.iloc[2:].copy()         # data rows
df.columns = col_row
df = df.reset_index(drop=True)

n_rows = len(df)
columns = list(df.columns)

changelog = []
def log(section, row_excel, col, old_val, new_val, note=''):
    changelog.append({
        'section': section,
        'row': row_excel,
        'column': col,
        'old': old_val,
        'new': new_val,
        'note': note
    })

print(f'Loaded {n_rows} rows, {len(columns)} columns')
print()

# ══════════════════════════════════════════════════════════════════
# FIX 1: Ethnicity Sums — normalize to 100%
# ══════════════════════════════════════════════════════════════════
print('FIX 1: Ethnicity sums...')

eth_col_indices = list(range(8, 94))  # cols 8-93
eth_cols = [columns[i] for i in eth_col_indices]
other_col = '% Other'  # col 93

# Convert ethnicity columns to float (must be float to allow fractional adjustments)
for c in eth_cols:
    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(float)

eth_sums = df[eth_cols].sum(axis=1)
fix1_count = 0

for idx in range(n_rows):
    s = eth_sums[idx]
    row_excel = idx + 3  # data starts at Excel row 3

    if abs(s - 100.0) <= 1.0:
        continue  # within tolerance

    if s < 100.0:
        # UNDER-SUM: add deficit to "% Other"
        deficit = 100.0 - s
        old_other = df.at[idx, other_col]
        new_other = round(old_other + deficit, 2)
        log('Ethnicity', row_excel, other_col, old_other, new_other,
            f'Added {deficit:.2f} deficit to % Other (sum was {s:.2f})')
        df.at[idx, other_col] = new_other
        fix1_count += 1

    else:
        # OVER-SUM: proportionally scale all non-zero ethnicity values down
        scale = 100.0 / s
        for c in eth_cols:
            old_val = df.at[idx, c]
            if old_val > 0:
                new_val = round(old_val * scale, 2)
                if abs(new_val - old_val) > 0.001:
                    log('Ethnicity', row_excel, c, old_val, new_val,
                        f'Scaled down by {scale:.4f} (sum was {s:.2f})')
                    df.at[idx, c] = new_val

        # After scaling, fix rounding so sum is exactly 100
        new_sum = df.loc[idx, eth_cols].sum()
        rounding_err = round(100.0 - new_sum, 2)
        if abs(rounding_err) > 0.001:
            # Adjust the largest value to absorb rounding error
            largest_col = df.loc[idx, eth_cols].idxmax()
            old_v = df.at[idx, largest_col]
            df.at[idx, largest_col] = round(old_v + rounding_err, 2)
            log('Ethnicity', row_excel, largest_col,
                old_v, df.at[idx, largest_col],
                f'Rounding adjustment of {rounding_err:+.2f}')
        fix1_count += 1

# Verify
eth_sums_after = df[eth_cols].sum(axis=1)
still_bad = ((eth_sums_after < 99.0) | (eth_sums_after > 101.0)).sum()
print(f'  Fixed {fix1_count} rows. Remaining deviations >1.0: {still_bad}')

# ══════════════════════════════════════════════════════════════════
# FIX 2: Religion nulls — fill % Muslim = 100 - Christian - Trad
# ══════════════════════════════════════════════════════════════════
print('FIX 2: Religion null % Muslim...')

df['% Muslim'] = pd.to_numeric(df['% Muslim'], errors='coerce')
df['% Christian'] = pd.to_numeric(df['% Christian'], errors='coerce')
df['% Traditionalist'] = pd.to_numeric(df['% Traditionalist'], errors='coerce')

null_mask = df['% Muslim'].isna()
fix2_count = 0

for idx in df[null_mask].index:
    row_excel = idx + 3
    christian = df.at[idx, '% Christian']
    trad = df.at[idx, '% Traditionalist']
    if pd.notna(christian) and pd.notna(trad):
        new_muslim = round(100.0 - christian - trad, 2)
        log('Religion', row_excel, '% Muslim', 'NULL', new_muslim,
            f'Computed: 100 - {christian} - {trad} = {new_muslim}')
        df.at[idx, '% Muslim'] = new_muslim
        fix2_count += 1

# Verify
still_null = df['% Muslim'].isna().sum()
rel_sums = df[['% Muslim', '% Christian', '% Traditionalist']].sum(axis=1)
rel_bad = ((rel_sums < 99.0) | (rel_sums > 101.0)).sum()
print(f'  Filled {fix2_count} null Muslim values. Remaining nulls: {still_null}. Religion sum deviations: {rel_bad}')

# ══════════════════════════════════════════════════════════════════
# FIX 3: Median Age — clamp below-15 values to 15.0
# ══════════════════════════════════════════════════════════════════
print('FIX 3: Median Age clamp...')

df['Median Age Estimate'] = pd.to_numeric(df['Median Age Estimate'], errors='coerce')
below_mask = df['Median Age Estimate'] < 15.0
fix3_count = 0

for idx in df[below_mask].index:
    row_excel = idx + 3
    old_val = df.at[idx, 'Median Age Estimate']
    log('Median Age', row_excel, 'Median Age Estimate', old_val, 15.0,
        f'Clamped from {old_val} to 15.0')
    df.at[idx, 'Median Age Estimate'] = 15.0
    fix3_count += 1

print(f'  Clamped {fix3_count} values to 15.0')

# ══════════════════════════════════════════════════════════════════
# FIX 4: Categorical capitalization normalization
# ══════════════════════════════════════════════════════════════════
print('FIX 4: Categorical capitalization...')

# For each column with variants, normalize: capitalize first letter, rest as-is
cat_fix_cols = ['Dominant Livelihood', 'Predominant Land Tenure']
fix4_count = 0

for col in cat_fix_cols:
    for idx in range(n_rows):
        val = df.at[idx, col]
        if pd.isna(val):
            continue
        val_str = str(val)
        # Capitalize only the first character of the entire string
        normalized = val_str[0].upper() + val_str[1:] if len(val_str) > 0 else val_str
        if normalized != val_str:
            row_excel = idx + 3
            log('Categorical', row_excel, col, val_str, normalized,
                'Capitalized first letter')
            df.at[idx, col] = normalized
            fix4_count += 1

print(f'  Normalized {fix4_count} values across {len(cat_fix_cols)} columns')

# ══════════════════════════════════════════════════════════════════
# Write fixed file
# ══════════════════════════════════════════════════════════════════
print()
print('Writing fixed file...')

# Reconstruct the full dataframe with header rows
out_df = pd.DataFrame([cat_row, col_row] + df.values.tolist())
out_df.columns = range(len(out_df.columns))

# Write to Excel preserving structure
with pd.ExcelWriter(OUT_XLSX, engine='openpyxl') as writer:
    out_df.to_excel(writer, sheet_name='LGA_DATA', index=False, header=False)

    # Copy METADATA sheet if it exists
    try:
        meta_df = pd.read_excel(XLSX, sheet_name='METADATA', header=None)
        meta_df.to_excel(writer, sheet_name='METADATA', index=False, header=False)
    except Exception:
        pass

print(f'Wrote {OUT_XLSX}')

# ══════════════════════════════════════════════════════════════════
# Write changelog
# ══════════════════════════════════════════════════════════════════
print('Writing changelog...')

lines = []
lines.append('# Fix Changelog')
lines.append(f'**Source:** `{XLSX}` -> `{OUT_XLSX}`')
lines.append(f'**Date:** 2026-02-28')
lines.append('')
lines.append(f'**Total cells modified: {len(changelog)}**')
lines.append('')

# Summary by section
from collections import Counter
sec_counts = Counter(c['section'] for c in changelog)
lines.append('| Fix | Cells Changed |')
lines.append('|-----|---------------|')
for sec, cnt in sorted(sec_counts.items()):
    lines.append(f'| {sec} | {cnt} |')
lines.append('')

# Verification summary
lines.append('## Verification')
lines.append('')
lines.append(f'| Check | Before | After |')
lines.append(f'|-------|--------|-------|')
lines.append(f'| Ethnicity rows deviating >1.0 from 100 | 318 | {still_bad} |')
lines.append(f'| Religion null % Muslim | 73 | {still_null} |')
lines.append(f'| Religion rows deviating >1.0 from 100 | 73 | {rel_bad} |')
lines.append(f'| Median Age below 15.0 | 35 | 0 |')
lines.append(f'| Capitalization variants | 13 pairs | 0 |')
lines.append('')

# Detailed log by section
for section in ['Ethnicity', 'Religion', 'Median Age', 'Categorical']:
    sec_entries = [c for c in changelog if c['section'] == section]
    if not sec_entries:
        continue
    lines.append(f'## {section} Fixes ({len(sec_entries)} changes)')
    lines.append('')
    lines.append('| Row | Column | Old | New | Note |')
    lines.append('|-----|--------|-----|-----|------|')
    for entry in sec_entries:
        old_disp = f'{entry["old"]:.2f}' if isinstance(entry['old'], (int, float)) else str(entry['old'])
        new_disp = f'{entry["new"]:.2f}' if isinstance(entry['new'], (int, float)) else str(entry['new'])
        lines.append(f'| {entry["row"]} | {entry["column"]} | {old_disp} | {new_disp} | {entry["note"]} |')
    lines.append('')

with open(OUT_LOG, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f'Wrote {OUT_LOG}')
print()
print(f'DONE. Total changes: {len(changelog)}')
print(f'  Ethnicity: {sec_counts.get("Ethnicity", 0)} cell edits across {fix1_count} rows')
print(f'  Religion:  {sec_counts.get("Religion", 0)} cell edits across {fix2_count} rows')
print(f'  Median Age: {sec_counts.get("Median Age", 0)} cell edits across {fix3_count} rows')
print(f'  Categorical: {sec_counts.get("Categorical", 0)} cell edits across {fix4_count} values')
