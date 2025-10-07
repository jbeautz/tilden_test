#!/bin/bash
# Apply VOC sensor fix and restart service

echo "================================================"
echo "Applying BME680 VOC Sensor Fix"
echo "================================================"
echo ""

# Stop the service
echo "1. Stopping rake-sensor service..."
sudo systemctl stop rake-sensor.service
sleep 2

# Check if files have been updated
echo ""
echo "2. Checking updated files..."
if grep -q "gas_history" display_forest_rings.py; then
    echo "   ✓ display_forest_rings.py has gas_history"
else
    echo "   ✗ display_forest_rings.py needs to be updated"
    echo "   Please copy the updated files from your Mac first!"
    exit 1
fi

if grep -q "Always return gas_resistance" sensor.py; then
    echo "   ✓ sensor.py updated to always return gas values"
else
    echo "   ✗ sensor.py needs to be updated"
    echo "   Please copy the updated files from your Mac first!"
    exit 1
fi

# Start the service
echo ""
echo "3. Starting rake-sensor service..."
sudo systemctl start rake-sensor.service
sleep 3

# Check status
echo ""
echo "4. Checking service status..."
sudo systemctl status rake-sensor.service --no-pager -l | head -20

echo ""
echo "================================================"
echo "Fix applied! Monitoring logs for gas readings..."
echo "================================================"
echo ""
echo "Gas sensor will take 5-10 minutes to stabilize."
echo "You should see messages like:"
echo "  'Gas sensor: 45230 Ω (warming up, not stable yet)'"
echo ""
echo "Press Ctrl+C to stop watching logs"
echo ""

# Follow logs
sudo journalctl -u rake-sensor.service -f
