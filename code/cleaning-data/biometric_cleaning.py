import pandas as pd
import re
from rapidfuzz import process, fuzz

# ======================================================
# STEP 1: LOAD IMPURE BIOMETRIC DATA
# ======================================================
file_path = "data/final_cleaned/aadhar_biometric_district_level_clean.csv"
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
output_path = "aadhar_biometric_district_level_FINAL_LGD_RESOLVED.csv"
district_df.to_csv(output_path, index=False)

print(f"✅ FINAL LGD-RESOLVED DISTRICT FILE SAVED → {output_path}")
