#!/bin/bash
# Complete Pi Display Auto-Start Setup Script
# This script configures the Pi to automatically start the GUI on boot

echo "🚀 Setting up Pi for GUI auto-start..."
echo "=================================================="

# 1. Ensure display is configured for GUI
echo "📺 Configuring display settings..."

# Add GPU memory split for proper graphics support
if ! grep -q "gpu_mem=128" /boot/config.txt; then
    echo "gpu_mem=128" | sudo tee -a /boot/config.txt
    echo "✅ Added GPU memory allocation"
fi

# Enable DRM/KMS for modern display support
if ! grep -q "dtoverlay=vc4-kms-v3d" /boot/config.txt; then
    echo "dtoverlay=vc4-kms-v3d" | sudo tee -a /boot/config.txt
    echo "✅ Enabled KMS display support"
fi

# 2. Fix auto-login (if not already working)
echo "🔓 Ensuring auto-login is configured..."

# Check if our custom autologin service exists and is enabled
if [ ! -f "/etc/systemd/system/autologin@.service" ]; then
    echo "Creating custom autologin service..."
    sudo tee /etc/systemd/system/autologin@.service > /dev/null << 'EOF'
[Unit]
Description=Auto Login Getty on %i
Wants=systemd-user-sessions.service
After=systemd-user-sessions.service
After=getty-pre.target
Before=getty.target
IgnoreOnIsolate=yes

[Service]
ExecStart=-/sbin/agetty --autologin maggi --noclear %i $TERM
Type=idle
Restart=always
RestartSec=0
UtmpIdentifier=%i
TTYPath=/dev/%i
TTYReset=yes
KillMode=process
IgnoreSIGPIPE=no
SendSIGHUP=yes

[Install]
WantedBy=getty.target
EOF
fi

# Enable the autologin service
sudo systemctl enable autologin@tty1.service
sudo systemctl disable getty@tty1.service

echo "✅ Auto-login configured"

# 3. Update the GUI service to run properly
echo "🎮 Configuring GUI service..."

sudo tee /etc/systemd/system/rake-sensor.service > /dev/null << 'EOF'
[Unit]
Description=Environmental Sensor GUI
After=graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
User=maggi
Group=maggi
WorkingDirectory=/home/maggi/tilden_test/rake_test
Environment=HOME=/home/maggi
Environment=XDG_RUNTIME_DIR=/run/user/1000
Environment=SDL_VIDEODRIVER=kmsdrm
Environment=SDL_NOMOUSE=1
ExecStartPre=/bin/sleep 10
ExecStart=/home/maggi/tilden_test/rake_test/myproject-venv/bin/python /home/maggi/tilden_test/rake_test/main.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF

# Enable the service
sudo systemctl daemon-reload
sudo systemctl enable rake-sensor.service

echo "✅ GUI service configured"

# 4. Create a startup script that runs after login
echo "📝 Creating startup script..."

# Create a .profile entry to start the GUI after login
if ! grep -q "cd ~/tilden_test/rake_test" /home/maggi/.profile; then
    cat >> /home/maggi/.profile << 'EOF'

# Auto-start environmental sensor GUI
if [ -z "$SSH_CLIENT" ] && [ -z "$SSH_TTY" ] && [ "$(tty)" = "/dev/tty1" ]; then
    cd ~/tilden_test/rake_test
    source myproject-venv/bin/activate
    python main.py
fi
EOF
    echo "✅ Added GUI auto-start to .profile"
fi

# 5. Ensure permissions are correct
echo "🔧 Setting permissions..."
sudo chown -R maggi:maggi /home/maggi/tilden_test/rake_test
sudo chmod +x /home/maggi/tilden_test/rake_test/*.py

echo ""
echo "=================================================="
echo "🎉 Setup complete! Configuration summary:"
echo "   ✅ GPU memory allocated (128MB)"
echo "   ✅ KMS display support enabled"
echo "   ✅ Auto-login configured for user 'maggi'"
echo "   ✅ GUI service configured"
echo "   ✅ Startup script added to .profile"
echo ""
echo "⚠️  REBOOT REQUIRED for all changes to take effect"
echo ""
echo "After reboot:"
echo "   - Pi should auto-login as 'maggi'"
echo "   - GUI should start automatically on the display"
echo "   - If GUI doesn't start, check: journalctl -u rake-sensor.service"
echo ""
echo "To reboot now: sudo reboot"
echo "=================================================="
