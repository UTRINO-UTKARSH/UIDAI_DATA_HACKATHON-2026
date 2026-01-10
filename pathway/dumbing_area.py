import pandas as pd
import re

# ---------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------
file_paths = [
    'data/raw/aadhar-enrollment-complete-dataset/api_data_aadhar_enrolment_0_500000.csv',
    'data/raw/aadhar-enrollment-complete-dataset/api_data_aadhar_enrolment_500000_1000000.csv',
    'data/raw/aadhar-enrollment-complete-dataset/api_data_aadhar_enrolment_1000000_1006029.csv'
]

dfs = []

for file in file_paths:
    try:
        # FIX 1: Use regex separator r'\s*\|\s*' to handle spaces around the pipe '|'
        # FIX 2: Use on_bad_lines='skip' to avoid crashing on malformed rows
        df = pd.read_csv(file, sep=r'\s*\|\s*', engine='python', on_bad_lines='skip')
        
        # FIX 3: Strip whitespace from column names immediately
        # This turns ' state ' into 'state'
        df.columns = df.columns.str.strip()
        
        # Drop the index column if it exists (it will now be named 'Unnamed: 0' without spaces)
        if 'Unnamed: 0' in df.columns:
            df.drop('Unnamed: 0', axis=1, inplace=True)
        elif df.columns[0] == '0':
             # Handle the specific case where the first column is literally named '0'
             df.drop(df.columns[0], axis=1, inplace=True)
            
        dfs.append(df)
        print(f"Loaded {file}: {df.shape[0]} rows")
        
    except Exception as e:
        print(f"Error loading {file}: {e}")

# ---------------------------------------------------------
# 2. COMBINE
# ---------------------------------------------------------
if dfs:
    combined_df = pd.concat(dfs, ignore_index=True)
    print(f"\nCombined Total Rows: {combined_df.shape[0]}")
    
    # Check columns to verify they are correct (Debug print)
    print("Current Columns:", combined_df.columns.tolist())
    
    # Strip whitespace from values (This will now work because 'state' exists)
    combined_df['state'] = combined_df['state'].str.strip()
    combined_df['district'] = combined_df['district'].str.strip()
    
    # ---------------------------------------------------------
    # 3. CLEANING & STANDARDIZATION
    # ---------------------------------------------------------
    # Example: Standardizing Bangalore to Bengaluru
    # Using .str.contains() is safer to catch variations
    combined_df.loc[combined_df['district'].str.contains('Bangalore', case=False, na=False), 'district'] = 'Bengaluru'
    
    # Ensure numeric columns are actually numeric
    numeric_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
    # Check if numeric columns exist before converting
    for col in numeric_cols:
        if col in combined_df.columns:
            combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce').fillna(0).astype(int)
        else:
            print(f"Warning: Column {col} not found in data.")

    # ---------------------------------------------------------
    # 4. AGGREGATION (District Level)
    # ---------------------------------------------------------
    # Only group if columns exist
    if 'state' in combined_df.columns and 'district' in combined_df.columns:
        district_analysis = combined_df.groupby(['state', 'district'])[numeric_cols].sum().reset_index()
        
        # Add a total column
        district_analysis['total_enrollments'] = district_analysis['age_0_5'] + district_analysis['age_5_17'] + district_analysis['age_18_greater']

        # Sort
        district_analysis = district_analysis.sort_values(by=['state', 'total_enrollments'], ascending=[True, False])

        # ---------------------------------------------------------
        # 5. OUTPUT
        # ---------------------------------------------------------
        output_filename = 'district_level_aggregated.csv'
        district_analysis.to_csv(output_filename, index=False)
        
        print(f"Aggregation complete. Saved to '{output_filename}'.")
        print("\nPreview of Aggregated Data:")
        print(district_analysis.head(10))
    else:
        print("Required columns for grouping are missing.")
else:
    print("No dataframes loaded.")