import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

# ======================================================
# Plot settings
# ======================================================
mpl.rcParams['figure.dpi'] = 200
mpl.rcParams['savefig.dpi'] = 200
mpl.rcParams['savefig.bbox'] = 'tight'

# ======================================================
# STEP 1: Load resolved data
# ======================================================
df = pd.read_csv(
    "data/cleaned-dataset/aadhar_enrollment_fully_resolved.csv"
)

print("Dataset shape:", df.shape)
print(df.head())

# ======================================================
# STEP 2: INDIA-LEVEL AGGREGATION
# ======================================================
india_totals = df[[
    "age_0_5", "age_5_17", "age_18_greater"
]].sum()

india_total = india_totals.sum()

india_pct = (india_totals / india_total) * 100

# ======================================================
# CHART 1: India-level age distribution (BAR)
# ======================================================
fig, ax = plt.subplots(figsize=(8, 5))

ax.bar(
    india_totals.index,
    india_totals.values
)

ax.set_title("India-wide Aadhaar Enrollments by Age Group")
ax.set_ylabel("Total Enrollments")

for i, v in enumerate(india_totals.values):
    ax.text(i, v, f"{int(v):,}", ha="center", va="bottom")

plt.tight_layout()
plt.savefig("output/01_india_age_distribution.png")
plt.close()

print("✓ Chart 1 saved")

# ======================================================
# STEP 3: STATE-LEVEL AGGREGATION
# ======================================================
state_totals = (
    df.groupby("state_norm")[[
        "age_0_5", "age_5_17", "age_18_greater"
    ]]
    .sum()
    .reset_index()
)

state_totals["total"] = (
    state_totals["age_0_5"] +
    state_totals["age_5_17"] +
    state_totals["age_18_greater"]
)

state_totals = state_totals.sort_values("total", ascending=False)

# ======================================================
# CHART 2: Top 10 states by enrollment
# ======================================================
top_states = state_totals.head(10)

fig, ax = plt.subplots(figsize=(10, 6))

ax.barh(
    top_states["state_norm"],
    top_states["total"]
)

ax.set_title("Top 10 States by Aadhaar Enrollments")
ax.set_xlabel("Total Enrollments")
ax.invert_yaxis()

plt.tight_layout()
plt.savefig("output/02_top_states.png")
plt.close()

print("✓ Chart 2 saved")

# ======================================================
# STEP 4: DISTRICT-LEVEL INSIGHTS
# ======================================================
df["total"] = (
    df["age_0_5"] +
    df["age_5_17"] +
    df["age_18_greater"]
)

top_districts = df.sort_values("total", ascending=False).head(10)
bottom_districts = df.sort_values("total", ascending=True).head(10)

# ======================================================
# CHART 3: Top 10 districts
# ======================================================
fig, ax = plt.subplots(figsize=(10, 6))

ax.barh(
    top_districts["district_resolved"],
    top_districts["total"]
)

ax.set_title("Top 10 Districts by Aadhaar Enrollments")
ax.set_xlabel("Total Enrollments")
ax.invert_yaxis()

plt.tight_layout()
plt.savefig("output/03_top_districts.png")
plt.close()

print("✓ Chart 3 saved")

# ======================================================
# STEP 5: SUMMARY STATISTICS
# ======================================================
print("\n" + "="*70)
print("SUMMARY STATISTICS (NO DATE DIMENSION)")
print("="*70)

print("\nTotal Enrollments (India):")
print(f"  Age 0–5:     {india_totals['age_0_5']:,} ({india_pct['age_0_5']:.1f}%)")
print(f"  Age 5–17:    {india_totals['age_5_17']:,} ({india_pct['age_5_17']:.1f}%)")
print(f"  Age 18+:     {india_totals['age_18_greater']:,} ({india_pct['age_18_greater']:.1f}%)")
print(f"  TOTAL:       {india_total:,}")

print("\nTop 5 Districts:")
print(top_districts[["state_norm", "district_resolved", "total"]])

print("\nBottom 5 Districts:")
print(bottom_districts[["state_norm", "district_resolved", "total"]])

print("\n" + "="*70)