#!/usr/bin/env python3
"""
Generate comprehensive HTML demo with individual trail views + aggregate view
"""

import pandas as pd
import folium
from folium import plugins
import os
from terrain_analysis import TerrainAnalyzer

FORAGE_SPECIES = [
    {
        'name': 'Purple Needlegrass',
        'scientific': 'Stipa pulchra',
        'humidity_range': (40, 60),
        'altitude_range': (250, 450),
        'description': 'CA state grass, deep roots, drought tolerant',
        'color': '#9370DB'
    },
    {
        'name': 'California Oatgrass',
        'scientific': 'Danthonia californica',
        'humidity_range': (50, 70),
        'altitude_range': (150, 400),
        'description': 'Bunching grass, cool-season growth, shade tolerant',
        'color': '#90EE90'
    },
    {
        'name': 'Creeping Wildrye',
        'scientific': 'Elymus triticoides',
        'humidity_range': (60, 80),
        'altitude_range': (200, 350),
        'description': 'Rhizomatous, erosion control, wetland edges',
        'color': '#87CEEB'
    },
    {
        'name': 'Blue Wildrye',
        'scientific': 'Elymus glaucus',
        'humidity_range': (35, 55),
        'altitude_range': (250, 500),
        'description': 'Tall bunch grass, wildlife habitat, fire resistant',
        'color': '#4169E1'
    },
    {
        'name': 'California Brome',
        'scientific': 'Bromus carinatus',
        'humidity_range': (45, 65),
        'altitude_range': (180, 380),
        'description': 'Versatile native, quick establishment, revegetation',
        'color': '#DAA520'
    }
]

def add_forage_zones(m, df):
    """Add forage prediction zones to map"""
    for species in FORAGE_SPECIES:
        suitable_points = []
        
        for _, row in df.iterrows():
            humidity = row['humidity']
            altitude = row['altitude']
            
            h_min, h_max = species['humidity_range']
            a_min, a_max = species['altitude_range']
            
            if h_min <= humidity <= h_max and a_min <= altitude <= a_max:
                suitable_points.append([row['latitude'], row['longitude']])
        
        if suitable_points:
            for point in suitable_points[::5]:
                folium.Circle(
                    location=point,
                    radius=20,
                    color=species['color'],
                    fill=True,
                    fillColor=species['color'],
                    fillOpacity=0.3,
                    opacity=0.5,
                    popup=f"<b>{species['name']}</b><br><i>{species['scientific']}</i><br>{species['description']}"
                ).add_to(m)

def create_trail_map(df, trail_name):
    """Create individual trail map"""
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=15,
        tiles='OpenTopoMap'
    )
    
    # Trail path
    trail_coords = list(zip(df['latitude'], df['longitude']))
    folium.PolyLine(
        trail_coords,
        color='#00FFCC',
        weight=3,
        opacity=0.8,
        popup=trail_name
    ).add_to(m)
    
    # Start/End markers
    folium.Marker(
        [df.iloc[0]['latitude'], df.iloc[0]['longitude']],
        popup='START',
        icon=folium.Icon(color='green', icon='play')
    ).add_to(m)
    
    folium.Marker(
        [df.iloc[-1]['latitude'], df.iloc[-1]['longitude']],
        popup='END',
        icon=folium.Icon(color='red', icon='stop')
    ).add_to(m)
    
    # Forage zones
    add_forage_zones(m, df)
    
    # Data markers
    for idx in range(0, len(df), 10):
        row = df.iloc[idx]
        popup_html = f"""
        <div style='font-family: monospace; color: #00FFCC; background: #000; padding: 5px;'>
            <b>SENSOR DATA</b><br>
            Temp: {row['temperature']:.1f}°C<br>
            Humidity: {row['humidity']:.1f}%<br>
            Pressure: {row['pressure']:.1f} hPa<br>
            Altitude: {row['altitude']:.1f}m<br>
            VOC: {row['gas']:.0f} Ω
        </div>
        """
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=3,
            color='#FF00FF',
            fill=True,
            fillColor='#FF00FF',
            fillOpacity=0.6,
            popup=folium.Popup(popup_html, max_width=200)
        ).add_to(m)
    
    return m

def create_aggregate_map(dfs_dict):
    """Create aggregate map with all trails"""
    all_lats = []
    all_lons = []
    for df in dfs_dict.values():
        all_lats.extend(df['latitude'].tolist())
        all_lons.extend(df['longitude'].tolist())
    
    center_lat = sum(all_lats) / len(all_lats)
    center_lon = sum(all_lons) / len(all_lons)
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=14,
        tiles='OpenTopoMap'
    )
    
    # Trail colors
    trail_colors = ['#00FFCC', '#FF00FF', '#00FF00', '#FFFF00', '#FF6600',
                   '#0099FF', '#FF0066', '#99FF00', '#CC00FF', '#FF9900']
    
    # Add each trail
    for idx, (trail_name, df) in enumerate(sorted(dfs_dict.items())):
        color = trail_colors[idx % len(trail_colors)]
        trail_coords = list(zip(df['latitude'], df['longitude']))
        
        folium.PolyLine(
            trail_coords,
            color=color,
            weight=2,
            opacity=0.7,
            popup=trail_name
        ).add_to(m)
    
    # Aggregate forage zones
    combined_df = pd.concat(dfs_dict.values(), ignore_index=True)
    
    for species in FORAGE_SPECIES:
        suitable_points = []
        
        for _, row in combined_df.iterrows():
            humidity = row['humidity']
            altitude = row['altitude']
            
            h_min, h_max = species['humidity_range']
            a_min, a_max = species['altitude_range']
            
            if h_min <= humidity <= h_max and a_min <= altitude <= a_max:
                suitable_points.append([row['latitude'], row['longitude']])
        
        if suitable_points:
            for point in suitable_points[::8]:
                folium.Circle(
                    location=point,
                    radius=30,
                    color=species['color'],
                    fill=True,
                    fillColor=species['color'],
                    fillOpacity=0.2,
                    opacity=0.4,
                    popup=f"<b>{species['name']}</b><br><i>{species['scientific']}</i>"
                ).add_to(m)
    
    return m

