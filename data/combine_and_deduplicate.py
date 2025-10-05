#!/usr/bin/env python3
"""
Combine and deduplicate USAJobs data from multiple parquet files
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Define paths
DATA_DIR = Path(__file__).parent
RAW_DIR = DATA_DIR / 'raw'
OUTPUT_DIR = DATA_DIR / 'processed'

# Create output directory
OUTPUT_DIR.mkdir(exist_ok=True)

def load_and_combine_data():
    """Load all parquet files and combine them"""
    print("Loading data files...")
    
    all_data = []
    
    # Load each file
    files_to_load = [
        'historical_jobs_2024.parquet',
        'current_jobs_2024.parquet',
        'historical_jobs_2025.parquet',
        'current_jobs_2025.parquet'
    ]
    
    for filename in files_to_load:
        filepath = RAW_DIR / filename
        if filepath.exists():
            print(f"  Loading {filename}...", end='')
            df = pd.read_parquet(filepath)
            print(f" {len(df):,} records")
            all_data.append(df)
        else:
            print(f"  Warning: {filename} not found")
    
    # Combine all dataframes
    print("\nCombining all data...")
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"Total records before deduplication: {len(combined_df):,}")
    
    return combined_df

def deduplicate_data(df):
    """Deduplicate based on usajobsControlNumber, keeping the most recent version"""
    print("\nDeduplicating data...")
    
    # Convert date columns to datetime
    date_columns = ['positionOpenDate', 'positionEndDate', 'lastUpdatedDate']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Sort by lastUpdatedDate (or another relevant date) to keep the most recent
    if 'lastUpdatedDate' in df.columns:
        df_sorted = df.sort_values('lastUpdatedDate', ascending=False)
    else:
        df_sorted = df
    
    # Drop duplicates, keeping the first (most recent) occurrence
    df_deduped = df_sorted.drop_duplicates(subset=['usajobsControlNumber'], keep='first')
    
    print(f"Records after deduplication: {len(df_deduped):,}")
    print(f"Duplicates removed: {len(df) - len(df_deduped):,}")
    
    return df_deduped

def load_occupational_series_mapping():
    """Load the occupational series code to name mapping"""
    series_path = DATA_DIR / 'occupational_series_clean.json'
    with open(series_path, 'r') as f:
        series_data = json.load(f)
    
    # Create a dictionary mapping code to title
    series_map = {item['code']: item['title'] for item in series_data}
    return series_map

def add_derived_columns(df):
    """Add useful derived columns for analysis"""
    print("\nAdding derived columns...")
    
    # Extract year from positionOpenDate
    df['year'] = df['positionOpenDate'].dt.year
    
    # Extract month
    df['month'] = df['positionOpenDate'].dt.month
    
    # Extract week
    df['week'] = df['positionOpenDate'].dt.isocalendar().week
    
    # Create a year-month column for grouping
    df['year_month'] = df['positionOpenDate'].dt.to_period('M').astype(str)
    
    # Create a simplified status column
    df['status_simplified'] = df['positionOpeningStatus'].fillna('Unknown')
    
    # Extract appointment type
    if 'positionSchedule' in df.columns:
        df['appointment_type'] = df['positionSchedule'].fillna('Unknown')
    
    # Load occupational series mapping
    series_map = load_occupational_series_mapping()
    
    # Map occupational series codes to names
    if 'occupationalSeries' in df.columns:
        df['occupationalSeriesName'] = df['occupationalSeries'].map(series_map).fillna('Unknown Series')
        print(f"  Mapped {df['occupationalSeriesName'].notna().sum()} occupational series names")
    else:
        print("  Warning: occupationalSeries column not found")
    
    return df

def save_processed_data(df):
    """Save the processed data in various formats"""
    print("\nSaving processed data...")
    
    # Save as parquet (efficient for large data)
    parquet_path = OUTPUT_DIR / 'usajobs_combined_2024_2025.parquet'
    df.to_parquet(parquet_path, index=False)
    print(f"  Saved to {parquet_path}")
    
    # Create a summary for quick stats
    summary = {
        'total_records': len(df),
        'date_range': {
            'start': df['positionOpenDate'].min().isoformat() if pd.notna(df['positionOpenDate'].min()) else None,
            'end': df['positionOpenDate'].max().isoformat() if pd.notna(df['positionOpenDate'].max()) else None
        },
        'years': sorted(df['year'].unique().tolist()),
        'departments': df['organizationName'].value_counts().to_dict(),
        'status_counts': df['status_simplified'].value_counts().to_dict(),
        'last_updated': datetime.now().isoformat()
    }
    
    summary_path = OUTPUT_DIR / 'data_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"  Saved summary to {summary_path}")
    
    # Create a smaller sample for web development (first 1000 records)
    sample_df = df.head(1000)
    
    # Select only essential columns for the sample
    essential_columns = [
        'usajobsControlNumber', 'positionTitle', 'organizationName', 
        'positionOpenDate', 'positionEndDate', 'positionOpeningStatus',
        'MinimumGradeLevel', 'MaximumGradeLevel', 'year', 'month', 
        'year_month', 'status_simplified', 'occupationalSeries', 'occupationalSeriesName'
    ]
    
    # Keep only columns that exist
    sample_columns = [col for col in essential_columns if col in df.columns]
    sample_df = sample_df[sample_columns]
    
    # Convert to JSON for web use
    sample_path = OUTPUT_DIR / 'sample_data.json'
    sample_df.to_json(sample_path, orient='records', date_format='iso')
    print(f"  Saved sample data to {sample_path}")
    
    return parquet_path, summary_path, sample_path

def main():
    """Main processing function"""
    print("USAJobs Data Processing")
    print("=" * 50)
    
    # Load and combine data
    combined_df = load_and_combine_data()
    
    # Deduplicate
    deduped_df = deduplicate_data(combined_df)
    
    # Add derived columns
    processed_df = add_derived_columns(deduped_df)
    
    # Save processed data
    parquet_path, summary_path, sample_path = save_processed_data(processed_df)
    
    print("\n" + "=" * 50)
    print("Processing complete!")
    print(f"\nKey columns in the dataset:")
    print(f"  {', '.join(processed_df.columns[:10])}...")
    print(f"\nTotal columns: {len(processed_df.columns)}")
    
    # Show some basic stats
    print(f"\nBasic statistics:")
    print(f"  Total unique jobs: {len(processed_df):,}")
    print(f"  Date range: {processed_df['positionOpenDate'].min()} to {processed_df['positionOpenDate'].max()}")
    print(f"  Unique departments: {processed_df['organizationName'].nunique()}")
    print(f"  Unique job titles: {processed_df['positionTitle'].nunique()}")

if __name__ == "__main__":
    main()