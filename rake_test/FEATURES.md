# 🌿⚡ Tilden Environmental Monitoring System - Complete Feature List

**Created: October 2025**  
**Project: Raspberry Pi soil/environmental sensor + GPS data logger + Analysis suite**

---

## 📦 System Overview

A complete environmental monitoring and analysis system for Tilden Regional Park, designed for:
- Real-time sensor data collection (Temperature, Humidity, Pressure, VOC/Gas)
- GPS tracking for spatial mapping
- Beautiful cyberpunk-nature visualization
- Native forage species prediction for cattle grazing
- Terrain-based microclimate analysis
- Historical data aggregation across multiple trails

---

## 🎯 Main Components

### 1. **Data Collection System** (Raspberry Pi)
**Files:** `main.py`, `sensor.py`, `gps.py`, `logger.py`, `display_forest_rings.py`

**Hardware:**
- Raspberry Pi 4 with touchscreen display (800x480)
- BME680 environmental sensor (I2C)
- GPS module
- Power supply for field deployment

**Features:**
- ✅ **Continuous 1Hz logging** from power-on to power-off
- ✅ **BME680 sensor** readings: Temperature, Humidity, Pressure, Gas/VOC
- ✅ **GPS tracking** with coordinates and altitude
- ✅ **Beautiful tree ring display** showing sensor data as growing rings
- ✅ **GPS caching** (60s hold time) prevents flashing
- ✅ **Touch support** enabled for Pi touchscreen
- ✅ **Auto-recovery logging** - creates new file each session
- ✅ **CSV export** with timestamps for analysis

**Display Themes:**
- 🌲 Forest Rings (default) - Nature-inspired tree growth visualization
- 🌆 Cyberpunk Theme - Neon-lit alternative GUI

---

### 2. **Data Analysis Suite** (Desktop/Pi)
**File:** `data_viewer.py`

**🌿⚡ CYBERPUNK-NATURE GUI**

**Visual Design:**
- **Black background** with sharp, hard edges
- **Cyan/magenta neon accents** (80s techno aesthetic)
- **Monospace fonts** for data displays
- **ASCII art decorations**: 🐄 cows, 🐑 sheep, 🌱 plants throughout
- **Glowing status bars** with real-time updates

**Four Main Tabs:**

#### 📡 **TOPO.MAP** - Interactive Topographic Mapping
- **OpenTopoMap tiles** for terrain visualization
- **Multiple base layers:** OpenStreetMap, Terrain, Satellite
- **Real trail data** from Tilden:
  - Lake Anza Beach → Mineral Springs Trail → Wildcat Canyon Road
  - Plus 10 additional historical trails covering entire park
- **Color-coded markers:**
  - 🔵 Blue = High humidity (lake shores, creek beds)
  - 🟡 Yellow = Medium humidity (forest trails)
  - 🔴 Red = Low humidity (exposed ridges, hilltops)
- **Clickable popups** with detailed sensor readings
- **Path lines** showing complete trail routes
- **Start/End markers** with location names

**Special Layers (Toggle On/Off):**

🌱 **Forage Prediction Zones:**
- Shows optimal seeding locations for 5 native East Bay species:
  1. **Purple Needlegrass** 🌾 - Dry hillsides (250-450m)
  2. **California Oatgrass** 🌿 - Moderate zones (150-400m)
  3. **Creeping Wildrye** 🌱 - Humid creek beds (200-350m)
  4. **Blue Wildrye** 🍃 - Mid-elevation slopes (250-500m)
  5. **California Brome** 🌾 - Transitional areas (180-380m)
- Zones sized by suitability (65-100% confidence)
- Conservative seeding: Only top 15% of trail marked
- Based on: Humidity, Altitude, VOC (organic matter)

🗺️ **Terrain-Based Predictions:**
- Extrapolates microclimate predictions beyond surveyed trails
- Uses altitude-based terrain clustering
- Grid-based prediction across expanded area
- Shows where species WOULD thrive based on similar terrain
- Confidence scores based on data density

