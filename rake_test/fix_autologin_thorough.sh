#!/bin/bash
# Thorough auto-login diagnostic and fix

echo "🔍 Auto-login Diagnostic and Fix"
echo "================================="

# Check current boot behavior
echo "📋 Current boot configuration:"
echo "Boot CLI setting: $(sudo raspi-config nonint get_boot_cli)"
echo "Boot autologin setting: $(sudo raspi-config nonint get_autologin)"

# Check what's preventing auto-login
echo ""
echo "🔧 Checking potential blockers:"

# Check if console autologin is properly configured
echo "Getty service configuration:"
if [ -f /etc/systemd/system/getty@tty1.service.d/autologin.conf ]; then
    echo "✅ Getty autologin override exists"
    cat /etc/systemd/system/getty@tty1.service.d/autologin.conf
else
    echo "❌ No getty autologin override found"
fi

# Check systemd default target
echo ""
echo "Systemd default target:"
systemctl get-default

# Check if display manager is interfering
echo ""
echo "Display manager status:"
if systemctl is-enabled lightdm >/dev/null 2>&1; then
    echo "LightDM is enabled"
    if [ -f /etc/lightdm/lightdm.conf ]; then
        echo "LightDM autologin config:"
        grep -E "autologin" /etc/lightdm/lightdm.conf || echo "No autologin settings found"
    fi
elif systemctl is-enabled gdm3 >/dev/null 2>&1; then
    echo "GDM3 is enabled"
else
    echo "No display manager found"
fi

echo ""
echo "🛠️ Applying comprehensive fix..."

# Force console boot with autologin (B2)
echo "Setting to console with autologin..."
sudo raspi-config nonint do_boot_behaviour B2

# Create/update getty override
echo "Creating getty autologin override..."
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d/
sudo tee /etc/systemd/system/getty@tty1.service.d/autologin.conf > /dev/null << 'EOF'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin maggi --noclear %I $TERM
Type=idle
EOF

# Disable any conflicting services
echo "Disabling potential conflicts..."
sudo systemctl disable serial-getty@ttyS0.service 2>/dev/null || true

# Reload systemd
sudo systemctl daemon-reload

# Enable and start getty service
sudo systemctl enable getty@tty1.service

echo ""
echo "✅ Auto-login configuration complete"
echo ""
echo "Verification:"
echo "Boot CLI: $(sudo raspi-config nonint get_boot_cli)"
echo "Boot autologin: $(sudo raspi-config nonint get_autologin)"
echo ""
echo "🔄 REBOOT NOW with: sudo reboot"
echo ""
echo "After reboot, you should see:"
echo "1. No login prompt"
echo "2. Automatic login as 'maggi'"
echo "3. Command prompt ready"
echo "4. GUI service should auto-start"
