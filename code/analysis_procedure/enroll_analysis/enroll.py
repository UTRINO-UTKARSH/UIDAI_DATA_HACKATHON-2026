# Build clean_df from the already-correctly-read raw_df and create 10 analyses with charts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ast

file_path = './enroll_ms.csv'
raw_df = pd.read_csv(file_path, encoding='ascii')
print(raw_df.head(10))

# The file appears to be a 3-column export with a 'data' column containing a Python-list-like string.
# Parse that into columns: month, state_norm, age_0_5, age_5_17, age_18_greater
parsed_rows = []
for row_val in raw_df['data'].astype(str).tolist():
    try:
        row_list = ast.literal_eval(row_val)
    except Exception:
        row_list = None
    if isinstance(row_list, list) and len(row_list) >= 5:
        parsed_rows.append(row_list[:5])

clean_df = pd.DataFrame(parsed_rows, columns=['month', 'state_norm', 'age_0_5', 'age_5_17', 'age_18_greater'])

# Coerce numeric
for col_name in ['age_0_5', 'age_5_17', 'age_18_greater']:
    clean_df[col_name] = pd.to_numeric(clean_df[col_name], errors='coerce').fillna(0).astype(int)

# Basic derived metrics
clean_df['total'] = clean_df['age_0_5'] + clean_df['age_5_17'] + clean_df['age_18_greater']
clean_df['share_0_5'] = np.where(clean_df['total'] > 0, clean_df['age_0_5'] / clean_df['total'], 0.0)
clean_df['share_5_17'] = np.where(clean_df['total'] > 0, clean_df['age_5_17'] / clean_df['total'], 0.0)
clean_df['share_18_plus'] = np.where(clean_df['total'] > 0, clean_df['age_18_greater'] / clean_df['total'], 0.0)

print(clean_df.head(10))
print(clean_df['month'].value_counts().head(10))
print(clean_df.shape)

# Keep for later cells


clean_df = raw_df.copy()
for col_name in ['age_0_5', 'age_5_17', 'age_18_greater']:
    clean_df[col_name] = pd.to_numeric(clean_df[col_name], errors='coerce').fillna(0)

clean_df['total'] = clean_df['age_0_5'] + clean_df['age_5_17'] + clean_df['age_18_greater']
clean_df['share_0_5'] = np.where(clean_df['total'] > 0, clean_df['age_0_5'] / clean_df['total'], 0.0)
clean_df['share_5_17'] = np.where(clean_df['total'] > 0, clean_df['age_5_17'] / clean_df['total'], 0.0)
clean_df['share_18_plus'] = np.where(clean_df['total'] > 0, clean_df['age_18_greater'] / clean_df['total'], 0.0)

# Month ordering
month_vals = clean_df['month'].astype(str)
clean_df['month_dt'] = pd.to_datetime(month_vals, format='%B %Y', errors='coerce')

print(clean_df.head(10))

sns.set_theme(style='whitegrid')

# 1) National totals by month (stacked area)
agg_month = clean_df.groupby('month_dt', dropna=False)[['age_0_5','age_5_17','age_18_greater','total']].sum().sort_index()
plt.figure(figsize=(10,5))
plt.stackplot(agg_month.index,
              agg_month['age_0_5'], agg_month['age_5_17'], agg_month['age_18_greater'],
              labels=['0-5','5-17','18+'], alpha=0.85)
plt.legend(loc='upper left')
plt.title('Enrollments by Age Group Over Time (All States)')
plt.xlabel('Month')
plt.ylabel('Enrollments')
plt.tight_layout()
plt.savefig('../../../output/enroll/01_enrollments_by_age_group_timeline.png', dpi=300, bbox_inches='tight')
plt.close()

# 2) Top 15 states by total (latest month)
latest_month = clean_df['month_dt'].max()
latest_df = clean_df[clean_df['month_dt'] == latest_month].copy()
state_totals_latest = latest_df.groupby('state_norm')[['total']].sum().sort_values('total', ascending=False).head(15)
plt.figure(figsize=(10,6))
sns.barplot(x=state_totals_latest['total'].values, y=state_totals_latest.index, color='#2a9d8f')
plt.title('Top 15 States by Total Enrollment (' + str(latest_month.date()) + ')')
plt.xlabel('Total')
plt.ylabel('State')
plt.tight_layout()
plt.savefig('../../../output/enroll/02_top_15_states_total_enrollment.png', dpi=300, bbox_inches='tight')
plt.close()

# 3) Age mix for top 10 states (latest month) - stacked bars
top_states = state_totals_latest.index[:10].tolist()
top_mix = latest_df[latest_df['state_norm'].isin(top_states)].groupby('state_norm')[['age_0_5','age_5_17','age_18_greater']].sum()
top_mix = top_mix.loc[top_states]
plt.figure(figsize=(10,6))
plt.barh(top_mix.index, top_mix['age_0_5'], label='0-5')
plt.barh(top_mix.index, top_mix['age_5_17'], left=top_mix['age_0_5'], label='5-17')
plt.barh(top_mix.index, top_mix['age_18_greater'], left=top_mix['age_0_5']+top_mix['age_5_17'], label='18+')
plt.title('Age Composition for Top 10 States (' + str(latest_month.date()) + ')')
plt.xlabel('Enrollments')
plt.ylabel('State')
plt.legend(loc='lower right')
plt.tight_layout()
plt.savefig('../../../output/enroll/03_top_10_states_age_composition.png', dpi=300, bbox_inches='tight')
plt.close()

