# Create a suite of pictorial representations (bar, line, pie, heatmap, map-like treemap) and summary tables
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ast
import os

# Create output directory if it doesn't exist
output_dir = 'output/biometric/district'
os.makedirs(output_dir, exist_ok=True)


# Load bio_time_final.csv, inspect structure, and build a clean long-form dataset

raw_df = pd.read_csv('data/time_seperation/biometric/bio_time_final.csv', encoding='ascii')
print(raw_df.head(10))

# The preview suggests a wide-to-long mishap: a column named 'data' containing list-like rows
if 'data' in raw_df.columns:
    parsed_rows = raw_df['data'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    clean_df = pd.DataFrame(parsed_rows.tolist(), columns=['month','state_norm','district_resolved','value_1','value_2'])
else:
    clean_df = raw_df.copy()

# Basic cleanup
clean_df['month'] = clean_df['month'].astype(str).str.strip()
clean_df['state_norm'] = clean_df['state_norm'].astype(str).str.strip().str.lower()
clean_df['district_resolved'] = clean_df['district_resolved'].astype(str).str.strip().str.lower()
# Convert numeric columns to numeric type
for col in clean_df.columns:
    if col not in ['month','state_norm','district_resolved']:
        clean_df[col] = pd.to_numeric(clean_df[col], errors='coerce')

print(clean_df.head(10))
print(clean_df.describe(include='all'))

# Fix: the parsed dataframe already has correct column names bio_age_5_17 and bio_age_17_
print(clean_df.head())

num_cols = [c for c in clean_df.columns if c not in ['month','state_norm','district_resolved']]
for col in num_cols:
    clean_df[col] = pd.to_numeric(clean_df[col], errors='coerce')

print(num_cols)
print(clean_df[num_cols].describe())
sns.set_theme(style='whitegrid')

viz_df = clean_df.copy()
# Month ordering (parse Month YYYY)
viz_df['month_dt'] = pd.to_datetime(viz_df['month'], format='%B %Y', errors='coerce')

# Aggregate helpers
state_tot = viz_df.groupby('state_norm')[['bio_age_5_17','bio_age_17_']].sum().sort_values('bio_age_5_17', ascending=False)
state_tot['total'] = state_tot.sum(axis=1)

top10_states = state_tot.head(10)

# 1) Top states bar chart
plt.figure(figsize=(10,5))
top10_states['total'].sort_values().plot(kind='barh', color="#22D44F")
plt.title('Top 10 states by total biometric counts (both age groups)')
plt.xlabel('Total')
plt.ylabel('State')
plt.tight_layout()
plt.savefig(f'{output_dir}/01_top_states.png', dpi=300, bbox_inches='tight')
plt.show()

# 2) Age group composition for top 8 states stacked bar
plt.figure(figsize=(10,5))
stack_states = state_tot.head(8)[['bio_age_5_17','bio_age_17_']]
stack_states.plot(kind='bar', stacked=True, figsize=(10,5), colormap='tab20')
plt.title('Age-group composition for top 8 states')
plt.xlabel('State')
plt.ylabel('Count')
plt.xticks(rotation=35, ha='right')
plt.tight_layout()
plt.savefig(f'{output_dir}/02_age_composition.png', dpi=300, bbox_inches='tight')
plt.show()

# 3) National age split pie chart
national = viz_df[['bio_age_5_17','bio_age_17_']].sum()
plt.figure(figsize=(6,6))
plt.pie(national.values, labels=national.index, autopct='%1.1f%%', startangle=90)
plt.title('National share by age group')
plt.tight_layout()
plt.savefig(f'{output_dir}/03_national_age_pie.png', dpi=300, bbox_inches='tight')
plt.show()

# 4) Month trend line (national)
month_tot = viz_df.groupby('month_dt')[['bio_age_5_17','bio_age_17_']].sum().sort_index()
plt.figure(figsize=(10,5))
plt.plot(month_tot.index, month_tot['bio_age_5_17'], marker='o', label='Age 5-17')
plt.plot(month_tot.index, month_tot['bio_age_17_'], marker='o', label='Age 17+')
plt.title('Monthly trend (national)')
plt.xlabel('Month')
plt.ylabel('Count')
plt.legend()
plt.tight_layout()
plt.savefig(f'{output_dir}/04_monthly_trend.png', dpi=300, bbox_inches='tight')
plt.show()

# 5) Heatmap: top 12 states x month total
heat_df = viz_df.copy()
heat_df['total'] = heat_df['bio_age_5_17'] + heat_df['bio_age_17_']
heat_states = state_tot.head(12).index
heat_piv = heat_df[heat_df['state_norm'].isin(heat_states)].groupby(['state_norm','month_dt'])['total'].sum().reset_index()
heat_piv = heat_piv.pivot(index='state_norm', columns='month_dt', values='total').fillna(0)
heat_piv = heat_piv.loc[heat_states]

plt.figure(figsize=(12,6))
sns.heatmap(heat_piv, cmap='YlGnBu', linewidths=0.2)
plt.title('Heatmap: total counts by month (top 12 states)')
plt.xlabel('Month')
plt.ylabel('State')
plt.tight_layout()
plt.savefig(f'{output_dir}/05_states_heatmap.png', dpi=300, bbox_inches='tight')
plt.show()

# 6) District concentration: top 15 districts overall
district_tot = viz_df.groupby(['state_norm','district_resolved'])[['bio_age_5_17','bio_age_17_']].sum()
district_tot['total'] = district_tot.sum(axis=1)
district_top15 = district_tot.sort_values('total', ascending=False).head(15).reset_index()

plt.figure(figsize=(10,6))
sns.barplot(data=district_top15, y='district_resolved', x='total', hue='state_norm', dodge=False)
plt.title('Top 15 districts by total counts')
plt.xlabel('Total')
plt.ylabel('District')
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
plt.tight_layout()
plt.savefig(f'{output_dir}/06_top_districts.png', dpi=300, bbox_inches='tight')
plt.show()

# 7) Pie chart: share of total accounted for by top 10 states vs rest
share_top10 = state_tot['total'].head(10).sum()
share_rest = state_tot['total'].sum() - share_top10
plt.figure(figsize=(6,6))
plt.pie([share_top10, share_rest], labels=['Top 10 states','All other states'], autopct='%1.1f%%', startangle=90)
plt.title('Concentration: Top 10 states vs rest')
plt.tight_layout()
plt.savefig(f'{output_dir}/07_top10_concentration.png', dpi=300, bbox_inches='tight')
plt.show()

# 8) Histogram: distribution of district totals
plt.figure(figsize=(9,5))
plt.hist(district_tot['total'].values, bins=40, color='#7D3C98', alpha=0.85)
plt.title('Distribution of district totals')
plt.xlabel('Total per district (all months)')
plt.ylabel('Number of districts')
plt.tight_layout()
plt.savefig(f'{output_dir}/08_district_histogram.png', dpi=300, bbox_inches='tight')
plt.show()
# Summary artifacts for later narrative
summary_info = {
    'rows': len(viz_df),
    'states': viz_df['state_norm'].nunique(),
    'districts': viz_df['district_resolved'].nunique(),
    'months': viz_df['month'].nunique(),
    'national_age_5_17': float(national['bio_age_5_17']),
    'national_age_17p': float(national['bio_age_17_']),
}
print(summary_info)
print(state_tot.head(10))
print(district_top15.head(10))