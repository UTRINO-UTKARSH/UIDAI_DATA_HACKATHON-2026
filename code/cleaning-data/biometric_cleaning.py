import pandas as pd
import re

# -------------------------------
# STEP 1: LOAD FILE
# -------------------------------
file_path = "data/final_cleaned/aadhar_biometric_district_level_clean.csv"
df = pd.read_csv(file_path, low_memory=False)

print("Raw shape:", df.shape)

# -------------------------------
# STEP 2: STANDARDIZE COLUMNS
# -------------------------------
df.columns = (
    df.columns
      .str.strip()
      .str.lower()
      .str.replace(" ", "_")
)

# -------------------------------
# STEP 3: CLEAN STATE / DISTRICT TEXT
# -------------------------------
def clean_text(x):
    if pd.isna(x):
        return None
    x = str(x).strip().title()
    return x if re.search(r"[A-Za-z]", x) else None

df["state"] = df["state"].apply(clean_text)
df["district"] = df["district"].apply(clean_text)

df = df.dropna(subset=["state", "district"])

print("After text cleaning:", df.shape)

# -------------------------------
# STEP 4: DROP PINCODE (DISTRICT LEVEL DATA)
# -------------------------------
if "pincode" in df.columns:
    df = df.drop(columns=["pincode"])

# -------------------------------
# STEP 5: EXPLICIT METRIC COLUMNS
# -------------------------------
key_cols = ["state", "district"]

metric_cols = [
    c for c in df.columns
    if c not in key_cols
    and pd.api.types.is_numeric_dtype(df[c])
]

print("Metrics used for aggregation:", metric_cols)

# -------------------------------
# STEP 6: CORRECT DISTRICT AGGREGATION
# -------------------------------
district_df = (
    df
    .groupby(key_cols, as_index=False)[metric_cols]
    .sum()
)

print("After aggregation:", district_df.shape)

# -------------------------------
# STEP 7: HARD DUPLICATE CHECK
# -------------------------------
dup_count = district_df.duplicated(subset=key_cols).sum()
print("Duplicate state-district rows:", dup_count)

assert dup_count == 0, "❌ Duplicate districts still exist!"

# -------------------------------
# STEP 8: FINAL SANITY CHECK
# -------------------------------
print("\nNull values:")
print(district_df.isna().sum())

district_df.info()

# -------------------------------
# STEP 9: SAVE CLEAN FILE
# -------------------------------
district_df.to_csv(
    "aadhar_biometric_district_level_FINAL_CLEAN.csv",
    index=False
)

print("✅ FINAL CLEAN DISTRICT FILE SAVED")
