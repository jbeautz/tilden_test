#!/bin/bash
# Script to run the GUI directly on the Pi's physical display
# Use this instead of running main.py via SSH

echo "🖥️ Starting GUI on physical Pi display..."

# Set environment for local display
export DISPLAY=:0
export SDL_VIDEODRIVER=fbcon
export SDL_FBDEV=/dev/fb0
export SDL_AUDIODRIVER=dummy

# Navigate to project directory
cd ~/tilden_test/rake_test

# Activate virtual environment
source .venv/bin/activate

# Run the GUI application
python main.py
