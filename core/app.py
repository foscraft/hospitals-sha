import os
import streamlit as st
from streamlit_folium import st_folium

from database_engine import get_connection  
from map_utils import get_type_color_map, create_facility_map, add_legend
from stats_utils import show_statistics, plot_charts


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="Health Facilities in Kenya",
    layout="wide",
    page_icon=os.path.join(BASE_DIR, '..', 'images', 'favicon.ico'),
)

st.title("🏥 Health Facilities in Kenya")
st.markdown("This app visualizes health facility locations and provides statistical analysis.")


conn = get_connection()

def sql_to_df(sql: str, params: tuple = ()):
    return conn.execute(sql, params).fetch_df()


# ---------------- Query Helpers ---------------- #
@st.cache_data(show_spinner=False)
def get_distinct_counties():
    sql = "SELECT DISTINCT County FROM facilities WHERE County IS NOT NULL ORDER BY County"
    rows = sql_to_df(sql)
    return ["All"] + rows["County"].tolist()

@st.cache_data(show_spinner=False)
def get_distinct_constituencies(county: str):
    if county != "All":
        sql = """
            SELECT DISTINCT Constituen
            FROM facilities
            WHERE County = ? AND Constituen IS NOT NULL
            ORDER BY Constituen
        """
        rows = sql_to_df(sql, (county,))
    else:
        sql = """
            SELECT DISTINCT Constituen
            FROM facilities
            WHERE Constituen IS NOT NULL
            ORDER BY Constituen
        """
        rows = sql_to_df(sql)
    return ["All"] + rows["Constituen"].tolist()

def build_where(county: str, constituency: str):
    clauses, params = [], []
    if county != "All":
        clauses.append("County = ?")
        params.append(county)
    if constituency != "All":
        clauses.append("Constituen = ?")
        params.append(constituency)
    where_sql = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    return where_sql, tuple(params)

def get_filtered_df(county: str, constituency: str):
    where_sql, params = build_where(county, constituency)
    sql = f"""
        SELECT Facility_N, Type, Owner, Sub_County, Constituen, Nearest_To, Latitude, Longitude, County
        FROM facilities
        {where_sql}
    """
    return sql_to_df(sql, params)

def get_metrics(county: str, constituency: str):
    where_sql, params = build_where(county, constituency)
    sql = f"""
        SELECT
            COUNT(*)::INT AS total_facilities,
            COUNT(DISTINCT County)::INT AS counties,
            COUNT(DISTINCT Constituen)::INT AS constituencies
        FROM facilities
        {where_sql}
    """
    row = conn.execute(sql, params).fetchone()
    return row if row else (0, 0, 0)

@st.cache_data(show_spinner=False)
def get_distinct_types():
    sql = "SELECT DISTINCT Type FROM facilities WHERE Type IS NOT NULL ORDER BY Type"
    rows = sql_to_df(sql)
    return rows["Type"].tolist()

@st.cache_resource(show_spinner=False)
def get_type_color_map_cached(types_tuple):
    return get_type_color_map(list(types_tuple))


# ---------------- Main App ---------------- #
def main():
    st.subheader("🔍 Filter Facilities")
    col_county, col_const = st.columns([1, 1])

    county_options = get_distinct_counties()
    with col_county:
        selected_county = st.selectbox("Select County", options=county_options)

    constituency_options = get_distinct_constituencies(selected_county)
    with col_const:
        selected_constituency = st.selectbox("Select Constituency", options=constituency_options)

    st.subheader("📊 Summary Stats")
    total, n_counties, n_const = get_metrics(selected_county, selected_constituency)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Facilities", f"{total:,}")
    c2.metric("Counties", n_counties)
    c3.metric("Constituencies", n_const)

    # --- Facility Types & Colors ---
    types = get_distinct_types()
    type_color_map = get_type_color_map_cached(tuple(types))

    # --- Filtered Slice ---
    filtered_df = get_filtered_df(selected_county, selected_constituency)

    # --- Map Section ---
    st.subheader("🗺️ Map of Health Facilities")
    with st.spinner("Rendering map..."):
        m = create_facility_map(filtered_df, type_color_map,
                                county=selected_county, constituency=selected_constituency)
        add_legend(m, type_color_map)
        st_folium(m, use_container_width=True, height=700)

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
