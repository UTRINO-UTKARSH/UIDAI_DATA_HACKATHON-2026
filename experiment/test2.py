import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the datasets
file1 = 'data/raw/aadhar-enrollment-complete-dataset/api_data_aadhar_enrolment_0_500000.csv'
file2 = 'data/raw/aadhar-enrollment-complete-dataset/api_data_aadhar_enrolment_500000_1000000.csv'
file3 = 'data/raw/aadhar-enrollment-complete-dataset/api_data_aadhar_enrolment_1000000_1006029.csv'

df1 = pd.read_csv(file1)
df2 = pd.read_csv(file2)
df3 = pd.read_csv(file3)

# Merge datasets
df = pd.concat([df1, df2, df3], ignore_index=True)

# Inspect the merged dataframe
print(df.head())
print(df.info())
# Convert date to datetime
df['date'] = pd.to_datetime(df['date'], dayfirst=True)

# Create 'Month' column (Month Name + Year)
df['Month'] = df['date'].dt.strftime('%B %Y')

# Fill missing numeric values with 0
numeric_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
df[numeric_cols] = df[numeric_cols].fillna(0)

# Total enrollment for each row
df['total_enrollment'] = df[numeric_cols].sum(axis=1)

# Grouping and aggregating
# Month (first priority), State (second priority), District (third priority)
aggregated_df = df.groupby(['Month', 'state', 'district']).agg({
    'age_0_5': 'sum',
    'age_5_17': 'sum',
    'age_18_greater': 'sum',
    'total_enrollment': 'sum'
}).reset_index()

# Sort by Month name (logic needed to sort chronologically, not alphabetically)
# We can create a temporary date column for sorting
aggregated_df['date_temp'] = pd.to_datetime(aggregated_df['Month'], format='%B %Y')
aggregated_df = aggregated_df.sort_values(by=['date_temp', 'state', 'district'])
aggregated_df = aggregated_df.drop(columns=['date_temp'])

# Reordering columns as requested
aggregated_df = aggregated_df[['Month', 'state', 'district', 'age_0_5', 'age_5_17', 'age_18_greater']]

# Save the final aggregated dataset
aggregated_df.to_csv('aggregated_aadhar_enrolment.csv', index=False)

print(aggregated_df.head())
print(aggregated_df.info())

# Analysis 1: Month-wise total enrollment trends
month_trends = aggregated_df.groupby('Month').agg({
    'age_0_5': 'sum',
    'age_5_17': 'sum',
    'age_18_greater': 'sum',
    'total_enrollment': 'sum'
}).reset_index()

# Chronological sorting for trends
month_trends['date_temp'] = pd.to_datetime(month_trends['Month'], format='%B %Y')
month_trends = month_trends.sort_values('date_temp')

# Visualization: Month-wise Trend
plt.figure(figsize=(12, 6))
plt.plot(month_trends['Month'], month_trends['total_enrollment'], marker='o', label='Total Enrollment', color='black', linewidth=2)
plt.bar(month_trends['Month'], month_trends['age_0_5'], label='0-5 Years', alpha=0.5)
plt.bar(month_trends['Month'], month_trends['age_5_17'], bottom=month_trends['age_0_5'], label='5-17 Years', alpha=0.5)
plt.bar(month_trends['Month'], month_trends['age_18_greater'], bottom=month_trends['age_0_5'] + month_trends['age_5_17'], label='18+ Years', alpha=0.5)
plt.title('Monthly Aadhaar Enrollment Trends by Age Group')
plt.xlabel('Month')
plt.ylabel('Enrollment Count')
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig('monthly_trends.png')

# Analysis 2: State-wise comparison (Total Enrollment)
state_comparison = aggregated_df.groupby('state')['total_enrollment'].sum().reset_index().sort_values(by='total_enrollment', ascending=False)

# Visualization: Top 15 States
plt.figure(figsize=(12, 8))
sns.barplot(data=state_comparison.head(15), x='total_enrollment', y='state', palette='viridis')
plt.title('Top 15 States by Total Aadhaar Enrollment')
plt.xlabel('Total Enrollment')
plt.ylabel('State')
plt.tight_layout()
plt.savefig('state_comparison.png')

# Analysis 3: Anomalies - Month-on-Month Growth Rate
month_trends['growth_rate'] = month_trends['total_enrollment'].pct_change() * 100

# Anomalies - High volume Districts
district_anomalies = aggregated_df.sort_values(by='total_enrollment', ascending=False).head(10)

# Output insights
print("Month-wise Growth Rates:")
print(month_trends[['Month', 'total_enrollment', 'growth_rate']])

print("\nTop 10 Districts by Enrollment (Possible Spikes/High Demand Zones):")
print(district_anomalies[['Month', 'state', 'district', 'total_enrollment']])

# Identify any sharp drops or spikes in the month trends
sharp_changes = month_trends[abs(month_trends['growth_rate']) > 50] # Arbitrary threshold for "sharp" change
print("\nMonths with Sharp Changes (>50%):")
print(sharp_changes[['Month', 'growth_rate']])