# Create month ordering, totals, and core derived metrics; then produce multiple graphs including a pie chart across all states
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load the uploaded CSV and do a quick sanity check


bio_ms_df = pd.read_csv('state_based/bio_ms.csv')
print(bio_ms_df.head())
print(bio_ms_df.describe(include='all'))

# Basic cleanup
bio_ms_df.columns = [c.strip() for c in bio_ms_df.columns]
bio_ms_df['month'] = bio_ms_df['month'].astype(str).str.strip()
bio_ms_df['state_norm'] = bio_ms_df['state_norm'].astype(str).str.strip()

# Ensure numeric columns
num_cols = [c for c in bio_ms_df.columns if c not in ['month', 'state_norm']]
for c in num_cols:
    bio_ms_df[c] = pd.to_numeric(bio_ms_df[c], errors='coerce')

print(bio_ms_df.head())

sns.set_theme(style='whitegrid')

# Parse month into a sortable datetime (assumes format like 'March 2025')
bio_ms_df['month_dt'] = pd.to_datetime(bio_ms_df['month'], format='%B %Y', errors='coerce')

# Derived totals
bio_ms_df['total_bio'] = bio_ms_df['bio_age_5_17'].fillna(0) + bio_ms_df['bio_age_17_'].fillna(0)

# Aggregations
state_totals_df = bio_ms_df.groupby('state_norm', as_index=False)[['bio_age_5_17','bio_age_17_','total_bio']].sum()
state_totals_df = state_totals_df.sort_values('total_bio', ascending=False)

month_totals_df = bio_ms_df.groupby('month_dt', as_index=False)[['bio_age_5_17','bio_age_17_','total_bio']].sum().sort_values('month_dt')

# Shares and ratios
state_totals_df['share_total'] = state_totals_df['total_bio'] / state_totals_df['total_bio'].sum()
state_totals_df['u5_17_share_within_state'] = state_totals_df['bio_age_5_17'] / state_totals_df['total_bio'].replace(0, np.nan)
state_totals_df['u17p_share_within_state'] = state_totals_df['bio_age_17_'] / state_totals_df['total_bio'].replace(0, np.nan)

# Long format for stacked/grouped plots
long_state_df = state_totals_df.melt(id_vars=['state_norm'], value_vars=['bio_age_5_17','bio_age_17_'], var_name='age_group', value_name='count')

# --- Plot 1: Total by state (bar)
plt.figure(figsize=(12, 8))
sns.barplot(data=state_totals_df, y='state_norm', x='total_bio', color='#4c72b0')
plt.title('Total BIO counts by state (all months)')
plt.xlabel('Total')
plt.ylabel('State')
plt.tight_layout()
plt.savefig('output/biometric/01_state_totals_bar.png', dpi=300, bbox_inches='tight')
# plt.close()

# --- Plot 2: Split by age group (stacked-ish via hue, top 15)
top15_states = state_totals_df.head(15)['state_norm'].tolist()
top15_long_df = long_state_df[long_state_df['state_norm'].isin(top15_states)].copy()
plt.figure(figsize=(12, 7))
sns.barplot(data=top15_long_df, x='count', y='state_norm', hue='age_group')
plt.title('Top 15 states split by age group (all months)')
plt.xlabel('Count')
plt.ylabel('State')
plt.legend(title='Age group')
plt.tight_layout()
plt.savefig('output/biometric/02_top_15_states_by_age_group.png', dpi=300, bbox_inches='tight')
# plt.close()

# --- Plot 3: Monthly trend total
plt.figure(figsize=(10, 5))
sns.lineplot(data=month_totals_df, x='month_dt', y='total_bio', marker='o')
plt.title('Monthly total BIO trend (all states)')
plt.xlabel('Month')
plt.ylabel('Total')
plt.tight_layout()
plt.savefig('output/biometric/03_monthly_trend_total.png', dpi=300, bbox_inches='tight')
# plt.close()

# --- Plot 4: Monthly trend by age group
month_long_df = bio_ms_df.groupby('month_dt', as_index=False)[['bio_age_5_17','bio_age_17_']].sum().sort_values('month_dt')
month_long_df = month_long_df.melt(id_vars=['month_dt'], value_vars=['bio_age_5_17','bio_age_17_'], var_name='age_group', value_name='count')
plt.figure(figsize=(10, 5))
sns.lineplot(data=month_long_df, x='month_dt', y='count', hue='age_group', marker='o')
plt.title('Monthly BIO trend by age group (all states)')
plt.xlabel('Month')
plt.ylabel('Count')
plt.tight_layout()
plt.savefig('output/biometric/04_monthly_trend_by_age_group.png', dpi=300, bbox_inches='tight')
# plt.close()

