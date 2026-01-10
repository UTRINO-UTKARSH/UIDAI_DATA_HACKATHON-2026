import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

mpl.rcParams['figure.dpi'] = 200
mpl.rcParams['savefig.dpi'] = 200
mpl.rcParams['savefig.bbox'] = 'tight'

# Load and prepare data
df_original = pd.read_csv('data/cleaned-dataset/aadhar_enrollment_final_aggregated.csv')
df_original['date'] = pd.to_datetime(df_original['date'])

# Aggregate by date
df_time_series = df_original.groupby('date')[['age_0_5', 'age_5_17', 'age_18_greater']].sum().reset_index()
df_time_series = df_time_series.sort_values('date')

# Calculate total enrollments and percentages
df_time_series['total'] = df_time_series['age_0_5'] + df_time_series['age_5_17'] + df_time_series['age_18_greater']
df_time_series['pct_0_5'] = (df_time_series['age_0_5'] / df_time_series['total'] * 100)
df_time_series['pct_5_17'] = (df_time_series['age_5_17'] / df_time_series['total'] * 100)
df_time_series['pct_18_greater'] = (df_time_series['age_18_greater'] / df_time_series['total'] * 100)

# ===== CHART 1: Line trends for absolute enrollments =====
fig, ax = plt.subplots(figsize=(12, 7), dpi=200)

ax.plot(df_time_series['date'], df_time_series['age_0_5'], marker='o', linewidth=2.5, 
        label='Age 0-5', color='#FF6B6B', markersize=6)
ax.plot(df_time_series['date'], df_time_series['age_5_17'], marker='s', linewidth=2.5, 
        label='Age 5-17', color='#4ECDC4', markersize=6)
ax.plot(df_time_series['date'], df_time_series['age_18_greater'], marker='^', linewidth=2.5, 
        label='Age 18+', color='#45B7D1', markersize=6)

ax.set_xlabel('Date', fontsize=12, fontweight='bold')
ax.set_ylabel('Aadhaar Enrollments', fontsize=12, fontweight='bold')
ax.set_title('Aadhaar Enrollment Trends by Age Group Over Time', fontsize=14, fontweight='bold', pad=20)
ax.legend(loc='best', fontsize=11, framealpha=0.95)
ax.grid(True, linestyle='--', alpha=0.3)
ax.tick_params(axis='x', rotation=45)
plt.tight_layout()
plt.savefig('/home/user/workspace/outputs/01_enrollment_trends_absolute_20260109_1.png', dpi=200, bbox_inches='tight')
plt.close()

print("✓ Chart 1: Absolute enrollment trends saved")

# ===== CHART 2: Stacked Area Chart =====
fig, ax = plt.subplots(figsize=(12, 7), dpi=200)

ax.stackplot(df_time_series['date'], 
             df_time_series['age_0_5'],
             df_time_series['age_5_17'],
             df_time_series['age_18_greater'],
             labels=['Age 0-5', 'Age 5-17', 'Age 18+'],
             colors=['#FF6B6B', '#4ECDC4', '#45B7D1'],
             alpha=0.8)

ax.set_xlabel('Date', fontsize=12, fontweight='bold')
ax.set_ylabel('Aadhaar Enrollments', fontsize=12, fontweight='bold')
ax.set_title('Cumulative Aadhaar Enrollment by Age Group Over Time', fontsize=14, fontweight='bold', pad=20)
ax.legend(loc='upper left', fontsize=11, framealpha=0.95)
ax.grid(True, linestyle='--', alpha=0.3, axis='y')
ax.tick_params(axis='x', rotation=45)
plt.tight_layout()
plt.savefig('/home/user/workspace/outputs/02_enrollment_trends_stacked_20260109_1.png', dpi=200, bbox_inches='tight')
plt.close()

print("✓ Chart 2: Stacked area chart saved")

# ===== CHART 3: Percentage Distribution Over Time =====
fig, ax = plt.subplots(figsize=(12, 7), dpi=200)

ax.plot(df_time_series['date'], df_time_series['pct_0_5'], marker='o', linewidth=2.5, 
        label='Age 0-5 (%)', color='#FF6B6B', markersize=6)
ax.plot(df_time_series['date'], df_time_series['pct_5_17'], marker='s', linewidth=2.5, 
        label='Age 5-17 (%)', color='#4ECDC4', markersize=6)
ax.plot(df_time_series['date'], df_time_series['pct_18_greater'], marker='^', linewidth=2.5, 
        label='Age 18+ (%)', color='#45B7D1', markersize=6)

