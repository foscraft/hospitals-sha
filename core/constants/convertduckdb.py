import duckdb
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, '..', 'data', 'healthcare_facilities.csv')
duckdb_path = os.path.join(BASE_DIR, '..', 'data', 'healthcare_facilities.duckdb')

# Load CSV and write to DuckDB
df = pd.read_csv(csv_path, encoding='ISO-8859-1')
conn = duckdb.connect(duckdb_path)
conn.register("df", df)
conn.execute("CREATE OR REPLACE TABLE facilities AS SELECT * FROM df")
conn.close()
print("Saved to DuckDB:", duckdb_path)