def main():
    print("\n" + "="*80)
    print("GENERATING MULTI-TRAIL HTML DEMO")
    print("="*80 + "\n")
    
    # Load all trail data
    log_files = [f for f in os.listdir('.') if f.startswith('rake_log_') and f.endswith('.csv')]
    
    if not log_files:
        print("❌ No log files found!")
        return
    
    dfs_dict = {}
    for log_file in sorted(log_files):
        try:
            df = pd.read_csv(log_file)
            trail_name = log_file.replace('rake_log_', '').replace('.csv', '')
            dfs_dict[trail_name] = df
            print(f"✓ Loaded: {trail_name} ({len(df)} points)")
        except Exception as e:
            print(f"✗ Error loading {log_file}: {e}")
    
    if not dfs_dict:
        print("❌ No data loaded!")
        return
    
    print(f"\n📊 Total trails: {len(dfs_dict)}")
    total_points = sum(len(df) for df in dfs_dict.values())
    print(f"📊 Total data points: {total_points:,}\n")
    
    # Generate HTML
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Tilden Multi-Trail Viewer</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Courier New', monospace;
            background-color: #000;
            color: #00FFCC;
        }
        
        .header {
            background-color: #000;
            border-bottom: 3px solid #00FFCC;
            padding: 20px;
            text-align: center;
        }
        
        .header h1 {
            margin: 0;
            color: #00FFCC;
            font-size: 24px;
            text-shadow: 0 0 10px #00FFCC;
        }
        
        .tab-container {
            display: flex;
            background-color: #111;
            border-bottom: 2px solid #00FFCC;
            overflow-x: auto;
            padding: 0;
        }
        
        .tab {
            padding: 15px 30px;
            cursor: pointer;
            border: none;
            background-color: #000;
            color: #00FFCC;
            border-right: 1px solid #00FFCC;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            white-space: nowrap;
        }
        
        .tab:hover {
            background-color: #1a1a1a;
        }
        
        .tab.active {
            background-color: #00FFCC;
            color: #000;
        }
        
        .map-content {
            display: none;
            width: 100%;
            height: calc(100vh - 180px);
        }
        
        .map-content.active {
            display: block;
        }
        
        .map-frame {
            width: 100%;
            height: 100%;
            border: none;
        }
        
        .info-panel {
            background-color: #1a1a1a;
            border-top: 2px solid #00FFCC;
            padding: 10px 20px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>╔══════════════════════════════════════════════════════════════════╗</h1>
        <h1>║        TILDEN MULTI-TRAIL VIEWER • TERRAIN INTELLIGENCE        ║</h1>
        <h1>╚══════════════════════════════════════════════════════════════════╝</h1>
    </div>
    
    <div class="tab-container">
        <button class="tab active" onclick="showMap(0)">🌐 ALL TRAILS</button>
"""
    
    # Add individual trail tabs
    for idx, trail_name in enumerate(sorted(dfs_dict.keys()), 1):
        short_name = ' '.join(trail_name.split('_')[2:5])[:20]
        html_content += f'        <button class="tab" onclick="showMap({idx})">📍 {short_name}</button>\n'
    
    html_content += """    </div>
    
    <div id="maps">
"""
    
    # Generate and embed aggregate map
    print("📍 Generating aggregate map...")
    aggregate_map = create_aggregate_map(dfs_dict)
    aggregate_html = aggregate_map._repr_html_()
    
    html_content += f"""
        <div class="map-content active" id="map-0">
            {aggregate_html}
        </div>
"""
    
    # Generate and embed individual trail maps
    for idx, (trail_name, df) in enumerate(sorted(dfs_dict.items()), 1):
        print(f"📍 Generating map for: {trail_name}")
        trail_map = create_trail_map(df, trail_name)
        trail_html = trail_map._repr_html_()
        
        html_content += f"""
        <div class="map-content" id="map-{idx}">
            {trail_html}
        </div>
"""
    
    html_content += """    </div>
    
    <div class="info-panel">
"""
    
    html_content += f"        <strong>TRAILS ANALYZED:</strong> {len(dfs_dict)} | "
    html_content += f"<strong>TOTAL DATA POINTS:</strong> {total_points:,} | "
    html_content += f"<strong>NATIVE SPECIES:</strong> 5 | "
    html_content += "<strong>PROTOCOL:</strong> Fukuoka Natural Farming"
    
    html_content += """
    </div>
    
    <script>
        function showMap(index) {
            // Hide all maps
            const maps = document.querySelectorAll('.map-content');
            maps.forEach(map => map.classList.remove('active'));
            
            // Remove active from all tabs
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Show selected map
            document.getElementById('map-' + index).classList.add('active');
            tabs[index].classList.add('active');
        }
    </script>
</body>
</html>
"""
    
    # Write to file
    output_file = 'tilden_multi_trail_demo.html'
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"\n✅ Generated: {output_file}")
    print(f"🌐 Open in browser to view all {len(dfs_dict)} trails!\n")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
