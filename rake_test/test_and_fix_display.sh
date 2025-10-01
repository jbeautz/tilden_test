#!/bin/bash
# Comprehensive Display Fix and Test Script for Raspberry Pi DSI Display
# Tests multiple approaches to get pygame working with 5" 800x480 DSI display

echo "🖥️  Display Fix and Test Script"
echo "=" * 60

# Step 1: Check display hardware detection
echo -e "\n📋 Step 1: Checking display hardware..."
if [ -e /dev/fb0 ]; then
    echo "✅ Framebuffer device /dev/fb0 exists"
    if [ -r /sys/class/graphics/fb0/virtual_size ]; then
        SIZE=$(cat /sys/class/graphics/fb0/virtual_size)
        echo "✅ Display resolution: $SIZE"
    fi
else
    echo "❌ No framebuffer device found!"
fi

# Check for DSI display in dmesg
echo -e "\n🔍 Checking kernel logs for display..."
sudo dmesg | grep -i "dsi\|display\|fb0" | tail -5

# Step 2: Check current display configuration
echo -e "\n⚙️  Step 2: Checking display configuration..."
echo "Current config.txt display settings:"
grep -E "display|framebuffer|hdmi|dtoverlay.*v3d" /boot/firmware/config.txt 2>/dev/null || echo "No display settings found"

# Step 3: Test direct framebuffer access
echo -e "\n🎨 Step 3: Testing direct framebuffer access..."
python3 << 'PYEND'
import os, struct, mmap

try:
    # Get framebuffer info
    with open("/sys/class/graphics/fb0/virtual_size", "r") as f:
        width, height = map(int, f.read().strip().split(","))
    
    print(f"Framebuffer: {width}x{height}")
    
    # Try to open framebuffer
    with open("/dev/fb0", "r+b") as fb:
        fb_size = width * height * 2  # 16 bits per pixel
        print("✅ Direct framebuffer access works!")
        print("   Display hardware is functional")
except Exception as e:
    print(f"❌ Direct framebuffer failed: {e}")
PYEND

# Step 4: Test pygame with different drivers
echo -e "\n🎮 Step 4: Testing pygame display drivers..."
cd ~/tilden_test/rake_test
source myproject-venv/bin/activate 2>/dev/null || true

python3 << 'PYEND'
import pygame
import os
import sys

drivers_to_test = ['fbdev', 'fbcon', 'kmsdrm', 'directfb', 'dummy']
working_drivers = []

for driver in drivers_to_test:
    try:
        os.environ['SDL_VIDEODRIVER'] = driver
        os.environ['SDL_FBDEV'] = '/dev/fb0'
        
        pygame.quit()
        pygame.init()
        pygame.display.init()
        
        screen = pygame.display.set_mode((800, 480))
        actual_driver = pygame.display.get_driver()
        
        print(f"✅ {driver:12} -> {actual_driver:12} SUCCESS")
        
        if actual_driver != 'dummy':
            working_drivers.append((driver, actual_driver))
        
        pygame.quit()
        
    except Exception as e:
        print(f"❌ {driver:12} -> FAILED: {e}")
        pygame.quit()

print(f"\n📊 Working drivers (non-dummy): {len(working_drivers)}")
for req, actual in working_drivers:
    print(f"   {req} -> {actual}")

if not working_drivers:
    print("⚠️  Only dummy driver works - display configuration needed")
PYEND

# Step 5: Check permissions
echo -e "\n🔐 Step 5: Checking framebuffer permissions..."
ls -l /dev/fb0

# Step 6: Suggest fixes based on findings
echo -e "\n" "=" * 60
echo "🔧 DISPLAY FIX OPTIONS:"
echo "=" * 60

echo -e "\n💡 Option 1: Enable KMS display driver (recommended)"
echo "   Run: sudo nano /boot/firmware/config.txt"
echo "   Ensure these lines are present and uncommented:"
echo "     dtoverlay=vc4-kms-v3d"
echo "     max_framebuffers=2"
echo "     display_auto_detect=1"
echo "   Then: sudo reboot"

echo -e "\n💡 Option 2: Force legacy framebuffer mode"
echo "   Run: sudo nano /boot/firmware/config.txt"
echo "   Comment out KMS driver:"
echo "     #dtoverlay=vc4-kms-v3d"
echo "   Add framebuffer settings:"
echo "     framebuffer_width=800"
echo "     framebuffer_height=480"
echo "   Then: sudo reboot"

echo -e "\n💡 Option 3: Fix framebuffer permissions"
echo "   Run: sudo chmod 666 /dev/fb0"
echo "   Or permanently:"
echo "     sudo tee /etc/udev/rules.d/99-framebuffer.rules << EOF"
echo "     SUBSYSTEM==\"graphics\", KERNEL==\"fb0\", MODE=\"0666\""
echo "     EOF"
echo "     sudo udevadm control --reload-rules"

echo -e "\n💡 Option 4: Run with sudo (temporary workaround)"
echo "   sudo python3 main.py"

