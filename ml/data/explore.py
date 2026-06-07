import pandas as pd
import os

DATA_PATH = "data/raw/DatasetAfricaMalaria.csv"

if not os.path.exists(DATA_PATH):
    print(f"ERROR: File not found at {DATA_PATH}")
    exit()

df = pd.read_csv(DATA_PATH)

print("=" * 50)
print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
print("=" * 50)
print("\nCOLUMNS:")
for col in df.columns:
    print(f"  - {col}")
print("\nFIRST 5 ROWS:")
print(df.head())
print("\nMISSING VALUES:")
print(df.isnull().sum())