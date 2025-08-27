from jinja2 import Template
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import json

def get_type_color_map(facility_types):
    """Generate a color map for facility types using matplotlib's tab20 colormap."""
    colors = cm.get_cmap('tab20', max(len(facility_types), 1))
    return {ftype: mcolors.to_hex(colors(i % 20)) for i, ftype in enumerate(sorted(facility_types))}

def create_facility_map(df, type_color_map, county=None, constituency=None):
    """Create an interactive map using Leaflet.js with facility markers and legend."""
    # Prepare marker data
    markers = []
    for _, row in df[["Facility_N", "Type", "Owner", "County", "Sub_County", "Nearest_To", "Latitude", "Longitude", "Constituen"]].iterrows():
        if row['Latitude'] and row['Longitude']:
            tooltip_text = (
                f"<b>{row['Facility_N']}</b><br>"
                f"Type: {row['Type']}<br>"
                f"Owner: {row['Owner']}<br>"
                f"County: {row['County']}<br>"
                f"Sub-County: {row['Sub_County']}<br>"
                f"Nearest Town: {row['Nearest_To']}"
            )
            popup_text = tooltip_text + f"<br>Constituency: {row.get('Constituen','')}"
            markers.append({
                'lat': row['Latitude'],
                'lon': row['Longitude'],
                'tooltip': tooltip_text,
                'popup': popup_text,
                'color': type_color_map.get(row['Type'], '#3186cc')
            })

    # Create legend items
    legend_items = [
        {'type': ftype, 'color': color}
        for ftype, color in type_color_map.items()
    ]

    # HTML template for Leaflet map
    template = Template("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Facility Map</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <style>
            #map { width: 100%; height: 700px; }
            .leaflet-tooltip { background: white; border: 1px solid grey; border-radius: 4px; padding: 5px; }
            .legend { 
                position: fixed; 
                bottom: 50px; 
                left: 50px; 
                width: 250px; 
                background: white; 
                border: 2px solid grey; 
                border-radius: 8px; 
                padding: 10px; 
                z-index: 9999; 
                font-size: 14px; 
            }
        </style>
    </head>
    <body>
        <div id="map"></div>
        <div class="legend">
            <b>Facility Type Legend</b><br>
            {% for item in legend_items %}
                <span style="display:inline-block;width:12px;height:12px;background:{{ item.color }};border-radius:50%;margin-right:8px;"></span>{{ item.type }}<br>
            {% endfor %}
        </div>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script>
            var map = L.map('map').setView([0.0236, 37.9062], 6);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(map);

            var markers = {{ markers | tojson }};
            markers.forEach(function(m) {
                var marker = L.circleMarker([m.lat, m.lon], {
                    radius: 7,
                    color: m.color,
                    fillColor: m.color,
                    fillOpacity: 0.9,
                    weight: 1
                }).addTo(map);
                marker.bindTooltip(m.tooltip, { sticky: true });
                marker.bindPopup(m.popup);
            });
        </script>
    </body>
    </html>
    """)

    # Render the HTML
    html_content = template.render(markers=markers, legend_items=legend_items)
    return html_content