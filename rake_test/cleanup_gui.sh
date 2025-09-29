#!/bin/bash
# Script to clean up multiple GUI instances and restart properly

echo "🧹 Cleaning up multiple GUI instances..."

# Stop the systemd service
echo "Stopping systemd service..."
sudo systemctl stop rake-sensor.service

# Kill any remaining python main.py processes
echo "Killing existing GUI processes..."
sudo pkill -f "python.*main.py" || echo "No processes to kill"

# Wait a moment
sleep 2

# Check if processes are gone
if pgrep -f "python.*main.py" > /dev/null; then
    echo "⚠️  Some processes still running, force killing..."
    sudo pkill -9 -f "python.*main.py"
    sleep 1
fi

# Show current status
echo "📊 Current python processes:"
ps aux | grep python | grep -v grep || echo "No python processes found"

echo ""
echo "✅ Cleanup complete. Now choose one option:"
echo ""
echo "Option 1 - Start via systemd service (recommended for auto-start):"
echo "   sudo systemctl start rake-sensor.service"
echo "   sudo journalctl -u rake-sensor -f"
echo ""
echo "Option 2 - Run manually for testing:"
echo "   source .venv/bin/activate"
echo "   DISPLAY=:0 SDL_VIDEODRIVER=fbcon SDL_FBDEV=/dev/fb0 python main.py"
echo ""
echo "📺 The GUI should appear on your Pi's physical display, not via SSH"
