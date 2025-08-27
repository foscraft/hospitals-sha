import folium
import matplotlib.cm as cm
import matplotlib.colors as mcolors

def get_type_color_map(facility_types):
    # Use a fixed color map for consistency and cacheability
    colors = cm.get_cmap('tab20', max(len(facility_types), 1))
    return {ftype: mcolors.to_hex(colors(i % 20)) for i, ftype in enumerate(sorted(facility_types))}

def create_facility_map(df, type_color_map, county=None, constituency=None):
    # Assume df is already filtered upstream for performance
    m = folium.Map(
        location=[0.0236, 37.9062],
        zoom_start=6,
        tiles="OpenStreetMap",
        width='100%',
        height='100%'
    )
    # Use only necessary columns for iteration to speed up
    for _, row in df[["Facility_N", "Type", "Owner", "County", "Sub_County", "Nearest_To", "Latitude", "Longitude", "Constituen"]].iterrows():
        tooltip_text = (
            f"<b>{row['Facility_N']}</b><br>"
            f"Type: {row['Type']}<br>"
            f"Owner: {row['Owner']}<br>"
            f"County: {row['County']}<br>"
            f"Sub-County: {row['Sub_County']}<br>"
            f"Nearest Town: {row['Nearest_To']}"
        )
        popup_text = tooltip_text + f"<br>Constituency: {row.get('Constituen','')}"
        # Only add marker if coordinates are valid
        if row['Latitude'] and row['Longitude']:
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
    # Build legend HTML only once
    legend_items = "".join(
        f'<span style="display:inline-block;width:12px;height:12px;background:{color};border-radius:50%;margin-right:8px;"></span>{ftype}<br>'
        for ftype, color in type_color_map.items()
    )
    legend_html = f"""
    <div style="position: fixed; 
         bottom: 50px; left: 50px; width: 250px; height: auto; 
         z-index:9999; font-size:14px; background: white; border:2px solid grey; border-radius:8px; padding: 10px;">
    <b>Facility Type Legend</b><br>
    {legend_items}
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))