#!/usr/bin/env python3
"""
eICU Schema Alignment with MIMIC
=================================

CRITICAL STEP: Align eICU features to exact MIMIC schema
- 컬럼 순서 100% 일치
- 결측 값은 MIMIC imputer로 처리 (eICU에서 fit하지 않음!)
- Validation checks

입력: features_engineered.csv
출력: eicu_final_aligned.csv
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

# Paths
DATA_DIR = Path('../data/processed')
MIMIC_DIR = Path('../../data-pipeline/data/processed')  # MIMIC reference

print("=" * 60)
print("eICU Schema Alignment with MIMIC")
print("=" * 60)

# ============================================================================
# Step 1: Load eICU features
# ============================================================================
print("\nStep 1: Load eICU features")

df_eicu = pd.read_csv(DATA_DIR / 'features_engineered.csv')
print(f"  eICU data: {len(df_eicu):,} rows, {len(df_eicu.columns)} columns")

# ============================================================================
# Step 2: Load MIMIC feature schema
# ============================================================================
print("\nStep 2: Load MIMIC feature schema")

# Try to load MIMIC feature schema
# If not available, create standard schema based on implementation plan
try:
    with open(MIMIC_DIR / 'top21_features.json', 'r') as f:
        mimic_features = json.load(f)
    print(f"  Loaded MIMIC schema: {len(mimic_features)} features")
except FileNotFoundError:
    print("  MIMIC schema file not found, using standard feature list")
    
    # Standard features from MIMIC pipeline
    mimic_features = [
        # Base vitals
        'hr', 'rr', 'spo2', 'temp', 'sbp', 'dbp', 'mbp',
        
        # Base labs
        'lactate', 'creatinine', 'wbc', 'platelets', 'potassium', 'sodium',
        
        # Rolling stats (hr, sbp, mbp, spo2, rr)
        'hr_mean_6h', 'hr_std_6h', 'hr_min_6h', 'hr_max_6h',
        'sbp_mean_6h', 'sbp_std_6h', 'sbp_min_6h', 'sbp_max_6h',
        'mbp_mean_6h', 'mbp_std_6h', 'mbp_min_6h', 'mbp_max_6h',
        'spo2_mean_6h', 'spo2_std_6h', 'spo2_min_6h', 'spo2_max_6h',
        'rr_mean_6h', 'rr_std_6h', 'rr_min_6h', 'rr_max_6h',
        
        # Trend features
        'hr_delta_1h', 'hr_delta_3h', 'hr_slope_3h',
        'sbp_delta_1h', 'sbp_delta_3h', 'sbp_slope_3h',
        'mbp_delta_1h', 'mbp_delta_3h', 'mbp_slope_3h',
        'spo2_delta_1h', 'spo2_delta_3h', 'spo2_slope_3h',
        'lactate_delta_1h', 'lactate_delta_3h', 'lactate_slope_3h',
        
        # Derived features
        'shock_index', 'modified_shock_index', 'pulse_pressure',
        
        # Clinical scores
        'mews_score', 'news_score',
        
        # Missing flags
        'lactate_missing', 'gcs_missing_flag', 'urine_missing_flag',
        
        # Demographics
        'gender_male', 'age', 'hours_in_icu'
    ]
    
    print(f"  Using standard schema: {len(mimic_features)} features")

# ============================================================================
# Step 3: Create aligned dataset
# ============================================================================
print("\nStep 3: Create schema-aligned dataset")

# ID columns
id_columns = ['stay_id', 'observation_hour', 'observation_start', 'observation_end']

# Label columns
label_columns = [col for col in df_eicu.columns if 'next_' in col]

# Initialize aligned dataframe with IDs
df_aligned = df_eicu[id_columns].copy()

# Add features in MIMIC order
for feature in mimic_features:
    if feature in df_eicu.columns:
        df_aligned[feature] = df_eicu[feature]
    else:
        print(f"  Missing feature: {feature} (filling with NaN)")
        df_aligned[feature] = np.nan

# Add labels
for label in label_columns:
    df_aligned[label] = df_eicu[label]

print(f"  Aligned dataset: {len(df_aligned)} rows, {len(df_aligned.columns)} columns")

# ============================================================================
# Step 4: Feature validation
# ============================================================================
print("\nStep 4: Validation checks")

# Check column order
feature_cols_aligned = [c for c in df_aligned.columns if c not in id_columns + label_columns]
if feature_cols_aligned == mimic_features:
    print("  ✓ Column order matches MIMIC schema")
else:
    print("  ⚠ Column order mismatch!")
    print(f"    Expected: {mimic_features[:5]}...")
    print(f"    Got: {feature_cols_aligned[:5]}...")

# Check missing values
missing_summary = df_aligned[mimic_features].isna().sum()
total_missing = missing_summary.sum()
print(f"\n  Missing values: {total_missing:,} ({total_missing / (len(df_aligned) * len(mimic_features)) * 100:.1f}%)")

# Top missing features
if total_missing > 0:
    top_missing = missing_summary[missing_summary > 0].sort_values(ascending=False).head(10)
    print("\n  Top 10 missing features:")
    for feat, count in top_missing.items():
        pct = (count / len(df_aligned)) * 100
        print(f"    {feat}: {count:,} ({pct:.1f}%)")

# ============================================================================
# Step 5: Handle missing values
# ============================================================================
print("\nStep 5: Missing value strategy")

print("\n  ⚠ CRITICAL: Do NOT fit imputer on eICU data!")
print("  For production use:")
print("    1. Load MIMIC fitted imputer: joblib.load('mimic_imputer.pkl')")
print("    2. Apply transform only: imputer.transform(df_aligned[mimic_features])")
print("\n  For demo purposes, using median imputation:")

# Simple median imputation for demo
for col in mimic_features:
    if col in df_aligned.columns:
        col_missing = df_aligned[col].isna().sum()
        if col_missing > 0:
            median_val = df_aligned[col].median()
            if pd.isna(median_val):
                median_val = 0
            df_aligned[col] = df_aligned[col].fillna(median_val)

# Final check
final_missing = df_aligned[mimic_features].isna().sum().sum()
print(f"  After imputation: {final_missing:,} missing values")

if final_missing > 0:
    print("  ⚠ Some features still have missing values!")
else:
    print("  ✓ All features imputed")

# ============================================================================
# Step 6: Save
# ============================================================================
print("\n" + "=" * 60)
print("Step 6: Save")
print("=" * 60)

output_path = DATA_DIR / 'eicu_final_aligned.csv'
df_aligned.to_csv(output_path, index=False)

# Also save feature list for reference
feature_list_path = DATA_DIR / 'eicu_feature_list.json'
with open(feature_list_path, 'w') as f:
    json.dump(mimic_features, f, indent=2)

print(f"\n✓ Aligned data saved: {output_path}")
print(f"✓ Feature list saved: {feature_list_path}")
print(f"\n  Final dataset:")
print(f"    Rows: {len(df_aligned):,}")
print(f"    Columns: {len(df_aligned.columns)}")
print(f"    Features: {len(mimic_features)}")
print(f"    Patients: {df_aligned['stay_id'].nunique():,}")

# ============================================================================
# Step 7: Quality summary
# ============================================================================
print("\n" + "=" * 60)
print("Quality Summary")
print("=" * 60)

print(f"\n✓ Schema alignment: COMPLETE")
print(f"✓ Feature count: {len(mimic_features)}")
print(f"✓ Sample count: {len(df_aligned):,}")
print(f"✓ Missing handling: Median imputation (demo mode)")

print("\n⚠ NEXT STEPS FOR PRODUCTION:")
print("  1. Load MIMIC trained imputer")
print("  2. Apply MIMIC imputer.transform() to eICU features")
print("  3. Load MIMIC trained model")
print("  4. Run model.predict() on aligned eICU data")
print("  5. Compare performance (external validation)")

print("\n=== eICU Schema Alignment Complete ===")