**Aggregate Analysis:**
- **📚 LOAD.ALL.LOGS button** - Load all 10 historical trails at once
- **16,620+ total data points** from diverse microclimates
- **Heat mapping** - More data = stronger predictions
- **Coverage:**
  - Humid zones: Wildcat Creek (85%), Jewel Lake (82%), Big Springs (78%)
  - Moderate zones: Curran Trail (68%), Laurel Canyon (72%)
  - Dry zones: Nimitz Way (48%), Pack Rat (45%), Quarry Trail (42%)

#### 📊 **DATA.PULSE** - Time Series Graphs
- **Neon cyberpunk styling:**
  - Cyan temperature line
  - Magenta humidity line
  - Yellow pressure line
  - Green VOC/gas line
- **Smooth interpolation** for clean visualization
- **Grid lines** with dark theme
- **Legend** with emoji indicators
- **Time-based X-axis** with proper formatting
- **Dual Y-axes** for different scales

#### 📈 **SYS.STATS** - Statistical Analysis + Fukuoka Insights
**Statistics Panel:**
- Mean, Min, Max, Std Dev for all sensors
- GPS coordinate ranges
- Altitude gain/loss calculations
- Data quality metrics
- Sample counts

**🌱 Fukuoka-Style Natural Farming Insights:**
Inspired by Masanobu Fukuoka's philosophy of observation-based farming:
- **"Observe before intervening"** - Patient data collection
- **Microclimate identification** - Respecting natural zones
- **Minimal intervention** - Work with nature, not against it
- **Species-terrain matching** - Right plant, right place
- **Seasonal recommendations** - Best times for seeding
- **Natural indicators** - Reading the land's story

**Sample Insights:**
```
🌾 "The land reveals itself through moisture patterns. 
   High humidity near water invites water-loving grasses. 
   Dry ridges call for drought-tolerant natives."

🐄 "Cattle prefer the middle path - not too wet, not too dry. 
   Moderate zones (60-70% humidity) host the most diverse forage."

⛰️ "Elevation is teacher. Each 100m climb brings 5% less humidity,
   2°C cooler air, and different plant communities."
```

**Historical Comparison:**
- Terrain type clustering (altitude bands)
- Average conditions per microclimate
- Best/worst trails for each species
- Seasonal variation analysis

#### 🌱 **FORAGE.PROTOCOL** - Seed Dispersal Recommendations
**Detailed Species Analysis:**

For each native species:
- **Optimal conditions** (humidity range, altitude, soil type)
- **Suitability scores** for surveyed locations
- **Recommended seeding zones** (map coordinates)
- **Germination likelihood** (conservative estimates)
- **Success probability** based on historical data
- **Grazing benefits** for cattle
- **Ecological role** in native ecosystem

**Seeding Strategy:**
- **Conservative approach** - Only seed where conditions are ideal
- **15% of trail** receives recommendations
- **Multiple species zones** can overlap for diversity
- **Seasonal timing** suggestions
- **Maintenance requirements** (minimal per Fukuoka method)

**Example Output:**
```
🌾 PURPLE NEEDLEGRASS (Stipa pulchra)
   Optimal: 40-60% humidity, 250-450m altitude
   Found 8 suitable zones (suitability >70%)
   Recommended seeding: 0.2 kg across 12 locations
   Expected germination: 65-80% (spring seeding)
   Cattle benefit: High protein, drought-resistant
```

---

### 3. **Terrain Analysis Engine**
**File:** `terrain_analysis.py`

**TerrainAnalyzer Class:**
- **Microclimate clustering** using scikit-learn
- **Altitude-based zoning** (50m bands)
- **Humidity pattern recognition**
- **VOC/organic matter mapping**
- **Similarity scoring** for extrapolation
- **Grid-based prediction** across unmapped areas
- **Confidence weighting** based on data density

