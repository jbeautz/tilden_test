#!/bin/bash
# Comprehensive display diagnostics and fixes

echo "🔧 Pi Display Configuration Diagnostics"
echo "========================================"

# Check Pi model and OS
echo "📋 System Info:"
cat /proc/device-tree/model 2>/dev/null || echo "Model info not available"
uname -a

echo ""
echo "🖥️ Display Hardware Check:"
# Check for DSI display
ls -la /sys/class/graphics/fb* 2>/dev/null || echo "No framebuffer devices in sysfs"

# Check framebuffer info
if [ -e /dev/fb0 ]; then
    echo "fb0 device info:"
    fbset -i -fb /dev/fb0 2>/dev/null || echo "fbset not available"
    cat /sys/class/graphics/fb0/virtual_size 2>/dev/null || echo "Virtual size not available"
    cat /sys/class/graphics/fb0/modes 2>/dev/null || echo "Modes not available"
fi

echo ""
echo "📺 Display Configuration:"
# Check boot config
echo "Boot config relevant settings:"
grep -E "^(display_|hdmi_|disable_overscan|framebuffer_)" /boot/config.txt 2>/dev/null || echo "No display settings in config.txt"

# Check display service
echo ""
echo "Display service status:"
tvservice -s 2>/dev/null || echo "tvservice not available"

echo ""
echo "🔍 Available Video Drivers:"
# List SDL video drivers
SDL_VIDEODRIVER=dummy python3 -c "
import pygame
import os
pygame.init()
print('SDL Version:', pygame.version.ver)
# Try different drivers
for driver in ['fbcon', 'directfb', 'svgalib', 'dga', 'x11', 'dummy']:
    try:
        os.environ['SDL_VIDEODRIVER'] = driver
        pygame.display.quit()
        pygame.display.init()
        print(f'{driver}: available')
    except:
        print(f'{driver}: not available')
pygame.quit()
"

echo ""
echo "🛠️ Suggested Fixes:"
echo "1. Enable DSI display in raspi-config:"
echo "   sudo raspi-config → Advanced Options → GL Driver → Legacy"
echo ""
echo "2. Add to /boot/config.txt if using DSI display:"
echo "   ignore_lcd=0"
echo "   lcd_rotate=2  # if display is upside down"
echo ""
echo "3. Alternative: Enable fake framebuffer for testing:"
echo "   sudo modprobe vfb vfb_enable=1"
echo ""
echo "4. Check if X server should be used instead:"
echo "   startx  # if desktop environment is available"
