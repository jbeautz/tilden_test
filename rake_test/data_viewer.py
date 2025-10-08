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
        
        # Setup UI
        self.setup_ui()
        
        # Load demo data by default
        self.load_demo_data()
    
    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Top control panel
        control_panel = QHBoxLayout()
        
        self.load_btn = QPushButton("📂 Load CSV Data")
        self.load_btn.clicked.connect(self.load_csv_data)
        control_panel.addWidget(self.load_btn)
        
        self.demo_btn = QPushButton("🎮 Demo Mode")
        self.demo_btn.clicked.connect(self.load_demo_data)
        control_panel.addWidget(self.demo_btn)
        
        self.refresh_btn = QPushButton("🔄 Refresh Map")
        self.refresh_btn.clicked.connect(self.update_map)
        control_panel.addWidget(self.refresh_btn)
        
        control_panel.addStretch()
        
        self.status_label = QLabel("Status: Demo Mode")
        control_panel.addWidget(self.status_label)
        
        main_layout.addLayout(control_panel)
        
        # Tabs for different views
        self.tabs = QTabWidget()
        
        # Map Tab
        self.map_tab = QWidget()
        map_layout = QVBoxLayout(self.map_tab)
        self.map_view = QWebEngineView()
        map_layout.addWidget(self.map_view)
        self.tabs.addTab(self.map_tab, "🗺️ Map View")
        
        # Graphs Tab
        self.graphs_tab = QWidget()
        graphs_layout = QVBoxLayout(self.graphs_tab)
        
        # Graph controls
        graph_controls = QHBoxLayout()
        graph_controls.addWidget(QLabel("Parameter:"))
        self.param_combo = QComboBox()
        self.param_combo.addItems(["Temperature", "Humidity", "Pressure", "Gas/VOC"])
        self.param_combo.currentTextChanged.connect(self.update_graph)
        graph_controls.addWidget(self.param_combo)
        graph_controls.addStretch()
        graphs_layout.addLayout(graph_controls)
        
        # Matplotlib canvas
        self.figure = Figure(figsize=(12, 6))
        self.canvas = FigureCanvasQTAgg(self.figure)
        graphs_layout.addWidget(self.canvas)
        
        self.tabs.addTab(self.graphs_tab, "📊 Graphs")
        
        # Statistics Tab
        self.stats_tab = QWidget()
        stats_layout = QVBoxLayout(self.stats_tab)
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        stats_layout.addWidget(self.stats_text)
        self.tabs.addTab(self.stats_tab, "📈 Statistics")
        
        main_layout.addWidget(self.tabs)
    
    def load_demo_data(self):
        """Generate demo data for Tilden Park area"""
        self.demo_mode = True
        self.status_label.setText("Status: Demo Mode - Tilden Park Area")
        
        # Tilden Park coordinates (Berkeley Hills)
        base_lat = 37.9050
        base_lon = -122.2450
        
        # Generate 50 demo points in a walking path pattern
        np.random.seed(42)
        n_points = 50
        
        # Create a realistic walking path
        times = pd.date_range(start='2025-10-07 10:00:00', periods=n_points, freq='30S')
        
        # Simulate a meandering path
        t = np.linspace(0, 4*np.pi, n_points)
        lats = base_lat + 0.01 * np.sin(t) + np.random.normal(0, 0.001, n_points)
        lons = base_lon + 0.01 * np.cos(t) + np.random.normal(0, 0.001, n_points)
        alts = 300 + 50 * np.sin(t) + np.random.normal(0, 5, n_points)
        
        # Simulate realistic sensor data
        temps = 22 + 3 * np.sin(t/2) + np.random.normal(0, 0.5, n_points)
        humids = 65 + 10 * np.cos(t/3) + np.random.normal(0, 2, n_points)
        press = 1013 + 5 * np.sin(t/4) + np.random.normal(0, 1, n_points)
        gas = 45000 + 5000 * np.sin(t/2) + np.random.normal(0, 1000, n_points)
        
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
        
        self.update_map()
        self.update_graph()
        self.update_statistics()
    
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
            self.status_label.setText(f"Status: Loaded {len(self.data)} points from {len(file_paths)} files")
            
            self.update_map()
            self.update_graph()
            self.update_statistics()
            
        except Exception as e:
            self.status_label.setText(f"Error loading data: {e}")
    
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
            zoom_start=15,
            tiles='OpenTopoMap',  # Topographic map
            control_scale=True
        )
        
        # Add alternative tile layers
        folium.TileLayer('OpenStreetMap').add_to(m)
        folium.TileLayer('Stamen Terrain').add_to(m)
        
        # Create color maps for temperature
        temps = self.data['temperature'].values
        temp_min, temp_max = temps.min(), temps.max()
        
        # Add markers for each point
        for idx, row in self.data.iterrows():
            # Color based on temperature
            temp_norm = (row['temperature'] - temp_min) / (temp_max - temp_min) if temp_max > temp_min else 0.5
            color = self.get_color_from_value(temp_norm)
            
            popup_html = f"""
            <b>Time:</b> {row['timestamp']}<br>
            <b>Temp:</b> {row['temperature']:.1f}°C<br>
            <b>Humidity:</b> {row['humidity']:.1f}%<br>
            <b>Pressure:</b> {row['pressure']:.1f} hPa<br>
            <b>Gas:</b> {row['gas']:.0f} Ω<br>
            <b>Altitude:</b> {row['altitude']:.1f} m
            """
            
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=6,
                popup=folium.Popup(popup_html, max_width=200),
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
        
        # Add start and end markers
        if len(self.data) > 0:
            first = self.data.iloc[0]
            last = self.data.iloc[-1]
            
            folium.Marker(
                [first['latitude'], first['longitude']],
                popup='Start',
                icon=folium.Icon(color='green', icon='play')
            ).add_to(m)
            
            folium.Marker(
                [last['latitude'], last['longitude']],
                popup='End',
                icon=folium.Icon(color='red', icon='stop')
            ).add_to(m)
        
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
        ax = self.figure.add_subplot(111)
        
        ax.plot(self.data['timestamp'], self.data[column], 'b-', linewidth=1.5, alpha=0.7)
        ax.set_xlabel('Time', fontsize=12, fontweight='bold')
        
        if column == 'temperature':
            ax.set_ylabel('Temperature (°C)', fontsize=12, fontweight='bold')
        elif column == 'humidity':
            ax.set_ylabel('Humidity (%)', fontsize=12, fontweight='bold')
        elif column == 'pressure':
            ax.set_ylabel('Pressure (hPa)', fontsize=12, fontweight='bold')
        elif column == 'gas':
            ax.set_ylabel('Gas Resistance (Ω)', fontsize=12, fontweight='bold')
        
        ax.set_title(f'{param} Over Time', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def update_statistics(self):
        """Update statistics view"""
        if self.data is None:
            return
        
        stats_text = "="*60 + "\n"
        stats_text += "ENVIRONMENTAL DATA STATISTICS\n"
        stats_text += "="*60 + "\n\n"
        
        stats_text += f"Total Data Points: {len(self.data)}\n"
        stats_text += f"Time Range: {self.data['timestamp'].min()} to {self.data['timestamp'].max()}\n"
        stats_text += f"Duration: {self.data['timestamp'].max() - self.data['timestamp'].min()}\n\n"
        
        stats_text += "-"*60 + "\n"
        stats_text += "SENSOR READINGS SUMMARY\n"
        stats_text += "-"*60 + "\n\n"
        
        for col in ['temperature', 'humidity', 'pressure', 'gas']:
            stats_text += f"\n{col.upper()}:\n"
            stats_text += f"  Mean:   {self.data[col].mean():.2f}\n"
            stats_text += f"  Median: {self.data[col].median():.2f}\n"
            stats_text += f"  Min:    {self.data[col].min():.2f}\n"
            stats_text += f"  Max:    {self.data[col].max():.2f}\n"
            stats_text += f"  StdDev: {self.data[col].std():.2f}\n"
        
        stats_text += "\n" + "-"*60 + "\n"
        stats_text += "GPS DATA\n"
        stats_text += "-"*60 + "\n\n"
        
        lat_range = self.data['latitude'].max() - self.data['latitude'].min()
        lon_range = self.data['longitude'].max() - self.data['longitude'].min()
        
        stats_text += f"Latitude Range:  {self.data['latitude'].min():.6f} to {self.data['latitude'].max():.6f}\n"
        stats_text += f"                 ({lat_range:.6f}° = ~{lat_range * 111:.1f} km)\n\n"
        stats_text += f"Longitude Range: {self.data['longitude'].min():.6f} to {self.data['longitude'].max():.6f}\n"
        stats_text += f"                 ({lon_range:.6f}° = ~{lon_range * 111:.1f} km)\n\n"
        stats_text += f"Altitude Range:  {self.data['altitude'].min():.1f}m to {self.data['altitude'].max():.1f}m\n"
        
        self.stats_text.setText(stats_text)


def main():
    app = QApplication(sys.argv)
    viewer = DataViewer()
    viewer.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