**Algorithms:**
- K-Means clustering for terrain types
- Inverse distance weighting for interpolation
- Nearest neighbor for quick predictions
- Statistical aggregation across multiple trails

---

### 4. **Historical Data System**
**Files:** `generate_historical_logs.py` + 10 CSV log files

**Simulated Trails:**
1. **Nimitz Way - South Section** (1500 pts) - Exposed ridge, dry
2. **Wildcat Creek Trail** (1800 pts) - Creek bed, very humid
3. **Seaview Trail** (2100 pts) - Mid-elevation loop
4. **Big Springs Trail** (1200 pts) - Spring-fed, moist
5. **Curran Trail** (1680 pts) - Shaded forest
6. **Pack Rat Trail** (1320 pts) - Sunny exposed hillside
7. **Laurel Canyon Trail** (1920 pts) - Deep canyon, humid
8. **Mezue Trail** (1560 pts) - Ridge connector, moderate
9. **Quarry Trail** (1080 pts) - Old quarry site, dry rocky
10. **Jewel Lake Loop** (1440 pts) - Lake shore, humid

**Coverage:**
- **16,620 total readings** across diverse microclimates
- **Elevation range:** 180m - 520m
- **Humidity range:** 35% - 85%
- **Realistic sensor noise** and natural variation
- **GPS paths** covering ~12 sq km of Tilden

---

### 5. **Desktop Launchers** (Raspberry Pi Desktop)
**Files:** `SoilMonitor.desktop`, `TildenViewer.desktop`, launcher scripts

**Soil Monitor Launcher:**
- Starts data collection system
- Forest rings display
- Logs to CSV
- Runs until manually stopped

**Tilden Data Viewer Launcher:**
- Opens analysis suite
- Demo mode pre-loaded
- Can load real CSV files
- Interactive map and graphs

---

## 🚀 Quick Start Guide

### On Raspberry Pi:

**1. Install Dependencies:**
```bash
pip3 install -r requirements_viewer.txt
```

**2. Collect Data (Manual Start):**
```bash
./start_forest_rings.sh
```
Or double-click `SoilMonitor.desktop` icon

**3. Analyze Data:**
```bash
python3 data_viewer.py
```
Or double-click `TildenViewer.desktop` icon

**4. Load All Historical Logs:**
- Open Tilden Data Viewer
- Click **📚 LOAD.ALL.LOGS** button
- Explore aggregate predictions on map!

### On Mac/Linux Desktop:

**1. Pull Latest Code:**
```bash
cd ~/tilden_test/rake_test
git pull
```

**2. Install Dependencies:**
```bash
pip3 install PyQt5 PyQtWebEngine folium pandas matplotlib numpy scikit-learn
```

**3. Run Viewer:**
```bash
python3 data_viewer.py
```

---

## 📊 Data Format

**CSV Log Files:** `rake_log_YYYYMMDD_HHMMSS.csv`

```csv
timestamp,temperature,humidity,pressure,gas,latitude,longitude,altitude
2025-10-07 10:00:00,18.5,78.2,1012.3,62450,37.8964,-122.2445,235.5
2025-10-07 10:00:01,18.5,78.1,1012.3,62380,37.8964,-122.2445,235.7
...
```

**Fields:**
- `timestamp`: ISO format date-time
- `temperature`: °C
- `humidity`: % relative humidity
- `pressure`: hPa (hectopascals)
- `gas`: Ω (ohms) - BME680 gas resistance (VOC indicator)
- `latitude`: Decimal degrees
- `longitude`: Decimal degrees
- `altitude`: Meters above sea level

---

## 🌍 Geographic Coverage

**Tilden Regional Park, Berkeley, CA**
- Center: ~37.90°N, 122.24°W
- Area: ~2,000 acres
- Elevation: 180m - 520m
- Ecosystems: Oak woodland, grassland, riparian, chaparral

**Surveyed Trails (Demo Data):**
- Lake Anza area (humid lakeside)
- Mineral Springs Trail (transitional)
- Wildcat Canyon corridors
- Nimitz Way ridgeline
- Various creek beds and springs

