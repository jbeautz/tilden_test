#!/bin/bash
# Start Forest Rings GUI with proper SDL video driver

# Set SDL video driver BEFORE running Python
export SDL_VIDEODRIVER=kmsdrm
export SDL_FBDEV=/dev/fb0

# Disable SDL mouse cursor (use touch instead)
export SDL_NOMOUSE=1

echo "🎮 Starting Forest Rings with SDL driver: $SDL_VIDEODRIVER"

cd ~/tilden_test/rake_test
exec python3 main.py "$@"
