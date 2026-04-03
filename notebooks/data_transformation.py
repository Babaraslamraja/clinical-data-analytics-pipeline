from pathlib import Path
import pandas as pd

# Get folder where the script is (notebooks/)
script_dir = Path(__file__).parent.resolve()

# Correct path from notebooks/ → CLINICAL_MODELING/ → data/raw/
data_path = script_dir.parent / "data" / "raw" / "source_data.csv"

print("=== DEBUG ===")
print("Script folder :", script_dir)
print("Trying path   :", data_path)
print("File exists?  :", data_path.exists())

# Load the file
df = pd.read_csv(data_path)
# Check duplicate rows
duplicate_count = df.duplicated().sum()
print("Duplicate rows:", duplicate_count)
print("\n SUCCESS! First 5 rows of data:")
print(df.head())
print(df.info())
print(df.describe())
print(df.isnull().sum())
print(df['gender'].value_counts())
df['birth_date'] = pd.to_datetime(df['birth_date'], dayfirst=True)
df['age'] = (pd.Timestamp.today() - df['birth_date']).dt.days // 365
print(df[['patient_id', 'birth_date', 'age']].head())
# Create processed path properly
processed_path = script_dir.parent / "data" / "processed" / "cleaned_data.csv"

# Save file
df.to_csv(processed_path, index=False)

print("Saved to:", processed_path)
# Check data types
print(df.dtypes)
# Convert encounter_date to datetime
df['encounter_date'] = pd.to_datetime(df['encounter_date'], errors='coerce')
print("Missing encounter_date:", df['encounter_date'].isna().sum())

df = df.dropna(subset=['encounter_date'])

print("After drop:", df['encounter_date'].isna().sum())

# Line 42 (your existing line)
print(df['encounter_date'].dtype)
# Verify
print(df['encounter_date'].dtype)
# Extract time features
df['encounter_year'] = df['encounter_date'].dt.year
df['encounter_month'] = df['encounter_date'].dt.month
df['encounter_day'] = df['encounter_date'].dt.day

# Verify
print(df[['encounter_date', 'encounter_year', 'encounter_month']].head())
# Check obs_value issues
print("Missing obs_value:", df['obs_value'].isna().sum())
print("Zero values:", (df['obs_value'] == 0).sum())
print("Negative values:", (df['obs_value'] < 0).sum())
# Create age groups
df['age_group'] = pd.cut(
    df['age'],
    bins=[0, 18, 30, 45, 60, 100],
    labels=['0-18', '19-30', '31-45', '46-60', '60+']
)

# Verify
print(df[['age', 'age_group']].head())
# Check categorical distributions
print("Encounter Type:\n", df['encounter_type'].value_counts())
print("\nCondition:\n", df['condition'].value_counts())
print("\nMedication:\n", df['medication'].value_counts())
# Aggregate: average obs_value by condition
condition_summary = (
    df.groupby('condition')['obs_value']
    .mean()
    .reset_index()
    .sort_values(by='obs_value', ascending=False)
)

print(condition_summary.head())
import matplotlib.pyplot as plt

# Bar chart
plt.figure()

plt.bar(condition_summary['condition'], condition_summary['obs_value'])

plt.xlabel("Condition")
plt.ylabel("Average Observation Value")
plt.title("Average Observation Value by Condition")

plt.xticks(rotation=45)

plt.tight_layout()
# 👉 ADD THIS LINE (save image)
plot_path = script_dir.parent / "data" / "visuals" / "condition_bar_chart.png"
plt.savefig(plot_path)

plt.show()

# 👉 ADD HERE (line chart)

monthly_trend = (
    df.groupby(['encounter_year', 'encounter_month'])['obs_value']
    .mean()
    .reset_index()
    .sort_values(['encounter_year', 'encounter_month'])
)

print(monthly_trend.head())
# Save monthly trend
trend_path = script_dir.parent / "data" / "processed" / "monthly_trend.csv"
# Create proper timeline column
monthly_trend['year_month'] = (
    monthly_trend['encounter_year'].astype(int).astype(str) + "-" +
    monthly_trend['encounter_month'].astype(int).astype(str)
)
monthly_trend.to_csv(trend_path, index=False)
plt.figure()

plt.plot(monthly_trend['year_month'], monthly_trend['obs_value'], marker='o')

plt.xlabel("Year-Month")
plt.ylabel("Average Observation Value")
plt.title("Monthly Trend of Observation Value")

plt.xticks(rotation=45)

plt.tight_layout()

plot_path = script_dir.parent / "data" / "visuals"/ "monthly_trend_chart.png"
plt.savefig(plot_path)

plt.show()

# Save aggregated dataset
summary_path = script_dir.parent / "data" / "processed" / "condition_summary.csv"

condition_summary.to_csv(summary_path, index=False)

print("Summary saved to:", summary_path)
# Aggregate by month

print("Monthly trend saved to:", trend_path)
# Select final columns
final_df = df[[
    'patient_id',
    'gender',
    'age',
    'age_group',
    'encounter_date',
    'encounter_year',
    'encounter_month',
    'encounter_type',
    'observation',
    'obs_value',
    'condition',
    'medication'
]]

# Save final dataset
final_path = script_dir.parent / "data" / "processed" / "final_dataset.csv"

final_df.to_csv(final_path, index=False)

print("Final dataset saved to:", final_path)
print("\n=== DATA SUMMARY ===")

print("Total records:", len(df))
print("Unique patients:", df['patient_id'].nunique())

print("\nTop Conditions:")
print(df['condition'].value_counts().head())

print("\nTop Medications:")
print(df['medication'].value_counts().head())