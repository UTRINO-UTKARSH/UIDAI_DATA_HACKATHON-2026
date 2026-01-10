# Step 1: Load the data
import pandas as pd
df = pd.read_csv('data/cleaned-dataset/aadhar_enrollment_final_aggregated.csv')

print("Original Dataset Shape:", df.shape)
print("Columns:", df.columns.tolist())
print(df.head())

# Step 2: Remove rows where both state AND district are numeric only
# Check for rows with numeric-only state and district
df_cleaned = df[~((df['state'].str.isnumeric()) & (df['district'].str.isnumeric()))]

print("\nAfter removing numeric state/district rows:", df_cleaned.shape)

# Step 3: Aggregate by state and district (sum all age groups)
# Group by state and district, and sum the enrollment numbers
df_aggregated = df_cleaned.groupby(['state', 'district'], as_index=False).agg({
    'age_0_5': 'sum',
    'age_5_17': 'sum',
    'age_18_greater': 'sum'
})

print("After aggregation (removing duplicates):", df_aggregated.shape)

# Step 4: Sort alphabetically by state, then by district
df_final_cleaned = df_aggregated.sort_values(['state', 'district']).reset_index(drop=True)

print("\nFinal cleaned dataset shape:", df_final_cleaned.shape)
print("\nFinal Dataset Preview:")
print(df_final_cleaned.head(10))

print("\nFinal Dataset Info:")
print(df_final_cleaned.info())

print("\nSummary Statistics:")
print(df_final_cleaned.describe())

# Save the cleaned dataset
# output_path = '/home/user/workspace/outputs/cleaned_aadhar_data.csv'
# df_final_cleaned.to_csv(output_path, index=False)
print(f"\nCleaned dataset saved to: cleaned_aadhar_data.csv")
