"""
Structural Integrity Audit for nigeria_lga_polsim_formatted.xlsx
Sheet: LGA_DATA
"""
import pandas as pd
import numpy as np
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

XLSX = 'nigeria_lga_polsim_formatted.xlsx'
SHEET = 'LGA_DATA'
OUT = 'audit_structural.md'

# ── Load data ──────────────────────────────────────────────────
# Row 1 = category headers (index 0 in 0-based), Row 2 = column names (index 1), data starts row 3 (index 2)
df = pd.read_excel(XLSX, sheet_name=SHEET, header=1)  # use row 2 as header (0-indexed row 1)

# Also load row 1 for category headers
df_cat = pd.read_excel(XLSX, sheet_name=SHEET, header=None, nrows=1)
category_row = df_cat.iloc[0].tolist()

# Forward-fill category row to map each column to its category
cat_filled = []
last_cat = None
for c in category_row:
    if pd.notna(c):
        last_cat = c
    cat_filled.append(last_cat)

columns = list(df.columns)
n_rows = len(df)

issues = []  # (severity, section, description)

report = []
def w(line=''):
    report.append(line)

def add_issue(severity, section, desc):
    issues.append((severity, section, desc))

w('# Structural Integrity Audit Report')
w(f'**File:** `{XLSX}` — Sheet: `{SHEET}`')
w(f'**Date:** 2026-02-28')
w(f'**Rows (data):** {n_rows}  |  **Columns:** {len(columns)}')
w()

# ══════════════════════════════════════════════════════════════════
# 1. ROW COUNT
# ══════════════════════════════════════════════════════════════════
w('---')
w('## 1. Row Count Check')
w()
w(f'Expected: **774** data rows')
w(f'Found: **{n_rows}** data rows')
w()

if n_rows == 774:
    w('**PASS** — Row count matches expected 774 LGAs.')
elif n_rows < 774:
    diff = 774 - n_rows
    w(f'**FAIL** — {diff} rows short of 774.')
    add_issue('CRITICAL', 'Row Count', f'{diff} rows missing from expected 774 (found {n_rows})')
else:
    diff = n_rows - 774
    w(f'**FAIL** — {diff} extra rows beyond 774.')
    add_issue('CRITICAL', 'Row Count', f'{diff} extra rows beyond expected 774 (found {n_rows})')

# Check for duplicate (State, LGA) pairs
state_col = 'State'
lga_col = 'LGA Name'
dupes = df[df.duplicated(subset=[state_col, lga_col], keep=False)]
if len(dupes) > 0:
    w()
    w(f'### Duplicate (State, LGA Name) Pairs: {len(dupes)} rows')
    w()
    w('| Row | State | LGA Name |')
    w('|-----|-------|----------|')
    for idx, row in dupes.iterrows():
        w(f'| {idx+3} | {row[state_col]} | {row[lga_col]} |')
    add_issue('CRITICAL', 'Row Count', f'{len(dupes)} rows involved in duplicate (State, LGA Name) pairs')
else:
    w()
    w('No duplicate (State, LGA Name) pairs found.')

# ── Cross-reference against official 774 LGA list ──
# Nigeria's 36 states + FCT with official LGA counts
OFFICIAL_STATE_LGA_COUNTS = {
    'Abia': 17, 'Adamawa': 21, 'Akwa Ibom': 31, 'Anambra': 21, 'Bauchi': 20,
    'Bayelsa': 8, 'Benue': 23, 'Borno': 27, 'Cross River': 18, 'Delta': 25,
    'Ebonyi': 13, 'Edo': 18, 'Ekiti': 16, 'Enugu': 17, 'FCT': 6,
    'Gombe': 11, 'Imo': 27, 'Jigawa': 27, 'Kaduna': 23, 'Kano': 44,
    'Katsina': 34, 'Kebbi': 21, 'Kogi': 21, 'Kwara': 16, 'Lagos': 20,
    'Nasarawa': 13, 'Niger': 25, 'Ogun': 20, 'Ondo': 18, 'Osun': 30,
    'Oyo': 33, 'Plateau': 17, 'Rivers': 23, 'Sokoto': 23, 'Taraba': 16,
    'Yobe': 17, 'Zamfara': 14
}