---

## 🐄 Native Forage Species

**1. Purple Needlegrass** (*Stipa pulchra*)
- California state grass
- Deep roots, drought tolerant
- Prefers: 40-60% humidity, well-drained slopes
- Cattle: High protein, year-round forage

**2. California Oatgrass** (*Danthonia californica*)
- Perennial bunchgrass
- Shade tolerant
- Prefers: 50-70% humidity, moderate elevations
- Cattle: Early spring grazing, nutritious

**3. Creeping Wildrye** (*Leymus triticoides*)
- Rhizomatous spreader
- Wetland tolerant
- Prefers: 60-80% humidity, low elevations near water
- Cattle: Summer forage, erosion control

**4. Blue Wildrye** (*Elymus glaucus*)
- Tall bunchgrass
- Cool season grower
- Prefers: 35-55% humidity, mid-high elevations
- Cattle: Spring/fall forage, wildlife habitat

**5. California Brome** (*Bromus carinatus*)
- Annual to short-lived perennial
- Pioneer species
- Prefers: 45-65% humidity, disturbed areas
- Cattle: Quick establishment, early forage

---

## 🔧 Technical Stack

**Hardware:**
- Raspberry Pi 4 (2-8GB RAM)
- BME680 I2C sensor
- GPS module (UART)
- Official 7" touchscreen or DSI display

**Software:**
- Python 3.9+
- pygame (real-time display)
- PyQt5 + PyQtWebEngine (analysis GUI)
- folium (web mapping)
- pandas (data analysis)
- matplotlib (graphing)
- numpy (numerical computing)
- scikit-learn (terrain clustering)

**Protocols:**
- I2C for BME680 sensor
- UART/Serial for GPS
- CSV for data storage
- Git for version control

---

## 📝 Usage Tips

**Best Practices:**
1. **Let BME680 warm up** - First 5-10 minutes may have unstable gas readings
2. **GPS needs clear sky** - Works poorly indoors/under dense canopy
3. **Power cycle creates new log** - Each boot = new CSV file
4. **Touch calibration** - If touch is off, recalibrate in Pi settings
5. **Data analysis** - Transfer CSVs to desktop for best performance
6. **Battery life** - External battery pack recommended for long hikes

**Troubleshooting:**
- **Display black?** Check DISPLAY=:0 environment variable
- **No GPS?** Ensure module has clear sky view, check wiring
- **Touch not working?** Verify SDL_NOMOUSE is NOT set
- **Sensor errors?** Check I2C connection: `i2cdetect -y 1`

---

## 🌟 Future Enhancements

**Potential Additions:**
- [ ] Soil moisture sensor integration
- [ ] Solar radiation measurement
- [ ] Wind speed/direction
- [ ] Multi-spectral imaging (NDVI)
- [ ] Real-time cloud sync
- [ ] Mobile app for remote monitoring
- [ ] Machine learning for advanced predictions
- [ ] Integration with satellite imagery
- [ ] Grazing pattern optimization
- [ ] Carbon sequestration tracking

---

## 📚 Educational Value

This system demonstrates:
- **Environmental science** - Microclimate variation
- **Ecology** - Species-habitat relationships
- **Agriculture** - Rotational grazing, native forage
- **Data science** - Collection, analysis, visualization
- **Engineering** - Embedded systems, sensor integration
- **Geography** - Spatial analysis, GIS concepts
- **Natural farming** - Fukuoka's observation-based methods

---

## 🙏 Acknowledgments

- **Masanobu Fukuoka** - Natural farming philosophy inspiration
- **East Bay Regional Park District** - Tilden Park stewardship
- **UC Berkeley** - Native plant research
- **Open source communities** - Python, PyQt, Folium, scikit-learn

---

## 📄 License

MIT License - Free to use, modify, and distribute

---

**Built with 🌿 for sustainable land management**
**Created October 2025 by Jack Beautz with GitHub Copilot**

