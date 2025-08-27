import os
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data(show_spinner="Loading data...")
def load_data():
    df = pd.read_csv(
        os.path.join(BASE_DIR, '..', 'data', 'healthcare_facilities.csv'),
        encoding='ISO-8859-1'
    )
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df = df.dropna(subset=['Latitude', 'Longitude'])
    return df