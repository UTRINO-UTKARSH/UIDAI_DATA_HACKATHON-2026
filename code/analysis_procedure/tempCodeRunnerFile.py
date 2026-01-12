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