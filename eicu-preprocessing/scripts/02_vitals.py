#!/usr/bin/env python3
"""
eICU Vitals Extraction
======================

vitalPeriodic + vitalAperiodic 테이블에서 vital signs 추출
MIMIC chartevents 형식으로 변환

필요 변수:
- Heart Rate (HR)
- Respiratory Rate (RR)
- SpO2
- Temperature
- Systolic BP (SBP)
- Diastolic BP (DBP)
- Mean BP (MBP)

출력: vitals_extracted.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths
EICU_DIR = Path('../../eicu/eicu-collaborative-research-database-demo-2.0.1')
DATA_DIR = Path('../data/processed')

print("=" * 60)
print("eICU Vitals Extraction")
print("=" * 60)

# Load cohort
print("\nLoading cohort...")
cohort = pd.read_csv(DATA_DIR / 'cohort_base.csv')
print(f"  Cohort: {len(cohort):,} patients")

# ============================================================================
# Step 1: Load vitalPeriodic (automated measurements)
# ============================================================================
print("\nStep 1: Load vitalPeriodic")

vital_periodic = pd.read_csv(EICU_DIR / 'vitalPeriodic.csv.gz', compression='gzip')
print(f"  Total records: {len(vital_periodic):,}")

# Filter to cohort patients only
vital_periodic = vital_periodic[vital_periodic['patientunitstayid'].isin(cohort['stay_id'])]
print(f"  After cohort filter: {len(vital_periodic):,}")

# Rename columns
vital_periodic = vital_periodic.rename(columns={
    'patientunitstayid': 'stay_id',
    'observationoffset': 'offset_min'
})

# Select relevant columns
vital_cols = ['stay_id', 'offset_min', 'temperature', 'sao2', 'heartrate', 
              'respiration', 'systemicsystolic', 'systemicdiastolic', 'systemicmean']
vital_periodic = vital_periodic[vital_cols].copy()

# ============================================================================  
# Step 2: Load vitalAperiodic (manual measurements)
# ============================================================================
print("\nStep 2: Load vitalAperiodic")

vital_aperiodic = pd.read_csv(EICU_DIR / 'vitalAperiodic.csv.gz', compression='gzip')
print(f"  Total records: {len(vital_aperiodic):,}")

# Filter to cohort
vital_aperiodic = vital_aperiodic[vital_aperiodic['patientunitstayid'].isin(cohort['stay_id'])]
print(f"  After cohort filter: {len(vital_aperiodic):,}")

# Rename
vital_aperiodic = vital_aperiodic.rename(columns={
    'patientunitstayid': 'stay_id',
    'observationoffset': 'offset_min'
})

# vitalAperiodic has different structure - need to pivot
# It has 'noninvasivesystolic', 'noninvasivediastolic', 'noninvasivemean'
aperiodic_cols = ['stay_id', 'offset_min', 'temperature', 'heartrate', 'respiration',
                  'noninvasivesystolic', 'noninvasivediastolic', 'noninvasivemean']

# Some columns might not exist, filter only existing ones
existing_cols = [col for col in aperiodic_cols if col in vital_aperiodic.columns]
vital_aperiodic = vital_aperiodic[existing_cols].copy()

# Rename to match periodic
rename_map = {
    'noninvasivesystolic': 'systemicsystolic',
    'noninvasivediastolic': 'systemicdiastolic', 
    'noninvasivemean': 'systemicmean'
}
vital_aperiodic = vital_aperiodic.rename(columns=rename_map)

# ============================================================================
# Step 3: Combine periodic and aperiodic
# ============================================================================
print("\nStep 3: Combine periodic and aperiodic")

# Combine
vitals = pd.concat([vital_periodic, vital_aperiodic], ignore_index=True)
print(f"  Combined: {len(vitals):,} records")

# ============================================================================
# Step 4: Convert to MIMIC naming
# ============================================================================
print("\nStep 4: Convert to MIMIC naming")

# eICU → MIMIC mapping
vitals = vitals.rename(columns={
    'heartrate': 'hr',
    'respiration': 'rr',
    'sao2': 'spo2',
    'temperature': 'temp',
    'systemicsystolic': 'sbp',
    'systemicdiastolic': 'dbp',
    'systemicmean': 'mbp'
})

# ============================================================================
# Step 5: Data cleaning and validation
# ============================================================================
print("\nStep 5: Data cleaning")

# Temperature: eICU stores in Celsius (like MIMIC)
# Range check: 25-45°C
if 'temp' in vitals.columns:
    before = vitals['temp'].notna().sum()
    vitals.loc[vitals['temp'] < 25, 'temp'] = np.nan
    vitals.loc[vitals['temp'] > 45, 'temp'] = np.nan
    after = vitals['temp'].notna().sum()
    print(f"  Temperature: {before:,} → {after:,} (removed {before-after:,} outliers)")

# Heart Rate: 0-300 bpm
if 'hr' in vitals.columns:
    before = vitals['hr'].notna().sum()
    vitals.loc[vitals['hr'] <= 0, 'hr'] = np.nan
    vitals.loc[vitals['hr'] > 300, 'hr'] = np.nan
    after = vitals['hr'].notna().sum()
    print(f"  Heart Rate: {before:,} → {after:,} (removed {before-after:,} outliers)")

# SpO2: 0-100%
if 'spo2' in vitals.columns:
    before = vitals['spo2'].notna().sum()
    vitals.loc[vitals['spo2'] <= 0, 'spo2'] = np.nan
    vitals.loc[vitals['spo2'] > 100, 'spo2'] = np.nan
    after = vitals['spo2'].notna().sum()
    print(f"  SpO2: {before:,} → {after:,} (removed {before-after:,} outliers)")

# Blood Pressure: SBP 0-300, DBP 0-200, MBP 0-250
for bp_col, max_val in [('sbp', 300), ('dbp', 200), ('mbp', 250)]:
    if bp_col in vitals.columns:
        before = vitals[bp_col].notna().sum()
        vitals.loc[vitals[bp_col] <= 0, bp_col] = np.nan
        vitals.loc[vitals[bp_col] > max_val, bp_col] = np.nan
        after = vitals[bp_col].notna().sum()
        print(f"  {bp_col.upper()}: {before:,} → {after:,} (removed {before-after:,} outliers)")

# ============================================================================
# Step 6: Save
# ============================================================================
print("\n" + "=" * 60)
print("Step 6: Save")
print("=" * 60)

output_path = DATA_DIR / 'vitals_extracted.csv'
vitals.to_csv(output_path, index=False)

print(f"\n✓ Vitals saved: {output_path}")
print(f"  Rows: {len(vitals):,}")
print(f"  Patients: {vitals['stay_id'].nunique():,}")

# Summary
print(f"\n=== Vitals Summary ===")
for col in ['hr', 'rr', 'spo2', 'temp', 'sbp', 'dbp', 'mbp']:
    if col in vitals.columns:
        count = vitals[col].notna().sum()
        pct = (count / len(vitals)) * 100
        if count > 0:
            mean = vitals[col].mean()
            print(f"  {col}: {count:,} values ({pct:.1f}%), mean={mean:.1f}")
        else:
            print(f"  {col}: {count:,} values ({pct:.1f}%)")

print("\n=== eICU Vitals Extraction Complete ===")
