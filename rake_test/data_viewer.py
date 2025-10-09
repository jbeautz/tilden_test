#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║                  T I L D E N   D A T A   V I E W E R                 ║
║                                                                      ║
║     Environmental Sensor Analysis & Terrain Intelligence            ║
║            Fukuoka Natural Farming • Bioforage Protocol             ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import sys
import os
import pandas as pd
import folium
from folium import plugins
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QLabel, QPushButton, 
                             QFileDialog, QTextEdit, QSplitter)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont, QPalette, QColor
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from terrain_analysis import TerrainAnalyzer
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════
#                         POPPYWAVE AESTHETIC
#    Golden poppies under ultraviolet skies - moody dusk energy
# ═══════════════════════════════════════════════════════════════════

COLORS = {
    'bg': '#3B1F4E',           # Smoky violet - moody dusk
    'primary': '#FFB400',      # Electric saffron - poppy fire
    'secondary': '#67E8F9',    # Skywire cyan - cool tech shimmer
    'success': '#E1C8FF',      # Cloud lavender
    'warning': '#FF8800',      # Warm poppy-orange
    'text': '#F3EBD3',         # Pale sand
    'text_dim': '#C0B49F',     # Dimmer sand
    'border': '#FFB400',       # Saffron borders
    'grid': '#2E1A3D',         # Darker violet grid
}

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

# ═══════════════════════════════════════════════════════════════════
#                         MAP GENERATOR
# ═══════════════════════════════════════════════════════════════════

class MapGenerator:
    """Generate folium maps with terrain analysis and forage zones"""
    
    def __init__(self, theme='dark'):
        self.theme = theme
        self.analyzer = TerrainAnalyzer()
    
    def create_map(self, df, title="Trail Map", show_forage=True):
        """Create a folium map from dataframe"""
        if df.empty:
            return self._create_empty_map()
        
        # Center on data
        center_lat = df['latitude'].mean()
        center_lon = df['longitude'].mean()
        
        # Create base map with OpenTopoMap
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=15,
            tiles='OpenTopoMap',
            attr='Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap'
        )
        
        # Add trail path
        trail_coords = list(zip(df['latitude'], df['longitude']))
        folium.PolyLine(
            trail_coords,
            color='#FFB400',  # Electric saffron - poppy gold
            weight=3,
            opacity=0.8,
            popup=title
        ).add_to(m)
        
        # Add start/end markers
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
        
        # Add forage prediction zones
        if show_forage:
            self._add_forage_zones(m, df)
        
        # Add data point markers (sample every 10th point to reduce clutter)
        for idx in range(0, len(df), 10):
            row = df.iloc[idx]
            self._add_data_marker(m, row)
        
        return m
    
    def create_aggregate_map(self, dfs_dict, show_forage=True):
        """Create map showing all trails together"""
        if not dfs_dict:
            return self._create_empty_map()
        
        # Get all coordinates
        all_lats = []
        all_lons = []
        for df in dfs_dict.values():
            all_lats.extend(df['latitude'].tolist())
            all_lons.extend(df['longitude'].tolist())
        
        center_lat = np.mean(all_lats)
        center_lon = np.mean(all_lons)
        
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=14,
            tiles='OpenTopoMap',
            attr='Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap'
        )
        
        # Poppywave color palette for different trails
        trail_colors = ['#FFB400', '#67E8F9', '#E1C8FF', '#FF8800', '#FFD6A5',
                       '#9B8FFF', '#FF6B6B', '#A6FF94', '#C77DFF', '#7DFFB2']
        
        # Add each trail with different color
        for idx, (trail_name, df) in enumerate(dfs_dict.items()):
            color = trail_colors[idx % len(trail_colors)]
            trail_coords = list(zip(df['latitude'], df['longitude']))
            
            folium.PolyLine(
                trail_coords,
                color=color,
                weight=2,
                opacity=0.7,
                popup=trail_name
            ).add_to(m)
        
        # Combine all dataframes for aggregate forage analysis
        if show_forage:
            combined_df = pd.concat(dfs_dict.values(), ignore_index=True)
            self._add_forage_zones(m, combined_df, aggregate=True)
        
        return m
    
    def _add_forage_zones(self, m, df, aggregate=False):
        """Add forage prediction zones to map"""
        # Analyze terrain
        clusters = self.analyzer.analyze_terrain(df)
        
        for species in FORAGE_SPECIES:
            suitable_points = []
            
            for _, row in df.iterrows():
                humidity = row['humidity']
                altitude = row['altitude']
                
                h_min, h_max = species['humidity_range']
                a_min, a_max = species['altitude_range']
                
                # Check if conditions are suitable
                if h_min <= humidity <= h_max and a_min <= altitude <= a_max:
                    suitable_points.append([row['latitude'], row['longitude']])
            
            if suitable_points:
                # Create zones around suitable points
                for point in suitable_points[::5]:  # Sample every 5th point
                    folium.Circle(
                        location=point,
                        radius=30 if aggregate else 20,
                        color=species['color'],
                        fill=True,
                        fillColor=species['color'],
                        fillOpacity=0.2 if aggregate else 0.3,
                        opacity=0.4 if aggregate else 0.5,
                        popup=f"<b>{species['name']}</b><br><i>{species['scientific']}</i><br>{species['description']}"
                    ).add_to(m)
    
    def _add_data_marker(self, m, row):
        """Add data point marker with sensor readings"""
        popup_html = f"""
        <div style='font-family: monospace; color: #F3EBD3; background: #3B1F4E; padding: 8px; border: 2px solid #FFB400;'>
            <b style='color: #FFB400;'>SENSOR DATA</b><br>
            <span style='color: #FF8800;'>Temp:</span> {row['temperature']:.1f}°C<br>
            <span style='color: #67E8F9;'>Humidity:</span> {row['humidity']:.1f}%<br>
            <span style='color: #E1C8FF;'>Pressure:</span> {row['pressure']:.1f} hPa<br>
            <span style='color: #FFB400;'>Altitude:</span> {row['altitude']:.1f}m<br>
            <span style='color: #FFB400;'>VOC:</span> {row['gas']:.0f} Ω
        </div>
        """
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=3,
            color='#67E8F9',  # Skywire cyan
            fill=True,
            fillColor='#67E8F9',
            fillOpacity=0.6,
            popup=folium.Popup(popup_html, max_width=250)
        ).add_to(m)
    
    def _create_empty_map(self):
        """Create empty map centered on Tilden Park"""
        return folium.Map(
            location=[37.9090, -122.2469],  # Tilden Park
            zoom_start=13,
            tiles='OpenTopoMap'
        )

