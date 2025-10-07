#!/bin/bash
# Verify VOC sensor is working

echo "================================================"
echo "BME680 VOC Sensor Verification"
echo "================================================"
echo ""

# Check service status
echo "1. Service Status:"
STATUS=$(sudo systemctl is-active rake-sensor.service)
if [ "$STATUS" = "active" ]; then
    echo "   ✓ Service is running"
else
    echo "   ✗ Service is NOT running (status: $STATUS)"
    exit 1
fi
echo ""

# Check recent logs for gas readings
echo "2. Checking for gas sensor readings in logs..."
RECENT_GAS=$(sudo journalctl -u rake-sensor.service --since "5 minutes ago" | grep -i "gas sensor" | tail -3)
if [ -n "$RECENT_GAS" ]; then
    echo "   ✓ Gas sensor is reporting values:"
    echo "$RECENT_GAS" | sed 's/^/     /'
else
    echo "   ⚠ No gas sensor messages in last 5 minutes"
    echo "   (This is normal after warm-up completes)"
fi
echo ""

# Check log file for gas data
echo "3. Checking CSV log file for gas data..."
LATEST_LOG=$(ls -t ~/tilden_test/rake_test/rake_log_*.csv 2>/dev/null | head -1)
if [ -n "$LATEST_LOG" ]; then
    echo "   Latest log: $(basename $LATEST_LOG)"
    
    # Check if gas column has values (not empty)
    GAS_VALUES=$(tail -10 "$LATEST_LOG" | cut -d',' -f5 | grep -v '^$' | grep -v 'gas' | wc -l)
    if [ "$GAS_VALUES" -gt 0 ]; then
        echo "   ✓ Gas column has $GAS_VALUES values in last 10 rows"
        echo ""
        echo "   Recent gas readings (kΩ):"
        tail -5 "$LATEST_LOG" | cut -d',' -f1,5 | while IFS=',' read timestamp gas; do
            if [ -n "$gas" ] && [ "$gas" != "gas" ]; then
                gas_kohm=$(echo "scale=1; $gas / 1000" | bc 2>/dev/null || echo "N/A")
                echo "     $timestamp: ${gas_kohm} kΩ"
            fi
        done
    else
        echo "   ✗ Gas column is empty in last 10 rows"
        echo "   Sensor may still be warming up (takes 5-10 minutes)"
    fi
else
    echo "   ✗ No log file found"
fi
echo ""

# Check display file for gas_history
echo "4. Checking display configuration..."
if grep -q "gas_history" ~/tilden_test/rake_test/display_forest_rings.py; then
    echo "   ✓ Display configured to show gas/VOC data"
else
    echo "   ✗ Display NOT configured for gas data"
    echo "   Need to update display_forest_rings.py"
fi
echo ""

# Summary
echo "================================================"
echo "Summary"
echo "================================================"
echo ""

if [ "$STATUS" = "active" ] && [ "$GAS_VALUES" -gt 0 ]; then
    echo "✓ VOC sensor is working correctly!"
    echo ""
    echo "Current air quality readings available in:"
    echo "  - Log file: $LATEST_LOG"
    echo "  - Display: 4th tree ring (bottom-right)"
    echo ""
    echo "Gas resistance interpretation:"
    echo "  > 100 kΩ = Excellent air quality"
    echo "  50-100 kΩ = Good (normal indoor)"
    echo "  20-50 kΩ = Moderate"
    echo "  < 20 kΩ = Poor (high VOC concentration)"
elif [ "$GAS_VALUES" -eq 0 ]; then
    echo "⚠ Sensor is warming up"
    echo ""
    echo "The BME680 gas sensor needs 5-10 minutes to stabilize."
    echo "Run this script again in a few minutes."
    echo ""
    echo "To watch live updates:"
    echo "  sudo journalctl -u rake-sensor.service -f"
else
    echo "✗ Issue detected"
    echo ""
    echo "Please check:"
    echo "  1. Files were updated correctly"
    echo "  2. Service restarted after updates"
    echo "  3. BME680 sensor is properly connected"
fi
echo ""
