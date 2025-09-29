#!/bin/bash
# Quick GPS serial port fix for Raspberry Pi
# Run this to enable serial port for GPS module

echo "🔧 Configuring serial port for GPS..."

# Check current serial configuration
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
