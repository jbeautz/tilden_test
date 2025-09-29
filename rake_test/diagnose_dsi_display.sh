#!/bin/bash
# Check DSI display configuration and force proper display setup

echo "🔍 DSI Display Configuration Check"
echo "=================================="

# Check current framebuffer devices
echo "📺 Framebuffer devices:"
ls -la /dev/fb* 2>/dev/null || echo "No framebuffer devices found"

# Check framebuffer info
for fb in /dev/fb*; do
    if [ -e "$fb" ]; then
        echo ""
        echo "Device: $fb"
        fbset -i -fb "$fb" 2>/dev/null || echo "Cannot read fbset info"
        if [ -e "/sys/class/graphics/$(basename $fb)/virtual_size" ]; then
            echo "Virtual size: $(cat /sys/class/graphics/$(basename $fb)/virtual_size)"
        fi
        if [ -e "/sys/class/graphics/$(basename $fb)/modes" ]; then
            echo "Modes: $(cat /sys/class/graphics/$(basename $fb)/modes)"
        fi
    fi
done

# Check boot config for display settings
echo ""
echo "📋 Boot configuration (/boot/config.txt):"
grep -E "^[^#]*(display|hdmi|gpu|framebuffer|lcd|ignore_lcd|dtoverlay.*vc4)" /boot/config.txt 2>/dev/null || echo "No display settings found"

# Check for DSI display overlays
echo ""
echo "🔌 Display overlays:"
dtoverlay -l 2>/dev/null || echo "Cannot list overlays"

echo ""
echo "🛠️ Recommended fixes:"
echo ""
echo "1. Add DSI display overlay to /boot/config.txt:"
echo "   dtoverlay=vc4-kms-v3d"
echo "   dtoverlay=vc4-kms-dsi-7inch"  # For 7-inch DSI
echo ""
echo "2. Or try generic DSI settings:"
echo "   ignore_lcd=0"
echo "   lcd_rotate=2"
echo ""
echo "3. Force framebuffer setup:"
echo "   framebuffer_width=800"
echo "   framebuffer_height=480"
echo ""

# Test if we can write to framebuffer directly
echo "🧪 Testing direct framebuffer write:"
if [ -w /dev/fb0 ]; then
    echo "Framebuffer is writable - testing pattern..."
    # Fill screen with test pattern
    sudo dd if=/dev/zero of=/dev/fb0 bs=1024 count=1200 2>/dev/null && echo "✅ Framebuffer write successful"
else
    echo "❌ Framebuffer not writable"
fi

echo ""
echo "Would you like to add DSI display settings to /boot/config.txt? (y/n)"