w()
w('### State-Level LGA Count Comparison')
w()
dataset_state_counts = df[state_col].value_counts().to_dict()

# Normalize state names for comparison
dataset_states = set(str(s).strip() for s in dataset_state_counts.keys())
official_states = set(OFFICIAL_STATE_LGA_COUNTS.keys())

# Map dataset states to official (case-insensitive)
state_map = {}
for ds in dataset_states:
    for os_name in official_states:
        if ds.lower().replace(' ', '') == os_name.lower().replace(' ', ''):
            state_map[ds] = os_name
            break

missing_official = official_states - set(state_map.values())
extra_dataset = dataset_states - set(state_map.keys())

w('| State (Official) | Official LGAs | Dataset LGAs | Diff |')
w('|-----------------|---------------|--------------|------|')
for st in sorted(OFFICIAL_STATE_LGA_COUNTS.keys()):
    official_n = OFFICIAL_STATE_LGA_COUNTS[st]
    # find in dataset
    ds_key = None
    for k, v in state_map.items():
        if v == st:
            ds_key = k
            break
    ds_n = dataset_state_counts.get(ds_key, 0) if ds_key else 0
    diff = ds_n - official_n
    flag = ' ⚠️' if diff != 0 else ''
    w(f'| {st} | {official_n} | {ds_n} | {diff:+d}{flag} |')
    if diff != 0:
        add_issue('WARNING', 'Row Count', f'{st}: expected {official_n} LGAs, found {ds_n} (diff: {diff:+d})')

if missing_official:
    w()
    w(f'**States in official list but missing from dataset:** {", ".join(sorted(missing_official))}')
    for s in missing_official:
        add_issue('CRITICAL', 'Row Count', f'State "{s}" missing from dataset entirely')

if extra_dataset:
    w()
    w(f'**States in dataset but not in official list:** {", ".join(sorted(extra_dataset))}')
    for s in extra_dataset:
        add_issue('WARNING', 'Row Count', f'State "{s}" in dataset but not in official 36+FCT list')

w()

# ══════════════════════════════════════════════════════════════════
# 2. IDENTIFICATION COLUMNS
# ══════════════════════════════════════════════════════════════════
w('---')
w('## 2. Identification Columns')
w()

# The dataset has: State, LGA Name, Colonial Era Region (as the "Administrative Zone" equivalent)
id_cols = {
    'State': state_col,
    'LGA Name': lga_col,
    'Administrative Zone (Colonial Era Region)': 'Colonial Era Region'
}

for label, col in id_cols.items():
    if col not in df.columns:
        w(f'**{label}**: Column `{col}` NOT FOUND in dataset!')
        add_issue('CRITICAL', 'Identification', f'Column "{col}" not found')
        continue
    null_count = df[col].isna().sum()
    if null_count > 0:
        w(f'**{label}** (`{col}`): **{null_count} null values** found')
        add_issue('CRITICAL', 'Identification', f'{col} has {null_count} null values')
        null_rows = df[df[col].isna()].index.tolist()
        w(f'  - Rows (Excel): {[r+3 for r in null_rows[:20]]}{"..." if len(null_rows)>20 else ""}')
    else:
        w(f'**{label}** (`{col}`): All {n_rows} rows populated. ✓')
w()

# Duplicate LGA names within same state
w('### Duplicate LGA Names Within Same State')
dup_within = df.groupby([state_col, lga_col]).size().reset_index(name='count')
dup_within = dup_within[dup_within['count'] > 1]
if len(dup_within) > 0:
    w()
    w('| State | LGA Name | Count |')
    w('|-------|----------|-------|')
    for _, row in dup_within.iterrows():
        w(f'| {row[state_col]} | {row[lga_col]} | {row["count"]} |')
    add_issue('CRITICAL', 'Identification', f'{len(dup_within)} duplicate LGA name(s) within same state')
