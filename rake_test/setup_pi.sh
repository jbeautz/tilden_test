#!/bin/bash
# Setup script for Raspberry Pi environmental monitoring with GUI
# Run this script on the Pi to configure all required settings

set -e

echo "🔧 Setting up Raspberry Pi for Environmental Monitoring..."

# Enable I2C and Serial interfaces
echo "📡 Enabling I2C and Serial interfaces..."
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_serial 0

# Disable serial console to free up /dev/serial0 for GPS
echo "🗣️ Disabling serial console for GPS use..."
sudo raspi-config nonint do_serial_hw 0
sudo raspi-config nonint do_serial_cons 1

# Update system packages
echo "📦 Updating system packages..."
sudo apt update
sudo apt install -y python3-pip python3-venv i2c-tools git

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
cd ~/tilden_test/rake_test
python3 -m venv .venv
source .venv/bin/activate

# Install Python packages
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Set up systemd service
echo "⚙️ Setting up systemd service..."
sudo cp rake-sensor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rake-sensor.service

# Update service to use virtual environment and correct user
echo "🔧 Configuring service to use virtual environment..."
sudo sed -i 's|^ExecStart=/usr/bin/python3.*|ExecStart=/home/maggi/tilden_test/rake_test/.venv/bin/python /home/maggi/tilden_test/rake_test/main.py|' /etc/systemd/system/rake-sensor.service
sudo sed -i 's|^# ExecStart=/home/pi/tilden_test/rake_test/.venv/bin/python.*|ExecStart=/home/maggi/tilden_test/rake_test/.venv/bin/python /home/maggi/tilden_test/rake_test/main.py|' /etc/systemd/system/rake-sensor.service
sudo sed -i 's|User=pi|User=maggi|' /etc/systemd/system/rake-sensor.service
sudo sed -i 's|Group=pi|Group=maggi|' /etc/systemd/system/rake-sensor.service
sudo sed -i 's|WorkingDirectory=/home/pi/tilden_test/rake_test|WorkingDirectory=/home/maggi/tilden_test/rake_test|' /etc/systemd/system/rake-sensor.service
sudo systemctl daemon-reload

# Enable auto-login to desktop (no login prompt)
echo "🔐 Enabling auto-login to desktop..."
sudo raspi-config nonint do_boot_behaviour B4

# Add user to required groups
echo "👥 Adding user to I2C and GPIO groups..."
sudo usermod -a -G i2c,spi,gpio maggi
sudo usermod -a -G dialout maggi

# Check hardware setup
echo "🔍 Checking hardware setup..."
echo "I2C Status:"
sudo i2cdetect -y 1

echo "Serial devices:"
ls -la /dev/serial* /dev/ttyS* /dev/ttyAMA* 2>/dev/null || echo "No serial devices found"

echo ""
echo "✅ Setup complete! Please reboot your Pi:"
echo "   sudo reboot"
echo ""
echo "After reboot, the GUI will auto-start. You can also:"
echo "   Check service: sudo systemctl status rake-sensor"
echo "   View logs: sudo journalctl -u rake-sensor -f"
echo "   Test manually: source .venv/bin/activate && python main.py"
echo ""
echo "🔌 Hardware connections needed:"
echo "   BME680: VCC→3.3V, GND→GND, SDA→GPIO2, SCL→GPIO3"
echo "   GPS: VCC→3.3V, GND→GND, TX→GPIO15 (UART RX)"
echo "   Display: Connected via DSI connector"
