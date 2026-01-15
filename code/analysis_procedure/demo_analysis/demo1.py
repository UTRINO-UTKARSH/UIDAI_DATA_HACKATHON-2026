# Create 10 analyses with graphs, including a pie chart of state shares
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

csv_path = 'state_based/demo_month_state.csv'
df_month_state = pd.read_csv(csv_path, encoding='ascii')

print(df_month_state.head(10))
print(df_month_state.shape)
print(df_month_state.columns.tolist())

# Basic cleaning: parse month to datetime (assume format like 'March 2025')
df_month_state['month_dt'] = pd.to_datetime(df_month_state['month'], format='%B %Y', errors='coerce')

# Identify metric columns (everything except month/state/month_dt)
exclude_cols = set(['month', 'state_norm', 'month_dt'])
metric_cols = [c for c in df_month_state.columns if c not in exclude_cols]
print(metric_cols)

# Ensure numeric
for c in metric_cols:
    df_month_state[c] = pd.to_numeric(df_month_state[c], errors='coerce')

# Overview stats
print(df_month_state[metric_cols].describe().T.head(15))

# Simple visualization: total across all states by month for first metric
if len(metric_cols) > 0:
    metric_0 = metric_cols[0]
    monthly_totals = df_month_state.groupby('month_dt', dropna=False)[metric_0].sum().sort_index()
    plt.figure(figsize=(10,4))
    sns.lineplot(x=monthly_totals.index, y=monthly_totals.values)
    plt.title('Monthly total of ' + metric_0 + ' across all states')
    plt.xlabel('Month')
    plt.ylabel(metric_0)
    plt.tight_layout()
    plt.savefig('output/demographic/state_time/01_monthly_total_' + metric_0 + '.png', dpi=300, bbox_inches='tight')
    plt.show()

sns.set_theme(style='whitegrid')

metric_cols = [c for c in df_month_state.columns if c not in ['month', 'state_norm', 'month_dt']]

df_month_state['total_all_metrics'] = df_month_state[metric_cols].sum(axis=1)

# 1) Data coverage: months and states
months_sorted = df_month_state['month_dt'].dropna().sort_values().unique()
states_sorted = sorted(df_month_state['state_norm'].dropna().unique().tolist())
print(len(months_sorted))
print(months_sorted[:5])
print(len(states_sorted))
print(states_sorted[:10])

# Helper aggregates
state_totals = df_month_state.groupby('state_norm')[metric_cols + ['total_all_metrics']].sum().sort_values('total_all_metrics', ascending=False)
month_totals = df_month_state.groupby('month_dt')[metric_cols + ['total_all_metrics']].sum().sort_index()

print(state_totals.head(10))
print(month_totals.head(5))

# 2) Monthly trend total
plt.figure(figsize=(10,4))
sns.lineplot(x=month_totals.index, y=month_totals['total_all_metrics'].values, marker='o')
plt.title('Monthly total across all states (sum of all metrics)')
plt.xlabel('Month')
plt.ylabel('Total')
plt.tight_layout()
plt.savefig('output/demographic/state_time/02_monthly_trend_total.png', dpi=300, bbox_inches='tight')
plt.show()

# 3) Monthly trend per metric
plt.figure(figsize=(10,4))
for c in metric_cols:
    sns.lineplot(x=month_totals.index, y=month_totals[c].values, marker='o', label=c)
plt.title('Monthly totals by metric (across all states)')
plt.xlabel('Month')
plt.ylabel('Total')
plt.legend()
plt.tight_layout()
plt.savefig('output/demographic/state_time/03_monthly_trend_per_metric.png', dpi=300, bbox_inches='tight')
plt.show()

# 4) Top 15 states by total
plt.figure(figsize=(10,6))
state_totals_top15 = state_totals.head(15).reset_index()
sns.barplot(data=state_totals_top15, y='state_norm', x='total_all_metrics', color='#4c72b0')
plt.title('Top 15 states by total (sum of all metrics)')
plt.xlabel('Total')
plt.ylabel('State')
plt.tight_layout()
plt.savefig('output/demographic/state_time/04_top_15_states.png', dpi=300, bbox_inches='tight')
plt.show()

# 5) Heatmap state x metric totals (top 20 states)
heat_df = state_totals.head(20)[metric_cols]
plt.figure(figsize=(10,7))
sns.heatmap(heat_df, cmap='Blues', linewidths=0.5)
plt.title('Top 20 states - totals by metric')
plt.xlabel('Metric')
plt.ylabel('State')
plt.tight_layout()
plt.savefig('output/demographic/state_time/05_heatmap_top_20_states.png', dpi=300, bbox_inches='tight')
plt.show()

