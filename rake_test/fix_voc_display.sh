#!/bin/bash
# Fix VOC display and restart GUI service

echo "================================================"
echo "Fixing VOC Display - Forest Rings GUI"
echo "================================================"
echo ""

# Stop the service
echo "1. Stopping rake-sensor service..."
sudo systemctl stop rake-sensor.service
sleep 2

# Pull latest changes
echo ""
echo "2. Pulling latest changes from git..."
git pull

# Verify files are updated
echo ""
echo "3. Verifying updated files..."
if grep -q "gas.*deque" main.py; then
    echo "   ✓ main.py includes gas history tracking"
else
    echo "   ✗ main.py missing gas history - please pull again"
    exit 1
fi

if grep -q "always return gas_resistance" sensor.py; then
    echo "   ✓ sensor.py configured for VOC readings"
else
    echo "   ✗ sensor.py not updated - please pull again"
    exit 1
fi

if grep -q "gas_history" display_forest_rings.py; then
    echo "   ✓ display_forest_rings.py has VOC support"
else
    echo "   ✗ display_forest_rings.py not updated"
    exit 1
fi

# Start the service
echo ""
echo "4. Starting rake-sensor service..."
sudo systemctl start rake-sensor.service
sleep 3

# Check service status
echo ""
echo "5. Service status:"
sudo systemctl is-active rake-sensor.service

# Show the screen should display forest rings with VOC
echo ""
echo "================================================"
echo "Forest Rings GUI should now be showing!"
echo "================================================"
echo ""
echo "The display should show:"
echo "• Temperature and Humidity rings (top row)"  
echo "• Pressure and Air Quality (VOC) rings (bottom row)"
echo ""
echo "Gas sensor readings will appear in bottom-right ring."
echo "Values stabilize after 5-10 minutes of continuous operation."
echo ""
echo "To monitor VOC readings in terminal:"
echo "sudo journalctl -u rake-sensor.service -f | grep -i gas"
echo ""
echo "Press Ctrl+C to stop monitoring logs"

# Follow logs filtered for gas readings
sudo journalctl -u rake-sensor.service -f | grep --line-buffered -i "gas\|error\|failed"
