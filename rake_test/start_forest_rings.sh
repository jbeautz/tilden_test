#!/bin/bash
# Start Forest Rings GUI with proper SDL video driver

# Use kmsdrm driver for DSI display (renders graphics properly)
# The quit-ignoring code in main.py prevents spurious QUIT events from exiting
export SDL_VIDEODRIVER=kmsdrm
export SDL_FBDEV=/dev/fb0
export SDL_NOMOUSE=1

echo "🎮 Starting Soil Monitor (kmsdrm driver for graphics)"

cd ~/tilden_test/rake_test
exec python3 main.py "$@"