else:
    w('No duplicates found. ✓')
w()

# Administrative Zones
zone_col = 'Colonial Era Region'
w('### Administrative Zones (Colonial Era Region)')
w()
if zone_col in df.columns:
    zone_counts = df[zone_col].value_counts().sort_index()
    w(f'Unique zones: **{len(zone_counts)}** (expected: ~8)')
    w()
    w('| Zone | LGA Count |')
    w('|------|-----------|')
    for z, c in zone_counts.items():
        w(f'| {z} | {c} |')
    if len(zone_counts) != 8:
        add_issue('INFO', 'Identification', f'Found {len(zone_counts)} zones instead of expected 8')
w()

# States
w('### States')
w()
state_counts = df[state_col].value_counts().sort_index()
w(f'Unique states: **{len(state_counts)}**')
w()
w('| State | LGA Count |')
w('|-------|-----------|')
for s, c in state_counts.items():
    w(f'| {s} | {c} |')
w()
if len(state_counts) < 36:
    add_issue('WARNING', 'Identification', f'Only {len(state_counts)} unique states (expected 36+FCT)')
elif len(state_counts) > 37:
    add_issue('WARNING', 'Identification', f'{len(state_counts)} unique states (expected 36+FCT)')

# ══════════════════════════════════════════════════════════════════
# 3. ETHNICITY SUM CHECK
# ══════════════════════════════════════════════════════════════════
w('---')
w('## 3. Ethnicity Sum Check')
w()

# Ethnicity columns: cols 8-93 in the original (0-indexed), which are columns with "%" prefix in row2
# From the column inventory: Col 8 (% Hausa) through Col 93 (% Other)
eth_cols = [c for c in columns if c.startswith('% ') and c not in ['% Muslim', '% Christian', '% Traditionalist', '% Population Under 30']]
# Filter to only the ethnolinguistic ones (cols 8–93)
eth_col_indices = []
for i, c in enumerate(columns):
    if i >= 8 and i <= 93:
        eth_col_indices.append(i)
eth_cols = [columns[i] for i in eth_col_indices]

w(f'Ethnicity columns identified: **{len(eth_cols)}** (col indices {eth_col_indices[0]}–{eth_col_indices[-1]})')
w(f'Range: `{eth_cols[0]}` ... `{eth_cols[-1]}`')
w()

# Convert to numeric
eth_df = df[eth_cols].apply(pd.to_numeric, errors='coerce')
eth_sums = eth_df.sum(axis=1)

w(f'| Metric | Value |')
w(f'|--------|-------|')
w(f'| Min sum | {eth_sums.min():.2f} |')
w(f'| Max sum | {eth_sums.max():.2f} |')
w(f'| Mean sum | {eth_sums.mean():.2f} |')
w(f'| Median sum | {eth_sums.median():.2f} |')
outside = ((eth_sums < 99.0) | (eth_sums > 101.0)).sum()
w(f'| Rows outside 99–101 | {outside} |')
deviated = ((eth_sums < 99.0) | (eth_sums > 101.0))
w(f'| Rows deviating >1.0 from 100 | {deviated.sum()} |')
w()

if deviated.sum() > 0:
    add_issue('WARNING', 'Ethnicity Sums', f'{deviated.sum()} rows with ethnicity sum deviating >1.0 from 100')
    w('### Rows with Ethnicity Sum Deviation > 1.0')
    w()
    w('| Row (Excel) | State | LGA | Sum |')
    w('|-------------|-------|-----|-----|')
    flagged = df[deviated][[state_col, lga_col]].copy()
    flagged['sum'] = eth_sums[deviated]
    for idx, row in flagged.iterrows():
        w(f'| {idx+3} | {row[state_col]} | {row[lga_col]} | {row["sum"]:.2f} |')
else:
    w('**PASS** — All ethnicity sums within 99–101. ✓')
w()

# ══════════════════════════════════════════════════════════════════
# 4. RELIGION SUM CHECK
# ══════════════════════════════════════════════════════════════════
w('---')
w('## 4. Religion Sum Check')
w()

