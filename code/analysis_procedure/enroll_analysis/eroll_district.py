# Load the uploaded CSV and do a quick first look
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Create output directory if it doesn't exist
output_dir = 'output/enroll/district'
os.makedirs(output_dir, exist_ok=True)

csv_path = 'data/time_seperation/enroll/enroll_time_final.csv'
df_enroll = pd.read_csv(csv_path, encoding='ascii')

print(df_enroll.head(10))
print(df_enroll.shape)

# Basic quick visualization: total enrollments distribution
age_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
df_enroll['total_enroll'] = df_enroll[age_cols].sum(axis=1)

plt.figure(figsize=(8,4))
sns.histplot(df_enroll['total_enroll'], bins=30, kde=True)
plt.title('Distribution of total enrollments per district-month row')
plt.xlabel('Total enrollments (age_0_5 + age_5_17 + age_18_greater)')
plt.ylabel('Count of rows')
plt.tight_layout()
plt.savefig(f'{output_dir}/00_distribution_intro.png', dpi=300, bbox_inches='tight')
plt.close()

# Create 15+ analyses with multiple charts including pie charts and save a few key figures

sns.set_theme(style='whitegrid')

# Parse month to datetime for ordering
month_dt = pd.to_datetime(df_enroll['month'], format='%B %Y', errors='coerce')
df_enroll['month_dt'] = month_dt

# Aggregations
by_month = df_enroll.groupby('month_dt')[age_cols].sum().sort_index().reset_index()
by_month['total'] = by_month[age_cols].sum(axis=1)

by_state = df_enroll.groupby('state_norm')[age_cols].sum().sort_values(by='age_5_17', ascending=False)
by_state['total'] = by_state[age_cols].sum(axis=1)

by_district = df_enroll.groupby(['state_norm','district_resolved'])[age_cols].sum()
by_district['total'] = by_district[age_cols].sum(axis=1)
by_district_sorted = by_district.sort_values('total', ascending=False).reset_index()

# 1) Line chart: total by month
plt.figure(figsize=(10,4))
plt.plot(by_month['month_dt'], by_month['total'], marker='o')
plt.title('Total enrollments over time (all states & districts)')
plt.xlabel('Month')
plt.ylabel('Total enrollments')
plt.tight_layout()
plt.savefig(f'{output_dir}/01_total_by_month.png', dpi=300, bbox_inches='tight')
plt.close()

# 2) Stacked area: age composition over time
plt.figure(figsize=(10,4))
plt.stackplot(by_month['month_dt'], by_month['age_0_5'], by_month['age_5_17'], by_month['age_18_greater'],
             labels=['age_0_5','age_5_17','age_18_greater'], alpha=0.85)
plt.title('Age-group composition over time (stacked area)')
plt.xlabel('Month')
plt.ylabel('Enrollments')
plt.legend(loc='upper left')
plt.tight_layout()
plt.savefig(f'{output_dir}/02_age_composition_stacked.png', dpi=300, bbox_inches='tight')
plt.close()

