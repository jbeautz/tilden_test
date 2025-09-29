#!/bin/bash
# Start X11 server and then the GUI service

echo "🖥️ Starting X11 server for GUI display..."

# Check if X server is already running
if ! pgrep Xorg > /dev/null; then
    echo "Starting X server..."
    # Start X server in background
    sudo systemctl start lightdm 2>/dev/null || {
        # If no display manager, start X manually
        startx &
        sleep 3
    }
else
    echo "X server already running"
fi

# Wait for X to be ready
sleep 2

# Set DISPLAY for current session
export DISPLAY=:0

# Restart the GUI service with proper environment
echo "🚀 Starting GUI service..."
sudo systemctl stop rake-sensor.service 2>/dev/null || true
sudo systemctl start rake-sensor.service

echo "📊 Service status:"
sudo systemctl status rake-sensor.service --no-pager -l

echo ""
echo "📋 Service logs:"
sudo journalctl -u rake-sensor.service --no-pager -n 10

echo ""
echo "✅ If X11 is running, the GUI should now appear on your display!"
echo "🔍 Check processes: ps aux | grep -E '(Xorg|python.*main)'"
