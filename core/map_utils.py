import folium
import matplotlib.cm as cm
import matplotlib.colors as mcolors

def get_type_color_map(facility_types):
    colors = cm.get_cmap('tab20', len(facility_types))
    return {ftype: mcolors.to_hex(colors(i)) for i, ftype in enumerate(facility_types)}

def create_facility_map(df, type_color_map, county=None, constituency=None):
    # Filter the DataFrame if filters are provided
    filtered_df = df.copy()
    if county and county != 'All':
        filtered_df = filtered_df[filtered_df['County'] == county]
    if constituency and constituency != 'All':
        filtered_df = filtered_df[filtered_df['Constituen'] == constituency]

    m = folium.Map(
        location=[0.0236, 37.9062],
        zoom_start=6,
        tiles="OpenStreetMap",
        width='100%',
        height='100%'
    )
    for idx, row in filtered_df.iterrows():
        tooltip_text = (
            f"<b>{row['Facility_N']}</b><br>"
            f"Type: {row['Type']}<br>"
            f"Owner: {row['Owner']}<br>"
            f"County: {row['County']}<br>"
            f"Sub-County: {row['Sub_County']}<br>"
            f"Nearest Town: {row['Nearest_To']}"
        )
        popup_text = (
            f"<b>{row['Facility_N']}</b><br>"
            f"Type: {row['Type']}<br>"
            f"Owner: {row['Owner']}<br>"
            f"County: {row['County']}<br>"
            f"Sub-County: {row['Sub_County']}<br>"
            f"Division: {row.get('Division','')}<br>"
            f"Location: {row.get('Location','')}<br>"
            f"Sub-Location: {row.get('Sub_Locati','')}<br>"
            f"Constituency: {row.get('Constituen','')}<br>"
            f"Nearest Town: {row['Nearest_To']}"
        )
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=7,
            color=type_color_map.get(row['Type'], "#3186cc"),
            fill=True,
            fill_color=type_color_map.get(row['Type'], "#3186cc"),
            fill_opacity=0.9,
            tooltip=folium.Tooltip(tooltip_text, sticky=True),
            popup=popup_text
        ).add_to(m)
    return m

def add_legend(m, type_color_map):
    legend_html = """
    <div style="position: fixed; 
         bottom: 50px; left: 50px; width: 250px; height: auto; 
         z-index:9999; font-size:14px; background: white; border:2px solid grey; border-radius:8px; padding: 10px;">
    <b>Facility Type Legend</b><br>
    """
    for ftype, color in type_color_map.items():
        legend_html += f'<span style="display:inline-block;width:12px;height:12px;background:{color};border-radius:50%;margin-right:8px;"></span>{ftype}<br>'
    legend_html += "</div>"
    m.get_root().html.add_child(folium.Element(legend_html))