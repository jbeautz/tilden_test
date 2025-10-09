# 🌅 Tilden Environmental Intelligence System - COMPLETE

**Status:** ✅ Fully Implemented & Pushed to GitHub  
**Repository:** jbeautz/tilden_test  
**Pi Location:** maggi@192.168.4.49:~/tilden_test/rake_test

---

## 🎨 NEW: Poppywave Color Scheme

**"Golden poppies under ultraviolet skies"**

The entire UI has been transformed with the Poppywave aesthetic:
- **Smoky Violet** (#3B1F4E) - moody dusk background
- **Electric Saffron** (#FFB400) - pure poppy fire accents  
- **Skywire Cyan** (#67E8F9) - cool tech shimmer
- **Cloud Lavender** (#E1C8FF) - soft highlights
- **Pale Sand** (#F3EBD3) - warm readable text

This creates a unique California-native aesthetic that honors the landscape being monitored!

---

## 🗺️ NEW: Multi-Trail Analysis System

### Individual Trail Tabs
The data viewer now includes:
- **10 historical trail logs** covering diverse Tilden microclimates
- **Individual trail tabs** - view each hike separately with its unique conditions
- **Aggregate view** - see all trails overlaid with combined predictions
- **15,600 total data points** spanning the entire park

### Trail Coverage
1. **Nimitz Way** - Exposed ridge (48% humidity, 350-420m)
2. **Wildcat Creek** - Creek bed (85% humidity, 200-260m)
3. **Seaview Trail** - Rolling terrain (58%, 280-380m)
4. **Big Springs** - Spring-fed (78%, 240-280m)
5. **Curran Trail** - Forest (68%, 260-340m)
6. **Pack Rat Trail** - Exposed hillside (45%, 310-400m)
7. **Laurel Canyon** - Deep canyon (72%, 220-310m)
8. **Mezue Trail** - Ridge connector (56%, 300-370m)
9. **Quarry Trail** - Dry rocky (42%, 340-410m)
10. **Jewel Lake Loop** - Lake shore (82%, 210-240m)

---

## 🌿 System Components

### 1. Real-Time Display (`display_forest_rings.py`)
**For:** Raspberry Pi with 800x480 touchscreen  
**Features:**
- Tree ring visualization with concentric growth rings
- Live sensor readings (temp, humidity, pressure, VOC)
- GPS coordinates with caching (60-second refresh)
- Touchscreen enabled
- Poppywave color scheme
- Runs continuously at 1Hz logging + 10Hz display refresh

### 2. Data Viewer (`data_viewer.py`)
**For:** Desktop analysis (PyQt5 application)  
**Four tabs:**

#### 📡 TOPO.MAP
- Interactive topographic maps using OpenTopoMap
- Individual trail tabs for each historical log
- Aggregate view showing all trails together
- Forage prediction zones overlaid
- Sensor data markers with detailed popups

#### 📊 DATA.PULSE
- Real-time graphs with Poppywave colors:
  - Temperature (warm poppy-orange)
  - Humidity (skywire cyan)
  - Pressure (cloud lavender)
  - VOC (electric saffron)

#### 📈 SYS.STATS
- Aggregate statistics across all trails
- Per-trail summaries
- Fukuoka natural farming insights

#### 🌱 FORAGE.PROTOCOL
- 5 native East Bay grass species
- Humidity and altitude requirements
- Seed ball preparation instructions
- Natural farming philosophy

---

## 🌾 Native Species Integration

Automated predictions for:
1. **Purple Needlegrass** (40-60% humidity, 250-450m)
2. **California Oatgrass** (50-70%, 150-400m)
3. **Creeping Wildrye** (60-80%, 200-350m)
4. **Blue Wildrye** (35-55%, 250-500m)
5. **California Brome** (45-65%, 180-380m)

Predictions based on terrain analysis with:
- K-Means clustering for microclimate identification
- 50m altitude bands
- Inverse distance weighting for interpolation
- Similarity scoring for recommendations

---

## 🔧 Hardware Setup

**Raspberry Pi 4:**
- BME680 sensor (I2C at 0x77) - temp, humidity, pressure, VOC
- GPS module (UART) - latitude, longitude, altitude
- 800x480 DSI touchscreen
- 1Hz CSV logging with auto-recovery

**Desktop/Laptop:**
- PyQt5 for data viewer
- Folium for web maps
- Matplotlib for graphs
- Pandas/NumPy for analysis

---

## 📂 Key Files

```
main.py                          # Main sensor loop (Pi)
display_forest_rings.py          # Poppywave GUI (Pi touchscreen)
data_viewer.py                   # Multi-trail analysis GUI (desktop)
sensor.py                        # BME680 interface
gps.py                          # GPS reader
logger.py                        # CSV logging with recovery
terrain_analysis.py              # K-Means clustering engine
generate_historical_logs.py      # Generate diverse trail data
generate_multi_trail_demo.py     # HTML demo generator

# Service files
rake-sensor.service              # Systemd service (disabled - using desktop launchers)
SoilMonitor.desktop             # Desktop launcher for sensor
TildenViewer.desktop            # Desktop launcher for viewer

# Documentation
FEATURES.md                      # Comprehensive feature documentation
POPPYWAVE_THEME.md              # Color scheme details
DEPLOYMENT_STATUS.md            # Deployment notes
```

---

## 🚀 Quick Start

### On Raspberry Pi:

**Option 1: Desktop Launcher**
- Double-click "Soil Monitor" icon on desktop
- Starts logging immediately

**Option 2: Terminal**
```bash
cd ~/tilden_test/rake_test
python3 main.py
```

### On Desktop/Laptop:

**Option 1: Desktop Launcher**  
- Double-click "Tilden Viewer" icon

**Option 2: Terminal**
```bash
cd ~/tilden_test/rake_test
python3 data_viewer.py
```

**Option 3: HTML Demo (macOS workaround)**
```bash
python3 generate_multi_trail_demo.py
open tilden_multi_trail_demo.html
```

---

## 🎯 Data Flow

```
Sensors (BME680 + GPS)
    ↓ 1 Hz
Logging System → rake_log_YYYYMMDD_HHMMSS.csv
    ↓
Display (Real-time tree rings on Pi)
    ↓
Data Viewer (Desktop analysis)
    ↓
Terrain Analysis (K-Means clustering)
    ↓
Forage Predictions (Native species zones)
```

---

## 🌟 What Makes This Special

### 1. Poppywave Aesthetic
Unique California-native color scheme that honors the landscape. No generic blue/green dashboards here!

### 2. Multi-Trail Intelligence
Individual trail analysis + aggregate predictions enable broader terrain understanding. See patterns across microclimates.

### 3. Fukuoka Integration
Not just data collection - actionable natural farming insights based on observed conditions.

### 4. Native Species Focus
Five East Bay native grasses with ecological restoration potential. Deep roots, carbon sequestration, wildlife habitat.

### 5. Beautiful Visualizations
- Tree ring growth patterns for sensor history
- Topographic maps with forage zones
- Cyberpunk-nature aesthetic throughout

---

## 📊 Data Generated

### Historical Logs:
- **10 trail configurations** across Tilden Regional Park
- **15,600 data points** total
- Humidity range: **42-85%**
- Elevation range: **200-420m**
- Temperature: **13-27°C** (realistic altitude gradients)
- VOC: **30,000-80,000Ω** (correlated with humidity/organic matter)

### Real-Time Collection:
- Continuous 1Hz logging from power-on to power-off
- Auto-recovery from crashes/power loss
- New CSV file per session with timestamp

---

## 🔮 Future Possibilities

- **Machine learning** on terrain patterns for better predictions
- **Weather integration** for seasonal recommendations
- **Multi-year analysis** tracking ecological changes
- **Community mapping** - multiple devices covering larger area
- **Seed dispersal tracker** - mark where seed balls were placed
- **Germination monitoring** - revisit sites to log success rates

---

## 📝 Credits

**Philosophy:** Masanobu Fukuoka's "One-Straw Revolution"  
**Location:** Tilden Regional Park, Berkeley, CA  
**Native Plants:** East Bay native grass species  
**Color Scheme:** Poppywave - inspired by California golden poppies  
**Tech Stack:** Python, PyQt5, Folium, Pygame, Matplotlib, Pandas, Scikit-learn

---

## 🎨 The Poppywave Philosophy

> *"Golden poppies under ultraviolet skies - a hillside in bloom viewed through a neon lens."*

This isn't just a data collection system. It's a bridge between:
- **Ancient wisdom** (Fukuoka's natural farming)
- **Modern technology** (sensors, ML, visualization)
- **California ecology** (native species restoration)
- **Artistic expression** (cyberpunk-nature aesthetic)

The violet background represents twilight in the East Bay hills. The saffron accents honor the golden poppy - California's state flower. The cyan shimmer brings in the tech element. Together, they create something unique: **technology in service of natural restoration**.

---

**🌅 Status: Complete and beautiful. Ready for deployment. Ready for bloom.**

╔══════════════════════════════════════════════════════════════════════╗
║              "The soil is not a mechanism to be mastered,            ║
║               but a living community to be nurtured."                ║
║                     - Inspired by Masanobu Fukuoka                   ║
╚══════════════════════════════════════════════════════════════════════╝
