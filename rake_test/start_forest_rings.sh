#!/bin/bash
# Start Forest Rings GUI with proper SDL video driver

# Use dummy driver (which still outputs to framebuffer on Pi)
# This works because the vc4 DRM driver renders to fb0 automatically
export SDL_VIDEODRIVER=dummy
export SDL_FBDEV=/dev/fb0
export SDL_NOMOUSE=1

echo "🎮 Starting Soil Monitor (dummy driver with framebuffer output)"

cd ~/tilden_test/rake_test
exec python3 main.py "$@"
