#!/usr/bin/env python3
"""
eICU Feature Engineering
=========================

MIMIC과 동일한 feature engineering 적용:
- Rolling 통계량 (mean, std, min, max)
- 추세 피처 (delta, slope)
- 파생 피처 (Shock Index, Pulse Pressure)
- 중증도 점수 (MEWS, NEWS)

출력: features_engineered.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths
DATA_DIR = Path('../data/processed')

print("=" * 60)
print("eICU Feature Engineering")
print("=" * 60)

# ============================================================================
# Step 1: Load sliding windows
# ============================================================================
print("\nStep 1: Load data")

df = pd.read_csv(DATA_DIR / 'sliding_windows.csv', parse_dates=['observation_start', 'observation_end'])
print(f"  Total windows: {len(df):,}")
print(f"  Columns before: {len(df.columns)}")

# Sort by stay and time
df = df.sort_values(['stay_id', 'observation_hour']).reset_index(drop=True)

# ============================================================================
# Step 2: Rolling statistics
# ============================================================================
print("\nStep 2: Rolling statistics (6 windows)")

rolling_features = ['hr', 'sbp', 'mbp', 'spo2', 'rr']
rolling_stats = ['mean', 'std', 'min', 'max']

for feat in rolling_features:
    if feat in df.columns:
        grouped = df.groupby('stay_id')[feat]
        
        df[f'{feat}_mean_6h'] = grouped.transform(lambda x: x.rolling(6, min_periods=1).mean())
        df[f'{feat}_std_6h'] = grouped.transform(lambda x: x.rolling(6, min_periods=1).std())
        df[f'{feat}_min_6h'] = grouped.transform(lambda x: x.rolling(6, min_periods=1).min())
        df[f'{feat}_max_6h'] = grouped.transform(lambda x: x.rolling(6, min_periods=1).max())

# Fill std NaN with 0 (first window)
std_cols = [col for col in df.columns if '_std_6h' in col]
df[std_cols] = df[std_cols].fillna(0)

print(f"  Added {len(rolling_features) * len(rolling_stats)} rolling features")

# ============================================================================
# Step 3: Trend features (delta, slope)
# ============================================================================
print("\nStep 3: Trend features")

trend_features = ['hr', 'sbp', 'mbp', 'spo2', 'lactate']

for feat in trend_features:
    if feat in df.columns:
        grouped = df.groupby('stay_id')[feat]
        
        # Delta
        df[f'{feat}_delta_1h'] = grouped.diff(1)
        df[f'{feat}_delta_3h'] = grouped.diff(3)
        
        # Slope
        def calc_slope(x):
            if len(x) < 2:
                return 0
            try:
                return np.polyfit(range(len(x)), x, 1)[0]
            except:
                return 0
        
        df[f'{feat}_slope_3h'] = grouped.transform(
            lambda x: x.rolling(3, min_periods=2).apply(calc_slope, raw=True)
        )

# Fill NaN with 0
delta_slope_cols = [col for col in df.columns if '_delta_' in col or '_slope_' in col]
df[delta_slope_cols] = df[delta_slope_cols].fillna(0)

print(f"  Added {len(trend_features) * 3} trend features")

# ============================================================================
# Step 4: Derived features
# ============================================================================
print("\nStep 4: Derived features")

# Shock Index
if 'hr' in df.columns and 'sbp' in df.columns:
    df['shock_index'] = df['hr'] / df['sbp'].replace(0, np.nan)
    df['shock_index'] = df['shock_index'].clip(0, 3).fillna(1)

# Modified Shock Index
if 'hr' in df.columns and 'mbp' in df.columns:
    df['modified_shock_index'] = df['hr'] / df['mbp'].replace(0, np.nan)
    df['modified_shock_index'] = df['modified_shock_index'].clip(0, 5).fillna(1)

# Pulse Pressure
if 'sbp' in df.columns and 'dbp' in df.columns:
    df['pulse_pressure'] = df['sbp'] - df['dbp']
    df['pulse_pressure'] = df['pulse_pressure'].clip(0, 150)

print("  Added 3 derived features")

# ============================================================================
# Step 5: Clinical scores (MEWS, NEWS)
# ============================================================================
print("\nStep 5: Clinical scores")

def calc_mews_vectorized(df):
    """Modified Early Warning Score"""
    score = pd.Series(0, index=df.index)
    
    # HR
    if 'hr' in df.columns:
        hr = df['hr']
        score += np.where((hr < 40) | (hr > 130), 3,
                 np.where((hr < 50) | (hr > 110), 2,
                 np.where((hr < 60) | (hr > 100), 1, 0)))
    
    # SBP
    if 'sbp' in df.columns:
        sbp = df['sbp']
        score += np.where(sbp < 70, 3,
                 np.where(sbp < 80, 2,
                 np.where(sbp < 100, 1, 0)))
    
    # RR
    if 'rr' in df.columns:
        rr = df['rr']
        score += np.where((rr < 9) | (rr > 30), 3,
                 np.where(rr > 25, 2,
                 np.where((rr < 12) | (rr > 20), 1, 0)))
    
    # Temp
    if 'temp' in df.columns:
        temp = df['temp']
        score += np.where((temp < 35) | (temp > 39), 2,
                 np.where((temp < 36) | (temp > 38), 1, 0))
    
    return score

def calc_news_vectorized(df):
    """National Early Warning Score"""
    score = pd.Series(0, index=df.index)
    
    # SpO2
    if 'spo2' in df.columns:
        spo2 = df['spo2']
        score += np.where(spo2 <= 91, 3,
                 np.where(spo2 <= 93, 2,
                 np.where(spo2 <= 95, 1, 0)))
    
    # SBP
    if 'sbp' in df.columns:
        sbp = df['sbp']
        score += np.where((sbp <= 90) | (sbp >= 220), 3,
                 np.where(sbp <= 100, 2,
                 np.where(sbp <= 110, 1, 0)))
    
    # HR
    if 'hr' in df.columns:
        hr = df['hr']
        score += np.where((hr <= 40) | (hr >= 131), 3,
                 np.where(hr >= 111, 2,
                 np.where((hr <= 50) | (hr >= 91), 1, 0)))
    
    return score

df['mews_score'] = calc_mews_vectorized(df)
df['news_score'] = calc_news_vectorized(df)

print("  Added 2 clinical scores")

# ============================================================================
# Step 6: Missing flags
# ============================================================================
print("\nStep 6: Missing flags")

if 'lactate' in df.columns:
    df['lactate_missing'] = df['lactate'].isna().astype(int)

# Add placeholder flags for GCS and urine (not available in demo)
df['gcs_missing_flag'] = 1  # Always missing in demo
df['urine_missing_flag'] = 1  # Demo doesn't have urine data

print("  Added 3 missing flags")

# ============================================================================
# Step 7: Save
# ============================================================================
print("\n" + "=" * 60)
print("Step 7: Save")
print("=" * 60)

output_path = DATA_DIR / 'features_engineered.csv'
df.to_csv(output_path, index=False)

print(f"\n✓ Features saved: {output_path}")
print(f"  Rows: {len(df):,}")
print(f"  Columns after: {len(df.columns)} (added {len(df.columns) - 30} features)")

# Summary of added features
rolling_count = len([c for c in df.columns if '_6h' in c and c not in ['composite_next_6h']])
trend_count = len([c for c in df.columns if '_delta_' in c or '_slope_' in c])
derived_count = 3  # shock indices + pulse pressure
score_count = 2  # MEWS + NEWS
flag_count = 3  # missing flags

print(f"\n=== Feature Engineering Summary ===")
print(f"  Rolling stats: {rolling_count}")
print(f"  Trend features: {trend_count}")
print(f"  Derived features: {derived_count}")
print(f"  Clinical scores: {score_count}")
print(f"  Missing flags: {flag_count}")
print(f"  Total added: {rolling_count + trend_count + derived_count + score_count + flag_count}")

print("\n=== eICU Feature Engineering Complete ===")