ax.set_xlabel('Date', fontsize=12, fontweight='bold')
ax.set_ylabel('Percentage of Total Enrollments (%)', fontsize=12, fontweight='bold')
ax.set_title('Age Group Distribution as Percentage of Total Enrollments', fontsize=14, fontweight='bold', pad=20)
ax.legend(loc='best', fontsize=11, framealpha=0.95)
ax.grid(True, linestyle='--', alpha=0.3)
ax.tick_params(axis='x', rotation=45)
ax.set_ylim(0, 100)
plt.tight_layout()
plt.savefig('/home/user/workspace/outputs/03_age_distribution_percentage_20260109_1.png', dpi=200, bbox_inches='tight')
plt.close()

print("✓ Chart 3: Percentage distribution chart saved")

# ===== CHART 4: Bar chart showing average enrollments =====
avg_enrollments = {
    'Age 0-5': df_time_series['age_0_5'].mean(),
    'Age 5-17': df_time_series['age_5_17'].mean(),
    'Age 18+': df_time_series['age_18_greater'].mean()
}

fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
bars = ax.bar(avg_enrollments.keys(), avg_enrollments.values(), 
              color=['#FF6B6B', '#4ECDC4', '#45B7D1'], alpha=0.8, edgecolor='black', linewidth=1.5)

ax.set_ylabel('Average Daily Enrollments', fontsize=12, fontweight='bold')
ax.set_title('Average Aadhaar Enrollments by Age Group', fontsize=14, fontweight='bold', pad=20)
ax.grid(True, linestyle='--', alpha=0.3, axis='y')

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('/home/user/workspace/outputs/04_average_enrollments_by_age_20260109_1.png', dpi=200, bbox_inches='tight')
plt.close()

print("✓ Chart 4: Average enrollments bar chart saved")

# ===== CHART 5: Heatmap of daily enrollments =====
# Reshape data for heatmap
df_pivot = df_time_series[['date', 'age_0_5', 'age_5_17', 'age_18_greater']].set_index('date')
df_pivot.columns = ['Age 0-5', 'Age 5-17', 'Age 18+']

fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
sns.heatmap(df_pivot.T, cmap='YlOrRd', cbar_kws={'label': 'Enrollments'}, ax=ax, linewidths=0.5)
ax.set_xlabel('Date', fontsize=12, fontweight='bold')
ax.set_ylabel('Age Group', fontsize=12, fontweight='bold')
ax.set_title('Daily Aadhaar Enrollment Heatmap by Age Group', fontsize=14, fontweight='bold', pad=20)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('/home/user/workspace/outputs/05_enrollment_heatmap_20260109_1.png', dpi=200, bbox_inches='tight')
plt.close()

print("✓ Chart 5: Enrollment heatmap saved")

# Print summary statistics
print("\n" + "="*70)
print("SUMMARY STATISTICS: AGE GROUP ENROLLMENT TRENDS")
print("="*70)
print(f"\nDate Range: {df_time_series['date'].min().date()} to {df_time_series['date'].max().date()}")
print(f"Total Days with Data: {len(df_time_series)} days")
print(f"\nTotal Enrollments by Age Group:")
print(f"  • Age 0-5:     {df_time_series['age_0_5'].sum():>12,} ({df_time_series['age_0_5'].sum()/df_time_series['total'].sum()*100:.1f}%)")
print(f"  • Age 5-17:    {df_time_series['age_5_17'].sum():>12,} ({df_time_series['age_5_17'].sum()/df_time_series['total'].sum()*100:.1f}%)")
print(f"  • Age 18+:     {df_time_series['age_18_greater'].sum():>12,} ({df_time_series['age_18_greater'].sum()/df_time_series['total'].sum()*100:.1f}%)")
print(f"  ─────────────────────────────────────────")
print(f"  • TOTAL:       {df_time_series['total'].sum():>12,} enrollments")

print(f"\nDaily Average Enrollments:")
print(f"  • Age 0-5:     {df_time_series['age_0_5'].mean():>12,.0f}")
print(f"  • Age 5-17:    {df_time_series['age_5_17'].mean():>12,.0f}")
print(f"  • Age 18+:     {df_time_series['age_18_greater'].mean():>12,.0f}")

print(f"\nDaily Peak Enrollments:")
print(f"  • Age 0-5:     {df_time_series['age_0_5'].max():>12,} on {df_time_series.loc[df_time_series['age_0_5'].idxmax(), 'date'].date()}")
print(f"  • Age 5-17:    {df_time_series['age_5_17'].max():>12,} on {df_time_series.loc[df_time_series['age_5_17'].idxmax(), 'date'].date()}")
print(f"  • Age 18+:     {df_time_series['age_18_greater'].max():>12,} on {df_time_series.loc[df_time_series['age_18_greater'].idxmax(), 'date'].date()}")

print("\n" + "="*70)