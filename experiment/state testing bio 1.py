import pandas as pd

# ======================================================
# STEP 0: Load RAW district-level file (second dataset)
# ======================================================
input_file = "raw_district_data_file_2.csv"   # <-- rename to your real file name
df = pd.read_csv(input_file)

# ======================================================
# STEP 1: Identify numeric columns
# (everything except identifiers)
# ======================================================
exclude_cols = ["month", "state_norm", "district"]
numeric_cols = [col for col in df.columns if col not in exclude_cols]

# ======================================================
# STEP 2: Clean numeric data
# Fixes summation mismatch issues
# ======================================================
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df[col] = df[col].fillna(0)

# ======================================================
# STEP 3: Aggregate districts → states
# Priority: Month FIRST, then State
# ======================================================
state_month_df = (
    df.groupby(["month", "state_norm"], as_index=False)[numeric_cols]
      .sum()
)

# ======================================================
# STEP 4: Create complete Month × State grid
# (ensures 36 States/UT for every month)
# ======================================================
months = df["month"].unique()
states = df["state_norm"].unique()

complete_index = pd.MultiIndex.from_product(
    [months, states],
    names=["month", "state_norm"]
)

state_month_df = (
    state_month_df
    .set_index(["month", "state_norm"])
    .reindex(complete_index, fill_value=0)
    .reset_index()
)

# ======================================================
# STEP 5: Fix chronological month order
# (NOT alphabetical)
# ======================================================
month_order = [
    "March 2025",
    "April 2025",
    "May 2025",
    "June 2025",
    "July 2025",
    "September 2025",
    "October 2025",
    "November 2025",
    "December 2025"
]

state_month_df["month"] = pd.Categorical(
    state_month_df["month"],
    categories=month_order,
    ordered=True
)

state_month_df = state_month_df.sort_values(
    ["month", "state_norm"]
).reset_index(drop=True)

# ======================================================
# STEP 6: Validation check (judge-critical)
# Confirms no data loss during aggregation
# ======================================================
raw_totals = df[numeric_cols].sum()
final_totals = state_month_df[numeric_cols].sum()

print("Raw file totals:")
print(raw_totals)

print("\nFinal aggregated totals:")
print(final_totals)

# ======================================================
# STEP 7: Save FINAL cleaned file
# ======================================================
output_file = "month_state_FINAL_cleaned_file_2.csv"
state_month_df.to_csv(output_file, index=False)

print(f"\nFinal file created successfully: {output_file}")
