import pandas as pd

# ===============================
# 1. Load raw district-level data
# ===============================
file_path = "data/time_seperation/demographic/demo_time_padded.csv"
df = pd.read_csv(file_path)

# ==========================================
# 2. Ensure numeric columns are REALLY numeric
# (this fixes wrong summation issues)
# ==========================================
numeric_cols = ["demo_age_5_17", "demo_age_17_"]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# =====================================================
# 3. Aggregate: District → State (Month priority FIRST)
# =====================================================
agg = (
    df.groupby(["month", "state_norm"], as_index=False)[numeric_cols]
      .sum()
)

# ==================================================
# 4. Build complete Month × State grid (36 × months)
# ==================================================
months = df["month"].unique()
states = df["state_norm"].unique()

full_index = pd.MultiIndex.from_product(
    [months, states],
    names=["month", "state_norm"]
)

agg_full = (
    agg.set_index(["month", "state_norm"])
       .reindex(full_index, fill_value=0)
       .reset_index()
)

# ==========================================
# 5. Enforce correct chronological month order
# ==========================================
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

agg_full["month"] = pd.Categorical(
    agg_full["month"],
    categories=month_order,
    ordered=True
)

agg_full = agg_full.sort_values(
    ["month", "state_norm"]
).reset_index(drop=True)

# ===============================
# 6. Final sanity check (IMPORTANT)
# ===============================
raw_total = df[numeric_cols].sum()
final_total = agg_full[numeric_cols].sum()

print("Raw totals:")
print(raw_total)

print("\nAggregated totals:")
print(final_total)

# ===============================
# 7. Save final submission file
# ===============================
output_file = "month_state_final_cleaned.csv"
agg_full.to_csv(output_file, index=False)

print(f"\nFinal file saved as: {output_file}")
