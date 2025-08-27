import os
import duckdb
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource(show_spinner=False)
def get_connection():
    """
    Create an in-memory DuckDB connection,
    load facilities table from Parquet once,
    and return a cached connection.
    """
    conn = duckdb.connect(database=':memory:')

    parquet_path = os.path.join(BASE_DIR, '..', 'data', 'healthcare_facilities.parquet')

    conn.execute(f"""
        CREATE OR REPLACE TABLE facilities AS
        SELECT *
        FROM read_parquet('{parquet_path}')
    """)

    conn.execute("ANALYZE facilities")  # collect stats for optimization
    return conn
