#!/usr/bin/env python3
"""
eICU Cohort Generation
======================

MIMIC-IV와 동일한 코호트 기준 적용:
- 성인 (age >= 18)
- 첫 ICU 입실
- ICU 재실 >= 24시간

출력: cohort_base.csv
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path

# Paths
EICU_DIR = Path('../../eicu/eicu-collaborative-research-database-demo-2.0.1')
OUTPUT_DIR = Path('../data/processed')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("eICU Cohort Generation")
print("=" * 60)

# ============================================================================
# Step 1: Load patient table
# ============================================================================
print("\nStep 1: Load patient table")

patient = pd.read_csv(EICU_DIR / 'patient.csv.gz', compression='gzip')
print(f"  Total patient records: {len(patient):,}")

# ============================================================================
# Step 2: Parse age (eICU stores age as string)
# ============================================================================
print("\nStep 2: Parse age")

def parse_age(age_str):
    """
    eICU age format:
    - '> 89' → 90 (MIMIC과 동일 처리)
    - Numeric string → int
    """
    if pd.isna(age_str):
        return np.nan
    if isinstance(age_str, str):
        if '> 89' in age_str or '>89' in age_str:
            return 90
        try:
            return int(age_str)
        except:
            return np.nan
    return int(age_str)

patient['age'] = patient['age'].apply(parse_age)

# Filter: age >= 18
before = len(patient)
patient = patient[patient['age'] >= 18].copy()
after = len(patient)
print(f"  Age >= 18: {after:,} stays ({before - after:,} excluded)")

# ============================================================================
# Step 3: Calculate LOS (Length of Stay)
# ============================================================================
print("\nStep 3: Calculate LOS")

# eICU uses offset in minutes from hospital admit
# Note: patient table doesn't have unitadmitoffset, using hospital offsets
patient['los_hours'] = (patient['hospitaldischargeoffset'] - patient['hospitaladmitoffset']) / 60.0

# Filter: LOS >= 24 hours
before = len(patient)
patient = patient[patient['los_hours'] >= 24].copy()
after = len(patient)
print(f"  LOS >= 24h: {after:,} stays ({before - after:,} excluded)")

# ============================================================================
# Step 4: First ICU stay only
# ============================================================================
print("\nStep 4: First ICU stay only")

# eICU: patienthealthsystemstayid identifies hospital admission
# Multiple ICU stays within same hospital admission → take first
patient = patient.sort_values(['patienthealthsystemstayid', 'hospitaladmitoffset'])
patient['icu_seq'] = patient.groupby('patienthealthsystemstayid').cumcount() + 1

before = len(patient)
patient = patient[patient['icu_seq'] == 1].copy()
after = len(patient)
print(f"  First ICU stay: {after:,} stays ({before - after:,} excluded)")

# ============================================================================
# Step 5: Create normalized timeline
# ============================================================================
print("\nStep 5: Create normalized timeline")

# Create virtual timestamps (hospital admit = t0)
# This allows us to use same sliding window logic as MIMIC
BASE_TIME = pd.Timestamp('2100-01-01 00:00:00')

patient['intime'] = BASE_TIME + pd.to_timedelta(patient['hospitaladmitoffset'], unit='m')
patient['outtime'] = BASE_TIME + pd.to_timedelta(patient['hospitaldischargeoffset'], unit='m')

# Get patient weight (needed for urine output calculation)
# eICU: admissionweight in kg
patient['weight_kg'] = patient['admissionweight']

# Handle missing weights (use median)
median_weight = patient['weight_kg'].median()
patient['weight_kg'] = patient['weight_kg'].fillna(median_weight)
print(f"  Weight: median={median_weight:.1f} kg, missing filled")

# ============================================================================
# Step 6: Select final columns
# ============================================================================
print("\nStep 6: Select final columns")

cohort_cols = [
    'patientunitstayid',      # eICU stay identifier (= stay_id)
    'patienthealthsystemstayid',  # Hospital admission ID
    'age',
    'gender',
    'intime',
    'outtime',
    'los_hours',
    'weight_kg',
    'hospitaladmitoffset',        # Keep for time alignment
    'hospitaldischargeoffset'
]

cohort = patient[cohort_cols].copy()
cohort = cohort.rename(columns={'patientunitstayid': 'stay_id'})

# ============================================================================
# Step 7: Save
# ============================================================================
print("\n" + "=" * 60)
print("Step 7: Save")
print("=" * 60)

output_path = OUTPUT_DIR / 'cohort_base.csv'
cohort.to_csv(output_path, index=False)

print(f"\n✓ Cohort saved: {output_path}")
print(f"  Rows: {len(cohort):,}")
print(f"  Columns: {len(cohort.columns)}")
print(f"  Unique patients: {cohort['stay_id'].nunique():,}")

# Summary statistics
print(f"\n=== Cohort Summary ===")
print(f"  Age: {cohort['age'].mean():.1f} ± {cohort['age'].std():.1f} years")
print(f"  Gender: {(cohort['gender'] == 'Male').sum():,} Male ({(cohort['gender'] == 'Male').mean()*100:.1f}%)")
print(f"  LOS: {cohort['los_hours'].mean():.1f} ± {cohort['los_hours'].std():.1f} hours")
print(f"  Weight: {cohort['weight_kg'].mean():.1f} ± {cohort['weight_kg'].std():.1f} kg")

print("\n=== eICU Cohort Generation Complete ===")
