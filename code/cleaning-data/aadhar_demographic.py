# import pandas as pd
# import os

# # ======================================================
# # 1. LOAD RAW FILES
# # ======================================================
# file_paths = [
#     "data/raw/demo_raw/demo_raw_0_500k.csv",
#     "data/raw/demo_raw/demo_raw_500k_1m.csv",
#     "data/raw/demo_raw/demo_raw_1m_1.5m.csv",
#     "data/raw/demo_raw/demo_raw_1.5m_2m.csv",
#     "data/raw/demo_raw/demo_raw_2m_end.csv"
# ]

# # Using a list comprehension to load and concat
# df = pd.concat([pd.read_csv(fp) for fp in file_paths], ignore_index=True)

# # ======================================================
# # 2. BASIC CLEANING & STANDARDIZATION
# # ======================================================
# # Remove rows where state is just a number
# df = df[~df['state'].astype(str).str.match(r'^\d+$', na=False)]

# # Convert to datetime and numbers
# df['date'] = pd.to_datetime(df['date'], errors='coerce')
# df['pincode'] = pd.to_numeric(df['pincode'], errors='coerce')

# for col in ['demo_age_5_17', 'demo_age_17_']:
#     df[col] = pd.to_numeric(df[col], errors='coerce')

# # Strip whitespace and lowercase for matching
# df['state'] = df['state'].astype(str).str.strip().str.lower()
# df['district'] = df['district'].astype(str).str.strip().str.lower()

# # Drop rows that missing critical identifiers
# df = df.dropna(subset=['state', 'district'])

# # ======================================================
# # 3. FIXING CANONICAL NAMES (MAPPING)
# # ======================================================
# state_map = {
#     'andaman & nicobar islands': 'andaman and nicobar islands',
#     'dadra & nagar haveli': 'dadra and nagar haveli and daman and diu',
#     'dadra and nagar haveli': 'dadra and nagar haveli and daman and diu',
#     'daman & diu': 'dadra and nagar haveli and daman and diu',
#     'daman and diu': 'dadra and nagar haveli and daman and diu',
#     'jammu & kashmir': 'jammu and kashmir'
# }

# district_map = {
#     # Andhra Pradesh
#     'ananthapur': 'anantapur',
#     'ananthapuramu': 'anantapur',
#     'karim nagar': 'karimnagar',
#     'k.v. rangareddy': 'k.v.rangareddy',
#     'visakhapatanam': 'visakhapatnam',
    
#     # West Bengal
#     'barddhaman': 'bardhaman',
#     'coochbehar': 'cooch behar',
#     'maldah': 'malda',
    
#     # Others
#     'nicobars': 'nicobar',
#     'purnea': 'purnia',
#     'jhajjar *': 'jhajjar'
# }

# # Apply mappings BEFORE grouping to ensure duplicates merge
# df['state'] = df['state'].replace(state_map)
# df['district'] = df['district'].replace(district_map)

# # ======================================================
# # 4. FINAL AGGREGATION (THE MERGE STEP)
# # ======================================================
# # We do NOT include 'date' or 'pincode' in the groupby.
# # This forces every row with the same (state, district) to become ONE row.
# df_district = (
#     df.groupby(['state', 'district'], as_index=False)
#       .agg({
#           'demo_age_5_17': 'sum',
#           'demo_age_17_': 'sum',
#           'date': 'max'  # Keeps the most recent update date
#       })
# )

# # ======================================================
# # 5. DERIVED METRICS & SORTING
# # ======================================================
# df_district['total_demographic_updates'] = (
#     df_district['demo_age_5_17'] + 
#     df_district['demo_age_17_']  
# )

# df_district = df_district.sort_values(by=['state', 'district']).reset_index(drop=True)

# print(f"Final cleaned dataset has {df_district.shape[0]} rows and {df_district.shape[1]} columns.")
# df_district.to_csv("data/cleaned-dataset/aadhar_demographic_cleaned.csv", index=False)

import pandas as pd
import re
from rapidfuzz import process, fuzz

