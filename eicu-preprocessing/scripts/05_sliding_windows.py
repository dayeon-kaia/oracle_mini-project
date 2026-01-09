#!/usr/bin/env python3
"""
eICU Sliding Window Generation - OPTIMIZED
===========================================

MIMIC과 동일한 sliding window 생성 (최적화된 버전)
- Vectorized operations 사용
- 대량 데이터 처리 속도 개선

출력: sliding_windows.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import timedelta

# Paths
DATA_DIR = Path('../data/processed')

print("=" * 60)
print("eICU Sliding Window Generation (Optimized)")
print("=" * 60)

# ============================================================================
# Step 1: Load all data
# ============================================================================
print("\nStep 1: Load data")

cohort = pd.read_csv(DATA_DIR / 'cohort_base.csv', parse_dates=['intime', 'outtime'])
vitals = pd.read_csv(DATA_DIR / 'vitals_extracted.csv')
labs = pd.read_csv(DATA_DIR / 'labs_extracted.csv')
events = pd.read_csv(DATA_DIR / 'events_extracted.csv', parse_dates=['vent_start_time', 'pressor_start_time'])

print(f"  Cohort: {len(cohort):,} patients")
print(f"  Vitals: {len(vitals):,} records")
print(f"  Labs: {len(labs):,} records")
print(f"  Events: {len(events):,} patients")

# ============================================================================
# Step 2: Generate candidate windows
# ============================================================================
print("\nStep 2: Generate sliding windows")

windows = []

for _, patient in cohort.iterrows():
    stay_id = patient['stay_id']
    intime = patient['intime']
    outtime = patient['outtime']
    
    # Get event times
    patient_events = events[events['stay_id'] == stay_id]
    vent_time = patient_events['vent_start_time'].iloc[0] if len(patient_events) > 0 else pd.NaT
    pressor_time = patient_events['pressor_start_time'].iloc[0] if len(patient_events) > 0 else pd.NaT
    
    # Generate windows: 6h to 72h, stride 2h
    for obs_hour in range(6, 73, 2):
        obs_end = intime + timedelta(hours=obs_hour)
        obs_start = obs_end - timedelta(hours=6)
        
        # Check if still in hospital
        if obs_end > outtime:
            break
        
        # Event censoring
        if pd.notna(vent_time) and obs_end >= vent_time:
            break
        if pd.notna(pressor_time) and obs_end >= pressor_time:
            break
        
        # Calculate labels
        vent_6h = int(pd.notna(vent_time) and vent_time > obs_end and vent_time <= obs_end + timedelta(hours=6))
        vent_12h = int(pd.notna(vent_time) and vent_time > obs_end and vent_time <= obs_end + timedelta(hours=12))
        vent_24h = int(pd.notna(vent_time) and vent_time > obs_end and vent_time <= obs_end + timedelta(hours=24))
        
        pressor_6h = int(pd.notna(pressor_time) and pressor_time > obs_end and pressor_time <= obs_end + timedelta(hours=6))
        pressor_12h = int(pd.notna(pressor_time) and pressor_time > obs_end and pressor_time <= obs_end + timedelta(hours=12))
        pressor_24h = int(pd.notna(pressor_time) and pressor_time > obs_end and pressor_time <= obs_end + timedelta(hours=24))
        
        window = {
            'stay_id': stay_id,
            'observation_hour': obs_hour,
            'observation_start': obs_start,
            'observation_end': obs_end,
            'vent_next_6h': vent_6h,
            'vent_next_12h': vent_12h,
            'vent_next_24h': vent_24h,
            'pressor_next_6h': pressor_6h,
            'pressor_next_12h': pressor_12h,
            'pressor_next_24h': pressor_24h,
            'composite_next_6h': max(vent_6h, pressor_6h),
            'composite_next_12h': max(vent_12h, pressor_12h),
            'composite_next_24h': max(vent_24h, pressor_24h)
        }
        
        windows.append(window)

windows_df = pd.DataFrame(windows)

print(f"  Generated {len(windows_df):,} windows")
print(f"  Patients with windows: {windows_df['stay_id'].nunique():,}")

# ============================================================================
# Step 3: Extract features - OPTIMIZED with vectorization
# ============================================================================
print("\nStep 3: Extract features (optimized)...")

# Add offset columns for faster filtering
cohort_offsets = cohort[['stay_id', 'intime']].copy()
windows_df = windows_df.merge(cohort_offsets, on='stay_id')

# Calculate offset ranges for each window
windows_df['start_offset'] = (windows_df['observation_start'] - windows_df['intime']).dt.total_seconds() / 60
windows_df['end_offset'] = (windows_df['observation_end'] - windows_df['intime']).dt.total_seconds() / 60

# Process in batches by stay_id for efficiency
feature_list = []

for stay_id in windows_df['stay_id'].unique():
    if len(feature_list) % 100 == 0:
        print(f"    Processing patient {len(feature_list)}/{windows_df['stay_id'].nunique()}...")
    
    # Get patient data
    patient_windows = windows_df[windows_df['stay_id'] == stay_id]
    patient_cohort = cohort[cohort['stay_id'] == stay_id].iloc[0]
    
    # Get vitals for this patient
    patient_vitals = vitals[vitals['stay_id'] == stay_id]
    
    # Get labs for this patient
    patient_labs = labs[labs['stay_id'] == stay_id]
    
    # For each window of this patient
    for _, window in patient_windows.iterrows():
        features = {}
        
        # Filter vitals in window
        window_vitals = patient_vitals[
            (patient_vitals['offset_min'] >= window['start_offset']) &
            (patient_vitals['offset_min'] <= window['end_offset'])
        ]
        
        # Vitals: median
        for col in ['hr', 'rr', 'spo2', 'temp', 'sbp', 'dbp', 'mbp']:
            features[col] = window_vitals[col].median() if col in window_vitals.columns else np.nan
        
        # Filter labs in window
        window_labs = patient_labs[
            (patient_labs['offset_min'] >= window['start_offset']) &
            (patient_labs['offset_min'] <= window['end_offset'])
        ]
        
        # Labs: latest value
        for col in ['lactate', 'creatinine', 'wbc', 'platelets', 'potassium', 'sodium']:
            if col in window_labs.columns and len(window_labs) > 0:
                features[col] = window_labs.sort_values('offset_min')[col].iloc[-1]
            else:
                features[col] = np.nan
        
        # Demographics
        features['age'] = patient_cohort['age']
        features['gender_male'] = 1 if patient_cohort['gender'] == 'Male' else 0
        features['hours_in_icu'] = window['observation_hour']
        
        feature_list.append(features)

features_df = pd.DataFrame(feature_list)

# Combine
final_df = pd.concat([
    windows_df[['stay_id', 'observation_hour', 'observation_start', 'observation_end',
                'vent_next_6h', 'vent_next_12h', 'vent_next_24h',
                'pressor_next_6h', 'pressor_next_12h', 'pressor_next_24h',
                'composite_next_6h', 'composite_next_12h', 'composite_next_24h']].reset_index(drop=True),
    features_df.reset_index(drop=True)
], axis=1)

print(f"  ✓ Features extracted")

# ============================================================================
# Step 4: Save
# ============================================================================
print("\n" + "=" * 60)
print("Step 4: Save")
print("=" * 60)

output_path = DATA_DIR / 'sliding_windows.csv'
final_df.to_csv(output_path, index=False)

print(f"\n✓ Sliding windows saved: {output_path}")
print(f"  Rows: {len(final_df):,}")
print(f"  Columns: {len(final_df.columns)}")
print(f"  Patients: {final_df['stay_id'].nunique():,}")

# Summary
print(f"\n=== Label Distribution ===")
for label in ['composite_next_6h', 'composite_next_12h', 'composite_next_24h']:
    pos = final_df[label].sum()
    pct = (pos / len(final_df)) * 100
    print(f"  {label}: {pos:,} positive ({pct:.2f}%)")

print("\n=== eICU Sliding Window Generation Complete ===")
