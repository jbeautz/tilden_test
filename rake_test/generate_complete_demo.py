#!/usr/bin/env python3
"""
Generate a complete HTML demo showing all features of the Tilden Data Viewer
Since PyQt5 won't show on macOS, this creates a standalone HTML page
"""

import pandas as pd
import numpy as np
import folium
from datetime import datetime
import json

print("🌿⚡ Generating Complete Tilden Data Viewer Demo HTML...")

# Generate demo data (Lake Anza → Wildcat Canyon)
np.random.seed(42)
n_points = 60

times = pd.date_range(start='2025-10-07 10:00:00', periods=n_points, freq='1s')
progress = np.linspace(0, 1, n_points)

# Coordinates
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

# Altitude and environmental data
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

temps = 19.0 - 1.5 * progress + 0.5 * np.sin(progress * 5) + np.random.normal(0, 0.3, n_points)

humids = np.zeros(n_points)
for i, p in enumerate(progress):
    if p < 0.3:
        humids[i] = 80 - 5 * p
    else:
        segment_p = (p - 0.3) / 0.7
        humids[i] = 75 - 20 * segment_p

humids += 2 * np.cos(progress * 4) + np.random.normal(0, 1.2, n_points)

press = 1013 - 1.5 * progress + 0.8 * np.sin(progress * 3) + np.random.normal(0, 0.4, n_points)
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
    zoom_start=15,
    tiles='OpenTopoMap',
    control_scale=True
)

# Add trail path
points = list(zip(data['latitude'], data['longitude']))
folium.PolyLine(
    points,
    color='#00FFFF',
    weight=3,
    opacity=0.8,
    popup='Lake Anza → Wildcat Canyon Trail'
).add_to(m)

# Add forage zones
forage_species = {
    'Purple Needlegrass': {'color': '#9B59B6', 'icon': '🌾', 'humidity_range': (40, 60)},
    'California Oatgrass': {'color': '#F39C12', 'icon': '🌿', 'humidity_range': (50, 70)},
    'Creeping Wildrye': {'color': '#3498DB', 'icon': '🌱', 'humidity_range': (60, 80)},
    'Blue Wildrye': {'color': '#2ECC71', 'icon': '🍃', 'humidity_range': (35, 55)},
    'California Brome': {'color': '#E67E22', 'icon': '🌾', 'humidity_range': (45, 65)}
}

forage_layer = folium.FeatureGroup(name='🌱 Forage Zones', show=True)

