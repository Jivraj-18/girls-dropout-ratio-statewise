#!/usr/bin/env python3
"""
STANDALONE VALIDATION SCRIPT: Promotion/Repetition/Dropout Formula
Verifies that: Promoted + Repeated + Dropout = 100%

Run: python validate_formula.py
"""
import pandas as pd
import os

DATA_DIR = 'udise_csv_data'

print("\n" + "=" * 80)
print("VALIDATION: PROMOTION + REPETITION + DROPOUT = 100%")
print("=" * 80)

# Load data for secondary level (9-10)
promotion_file = os.path.join(
    DATA_DIR,
    '2024-25/csv_files',
    'Table 6.11 Promotion Rate by level of education and gender, 2024-25,,,, - page 118.csv'
)

repetition_file = os.path.join(
    DATA_DIR,
    '2024-25/csv_files',
    'Table 6.12 Repetition Rate by level of education and gender, 2024-25,,, - page 119.csv'
)

dropout_file = os.path.join(
    DATA_DIR,
    '2024-25/csv_files',
    'Table 6.13 Dropout Rate by level of education and gender, 2024-25,,,, - page 120.csv'
)

# Read tables (columns 7, 8, 9 = Boys, Girls, Total for secondary)
prom = pd.read_csv(promotion_file, skiprows=4, usecols=[0, 7, 8]).iloc[0]
rep = pd.read_csv(repetition_file, skiprows=4, usecols=[0, 7, 8]).iloc[0]
drop = pd.read_csv(dropout_file, skiprows=4, usecols=[0, 7, 8]).iloc[0]

# Convert to numeric
prom_boys, prom_girls = float(prom[1]), float(prom[2])
rep_boys, rep_girls = float(rep[1]), float(rep[2])
drop_boys, drop_girls = float(drop[1]), float(drop[2])

print(f"\nNATIONAL SECONDARY (9-10) 2024-25:\n")

# Verify formula
boys_sum = prom_boys + rep_boys + drop_boys
girls_sum = prom_girls + rep_girls + drop_girls

print(f"BOYS:")
print(f"  Promoted:  {prom_boys:6.2f}%")
print(f"  Repeated:  {rep_boys:6.2f}%")
print(f"  Dropout:   {drop_boys:6.2f}%")
print(f"  SUM:       {boys_sum:6.2f}%")

print(f"\nGIRLS:")
print(f"  Promoted:  {prom_girls:6.2f}%")
print(f"  Repeated:  {rep_girls:6.2f}%")
print(f"  Dropout:   {drop_girls:6.2f}%")
print(f"  SUM:       {girls_sum:6.2f}%")

# Check
boys_valid = abs(boys_sum - 100) < 0.2
girls_valid = abs(girls_sum - 100) < 0.2

print(f"\nVERIFICATION:")
if boys_valid:
    print(f"  ✅ BOYS: Sums to {boys_sum:.2f}% (within tolerance)")
else:
    print(f"  ❌ BOYS: Sums to {boys_sum:.2f}% (DEVIATION: {100 - boys_sum:.2f}%)")

if girls_valid:
    print(f"  ✅ GIRLS: Sums to {girls_sum:.2f}% (within tolerance)")
else:
    print(f"  ❌ GIRLS: Sums to {girls_sum:.2f}% (DEVIATION: {100 - girls_sum:.2f}%)")

# Key insight
print(f"\nKEY INSIGHT:")
print(f"  Boys dropout {drop_boys - drop_girls:+.2f}pp more because:")
print(f"    → Lower promotion: {prom_boys - prom_girls:+.2f}pp worse")
print(f"    → Higher repetition: {rep_boys - rep_girls:+.2f}pp worse")
print(f"    → Combined effect: {(prom_boys - prom_girls) + (rep_boys - rep_girls):+.2f}pp → {drop_boys - drop_girls:+.2f}pp dropout gap")

print(f"\n✅ SOURCE: Tables 6.11, 6.12, 6.13 - UDISE+ 2024-25")
print(f"=" * 80 + "\n")
