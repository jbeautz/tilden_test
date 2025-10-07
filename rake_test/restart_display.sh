#!/bin/bash
# Simple restart script to restore forest rings display

echo "Stopping service..."
sudo systemctl stop rake-sensor.service
sleep 2

echo "Starting service..."
sudo systemctl start rake-sensor.service
sleep 3

echo ""
echo "Service Status:"
sudo systemctl status rake-sensor.service --no-pager | head -15

echo ""
echo "============================================"
echo "If you see a black screen, check logs with:"
echo "sudo journalctl -u rake-sensor.service -f"
echo "============================================"
