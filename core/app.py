import os
import streamlit as st
from streamlit_folium import st_folium
from data_loader import load_data
from map_utils import get_type_color_map, create_facility_map, add_legend
from stats_utils import show_statistics, plot_charts

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="Health Facilities in Kenya",
    layout="wide",
    page_icon=os.path.join(BASE_DIR, '..', 'images', 'favicon.ico'),
)
st.title("Health Facilities in Kenya")
st.markdown("This app visualizes health facility locations and provides statistical analysis.")

@st.cache_data(show_spinner=False)
def get_filter_options(df):
    counties = sorted(df['County'].dropna().unique().tolist())
    return ['All'] + counties

@st.cache_data(show_spinner=False)
def get_constituency_options(df, selected_county):
    if selected_county != 'All':
        constituencies = sorted(df.loc[df['County'] == selected_county, 'Constituen'].dropna().unique().tolist())
    else:
        constituencies = sorted(df['Constituen'].dropna().unique().tolist())
    return ['All'] + constituencies

@st.cache_data(show_spinner=False)
def filter_facilities(df, county, constituency):
    filtered = df
    if county != 'All':
        filtered = filtered[filtered['County'] == county]
    if constituency != 'All':
        filtered = filtered[filtered['Constituen'] == constituency]
    return filtered

@st.cache_resource(show_spinner=False)
def get_map(df, type_color_map, county, constituency):
    m = create_facility_map(df, type_color_map, county=county, constituency=constituency)
    add_legend(m, type_color_map)
    return m

def main():
    df = load_data()
    facility_types = df['Type'].unique()
    type_color_map = get_type_color_map(facility_types)

    # --- Filter Section ---
    st.subheader("Filter Facilities by County and Constituency")
    col_county, col_const = st.columns(2)

    county_options = get_filter_options(df)
    with col_county:
        selected_county = st.selectbox("Select a County", options=county_options)

    constituency_options = get_constituency_options(df, selected_county)
    with col_const:
        selected_constituency = st.selectbox("Select a Constituency", options=constituency_options)

    # --- Filtered Data ---
    filtered_df = filter_facilities(df, selected_county, selected_constituency)

    # --- Map Section ---
    st.subheader("Map of Health Facilities")
    m = get_map(df, type_color_map, selected_county, selected_constituency)
    st_folium(m, width=2200, height=1200)

    # --- Stats Section ---
    st.subheader("Statistical Analysis")
    plot_charts(filtered_df)
    show_statistics(filtered_df)

    # --- Data Table ---
    st.markdown(f"### Facilities in {selected_county} {'/ ' + selected_constituency if selected_constituency != 'All' else ''}")
    st.dataframe(filtered_df[['Facility_N', 'Type', 'Owner', 'Sub_County', 'Constituen', 'Nearest_To', 'Latitude', 'Longitude']])

    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name=f"facilities_{selected_county}_{selected_constituency}.csv".replace("All", "all"),
        mime="text/csv",
    )

    st.markdown("---")
    st.markdown("Developed by: [foscraft](https://github.com/foscraft).")
    st.markdown("Talk to me  [here](https://wa.link/6uwu0u)")
    st.markdown("Data Source: [Energy Open Data](https://energydata.info/dataset/kenya-healthcare-facilities).")

if __name__ == "__main__":
    main()
