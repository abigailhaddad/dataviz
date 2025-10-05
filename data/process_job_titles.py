import pandas as pd
import json

# Read the parquet file
df = pd.read_parquet('processed/usajobs_combined_2024_2025.parquet')

print("Available columns:", df.columns.tolist())
print("Data shape:", df.shape)

# Filter for 2024 data
if 'year' in df.columns:
    df_2024 = df[df['year'] == 2024]
    print(f"Found {len(df_2024)} records for 2024")
else:
    print("No year column found, using all data")
    df_2024 = df

# Check if we have JobCategories column which contains occupational series
if 'JobCategories' in df_2024.columns:
    # Filter for 2210 series
    df_2210 = df_2024[df_2024['JobCategories'].astype(str).str.contains('2210', na=False)]
    print(f"Found {len(df_2210)} records for 2210 series")
    df_2024 = df_2210
else:
    print("No JobCategories column found, checking other columns...")
    # Try other possible column names
    for col in ['occupational_series', 'series', 'job_series', 'occupation']:
        if col in df_2024.columns:
            df_2210 = df_2024[df_2024[col].astype(str).str.contains('2210', na=False)]
            print(f"Found {len(df_2210)} records for 2210 series in column {col}")
            df_2024 = df_2210
            break

# Normalize job titles to be case-insensitive
df_2024['positionTitle_normalized'] = df_2024['positionTitle'].str.upper()

# Group by normalized job title and count announcements
job_title_counts = df_2024.groupby('positionTitle_normalized').size().reset_index(name='announcement_count')

# Get the original title (most common case variation) for each normalized title
job_title_original = df_2024.groupby('positionTitle_normalized')['positionTitle'].agg(lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0]).reset_index()
job_title_original.columns = ['positionTitle_normalized', 'positionTitle']

# Get most common agency and department for each normalized job title
job_title_info = df_2024.groupby('positionTitle_normalized').agg({
    'hiringAgencyName': lambda x: x.mode()[0] if not x.mode().empty else 'Unknown',
    'hiringDepartmentName': lambda x: x.mode()[0] if not x.mode().empty else 'Unknown'
}).reset_index()

# Merge all the data together
result = pd.merge(job_title_counts, job_title_original, on='positionTitle_normalized')
result = pd.merge(result, job_title_info, on='positionTitle_normalized')

# Drop the normalized column as we don't need it in the output
result = result.drop('positionTitle_normalized', axis=1)

# Rename columns
result = result.rename(columns={
    'positionTitle': 'job_title',
    'hiringAgencyName': 'agency',
    'hiringDepartmentName': 'department'
})

# Sort by announcement count descending
result = result.sort_values('announcement_count', ascending=False)

# Convert to dict for JSON export
data = result.to_dict('records')

# Save as JSON
with open('processed/job_titles_2024.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"Processed {len(data)} unique job titles")
print(f"Top 10 job titles by announcement count:")
print(result.head(10)[['job_title', 'announcement_count', 'agency', 'department']])