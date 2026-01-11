# ======================================================
# STEP 0: Imports
# ======================================================
import pandas as pd
import re

# ======================================================
# STEP 1: Load the data
# ======================================================
df = pd.read_csv(
    "data/final_cleaned/aadhar_enrollment_fully_resolved.csv"
)

print("Original Dataset Shape:", df.shape)
print("Columns:", df.columns.tolist())
print(df.head())

# ======================================================
# STEP 2: Text normalization function
# ======================================================
def normalize_text(text):
    if pd.isna(text):
        return ""

    text = str(text).lower().strip()

    # remove special characters & numbers
    text = re.sub(r"[^a-z\s]", " ", text)

    # collapse multiple spaces
    text = re.sub(r"\s+", " ", text)

    # common word cleanup
    replacements = {
        " district ": " ",
        " dist ": " ",
        " urban ": " ",
        " rural ": " ",
        " city ": " ",
        " nagar ": " ",
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return text.strip()

# ======================================================
# STEP 3: Normalize state & district
# ======================================================
df["state_norm"] = df["state"].apply(normalize_text)
df["district_norm"] = df["district"].apply(normalize_text)

print("\nAfter normalization:")
print(df[["state", "state_norm", "district", "district_norm"]].head())

# ======================================================
# STEP 4: Remove garbage rows
#   - numeric-only
#   - empty after normalization
# ======================================================
df_cleaned = df[
    (df["state_norm"] != "") &
    (df["district_norm"] != "") &
    (~df["state_norm"].str.isnumeric()) &
    (~df["district_norm"].str.isnumeric())
]

print("\nAfter removing garbage rows:", df_cleaned.shape)

# ======================================================
# STEP 5: Diagnostics BEFORE aggregation
# ======================================================
print("\nUnique states BEFORE :", df["state"].nunique())
print("Unique districts BEFORE :", df["district"].nunique())

print("\nUnique states AFTER normalization :", df_cleaned["state_norm"].nunique())
print("Unique districts AFTER normalization :", df_cleaned["district_norm"].nunique())

# ======================================================
# STEP 6: Aggregate by NORMALIZED keys
# ======================================================
df_aggregated = (
    df_cleaned
    .groupby(["state_norm", "district_norm"], as_index=False)
    .agg({
        "age_0_5": "sum",
        "age_5_17": "sum",
        "age_18_greater": "sum"
    })
)

print("\nAfter aggregation:", df_aggregated.shape)

# ======================================================
# STEP 7: Sort for readability
# ======================================================
df_final_cleaned = (
    df_aggregated
    .sort_values(["state_norm", "district_norm"])
    .reset_index(drop=True)
)

# ======================================================
# STEP 8: Final diagnostics
# ======================================================
print("\nFinal cleaned dataset shape:", df_final_cleaned.shape)
print("\nFinal Dataset Preview:")
print(df_final_cleaned.head(10))

print("\nFinal Dataset Info:")
print(df_final_cleaned.info())

print("\nSummary Statistics:")
print(df_final_cleaned.describe())

# ======================================================
# STEP 10: Load district master (canonical reference)
# ======================================================
from rapidfuzz import process, fuzz

district_master = pd.read_csv("keys/district_master.csv")

print("\nDistrict master preview:")
print(district_master.head())

# ======================================================
# STEP 11: Build state → district lookup
# ======================================================
state_district_lookup = (
    district_master
    .groupby("state_norm")["district_standard"]
    .apply(list)
    .to_dict()
)

print("\nNumber of states in master:", len(state_district_lookup))

# ======================================================
# STEP 12: Fuzzy matching function (STATE-AWARE)
# ======================================================
def resolve_district(row, threshold=85):
    state = row["state_norm"]
    district = row["district_norm"]

    # state not found in master
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

    matched_district, score, _ = match

    if score >= threshold:
        return pd.Series([matched_district, score, "matched"])
    else:
        return pd.Series([matched_district, score, "low_confidence"])

# ======================================================
# STEP 13: Apply fuzzy resolution
# ======================================================
df_final_cleaned[
    ["district_resolved", "match_score", "match_status"]
] = df_final_cleaned.apply(resolve_district, axis=1)

# ======================================================
# STEP 14: Diagnostics after fuzzy matching
# ======================================================
print("\nMatch status distribution:")
print(df_final_cleaned["match_status"].value_counts())

print("\nLow-confidence samples:")
print(
    df_final_cleaned[df_final_cleaned["match_status"] == "low_confidence"]
    [["state_norm", "district_norm", "district_resolved", "match_score"]]
    .head(10)
)

# ======================================================
# STEP 15: Final aggregation using RESOLVED districts
# ======================================================
df_resolved_final = (
    df_final_cleaned[df_final_cleaned["match_status"] == "matched"]
    .groupby(["state_norm", "district_resolved"], as_index=False)
    .agg({
        "age_0_5": "sum",
        "age_5_17": "sum",
        "age_18_greater": "sum"
    })
)

print("\nFinal resolved dataset shape:", df_resolved_final.shape)
print("Unique districts after resolution:",
      df_resolved_final["district_resolved"].nunique())

print("\nFinal resolved preview:")
print(df_resolved_final.head(10))

# ======================================================
# STEP 16: Save FINAL output
# ======================================================
final_output_path = "data/cleaned-dataset/aadhar_enrollment_fully_resolved.csv"
df_resolved_final.to_csv(final_output_path, index=False)

print(f"\nFinal resolved dataset saved to: {final_output_path}")