# ======================================================
# STEP 1: LOAD IMPURE BIOMETRIC DATA
# ======================================================
file_path = "data/cleaned-dataset/demo_clean.csv"
df = pd.read_csv(file_path, low_memory=False)

print("Raw shape:", df.shape)

# ======================================================
# STEP 2: STANDARDIZE COLUMN NAMES
# ======================================================
df.columns = (
    df.columns
      .str.strip()
      .str.lower()
      .str.replace(" ", "_")
)

# ======================================================
# STEP 3: NORMALIZATION FUNCTION (STRICT)
# ======================================================
def normalize_text(x):
    if pd.isna(x):
        return ""
    x = str(x).lower().strip()
    x = re.sub(r"[^a-z\s]", " ", x)
    x = re.sub(r"\s+", " ", x)
    return x.strip()

df["state_norm"] = df["state"].apply(normalize_text)
df["district_norm"] = df["district"].apply(normalize_text)

df = df[
    (df["state_norm"] != "") &
    (df["district_norm"] != "")
]

print("After normalization:", df.shape)

# ======================================================
# STEP 4: DROP PINCODE (DISTRICT-LEVEL DATA)
# ======================================================
if "pincode" in df.columns:
    df = df.drop(columns=["pincode"])

# ======================================================
# STEP 5: IDENTIFY METRIC COLUMNS
# ======================================================
key_cols = ["state_norm", "district_norm"]

metric_cols = [
    c for c in df.columns
    if c not in key_cols
    and pd.api.types.is_numeric_dtype(df[c])
]

print("Metrics used for aggregation:", metric_cols)

# ======================================================
# STEP 6: LOAD LGD DISTRICT MASTER
# ======================================================
lgd = pd.read_csv("keys/district_master.csv")

print("LGD districts:", lgd.shape)

# Build state → district lookup
state_district_lookup = (
    lgd.groupby("state_norm")["district_standard"]
       .apply(list)
       .to_dict()
)

# ======================================================
# STEP 7: STATE-AWARE FUZZY RESOLUTION
# ======================================================
def resolve_district(row, threshold=85):
    state = row["state_norm"]
    district = row["district_norm"]

    if state not in state_district_lookup:
        return pd.Series([None, 0, "state_not_found"])

    choices = state_district_lookup[state]

    match = process.extractOne(
        district,
        choices,
        scorer=fuzz.token_sort_ratio
    )

    if match is None:
        return pd.Series([None, 0, "no_match"])

    resolved, score, _ = match

    if score >= threshold:
        return pd.Series([resolved, score, "matched"])
    else:
        return pd.Series([resolved, score, "low_confidence"])

df[
    ["district_resolved", "match_score", "match_status"]
] = df.apply(resolve_district, axis=1)

print("\nMatch status distribution:")
print(df["match_status"].value_counts())

# ======================================================
# STEP 8: FILTER SAFE MATCHES ONLY
# ======================================================
df_matched = df[df["match_status"] == "matched"]

# ======================================================
# STEP 9: FINAL DISTRICT-LEVEL AGGREGATION
# ======================================================
district_df = (
    df_matched
    .groupby(
        ["state_norm", "district_resolved"],
        as_index=False
    )[metric_cols]
    .sum()
)

print("After LGD-based aggregation:", district_df.shape)

# ======================================================
# STEP 10: DUPLICATE SAFETY CHECK
# ======================================================
dup_count = district_df.duplicated(
    subset=["state_norm", "district_resolved"]
).sum()

print("Duplicate state-district rows:", dup_count)
assert dup_count == 0, "❌ Duplicate districts still exist!"

# ======================================================
# STEP 11: FINAL SANITY CHECK
# ======================================================
print("\nNull values:")
print(district_df.isna().sum())

district_df.info()

# ======================================================
# STEP 12: SAVE FINAL CLEAN FILE
# ======================================================
output_path = "data/final_cleaned/demo_final.csv"
district_df.to_csv(output_path, index=False)

print(f"✅ FINAL LGD-RESOLVED DISTRICT FILE SAVED → {output_path}")