rel_cols = ['% Muslim', '% Christian', '% Traditionalist']
found_rel = [c for c in rel_cols if c in columns]
missing_rel = [c for c in rel_cols if c not in columns]

if missing_rel:
    w(f'**Missing columns:** {missing_rel}')
    add_issue('CRITICAL', 'Religion Sums', f'Missing religion columns: {missing_rel}')

if found_rel:
    rel_df = df[found_rel].apply(pd.to_numeric, errors='coerce')
    rel_sums = rel_df.sum(axis=1)

    w(f'Religion columns: `{", ".join(found_rel)}`')
    w()
    w(f'| Metric | Value |')
    w(f'|--------|-------|')
    w(f'| Min sum | {rel_sums.min():.2f} |')
    w(f'| Max sum | {rel_sums.max():.2f} |')
    w(f'| Mean sum | {rel_sums.mean():.2f} |')
    w(f'| Median sum | {rel_sums.median():.2f} |')
    outside_r = ((rel_sums < 99.0) | (rel_sums > 101.0)).sum()
    w(f'| Rows outside 99–101 | {outside_r} |')
    deviated_r = ((rel_sums < 99.0) | (rel_sums > 101.0))
    w(f'| Rows deviating >1.0 from 100 | {deviated_r.sum()} |')
    w()

    if deviated_r.sum() > 0:
        add_issue('WARNING', 'Religion Sums', f'{deviated_r.sum()} rows with religion sum deviating >1.0 from 100')
        w('### Rows with Religion Sum Deviation > 1.0')
        w()
        w('| Row (Excel) | State | LGA | Sum |')
        w('|-------------|-------|-----|-----|')
        flagged_r = df[deviated_r][[state_col, lga_col]].copy()
        flagged_r['sum'] = rel_sums[deviated_r]
        for idx, row in flagged_r.iterrows():
            w(f'| {idx+3} | {row[state_col]} | {row[lga_col]} | {row["sum"]:.2f} |')
    else:
        w('**PASS** — All religion sums within 99–101. ✓')
w()

# ══════════════════════════════════════════════════════════════════
# 5. NUMERIC VALIDATION
# ══════════════════════════════════════════════════════════════════
w('---')
w('## 5. Numeric Validation')
w()

# Define column -> expected range mappings
range_rules = {}

# Percentage columns (0-100)
pct_keywords = ['%', 'Pct', 'Rate', 'Penetration']
for c in columns:
    for kw in pct_keywords:
        if kw in c and c not in range_rules:
            range_rules[c] = (0, 100, 'percentage')

# Specific overrides
specific_ranges = {
    'Estimated Population': (1, None, 'population'),
    'Population Density per km2': (0.001, None, 'density'),
    'Median Age Estimate': (15, 55, 'median_age'),
    'Gender Parity Index': (0, 2.0, 'gpi'),
    'Num Secondary Schools': (0, None, 'count'),
}

for c, (lo, hi, tag) in specific_ranges.items():
    if c in columns:
        range_rules[c] = (lo, hi, tag)

# Find all columns that should be numeric
numeric_candidates = []
for i, c in enumerate(columns):
    if c in [state_col, lga_col, zone_col, 'Terrain Type', 'Dominant Livelihood',
             'Religious Subtype Notes', 'Major Urban Center', 'Urban Rural Split',
             'Oil Producing', 'Resource Extraction Notes', 'Road Infrastructure Quality',
             'Market Access', 'Tertiary Institution Present', 'Traditional Authority',
             'Traditional Authority Influence', 'Predominant Land Tenure', 'Data Notes',
             'Almajiri Prevalence']:
        continue
    # Try to detect if column is numeric
    col_data = df[c]
    numeric_vals = pd.to_numeric(col_data, errors='coerce')
    non_null = col_data.dropna()
    if len(non_null) == 0:
        continue
    numeric_ratio = numeric_vals.notna().sum() / max(len(non_null), 1)
    if numeric_ratio > 0.5:
        numeric_candidates.append(c)

