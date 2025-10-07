#!/bin/bash
# Switch to Forest Rings GUI theme

echo "Switching to Forest Rings GUI theme..."

# Stop the service
sudo systemctl stop rake-sensor.service

# Restore from backup or use original
cd /home/pi/tilden_test/rake_test || cd "$(dirname "$0")"

if [ -f display_backup.py ]; then
    cp display_backup.py display_forest_rings.py
    echo "✓ Restored Forest Rings theme from backup"
else
    echo "✓ Using current Forest Rings theme"
fi

echo ""
echo "Starting service..."
sudo systemctl start rake-sensor.service
sleep 2

echo ""
echo "Service status:"
sudo systemctl status rake-sensor.service --no-pager -l | head -15

echo ""
echo "================================================"
echo "Forest Rings GUI is now active!"
echo "================================================"
echo ""
echo "The display features:"
echo "• Nature-themed tree ring visualization"
echo "• All BME680 sensor data (Temp, Humidity, Pressure, VOC)"
echo "• GPS coordinates with 60-second caching"
echo "• Rings grow as data changes over time"
echo ""
echo "To switch to Cyberpunk theme:"
echo "./switch_to_cyberpunk.sh"
