#!/usr/bin/env python3
"""
eICU Full Pipeline Runner
==========================

전체 전처리 파이프라인을 순서대로 실행

단계:
1. Cohort generation
2. Vitals extraction
3. Labs extraction
4. Events extraction
5. Sliding windows
6. Feature engineering
7. Schema alignment
"""

import subprocess
import sys
from pathlib import Path
import time

# Script directory
SCRIPT_DIR = Path(__file__).parent

scripts = [
    ("01. Cohort Generation", "01_cohort.py"),
    ("02. Vitals Extraction", "02_vitals.py"),
    ("03. Labs Extraction", "03_labs.py"),
    ("04. Events Extraction", "04_events.py"),
    ("05. Sliding Windows", "05_sliding_windows.py"),
    ("06. Feature Engineering", "06_feature_engineering.py"),
    ("07. Schema Alignment", "07_schema_alignment.py")
]

print("=" * 70)
print("eICU PREPROCESSING PIPELINE - FULL RUN")
print("=" * 70)
print(f"\nTotal steps: {len(scripts)}")
print()

start_time = time.time()
failed_scripts = []

for i, (name, script) in enumerate(scripts, 1):
    print(f"\n{'='*70}")
    print(f"STEP {i}/{len(scripts)}: {name}")
    print(f"{'='*70}\n")
    
    script_path = SCRIPT_DIR / script
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            capture_output=False
        )
        
        print(f"\n✓ Step {i} completed successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Step {i} failed with error code {e.returncode}")
        failed_scripts.append((i, name, script))
        
        user_input = input("\nContinue to next step? (y/n): ")
        if user_input.lower() != 'y':
            print("\nPipeline aborted by user")
            break
    
    except Exception as e:
        print(f"\n✗ Step {i} failed with error: {e}")
        failed_scripts.append((i, name, script))
        break

# Final summary
elapsed = time.time() - start_time

print("\n" + "=" * 70)
print("PIPELINE SUMMARY")
print("=" * 70)

if not failed_scripts:
    print(f"\n✓ All {len(scripts)} steps completed successfully")
else:
    print(f"\n✗ {len(failed_scripts)} step(s) failed:")
    for step_num, step_name, step_script in failed_scripts:
        print(f"    Step {step_num}: {step_name} ({step_script})")

print(f"\nTotal time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")

# Next steps
if not failed_scripts:
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("\n1. Check output: ../data/processed/eicu_final_aligned.csv")
    print("2. Load MIMIC trained model")
    print("3. Run inference on eICU data")
    print("4. Evaluate external validation performance")
    print("\nSee implementation_plan.md for details.")
else:
    print("\nPlease fix errors and re-run the pipeline")

print("\n" + "=" * 70)
