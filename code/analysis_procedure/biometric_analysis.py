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
    "data/final_cleaned/bio_final.csv"
)

print("Dataset shape:", df.shape)
print(df.head())

# ======================================================
# STEP 2: Define biometric age columns
# ======================================================
AGE_COLS = ["bio_age_5_17", "bio_age_17_"]

# Ensure numeric safety
df[AGE_COLS] = df[AGE_COLS].apply(pd.to_numeric, errors="coerce").fillna(0)

# ======================================================
# STEP 3: INDIA-LEVEL AGGREGATION
# ======================================================
india_totals = df[AGE_COLS].sum()
india_total = india_totals.sum()
india_pct = (india_totals / india_total) * 100

# ======================================================
# CHART 1: India-level age distribution
# ======================================================
fig, ax = plt.subplots(figsize=(8, 5))

bars = ax.bar(
    ["Age 5–17", "Age 17+"],
    india_totals.values
)

ax.set_title("India-wide Aadhaar Biometric Enrollments by Age Group")
ax.set_ylabel("Total Enrollments")

for bar, pct in zip(bars, india_pct.values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{int(bar.get_height()):,}\n({pct:.1f}%)",
        ha="center",
        va="bottom",
        fontsize=10
    )

plt.tight_layout()
plt.savefig("output/biometric/bio_india_age_distribution.png")
plt.close()

print("✓ Chart 1 saved")

# ======================================================
# STEP 4: STATE-LEVEL AGGREGATION
# ======================================================
state_totals = (
    df.groupby("state_norm")[AGE_COLS]
    .sum()
    .reset_index()
)

state_totals["total"] = state_totals[AGE_COLS].sum(axis=1)
state_totals = state_totals.sort_values("total", ascending=False)

# ======================================================
# CHART 2: Top 10 states
# ======================================================
top_states = state_totals.head(10)

fig, ax = plt.subplots(figsize=(10, 6))

ax.barh(
    top_states["state_norm"],
    top_states["total"]
)

ax.set_title("Top 10 States by Aadhaar Biometric Enrollments")
ax.set_xlabel("Total Enrollments")
ax.invert_yaxis()

plt.tight_layout()
plt.savefig("output/biometric/bio_top_states.png")
plt.close()

print("✓ Chart 2 saved")

# ======================================================
# STEP 5: DISTRICT-LEVEL INSIGHTS
# ======================================================
df["total"] = df[AGE_COLS].sum(axis=1)

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

ax.set_title("Top 10 Districts by Aadhaar Biometric Enrollments")
ax.set_xlabel("Total Enrollments")
ax.invert_yaxis()

plt.tight_layout()
plt.savefig("output/biometric/bio_top_districts.png")
plt.close()

print("✓ Chart 3 saved")

# ======================================================
# STEP 6: SUMMARY STATISTICS
# ======================================================
print("\n" + "=" * 70)
print("SUMMARY STATISTICS — BIOMETRIC ENROLLMENTS")
print("=" * 70)

print("\nTotal Enrollments (India):")
print(f"  Age 5–17: {india_totals['bio_age_5_17']:,} ({india_pct['bio_age_5_17']:.1f}%)")
print(f"  Age 17+:  {india_totals['bio_age_17_']:,} ({india_pct['bio_age_17_']:.1f}%)")
print(f"  TOTAL:    {india_total:,}")

print("\nTop 5 Districts:")
print(top_districts[["state_norm", "district_resolved", "total"]].head(5))

print("\nBottom 5 Districts:")
print(bottom_districts[["state_norm", "district_resolved", "total"]].head(5))

print("\n" + "=" * 70)