# ═══════════════════════════════════════════════════════════════════
#                      MATPLOTLIB GRAPH WIDGET
# ═══════════════════════════════════════════════════════════════════

class GraphCanvas(FigureCanvas):
    """Cyberpunk-themed matplotlib canvas"""
    
    def __init__(self, parent=None):
        fig = Figure(figsize=(10, 6), facecolor='#000000')
        super().__init__(fig)
        self.setParent(parent)
        self.figure = fig
        
        # Apply cyberpunk style
        plt.style.use('dark_background')
        
    def plot_sensor_data(self, df):
        """Plot sensor data over time"""
        self.figure.clear()
        
        if df.empty:
            ax = self.figure.add_subplot(111)
            ax.set_facecolor('#3B1F4E')
            ax.text(0.5, 0.5, 'NO DATA LOADED', 
                   ha='center', va='center', color='#FFB400', fontsize=20)
            self.draw()
            return
        
        # Create 4 subplots with Poppywave colors
        axes = []
        for i in range(4):
            ax = self.figure.add_subplot(2, 2, i+1)
            ax.set_facecolor('#3B1F4E')  # Smoky violet background
            ax.grid(True, color='#2E1A3D', linestyle='-', linewidth=0.5)
            ax.spines['bottom'].set_color('#FFB400')  # Saffron borders
            ax.spines['top'].set_color('#FFB400')
            ax.spines['left'].set_color('#FFB400')
            ax.spines['right'].set_color('#FFB400')
            ax.tick_params(colors='#F3EBD3')  # Pale sand ticks
            axes.append(ax)
        
        # Temperature - warm poppy-orange
        axes[0].plot(df.index, df['temperature'], color='#FF8800', linewidth=2)
        axes[0].set_title('TEMPERATURE', color='#FFB400', fontweight='bold')
        axes[0].set_ylabel('°C', color='#F3EBD3')
        
        # Humidity - skywire cyan
        axes[1].plot(df.index, df['humidity'], color='#67E8F9', linewidth=2)
        axes[1].set_title('HUMIDITY', color='#FFB400', fontweight='bold')
        axes[1].set_ylabel('%', color='#F3EBD3')
        
        # Pressure - cloud lavender
        axes[2].plot(df.index, df['pressure'], color='#E1C8FF', linewidth=2)
        axes[2].set_title('PRESSURE', color='#FFB400', fontweight='bold')
        axes[2].set_ylabel('hPa', color='#F3EBD3')
        
        # VOC/Gas - electric saffron
        axes[3].plot(df.index, df['gas'], color='#FFB400', linewidth=2)
        axes[3].set_title('VOC RESISTANCE', color='#FFB400', fontweight='bold')
        axes[3].set_ylabel('Ω', color='#F3EBD3')
        
        self.figure.tight_layout()
        self.draw()

