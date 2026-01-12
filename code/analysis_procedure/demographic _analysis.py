# import pandas as pd
# import matplotlib.pyplot as plt
# import matplotlib as mpl

# # ======================================================
# # Plot settings
# # ======================================================
# mpl.rcParams['figure.dpi'] = 200
# mpl.rcParams['savefig.dpi'] = 200
# mpl.rcParams['savefig.bbox'] = 'tight'

# # ======================================================
# # STEP 1: Load resolved data
# # ======================================================
# df = pd.read_csv(
#     "data/time_seperation/demographic/final_time_demo_series_resolved.csv"
# )

# print("Dataset shape:", df.shape)
# print(df.head())

# # ======================================================
# # STEP 2: Define biometric age columns
# # ======================================================
# AGE_COLS = ["demo_age_5_17", "demo_age_17_"]

# # Ensure numeric safety
# df[AGE_COLS] = df[AGE_COLS].apply(pd.to_numeric, errors="coerce").fillna(0)

# # ======================================================
# # STEP 3: INDIA-LEVEL AGGREGATION
# # ======================================================
# india_totals = df[AGE_COLS].sum()
# india_total = india_totals.sum()
# india_pct = (india_totals / india_total) * 100

# # ======================================================
# # CHART 1: India-level age distribution
# # ======================================================
# fig, ax = plt.subplots(figsize=(8, 5))

# bars = ax.bar(
#     ["Age 5–17", "Age 17+"],
#     india_totals.values
# )

# ax.set_title("India-wide Aadhaar demographic updates by Age Group")
# ax.set_ylabel("Total Enrollments")

# for bar, pct in zip(bars, india_pct.values):
#     ax.text(
#         bar.get_x() + bar.get_width() / 2,
#         bar.get_height(),
#         f"{int(bar.get_height()):,}\n({pct:.1f}%)",
#         ha="center",
#         va="bottom",
#         fontsize=10
#     )

# plt.tight_layout()
# plt.savefig("output/demographic/demo_india_age_distribution.png")
# plt.close()

# print("✓ Chart 1 saved")

# # ======================================================
# # STEP 4: STATE-LEVEL AGGREGATION
# # ======================================================
# state_totals = (
#     df.groupby("state_norm")[AGE_COLS]
#     .sum()
#     .reset_index()
# )

# state_totals["total"] = state_totals[AGE_COLS].sum(axis=1)
# state_totals = state_totals.sort_values("total", ascending=False)

# # ======================================================
# # CHART 2: Top 10 states
# # ======================================================
# top_states = state_totals.head(10)

# fig, ax = plt.subplots(figsize=(10, 6))

# ax.barh(
#     top_states["state_norm"],
#     top_states["total"]
# )

# ax.set_title("Top 10 States by Aadhaar demographic updates")
# ax.set_xlabel("Total Enrollments")
# ax.invert_yaxis()

# plt.tight_layout()
# plt.savefig("output/demographic/demo_top_states.png")
# plt.close()

# print("✓ Chart 2 saved")

# # ======================================================
# # STEP 5: DISTRICT-LEVEL INSIGHTS
# # ======================================================
# df["total"] = df[AGE_COLS].sum(axis=1)

# top_districts = df.sort_values("total", ascending=False).head(10)
# bottom_districts = df.sort_values("total", ascending=True).head(10)

# # ======================================================
# # CHART 3: Top 10 districts
# # ======================================================
# fig, ax = plt.subplots(figsize=(10, 6))

# ax.barh(
#     top_districts["district_resolved"],
#     top_districts["total"]
# )

# ax.set_title("Top 10 Districts by Aadhaar demographic Enrollments updates")
# ax.set_xlabel("Total Enrollments")
# ax.invert_yaxis()

# plt.tight_layout()
# plt.savefig("output/demographic/demo_top_districts.png")
# plt.close()

# print("✓ Chart 3 saved")

# # ======================================================
# # STEP 6: SUMMARY STATISTICS
# # ======================================================
# print("\n" + "=" * 70)
# print("SUMMARY STATISTICS — DEMOGRAPHIC ENROLLMENTS")
# print("=" * 70)

# print("\nTotal Enrollments (India):")
# print(f"  Age 5–17: {india_totals['demo_age_5_17']:,} ({india_pct['demo_age_5_17']:.1f}%)")
# print(f"  Age 17+:  {india_totals['demo_age_17_']:,} ({india_pct['demo_age_17_']:.1f}%)")
# print(f"  TOTAL:    {india_total:,}")

# print("\nTop 5 Districts:")
# print(top_districts[["state_norm", "district_resolved", "total"]].head(5))

