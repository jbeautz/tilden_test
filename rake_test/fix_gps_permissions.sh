#!/bin/bash
# Comprehensive GPS UART permission fix for Raspberry Pi
# This script addresses all common GPS permission issues

echo "🔧 GPS UART Permission Fix"
echo "=" * 60

# Step 1: Check current device state
echo -e "\n📋 Step 1: Checking UART devices..."
ls -l /dev/serial0 /dev/ttyS0 /dev/ttyAMA0 2>/dev/null || echo "Some devices not found"

# Step 2: Check user groups
echo -e "\n👤 Step 2: Checking user groups..."
groups
echo "Current groups: $(groups)"
if ! groups | grep -q dialout; then
    echo "⚠️  Adding user to dialout group..."
    sudo usermod -a -G dialout $USER
    echo "✅ Added to dialout group (reboot required)"
fi
if ! groups | grep -q tty; then
    echo "⚠️  Adding user to tty group..."
    sudo usermod -a -G tty $USER
    echo "✅ Added to tty group (reboot required)"
fi

# Step 3: Remove serial console from cmdline.txt
echo -e "\n🚫 Step 3: Removing serial console from boot..."
if grep -q "console=serial0" /boot/firmware/cmdline.txt 2>/dev/null; then
    echo "Found serial console in cmdline.txt, removing..."
    sudo sed -i 's/ console=serial0,[0-9]*//g; s/ console=ttyAMA0,[0-9]*//g' /boot/firmware/cmdline.txt
    echo "✅ Removed serial console from cmdline.txt"
else
    echo "✅ No serial console in cmdline.txt"
fi

# Step 4: Disable getty services on serial ports
echo -e "\n🔌 Step 4: Disabling getty services on UART..."
sudo systemctl disable --now serial-getty@ttyAMA0.service 2>/dev/null && echo "✅ Disabled ttyAMA0 getty" || echo "ℹ️  ttyAMA0 getty already disabled"
sudo systemctl disable --now serial-getty@serial0.service 2>/dev/null && echo "✅ Disabled serial0 getty" || echo "ℹ️  serial0 getty already disabled"
sudo systemctl disable --now serial-getty@ttyS0.service 2>/dev/null && echo "✅ Disabled ttyS0 getty" || echo "ℹ️  ttyS0 getty already disabled"

# Step 5: Ensure UART is enabled in config.txt
echo -e "\n⚙️  Step 5: Ensuring UART enabled in config..."
if grep -q "^enable_uart=1" /boot/firmware/config.txt; then
    echo "✅ UART already enabled"
else
    echo "enable_uart=1" | sudo tee -a /boot/firmware/config.txt
    echo "✅ Added enable_uart=1 to config.txt"
fi

# Step 6: Create persistent udev rules for GPS
echo -e "\n📝 Step 6: Creating persistent udev rules..."
sudo tee /etc/udev/rules.d/99-gps-uart.rules > /dev/null << 'EOF'
# GPS UART permissions - allow all users to access
SUBSYSTEM=="tty", KERNEL=="ttyS0", MODE="0666", GROUP="dialout", SYMLINK+="gps0"
SUBSYSTEM=="tty", KERNEL=="ttyAMA0", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", KERNEL=="serial0", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", KERNEL=="serial1", MODE="0666", GROUP="dialout"
EOF
echo "✅ Created udev rules"

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
echo "✅ Reloaded udev rules"

# Step 7: Set temporary permissions (until reboot)
echo -e "\n🔓 Step 7: Setting temporary permissions..."
sudo chmod 666 /dev/ttyS0 2>/dev/null && echo "✅ Set ttyS0 permissions" || echo "⚠️  ttyS0 not found"
sudo chmod 666 /dev/serial0 2>/dev/null && echo "✅ Set serial0 permissions" || echo "⚠️  serial0 not found"
sudo chmod 666 /dev/ttyAMA0 2>/dev/null && echo "✅ Set ttyAMA0 permissions" || echo "ℹ️  ttyAMA0 not found"

# Step 8: Set correct group ownership
echo -e "\n👥 Step 8: Setting group ownership..."
sudo chgrp dialout /dev/ttyS0 2>/dev/null && echo "✅ Set ttyS0 group to dialout" || echo "ℹ️  ttyS0 not found"
sudo chgrp dialout /dev/serial0 2>/dev/null && echo "✅ Set serial0 group to dialout" || echo "ℹ️  serial0 not found"

echo -e "\n" "=" * 60
echo "📊 CURRENT STATUS:"
echo "=" * 60
echo -e "\n📁 UART Devices:"
ls -l /dev/serial0 /dev/ttyS0 /dev/ttyAMA0 2>/dev/null || echo "Some devices not found"

echo -e "\n👤 User Groups:"
groups

echo -e "\n⚙️  UART Config:"
grep -E "enable_uart" /boot/firmware/config.txt 2>/dev/null || echo "Config not found"

echo -e "\n📜 Boot Command Line:"
cat /boot/firmware/cmdline.txt 2>/dev/null | grep -o "console=[^ ]*" || echo "No console parameters"

echo -e "\n" "=" * 60
echo "🔄 NEXT STEPS:"
echo "=" * 60
echo "1. REBOOT your Pi: sudo reboot"
echo "2. After reboot, run: cd ~/tilden_test/rake_test && source myproject-venv/bin/activate"
echo "3. Test GPS: python3 -c 'import serial; s=serial.Serial(\"/dev/serial0\",9600,timeout=1); print(\"GPS OK\"); s.close()'"
echo "4. If working, run: python3 main.py"
echo ""
echo "✅ GPS permission fix complete! Reboot required for all changes to take effect."