# 4) Distribution of totals across states (latest month)
plt.figure(figsize=(10,5))
sns.histplot(latest_df['total'], bins=30, kde=True, color='#457b9d')
plt.title('Distribution of State Total Enrollment (' + str(latest_month.date()) + ')')
plt.xlabel('Total Enrollment')
plt.ylabel('Count of States/UTs')
plt.tight_layout()
plt.savefig('../../../output/enroll/04_enrollment_distribution_by_state.png', dpi=300, bbox_inches='tight')
plt.close()

# 5) Scatter: total vs share of 5-17 (latest)
plt.figure(figsize=(8,6))
sns.scatterplot(data=latest_df, x='total', y='share_5_17', size='total', sizes=(20, 400), alpha=0.7, legend=False)
plt.title('Total vs Share of Age 5-17 (' + str(latest_month.date()) + ')')
plt.xlabel('Total Enrollment')
plt.ylabel('Share age 5-17')
plt.tight_layout()
plt.savefig('../../../output/enroll/05_total_vs_age_5_17_share.png', dpi=300, bbox_inches='tight')
plt.close()

# 6) Top 10 states growth from earliest to latest (total)
earliest_month = clean_df['month_dt'].min()
earliest_df = clean_df[clean_df['month_dt'] == earliest_month].groupby('state_norm')[['total']].sum()
latest_state_total = latest_df.groupby('state_norm')[['total']].sum()
growth = latest_state_total.join(earliest_df, lsuffix='_latest', rsuffix='_earliest', how='outer').fillna(0)
growth['abs_change'] = growth['total_latest'] - growth['total_earliest']
growth_top = growth.sort_values('abs_change', ascending=False).head(10)
plt.figure(figsize=(10,6))
sns.barplot(x=growth_top['abs_change'].values, y=growth_top.index, color='#e76f51')
plt.title('Top 10 States by Absolute Change (Earliest to Latest)')
plt.xlabel('Absolute Change in Total')
plt.ylabel('State')
plt.tight_layout()
plt.savefig('../../../output/enroll/06_top_10_states_growth_earliest_to_latest.png', dpi=300, bbox_inches='tight')
plt.close()

# 7) Heatmap: totals by state (top 15) and month
pivot_totals = clean_df.pivot_table(index='state_norm', columns='month_dt', values='total', aggfunc='sum', fill_value=0)
row_order = pivot_totals.sum(axis=1).sort_values(ascending=False).head(15).index
pivot_top = pivot_totals.loc[row_order].sort_index(axis=1)
plt.figure(figsize=(12,6))
sns.heatmap(pivot_top, cmap='YlGnBu')
plt.title('Heatmap of Total Enrollment - Top 15 States Across Months')
plt.xlabel('Month')
plt.ylabel('State')
plt.tight_layout()
plt.savefig('../../../output/enroll/07_states_enrollment_heatmap_by_month.png', dpi=300, bbox_inches='tight')
plt.close()

# 8) National share by age group over time (line)
shares_month = agg_month[['age_0_5','age_5_17','age_18_greater']].div(agg_month['total'], axis=0).replace([np.inf, -np.inf], 0).fillna(0)
plt.figure(figsize=(10,5))
plt.plot(shares_month.index, shares_month['age_0_5'], label='0-5')
plt.plot(shares_month.index, shares_month['age_5_17'], label='5-17')
plt.plot(shares_month.index, shares_month['age_18_greater'], label='18+')
plt.title('National Age-Group Shares Over Time')
plt.xlabel('Month')
plt.ylabel('Share of Total')
plt.ylim(0, 1)
plt.legend(loc='best')
plt.tight_layout()
plt.savefig('../../../output/enroll/08_national_age_group_shares_timeline.png', dpi=300, bbox_inches='tight')
plt.close()

# 9) Concentration curve: cumulative share of national total by top states (latest)
latest_sorted = latest_df.groupby('state_norm')[['total']].sum().sort_values('total', ascending=False)
latest_sorted['cum_share'] = latest_sorted['total'].cumsum() / max(latest_sorted['total'].sum(), 1)
plt.figure(figsize=(10,5))
plt.plot(range(1, len(latest_sorted)+1), latest_sorted['cum_share'].values, color='#6a4c93')
plt.axhline(0.5, color='gray', linestyle='--', linewidth=1)
plt.axhline(0.8, color='gray', linestyle='--', linewidth=1)
plt.title('Concentration of Enrollment by States (Latest Month)')
plt.xlabel('Number of top states included')
plt.ylabel('Cumulative share of national total')
plt.tight_layout()
plt.savefig('../../../output/enroll/09_enrollment_concentration_curve.png', dpi=300, bbox_inches='tight')
plt.close()

# 10) Correlation heatmap between age groups and total (all rows)
corr_mat = clean_df[['age_0_5','age_5_17','age_18_greater','total']].corr()
plt.figure(figsize=(6,5))
sns.heatmap(corr_mat, annot=True, cmap='RdBu_r', vmin=-1, vmax=1)
plt.title('Correlation Between Age Buckets and Total')
plt.tight_layout()
plt.savefig('../../../output/enroll/10_age_groups_correlation_matrix.png', dpi=300, bbox_inches='tight')
plt.close()

# Tables to reference in narrative
print(agg_month.tail(6))
print(state_totals_latest.head(15))
print(growth_top)