# print("\nBottom 5 Districts:")
# print(bottom_districts[["state_norm", "district_resolved", "total"]].head(5))

# print("\n" + "=" * 70)

import pandas as pd
import matplotlib.pyplot as plt

# =====================================================
# 1. LOAD DATA
# =====================================================
df = pd.read_csv("data/time_seperation/demographic/final_time_demo_series_resolved.csv")

# =====================================================
# 2. FIX MONTH ORDER (NO JAN/FEB)
# =====================================================
month_order = [
    "March 2025", "April 2025", "May 2025", "June 2025",
    "July 2025", "August 2025", "September 2025",
    "October 2025", "November 2025", "December 2025"
]

df["month"] = pd.Categorical(df["month"], categories=month_order, ordered=True)

# =====================================================
# 3. PAN-INDIA MONTH-WISE AGGREGATION
# =====================================================
india_month = (
    df.groupby("month", as_index=False)
      .agg({
          "demo_age_5_17": "sum",
          "demo_age_17_": "sum"
      })
      .dropna()
)

india_month["total_updates"] = (
    india_month["demo_age_5_17"] + india_month["demo_age_17_"]
)

# =====================================================
# ANALYSIS 1: TOTAL DEMOGRAPHIC UPDATES TREND
# (Overall system pressure)
# =====================================================
plt.figure()
plt.plot(india_month["month"], india_month["total_updates"])
plt.xticks(rotation=45)
plt.xlabel("Month")
plt.ylabel("Total Demographic Updates")
plt.title("Pan-India Aadhaar Demographic Updates Trend (2025)")
plt.tight_layout()
plt.show()

# =====================================================
# ANALYSIS 2: AGE-WISE UPDATE TREND
# (Who is driving updates?)
# =====================================================
plt.figure()
plt.plot(india_month["month"], india_month["demo_age_5_17"], label="Age 5–17")
plt.plot(india_month["month"], india_month["demo_age_17_"], label="Age 17+")
plt.xticks(rotation=45)
plt.xlabel("Month")
plt.ylabel("Demographic Updates")
plt.title("Age-wise Aadhaar Demographic Update Trend")
plt.legend()
plt.tight_layout()
plt.show()

# =====================================================
# ANALYSIS 3: AGE COMPOSITION OVER TIME
# (Demographic structure of updates)
# =====================================================
plt.figure()
plt.stackplot(
    india_month["month"],
    india_month["demo_age_5_17"],
    india_month["demo_age_17_"]
)
plt.xticks(rotation=45)
plt.xlabel("Month")
plt.ylabel("Demographic Updates")
plt.title("Composition of Aadhaar Demographic Updates by Age Group")
plt.tight_layout()
plt.show()

# =====================================================
# ANALYSIS 4: ADULT SHARE (%)
# (Migration intensity proxy)
# =====================================================
india_month["adult_share_pct"] = (
    india_month["demo_age_17_"] / india_month["total_updates"] * 100
)

plt.figure()
plt.plot(india_month["month"], india_month["adult_share_pct"])
plt.xticks(rotation=45)
plt.xlabel("Month")
plt.ylabel("Adult Update Share (%)")
plt.title("Adult Share in Aadhaar Demographic Updates (Migration Signal)")
plt.tight_layout()
plt.show()

# =====================================================
# ANALYSIS 5: MONTH-TO-MONTH UPDATE VOLATILITY
# (Mobility shocks / surges)
# =====================================================
india_month["monthly_change"] = india_month["total_updates"].diff()

plt.figure()
plt.bar(india_month["month"], india_month["monthly_change"])
plt.xticks(rotation=40)
plt.xlabel("Month")
plt.ylabel("Change in Updates")
plt.title("Month-to-Month Change in Demographic Updates")
plt.tight_layout()
plt.show()

# =====================================================
# ANALYSIS 6: PEAK MIGRATION MONTH ANALYSIS
# =====================================================
peak_month = india_month.loc[india_month["demo_age_17_"].idxmax()]

plt.figure()
plt.bar(
    ["Age 5–17", "Age 17+"],
    [peak_month["demo_age_5_17"], peak_month["demo_age_17_"]]
)
plt.xlabel("Age Group")
plt.ylabel("Demographic Updates")
plt.title(f"Age-wise Updates in Peak Migration Month ({peak_month['month']})")
plt.tight_layout()
plt.show()

# =====================================================
# FINAL TABLE (FOR REPORT)
# =====================================================
india_month.to_csv("demographic_update_trends_2025.csv", index=False)