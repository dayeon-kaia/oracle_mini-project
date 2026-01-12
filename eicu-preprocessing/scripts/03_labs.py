#!/usr/bin/env python3
"""
eICU Labs Extraction
====================

lab 테이블에서 주요 검사 결과 추출
MIMIC labevents 형식으로 변환

필요 변수:
- Lactate
- Creatinine
- WBC
- Platelets
- Potassium (K)
- Sodium (Na)

출력: labs_extracted.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths
EICU_DIR = Path('../../eicu/eicu-collaborative-research-database-demo-2.0.1')
DATA_DIR = Path('../data/processed')

print("=" * 60)
print("eICU Labs Extraction")
print("=" * 60)

# Load cohort
print("\nLoading cohort...")
cohort = pd.read_csv(DATA_DIR / 'cohort_base.csv')
print(f"  Cohort: {len(cohort):,} patients")

# ============================================================================
# Step 1: Load lab table
# ============================================================================
print("\nStep 1: Load lab table")

labs = pd.read_csv(EICU_DIR / 'lab.csv.gz', compression='gzip')
print(f"  Total lab records: {len(labs):,}")

# Filter to cohort patients
labs = labs[labs['patientunitstayid'].isin(cohort['stay_id'])]
print(f"  After cohort filter: {len(labs):,}")

# Rename columns
labs = labs.rename(columns={
    'patientunitstayid': 'stay_id',
    'labresultoffset': 'offset_min',
    'labname': 'lab_name',
    'labresult': 'lab_value'
})

# ============================================================================
# Step 2: Filter to required labs
# ============================================================================
print("\nStep 2: Filter to required labs")

# eICU lab names can vary - use contains for robustness
required_labs = {
    'lactate': ['lactate'],
    'creatinine': ['creatinine'],
    'wbc': ['WBC', 'wbc'],
    'platelets': ['platelet'],
    'potassium': ['potassium', 'K'],
    'sodium': ['sodium', 'Na']
}

# Create mapping
def map_lab_name(lab_name):
    """Map eICU lab name to MIMIC standard name"""
    if pd.isna(lab_name):
        return None
    
    lab_lower = str(lab_name).lower()
    
    for mimic_name, eicu_variants in required_labs.items():
        for variant in eicu_variants:
            if variant.lower() in lab_lower:
                return mimic_name
    return None

labs['mimic_lab_name'] = labs['lab_name'].apply(map_lab_name)

# Filter to only required labs
labs_filtered = labs[labs['mimic_lab_name'].notna()].copy()
print(f"  Required labs: {len(labs_filtered):,} records")

# Show distribution
print("\n  Lab distribution:")
for lab in required_labs.keys():
    count = (labs_filtered['mimic_lab_name'] == lab).sum()
    print(f"    {lab}: {count:,}")

# ============================================================================
# Step 3: Unit conversion and validation
# ============================================================================
print("\nStep 3: Unit conversion and validation")

# Convert to numeric
labs_filtered['lab_value'] = pd.to_numeric(labs_filtered['lab_value'], errors='coerce')

# Unit conversions and range checks
def validate_lab(row):
    """Validate and convert lab values"""
    lab_name = row['mimic_lab_name']
    value = row['lab_value']
    
    if pd.isna(value):
        return np.nan
    
    # Lactate: 0.1-30 mmol/L
    if lab_name == 'lactate':
        if 0.1 <= value <= 30:
            return value
    
    # Creatinine: 0.1-20 mg/dL
    elif lab_name == 'creatinine':
        if 0.1 <= value <= 20:
            return value
    
    # WBC: 0.1-100 K/μL (eICU might use different units)
    elif lab_name == 'wbc':
        # Sometimes stored as x1000
        if value > 200:  # Likely in cells/μL
            value = value / 1000
        if 0.1 <= value <= 100:
            return value
    
    # Platelets: 1-1000 K/μL
    elif lab_name == 'platelets':
        if value > 2000:  # Likely in cells/μL
            value = value / 1000
        if 1 <= value <= 1000:
            return value
    
    # Potassium: 1-10 mEq/L
    elif lab_name == 'potassium':
        if 1 <= value <= 10:
            return value
    
    # Sodium: 100-200 mEq/L
    elif lab_name == 'sodium':
        if 100 <= value <= 200:
            return value
    
    return np.nan

labs_filtered['lab_value_validated'] = labs_filtered.apply(validate_lab, axis=1)

# Drop invalid values
before = len(labs_filtered)
labs_filtered = labs_filtered[labs_filtered['lab_value_validated'].notna()].copy()
after = len(labs_filtered)
print(f"  Validation: {before:,} → {after:,} (removed {before-after:,} outliers)")

# ============================================================================
# Step 4: Pivot to wide format
# ============================================================================
print("\nStep 4: Pivot to wide format")

# Select columns
labs_final = labs_filtered[['stay_id', 'offset_min', 'mimic_lab_name', 'lab_value_validated']].copy()

# For each stay_id + offset, take the median if multiple values
labs_agg = labs_final.groupby(['stay_id', 'offset_min', 'mimic_lab_name'])['lab_value_validated'].median().reset_index()

# Pivot
labs_wide = labs_agg.pivot_table(
    index=['stay_id', 'offset_min'],
    columns='mimic_lab_name',
    values='lab_value_validated',
    aggfunc='first'  # Should be only one value after groupby
).reset_index()

# Flatten column names
labs_wide.columns.name = None

print(f"  Pivoted: {len(labs_wide):,} time points")

# ============================================================================
# Step 5: Save
# ============================================================================
print("\n" + "=" * 60)
print("Step 5: Save")
print("=" * 60)

output_path = DATA_DIR / 'labs_extracted.csv'
labs_wide.to_csv(output_path, index=False)

print(f"\n✓ Labs saved: {output_path}")
print(f"  Rows: {len(labs_wide):,}")
print(f"  Patients: {labs_wide['stay_id'].nunique():,}")

# Summary
print(f"\n=== Labs Summary ===")
for col in required_labs.keys():
    if col in labs_wide.columns:
        count = labs_wide[col].notna().sum()
        pct = (count / len(labs_wide)) * 100
        if count > 0:
            mean = labs_wide[col].mean()
            print(f"  {col}: {count:,} values ({pct:.1f}%), mean={mean:.2f}")
        else:
            print(f"  {col}: {count:,} values ({pct:.1f}%)")

print("\n=== eICU Labs Extraction Complete ===")