w(f'Numeric columns identified: **{len(numeric_candidates)}**')
w()

# 5a. Non-numeric values in numeric columns
w('### 5a. Non-Numeric Values in Numeric Columns')
w()
non_numeric_issues = []
for c in numeric_candidates:
    col_data = df[c].dropna()
    if len(col_data) == 0:
        continue
    numeric_parsed = pd.to_numeric(col_data, errors='coerce')
    bad_mask = col_data.notna() & numeric_parsed.isna()
    bad_count = bad_mask.sum()
    if bad_count > 0:
        bad_vals = col_data[bad_mask].unique()[:5]
        non_numeric_issues.append((c, bad_count, bad_vals))

if non_numeric_issues:
    w('| Column | Non-Numeric Count | Sample Values |')
    w('|--------|-------------------|---------------|')
    for c, cnt, vals in non_numeric_issues:
        w(f'| {c} | {cnt} | {", ".join(str(v) for v in vals)} |')
        add_issue('WARNING', 'Numeric Validation', f'Column "{c}" has {cnt} non-numeric values')
else:
    w('No non-numeric values found in numeric columns. ✓')
w()

# 5b. Null/missing values
w('### 5b. Null/Missing Values in Numeric Columns')
w()
null_issues = []
for c in numeric_candidates:
    nc = df[c].isna().sum()
    if nc > 0:
        null_issues.append((c, nc))

if null_issues:
    w('| Column | Null Count |')
    w('|--------|------------|')
    for c, nc in sorted(null_issues, key=lambda x: -x[1]):
        w(f'| {c} | {nc} |')
        if nc > n_rows * 0.5:
            add_issue('WARNING', 'Numeric Validation', f'Column "{c}" has {nc} nulls ({nc*100/n_rows:.0f}%)')
        elif nc > 0:
            add_issue('INFO', 'Numeric Validation', f'Column "{c}" has {nc} null values')
else:
    w('No null values in numeric columns. ✓')
w()

# 5c. Out-of-range values
w('### 5c. Out-of-Range Values')
w()

oor_found = False
oor_rows = []
for c in numeric_candidates:
    if c not in range_rules:
        continue
    lo, hi, tag = range_rules[c]
    vals = pd.to_numeric(df[c], errors='coerce')
    violations = []
    if lo is not None:
        below = (vals < lo) & vals.notna()
        if below.sum() > 0:
            violations.append(f'{below.sum()} below {lo}')
            for idx in df[below].index[:5]:
                oor_rows.append((idx+3, c, float(vals[idx]), f'< {lo}'))
    if hi is not None:
        above = (vals > hi) & vals.notna()
        if above.sum() > 0:
            violations.append(f'{above.sum()} above {hi}')
            for idx in df[above].index[:5]:
                oor_rows.append((idx+3, c, float(vals[idx]), f'> {hi}'))
    if violations:
        if not oor_found:
            w('| Column | Range | Violations |')
            w('|--------|-------|------------|')
            oor_found = True
        w(f'| {c} | [{lo}, {hi}] | {"; ".join(violations)} |')
        for v in violations:
            add_issue('WARNING', 'Numeric Validation', f'Column "{c}": {v} (range [{lo},{hi}])')

if not oor_found:
    w('No out-of-range values found. ✓')
else:
    w()
    w('#### Sample Out-of-Range Rows (first 5 per column)')
    w()
    w('| Row (Excel) | Column | Value | Violation |')
    w('|-------------|--------|-------|-----------|')
    for row_n, col, val, viol in oor_rows:
        w(f'| {row_n} | {col} | {val:.4f} | {viol} |')
w()

# ══════════════════════════════════════════════════════════════════
# 6. CATEGORICAL CONSISTENCY
# ══════════════════════════════════════════════════════════════════
w('---')
w('## 6. Categorical Consistency')
w()

cat_cols_to_check = [
    'Terrain Type', 'Dominant Livelihood', 'Almajiri Prevalence',
    'Urban Rural Split', 'Oil Producing', 'Road Infrastructure Quality',
    'Market Access', 'Traditional Authority Influence',
    'Tertiary Institution Present', 'Predominant Land Tenure',
    'Major Urban Center'
]

