#!/usr/bin/env python3
"""
Quick demo: Generate the map HTML and open it in browser
No PyQt5 GUI needed - just creates the HTML map file
"""
import pandas as pd
import numpy as np
import folium
import webbrowser
import os

# Generate demo data (same as in data_viewer.py)
np.random.seed(42)
n_points = 60

# Create waypoints for the trail route
times = pd.date_range(start='2025-10-07 10:00:00', periods=n_points, freq='1s')
progress = np.linspace(0, 1, n_points)

# Latitude: move northeast from beach → around lake → up trail → Wildcat Rd
lat_beach = 37.8964
lat_east_lake = 37.8972
lat_trailhead = 37.8980
lat_wildcat = 37.9010

lats = np.zeros(n_points)
for i, p in enumerate(progress):
    if p < 0.25:
        segment_p = p / 0.25
        lats[i] = lat_beach + (lat_east_lake - lat_beach) * segment_p
    elif p < 0.4:
        segment_p = (p - 0.25) / 0.15
        lats[i] = lat_east_lake + (lat_trailhead - lat_east_lake) * segment_p
    else:
        segment_p = (p - 0.4) / 0.6
        lats[i] = lat_trailhead + (lat_wildcat - lat_trailhead) * segment_p

lats += 0.00015 * np.sin(progress * 12) + np.random.normal(0, 0.00004, n_points)

# Longitude
lon_beach = -122.2445
lon_east_lake = -122.2435
lon_trailhead = -122.2430
lon_wildcat = -122.2405

lons = np.zeros(n_points)
for i, p in enumerate(progress):
    if p < 0.25:
        segment_p = p / 0.25
        lons[i] = lon_beach + (lon_east_lake - lon_beach) * segment_p
    elif p < 0.4:
        segment_p = (p - 0.25) / 0.15
        lons[i] = lon_east_lake + (lon_trailhead - lon_east_lake) * segment_p
    else:
        segment_p = (p - 0.4) / 0.6
        lons[i] = lon_trailhead + (lon_wildcat - lon_trailhead) * segment_p

lons += 0.0002 * np.cos(progress * 10) + np.random.normal(0, 0.00005, n_points)

# Altitude
alt_beach = 230
alt_trailhead = 250
alt_wildcat = 350

alts = np.zeros(n_points)
for i, p in enumerate(progress):
    if p < 0.4:
        alts[i] = alt_beach + (alt_trailhead - alt_beach) * (p / 0.4)
    else:
        segment_p = (p - 0.4) / 0.6
        alts[i] = alt_trailhead + (alt_wildcat - alt_trailhead) * segment_p

alts += 3 * np.sin(progress * 8) + np.random.normal(0, 1.5, n_points)

# Temperature
temps = 19.0 - 1.5 * progress + 0.5 * np.sin(progress * 5) + np.random.normal(0, 0.3, n_points)

# Humidity
humids = np.zeros(n_points)
for i, p in enumerate(progress):
    if p < 0.3:
        humids[i] = 80 - 5 * p
    else:
        segment_p = (p - 0.3) / 0.7
        humids[i] = 75 - 20 * segment_p

humids += 2 * np.cos(progress * 4) + np.random.normal(0, 1.2, n_points)

# Pressure
press = 1013 - 1.5 * progress + 0.8 * np.sin(progress * 3) + np.random.normal(0, 0.4, n_points)

# Gas/VOC
gas = 65000 - 15000 * (progress ** 1.3) + 2000 * np.sin(progress * 6) + np.random.normal(0, 500, n_points)

data = pd.DataFrame({
    'timestamp': times,
    'latitude': lats,
    'longitude': lons,
    'altitude': alts,
    'temperature': temps,
    'humidity': humids,
    'pressure': press,
    'gas': gas
})

# Create map
center_lat = data['latitude'].mean()
center_lon = data['longitude'].mean()

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=16,
    tiles='OpenTopoMap',
    control_scale=True
)

# Add alternative tile layers
folium.TileLayer('OpenStreetMap').add_to(m)

# Color function for humidity
def get_humidity_color(norm_humid):
    if norm_humid > 0.7:
        return '#0066FF'  # Blue - very humid
    elif norm_humid > 0.4:
        return '#FFAA00'  # Orange - medium
    else:
        return '#FF3333'  # Red - dry

# Add markers
humids = data['humidity'].values
humid_min, humid_max = humids.min(), humids.max()

for idx, row in data.iterrows():
    humid_norm = (row['humidity'] - humid_min) / (humid_max - humid_min) if humid_max > humid_min else 0.5
    color = get_humidity_color(humid_norm)
    
    if row['humidity'] > 70:
        location = "Lake Anza Beach/Shoreline"
    elif row['humidity'] > 60:
        location = "Mineral Springs Trailhead"
    else:
        location = "Mineral Springs Trail / Hillside"
    
    popup_html = f"""
    <b>Location:</b> {location}<br>
    <b>Time:</b> {row['timestamp']}<br>
    <b>Altitude:</b> {row['altitude']:.1f} m<br>
    <hr>
    <b>Humidity:</b> {row['humidity']:.1f}% {'💧' if row['humidity'] > 65 else '☀️' if row['humidity'] < 55 else '🌤️'}<br>
    <b>Temp:</b> {row['temperature']:.1f}°C<br>
    <b>Pressure:</b> {row['pressure']:.1f} hPa<br>
    <b>VOC/Gas:</b> {row['gas']:.0f} Ω
    """
    
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=6,
        popup=folium.Popup(popup_html, max_width=250),
        color=color,
        fill=True,
        fillColor=color,
        fillOpacity=0.7
    ).add_to(m)

# Add path line
points = list(zip(data['latitude'], data['longitude']))
folium.PolyLine(
    points,
    color='blue',
    weight=2,
    opacity=0.5
).add_to(m)

# Add start and end markers
first = data.iloc[0]
last = data.iloc[-1]

folium.Marker(
    [first['latitude'], first['longitude']],
    popup=f'<b>START: Lake Anza Beach</b><br>Humid Lakeside<br>Alt: {first["altitude"]:.0f}m<br>Humidity: {first["humidity"]:.1f}%',
    icon=folium.Icon(color='green', icon='play')
).add_to(m)

folium.Marker(
    [last['latitude'], last['longitude']],
    popup=f'<b>END: Wildcat Canyon Road</b><br>Drier Hillside<br>Alt: {last["altitude"]:.0f}m<br>Humidity: {last["humidity"]:.1f}%',
    icon=folium.Icon(color='red', icon='stop')
).add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Save map
map_file = 'tilden_trail_map_demo.html'
m.save(map_file)
print(f"Map saved to: {os.path.abspath(map_file)}")
print(f"Opening in browser...")

# Open in browser
webbrowser.open('file://' + os.path.abspath(map_file))
print("Done!")
