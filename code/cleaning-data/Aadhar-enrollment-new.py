import pandas as pd
import os

# ======================================================
# 1. LOAD RAW FILES
# ======================================================
file_paths = [
    "data/raw/aadhar-enrollment-complete-dataset/api_data_aadhar_enrolment_0_500000.csv",
    "data/raw/aadhar-enrollment-complete-dataset/api_data_aadhar_enrolment_500000_1000000.csv",
    "data/raw/aadhar-enrollment-complete-dataset/api_data_aadhar_enrolment_1000000_1006029.csv"
]

# Using a list comprehension to load and concat
df = pd.concat([pd.read_csv(fp) for fp in file_paths], ignore_index=True)

# ======================================================
# 2. BASIC CLEANING & STANDARDIZATION
# ======================================================
# Remove rows where state is just a number
df = df[~df['state'].astype(str).str.match(r'^\d+$', na=False)]

# Convert to datetime and numbers
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['pincode'] = pd.to_numeric(df['pincode'], errors='coerce')

for col in ['age_0_5', 'age_5_17', 'age_18_greater']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Strip whitespace and lowercase for matching
df['state'] = df['state'].astype(str).str.strip().str.lower()
df['district'] = df['district'].astype(str).str.strip().str.lower()

# Drop rows that missing critical identifiers
df = df.dropna(subset=['state', 'district'])

# ======================================================
# 3. FIXING CANONICAL NAMES (MAPPING)
# ======================================================
state_map = {
    'andaman & nicobar islands': 'andaman and nicobar islands',
    'dadra & nagar haveli': 'dadra and nagar haveli and daman and diu',
    'dadra and nagar haveli': 'dadra and nagar haveli and daman and diu',
    'daman & diu': 'dadra and nagar haveli and daman and diu',
    'daman and diu': 'dadra and nagar haveli and daman and diu',
    'jammu & kashmir': 'jammu and kashmir'
}

district_map = {
    # Andhra Pradesh
    'ananthapur': 'anantapur',
    'ananthapuramu': 'anantapur',
    'karim nagar': 'karimnagar',
    'k.v. rangareddy': 'k.v.rangareddy',
    'visakhapatanam': 'visakhapatnam',
    
    # West Bengal
    'barddhaman': 'bardhaman',
    'coochbehar': 'cooch behar',
    'maldah': 'malda',
    
    # Others
    'nicobars': 'nicobar',
    'purnea': 'purnia',
    'jhajjar *': 'jhajjar'
}

# Apply mappings BEFORE grouping to ensure duplicates merge
df['state'] = df['state'].replace(state_map)
df['district'] = df['district'].replace(district_map)

# ======================================================
# 4. FINAL AGGREGATION (THE MERGE STEP)
# ======================================================
# We do NOT include 'date' or 'pincode' in the groupby.
# This forces every row with the same (state, district) to become ONE row.
df_district = (
    df.groupby(['state', 'district'], as_index=False)
      .agg({
          'age_0_5': 'sum',
          'age_5_17': 'sum',
          'age_18_greater': 'sum',
          'date': 'max'  # Keeps the most recent update date
      })
)

# ======================================================
# 5. DERIVED METRICS & SORTING
# ======================================================
df_district['total_enrolments'] = (
    df_district['age_0_5'] + 
    df_district['age_5_17'] + 
    df_district['age_18_greater']
)

df_district = df_district.sort_values(by=['state', 'district']).reset_index(drop=True)

# ======================================================
# 6. EXPORT & VERIFICATION
# ======================================================

# df_district.to_csv("data/cleaned-dataset/aadhar_enrolment_district_level_clean.csv", index=False)

# This final check MUST be 0
duplicate_count = df_district.duplicated(subset=['state', 'district']).sum()
print(f"Final shape: {df_district.shape}")
print(f"Duplicate state-district occurrences: {duplicate_count}")

# Check specific fix
print("\nCheck Anantapur consolidation:")
print(df_district[df_district['district'] == 'anantapur'])
print("Final shape:", df_district.shape)
print("\nDistrict count per state (sample):")
print(df_district.groupby('state')['district'].nunique().head())