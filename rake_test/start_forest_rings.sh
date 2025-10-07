#!/bin/bash
# Start Forest Rings GUI with proper SDL video driver
# Wait for graphics subsystem to be ready when run at boot

MAX_WAIT=60
WAIT_TIME=0

echo "Checking if graphics subsystem is ready..."

# Wait for /dev/fb0 to be accessible
while [ $WAIT_TIME -lt $MAX_WAIT ]; do
    if [ -c /dev/fb0 ] && [ -r /dev/fb0 ] && [ -w /dev/fb0 ]; then
        echo "✓ /dev/fb0 is accessible"
        break
    fi
    echo "  Waiting for /dev/fb0... ($WAIT_TIME seconds)"
    sleep 2
    WAIT_TIME=$((WAIT_TIME + 2))
done

# Wait for DRM device to be ready
WAIT_TIME=0
while [ $WAIT_TIME -lt $MAX_WAIT ]; do
    if [ -c /dev/dri/card0 ] && [ -r /dev/dri/card0 ]; then
        echo "✓ /dev/dri/card0 is accessible"
        break
    fi
    echo "  Waiting for DRM device... ($WAIT_TIME seconds)"
    sleep 2
    WAIT_TIME=$((WAIT_TIME + 2))
done

# Additional wait to ensure video subsystem is fully initialized
echo "Waiting additional 5 seconds for video subsystem initialization..."
sleep 5

echo "✓ Graphics subsystem ready"

# Use kmsdrm driver for DSI display (renders graphics properly)
# The quit-ignoring code in main.py prevents spurious QUIT events from exiting
export SDL_VIDEODRIVER=kmsdrm
export SDL_FBDEV=/dev/fb0
export SDL_NOMOUSE=1

echo "🎮 Starting Soil Monitor (kmsdrm driver for graphics)"

cd ~/tilden_test/rake_test

# Activate virtual environment to get BME680 library
if [ -d "myproject-venv" ]; then
    echo "✓ Activating virtual environment"
    source myproject-venv/bin/activate
else
    echo "⚠ Virtual environment not found, using system python"
fi

exec python3 main.py "$@"
