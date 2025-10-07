#!/bin/bash
# Apply cleanup and BME680 fix

set -e  # Exit on error

echo "=========================================="
echo "Applying Soil Monitor Fixes"
echo "=========================================="
echo ""

# 1. Clean up old log files
echo "1️⃣  Cleaning up old/empty log files..."
cd ~/tilden_test/rake_test
find . -name "rake_log_*.csv" -type f -size -10k -ls
echo ""
read -p "Delete these files? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    find . -name "rake_log_*.csv" -type f -size -10k -delete
    echo "✓ Old log files deleted"
else
    echo "⊘ Skipped cleanup"
fi
echo ""

# 2. Update systemd service
echo "2️⃣  Updating systemd service to use virtual environment..."
sudo cp rake-sensor-fixed.service /etc/systemd/system/rake-sensor.service
sudo systemctl daemon-reload
echo "✓ Service file updated"
echo ""

# 3. Restart service
echo "3️⃣  Restarting service..."
sudo systemctl restart rake-sensor.service
echo "✓ Service restarted"
echo ""

# 4. Check status
echo "4️⃣  Service status:"
sudo systemctl status rake-sensor.service --no-pager -l | head -20
echo ""

# 5. Wait and check logs
echo "5️⃣  Checking for BME680 sensor data (waiting 5 seconds)..."
sleep 5
echo ""
sudo journalctl -u rake-sensor.service -n 10 --no-pager
echo ""

echo "=========================================="
echo "✓ Fixes applied!"
echo "=========================================="
echo ""
echo "To monitor the service:"
echo "  sudo journalctl -u rake-sensor.service -f"
echo ""
echo "Remaining log files:"
ls -lht rake_log_*.csv | head -5
