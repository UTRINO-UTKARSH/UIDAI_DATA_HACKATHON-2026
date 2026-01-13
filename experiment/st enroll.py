import pandas as pd

# ======================================================
# STEP 0: Load RAW district-level file (third dataset)
# ======================================================
input_file = "data/time_seperation/enroll/enroll_time_padded.csv"   # <-- rename to your real file name
df = pd.read_csv(input_file)

# ======================================================
# STEP 1: Identify numeric columns
# ======================================================
exclude_cols = ["month", "state_norm", "district"]
numeric_cols = [col for col in df.columns if col not in exclude_cols]

# ======================================================
# STEP 2: Clean numeric data
# ======================================================
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df[col] = df[col].fillna(0)

# ======================================================
# STEP 3: Aggregate districts → states (month priority)
# ======================================================
state_month_df = (
    df.groupby(["month", "state_norm"], as_index=False)[numeric_cols]
      .sum()
)

# ======================================================
# STEP 4: Create complete Month × State grid
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
# STEP 6: Validation (judge-critical)
# ======================================================
print("Raw totals:")
print(df[numeric_cols].sum())

print("\nFinal totals:")
print(state_month_df[numeric_cols].sum())

# ======================================================
# STEP 7: Save FINAL cleaned file
# ======================================================
output_file = "enroll_ms.csv"
state_month_df.to_csv(output_file, index=False)

print(f"\nFinal file created: {output_file}")
