
# Create derived fields and compute core summaries used by multiple charts

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create output directory if it doesn't exist
output_dir = 'output/demographic/district'
os.makedirs(output_dir, exist_ok=True)

# Load demographic data
demo_df = pd.read_csv('data/time_seperation/demographic/demo_time_final.csv', encoding='ascii')
print(demo_df.head(10))

# Parse the data column if needed
import ast
if 'data' in demo_df.columns:
    parsed_rows = demo_df['data'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    demo_df = pd.DataFrame(parsed_rows.tolist(), columns=['month','state_norm','district_resolved','demo_age_5_17','demo_age_17_'])
    # Add numeric columns if they exist
    for col in demo_df.columns:
        if col not in ['month','state_norm','district_resolved']:
            demo_df[col] = pd.to_numeric(demo_df[col], errors='coerce')

# Use the loaded dataframe demo_df
analysis_df = demo_df.copy()

# Ensure numeric
for col_name in ["demo_age_5_17", "demo_age_17_"]:
    analysis_df[col_name] = pd.to_numeric(analysis_df[col_name], errors="coerce")

analysis_df["total"] = analysis_df["demo_age_5_17"].fillna(0) + analysis_df["demo_age_17_"].fillna(0)
analysis_df["share_5_17"] = np.where(analysis_df["total"] > 0, analysis_df["demo_age_5_17"] / analysis_df["total"], np.nan)
analysis_df["share_17_plus"] = np.where(analysis_df["total"] > 0, analysis_df["demo_age_17_"] / analysis_df["total"], np.nan)
analysis_df["ratio_17_to_5_17"] = np.where(analysis_df["demo_age_5_17"] > 0, analysis_df["demo_age_17_"] / analysis_df["demo_age_5_17"], np.nan)

# Aggregations
state_agg_df = (analysis_df
    .groupby(["month", "state_norm"], as_index=False)
    .agg(demo_age_5_17_sum=("demo_age_5_17", "sum"),
         demo_age_17_plus_sum=("demo_age_17_", "sum"),
         total_sum=("total", "sum"),
         districts=("district_resolved", "nunique"))
)
state_agg_df["state_share_5_17"] = np.where(state_agg_df["total_sum"] > 0, state_agg_df["demo_age_5_17_sum"] / state_agg_df["total_sum"], np.nan)
state_agg_df["state_ratio_17_to_5_17"] = np.where(state_agg_df["demo_age_5_17_sum"] > 0, state_agg_df["demo_age_17_plus_sum"] / state_agg_df["demo_age_5_17_sum"], np.nan)

month_agg_df = (analysis_df
    .groupby(["month"], as_index=False)
    .agg(demo_age_5_17_sum=("demo_age_5_17", "sum"),
         demo_age_17_plus_sum=("demo_age_17_", "sum"),
         total_sum=("total", "sum"),
         states=("state_norm", "nunique"),
         districts=("district_resolved", "nunique"))
)
month_agg_df["month_share_5_17"] = np.where(month_agg_df["total_sum"] > 0, month_agg_df["demo_age_5_17_sum"] / month_agg_df["total_sum"], np.nan)

# Basic descriptive stats
print(analysis_df.head())
print(month_agg_df)
print(state_agg_df.head())

# Build the requested charts (bar, pie, hist, scatter, heatmap-style) and compute key ranked tables

sns.set_theme(style="whitegrid")

# Month ordering helper
month_order = [
    "March 2025","April 2025","May 2025","June 2025","July 2025",
    "September 2025","October 2025","November 2025","December 2025"
]
month_agg_plot_df = month_agg_df.copy()
month_agg_plot_df["month"] = pd.Categorical(month_agg_plot_df["month"], categories=month_order, ordered=True)
month_agg_plot_df = month_agg_plot_df.sort_values("month")

# State totals across all months
state_total_df = (analysis_df
    .groupby("state_norm", as_index=False)
    .agg(age_5_17_sum=("demo_age_5_17","sum"),
         age_17_plus_sum=("demo_age_17_","sum"),
         total_sum=("total","sum"),
         districts=("district_resolved","nunique"),
         months=("month","nunique"))
)
state_total_df["share_5_17"] = np.where(state_total_df["total_sum"]>0, state_total_df["age_5_17_sum"]/state_total_df["total_sum"], np.nan)

# District totals across all months
district_total_df = (analysis_df
    .groupby(["state_norm","district_resolved"], as_index=False)
    .agg(age_5_17_sum=("demo_age_5_17","sum"),
         age_17_plus_sum=("demo_age_17_","sum"),
         total_sum=("total","sum"),
         months=("month","nunique"))
)

def topn(df_in, col_name, n=10):
    return df_in.sort_values(col_name, ascending=False).head(n)

# Tables for narrative
month_rank_df = month_agg_df.sort_values("total_sum", ascending=False)
state_top_total_df = topn(state_total_df, "total_sum", 10)
state_top_share_5_17_df = topn(state_total_df[state_total_df["total_sum"]>0], "share_5_17", 10)
state_low_share_5_17_df = state_total_df[state_total_df["total_sum"]>0].sort_values("share_5_17", ascending=True).head(10)

district_top_total_df = topn(district_total_df, "total_sum", 10)

# 1) Monthly totals (stacked bars)
plt.figure(figsize=(10,4))
plt.bar(month_agg_plot_df["month"].astype(str), month_agg_plot_df["demo_age_17_plus_sum"], label="17+", color="#4C78A8")
plt.bar(month_agg_plot_df["month"].astype(str), month_agg_plot_df["demo_age_5_17_sum"], bottom=month_agg_plot_df["demo_age_17_plus_sum"], label="5-17", color="#F58518")
plt.xticks(rotation=35, ha="right")
plt.ylabel("Total count")
plt.title("Monthly totals by age group (stacked)")
plt.legend()
plt.tight_layout()
plt.savefig(f'{output_dir}/01_monthly_totals_stacked.png', dpi=300, bbox_inches='tight')
plt.show()

# 2) Monthly 5-17 share (line)
plt.figure(figsize=(10,3.5))
plt.plot(month_agg_plot_df["month"].astype(str), month_agg_plot_df["month_share_5_17"], marker="o")
plt.xticks(rotation=35, ha="right")
plt.ylabel("Share (5-17)")
plt.title("Monthly share of 5-17")
plt.ylim(0, max(0.15, float(month_agg_plot_df["month_share_5_17"].max())*1.15))
plt.tight_layout()
plt.savefig(f'{output_dir}/02_monthly_share_5_17.png', dpi=300, bbox_inches='tight')
plt.show()

# 3) Pie chart overall composition
overall_5_17 = float(analysis_df["demo_age_5_17"].sum())
overall_17_plus = float(analysis_df["demo_age_17_"].sum())
plt.figure(figsize=(6,6))
plt.pie([overall_5_17, overall_17_plus], labels=["5-17", "17+"], autopct="%.1f%%", startangle=90, colors=["#F58518", "#4C78A8"])
plt.title("Overall composition: 5-17 vs 17+")
plt.tight_layout()
plt.savefig(f'{output_dir}/03_overall_composition.png', dpi=300, bbox_inches='tight')
plt.show()

# 4) Top 15 states by total (bar)
plt.figure(figsize=(10,5))
plot_states_df = state_total_df.sort_values("total_sum", ascending=False).head(15).sort_values("total_sum", ascending=True)
plt.barh(plot_states_df["state_norm"], plot_states_df["total_sum"], color="#4C78A8")
plt.xlabel("Total count")
plt.title("Top 15 states by total")
plt.tight_layout()
plt.savefig(f'{output_dir}/04_top_15_states.png', dpi=300, bbox_inches='tight')
plt.show()

# 5) Pie chart for top 8 states share of total (others as rest)
state_total_sum_all = float(state_total_df["total_sum"].sum())
pie_states_df = state_total_df.sort_values("total_sum", ascending=False).head(8).copy()
pie_states_df["pct"] = pie_states_df["total_sum"] / state_total_sum_all
others_pct = 1 - float(pie_states_df["pct"].sum())
labels_vals = pie_states_df["state_norm"].tolist() + ["Others"]
vals = pie_states_df["pct"].tolist() + [others_pct]
plt.figure(figsize=(7,7))
plt.pie(vals, labels=labels_vals, autopct="%.1f%%", startangle=90)
plt.title("Share of total: top 8 states vs others")
plt.tight_layout()
plt.savefig(f'{output_dir}/05_top_8_states_share.png', dpi=300, bbox_inches='tight')
plt.show()

# 6) Distribution: district totals (hist, log-like via bins)
plt.figure(figsize=(9,4))
valid_totals = district_total_df["total_sum"].replace([np.inf,-np.inf], np.nan).dropna()
plt.hist(valid_totals, bins=50, color="#72B7B2")
plt.xlabel("District total (all months)")
plt.ylabel("Number of districts")
plt.title("Distribution of district totals")
plt.tight_layout()
plt.savefig(f'{output_dir}/06_district_distribution.png', dpi=300, bbox_inches='tight')
plt.show()

# 7) Scatter: district 5-17 vs 17+
plt.figure(figsize=(6,5))
scatter_df = analysis_df[["demo_age_5_17","demo_age_17_","state_norm"]].dropna().copy()
scatter_df = scatter_df[(scatter_df["demo_age_5_17"]>=0) & (scatter_df["demo_age_17_"]>=0)]
# Sample for speed/visibility
if len(scatter_df) > 4000:
    scatter_df = scatter_df.sample(4000, random_state=7)
plt.scatter(scatter_df["demo_age_5_17"], scatter_df["demo_age_17_"], s=10, alpha=0.35)
plt.xlabel("5-17")
plt.ylabel("17+")
plt.title("District-month points: 5-17 vs 17+")
plt.tight_layout()
plt.savefig(f'{output_dir}/07_scatter_5_17_vs_17plus.png', dpi=300, bbox_inches='tight')
plt.show()

# 8) Heatmap-style: month x age-group totals
heat_df = month_agg_plot_df.set_index("month")[["demo_age_5_17_sum","demo_age_17_plus_sum"]]
plt.figure(figsize=(6,4))
sns.heatmap(heat_df, annot=True, fmt=".0f", cmap="YlGnBu")
plt.title("Month x age-group totals")
plt.tight_layout()
plt.savefig(f'{output_dir}/08_month_agegroup_heatmap.png', dpi=300, bbox_inches='tight')
plt.show()

# Print key ranked tables (head only as requested)
print(month_rank_df[["month","total_sum","month_share_5_17","states","districts"]].head(9))
print(state_top_total_df[["state_norm","total_sum","share_5_17","districts","months"]].head(10))
print(state_top_share_5_17_df[["state_norm","total_sum","share_5_17","districts","months"]].head(10))
print(state_low_share_5_17_df[["state_norm","total_sum","share_5_17","districts","months"]].head(10))
print(district_top_total_df.head(10))
