#!/bin/bash
# Quick fix to enable auto-login on Raspberry Pi
# This eliminates the login prompt on boot

echo "🔐 Enabling auto-login for user 'maggi'..."

# Method 1: Using raspi-config (cleanest)
echo "Using raspi-config to enable auto-login to desktop..."
sudo raspi-config nonint do_boot_behaviour B4

# Method 2: Manual systemd override (backup method)
echo "Creating systemd auto-login override..."
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d/
sudo tee /etc/systemd/system/getty@tty1.service.d/autologin.conf > /dev/null << EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin maggi --noclear %I \$TERM
EOF

# Reload systemd
sudo systemctl daemon-reload

echo ""
echo "✅ Auto-login configured for user 'maggi'"
echo "🔄 Reboot required for changes to take effect:"
echo "   sudo reboot"
echo ""
echo "After reboot:"
echo "  - No login prompt should appear"
echo "  - Desktop should load automatically"
echo "  - GUI service should start automatically"
