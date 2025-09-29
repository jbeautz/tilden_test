#!/bin/bash
# Quick fix to re-enable auto-login

echo "🔐 Re-enabling auto-login..."

# Method 1: Use raspi-config to enable desktop auto-login
echo "Setting boot to desktop with auto-login..."
sudo raspi-config nonint do_boot_behaviour B4

# Method 2: Direct systemd override (backup method)
echo "Creating systemd auto-login override..."
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d/
sudo tee /etc/systemd/system/getty@tty1.service.d/autologin.conf > /dev/null << EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin maggi --noclear %I \$TERM
EOF

# Reload systemd
sudo systemctl daemon-reload

# Also ensure lightdm auto-login (if using desktop)
if [ -f /etc/lightdm/lightdm.conf ]; then
    echo "Configuring lightdm auto-login..."
    sudo sed -i 's/#autologin-user=/autologin-user=maggi/' /etc/lightdm/lightdm.conf
    sudo sed -i 's/#autologin-user-timeout=0/autologin-user-timeout=0/' /etc/lightdm/lightdm.conf
fi

echo ""
echo "✅ Auto-login re-enabled for user 'maggi'"
echo "🔄 Changes will take effect after reboot"
echo ""
echo "Current boot behavior:"
sudo raspi-config nonint get_boot_cli
