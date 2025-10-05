#!/usr/bin/env python3
"""
Quick script to check available columns in the parquet files
"""

import pandas as pd
from pathlib import Path

# Check one of the parquet files to see available columns
data_dir = Path('data/raw')
sample_file = data_dir / 'historical_jobs_2024.parquet'

if sample_file.exists():
    df = pd.read_parquet(sample_file, engine='pyarrow')
    print(f"Total columns: {len(df.columns)}")
    print("\nAll available columns:")
    print("=" * 50)
    for i, col in enumerate(sorted(df.columns), 1):
        print(f"{i:3d}. {col}")
    
    print("\n" + "=" * 50)
    print(f"\nSample data types:")
    print(df.dtypes.head(20))
    
    print("\n" + "=" * 50)
    print(f"\nFirst few rows of key columns:")
    key_cols = ['usajobsControlNumber', 'positionTitle', 'hiringDepartmentName', 
                'hiringAgencyName', 'positionOpenDate', 'positionOpeningStatus']
    # Only show columns that exist
    available_key_cols = [col for col in key_cols if col in df.columns]
    if available_key_cols:
        print(df[available_key_cols].head())
    
    # Show some sample values for important categorical columns
    print("\n" + "=" * 50)
    print("\nSample values for key categorical columns:")
    categorical_cols = ['appointmentType', 'workSchedule', 'payScale', 'whoMayApply', 
                       'teleworkEligible', 'securityClearance', 'positionOpeningStatus']
    for col in categorical_cols:
        if col in df.columns:
            print(f"\n{col}:")
            print(df[col].value_counts().head())
    
    # Check for JSON columns
    print("\n" + "=" * 50)
    print("\nChecking JSON columns:")
    json_cols = ['HiringPaths', 'JobCategories', 'PositionLocations']
    for col in json_cols:
        if col in df.columns:
            sample = df[col].iloc[0] if len(df) > 0 else None
            print(f"\n{col} (first non-null value):")
            for i in range(len(df)):
                if pd.notna(df[col].iloc[i]):
                    print(f"  Type: {type(df[col].iloc[i])}")
                    print(f"  Sample: {str(df[col].iloc[i])[:200]}...")
                    break
else:
    print(f"File not found: {sample_file}")