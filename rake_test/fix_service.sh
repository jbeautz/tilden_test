#!/bin/bash
# Quick fix for the service file path issue

echo "🔧 Fixing service configuration..."

# Stop the failing service
sudo systemctl stop rake-sensor.service

# Fix the ExecStart path to use main.py instead of rake_sensor.py
sudo sed -i 's|rake_sensor.py|main.py|g' /etc/systemd/system/rake-sensor.service

# Reload systemd
sudo systemctl daemon-reload

# Show the corrected service file
echo "📄 Updated service configuration:"
grep "ExecStart" /etc/systemd/system/rake-sensor.service

# Reset the restart counter
sudo systemctl reset-failed rake-sensor.service

# Start the service
echo "🚀 Starting corrected service..."
sudo systemctl start rake-sensor.service

# Check status
echo "📊 Service status:"
sudo systemctl status rake-sensor.service --no-pager -l

echo ""
echo "✅ If service is now active, the GUI should appear on your Pi display"
echo "📋 Monitor logs with: sudo journalctl -u rake-sensor -f"
