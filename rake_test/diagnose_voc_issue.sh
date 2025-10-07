#!/bin/bash
# Diagnose VOC display issue

echo "================================================"
echo "Diagnosing VOC Display Issue"
echo "================================================"
echo ""

echo "1. Service Status:"
sudo systemctl status rake-sensor.service --no-pager -l | head -30
echo ""

echo "2. Recent Error Logs:"
sudo journalctl -u rake-sensor.service -n 50 --no-pager | tail -30
echo ""

echo "3. Checking if display is running:"
ps aux | grep -E "python.*main.py|python.*display" | grep -v grep
echo ""

echo "4. Testing sensor.py directly:"
cd /home/pi/tilden_test/rake_test
python3 -c "from sensor import read_sensor; print(read_sensor())"
echo ""

echo "5. Checking X display:"
echo "DISPLAY=$DISPLAY"
echo ""

echo "================================================"
echo "To restart service manually:"
echo "sudo systemctl restart rake-sensor.service"
echo ""
echo "To watch live logs:"
echo "sudo journalctl -u rake-sensor.service -f"
echo "================================================"
