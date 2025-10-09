#!/usr/bin/env python3
"""
Tilden Data Viewer - Interactive Map and Graph Analysis Tool
Displays sensor data on topographical maps and creates analysis graphs
"""

import sys
import os
import glob
import pandas as pd
import folium
from folium import plugins
import webbrowser
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np

# Import terrain analysis module
try:
    from terrain_analysis import TerrainAnalyzer
    TERRAIN_ANALYSIS_AVAILABLE = True
except ImportError:
    print("Warning: terrain_analysis module not found - advanced features disabled")
    TERRAIN_ANALYSIS_AVAILABLE = False

try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QPushButton, QLabel, QComboBox,
                                 QFileDialog, QTabWidget, QTextEdit, QSplitter)
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    from PyQt5.QtCore import QUrl, Qt
except ImportError:
    print("PyQt5 not installed. Installing required packages...")
    print("Run: pip3 install PyQt5 PyQtWebEngine folium pandas matplotlib")
    sys.exit(1)


class DataViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tilden Data Viewer - Environmental Data Analysis")
        self.setGeometry(100, 100, 1400, 900)
        
        # Data storage
        self.data = None
        self.demo_mode = True
        self.historical_data = []  # Store historical hikes for comparison
        self.terrain_profiles = []  # Terrain type analysis
        
        # Initialize terrain analyzer
        if TERRAIN_ANALYSIS_AVAILABLE:
            self.terrain_analyzer = TerrainAnalyzer()
        else:
            self.terrain_analyzer = None
        
        # Setup UI
        self.setup_ui()
        
        # Load demo data by default
        self.load_demo_data()
    
    def setup_ui(self):
        """Setup the user interface with nature-cyberpunk aesthetic"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Apply cyberpunk-nature stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a1f1f, stop:1 #051010);
            }
            QWidget {
                background-color: #0a1f1f;
                color: #00ff88;
                font-family: 'Courier New', monospace;
                font-size: 12pt;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a4040, stop:1 #0a2525);
                color: #00ffaa;
                border: 2px solid #00ff88;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a5555, stop:1 #1a3535);
                color: #00ffcc;
                border: 2px solid #00ffcc;
                box-shadow: 0 0 10px #00ff88;
            }
            QPushButton:pressed {
                background: #0a2525;
                border: 2px solid #00cc88;
            }
            QLabel {
                color: #88ffcc;
                font-size: 11pt;
                padding: 4px;
            }
            QTabWidget::pane {
                border: 2px solid #00ff88;
                background: #051515;
                border-radius: 4px;
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a3030, stop:1 #0a1818);
                color: #88ffaa;
                border: 2px solid #006644;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 10px 20px;
                margin-right: 4px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a5050, stop:1 #1a3030);
                color: #00ffaa;
                border: 2px solid #00ff88;
                border-bottom: none;
            }
            QTabBar::tab:hover {
                background: #1a4040;
                color: #00ffcc;
            }
            QTextEdit {
                background-color: #0a1818;
                color: #88ffaa;
                border: 2px solid #006644;
                border-radius: 4px;
                padding: 8px;
                selection-background-color: #00ff88;
                selection-color: #000000;
            }
            QComboBox {
                background: #1a3030;
                color: #00ffaa;
                border: 2px solid #00ff88;
                border-radius: 4px;
                padding: 6px;
            }
            QComboBox:hover {
                border: 2px solid #00ffcc;
                background: #2a4040;
            }
            QComboBox::drop-down {
                border: none;
                background: #00ff88;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid #0a1f1f;
            }
            QComboBox QAbstractItemView {
                background: #1a3030;
                color: #00ffaa;
                border: 2px solid #00ff88;
                selection-background-color: #00ff88;
                selection-color: #000000;
            }
        """)
        
        # Top control panel - Cyberpunk style
        control_panel = QHBoxLayout()
        
        self.load_btn = QPushButton("⚡ LOAD FILES")
        self.load_btn.clicked.connect(self.load_csv_data)
        control_panel.addWidget(self.load_btn)
        
        self.load_all_btn = QPushButton("📊 LOAD ALL LOGS")
        self.load_all_btn.clicked.connect(self.load_all_historical_logs)
        control_panel.addWidget(self.load_all_btn)
        
        self.demo_btn = QPushButton("� DEMO MODE")
        self.demo_btn.clicked.connect(self.load_demo_data)
        control_panel.addWidget(self.demo_btn)
        
        self.refresh_btn = QPushButton("🔄 SYNC")
        self.refresh_btn.clicked.connect(self.update_map)
        control_panel.addWidget(self.refresh_btn)
        
        control_panel.addStretch()
        
        self.status_label = QLabel("⬢ SYSTEM READY • DEMO MODE ACTIVE")
        control_panel.addWidget(self.status_label)
        
        main_layout.addLayout(control_panel)
        
        # Tabs for different views
        self.tabs = QTabWidget()
        
        # Map Tab
        self.map_tab = QWidget()
        map_layout = QVBoxLayout(self.map_tab)
        self.map_view = QWebEngineView()
        map_layout.addWidget(self.map_view)
        self.tabs.addTab(self.map_tab, "⬢ TERRAIN MAP")
        
        # Graphs Tab
        self.graphs_tab = QWidget()
        graphs_layout = QVBoxLayout(self.graphs_tab)
        
        # Graph controls
        graph_controls = QHBoxLayout()
        graph_controls.addWidget(QLabel("⚡ SENSOR:"))
        self.param_combo = QComboBox()
        self.param_combo.addItems(["Temperature", "Humidity", "Pressure", "Gas/VOC"])
        self.param_combo.currentTextChanged.connect(self.update_graph)
        graph_controls.addWidget(self.param_combo)
        graph_controls.addStretch()
        graphs_layout.addLayout(graph_controls)
        
        # Matplotlib canvas with cyberpunk dark theme
        self.figure = Figure(figsize=(12, 6), facecolor='#0a1f1f')
        self.canvas = FigureCanvasQTAgg(self.figure)
        graphs_layout.addWidget(self.canvas)
        
        self.tabs.addTab(self.graphs_tab, "⚡ DATA STREAM")
        
        # Statistics Tab
        self.stats_tab = QWidget()
        stats_layout = QVBoxLayout(self.stats_tab)
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        stats_layout.addWidget(self.stats_text)
        self.tabs.addTab(self.stats_tab, "� ANALYTICS")
        
        # Native Forage Recommendations Tab
        self.forage_tab = QWidget()
        forage_layout = QVBoxLayout(self.forage_tab)
        self.forage_text = QTextEdit()
        self.forage_text.setReadOnly(True)
        forage_layout.addWidget(self.forage_text)
        self.tabs.addTab(self.forage_tab, "� BIOFORGE PROTOCOL")
        
        main_layout.addWidget(self.tabs)
    
    def load_demo_data(self):
        """Generate demo data for Lake Anza Beach → Mineral Springs Trail → Wildcat Canyon Road"""
        self.demo_mode = True
        self.status_label.setText("⬢ SIMULATION ACTIVE • Lake Anza Beach ➜ Mineral Springs ➜ Wildcat Canyon")
        
        # Real Tilden Park coordinates for this specific trail
        # Lake Anza Beach (start, humid): 37.8964, -122.2445, ~230m elevation
        # Around lake east side: 37.8972, -122.2435
        # Mineral Springs Trailhead: 37.8980, -122.2430, ~250m
        # Up Mineral Springs Trail: climbing northeast
        # Wildcat Canyon Road (end): 37.9010, -122.2405, ~350m elevation
        
        np.random.seed(42)
        n_points = 60  # 60 points = 1 minute of hiking data at 1 Hz
        
        # Create waypoints for the trail route
        times = pd.date_range(start='2025-10-07 10:00:00', periods=n_points, freq='1s')
        progress = np.linspace(0, 1, n_points)
        
        # Define trail segments with waypoints
        # Segment 1 (0-0.25): Lake Anza beach to east side (humid, flat)
        # Segment 2 (0.25-0.4): Around lake to Mineral Springs trailhead
        # Segment 3 (0.4-1.0): Up Mineral Springs Trail to Wildcat Canyon Rd (climbing, drying)
        
        # Latitude: move northeast from beach (37.8964) → around lake → up trail → Wildcat Rd (37.9010)
        lat_beach = 37.8964
        lat_east_lake = 37.8972
        lat_trailhead = 37.8980
        lat_wildcat = 37.9010
        
        lats = np.zeros(n_points)
        for i, p in enumerate(progress):
            if p < 0.25:  # Beach to east side
                segment_p = p / 0.25
                lats[i] = lat_beach + (lat_east_lake - lat_beach) * segment_p
            elif p < 0.4:  # East side to trailhead
                segment_p = (p - 0.25) / 0.15
                lats[i] = lat_east_lake + (lat_trailhead - lat_east_lake) * segment_p
            else:  # Up Mineral Springs Trail
                segment_p = (p - 0.4) / 0.6
                lats[i] = lat_trailhead + (lat_wildcat - lat_trailhead) * segment_p
        
        # Add natural path winding
        lats += 0.00015 * np.sin(progress * 12) + np.random.normal(0, 0.00004, n_points)
        
        # Longitude: move east then northeast
        lon_beach = -122.2445
        lon_east_lake = -122.2435
        lon_trailhead = -122.2430
        lon_wildcat = -122.2405
        
        lons = np.zeros(n_points)
        for i, p in enumerate(progress):
            if p < 0.25:  # Beach to east side (moving east)
                segment_p = p / 0.25
                lons[i] = lon_beach + (lon_east_lake - lon_beach) * segment_p
            elif p < 0.4:  # East side to trailhead
                segment_p = (p - 0.25) / 0.15
                lons[i] = lon_east_lake + (lon_trailhead - lon_east_lake) * segment_p
            else:  # Up trail (continuing east/northeast)
                segment_p = (p - 0.4) / 0.6
                lons[i] = lon_trailhead + (lon_wildcat - lon_trailhead) * segment_p
        
        # Add trail curves
        lons += 0.0002 * np.cos(progress * 10) + np.random.normal(0, 0.00005, n_points)
        
        # Altitude: gentle start, then steady climb up Mineral Springs
        alt_beach = 230  # Lake Anza beach level
        alt_trailhead = 250  # Slight rise to trailhead
        alt_wildcat = 350  # Wildcat Canyon Road
        
        alts = np.zeros(n_points)
        for i, p in enumerate(progress):
            if p < 0.4:  # Beach to trailhead (gentle rise)
                alts[i] = alt_beach + (alt_trailhead - alt_beach) * (p / 0.4)
            else:  # Up Mineral Springs Trail (steady climb)
                segment_p = (p - 0.4) / 0.6
                alts[i] = alt_trailhead + (alt_wildcat - alt_trailhead) * segment_p
        
        alts += 3 * np.sin(progress * 8) + np.random.normal(0, 1.5, n_points)
        
        # Temperature: slightly cooler as you climb, warmer at lake
        temps = 19.0 - 1.5 * progress + 0.5 * np.sin(progress * 5) + np.random.normal(0, 0.3, n_points)
        
        # Humidity: VERY HIGH at lake beach (~80%), drops as you climb trail (~55%)
        # Stays humid around the lake, then drops on exposed hillside
        humids = np.zeros(n_points)
        for i, p in enumerate(progress):
            if p < 0.3:  # Around lake (very humid)
                humids[i] = 80 - 5 * p
            else:  # Climbing trail (gradually drying)
                segment_p = (p - 0.3) / 0.7
                humids[i] = 75 - 20 * segment_p
        
        humids += 2 * np.cos(progress * 4) + np.random.normal(0, 1.2, n_points)
        
        # Pressure: decreases with altitude
        press = 1013 - 1.5 * progress + 0.8 * np.sin(progress * 3) + np.random.normal(0, 0.4, n_points)
        
        # Gas/VOC: Higher near humid lake, lower on drier hillside trail
        gas = 65000 - 15000 * (progress ** 1.3) + 2000 * np.sin(progress * 6) + np.random.normal(0, 500, n_points)
        
        self.data = pd.DataFrame({
            'timestamp': times,
            'latitude': lats,
            'longitude': lons,
            'altitude': alts,
            'temperature': temps,
            'humidity': humids,
            'pressure': press,
            'gas': gas
        })
        
        # Generate historical comparison data (3 previous hikes in similar areas)
        self._generate_historical_data()
        
        # Perform terrain analysis
        if self.terrain_analyzer:
            self.data, self.terrain_profiles = self.terrain_analyzer.analyze_terrain_patterns(self.data)
        
        self.update_map()
        self.update_graph()
        self.update_statistics()
        self.update_forage_analysis()
    
    def _generate_historical_data(self):
        """Generate 3 historical hikes for comparison"""
        self.historical_data = []
        
        # Historical Hike 1: Similar route, 2 weeks ago, slightly drier
        hist1 = self._generate_historical_hike(
            name="Lake Anza Loop (Sept 23)",
            date_offset=-14,
            humidity_offset=-5,
            temp_offset=+2,
            seed=100
        )
        self.historical_data.append(hist1)
        
        # Historical Hike 2: Wildcat Peak route, 1 month ago, wetter
        hist2 = self._generate_historical_hike(
            name="Wildcat Peak Trail (Sept 7)",
            date_offset=-30,
            humidity_offset=+8,
            temp_offset=-1,
            seed=200,
            route_variation=0.0015  # Different path
        )
        self.historical_data.append(hist2)
        
        # Historical Hike 3: Inspiration Point, 2 months ago, similar conditions
        hist3 = self._generate_historical_hike(
            name="Inspiration Point (Aug 7)",
            date_offset=-60,
            humidity_offset=+1,
            temp_offset=+3,
            seed=300,
            route_variation=0.002
        )
        self.historical_data.append(hist3)
    
    def _generate_historical_hike(self, name, date_offset, humidity_offset, temp_offset, seed, route_variation=0):
        """Generate a single historical hike with variations"""
        np.random.seed(seed)
        n_points = 60
        
        from datetime import timedelta
        base_date = datetime(2025, 10, 7, 10, 0, 0) + timedelta(days=date_offset)
        times = pd.date_range(start=base_date, periods=n_points, freq='1s')
        progress = np.linspace(0, 1, n_points)
        
        # Similar route with variation
        lat_beach = 37.8964 + route_variation
        lat_east_lake = 37.8972 + route_variation
        lat_trailhead = 37.8980 + route_variation
        lat_wildcat = 37.9010 + route_variation
        
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
        
        lon_beach = -122.2445 - route_variation
        lon_east_lake = -122.2435 - route_variation
        lon_trailhead = -122.2430 - route_variation
        lon_wildcat = -122.2405 - route_variation
        
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
        
        temps = (19.0 + temp_offset) - 1.5 * progress + 0.5 * np.sin(progress * 5) + np.random.normal(0, 0.3, n_points)
        
        humids = np.zeros(n_points)
        for i, p in enumerate(progress):
            if p < 0.3:
                humids[i] = (80 + humidity_offset) - 5 * p
            else:
                segment_p = (p - 0.3) / 0.7
                humids[i] = (75 + humidity_offset) - 20 * segment_p
        
        humids += 2 * np.cos(progress * 4) + np.random.normal(0, 1.2, n_points)
        
        press = 1013 - 1.5 * progress + 0.8 * np.sin(progress * 3) + np.random.normal(0, 0.4, n_points)
        gas = 65000 - 15000 * (progress ** 1.3) + 2000 * np.sin(progress * 6) + np.random.normal(0, 500, n_points)
        
        return pd.DataFrame({
            'name': [name] * n_points,
            'timestamp': times,
            'latitude': lats,
            'longitude': lons,
            'altitude': alts,
            'temperature': temps,
            'humidity': humids,
            'pressure': press,
            'gas': gas
        })
    
    def load_csv_data(self):
        """Load real CSV data from log files"""
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(
            self, "Select CSV Log Files", "", "CSV Files (*.csv)"
        )
        
        if not file_paths:
            return
        
        try:
            all_data = []
            for file_path in file_paths:
                df = pd.read_csv(file_path, comment='#')
                all_data.append(df)
            
            self.data = pd.concat(all_data, ignore_index=True)
            self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
            self.data = self.data.sort_values('timestamp')
            self.data = self.data.drop_duplicates(subset='timestamp', keep='first')
            
            # Filter out rows without GPS
            self.data = self.data[self.data['latitude'].notna() & self.data['longitude'].notna()]
            
            self.demo_mode = False
            self.status_label.setText(f"⬢ DATA UPLINK COMPLETE • {len(self.data)} POINTS • {len(file_paths)} FILES")
            
            self.update_map()
            self.update_graph()
            self.update_statistics()
            self.update_forage_analysis()
            
        except Exception as e:
            self.status_label.setText(f"⚠️ ERROR • UPLINK FAILED: {e}")
    
    def load_all_historical_logs(self):
        """Load all historical log files from the current directory for aggregate analysis"""
        try:
            # Find all rake_log CSV files in current directory
            log_files = glob.glob('rake_log_*.csv')
            
            if not log_files:
                self.status_label.setText("⚠️ NO LOG FILES FOUND • Generate them first")
                return
            
            self.status_label.setText(f"⚙️ LOADING {len(log_files)} LOG FILES...")
            
            # Store each trail as a separate dataset for colored display
            self.trail_datasets = []
            all_data = []
            
            for file_path in sorted(log_files):
                df = pd.read_csv(file_path, comment='#')
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                # Extract trail name from filename
                trail_name = file_path.replace('rake_log_', '').replace('.csv', '')
                df['trail_name'] = trail_name
                
                # Filter out rows without GPS
                df = df[df['latitude'].notna() & df['longitude'].notna()]
                
                if len(df) > 0:
                    self.trail_datasets.append({
                        'name': trail_name,
                        'data': df,
                        'color': self.get_trail_color(len(self.trail_datasets))
                    })
                    all_data.append(df)
            
            if not all_data:
                self.status_label.setText("⚠️ NO VALID DATA • Check log files")
                return
            
            # Combine all data
            self.data = pd.concat(all_data, ignore_index=True)
            self.data = self.data.sort_values('timestamp')
            
            self.demo_mode = False
            total_points = len(self.data)
            total_trails = len(self.trail_datasets)
            
            self.status_label.setText(
                f"⬢ AGGREGATE LOADED • {total_trails} TRAILS • {total_points} POINTS • "
                f"🌍 TERRAIN ANALYSIS ACTIVE"
            )
            
            # Update all views with aggregate data
            self.update_map_with_multiple_trails()
            self.update_graph()
            self.update_statistics()
            self.update_forage_analysis()
            
        except Exception as e:
            self.status_label.setText(f"⚠️ ERROR • LOADING FAILED: {e}")
            print(f"Error loading logs: {e}")
            import traceback
            traceback.print_exc()
    
    def get_trail_color(self, index):
        """Get a distinct color for each trail"""
        colors = [
            '#FF00FF',  # Magenta
            '#00FFFF',  # Cyan
            '#FFFF00',  # Yellow
            '#FF6600',  # Orange
            '#00FF00',  # Green
            '#FF0099',  # Pink
            '#0099FF',  # Blue
            '#99FF00',  # Lime
            '#FF3366',  # Red-pink
            '#66FF99',  # Mint
            '#9933FF',  # Purple
            '#FFCC00',  # Gold
        ]
        return colors[index % len(colors)]
    
    def update_map_with_multiple_trails(self):
        """Create map showing all trails with different colors and aggregate predictions"""
        if not hasattr(self, 'trail_datasets') or len(self.trail_datasets) == 0:
            self.update_map()  # Fall back to regular map
            return
        
        # Calculate center from all data
        center_lat = self.data['latitude'].mean()
        center_lon = self.data['longitude'].mean()
        
        # Create map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=14,  # Zoom out to see all trails
            tiles='OpenTopoMap',
            control_scale=True
        )
        
        # Add alternative tile layers
        folium.TileLayer('OpenStreetMap').add_to(m)
        folium.TileLayer(
            tiles='https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg',
            attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.',
            name='Terrain',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Add each trail as a separate layer
        for trail_info in self.trail_datasets:
            trail_name = trail_info['name']
            trail_data = trail_info['data']
            trail_color = trail_info['color']
            
            # Create feature group for this trail
            trail_layer = folium.FeatureGroup(name=f"🥾 {trail_name}", show=True)
            
            # Add path line for trail
            points = list(zip(trail_data['latitude'], trail_data['longitude']))
            folium.PolyLine(
                points,
                color=trail_color,
                weight=3,
                opacity=0.7,
                popup=f"<b>{trail_name}</b><br>{len(trail_data)} data points"
            ).add_to(trail_layer)
            
            # Add start/end markers for each trail
            first = trail_data.iloc[0]
            last = trail_data.iloc[-1]
            
            folium.CircleMarker(
                [first['latitude'], first['longitude']],
                radius=8,
                color=trail_color,
                fill=True,
                fillColor=trail_color,
                fillOpacity=0.8,
                popup=f"<b>START:</b> {trail_name}<br>Alt: {first['altitude']:.0f}m<br>Humid: {first['humidity']:.1f}%"
            ).add_to(trail_layer)
            
            folium.CircleMarker(
                [last['latitude'], last['longitude']],
                radius=8,
                color=trail_color,
                fill=True,
                fillColor='white',
                fillOpacity=0.6,
                popup=f"<b>END:</b> {trail_name}<br>Alt: {last['altitude']:.0f}m<br>Humid: {last['humidity']:.1f}%"
            ).add_to(trail_layer)
            
            trail_layer.add_to(m)
        
        # Add aggregate bioforage prediction zones using ALL data
        self.add_forage_prediction_zones(m)
        
        # Add aggregate heat map layer showing data density
        heat_data = [[row['latitude'], row['longitude']] for _, row in self.data.iterrows()]
        plugins.HeatMap(heat_data, name='🔥 Data Density Heatmap', show=False, radius=15, blur=20).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Save and display
        map_file = '/tmp/tilden_aggregate_map.html'
        m.save(map_file)
        self.map_view.setUrl(QUrl.fromLocalFile(map_file))
    
    def update_map(self):
        """Create and display interactive map"""
        if self.data is None or len(self.data) == 0:
            return
        
        # Center map on data
        center_lat = self.data['latitude'].mean()
        center_lon = self.data['longitude'].mean()
        
        # Create map with topographic tiles
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=16,  # Closer zoom for trail detail
            tiles='OpenTopoMap',  # Topographic map
            control_scale=True
        )
        
        # Add alternative tile layers
        folium.TileLayer('OpenStreetMap').add_to(m)
        folium.TileLayer(
            tiles='https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg',
            attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.',
            name='Terrain',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Create color maps for temperature
        temps = self.data['temperature'].values
        temp_min, temp_max = temps.min(), temps.max()
        
        # Add markers for each point
        for idx, row in self.data.iterrows():
            # Color based on humidity (key differentiator: Lake Anza = high, Inspiration Point = low)
            humids = self.data['humidity'].values
            humid_min, humid_max = humids.min(), humids.max()
            humid_norm = (row['humidity'] - humid_min) / (humid_max - humid_min) if humid_max > humid_min else 0.5
            color = self.get_humidity_color(humid_norm)
            
            # Determine location description based on trail position
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
        points = list(zip(self.data['latitude'], self.data['longitude']))
        folium.PolyLine(
            points,
            color='blue',
            weight=2,
            opacity=0.5
        ).add_to(m)
        
        # Add start and end markers with location names
        if len(self.data) > 0:
            first = self.data.iloc[0]
            last = self.data.iloc[-1]
            
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
        
        # Add bioforage prediction zones using terrain analysis
        self.add_forage_prediction_zones(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Save and display map
        map_file = '/tmp/tilden_data_map.html'
        m.save(map_file)
        self.map_view.setUrl(QUrl.fromLocalFile(map_file))
    
    def get_color_from_value(self, normalized_value):
        """Convert normalized value (0-1) to color (blue to red)"""
        if normalized_value < 0.25:
            return 'blue'
        elif normalized_value < 0.5:
            return 'green'
        elif normalized_value < 0.75:
            return 'orange'
        else:
            return 'red'
    
    def get_humidity_color(self, normalized_humidity):
        """Convert humidity (0=dry to 1=humid) to color (blue=humid, orange=dry)"""
        # High humidity = blue (Lake Anza), Low humidity = orange/red (Inspiration Point)
        if normalized_humidity > 0.75:
            return 'darkblue'  # Very humid (Lake Anza)
        elif normalized_humidity > 0.5:
            return 'blue'  # Humid (Gorge)
        elif normalized_humidity > 0.25:
            return 'lightblue'  # Moderate (Mid-trail)
        else:
            return 'orange'  # Dry (Inspiration Point)
    
    def update_graph(self):
        """Update the graph view"""
        if self.data is None:
            return
        
        param = self.param_combo.currentText()
        param_map = {
            'Temperature': 'temperature',
            'Humidity': 'humidity',
            'Pressure': 'pressure',
            'Gas/VOC': 'gas'
        }
        
        column = param_map[param]
        
        self.figure.clear()
        ax = self.figure.add_subplot(111, facecolor='#051515')
        
        # Cyberpunk neon colors for different parameters
        color_map = {
            'temperature': '#ff3366',  # Hot pink
            'humidity': '#00ffcc',     # Cyan
            'pressure': '#ffaa00',     # Orange
            'gas': '#00ff88'           # Green
        }
        
        ax.plot(self.data['timestamp'], self.data[column], 
                color=color_map.get(column, '#00ffaa'), 
                linewidth=2, alpha=0.9, linestyle='-')
        
        # Add glow effect
        ax.plot(self.data['timestamp'], self.data[column], 
                color=color_map.get(column, '#00ffaa'), 
                linewidth=6, alpha=0.2)
        
        ax.set_xlabel('⏱ TIME', fontsize=11, fontweight='bold', color='#88ffcc', family='monospace')
        
        if column == 'temperature':
            ax.set_ylabel('🌡 TEMP (°C)', fontsize=11, fontweight='bold', color='#ff3366', family='monospace')
        elif column == 'humidity':
            ax.set_ylabel('💧 HUMIDITY (%)', fontsize=11, fontweight='bold', color='#00ffcc', family='monospace')
        elif column == 'pressure':
            ax.set_ylabel('⚡ PRESSURE (hPa)', fontsize=11, fontweight='bold', color='#ffaa00', family='monospace')
        elif column == 'gas':
            ax.set_ylabel('🌿 VOC (Ω)', fontsize=11, fontweight='bold', color='#00ff88', family='monospace')
        
        ax.set_title(f'⬢ {param.upper()} DATASTREAM ⬢', fontsize=13, fontweight='bold', 
                     color='#00ffaa', family='monospace', pad=15)
        ax.grid(True, alpha=0.15, color='#00ff88', linestyle='--')
        ax.tick_params(colors='#88ffcc', labelsize=9)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, color='#88ffcc')
        
        # Cyberpunk frame
        for spine in ax.spines.values():
            spine.set_edgecolor('#00ff88')
            spine.set_linewidth(2)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def update_statistics(self):
        """Update statistics view"""
        if self.data is None:
            return
        
        stats_text = "╔" + "═"*60 + "╗\n"
        stats_text += "║  ⬢ ENVIRONMENTAL DATA ANALYTICS ⬢" + " "*25 + "║\n"
        stats_text += "╚" + "═"*60 + "╝\n\n"
        
        stats_text += f"⚡ TOTAL DATA POINTS: {len(self.data)}\n"
        stats_text += f"⏱ TIME RANGE: {self.data['timestamp'].min()} ➜ {self.data['timestamp'].max()}\n"
        stats_text += f"⏳ DURATION: {self.data['timestamp'].max() - self.data['timestamp'].min()}\n\n"
        
        stats_text += "┌" + "─"*60 + "┐\n"
        stats_text += "│  ⚡ SENSOR DATASTREAM" + " "*38 + "│\n"
        stats_text += "└" + "─"*60 + "┘\n\n"
        
        icon_map = {
            'temperature': '🌡',
            'humidity': '💧',
            'pressure': '⚡',
            'gas': '🌿'
        }
        
        for col in ['temperature', 'humidity', 'pressure', 'gas']:
            icon = icon_map.get(col, '⬢')
            stats_text += f"\n{icon} {col.upper()}:\n"
            stats_text += f"  ├─ Mean:   {self.data[col].mean():.2f}\n"
            stats_text += f"  ├─ Median: {self.data[col].median():.2f}\n"
            stats_text += f"  ├─ Min:    {self.data[col].min():.2f}\n"
            stats_text += f"  ├─ Max:    {self.data[col].max():.2f}\n"
            stats_text += f"  └─ StdDev: {self.data[col].std():.2f}\n"
        
        stats_text += "\n┌" + "─"*60 + "┐\n"
        stats_text += "│  📍 GPS TELEMETRY" + " "*41 + "│\n"
        stats_text += "└" + "─"*60 + "┘\n\n"
        
        lat_range = self.data['latitude'].max() - self.data['latitude'].min()
        lon_range = self.data['longitude'].max() - self.data['longitude'].min()
        
        stats_text += f"Latitude Range:  {self.data['latitude'].min():.6f} to {self.data['latitude'].max():.6f}\n"
        stats_text += f"                 ({lat_range:.6f}° = ~{lat_range * 111:.1f} km)\n\n"
        stats_text += f"Longitude Range: {self.data['longitude'].min():.6f} to {self.data['longitude'].max():.6f}\n"
        stats_text += f"                 ({lon_range:.6f}° = ~{lon_range * 111:.1f} km)\n\n"
        stats_text += f"Altitude Range:  {self.data['altitude'].min():.1f}m to {self.data['altitude'].max():.1f}m\n\n"
        
        # Add Fukuoka-style terrain analysis
        if self.terrain_analyzer and len(self.terrain_profiles) > 0:
            stats_text += "\n" + "═"*62 + "\n"
            stats_text += self.terrain_analyzer.generate_fukuoka_insights(
                self.data, 
                self.terrain_profiles,
                self.historical_data if len(self.historical_data) > 0 else None
            )
            stats_text += "\n" + "═"*62 + "\n"
        
        self.stats_text.setText(stats_text)
    
    def update_forage_analysis(self):
        """Analyze trail conditions for native East Bay forage seed dispersal"""
        if self.data is None:
            return
        
        # Define 5 native East Bay forage species suitable for cattle grazing
        forage_species = {
            'Purple Needlegrass': {
                'scientific': 'Stipa pulchra',
                'ideal_humidity': (45, 60),  # Prefers drier conditions
                'ideal_altitude': (250, 400),
                'manure_benefit': 'moderate',  # Benefits from some manure
                'description': 'CA state grass, drought-tolerant, deep roots',
                'germination_temp': (15, 25),
                'seeds_per_lb': 150000
            },
            'Blue Wild Rye': {
                'scientific': 'Elymus glaucus',
                'ideal_humidity': (55, 75),  # Tolerates more moisture
                'ideal_altitude': (200, 350),
                'manure_benefit': 'high',  # Thrives with manure nutrients
                'description': 'Bunchgrass, excellent forage quality',
                'germination_temp': (10, 20),
                'seeds_per_lb': 110000
            },
            'California Brome': {
                'scientific': 'Bromus carinatus',
                'ideal_humidity': (50, 70),
                'ideal_altitude': (230, 380),
                'manure_benefit': 'high',  # Nitrogen-loving
                'description': 'Quick establishment, palatable to cattle',
                'germination_temp': (12, 22),
                'seeds_per_lb': 140000
            },
            'Foothill Needlegrass': {
                'scientific': 'Stipa lepida',
                'ideal_humidity': (40, 55),  # Very drought-tolerant
                'ideal_altitude': (280, 450),
                'manure_benefit': 'low',  # Prefers lower nutrients
                'description': 'Exceptional drought resistance',
                'germination_temp': (15, 25),
                'seeds_per_lb': 160000
            },
            'California Oatgrass': {
                'scientific': 'Danthonia californica',
                'ideal_humidity': (60, 80),  # Moisture-loving
                'ideal_altitude': (200, 300),
                'manure_benefit': 'moderate',
                'description': 'Shade tolerant, near water sources',
                'germination_temp': (10, 18),
                'seeds_per_lb': 180000
            }
        }
        
        # Calculate suitability scores for each point
        results = []
        for idx, row in self.data.iterrows():
            point_analysis = {
                'index': idx,
                'location': f"{row['latitude']:.5f}, {row['longitude']:.5f}",
                'altitude': row['altitude'],
                'humidity': row['humidity'],
                'temperature': row['temperature'],
                'gas': row['gas'],  # Higher gas may indicate manure presence
                'timestamp': row['timestamp'],
                'species_scores': {}
            }
            
            # Score each species for this location
            for species, specs in forage_species.items():
                score = 0
                factors = []
                
                # Humidity match (0-40 points)
                humid_min, humid_max = specs['ideal_humidity']
                if humid_min <= row['humidity'] <= humid_max:
                    humid_score = 40
                    factors.append(f"✓ Humidity ideal")
                else:
                    humid_diff = min(abs(row['humidity'] - humid_min), abs(row['humidity'] - humid_max))
                    humid_score = max(0, 40 - humid_diff * 2)
                    factors.append(f"⚠ Humidity {humid_diff:.0f}% off ideal")
                score += humid_score
                
                # Altitude match (0-30 points)
                alt_min, alt_max = specs['ideal_altitude']
                if alt_min <= row['altitude'] <= alt_max:
                    alt_score = 30
                    factors.append(f"✓ Elevation ideal")
                else:
                    alt_diff = min(abs(row['altitude'] - alt_min), abs(row['altitude'] - alt_max))
                    alt_score = max(0, 30 - alt_diff * 0.3)
                    factors.append(f"⚠ Elevation {alt_diff:.0f}m off")
                score += alt_score
                
                # Temperature match (0-20 points)
                temp_min, temp_max = specs['germination_temp']
                if temp_min <= row['temperature'] <= temp_max:
                    temp_score = 20
                    factors.append(f"✓ Temp good for germination")
                else:
                    temp_diff = min(abs(row['temperature'] - temp_min), abs(row['temperature'] - temp_max))
                    temp_score = max(0, 20 - temp_diff * 2)
                    if temp_score < 10:
                        factors.append(f"✗ Temp too far from germination range")
                score += temp_score
                
                # Manure/nutrient benefit (0-10 points)
                # Higher gas readings may indicate cattle presence
                manure_indicator = (row['gas'] - self.data['gas'].min()) / (self.data['gas'].max() - self.data['gas'].min())
                if specs['manure_benefit'] == 'high':
                    manure_score = manure_indicator * 10
                    if manure_indicator > 0.6:
                        factors.append(f"✓ High nutrient/manure area")
                elif specs['manure_benefit'] == 'low':
                    manure_score = (1 - manure_indicator) * 10
                    if manure_indicator < 0.4:
                        factors.append(f"✓ Low nutrient preferred")
                else:  # moderate
                    manure_score = 5
                score += manure_score
                
                point_analysis['species_scores'][species] = {
                    'score': score,
                    'factors': factors
                }
            
            results.append(point_analysis)
        
        # Generate recommendations - only disperse seeds in top 15% of suitable locations
        forage_text = "="*80 + "\n"
        forage_text += "NATIVE EAST BAY FORAGE SEED DISPERSAL ANALYSIS\n"
        forage_text += "Lake Anza Beach → Mineral Springs Trail → Wildcat Canyon Road\n"
        forage_text += "="*80 + "\n\n"
        
        forage_text += "CATTLE-SUITABLE NATIVE SPECIES:\n"
        forage_text += "-"*80 + "\n"
        for species, specs in forage_species.items():
            forage_text += f"\n🌱 {species} ({specs['scientific']})\n"
            forage_text += f"   {specs['description']}\n"
            forage_text += f"   Ideal: {specs['ideal_humidity'][0]}-{specs['ideal_humidity'][1]}% humidity, "
            forage_text += f"{specs['ideal_altitude'][0]}-{specs['ideal_altitude'][1]}m elevation\n"
        
        forage_text += "\n\n" + "="*80 + "\n"
        forage_text += "SEED DISPERSAL RECOMMENDATIONS (Top 15% of Trail)\n"
        forage_text += "="*80 + "\n\n"
        
        # For each species, find best locations and recommend dispersal
        dispersal_plan = {}
        for species in forage_species.keys():
            # Get scores for this species across all points
            scores = [(r['index'], r['species_scores'][species]['score'], r) for r in results]
            scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select top 15% of trail
            n_disperse = max(1, int(len(scores) * 0.15))
            top_locations = scores[:n_disperse]
            
            # Only recommend if average score is above 60 (conservative threshold)
            avg_score = np.mean([s[1] for s in top_locations])
            
            if avg_score >= 60:
                dispersal_plan[species] = {
                    'locations': top_locations,
                    'avg_score': avg_score,
                    'recommended': True
                }
            else:
                dispersal_plan[species] = {
                    'locations': [],
                    'avg_score': avg_score,
                    'recommended': False,
                    'reason': 'Conditions not optimal enough for conservative dispersal'
                }
        
        # Print recommendations
        dispersed_count = 0
        for species, plan in dispersal_plan.items():
            forage_text += f"\n{'='*80}\n"
            forage_text += f"🌾 {species} ({forage_species[species]['scientific']})\n"
            forage_text += f"{'='*80}\n"
            
            if plan['recommended']:
                dispersed_count += 1
                forage_text += f"✅ RECOMMENDED FOR DISPERSAL\n"
                forage_text += f"   Average Suitability Score: {plan['avg_score']:.1f}/100\n"
                forage_text += f"   Disperse at {len(plan['locations'])} locations ({len(plan['locations'])/len(results)*100:.1f}% of trail)\n\n"
                
                forage_text += "   Top Dispersal Locations:\n"
                for i, (idx, score, point) in enumerate(plan['locations'][:5], 1):  # Show top 5
                    forage_text += f"\n   Location {i} (Score: {score:.1f}/100):\n"
                    forage_text += f"      Position: {point['location']}\n"
                    forage_text += f"      Altitude: {point['altitude']:.0f}m, Humidity: {point['humidity']:.1f}%\n"
                    forage_text += f"      Temp: {point['temperature']:.1f}°C, VOC: {point['gas']:.0f}Ω\n"
                    for factor in point['species_scores'][species]['factors'][:3]:
                        forage_text += f"      {factor}\n"
                
                # Germination likelihood
                if plan['avg_score'] >= 85:
                    forage_text += f"\n   🟢 Germination Likelihood: EXCELLENT (85-95%)\n"
                    forage_text += f"   🟢 Overall Success Probability: VERY HIGH\n"
                elif plan['avg_score'] >= 75:
                    forage_text += f"\n   🟡 Germination Likelihood: GOOD (70-85%)\n"
                    forage_text += f"   🟡 Overall Success Probability: HIGH\n"
                else:
                    forage_text += f"\n   🟠 Germination Likelihood: MODERATE (55-70%)\n"
                    forage_text += f"   🟠 Overall Success Probability: MODERATE\n"
            else:
                forage_text += f"❌ NOT RECOMMENDED\n"
                forage_text += f"   Average Suitability Score: {plan['avg_score']:.1f}/100 (threshold: 60)\n"
                forage_text += f"   Reason: {plan['reason']}\n"
                forage_text += f"   💡 Consider: May succeed in specific microclimates, but conservative dispersal\n"
                forage_text += f"              suggests waiting for more optimal conditions or different locations.\n"
        
        forage_text += f"\n\n{'='*80}\n"
        forage_text += f"SUMMARY\n"
        forage_text += f"{'='*80}\n"
        forage_text += f"Species Recommended for Dispersal: {dispersed_count}/5\n"
        forage_text += f"Conservative Strategy: Only seed where conditions are optimal\n"
        forage_text += f"Trail Coverage: ~15% (concentrated in best microclimates)\n\n"
        forage_text += f"🐄 Note: Manure presence (indicated by VOC levels) can improve germination\n"
        forage_text += f"   for nitrogen-loving species like Blue Wild Rye and California Brome.\n"
        
        self.forage_text.setText(forage_text)
    
    def add_forage_prediction_zones(self, folium_map):
        """Add bioforage prediction zones to the map based on terrain analysis"""
        if self.data is None or len(self.data) < 10:
            return
        
        # Define native East Bay forage species with their optimal conditions
        forage_species = {
            'Purple Needlegrass': {
                'humidity_range': (40, 60),
                'altitude_range': (200, 450),
                'voc_preference': 'low',  # Prefers well-drained, less organic soil
                'color': '#9B59B6',  # Purple
                'icon': '🌾'
            },
            'California Oatgrass': {
                'humidity_range': (50, 70),
                'altitude_range': (150, 400),
                'voc_preference': 'medium',
                'color': '#F39C12',  # Orange-gold
                'icon': '🌿'
            },
            'Creeping Wildrye': {
                'humidity_range': (60, 80),
                'altitude_range': (200, 350),
                'voc_preference': 'high',  # Tolerates rich soil near water
                'color': '#3498DB',  # Blue
                'icon': '🌱'
            },
            'Blue Wildrye': {
                'humidity_range': (35, 55),
                'altitude_range': (250, 500),
                'voc_preference': 'low',  # Dry hillsides
                'color': '#2ECC71',  # Green
                'icon': '🍃'
            },
            'California Brome': {
                'humidity_range': (45, 65),
                'altitude_range': (180, 380),
                'voc_preference': 'medium',
                'color': '#E67E22',  # Burnt orange
                'icon': '🌾'
            }
        }
        
        # Create a feature group for forage predictions (can be toggled on/off)
        forage_layer = folium.FeatureGroup(name='🌱 Forage Prediction Zones', show=True)
        
        # Analyze terrain and create prediction zones for each species
        for species_name, prefs in forage_species.items():
            optimal_points = []
            
            # Find points that match this species' preferences
            for idx, row in self.data.iterrows():
                # Check humidity match
                humidity_score = 0
                if prefs['humidity_range'][0] <= row['humidity'] <= prefs['humidity_range'][1]:
                    humidity_score = 1.0
                elif abs(row['humidity'] - np.mean(prefs['humidity_range'])) < 15:
                    humidity_score = 0.5
                
                # Check altitude match
                altitude_score = 0
                if prefs['altitude_range'][0] <= row['altitude'] <= prefs['altitude_range'][1]:
                    altitude_score = 1.0
                elif abs(row['altitude'] - np.mean(prefs['altitude_range'])) < 50:
                    altitude_score = 0.5
                
                # Check VOC/organic matter preference
                voc_score = 0
                if prefs['voc_preference'] == 'high' and row['gas'] > 55000:
                    voc_score = 1.0
                elif prefs['voc_preference'] == 'medium' and 50000 < row['gas'] < 60000:
                    voc_score = 1.0
                elif prefs['voc_preference'] == 'low' and row['gas'] < 52000:
                    voc_score = 1.0
                else:
                    voc_score = 0.3
                
                # Calculate overall suitability (need high scores in all areas)
                suitability = (humidity_score + altitude_score + voc_score) / 3.0
                
                if suitability > 0.65:  # Threshold for "good" conditions
                    optimal_points.append({
                        'lat': row['latitude'],
                        'lon': row['longitude'],
                        'suitability': suitability,
                        'altitude': row['altitude'],
                        'humidity': row['humidity'],
                        'gas': row['gas']
                    })
            
            # Only add zones if we found suitable points (15% of trail as requested)
            if len(optimal_points) >= 3:
                # Sort by suitability and take top 15% of trail points
                optimal_points.sort(key=lambda x: x['suitability'], reverse=True)
                top_points = optimal_points[:max(3, len(optimal_points) // 2)]
                
                # Create circles around optimal zones
                for point in top_points:
                    # Size of zone based on suitability
                    radius = 15 + (point['suitability'] * 25)  # 15-40 meter radius
                    
                    popup_html = f"""
                    <div style='font-family: monospace; background: #000; color: {prefs['color']}; padding: 10px;'>
                    <b>{prefs['icon']} {species_name}</b><br>
                    <hr style='border-color: {prefs['color']};'>
                    <b>SUITABILITY:</b> {point['suitability']*100:.0f}%<br>
                    <b>Altitude:</b> {point['altitude']:.0f}m<br>
                    <b>Humidity:</b> {point['humidity']:.1f}%<br>
                    <b>Soil Organic:</b> {point['gas']:.0f}Ω<br>
                    <hr style='border-color: {prefs['color']};'>
                    <small>🐄 GRAZING RECOMMENDATION:</small><br>
                    <small>Seed here for optimal germination</small>
                    </div>
                    """
                    
                    folium.Circle(
                        location=[point['lat'], point['lon']],
                        radius=radius,
                        popup=folium.Popup(popup_html, max_width=300),
                        color=prefs['color'],
                        fill=True,
                        fillColor=prefs['color'],
                        fillOpacity=0.15,
                        weight=2,
                        opacity=0.6
                    ).add_to(forage_layer)
                    
                    # Add small marker at center
                    folium.CircleMarker(
                        location=[point['lat'], point['lon']],
                        radius=4,
                        color=prefs['color'],
                        fill=True,
                        fillColor=prefs['color'],
                        fillOpacity=0.8,
                        popup=folium.Popup(f"{prefs['icon']} {species_name}", max_width=150)
                    ).add_to(forage_layer)
        
        # Add the forage layer to the map
        forage_layer.add_to(folium_map)
        
        # Use terrain analysis to predict similar microclimates beyond the trail
        if TERRAIN_ANALYSIS_AVAILABLE and hasattr(self, 'terrain_analyzer'):
            self.add_terrain_extrapolation_zones(folium_map, forage_species)
    
    def add_terrain_extrapolation_zones(self, folium_map, forage_species):
        """Extrapolate forage predictions to similar terrain beyond surveyed trail"""
        # Create prediction layer for extrapolated zones
        extrapolation_layer = folium.FeatureGroup(name='🗺️ Terrain-Based Predictions', show=False)
        
        # Get bounds of current data
        lat_min, lat_max = self.data['latitude'].min(), self.data['latitude'].max()
        lon_min, lon_max = self.data['longitude'].min(), self.data['longitude'].max()
        
        # Expand search area by 50% in each direction
        lat_range = lat_max - lat_min
        lon_range = lon_max - lon_min
        
        expanded_lat_min = lat_min - lat_range * 0.5
        expanded_lat_max = lat_max + lat_range * 0.5
        expanded_lon_min = lon_min - lon_range * 0.5
        expanded_lon_max = lon_max + lon_range * 0.5
        
        # Create a grid of prediction points across the expanded area
        grid_resolution = 20  # Number of points per dimension
        lat_grid = np.linspace(expanded_lat_min, expanded_lat_max, grid_resolution)
        lon_grid = np.linspace(expanded_lon_min, expanded_lon_max, grid_resolution)
        
        # For each grid point, predict microclimate based on terrain similarity
        terrain_clusters = {}
        
        # Cluster surveyed data by altitude bands (50m bands)
        for idx, row in self.data.iterrows():
            alt_band = int(row['altitude'] / 50) * 50
            if alt_band not in terrain_clusters:
                terrain_clusters[alt_band] = {
                    'humidity_avg': [],
                    'gas_avg': [],
                    'count': 0
                }
            terrain_clusters[alt_band]['humidity_avg'].append(row['humidity'])
            terrain_clusters[alt_band]['gas_avg'].append(row['gas'])
            terrain_clusters[alt_band]['count'] += 1
        
        # Calculate averages for each altitude band
        for band in terrain_clusters:
            terrain_clusters[band]['humidity_avg'] = np.mean(terrain_clusters[band]['humidity_avg'])
            terrain_clusters[band]['gas_avg'] = np.mean(terrain_clusters[band]['gas_avg'])
        
        # Now predict zones for each species in unexplored areas
        prediction_points = []
        
        for i, lat in enumerate(lat_grid[::3]):  # Sample every 3rd point to reduce clutter
            for j, lon in enumerate(lon_grid[::3]):
                # Estimate altitude for this point (simple interpolation from nearby surveyed points)
                distances = np.sqrt((self.data['latitude'] - lat)**2 + (self.data['longitude'] - lon)**2)
                nearest_idx = distances.argmin()
                estimated_altitude = self.data.iloc[nearest_idx]['altitude']
                
                # Find matching terrain cluster
                alt_band = int(estimated_altitude / 50) * 50
                if alt_band in terrain_clusters:
                    predicted_humidity = terrain_clusters[alt_band]['humidity_avg']
                    predicted_gas = terrain_clusters[alt_band]['gas_avg']
                    
                    # Check which species would thrive here
                    best_species = None
                    best_score = 0
                    
                    for species_name, prefs in forage_species.items():
                        # Calculate suitability
                        humidity_match = prefs['humidity_range'][0] <= predicted_humidity <= prefs['humidity_range'][1]
                        altitude_match = prefs['altitude_range'][0] <= estimated_altitude <= prefs['altitude_range'][1]
                        
                        if humidity_match and altitude_match:
                            score = 1.0 - abs(predicted_humidity - np.mean(prefs['humidity_range'])) / 30
                            if score > best_score:
                                best_score = score
                                best_species = species_name
                    
                    if best_species and best_score > 0.6:
                        prediction_points.append({
                            'lat': lat,
                            'lon': lon,
                            'species': best_species,
                            'score': best_score,
                            'altitude': estimated_altitude
                        })
        
        # Add prediction markers (subtle, small circles)
        for point in prediction_points:
            species_prefs = forage_species[point['species']]
            
            folium.CircleMarker(
                location=[point['lat'], point['lon']],
                radius=3,
                color=species_prefs['color'],
                fill=True,
                fillColor=species_prefs['color'],
                fillOpacity=0.3,
                weight=1,
                popup=folium.Popup(
                    f"<b>PREDICTED:</b> {species_prefs['icon']} {point['species']}<br>"
                    f"Est. Alt: {point['altitude']:.0f}m<br>"
                    f"Confidence: {point['score']*100:.0f}%<br>"
                    f"<small>Based on terrain similarity</small>",
                    max_width=200
                )
            ).add_to(extrapolation_layer)
        
        # Add extrapolation layer to map (hidden by default - user can toggle on)
        extrapolation_layer.add_to(folium_map)
