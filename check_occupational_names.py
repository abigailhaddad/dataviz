#!/usr/bin/env python3
"""
Check if the parquet files already contain occupational series names
"""

import pandas as pd
import json
from pathlib import Path

# Check each parquet file
data_dir = Path('data/raw')
files = ['historical_jobs_2024.parquet', 'current_jobs_2024.parquet', 
         'historical_jobs_2025.parquet', 'current_jobs_2025.parquet']

for filename in files:
    filepath = data_dir / filename
    if filepath.exists():
        print(f"\n{'='*60}")
        print(f"Checking: {filename}")
        print('='*60)
        
        df = pd.read_parquet(filepath)
        
        # Check for any column that might contain occupational series names
        potential_cols = [col for col in df.columns if 'occup' in col.lower() or 'series' in col.lower()]
        print(f"Columns with 'occup' or 'series': {potential_cols}")
        
        # Check JobCategories content
        if 'JobCategories' in df.columns:
            print("\nSample JobCategories values:")
            for i in range(min(5, len(df))):
                if pd.notna(df['JobCategories'].iloc[i]):
                    print(f"\nRow {i}:")
                    print(f"  Raw value: {df['JobCategories'].iloc[i]}")
                    try:
                        # Parse if it's JSON
                        if isinstance(df['JobCategories'].iloc[i], str):
                            parsed = json.loads(df['JobCategories'].iloc[i])
                            print(f"  Parsed: {parsed}")
                            # Check what fields are in the JobCategories
                            if parsed and isinstance(parsed, list) and len(parsed) > 0:
                                print(f"  Fields in first item: {list(parsed[0].keys())}")
                    except:
                        pass
                    break
        
        # Check all columns to see if any contain occupational names
        print("\nChecking all columns for occupational series names...")
        for col in df.columns:
            if df[col].dtype == 'object':  # Only check string columns
                sample_vals = df[col].dropna().head(3).tolist()
                # Look for patterns like "0301 - Administration" or similar
                for val in sample_vals:
                    if isinstance(val, str) and ' - ' in val and any(c.isdigit() for c in val):
                        print(f"  Found potential series with name in '{col}': {val}")
                        break