echo -e "\n💡 Option 5: Use environment variables"
echo "   SDL_VIDEODRIVER=fbdev SDL_FBDEV=/dev/fb0 python3 main.py"

# Step 7: Create automated fix scripts
echo -e "\n📝 Creating automated fix scripts..."

# Create KMS fix script
cat > fix_display_kms.sh << 'KMSEND'
#!/bin/bash
# Enable KMS display driver for DSI

echo "Enabling KMS display driver..."

# Backup config
sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.backup.$(date +%s)

# Remove any conflicting settings
sudo sed -i 's/^framebuffer_width/#framebuffer_width/' /boot/firmware/config.txt
sudo sed -i 's/^framebuffer_height/#framebuffer_height/' /boot/firmware/config.txt

# Ensure KMS driver is enabled
if ! grep -q "^dtoverlay=vc4-kms-v3d" /boot/firmware/config.txt; then
    echo "dtoverlay=vc4-kms-v3d" | sudo tee -a /boot/firmware/config.txt
fi

if ! grep -q "^max_framebuffers=" /boot/firmware/config.txt; then
    echo "max_framebuffers=2" | sudo tee -a /boot/firmware/config.txt
fi

if ! grep -q "^display_auto_detect=" /boot/firmware/config.txt; then
    echo "display_auto_detect=1" | sudo tee -a /boot/firmware/config.txt
fi

echo "✅ KMS display driver enabled"
echo "⚠️  Reboot required: sudo reboot"
KMSEND
chmod +x fix_display_kms.sh

# Create legacy framebuffer fix script
cat > fix_display_legacy.sh << 'LEGACYEND'
#!/bin/bash
# Use legacy framebuffer mode for DSI

echo "Configuring legacy framebuffer mode..."

# Backup config
sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.backup.$(date +%s)

# Disable KMS driver
sudo sed -i 's/^dtoverlay=vc4-kms-v3d/#dtoverlay=vc4-kms-v3d/' /boot/firmware/config.txt
sudo sed -i 's/^dtoverlay=vc4-fkms-v3d/#dtoverlay=vc4-fkms-v3d/' /boot/firmware/config.txt

# Add framebuffer settings
if ! grep -q "^framebuffer_width=800" /boot/firmware/config.txt; then
    echo "framebuffer_width=800" | sudo tee -a /boot/firmware/config.txt
fi

if ! grep -q "^framebuffer_height=480" /boot/firmware/config.txt; then
    echo "framebuffer_height=480" | sudo tee -a /boot/firmware/config.txt
fi

if ! grep -q "^display_auto_detect=1" /boot/firmware/config.txt; then
    echo "display_auto_detect=1" | sudo tee -a /boot/firmware/config.txt
fi

echo "✅ Legacy framebuffer mode enabled"
echo "⚠️  Reboot required: sudo reboot"
LEGACYEND
chmod +x fix_display_legacy.sh

# Create permissions fix script
cat > fix_display_permissions.sh << 'PERMEND'
#!/bin/bash
# Fix framebuffer permissions

echo "Fixing framebuffer permissions..."

# Immediate fix
sudo chmod 666 /dev/fb0
echo "✅ Set /dev/fb0 permissions to 666"

# Persistent fix with udev rule
sudo tee /etc/udev/rules.d/99-framebuffer.rules > /dev/null << 'EOF'
# Framebuffer permissions for pygame
SUBSYSTEM=="graphics", KERNEL=="fb0", MODE="0666", GROUP="video"
SUBSYSTEM=="graphics", KERNEL=="fb*", MODE="0666", GROUP="video"
EOF

# Add user to video group
sudo usermod -a -G video $USER

# Reload udev
sudo udevadm control --reload-rules
sudo udevadm trigger

echo "✅ Created persistent udev rule"
echo "✅ Added user to video group"
echo "ℹ️  Log out and back in for group changes to take effect"
PERMEND
chmod +x fix_display_permissions.sh

echo "✅ Created fix_display_kms.sh"
echo "✅ Created fix_display_legacy.sh"
echo "✅ Created fix_display_permissions.sh"

# Step 8: Provide recommendations
echo -e "\n" "=" * 60
echo "📋 RECOMMENDED ACTIONS:"
echo "=" * 60

echo -e "\n1️⃣  First, try fixing permissions (fastest):"
echo "   ./fix_display_permissions.sh"
echo "   Then test: python3 main.py"

echo -e "\n2️⃣  If that doesn't work, try KMS driver:"
echo "   ./fix_display_kms.sh"
echo "   sudo reboot"
echo "   Then test: python3 main.py"

echo -e "\n3️⃣  If KMS has issues, try legacy mode:"
echo "   ./fix_display_legacy.sh"
echo "   sudo reboot"
echo "   Then test: python3 main.py"

echo -e "\n4️⃣  Test display with specific driver:"
echo "   SDL_VIDEODRIVER=fbdev python3 main.py"

echo -e "\n5️⃣  Emergency fallback (always works):"
echo "   sudo python3 main.py"

echo -e "\n✅ Display diagnostic complete!"
