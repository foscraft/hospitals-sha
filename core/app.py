import os
import streamlit as st
from streamlit_folium import st_folium
import duckdb
from data_loader import load_data
from map_utils import get_type_color_map, create_facility_map, add_legend
from stats_utils import show_statistics, plot_charts

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(page_title="Health Facilities in Kenya", layout="wide", page_icon=os.path.join(BASE_DIR, '..', 'images', 'favicon.ico'),)
st.title("Health Facilities in Kenya")
st.markdown("This app visualizes health facility locations and provides statistical analysis. Zoom in/out on the map and explore the stats below.")

#@st.cache_data(show_spinner="Preparing DuckDB...")
def get_duckdb_connection(df):
    con = duckdb.connect(database=':memory:')
    con.register('facilities', df)
    return con

def get_filter_options(con):
    counties = con.execute("SELECT DISTINCT County FROM facilities ORDER BY County").fetchdf()['County'].dropna().tolist()
    return ['All'] + counties

def get_constituency_options(con, selected_county):
    if selected_county != 'All':
        query = "SELECT DISTINCT Constituen FROM facilities WHERE County = ? ORDER BY Constituen"
        params = (selected_county,)
    else:
        query = "SELECT DISTINCT Constituen FROM facilities ORDER BY Constituen"
        params = ()
    constituencies = con.execute(query, params).fetchdf()['Constituen'].dropna().tolist()
    return ['All'] + constituencies

def filter_facilities(con, county, constituency):
    query = "SELECT * FROM facilities"
    conditions = []
    params = []
    if county != 'All':
        conditions.append("County = ?")
        params.append(county)
    if constituency != 'All':
        conditions.append("Constituen = ?")
        params.append(constituency)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    return con.execute(query, params).fetchdf()

def main():
    try:
        df = load_data()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

    con = get_duckdb_connection(df)
    facility_types = df['Type'].unique()
    type_color_map = get_type_color_map(facility_types)

    # --- Filter Section ---
    st.subheader("Filter Facilities by County and Constituency")
    col_county, col_const = st.columns(2)

    with col_county:
        county_options = get_filter_options(con)
        selected_county = st.selectbox("Select a County", options=county_options)

    with col_const:
        constituency_options = get_constituency_options(con, selected_county)
        selected_constituency = st.selectbox("Select a Constituency", options=constituency_options)

    # --- Filtering with DuckDB ---
    filtered_df = filter_facilities(con, selected_county, selected_constituency)

    # --- Map Section (filtered) ---
    m = create_facility_map(df, type_color_map, county=selected_county, constituency=selected_constituency)
    add_legend(m, type_color_map)
    st.subheader("Map of Health Facilities")
    st_folium(m, width=2200, height=1200)

    # --- Statistics Section (filtered) ---
    st.subheader("Statistical Analysis")
    plot_charts(filtered_df)
    show_statistics(filtered_df)

    # --- Data Table Section ---
    st.markdown(
        f"### Facilities in "
        f"{selected_county if selected_county != 'All' else 'All Counties'}"
        f"{' / ' + selected_constituency if selected_constituency != 'All' else ''}"
    )
    st.dataframe(filtered_df[['Facility_N', 'Type', 'Owner', 'Sub_County', 'Constituen', 'Nearest_To', 'Latitude', 'Longitude']])

    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name=f"facilities_{selected_county if selected_county != 'All' else 'all'}_{selected_constituency if selected_constituency != 'All' else 'all'}.csv",
        mime="text/csv",
    )

    st.markdown("---")
    st.markdown("Developed by: [foscraft](https://github.com/foscraft).")
    st.markdown("Talk to me  [here](https://wa.link/6uwu0u)")
    st.markdown("Data Source: [Energy Open Data](https://energydata.info/dataset/kenya-healthcare-facilities).")

if __name__ == "__main__":
    main()