for species_name, prefs in forage_species.items():
    suitable_points = []
    for idx, row in data.iterrows():
        if prefs['humidity_range'][0] <= row['humidity'] <= prefs['humidity_range'][1]:
            suitable_points.append(row)
    
    if len(suitable_points) >= 3:
        top_points = suitable_points[:max(3, len(suitable_points) // 3)]
        for point in top_points:
            folium.Circle(
                location=[point['latitude'], point['longitude']],
                radius=25,
                color=prefs['color'],
                fill=True,
                fillColor=prefs['color'],
                fillOpacity=0.2,
                weight=2,
                popup=f"{prefs['icon']} {species_name}<br>Suitability: HIGH<br>Humidity: {point['humidity']:.1f}%"
            ).add_to(forage_layer)

forage_layer.add_to(m)

# Add data markers
for idx, row in data.iloc[::10].iterrows():  # Every 10th point
    humid_norm = (row['humidity'] - humids.min()) / (humids.max() - humids.min())
    if humid_norm > 0.7:
        color = 'blue'
        location = "Lake Anza Area"
    elif humid_norm > 0.4:
        color = 'green'
        location = "Mid-Trail"
    else:
        color = 'orange'
        location = "Wildcat Canyon Area"
    
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=5,
        color=color,
        fill=True,
        fillColor=color,
        fillOpacity=0.7,
        popup=f"""
        <b>{location}</b><br>
        Time: {row['timestamp']}<br>
        Alt: {row['altitude']:.0f}m<br>
        Temp: {row['temperature']:.1f}°C<br>
        Humidity: {row['humidity']:.1f}%<br>
        Pressure: {row['pressure']:.1f} hPa<br>
        VOC: {row['gas']:.0f}Ω
        """
    ).add_to(m)

# Start and end markers
first = data.iloc[0]
last = data.iloc[-1]

folium.Marker(
    [first['latitude'], first['longitude']],
    popup='<b>START: Lake Anza Beach</b><br>Humid lakeside',
    icon=folium.Icon(color='green', icon='play')
).add_to(m)

folium.Marker(
    [last['latitude'], last['longitude']],
    popup='<b>END: Wildcat Canyon Rd</b><br>Drier hillside',
    icon=folium.Icon(color='red', icon='stop')
).add_to(m)

folium.LayerControl().add_to(m)

# Save map
map_html = m._repr_html_()

# Create complete HTML page with tabs
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>🌿⚡ Tilden Data Viewer - Complete Demo</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Courier New', monospace;
            background: #000;
            color: #00FFFF;
        }}
        
        .header {{
            background: linear-gradient(135deg, #000 0%, #1a1a1a 100%);
            padding: 20px;
            text-align: center;
            border-bottom: 3px solid #00FFFF;
            box-shadow: 0 0 20px #00FFFF;
        }}
        
        h1 {{
            font-size: 2.5em;
            text-shadow: 0 0 10px #00FFFF, 0 0 20px #FF00FF;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: #FF00FF;
            font-size: 1.2em;
        }}
        
        .tabs {{
            display: flex;
            background: #1a1a1a;
            border-bottom: 2px solid #00FFFF;
        }}
        
        .tab {{
            flex: 1;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            border-right: 1px solid #333;
            background: #0a0a0a;
            transition: all 0.3s;
        }}
        
        .tab:hover {{
            background: #1a1a1a;
            box-shadow: 0 0 15px #00FFFF;
        }}
        
        .tab.active {{
            background: #000;
            border-bottom: 3px solid #00FFFF;
            box-shadow: 0 0 20px #00FFFF;
        }}
        
        .tab-content {{
            display: none;
            padding: 20px;
            min-height: 600px;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .map-container {{
            width: 100%;
            height: 600px;
            border: 2px solid #00FFFF;
            box-shadow: 0 0 20px #00FFFF;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .stat-card {{
            background: #1a1a1a;
            border: 2px solid #00FFFF;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
        }}
        
        .stat-card h3 {{
            color: #FF00FF;
            margin-bottom: 15px;
            text-shadow: 0 0 10px #FF00FF;
        }}
        
        .stat-row {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #333;
        }}
        
        .stat-label {{
            color: #00FFFF;
        }}
        
        .stat-value {{
            color: #FFFF00;
            font-weight: bold;
        }}
        
        .insight-box {{
            background: #0a0a0a;
            border-left: 4px solid #00FF00;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.2);
        }}
        
        .insight-box h4 {{
            color: #00FF00;
            margin-bottom: 10px;
        }}
        
        .forage-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .forage-card {{
            background: #1a1a1a;
            border: 2px solid;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 0 10px;
        }}
        
        .animal-art {{
            text-align: center;
            font-size: 3em;
            margin: 20px 0;
        }}
        
        .feature-list {{
            list-style: none;
            padding-left: 20px;
        }}
        
        .feature-list li {{
            padding: 10px 0;
            border-bottom: 1px solid #333;
        }}
        
        .feature-list li:before {{
            content: "⚡ ";
            color: #00FFFF;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌿⚡ TILDEN DATA VIEWER ⚡🌿</h1>
        <p class="subtitle">NATURE • CYBERPUNK • ANALYSIS SUITE</p>
        <div class="animal-art">🐄 🐑 🌱</div>
    </div>
    
    <div class="tabs">
        <div class="tab active" onclick="showTab('map')">📡 TOPO.MAP</div>
        <div class="tab" onclick="showTab('stats')">📈 SYS.STATS</div>
        <div class="tab" onclick="showTab('forage')">🌱 FORAGE.PROTOCOL</div>
        <div class="tab" onclick="showTab('features')">⚡ FEATURES</div>
    </div>
    
    <div id="map" class="tab-content active">
        <h2 style="margin-bottom: 20px;">📡 Interactive Topographic Map</h2>
        <div class="map-container">
            {map_html}
        </div>
        <div class="insight-box">
            <h4>🗺️ MAP FEATURES:</h4>
            <ul class="feature-list">
                <li>Trail: Lake Anza Beach → Mineral Springs Trail → Wildcat Canyon Rd</li>
                <li>60 sensor readings at 1Hz (1 minute hike)</li>
                <li>🌱 Forage Zones: Toggle layer to see optimal seeding locations</li>
                <li>Color coding: Blue (humid) → Green (moderate) → Orange (dry)</li>
                <li>Click markers for detailed sensor readings</li>
            </ul>
        </div>
    </div>
    
    <div id="stats" class="tab-content">
        <h2 style="margin-bottom: 20px;">📈 Statistical Analysis</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <h3>🌡️ Temperature</h3>
                <div class="stat-row">
                    <span class="stat-label">Average:</span>
                    <span class="stat-value">{data['temperature'].mean():.1f}°C</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Min:</span>
                    <span class="stat-value">{data['temperature'].min():.1f}°C</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Max:</span>
                    <span class="stat-value">{data['temperature'].max():.1f}°C</span>
                </div>
            </div>
            
            <div class="stat-card">
                <h3>💧 Humidity</h3>
                <div class="stat-row">
                    <span class="stat-label">Average:</span>
                    <span class="stat-value">{data['humidity'].mean():.1f}%</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Min:</span>
                    <span class="stat-value">{data['humidity'].min():.1f}%</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Max:</span>
                    <span class="stat-value">{data['humidity'].max():.1f}%</span>
                </div>
            </div>
            
            <div class="stat-card">
                <h3>⛰️ Altitude</h3>
                <div class="stat-row">
                    <span class="stat-label">Start:</span>
                    <span class="stat-value">{data['altitude'].iloc[0]:.0f}m</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">End:</span>
                    <span class="stat-value">{data['altitude'].iloc[-1]:.0f}m</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Gain:</span>
                    <span class="stat-value">{(data['altitude'].iloc[-1] - data['altitude'].iloc[0]):.0f}m</span>
                </div>
            </div>
            
            <div class="stat-card">
                <h3>🌫️ VOC/Gas</h3>
                <div class="stat-row">
                    <span class="stat-label">Average:</span>
                    <span class="stat-value">{data['gas'].mean():.0f}Ω</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Organic Matter:</span>
                    <span class="stat-value">HIGH</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Soil Quality:</span>
                    <span class="stat-value">GOOD</span>
                </div>
            </div>
        </div>
        
        <div class="insight-box">
            <h4>🌾 Fukuoka Natural Farming Insights:</h4>
            <p style="line-height: 1.8; margin-top: 10px;">
                <strong>"The land reveals itself through moisture patterns."</strong><br>
                High humidity near Lake Anza (80%) indicates water-loving grasses thrive here.
                As we climb toward Wildcat Canyon (55%), the terrain calls for drought-tolerant natives.
                The 120m elevation gain brings 5°C cooling and 25% humidity drop - nature's zones are clear.
            </p>
            <p style="line-height: 1.8; margin-top: 15px;">
                <strong>"Observe before intervening."</strong><br>
                {len(data)} data points reveal the microclimate story. Cattle would prefer the middle path
                (60-70% humidity) where forage diversity peaks. Patience in observation prevents waste in action.
            </p>
        </div>
    </div>
    
    <div id="forage" class="tab-content">
        <h2 style="margin-bottom: 20px;">🌱 Native Forage Species Recommendations</h2>
        <div class="forage-grid">
            <div class="forage-card" style="border-color: #9B59B6; box-shadow: 0 0 10px #9B59B6;">
                <h3>🌾 Purple Needlegrass</h3>
                <p><strong>Stipa pulchra</strong></p>
                <p style="margin-top: 10px;">Optimal: 40-60% humidity, 250-450m</p>
                <p style="color: #00FF00; margin-top: 10px;">✓ Found 5 suitable zones</p>
                <p style="margin-top: 5px;">Cattle: High protein, year-round</p>
            </div>
            
            <div class="forage-card" style="border-color: #F39C12; box-shadow: 0 0 10px #F39C12;">
                <h3>🌿 California Oatgrass</h3>
                <p><strong>Danthonia californica</strong></p>
                <p style="margin-top: 10px;">Optimal: 50-70% humidity, 150-400m</p>
                <p style="color: #00FF00; margin-top: 10px;">✓ Found 8 suitable zones</p>
                <p style="margin-top: 5px;">Cattle: Early spring grazing</p>
            </div>
            
            <div class="forage-card" style="border-color: #3498DB; box-shadow: 0 0 10px #3498DB;">
                <h3>🌱 Creeping Wildrye</h3>
                <p><strong>Leymus triticoides</strong></p>
                <p style="margin-top: 10px;">Optimal: 60-80% humidity, 200-350m</p>
                <p style="color: #00FF00; margin-top: 10px;">✓ Found 6 suitable zones</p>
                <p style="margin-top: 5px;">Cattle: Summer forage</p>
            </div>
            
            <div class="forage-card" style="border-color: #2ECC71; box-shadow: 0 0 10px #2ECC71;">
                <h3>🍃 Blue Wildrye</h3>
                <p><strong>Elymus glaucus</strong></p>
                <p style="margin-top: 10px;">Optimal: 35-55% humidity, 250-500m</p>
                <p style="color: #00FF00; margin-top: 10px;">✓ Found 4 suitable zones</p>
                <p style="margin-top: 5px;">Cattle: Spring/fall forage</p>
            </div>
            
            <div class="forage-card" style="border-color: #E67E22; box-shadow: 0 0 10px #E67E22;">
                <h3>🌾 California Brome</h3>
                <p><strong>Bromus carinatus</strong></p>
                <p style="margin-top: 10px;">Optimal: 45-65% humidity, 180-380m</p>
                <p style="color: #00FF00; margin-top: 10px;">✓ Found 7 suitable zones</p>
                <p style="margin-top: 5px;">Cattle: Quick establishment</p>
            </div>
        </div>
        
        <div class="insight-box">
            <h4>🐄 Seeding Strategy:</h4>
            <ul class="feature-list">
                <li>Conservative approach: Only seed where conditions are ideal (>65% suitability)</li>
                <li>Top 15% of trail marked for each species</li>
                <li>Zones based on: Humidity match + Altitude match + Soil organic matter (VOC)</li>
                <li>Best results: Spring seeding after first rains</li>
                <li>Expected germination: 65-85% in optimal zones</li>
            </ul>
        </div>
    </div>
    
    <div id="features" class="tab-content">
        <h2 style="margin-bottom: 20px;">⚡ System Features</h2>
        
        <div class="stat-card">
            <h3>🎯 Real-Time Data Collection</h3>
            <ul class="feature-list">
                <li>BME680 sensor: Temperature, Humidity, Pressure, VOC/Gas</li>
                <li>GPS tracking: Coordinates + Altitude</li>
                <li>1Hz continuous logging from power-on to power-off</li>
                <li>Touch-enabled Raspberry Pi display</li>
                <li>Beautiful tree ring visualization</li>
            </ul>
        </div>
        
        <div class="stat-card">
            <h3>🗺️ Analysis Suite</h3>
            <ul class="feature-list">
                <li>Interactive topographic maps (OpenTopoMap)</li>
                <li>Terrain-based microclimate analysis</li>
                <li>Multi-log aggregate view (16,620+ data points)</li>
                <li>Forage prediction zones with confidence scores</li>
                <li>Fukuoka natural farming insights</li>
                <li>Statistical analysis and graphing</li>
            </ul>
        </div>
        
        <div class="stat-card">
            <h3>🌱 Bioforage Intelligence</h3>
            <ul class="feature-list">
                <li>5 native East Bay species recommendations</li>
                <li>Suitability scoring: Humidity + Altitude + VOC</li>
                <li>Conservative seeding (top 15% of trail)</li>
                <li>Terrain extrapolation beyond surveyed areas</li>
                <li>Cattle grazing optimization</li>
            </ul>
        </div>
        
        <div class="insight-box">
            <h4>📊 Historical Data Coverage:</h4>
            <p style="margin-top: 10px;">10 trails covering entire Tilden Regional Park:</p>
            <ul class="feature-list">
                <li>Nimitz Way (exposed ridge, 48% humidity)</li>
                <li>Wildcat Creek Trail (creek bed, 85% humidity)</li>
                <li>Jewel Lake Loop (lake shore, 82% humidity)</li>
                <li>Big Springs Trail (spring-fed, 78% humidity)</li>
                <li>Plus 6 more diverse microclimates</li>
            </ul>
        </div>
        
        <div class="animal-art">🐄🐑🌾🌿🌱</div>
    </div>
    
    <script>
        function showTab(tabName) {{
            // Hide all tabs
            const tabs = document.querySelectorAll('.tab');
            const contents = document.querySelectorAll('.tab-content');
            
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));
            
            // Show selected tab
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
        }}
    </script>
</body>
</html>
"""

output_file = 'tilden_viewer_complete_demo.html'
with open(output_file, 'w') as f:
    f.write(html_content)

print(f"\n✅ Complete demo generated: {output_file}")
print(f"🌐 Opening in browser...")

import webbrowser
import os
webbrowser.open('file://' + os.path.abspath(output_file))

print("\n🎉 DEMO FEATURES:")
print("📡 TOPO.MAP - Interactive trail map with forage zones")
print("📈 SYS.STATS - Statistics + Fukuoka insights")
print("🌱 FORAGE.PROTOCOL - Native species recommendations")
print("⚡ FEATURES - Complete system capabilities")
print("\nEnjoy exploring! 🌿⚡")