# --- Plot 5: Heatmap state x month (total)
heat_df = bio_ms_df.pivot_table(index='state_norm', columns='month_dt', values='total_bio', aggfunc='sum', fill_value=0)
heat_df = heat_df.loc[state_totals_df['state_norm']]  # order by total
plt.figure(figsize=(12, 10))
sns.heatmap(heat_df, cmap='Blues')
plt.title('Heatmap of total BIO by state and month')
plt.xlabel('Month')
plt.ylabel('State')
plt.tight_layout()
plt.savefig('output/biometric/05_state_month_heatmap.png', dpi=300, bbox_inches='tight')
# plt.close()
# --- Plot 6: Pie chart of state shares
# Improve the pie chart readability and produce a table with % share for each state

# Use the already-computed state_totals_df if present; otherwise compute quickly from bio_ms_df
try:
    state_totals_df
except NameError:
    state_totals_df = bio_ms_df.groupby('state_norm', as_index=False)[['bio_age_5_17','bio_age_17_']].sum()
    state_totals_df['total_bio'] = state_totals_df['bio_age_5_17'].fillna(0) + state_totals_df['bio_age_17_'].fillna(0)

state_totals_df = state_totals_df.sort_values('total_bio', ascending=False).copy()
state_totals_df['share_pct'] = 100 * state_totals_df['total_bio'] / state_totals_df['total_bio'].sum()

# Improved pie: show top N as slices, rest grouped as Other (keeps it legible)
top_n = 12
pie_df = state_totals_df.head(top_n).copy()
other_sum = state_totals_df.iloc[top_n:]['total_bio'].sum()
if other_sum > 0:
    pie_df = pd.concat([
        pie_df,
        pd.DataFrame({'state_norm': ['Other'], 'total_bio': [other_sum]})
    ], ignore_index=True)

pie_df['share_pct'] = 100 * pie_df['total_bio'] / pie_df['total_bio'].sum()

# Draw pie with percentages on wedges
plt.figure(figsize=(10, 10))
colors_vals = plt.cm.tab20(np.linspace(0, 1, len(pie_df)))
wedges, texts, autotexts = plt.pie(
    pie_df['total_bio'].values,
    labels=pie_df['state_norm'].values,
    autopct=lambda p: ('%.1f%%' % p) if p >= 2 else '',
    startangle=90,
    counterclock=False,
    colors=colors_vals,
    textprops={'fontsize': 10}
)
plt.title('Share of total BIO by state (Top ' + str(top_n) + ' + Other)')
plt.tight_layout()
plt.savefig('output/biometric/06_state_share_pie_chart.png', dpi=300, bbox_inches='tight')
# plt.close()


# --- Plot 7: Distribution of state totals
plt.figure(figsize=(10, 5))
sns.histplot(state_totals_df['total_bio'], bins=20, kde=True, color='#55a868')
plt.title('Distribution of total BIO across states')
plt.xlabel('Total per state (all months)')
plt.ylabel('Number of states')
plt.tight_layout()
plt.savefig('output/biometric/07_state_total_distribution.png', dpi=300, bbox_inches='tight')
# plt.close()

# --- Plot 8: Top 10 states share (bar, %)
top10_share_df = state_totals_df.head(10).copy()
top10_share_df['share_pct'] = 100 * top10_share_df['share_total']
plt.figure(figsize=(10, 6))
sns.barplot(data=top10_share_df, x='share_pct', y='state_norm', color='#c44e52')
plt.title('Top 10 states by share of total BIO (all months)')
plt.xlabel('Share (%)')
plt.ylabel('State')
plt.tight_layout()
plt.savefig('output/biometric/08_top_10_states_share_percentage.png', dpi=300, bbox_inches='tight')
# plt.close()

# --- Plot 9: Within-state composition scatter
plt.figure(figsize=(8, 6))
sns.scatterplot(data=state_totals_df, x='u5_17_share_within_state', y='total_bio', size='total_bio', sizes=(40, 400), alpha=0.7)
plt.title('Within-state composition: share age 5-17 vs total')
plt.xlabel('Share age 5-17 within state')
plt.ylabel('Total (all months)')
plt.tight_layout()
plt.savefig('output/biometric/09_within_state_composition_scatter.png', dpi=300, bbox_inches='tight')
# plt.close()

# --- Plot 10: Boxplot of monthly totals across states
state_month_totals_df = bio_ms_df.groupby(['month_dt','state_norm'], as_index=False)['total_bio'].sum()
plt.figure(figsize=(10, 5))
sns.boxplot(data=state_month_totals_df, x='month_dt', y='total_bio', color='#8172b2')
plt.title('Spread across states each month (boxplot of state totals)')
plt.xlabel('Month')
plt.ylabel('State total')
plt.tight_layout()
plt.savefig('output/biometric/10_monthly_spread_boxplot.png', dpi=300, bbox_inches='tight')
# plt.close()

# Print a couple useful tables (head only)
print(state_totals_df.head(10))
print(month_totals_df)