# 3) Pie chart: overall age distribution
overall_age = df_enroll[age_cols].sum()
plt.figure(figsize=(6,6))
plt.pie(overall_age.values, labels=overall_age.index, autopct='%1.1f%%', startangle=90)
plt.title('Overall enrollment share by age group')
plt.tight_layout()
plt.savefig(f'{output_dir}/03_overall_age_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# 4) Bar: top 15 states by total
state_top15 = by_state.sort_values('total', ascending=False).head(15)
plt.figure(figsize=(10,5))
sns.barplot(x=state_top15['total'].values, y=state_top15.index, orient='h')
plt.title('Top 15 states by total enrollments')
plt.xlabel('Total enrollments')
plt.ylabel('State')
plt.tight_layout()
plt.savefig(f'{output_dir}/04_top_15_states.png', dpi=300, bbox_inches='tight')
plt.close()

# 5) Pie chart: share by top 10 states (others grouped)
state_totals = by_state['total'].sort_values(ascending=False)
state_top10 = state_totals.head(10)
others = state_totals.iloc[10:].sum()
pie_vals = pd.concat([state_top10, pd.Series({'others': others})])
plt.figure(figsize=(7,7))
plt.pie(pie_vals.values, labels=pie_vals.index, autopct='%1.1f%%', startangle=90)
plt.title('Total enrollment share by state (Top 10 + Others)')
plt.tight_layout()
plt.savefig(f'{output_dir}/05_top10_states_share.png', dpi=300, bbox_inches='tight')
plt.close()

# 6) Bar: top 20 districts by total
district_top20 = by_district_sorted.head(20).copy()
district_top20['label'] = district_top20['district_resolved'] + ', ' + district_top20['state_norm']
plt.figure(figsize=(10,6))
sns.barplot(x='total', y='label', data=district_top20, orient='h')
plt.title('Top 20 districts by total enrollments')
plt.xlabel('Total enrollments')
plt.ylabel('District, State')
plt.tight_layout()
plt.savefig(f'{output_dir}/06_top_20_districts.png', dpi=300, bbox_inches='tight')
plt.close()

# 7) Heatmap: month x age group (normalized share)
by_month_share = by_month.copy()
for c in age_cols:
    by_month_share[c] = by_month_share[c] / by_month_share['total'].replace(0, np.nan)
heat_df = by_month_share.set_index('month_dt')[age_cols]
plt.figure(figsize=(8,4))
sns.heatmap(heat_df.T, cmap='viridis', cbar_kws={'label':'Share'})
plt.title('Share of enrollments by age group over time (heatmap)')
plt.xlabel('Month')
plt.ylabel('Age group')
plt.tight_layout()
plt.savefig(f'{output_dir}/07_age_group_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()

# 8) Boxplot: distribution by age group across all district-month rows
plt.figure(figsize=(8,4))
sns.boxplot(data=df_enroll[age_cols])
plt.title('Distribution across district-month rows by age group')
plt.xlabel('Age group')
plt.ylabel('Enrollments per row')
plt.tight_layout()
plt.savefig(f'{output_dir}/08_age_group_boxplot.png', dpi=300, bbox_inches='tight')
plt.close()

# 9) Correlation heatmap among age groups
corr = df_enroll[age_cols].corr()
plt.figure(figsize=(5,4))
sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
plt.title('Correlation between age-group enrollments')
plt.tight_layout()
plt.savefig(f'{output_dir}/09_age_correlation_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()

# 10) Scatter: age_5_17 vs age_18_greater with size by age_0_5
plt.figure(figsize=(7,5))
plt.scatter(df_enroll['age_5_17'], df_enroll['age_18_greater'],
            s=(df_enroll['age_0_5'] + 1) * 0.8, alpha=0.25)
plt.title('Relationship between age_5_17 and age_18_greater (bubble size = age_0_5)')
plt.xlabel('age_5_17')
plt.ylabel('age_18_greater')
plt.tight_layout()
plt.savefig(f'{output_dir}/10_age_scatter.png', dpi=300, bbox_inches='tight')
plt.close()

# 11) Pareto-style: cumulative contribution of top districts
district_tot = by_district_sorted['total'].values
cum_share = np.cumsum(district_tot) / np.sum(district_tot)
plt.figure(figsize=(10,4))
plt.plot(np.arange(1, len(cum_share) + 1), cum_share)
plt.axhline(0.8, color='red', linestyle='--', linewidth=1)
plt.title('Cumulative share of total enrollments by districts (sorted)')
plt.xlabel('Top N districts')
plt.ylabel('Cumulative share')
plt.tight_layout()
plt.savefig(f'{output_dir}/11_pareto_districts.png', dpi=300, bbox_inches='tight')
plt.close()

# 12) Identify months with highest totals
month_rank = by_month[['month_dt','total']].sort_values('total', ascending=False).head(10)
print(month_rank)

# 13) State age-mix: stacked bar for top 10 states
state_top10_mix = by_state.sort_values('total', ascending=False).head(10)[age_cols]
state_top10_mix = state_top10_mix.loc[state_top10_mix.sum(axis=1).sort_values(ascending=False).index]
plt.figure(figsize=(10,5))
state_top10_mix.plot(kind='bar', stacked=True)
plt.title('Age-group mix for top 10 states (stacked bars)')
plt.xlabel('State')
plt.ylabel('Enrollments')
plt.tight_layout()
plt.savefig(f'{output_dir}/13_state_age_mix.png', dpi=300, bbox_inches='tight')
plt.close()

# 14) Month-over-month growth for total
by_month_growth = by_month[['month_dt','total']].copy()
by_month_growth['mom_growth_pct'] = by_month_growth['total'].pct_change() * 100
plt.figure(figsize=(10,4))
plt.plot(by_month_growth['month_dt'], by_month_growth['mom_growth_pct'], marker='o')
plt.axhline(0, color='black', linewidth=1)
plt.title('Month-over-month growth rate of total enrollments (%)')
plt.xlabel('Month')
plt.ylabel('MoM growth (%)')
plt.tight_layout()
plt.savefig(f'{output_dir}/14_mom_growth.png', dpi=300, bbox_inches='tight')
plt.close()

# 15) District variability over time: sample a state with most rows and show top districts trend
state_counts = df_enroll['state_norm'].value_counts()
state_focus = state_counts.index[0]
df_state = df_enroll[df_enroll['state_norm'] == state_focus].copy()
df_state['total'] = df_state[age_cols].sum(axis=1)
# pick top 5 districts by total within that state
state_district_tot = df_state.groupby('district_resolved')['total'].sum().sort_values(ascending=False).head(5)
df_state_top = df_state[df_state['district_resolved'].isin(state_district_tot.index)]
trend = df_state_top.groupby(['month_dt','district_resolved'])['total'].sum().reset_index().sort_values('month_dt')
plt.figure(figsize=(10,5))
sns.lineplot(data=trend, x='month_dt', y='total', hue='district_resolved', marker='o')
plt.title('Top 5 districts trend in ' + str(state_focus))
plt.xlabel('Month')
plt.ylabel('Total enrollments')
plt.tight_layout()
plt.savefig(f'{output_dir}/15_district_trend.png', dpi=300, bbox_inches='tight')
plt.close()

# Extra: summary stats table for totals per row
print(df_enroll['total_enroll'].describe())