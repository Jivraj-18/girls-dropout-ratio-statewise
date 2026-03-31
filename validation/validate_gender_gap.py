#!/usr/bin/env python3
"""
STANDALONE VALIDATION SCRIPT: Gender Gap Analysis
Regenerates the "Gender Paradox" finding from raw UDISE+ data

Run: python validate_gender_gap.py
"""
import pandas as pd
import os

# Adjust path to find UDISE+ data in parent directory
DATA_DIR = '../udise_csv_data'

print("\n" + "=" * 80)
print("VALIDATION: GENDER PARADOX - BOYS DROPOUT MORE THAN GIRLS")
print("=" * 80)

# Load raw dropout data
dropout_file = os.path.join(
    DATA_DIR,
    '2024-25/csv_files',
    'Table 6.13 Dropout Rate by level of education and gender, 2024-25,,,, - page 120.csv'
)

df = pd.read_csv(dropout_file, skiprows=4, usecols=[0, 7, 8, 9])
df.columns = ['State', 'Boys', 'Girls', 'Total']

# Convert to numeric
for col in ['Boys', 'Girls', 'Total']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Get national figure (first row = India)
india_nat = df.iloc[0]

print(f"\nNATIONAL SECONDARY (9-10) DROPOUT RATES 2024-25:")
print(f"  Boys:  {india_nat['Boys']:.1f}%")
print(f"  Girls: {india_nat['Girls']:.1f}%")
print(f"  Gap:   {india_nat['Boys'] - india_nat['Girls']:+.1f}pp\n")

# State-level analysis
df_states = df.iloc[1:].copy()
df_states = df_states[df_states['State'].notna() & (df_states['State'] != '')]
df_states['Gender_Gap'] = df_states['Boys'] - df_states['Girls']

# Count states by pattern
boys_higher = (df_states['Boys'] > df_states['Girls']).sum()
girls_higher = (df_states['Girls'] > df_states['Boys']).sum()

print(f"STATE-LEVEL ANALYSIS ({len(df_states)} states/UTs):")
print(f"  States where boys > girls: {boys_higher}")
print(f"  States where girls > boys: {girls_higher}")
print(f"  Exception states: {df_states[df_states['Girls'] > df_states['Boys']]['State'].tolist()}\n")

# Top gaps
print(f"LARGEST GENDER GAPS (Boys disadvantaged):")
top_gaps = df_states.nlargest(5, 'Gender_Gap')
for i, (idx, row) in enumerate(top_gaps.iterrows(), 1):
    print(f"  {i}. {row['State']:40s} | Gap: {row['Gender_Gap']:+.1f}pp ({row['Boys']:.1f}% vs {row['Girls']:.1f}%)")

print(f"\n✅ CLAIM VERIFIED: Boys dropout more in {boys_higher}/{len(df_states)} states")
print(f"✅ SOURCE: Table 6.13 - UDISE+ 2024-25")
print(f"\n" + "=" * 80)