# Also check if any additional categorical columns from user's list exist
extra_cats = [
    'Prestige Language', 'Housing Pressure', 'Net Migration Trend',
    'Industrial Profile', 'Chinese Investment Presence', 'Automation Penetration',
    'Rail Access', 'Planned City', 'BIC Activity Level', 'Al-Shahid Influence',
    'Sharia Court Status'
]

for ec in extra_cats:
    if ec in columns:
        cat_cols_to_check.append(ec)

for c in cat_cols_to_check:
    if c not in columns:
        w(f'### `{c}` — NOT FOUND IN DATASET')
        add_issue('INFO', 'Categorical', f'Column "{c}" not found in dataset')
        w()
        continue
    w(f'### `{c}`')
    w()
    vc = df[c].value_counts(dropna=False)
    null_count = df[c].isna().sum()

    w(f'Unique values: **{df[c].nunique()}** | Nulls: **{null_count}**')
    w()
    w('| Value | Count |')
    w('|-------|-------|')
    for val, cnt in vc.items():
        display = val if pd.notna(val) else '*(null)*'
        w(f'| {display} | {cnt} |')
    w()

    # Check for capitalization/spelling variants
    non_null_vals = [str(v).strip() for v in df[c].dropna().unique()]
    lower_map = {}
    for v in non_null_vals:
        key = v.lower().replace('_', ' ').replace('-', ' ')
        if key not in lower_map:
            lower_map[key] = []
        lower_map[key].append(v)
    variants = {k: v for k, v in lower_map.items() if len(v) > 1}
    if variants:
        w('**Potential spelling/capitalization variants:**')
        for k, v in variants.items():
            w(f'  - {v}')
        add_issue('INFO', 'Categorical', f'Column "{c}" has potential spelling variants: {variants}')
    w()

# ══════════════════════════════════════════════════════════════════
# 7. COLUMN INVENTORY
# ══════════════════════════════════════════════════════════════════
w('---')
w('## 7. Column Inventory')
w()
w('| Col Index | Column Name | Category (Row 1) | Data Type | Null Count |')
w('|-----------|-------------|-------------------|-----------|------------|')

for i, c in enumerate(columns):
    cat_label = cat_filled[i] if i < len(cat_filled) else ''
    null_c = df[c].isna().sum()
    # Determine data type
    non_null = df[c].dropna()
    if len(non_null) == 0:
        dtype = 'empty'
    else:
        numeric_parsed = pd.to_numeric(non_null, errors='coerce')
        if numeric_parsed.notna().sum() / len(non_null) > 0.8:
            dtype = 'numeric'
        else:
            dtype = 'categorical/text'
    w(f'| {i} | {c} | {cat_label} | {dtype} | {null_c} |')

w()

# ══════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════
w('---')
w('## Summary')
w()

critical = [i for i in issues if i[0] == 'CRITICAL']
warning = [i for i in issues if i[0] == 'WARNING']
info = [i for i in issues if i[0] == 'INFO']

w(f'**Total issues found: {len(issues)}**')
w()
w(f'| Severity | Count |')
w(f'|----------|-------|')
w(f'| CRITICAL | {len(critical)} |')
w(f'| WARNING | {len(warning)} |')
w(f'| INFO | {len(info)} |')
w()

if critical:
    w('### CRITICAL Issues')
    w()
    for sev, section, desc in critical:
        w(f'- **[{section}]** {desc}')
    w()

if warning:
    w('### WARNING Issues')
    w()
    for sev, section, desc in warning:
        w(f'- **[{section}]** {desc}')
    w()

if info:
    w('### INFO Issues')
    w()
    for sev, section, desc in info:
        w(f'- **[{section}]** {desc}')
    w()

# ── Write report ──
with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print(f'Audit report written to {OUT}')
print(f'Total issues: {len(issues)} (CRITICAL: {len(critical)}, WARNING: {len(warning)}, INFO: {len(info)})')
