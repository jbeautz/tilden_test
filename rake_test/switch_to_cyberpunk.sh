#!/bin/bash
# Switch to Cyberpunk GUI theme

echo "Switching to Cyberpunk GUI theme..."

# Stop the service
sudo systemctl stop rake-sensor.service

# Backup current display and switch
cd /home/pi/tilden_test/rake_test || cd "$(dirname "$0")"

# Create backup of current display if not already backed up
if [ ! -f display_backup.py ]; then
    cp display_forest_rings.py display_backup.py
fi

# Copy cyberpunk theme to display module
cp gui_cyberpunk_theme.py display_forest_rings.py

echo "✓ Switched to Cyberpunk theme"
echo ""
echo "Starting service..."
sudo systemctl start rake-sensor.service
sleep 2

echo ""
echo "Service status:"
sudo systemctl status rake-sensor.service --no-pager -l | head -15

echo ""
echo "================================================"
echo "Cyberpunk GUI is now active!"
echo "================================================"
echo ""
echo "The display features:"
echo "• Neon glow effects and cyberpunk aesthetics"
echo "• Current time and date display"
echo "• All BME680 sensor data (Temp, Humidity, Pressure, VOC)"
echo "• GPS coordinates when available"
echo "• Temperature graph with hologram effects"
echo ""
echo "To switch back to Forest Rings:"
echo "./switch_to_forest.sh"
