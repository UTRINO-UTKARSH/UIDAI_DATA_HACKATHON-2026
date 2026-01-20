# Load the uploaded CSV into a dataframe
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create output directory if it doesn't exist
output_dir = 'output/enroll/18+'
os.makedirs(output_dir, exist_ok=True)

csv_path = 'data/time_seperation/enroll/enroll_time_padded.csv'
df_enroll = pd.read_csv(csv_path, encoding='ascii')

# Basic cleanup
for col in ['state_norm', 'district', 'month']:
    df_enroll[col] = df_enroll[col].astype(str).str.strip().str.lower()

# Parse month strings like 'March 2025' to datetime month start
month_dt_vals = pd.to_datetime(df_enroll['month'].str.title(), format='%B %Y', errors='coerce')
df_enroll['month_dt'] = month_dt_vals

# Ensure numeric columns are numeric
for col in ['age_0_5', 'age_5_17', 'age_18_greater']:
    df_enroll[col] = pd.to_numeric(df_enroll[col], errors='coerce').fillna(0)

# Show head
print(df_enroll.head())

# Create 7 visual analyses focused on age_18_greater (18+) using seaborn/matplotlib
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='whitegrid')

# Aggregate helpers
month_agg = df_enroll.groupby('month_dt', as_index=False)['age_18_greater'].sum().sort_values('month_dt')
state_agg = df_enroll.groupby('state_norm', as_index=False)['age_18_greater'].sum().sort_values('age_18_greater', ascending=False)
district_agg = df_enroll.groupby(['state_norm','district'], as_index=False)['age_18_greater'].sum().sort_values('age_18_greater', ascending=False)

# For month x state heatmap use top 12 states by total 18+
top_states = state_agg.head(12)['state_norm'].tolist()
state_month = df_enroll[df_enroll['state_norm'].isin(top_states)].groupby(['state_norm','month_dt'], as_index=False)['age_18_greater'].sum()
heat_pivot = state_month.pivot(index='state_norm', columns='month_dt', values='age_18_greater').fillna(0)

# For age distribution comparison (18+ vs others) by month
month_all_ages = df_enroll.groupby('month_dt', as_index=False)[['age_0_5','age_5_17','age_18_greater']].sum().sort_values('month_dt')
month_all_ages_long = month_all_ages.melt(id_vars='month_dt', var_name='age_group', value_name='count')

# 1) Monthly trend line for 18+
plt.figure(figsize=(10,4))
sns.lineplot(data=month_agg, x='month_dt', y='age_18_greater', marker='o')
plt.title('18+ enrollments over time (monthly total)')
plt.xlabel('Month')
plt.ylabel('18+ enrollments')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(f'{output_dir}/01_monthly_trend_18plus.png', dpi=300, bbox_inches='tight')
plt.show()

# 2) Bar chart - total 18+ by month
plt.figure(figsize=(10,4))
sns.barplot(data=month_agg, x='month_dt', y='age_18_greater', color='#4C72B0')
plt.title('18+ enrollments by month (bar)')
plt.xlabel('Month')
plt.ylabel('18+ enrollments')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(f'{output_dir}/02_monthly_bar_18plus.png', dpi=300, bbox_inches='tight')
plt.show()

# 3) Top 15 states by total 18+ (bar)
plt.figure(figsize=(10,5))
state_top15 = state_agg.head(15).copy()
sns.barplot(data=state_top15, y='state_norm', x='age_18_greater', hue='state_norm', palette='viridis', legend=False)
plt.title('Top 15 states by total 18+ enrollments')
plt.xlabel('18+ enrollments')
plt.ylabel('State')
plt.tight_layout()
plt.savefig(f'{output_dir}/03_top15_states_18plus.png', dpi=300, bbox_inches='tight')
plt.show()

# 4) Top 20 districts by total 18+ (bar with state colors)
plt.figure(figsize=(12,7))
district_top20 = district_agg.head(20).copy()
district_top20 = district_top20.sort_values('age_18_greater', ascending=True)

# Create a color map for states
unique_states = district_top20['state_norm'].unique()
state_colors = {state: plt.cm.tab20(i % 20) for i, state in enumerate(unique_states)}
bar_colors = [state_colors[state] for state in district_top20['state_norm']]

# Create horizontal bar chart
ax = plt.barh(district_top20['district'], district_top20['age_18_greater'], color=bar_colors)

# Add state labels on the bars
for i, (idx, row) in enumerate(district_top20.iterrows()):
    ax[i].set_label(row['state_norm'])
    plt.text(row['age_18_greater']/2, i, row['state_norm'], 
             va='center', ha='center', fontsize=9, fontweight='bold', color='white')

plt.title('Top 20 districts by total 18+ enrollments (colored by state)', fontsize=12, fontweight='bold')
plt.xlabel('18+ enrollments', fontsize=11)
plt.ylabel('District', fontsize=11)

# Create custom legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=state_colors[state], label=state) for state in sorted(unique_states)]
plt.legend(handles=legend_elements, loc='lower right', fontsize=9, title='State', title_fontsize=10)

plt.tight_layout()
plt.savefig(f'{output_dir}/04_top20_districts_18plus.png', dpi=300, bbox_inches='tight')
plt.show()

# 5) Heatmap - month x top states 18+
plt.figure(figsize=(12,5))
sns.heatmap(heat_pivot, cmap='YlOrRd')
plt.title('18+ enrollments heatmap: top states across months')
plt.xlabel('Month')
plt.ylabel('State')
plt.tight_layout()
plt.savefig(f'{output_dir}/05_heatmap_states_months.png', dpi=300, bbox_inches='tight')
plt.show()

# 6) Share of 18+ by month (18+ / total)
month_totals = month_all_ages.copy()
month_totals['total_all_ages'] = month_totals['age_0_5'] + month_totals['age_5_17'] + month_totals['age_18_greater']
month_totals['share_18_plus'] = np.where(month_totals['total_all_ages'] > 0,
                                         month_totals['age_18_greater'] / month_totals['total_all_ages'],
                                         np.nan)
plt.figure(figsize=(10,4))
sns.lineplot(data=month_totals, x='month_dt', y='share_18_plus', marker='o', color='#DD8452')
plt.title('18+ share of total enrollments over time')
plt.xlabel('Month')
plt.ylabel('Share (18+ / total)')
plt.ylim(0, 1)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(f'{output_dir}/06_share_18plus_over_time.png', dpi=300, bbox_inches='tight')
plt.show()

# 7) Stacked area - all age groups by month (includes 18+)
plt.figure(figsize=(10,5))
month_plot = month_all_ages.sort_values('month_dt')
plt.stackplot(month_plot['month_dt'],
              month_plot['age_0_5'], month_plot['age_5_17'], month_plot['age_18_greater'],
              labels=['0-5','5-17','18+'], alpha=0.85)
plt.title('Enrollments by age group over time (stacked area)')
plt.xlabel('Month')
plt.ylabel('Enrollments')
plt.xticks(rotation=45, ha='right')
plt.legend(loc='upper left')
plt.tight_layout()
plt.savefig(f'{output_dir}/07_stacked_area_all_ages.png', dpi=300, bbox_inches='tight')
plt.show()

# Print a small summary table for monthly totals and share
summary_tbl = month_totals[['month_dt','age_18_greater','total_all_ages','share_18_plus']].copy()
print(summary_tbl.head(10))