import pandas as pd
import re

# -------------------------------
# STEP 1: LOAD FILE
# -------------------------------
file_path = "data/cleaned-dataset/aadhar_biometric_district_level_clean.csv"

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
# STEP 3: REMOVE JUNK STATE/DISTRICT NAMES
# -------------------------------
def is_valid_name(x):
    if pd.isna(x):
        return False
    return bool(re.search(r"[a-zA-Z]", str(x)))

df = df[
    df["state"].apply(is_valid_name) &
    df["district"].apply(is_valid_name)
]

print("After removing junk names:", df.shape)

# -------------------------------
# STEP 4: DROP NULL KEYS
# -------------------------------
df = df.dropna(subset=["state", "district", "pincode"])

# -------------------------------
# STEP 5: SAFE DEDUPLICATION (ADD COUNTS)
# -------------------------------
numeric_cols = df.select_dtypes(include="number").columns

df_clean = (
    df.groupby(
        ["state", "district", "pincode"],
        as_index=False
    )[numeric_cols]
    .sum()
)

print("After logical deduplication:", df_clean.shape)

# -------------------------------
# STEP 6: PINCODE → DISTRICT AGGREGATION
# -------------------------------
district_df = (
    df_clean
    .groupby(["state", "district"], as_index=False)
    .sum(numeric_only=True)
)

print("District-level shape:", district_df.shape)

# -------------------------------
# STEP 7: FINAL VALIDATION
# -------------------------------
print("Nulls:\n", district_df.isna().sum())
print("Duplicates:", district_df.duplicated().sum())
district_df.info()

# -------------------------------
# STEP 8: SAVE FINAL CLEAN FILE
# -------------------------------
district_df.to_csv(
    "data/cleaned-dataset/BIOMETRIC_CLEAN/aadhar_biometric_district_level_clean.csv",
    index=False
)
