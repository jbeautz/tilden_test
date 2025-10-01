#!/bin/bash
# Start Forest Rings GUI with proper SDL video driver

export SDL_VIDEODRIVER=kmsdrm
export SDL_FBDEV=/dev/fb0

cd ~/tilden_test/rake_test
python3 main.py "$@"
