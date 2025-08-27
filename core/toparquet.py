import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, '..', 'data', 'healthcare_facilities.csv')
parquet_path = os.path.join(BASE_DIR, '..', 'data', 'healthcare_facilities.parquet')

df = pd.read_csv(csv_path, encoding='ISO-8859-1')

# Replace empty strings and whitespace-only strings with pd.NA
df = df.applymap(lambda x: pd.NA if isinstance(x, str) and x.strip() == "" else x)

# Optionally, also replace all missing values (NaN) with pd.NA for consistency
df = df.where(pd.notnull(df), pd.NA)

df.to_parquet(parquet_path, engine="pyarrow", index=False)  # or engine="fastparquet"
print("Converted to Parquet:", parquet_path)