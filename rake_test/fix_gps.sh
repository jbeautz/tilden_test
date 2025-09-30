#!/bin/bash
# GPS Port Cleanup Script - Fixes "multiple access on port" errors
# Run this to fix GPS port conflicts

echo "🛰️  GPS Port Cleanup - Fixing Multiple Access Errors"
echo "=================================================="

GPS_PORT="/dev/serial0"

echo "📡 Checking processes using GPS port..."

# Check what processes are using the GPS port
PROCESSES=$(sudo fuser $GPS_PORT 2>/dev/null)

if [ -n "$PROCESSES" ]; then
    echo "⚠️  Found processes using $GPS_PORT: $PROCESSES"
    echo "🔧 Terminating processes..."
    sudo fuser -k $GPS_PORT
    sleep 2
    echo "✅ Processes terminated"
else
    echo "✅ No processes currently using $GPS_PORT"
fi

# Check if port is accessible
echo "🔍 Testing port accessibility..."
if [ -c "$GPS_PORT" ]; then
    echo "✅ GPS port $GPS_PORT exists and is accessible"
    ls -la $GPS_PORT
else
    echo "❌ GPS port $GPS_PORT not found"
    echo "📋 Current serial port status:"
    sudo raspi-config nonint get_serial
    sudo raspi-config nonint get_serial_hw
    echo ""
    
    # Disable serial console (frees up /dev/serial0 for GPS)
    echo "🗣️ Disabling serial console..."
    sudo raspi-config nonint do_serial_cons 1
    
    # Enable serial port hardware
    echo "📡 Enabling serial hardware..."
    sudo raspi-config nonint do_serial_hw 0
fi

# Clear any stale locks
echo "🧹 Clearing any stale locks..."
sudo rm -f /var/lock/LCK..ttyAMA0 2>/dev/null
sudo rm -f /var/lock/LCK..serial0 2>/dev/null
echo "✅ Locks cleared"

# Test quick GPS read
echo "📡 Testing GPS data reception..."
timeout 3s sudo cat $GPS_PORT 2>/dev/null | head -5 || echo "No immediate GPS data (this is normal if GPS is cold starting)"

echo ""
echo "=================================================="
echo "🎉 GPS port cleanup complete!"
echo ""
echo "Now you can run your GPS applications:"
echo "   python main.py"
echo "   python diagnose_gps.py"
echo ""
echo "If you still get 'multiple access' errors:"
echo "   1. Reboot the Pi: sudo reboot"
echo "   2. Or run this script again: ./fix_gps.sh"
echo "=================================================="
fi

# Check what serial devices exist
echo "🔍 Available serial devices:"
ls -la /dev/tty* | grep -E "(USB|AMA|S0|S1|serial)"
echo ""

# Check if serial0 exists after changes
if [ -e /dev/serial0 ]; then
    echo "✅ /dev/serial0 exists"
    ls -la /dev/serial0
else
    echo "❌ /dev/serial0 not found"
    echo "Available alternatives:"
    ls -la /dev/ttyAMA* /dev/ttyS* 2>/dev/null || echo "No UART devices found"
fi

echo ""
echo "🔄 You need to reboot for serial changes to take effect:"
echo "   sudo reboot"
echo ""
echo "After reboot, test GPS with:"
echo "   sudo cat /dev/serial0  # Should show NMEA sentences"
echo "   sudo chmod 666 /dev/serial0  # If permission denied"
