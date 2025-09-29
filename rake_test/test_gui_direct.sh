#!/bin/bash
# Test GUI directly on console without X11

echo "🖥️ Testing GUI directly on console..."

# Stop any X11 services
sudo systemctl stop lightdm 2>/dev/null || true
sudo pkill Xorg 2>/dev/null || true

# Stop the failing service
sudo systemctl stop rake-sensor.service

# Run GUI manually to test display methods
cd ~/tilden_test/rake_test
source .venv/bin/activate

echo "🚀 Starting GUI manually..."
echo "The updated display.py should try multiple display methods:"
echo "- X11 (if available)"
echo "- Framebuffer (if configured)" 
echo "- DirectFB (alternative)"
echo "- Dummy (invisible fallback)"
echo ""

# Run with output to see which display method works
python main.py

echo ""
echo "📋 If GUI started successfully, you should see it on your Pi display"
echo "🔄 Press Ctrl+C to stop and return to console"
