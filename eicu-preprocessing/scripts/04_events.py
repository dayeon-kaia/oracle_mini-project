#!/usr/bin/env python3
"""
eICU Events Extraction
======================

Ventilation and Pressor start times 추출
MIMIC procedureevents/inputevents 형식으로 변환

Events:
- Ventilation start (invasive only)
- Pressor start (vasopressors)

출력: events_extracted.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths
EICU_DIR = Path('../../eicu/eicu-collaborative-research-database-demo-2.0.1')
DATA_DIR = Path('../data/processed')

print("=" * 60)
print("eICU Events Extraction")
print("=" * 60)

# Load cohort
print("\nLoading cohort...")
cohort = pd.read_csv(DATA_DIR / 'cohort_base.csv')
print(f"  Cohort: {len(cohort):,} patients")

# ============================================================================
# Step 1: Ventilation events from respiratoryCare
# ============================================================================
print("\nStep 1: Extract ventilation events")

try:
    resp_care = pd.read_csv(EICU_DIR / 'respiratoryCare.csv.gz', compression='gzip')
    print(f"  Total respiratoryCare records: {len(resp_care):,}")
    
    # Filter to cohort
    resp_care = resp_care[resp_care['patientunitstayid'].isin(cohort['stay_id'])]
    print(f"  After cohort filter: {len(resp_care):,}")
    
    # Invasive ventilation only
    # airwayType: 'Oral ETT', 'Nasal ETT', 'Tracheostomy'
    invasive_types = ['Oral ETT', 'Nasal ETT', 'Tracheostomy']
    
    if 'airwaytype' in resp_care.columns:
        vent_events = resp_care[resp_care['airwaytype'].isin(invasive_types)].copy()
        
        # Get first ventilation time per patient
        vent_events = vent_events.rename(columns={
            'patientunitstayid': 'stay_id',
            'respcarestatusoffset': 'offset_min'
        })
        
        # Take minimum offset (first vent start)
        vent_start = vent_events.groupby('stay_id')['offset_min'].min().reset_index()
        vent_start = vent_start.rename(columns={'offset_min': 'vent_start_offset'})
        
        print(f"  Ventilation starts: {len(vent_start):,} patients")
    else:
        print("  Warning: airwaytype column not found, skipping ventilation")
        vent_start = pd.DataFrame(columns=['stay_id', 'vent_start_offset'])
        
except FileNotFoundError:
    print("  respiratoryCare.csv not found, skipping ventilation")
    vent_start = pd.DataFrame(columns=['stay_id', 'vent_start_offset'])

# ============================================================================
# Step 2: Pressor events from infusionDrug
# ============================================================================
print("\nStep 2: Extract pressor events")

try:
    infusion = pd.read_csv(EICU_DIR / 'infusionDrug.csv.gz', compression='gzip')
    print(f"  Total infusionDrug records: {len(infusion):,}")
    
    # Filter to cohort
    infusion = infusion[infusion['patientunitstayid'].isin(cohort['stay_id'])]
    print(f"  After cohort filter: {len(infusion):,}")
    
    # Vasopressors list (case-insensitive)
    vasopressors = [
        'norepinephrine', 'norepi', 'levophed',
        'epinephrine', 'epi', 'adrenaline',
        'vasopressin',
        'dopamine',
        'phenylephrine', 'neosynephrine'
    ]
    
    if 'drugname' in infusion.columns:
        # Filter to pressors
        def is_pressor(drug_name):
            if pd.isna(drug_name):
                return False
            drug_lower = str(drug_name).lower()
            return any(vp in drug_lower for vp in vasopressors)
        
        pressor_events = infusion[infusion['drugname'].apply(is_pressor)].copy()
        
        # Rename
        pressor_events = pressor_events.rename(columns={
            'patientunitstayid': 'stay_id',
            'infusionoffset': 'offset_min'
        })
        
        # Take minimum offset (first pressor start)
        pressor_start = pressor_events.groupby('stay_id')['offset_min'].min().reset_index()
        pressor_start = pressor_start.rename(columns={'offset_min': 'pressor_start_offset'})
        
        print(f"  Pressor starts: {len(pressor_start):,} patients")
    else:
        print("  Warning: drugname column not found, skipping pressors")
        pressor_start = pd.DataFrame(columns=['stay_id', 'pressor_start_offset'])
        
except FileNotFoundError:
    print("  infusionDrug.csv not found, skipping pressors")
    pressor_start = pd.DataFrame(columns=['stay_id', 'pressor_start_offset'])

# ============================================================================
# Step 3: Merge with cohort
# ============================================================================
print("\nStep 3: Merge with cohort")

# Start with cohort
events = cohort[['stay_id', 'intime', 'hospitaladmitoffset']].copy()

# Convert intime to datetime if it's not already
events['intime'] = pd.to_datetime(events['intime'])

# Merge vent
events = events.merge(vent_start, on='stay_id', how='left')

# Merge pressor  
events = events.merge(pressor_start, on='stay_id', how='left')

# Convert offsets to timestamps
# offset is in minutes from hospital admit
events['vent_start_time'] = events['intime'] + pd.to_timedelta(events['vent_start_offset'], unit='m')
events['pressor_start_time'] = events['intime'] + pd.to_timedelta(events['pressor_start_offset'], unit='m')

# ============================================================================
# Step 4: Save
# ============================================================================
print("\n" + "=" * 60)
print("Step 4: Save")
print("=" * 60)

output_path = DATA_DIR / 'events_extracted.csv'
events[['stay_id', 'vent_start_offset', 'vent_start_time', 
        'pressor_start_offset', 'pressor_start_time']].to_csv(output_path, index=False)

print(f"\n✓ Events saved: {output_path}")
print(f"  Rows: {len(events):,}")

# Summary
print(f"\n=== Events Summary ===")
vent_count = events['vent_start_time'].notna().sum()
pressor_count = events['pressor_start_time'].notna().sum()
print(f"  Ventilation starts: {vent_count:,} ({vent_count/len(events)*100:.1f}%)")
print(f"  Pressor starts: {pressor_count:,} ({pressor_count/len(events)*100:.1f}%)")

print("\n=== eICU Events Extraction Complete ===")