# ═══════════════════════════════════════════════════════════════════
#                         MAIN VIEWER WINDOW
# ═══════════════════════════════════════════════════════════════════

class DataViewer(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.df_dict = {}  # Dictionary to hold multiple dataframes
        self.map_generator = MapGenerator()
        self.init_ui()
        self.load_all_logs()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('TILDEN DATA VIEWER • Environmental Intelligence')
        self.setGeometry(100, 100, 1400, 900)
        
        # Apply cyberpunk theme
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['bg']};
            }}
            QTabWidget::pane {{
                border: 2px solid {COLORS['border']};
                background-color: {COLORS['bg']};
            }}
            QTabBar::tab {{
                background-color: {COLORS['bg']};
                color: {COLORS['text']};
                border: 2px solid {COLORS['border']};
                border-bottom: none;
                padding: 8px 20px;
                margin-right: 2px;
                font-family: 'Courier New';
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['grid']};
                color: {COLORS['primary']};
            }}
            QLabel {{
                color: {COLORS['text']};
                font-family: 'Courier New';
            }}
            QPushButton {{
                background-color: {COLORS['bg']};
                color: {COLORS['primary']};
                border: 2px solid {COLORS['primary']};
                padding: 10px 20px;
                font-family: 'Courier New';
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
                color: {COLORS['bg']};
            }}
            QTextEdit {{
                background-color: {COLORS['bg']};
                color: {COLORS['text']};
                border: 2px solid {COLORS['border']};
                font-family: 'Courier New';
                font-size: 11px;
            }}
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("""
╔══════════════════════════════════════════════════════════════════════╗
║              T I L D E N   D A T A   V I E W E R                     ║
║          Environmental Intelligence • Bioforage Protocol             ║
╚══════════════════════════════════════════════════════════════════════╝
        """)
        header.setAlignment(Qt.AlignCenter)
        font = QFont('Courier New', 10)
        font.setBold(True)
        header.setFont(font)
        layout.addWidget(header)
        
        # Load button
        btn_layout = QHBoxLayout()
        self.load_btn = QPushButton('⟳ RELOAD ALL LOGS')
        self.load_btn.clicked.connect(self.load_all_logs)
        btn_layout.addWidget(self.load_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Main tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.create_map_tab()
        self.create_graph_tab()
        self.create_stats_tab()
        self.create_forage_tab()
        
    def create_map_tab(self):
        """Create map tab with sub-tabs for individual trails"""
        # Create container widget with sub-tabs
        map_container = QWidget()
        map_layout = QVBoxLayout(map_container)
        
        # Create sub-tab widget for different trail views
        self.map_tabs = QTabWidget()
        map_layout.addWidget(self.map_tabs)
        
        # Add to main tabs
        self.tabs.addTab(map_container, '📡 TOPO.MAP')
        
    def create_graph_tab(self):
        """Create graph tab"""
        graph_widget = QWidget()
        layout = QVBoxLayout(graph_widget)
        
        self.graph_canvas = GraphCanvas()
        layout.addWidget(self.graph_canvas)
        
        self.tabs.addTab(graph_widget, '📊 DATA.PULSE')
        
    def create_stats_tab(self):
        """Create statistics tab"""
        stats_widget = QWidget()
        layout = QVBoxLayout(stats_widget)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        layout.addWidget(self.stats_text)
        
        self.tabs.addTab(stats_widget, '📈 SYS.STATS')
        
    def create_forage_tab(self):
        """Create forage recommendations tab"""
        forage_widget = QWidget()
        layout = QVBoxLayout(forage_widget)
        
        self.forage_text = QTextEdit()
        self.forage_text.setReadOnly(True)
        self.forage_text.setHtml(self._get_forage_info())
        layout.addWidget(self.forage_text)
        
        self.tabs.addTab(forage_widget, '🌱 FORAGE.PROTOCOL')
    
    def load_all_logs(self):
        """Load all rake_log CSV files from current directory"""
        # Find all rake_log files
        log_files = [f for f in os.listdir('.') if f.startswith('rake_log_') and f.endswith('.csv')]
        
        if not log_files:
            self.update_stats('NO LOG FILES FOUND')
            return
        
        # Load each file
        self.df_dict = {}
        for log_file in sorted(log_files):
            try:
                df = pd.read_csv(log_file)
                # Extract trail name from filename
                trail_name = log_file.replace('rake_log_', '').replace('.csv', '')
                self.df_dict[trail_name] = df
            except Exception as e:
                print(f"Error loading {log_file}: {e}")
        
        # Update all displays
        self.update_maps()
        self.update_graphs()
        self.update_stats()
    
    def update_maps(self):
        """Update map tab with individual trail tabs + aggregate view"""
        # Clear existing tabs
        self.map_tabs.clear()
        
        if not self.df_dict:
            return
        
        # Add aggregate view first
        aggregate_map = self.map_generator.create_aggregate_map(self.df_dict)
        aggregate_view = QWebEngineView()
        aggregate_html = aggregate_map._repr_html_()
        aggregate_view.setHtml(aggregate_html)
        self.map_tabs.addTab(aggregate_view, '🌐 ALL TRAILS')
        
        # Add individual trail tabs
        for trail_name, df in sorted(self.df_dict.items()):
            trail_map = self.map_generator.create_map(df, title=trail_name)
            web_view = QWebEngineView()
            html = trail_map._repr_html_()
            web_view.setHtml(html)
            
            # Shorten tab name
            short_name = trail_name.split('_')[2:5]  # Get trail name parts
            tab_label = ' '.join(short_name)[:15]  # Limit to 15 chars
            self.map_tabs.addTab(web_view, f'📍 {tab_label}')
    
    def update_graphs(self):
        """Update graph tab with data from all trails"""
        if self.df_dict:
            # Use first dataframe for now (could add selector later)
            first_df = list(self.df_dict.values())[0]
            self.graph_canvas.plot_sensor_data(first_df)
    
    def update_stats(self, error_msg=None):
        """Update statistics display"""
        if error_msg:
            self.stats_text.setPlainText(error_msg)
            return
        
        if not self.df_dict:
            self.stats_text.setPlainText('NO DATA LOADED')
            return
        
        # Aggregate statistics from all trails
        stats_lines = []
        stats_lines.append('═' * 70)
        stats_lines.append('           TILDEN ENVIRONMENTAL INTELLIGENCE REPORT')
        stats_lines.append('═' * 70)
        stats_lines.append('')
        
        # Trail summary
        stats_lines.append(f'TRAILS ANALYZED: {len(self.df_dict)}')
        total_points = sum(len(df) for df in self.df_dict.values())
        stats_lines.append(f'TOTAL DATA POINTS: {total_points:,}')
        stats_lines.append('')
        
        # Per-trail stats
        stats_lines.append('TRAIL SUMMARIES:')
        stats_lines.append('─' * 70)
        
        for trail_name, df in sorted(self.df_dict.items()):
            stats_lines.append(f'\n{trail_name}:')
            stats_lines.append(f'  Points: {len(df)}')
            stats_lines.append(f'  Temperature: {df["temperature"].mean():.1f}°C ({df["temperature"].min():.1f} - {df["temperature"].max():.1f})')
            stats_lines.append(f'  Humidity: {df["humidity"].mean():.1f}% ({df["humidity"].min():.1f} - {df["humidity"].max():.1f})')
            stats_lines.append(f'  Altitude: {df["altitude"].mean():.1f}m ({df["altitude"].min():.1f} - {df["altitude"].max():.1f})')
            stats_lines.append(f'  VOC: {df["gas"].mean():.0f}Ω')
        
        stats_lines.append('')
        stats_lines.append('═' * 70)
        stats_lines.append('        FUKUOKA NATURAL FARMING INSIGHTS')
        stats_lines.append('═' * 70)
        stats_lines.append('')
        stats_lines.append('🌾 Principle: Observe nature, work with its patterns')
        stats_lines.append('🌱 Diversity strengthens resilience')
        stats_lines.append('💧 Moisture zones indicate natural water flow')
        stats_lines.append('🌡️  Temperature gradients reveal microclimates')
        stats_lines.append('⛰️  Altitude variation creates ecological niches')
        stats_lines.append('')
        stats_lines.append('Suggested Action:')
        stats_lines.append('- Plant species matched to observed microclimates')
        stats_lines.append('- Focus on humid creek beds for moisture-loving species')
        stats_lines.append('- Use exposed ridges for drought-tolerant natives')
        stats_lines.append('- Respect natural gradients, avoid monoculture')
        
        self.stats_text.setPlainText('\n'.join(stats_lines))
    
    def _get_forage_info(self):
        """Generate forage species information HTML"""
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    background-color: {COLORS['bg']};
                    color: {COLORS['text']};
                    font-family: 'Courier New', monospace;
                    padding: 20px;
                }}
                h1 {{
                    color: {COLORS['primary']};
                    border-bottom: 2px solid {COLORS['primary']};
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: {COLORS['secondary']};
                    margin-top: 20px;
                }}
                .species {{
                    background-color: {COLORS['grid']};
                    border-left: 4px solid {COLORS['success']};
                    padding: 15px;
                    margin: 15px 0;
                }}
                .scientific {{
                    color: {COLORS['text_dim']};
                    font-style: italic;
                }}
                .requirements {{
                    color: {COLORS['warning']};
                    margin-top: 10px;
                }}
            </style>
        </head>
        <body>
            <h1>🌾 NATIVE FORAGE PROTOCOL</h1>
            <p>East Bay native grasses for ecological restoration and bioforage</p>
            
            <h2>SPECIES DATABASE:</h2>
        """
        
        for species in FORAGE_SPECIES:
            html += f"""
            <div class="species">
                <h3>{species['name']}</h3>
                <p class="scientific">{species['scientific']}</p>
                <p>{species['description']}</p>
                <p class="requirements">
                    <strong>Humidity:</strong> {species['humidity_range'][0]}-{species['humidity_range'][1]}%<br>
                    <strong>Altitude:</strong> {species['altitude_range'][0]}-{species['altitude_range'][1]}m
                </p>
            </div>
            """
        
        html += """
            <h2>FUKUOKA SEEDING PROTOCOL:</h2>
            <div class="species">
                <p><strong>1. Seed Ball Preparation:</strong></p>
                <ul>
                    <li>Mix seeds with clay and compost</li>
                    <li>Form 1-inch balls</li>
                    <li>Dry in shade for 48 hours</li>
                </ul>
                
                <p><strong>2. Dispersal Strategy:</strong></p>
                <ul>
                    <li>Target microclimates identified by sensor data</li>
                    <li>Scatter in early winter before rains</li>
                    <li>No tilling or soil disturbance</li>
                </ul>
                
                <p><strong>3. Observation:</strong></p>
                <ul>
                    <li>Monitor germination patterns</li>
                    <li>Let strongest individuals establish</li>
                    <li>Trust natural selection</li>
                </ul>
            </div>
            
            <h2>WHY NATIVE GRASSES?</h2>
            <p>• Deep root systems (up to 20 feet) sequester carbon<br>
            • Prevent erosion and build soil<br>
            • Provide habitat for native insects and birds<br>
            • Require no irrigation once established<br>
            • Adapted to local climate patterns</p>
        </body>
        </html>
        """
        
        return html

# ═══════════════════════════════════════════════════════════════════
#                              MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    
    # Set app-wide font
    font = QFont('Courier New', 10)
    app.setFont(font)
    
    viewer = DataViewer()
    viewer.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
