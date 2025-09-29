#!/bin/bash
# Diagnostic script to check display and service status

echo "🔍 Checking display and service status..."

# Check if service is running
echo "📊 Service Status:"
sudo systemctl is-active rake-sensor.service
sudo systemctl status rake-sensor.service --no-pager -l | head -10

echo ""
echo "📺 Display Information:"
# Check what displays are available
echo "Available displays:"
ls -la /dev/fb* 2>/dev/null || echo "No framebuffer devices found"

# Check if X server is running
echo "X Server processes:"
ps aux | grep -E "(Xorg|startx|xinit)" | grep -v grep || echo "No X server found"

# Check current display settings
echo "Current DISPLAY environment:"
echo "DISPLAY=$DISPLAY"

echo ""
echo "🖥️ Testing direct framebuffer access:"
# Test if we can write to framebuffer
if [ -w /dev/fb0 ]; then
    echo "✅ Framebuffer /dev/fb0 is writable"
else
    echo "❌ Framebuffer /dev/fb0 not writable"
    echo "Permissions:"
    ls -la /dev/fb0 2>/dev/null || echo "fb0 not found"
fi

echo ""
echo "🔧 Service Environment Check:"
# Show actual service environment
sudo systemctl show rake-sensor.service -p Environment

echo ""
echo "📋 Recent service logs (last 20 lines):"
sudo journalctl -u rake-sensor.service --no-pager -n 20
