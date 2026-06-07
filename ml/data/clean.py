# ml/data/clean.py
# Purpose: Clean the raw malaria dataset and prepare it for ML
# This script runs AFTER explore.py

import pandas as pd
import numpy as np
import os

print("Starting data cleaning...")

# ── 1. LOAD RAW DATA ──────────────────────────────────────────────
df = pd.read_csv("data/raw/DatasetAfricaMalaria.csv")
print(f"Raw data: {df.shape[0]} rows, {df.shape[1]} columns")

# ── 2. DROP COLUMNS WITH MORE THAN 50% MISSING ────────────────────
# Calculate percentage of missing values per column
missing_pct = df.isnull().mean()

# Keep only columns where less than 50% of values are missing
cols_to_keep = missing_pct[missing_pct < 0.5].index.tolist()
df = df[cols_to_keep]
print(f"After dropping sparse columns: {df.shape[1]} columns remain")
print("Remaining columns:", list(df.columns))

# ── 3. DROP ROWS WHERE TARGET VARIABLE IS MISSING ─────────────────
# Our target is "Incidence of malaria (per 1,000 population at risk)"
# We cannot train or evaluate on rows where we don't know the answer

TARGET_COL = "Incidence of malaria (per 1,000 population at risk)"

# Check if the column exists after our filtering
if TARGET_COL not in df.columns:
    print(f"ERROR: Target column not found!")
    print("Available columns:", list(df.columns))
    exit()

# Drop rows where target is missing
before = len(df)
df = df.dropna(subset=[TARGET_COL])
after = len(df)
print(f"Removed {before - after} rows with missing target value")
print(f"Remaining rows: {after}")

# ── 4. RENAME COLUMNS TO SIMPLER NAMES ────────────────────────────
# Long column names are hard to work with in code
df = df.rename(columns={
    "Country Name": "country",
    "Year": "year",
    "Country Code": "country_code",
    "Incidence of malaria (per 1,000 population at risk)": "malaria_incidence",
    "Malaria cases reported": "malaria_cases",
})

print("\nRenamed columns:", list(df.columns))

# ── 5. CREATE RISK CATEGORY (OUR PREDICTION TARGET) ───────────────
# We turn the continuous incidence number into 3 risk levels
# This makes it a classification problem (easier to start with)
#
# Thresholds based on WHO malaria burden categories:
# Low:    < 100 cases per 1,000 people
# Medium: 100–300 cases per 1,000 people  
# High:   > 300 cases per 1,000 people

def assign_risk(incidence):
    if incidence < 100:
        return "Low"
    elif incidence < 300:
        return "Medium"
    else:
        return "High"

df["risk_level"] = df["malaria_incidence"].apply(assign_risk)

# Show the distribution of risk levels
print("\nRisk level distribution:")
print(df["risk_level"].value_counts())

# ── 6. FILL REMAINING MISSING VALUES ──────────────────────────────
# For any numeric columns still having missing values,
# fill with the median (middle value) — more robust than mean

numeric_cols = df.select_dtypes(include=[np.number]).columns
for col in numeric_cols:
    missing = df[col].isnull().sum()
    if missing > 0:
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)
        print(f"Filled {missing} missing values in '{col}' with median {median_val:.2f}")

# ── 7. SAVE CLEANED DATA ──────────────────────────────────────────
os.makedirs("data/processed", exist_ok=True)
output_path = "data/processed/malaria_clean.csv"
df.to_csv(output_path, index=False)

print(f"\n✓ Cleaned data saved to {output_path}")
print(f"✓ Final shape: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"✓ Columns: {list(df.columns)}")
print("\nSample of cleaned data:")
print(df.head(3))