# 6) Pie chart for all states share (group small into Other to keep readable)
share_series = state_totals['total_all_metrics'].copy()
share_pct = share_series / share_series.sum()
major = share_pct[share_pct >= 0.02]
minor_sum = share_pct[share_pct < 0.02].sum()
share_pie = major.copy()
share_pie.loc['other'] = minor_sum

plt.figure(figsize=(9,9))
plt.pie(share_pie.values, labels=share_pie.index, autopct='%1.1f%%', startangle=90, counterclock=False)
plt.title('Share of total by state (all states, small grouped as other)')
plt.tight_layout()
plt.savefig('output/demographic/state_time/06_pie_chart_state_share.png', dpi=300, bbox_inches='tight')
plt.show()

# 7) Distribution across states (boxplot) for each metric
plt.figure(figsize=(10,5))
df_long = df_month_state.melt(id_vars=['month_dt', 'state_norm'], value_vars=metric_cols, var_name='metric', value_name='value')
sns.boxplot(data=df_long, x='metric', y='value')
plt.yscale('log')
plt.title('Distribution across states (log scale)')
plt.xlabel('Metric')
plt.ylabel('Value (log scale)')
plt.tight_layout()
plt.savefig('output/demographic/state_time/07_boxplot_distribution_across_states.png', dpi=300, bbox_inches='tight')
plt.show()

# 8) Relationship between the two metrics (scatter)
if len(metric_cols) >= 2:
    x_col = metric_cols[0]
    y_col = metric_cols[1]
    plt.figure(figsize=(7,5))
    sns.scatterplot(data=df_month_state, x=x_col, y=y_col, alpha=0.6)
    plt.xscale('log')
    plt.yscale('log')
    plt.title('Relationship between ' + x_col + ' and ' + y_col + ' (log-log)')
    plt.tight_layout()
    plt.savefig('output/demographic/state_time/08_scatter_relationship.png', dpi=300, bbox_inches='tight')
    plt.show()

# 9) State rank stability by month (top 10 states each month)
rank_rows = []
for m_val in sorted(df_month_state['month_dt'].dropna().unique().tolist()):
    temp = df_month_state[df_month_state['month_dt'] == m_val].groupby('state_norm')['total_all_metrics'].sum().sort_values(ascending=False)
    top10 = temp.head(10)
    for rank_idx, (st_val, tot_val) in enumerate(top10.items(), start=1):
        rank_rows.append({'month_dt': m_val, 'state_norm': st_val, 'rank': rank_idx, 'total': tot_val})

df_ranks = pd.DataFrame(rank_rows)
plt.figure(figsize=(10,5))
sns.lineplot(data=df_ranks, x='month_dt', y='rank', hue='state_norm', marker='o', palette='tab10')
plt.gca().invert_yaxis()
plt.title('Top 10 states rank over time (lower is better)')
plt.xlabel('Month')
plt.ylabel('Rank')
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.savefig('output/demographic/state_time/09_state_rank_stability.png', dpi=300, bbox_inches='tight')
plt.show()

# 10) Contribution of top 5 states over time
state_top5 = state_totals.head(5).index.tolist()
df_top5 = df_month_state[df_month_state['state_norm'].isin(state_top5)].groupby(['month_dt','state_norm'])['total_all_metrics'].sum().reset_index()
plt.figure(figsize=(10,5))
sns.lineplot(data=df_top5, x='month_dt', y='total_all_metrics', hue='state_norm', marker='o')
plt.title('Top 5 states - monthly totals')
plt.xlabel('Month')
plt.ylabel('Total')
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.savefig('output/demographic/state_time/10_top_5_states_monthly.png', dpi=300, bbox_inches='tight')
plt.show()

# Summary stats for narrative
state_share_top10 = (state_totals['total_all_metrics'].head(10) / state_totals['total_all_metrics'].sum()).sum()
print(state_share_top10)

# Correlation between metrics
corr_val = df_month_state[metric_cols].corr(numeric_only=True)
print(corr_val)

# Missingness check
missing_counts = df_month_state[metric_cols].isna().sum()
print(missing_counts)

# Save a compact table of top states
state_totals_out = state_totals.reset_index()
state_totals_out.to_csv('output/demographic/state_time/state_totals_summary.csv', index=False)
print(state_totals_out.head(10))