import os
import streamlit as st
import streamlit.components.v1 as components

from database_engine import get_connection
from map_utils import get_type_color_map, create_facility_map
from stats_utils import show_statistics, plot_charts

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="Health Facilities in Kenya",
    layout="wide",
    page_icon=os.path.join(BASE_DIR, '..', 'images', 'favicon.ico'),
)

st.title("🏥 Health Facilities in Kenya")
st.markdown("This app visualizes health facility locations and provides statistical analysis.")

# --- Cached DB Connection --- #
@st.cache_resource(show_spinner=False)
def get_conn():
    return get_connection()

def sql_to_df(sql: str, params: tuple = ()):
    conn = get_conn()
    return conn.execute(sql, params).fetch_df()

# --- Cache the full facilities DataFrame for fast filtering --- #
@st.cache_data(show_spinner=False)
def get_facilities_df():
    sql = """
        SELECT Facility_N, Type, Owner, Sub_County, Constituen, Nearest_To, Latitude, Longitude, County
        FROM facilities
    """
    return sql_to_df(sql)

# ---------------- Query Helpers ---------------- #
@st.cache_data(show_spinner=False)
def get_distinct_counties(df=None):
    if df is None:
        df = get_facilities_df()
    counties = sorted(df['County'].dropna().unique())
    return ["All"] + counties

@st.cache_data(show_spinner=False)
def get_distinct_constituencies(df, county: str):
    if county != "All":
        df = df[df['County'] == county]
    constituencies = sorted(df['Constituen'].dropna().unique())
    return ["All"] + constituencies

def get_filtered_df(df, county: str, constituency: str):
    if county != "All":
        df = df[df['County'] == county]
    if constituency != "All":
        df = df[df['Constituen'] == constituency]
    return df

def get_metrics(df):
    total = len(df)
    n_counties = df['County'].nunique()
    n_const = df['Constituen'].nunique()
    return total, n_counties, n_const

@st.cache_data(show_spinner=False)
def get_distinct_types(df=None):
    if df is None:
        df = get_facilities_df()
    return sorted(df['Type'].dropna().unique())

@st.cache_resource(show_spinner=False)
def get_type_color_map_cached(types_tuple):
    return get_type_color_map(list(types_tuple))

# ---------------- Main App ---------------- #
def main():
    # Preload the full facilities DataFrame once
    facilities_df = get_facilities_df()

    st.subheader("🔍 Filter Facilities")
    col_county, col_const = st.columns([1, 1])

    county_options = get_distinct_counties(facilities_df)
    with col_county:
        selected_county = st.selectbox("Select County", options=county_options)

    constituency_options = get_distinct_constituencies(facilities_df, selected_county)
    with col_const:
        selected_constituency = st.selectbox("Select Constituency", options=constituency_options)

    # --- Filtered Slice ---
    filtered_df = get_filtered_df(facilities_df, selected_county, selected_constituency)

    st.subheader("📊 Summary Stats")
    total, n_counties, n_const = get_metrics(filtered_df)
    c1, c2 = st.columns(2)
    c1.metric("Total Facilities", f"{total:,}")
    c2.metric("Counties", n_counties)
    #c3.metric("Constituencies", n_const)

    # --- Facility Types & Colors ---
    types = get_distinct_types(facilities_df)
    type_color_map = get_type_color_map_cached(tuple(types))

    # --- Map Section ---
    st.subheader("🗺️ Map of Health Facilities")
    with st.spinner("Rendering map..."):
        html_content = create_facility_map(filtered_df, type_color_map,
                                          county=selected_county, constituency=selected_constituency)
        components.html(html_content, height=700)

    # --- Stats & Charts ---
    st.subheader("📈 Detailed Analysis")
    with st.spinner("Generating charts..."):
        plot_charts(filtered_df)
        show_statistics(filtered_df)

    # --- Data Table + Download ---
    label_loc = f"{selected_county}" + (f" / {selected_constituency}" if selected_constituency != "All" else "")
    st.markdown(f"### 📋 Facilities in {label_loc or 'All'}")

    st.dataframe(filtered_df, use_container_width=True)

    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=csv,
        file_name=f"facilities_{selected_county}_{selected_constituency}.csv".replace("All", "all"),
        mime="text/csv",
    )

    # --- Footer ---
    st.markdown("---")
    st.markdown("Developed by: [foscraft](https://github.com/foscraft) 🚀")
    st.markdown("💬 Talk to me [here](https://wa.link/6uwu0u)")
    st.markdown("📂 Data Source: [Energy Open Data](https://energydata.info/dataset/kenya-healthcare-facilities).")

if __name__ == "__main__":
    main()