#!/bin/bash
# Find and configure display settings in raspi-config

echo "🔧 Finding display configuration options..."

# Check Raspberry Pi OS version
echo "📋 System Version:"
cat /etc/os-release | grep -E "(PRETTY_NAME|VERSION)"
echo ""

# Check current GPU/display settings
echo "🖥️ Current GPU Settings:"
vcgencmd get_config int | grep -E "(gpu_mem|display|hdmi|framebuffer)" || echo "vcgencmd not available"
echo ""

# Show current boot config display settings
echo "📺 Current /boot/config.txt display settings:"
grep -E "^[^#]*(display|hdmi|gpu|framebuffer|lcd|ignore_lcd)" /boot/config.txt 2>/dev/null || echo "No display settings found"
echo ""

echo "🛠️ Manual raspi-config navigation:"
echo "Try these menu paths (varies by Pi OS version):"
echo ""
echo "Option A - Newer Pi OS:"
echo "  sudo raspi-config"
echo "  → 7 Advanced Options → A2 GL Driver → G1 Legacy"
echo ""
echo "Option B - Older Pi OS:"
echo "  sudo raspi-config" 
echo "  → 6 Advanced Options → GL Driver → Legacy"
echo ""
echo "Option C - Some versions:"
echo "  sudo raspi-config"
echo "  → System Options → Boot/Auto Login → Desktop"
echo ""
echo "🔧 Manual configuration (if raspi-config doesn't work):"
echo "Add these lines to /boot/config.txt:"
echo ""
echo "# Enable DSI display"
echo "ignore_lcd=0"
echo "disable_overscan=1"
echo ""
echo "# Force framebuffer size for 800x480 display"
echo "framebuffer_width=800"
echo "framebuffer_height=480"
echo ""
echo "# Alternative: Force HDMI if DSI not working"
echo "# hdmi_force_hotplug=1"
echo "# hdmi_group=2"
echo "# hdmi_mode=87"
echo "# hdmi_cvt=800 480 60 6 0 0 0"
echo ""

echo "Would you like me to add DSI display settings to /boot/config.txt? (y/n)"
read -p "Enter choice: " choice

if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo "Adding DSI display configuration..."
    
    # Backup current config
    sudo cp /boot/config.txt /boot/config.txt.backup
    
    # Add DSI settings if not present
    if ! grep -q "ignore_lcd" /boot/config.txt; then
        echo "" | sudo tee -a /boot/config.txt
        echo "# DSI Display Configuration" | sudo tee -a /boot/config.txt
        echo "ignore_lcd=0" | sudo tee -a /boot/config.txt
        echo "disable_overscan=1" | sudo tee -a /boot/config.txt
        echo "framebuffer_width=800" | sudo tee -a /boot/config.txt
        echo "framebuffer_height=480" | sudo tee -a /boot/config.txt
        echo "✅ DSI display settings added to /boot/config.txt"
    else
        echo "⚠️ DSI settings already present in config.txt"
    fi
    
    echo ""
    echo "🔄 Reboot required: sudo reboot"
else
    echo "❌ Skipping automatic configuration"
fi
