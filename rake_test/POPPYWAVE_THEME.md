╔══════════════════════════════════════════════════════════════════════╗
║                    POPPYWAVE COLOR SCHEME APPLIED                    ║
║            Golden Poppies Under Ultraviolet Skies                    ║
╚══════════════════════════════════════════════════════════════════════╝

🎨 POPPYWAVE PALETTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Concept: A hillside of California golden poppies viewed through a neon lens.
         Moody dusk energy meets vibrant bloom — analog and alive.

PRIMARY COLORS:
  🟣 Smoky Violet (#3B1F4E)     - Background, moody dusk base
  🟡 Electric Saffron (#FFB400)  - Primary accent, pure poppy fire
  🔵 Skywire Cyan (#67E8F9)      - Cool tech shimmer
  🟪 Cloud Lavender (#E1C8FF)    - Highlights and tertiary accent
  📄 Pale Sand (#F3EBD3)         - Text, warm and readable

GRADIENT COLORS:
  🧡 Warm Poppy-Orange (#FF8800) - Temperature visualization
  🌸 Lighter Violet (#4D2961)     - Elevated UI elements
  🌙 Darker Violet (#2E1A3D)      - Inset areas, cards

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 APPLIED TO DISPLAY (display_forest_rings.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Background:           Smoky Violet (#3B1F4E)
  Tree Ring - Temp:     Warm Poppy-Orange (#FF8800)
  Tree Ring - Humidity: Skywire Cyan (#67E8F9)
  Tree Ring - Pressure: Cloud Lavender (#E1C8FF)
  Tree Ring - GPS:      Electric Saffron (#FFB400)
  
  Text:                 Pale Sand (#F3EBD3)
  Reading Borders:      Electric Saffron (#FFB400)
  Reading Background:   Darker Violet (#2E1A3D)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💻 APPLIED TO DATA VIEWER (data_viewer.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MAIN UI:
  Window Background:    Smoky Violet (#3B1F4E)
  Borders & Tabs:       Electric Saffron (#FFB400)
  Text:                 Pale Sand (#F3EBD3)
  Active Tab:           Saffron on Violet
  Grid Lines:           Darker Violet (#2E1A3D)

GRAPHS (DATA.PULSE tab):
  Background:           Smoky Violet (#3B1F4E)
  Temperature Line:     Warm Poppy-Orange (#FF8800)
  Humidity Line:        Skywire Cyan (#67E8F9)
  Pressure Line:        Cloud Lavender (#E1C8FF)
  VOC Line:             Electric Saffron (#FFB400)
  Axes & Labels:        Saffron borders, Sand text

MAPS (TOPO.MAP tab):
  Trail Paths:          Electric Saffron (#FFB400) - primary trail
  Multi-trail Palette:  Saffron, Cyan, Lavender, Orange, Peach
  Data Markers:         Skywire Cyan circles
  Sensor Popups:        Violet background, Saffron border

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ MOOD & AESTHETIC
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"A hillside in bloom viewed through a neon lens."

Perfect for:
  • Artistic data visualization
  • Nostalgic California vibes with tech edge
  • Nature-meets-cyberpunk aesthetic
  • Dashboard with heart and warmth
  • Topographic maps that pop against violet dusk

The color combination evokes:
  🌅 Sunset over poppy fields in the East Bay hills
  💜 Twilight hour when the sky turns deep violet
  🌼 Vibrant wildflower bloom season
  🔮 Sci-fi future meets natural farming
  🎸 80s synth-wave meets soil science

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 FILES UPDATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ display_forest_rings.py  - Real-time sensor display (Pi touchscreen)
✅ data_viewer.py            - Analysis GUI with graphs and maps
✅ generate_historical_logs.py - Added 10 diverse trail configurations
✅ generate_multi_trail_demo.py - HTML demo with individual trail tabs

📊 Generated Data:
   • 10 trail logs covering diverse Tilden microclimates
   • 15,600 total data points
   • Humidity range: 42-85%
   • Elevation range: 200-420m

🌐 New Features:
   • Individual trail tabs in map viewer
   • Aggregate view showing all trails together
   • Per-trail microclimate analysis
   • Enhanced forage zone predictions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 DEPLOYMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Changes pushed to git: jbeautz/tilden_test

To deploy on Raspberry Pi:
  1. SSH: ssh maggi@192.168.4.49
  2. Update: cd ~/tilden_test/rake_test && git pull
  3. Run display: python3 main.py
  4. Run viewer: python3 data_viewer.py

The Poppywave theme will render beautifully on the 800x480 touchscreen!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌟 WHY POPPYWAVE?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Perfect match for this project:
  
  🌾 California Native: Golden poppies are THE iconic CA flower
  🏔️  Tilden Park: Purple mountains' majesty at dusk
  🌱 Natural Farming: Warm earth tones meet cool tech
  📊 Data Viz: High contrast for readability
  ✨ Unique: Stands out from generic green/blue dashboards
  
The violet background is easy on the eyes for long monitoring sessions,
while the saffron accents provide clear visual hierarchy. The cyan and
lavender create depth and variety without visual chaos.

It's a color scheme that honors the landscape being monitored. 🌅

╔══════════════════════════════════════════════════════════════════════╗
║                 "Golden poppies under ultraviolet skies"             ║
╚══════════════════════════════════════════════════════════════════════╝
