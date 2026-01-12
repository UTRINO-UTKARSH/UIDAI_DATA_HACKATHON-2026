import pandas as pd
import re
from rapidfuzz import process, fuzz

# ======================================================
# STEP 1: Load Raw Enrollment Data & District Master
# ======================================================
#change file paths as needed

raw_files = [
    'data/raw/Aadhaar Biometric Update dataset/api_data_aadhar_biometric_0_500000.csv',
    'data/raw/Aadhaar Biometric Update dataset/api_data_aadhar_biometric_500000_1000000.csv',
    'data/raw/Aadhaar Biometric Update dataset/api_data_aadhar_biometric_1000000_1500000.csv',
    'data/raw/Aadhaar Biometric Update dataset/api_data_aadhar_biometric_1500000_1861108.csv'
]

df_raw = pd.concat([pd.read_csv(f) for f in raw_files], ignore_index=True)

# Load your canonical list (the 729 districts)
district_master = pd.read_csv("keys/district_master.csv") 

# ======================================================
# STEP 2: Text Normalization Function
# ======================================================
def normalize_text(text):
    if pd.isna(text): return ""
    text = str(text).lower().strip()
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    replacements = {
        " district ": " ", " dist ": " ", " urban ": " ",
        " rural ": " ", " city ": " ", " nagar ": " ",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.strip()

# Prepare raw data for matching
df_raw["state_norm"] = df_raw["state"].apply(normalize_text)
df_raw["district_norm"] = df_raw["district"].apply(normalize_text)
df_raw['date'] = pd.to_datetime(df_raw['date'], dayfirst=True)
df_raw['month'] = df_raw['date'].dt.strftime('%B %Y')

# ======================================================
# STEP 3: State-Aware Fuzzy Resolution
# ======================================================
state_district_lookup = district_master.groupby("state_norm")["district_standard"].apply(list).to_dict()

def resolve_district(row, threshold=85):
    state, district = row["state_norm"], row["district_norm"]
    if state not in state_district_lookup: return None
    choices = state_district_lookup[state]
    match = process.extractOne(district, choices, scorer=fuzz.token_sort_ratio)
    return match[0] if match and match[1] >= threshold else None

# Map raw records to standard district names
unique_raw_pairs = df_raw[['state_norm', 'district_norm']].drop_duplicates()
unique_raw_pairs['district_resolved'] = unique_raw_pairs.apply(resolve_district, axis=1)
df_mapped = pd.merge(df_raw, unique_raw_pairs, on=['state_norm', 'district_norm'], how='left')

# Aggregate the "active" raw data
df_active_agg = df_mapped.groupby(['month', 'state_norm', 'district_resolved']).agg({
    'bio_age_5_17': 'sum', 'bio_age_17_': 'sum'
}).reset_index()

# ======================================================
# STEP 4: Create the "Padded" Grid (The Cross Join)
# ======================================================
# Get unique months and unique canonical districts
all_months = df_active_agg['month'].unique()
all_districts = district_master[['state_norm', 'district_standard']].drop_duplicates()

# Create the full template: every district x every month
months_df = pd.DataFrame({'month': all_months})
all_districts['key'], months_df['key'] = 1, 1
df_template = pd.merge(all_districts, months_df, on='key').drop('key', axis=1)

# ======================================================
# STEP 5: Final Merge & Fill Zeros
# ======================================================
# Merge our "active" data into the full template
df_final = pd.merge(
    df_template, 
    df_active_agg, 
    left_on=['month', 'state_norm', 'district_standard'],
    right_on=['month', 'state_norm', 'district_resolved'],
    how='left'
)

# Fill gaps with 0 and clean up columns
cols_to_fix = ['bio_age_5_17', 'bio_age_17_']
df_final[cols_to_fix] = df_final[cols_to_fix].fillna(0).astype(int)
df_final = df_final.drop(columns=['district_resolved']).rename(columns={'district_standard': 'district'})

# Sort chronologically and save
df_final['month_dt'] = pd.to_datetime(df_final['month'], format='%B %Y')
df_final = df_final.sort_values(['month_dt', 'state_norm', 'district'])
df_final.drop(columns=['month_dt']).to_csv("final_padded_bio_time_series.csv", index=False)

# without changes the previous version where the inactivity is not shown of this file was as below:


# import pandas as pd
# import re
# from rapidfuzz import process, fuzz

# # ======================================================
# # STEP 1: Load Raw Enrollment Data & District Master
# # ======================================================
# raw_files = [
#     'data/raw/Aadhaar Biometric Update dataset/api_data_aadhar_biometric_0_500000.csv',
#     'data/raw/Aadhaar Biometric Update dataset/api_data_aadhar_biometric_500000_1000000.csv',
#     'data/raw/Aadhaar Biometric Update dataset/api_data_aadhar_biometric_1000000_1500000.csv',
#     'data/raw/Aadhaar Biometric Update dataset/api_data_aadhar_biometric_1500000_1861108.csv'
# ]
# df_raw = pd.concat([pd.read_csv(f) for f in raw_files], ignore_index=True)
# district_master = pd.read_csv("keys/district_master.csv") # Your canonical reference

# # ======================================================
# # STEP 2: Text Normalization (Using your exact logic)
# # ======================================================
# def normalize_text(text):
#     if pd.isna(text): return ""
#     text = str(text).lower().strip()
#     text = re.sub(r"[^a-z\s]", " ", text)
#     text = re.sub(r"\s+", " ", text)
#     replacements = {
#         " district ": " ", " dist ": " ", " urban ": " ",
#         " rural ": " ", " city ": " ", " nagar ": " ",
#     }
#     for k, v in replacements.items():
#         text = text.replace(k, v)
#     return text.strip()

# # Apply normalization and handle Date/Month
# df_raw["state_norm"] = df_raw["state"].apply(normalize_text)
# df_raw["district_norm"] = df_raw["district"].apply(normalize_text)
# df_raw['date'] = pd.to_datetime(df_raw['date'], dayfirst=True)
# df_raw['month'] = df_raw['date'].dt.strftime('%B %Y')

# # ======================================================
# # STEP 3: State-Aware Fuzzy Resolution Logic
# # ======================================================
# state_district_lookup = district_master.groupby("state_norm")["district_standard"].apply(list).to_dict()

# def resolve_district(row, threshold=85):
#     state, district = row["state_norm"], row["district_norm"]
#     if state not in state_district_lookup:
#         return pd.Series([None, "state_not_found"])
    
#     choices = state_district_lookup[state]
#     match = process.extractOne(district, choices, scorer=fuzz.token_sort_ratio)
    
#     if match and match[1] >= threshold:
#         return pd.Series([match[0], "matched"])
#     return pd.Series([None, "low_confidence_or_no_match"])

# # ======================================================
# # STEP 4: Mapping Raw Data to Resolved Districts
# # ======================================================
# # Create a unique map of raw district-state pairs to speed up processing
# unique_pairs = df_raw[['state_norm', 'district_norm']].drop_duplicates()
# unique_pairs[["district_resolved", "match_status"]] = unique_pairs.apply(resolve_district, axis=1)

# # Merge resolutions back to the main raw dataframe
# df_mapped = pd.merge(df_raw, unique_pairs, on=['state_norm', 'district_norm'], how='left')

# # ======================================================
# # STEP 5: Final Month-wise Aggregation
# # ======================================================
# # Filter for successfully matched districts only
# df_final_time_series = (
#     df_mapped[df_mapped["match_status"] == "matched"]
#     .groupby(["month", "state_norm", "district_resolved"], as_index=False)
#     .agg({
#         "bio_age_5_17": "sum",
#         "bio_age_17_": "sum",
#     })
# )

# # Chronological sorting
# df_final_time_series['month_dt'] = pd.to_datetime(df_final_time_series['month'], format='%B %Y')
# df_final_time_series = df_final_time_series.sort_values(['month_dt', 'state_norm', 'district_resolved'])

# # Save result
# df_final_time_series.drop(columns=['month_dt']).to_csv("final_time_bio_series_resolved.csv", index=False)