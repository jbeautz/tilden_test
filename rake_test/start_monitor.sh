#!/bin/bash
# Launcher script for Soil Monitor

# Change to project directory
cd /home/pi/tilden_test/rake_test || exit 1

# Set display environment
export DISPLAY=:0
export SDL_AUDIODRIVER=dummy

echo "================================================"
echo "Starting Soil Monitor..."
echo "================================================"
echo ""
echo "Press Ctrl+C to stop monitoring"
echo ""

# Run the main program
python3 main.py

echo ""
echo "Monitor stopped."
read -p "Press Enter to close..." 
