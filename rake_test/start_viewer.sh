#!/bin/bash
# Launcher script for Tilden Data Viewer

# Change to project directory
cd /home/pi/tilden_test/rake_test || exit 1

# Set display environment
export DISPLAY=:0

echo "Starting Tilden Data Viewer..."

# Run the viewer
python3 data_viewer.py

echo "Viewer closed."
