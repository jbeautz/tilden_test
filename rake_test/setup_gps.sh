#!/bin/bash
# GPS Setup Script for GY-GPS6MV2 at 9600 baud
# Configures Raspberry Pi UART for GPS communication

echo "🛰️  Setting up GPS sensor (9600 baud)..."
echo "=================================================="

# 1. Configure UART in boot config
echo "📡 Configuring UART in boot config..."

# Add UART enable if not present
if ! grep -q "enable_uart=1" /boot/config.txt; then
    echo "enable_uart=1" | sudo tee -a /boot/config.txt
    echo "✅ Added enable_uart=1 to boot config"
else
    echo "✅ UART already enabled in boot config"
fi

# Add UART0 parameter if not present  
if ! grep -q "dtparam=uart0=on" /boot/config.txt; then
    echo "dtparam=uart0=on" | sudo tee -a /boot/config.txt
    echo "✅ Added dtparam=uart0=on to boot config"
else
    echo "✅ UART0 already enabled in boot config"
fi

# 2. Disable serial console (if enabled)
echo "🔧 Checking serial console configuration..."

# Check if serial console is in cmdline.txt
if grep -q "console=serial0" /boot/cmdline.txt; then
    echo "⚠️  Serial console found in cmdline.txt - removing..."
    sudo sed -i 's/console=serial0,[0-9]\+ //g' /boot/cmdline.txt
    sudo sed -i 's/console=ttyAMA0,[0-9]\+ //g' /boot/cmdline.txt
    echo "✅ Serial console removed from kernel command line"
else
    echo "✅ Serial console not interfering with GPS"
fi

# 3. Add user to dialout group
echo "👤 Configuring user permissions..."

if groups $USER | grep -q dialout; then
    echo "✅ User $USER already in dialout group"
else
    sudo usermod -a -G dialout $USER
    echo "✅ Added user $USER to dialout group"
    echo "⚠️  You need to logout and login again for group changes to take effect"
fi

# 4. Install required Python packages
echo "📦 Installing required Python packages..."

# Check if in virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Using virtual environment: $VIRTUAL_ENV"
    pip install pyserial pynmea2
else
    echo "Installing system-wide packages"
    pip3 install pyserial pynmea2
fi

echo "✅ Python packages installed"

# 5. Test serial port access
echo "🔍 Testing serial port access..."

if [ -e "/dev/serial0" ]; then
    echo "✅ /dev/serial0 exists"
    ls -la /dev/serial0
else
    echo "❌ /dev/serial0 not found - UART may not be properly enabled"
fi

# 6. Create a quick test script
echo "📝 Creating GPS test command..."

cat > gps_quick_test.sh << 'EOF'
#!/bin/bash
echo "🛰️  Quick GPS Test - Press Ctrl+C to stop"
echo "Listening for NMEA data on /dev/serial0 at 9600 baud..."
echo "You should see lines starting with \$GP..."
echo "=================================================="
timeout 10s cat /dev/serial0 2>/dev/null || echo "No data received - check connections and configuration"
EOF

chmod +x gps_quick_test.sh
echo "✅ Created gps_quick_test.sh for manual testing"

echo ""
echo "=================================================="
echo "🎉 GPS setup complete! Configuration summary:"
echo "   ✅ UART enabled in boot config"
echo "   ✅ Serial console disabled"
echo "   ✅ User added to dialout group"
echo "   ✅ Python packages installed (pyserial, pynmea2)"
echo "   ✅ Test script created"
echo ""
echo "🔌 Hardware Connections Required:"
echo "   GPS VCC → Pi 3.3V (Pin 1) or 5V (Pin 2)"
echo "   GPS GND → Pi GND (Pin 6)"
echo "   GPS TXD → Pi GPIO 15 (Pin 10)"
echo "   GPS RXD → Pi GPIO 14 (Pin 8)"
echo ""
echo "🧪 Testing Options:"
echo "   1. Quick test: ./gps_quick_test.sh"
echo "   2. Full diagnostic: python diagnose_gps.py"
echo "   3. Manual check: sudo cat /dev/serial0"
echo ""
echo "⚠️  REBOOT REQUIRED for UART changes to take effect"
echo "   After reboot, test GPS with: python diagnose_gps.py"
echo ""
echo "To reboot now: sudo reboot"
echo "=================================================="
