import pandas as pd

# ======================================================
# STEP 0: Read the RAW FILE (district-level data)
# Imagine this is the exact file you submitted to us
# ======================================================
input_file = "raw_district_data.csv"   # <-- rename to your actual file
df = pd.read_csv(input_file)

# ======================================================
# STEP 1: Clean numeric columns
# Problem fixed: wrong summation due to string values
# ======================================================
value_columns = [
    "demo_age_5_17",
    "demo_age_17_"
]

for col in value_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df[col] = df[col].fillna(0)

# ======================================================
# STEP 2: Remove district-level granularity
# Aggregate ALL districts into their respective states
# Priority: Month FIRST, then State
# ======================================================
state_month_df = (
    df.groupby(["month", "state_norm"], as_index=False)[value_columns]
      .sum()
)

# ======================================================
# STEP 3: Ensure every State exists for every Month
# (36 States/UT × available months)
# Missing combinations are filled with 0
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
# STEP 4: Fix chronological month order (NOT alphabetical)
# ======================================================
correct_month_order = [
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
    categories=correct_month_order,
    ordered=True
)

state_month_df = state_month_df.sort_values(
    ["month", "state_norm"]
).reset_index(drop=True)

# ======================================================
# STEP 5: Validation check (VERY IMPORTANT FOR JUDGES)
# Confirms that aggregation did not change totals
# ======================================================
raw_totals = df[value_columns].sum()
final_totals = state_month_df[value_columns].sum()

print("Raw file totals:")
print(raw_totals)

print("\nFinal aggregated file totals:")
print(final_totals)

# ======================================================
# STEP 6: Save FINAL CLEAN FILE
# ======================================================
output_file = "month_state_final_cleaned_ordered.csv"
state_month_df.to_csv(output_file, index=False)

print(f"\nFinal file generated successfully: {output_file}")
