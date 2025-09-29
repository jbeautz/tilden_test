#!/bin/bash
# Debug and fix getty autologin service

echo "🔍 Getty Autologin Debug and Fix"
echo "================================"

# Check current getty service status
echo "📊 Current getty@tty1 service status:"
sudo systemctl status getty@tty1.service --no-pager

echo ""
echo "📋 Checking autologin configuration:"
if [ -f /etc/systemd/system/getty@tty1.service.d/autologin.conf ]; then
    echo "Autologin override file exists:"
    cat /etc/systemd/system/getty@tty1.service.d/autologin.conf
else
    echo "❌ No autologin override file found"
fi

echo ""
echo "🔧 Creating correct autologin configuration..."

# Stop the service
sudo systemctl stop getty@tty1.service

# Create the override directory
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d/

# Create proper autologin configuration
sudo tee /etc/systemd/system/getty@tty1.service.d/override.conf > /dev/null << 'EOF'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin maggi --noclear %I $TERM
EOF

# Alternative method - modify the main service temporarily
echo ""
echo "🔧 Alternative: Direct service modification..."

# Create a complete service override
sudo tee /etc/systemd/system/getty@tty1.service << 'EOF'
[Unit]
Description=Getty on %i
Documentation=man:agetty(8) man:systemd-getty-generator(8)
Documentation=http://0pointer.de/blog/projects/serial-console.html
After=systemd-user-sessions.service plymouth-quit-wait.service getty-pre.target
After=rc-local.service

# On systems without virtual consoles, don't start any getty. Note
# that serial gettys are covered by serial-getty@.service, not this
# unit.
ConditionPathExists=/dev/tty0

[Service]
# the VT is cleared by TTYVTDisallocate
# The '-o' option value tells agetty to replace 'login' arguments with an
# option to preserve environment (-p), followed by '--' for safety, and then
# the entered username.
ExecStart=-/sbin/agetty --autologin maggi --noclear %I $TERM
Type=idle
Restart=always
RestartSec=0
UtmpIdentifier=%I
TTYPath=/dev/%i
TTYReset=yes
TTYVHangup=yes
TTYVTDisallocate=yes
KillMode=process
IgnoreSIGPIPE=no
SendSIGHUP=yes

[Install]
WantedBy=getty.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable getty@tty1.service
sudo systemctl start getty@tty1.service

echo ""
echo "✅ Getty autologin reconfigured"
echo ""
echo "📊 New service status:"
sudo systemctl status getty@tty1.service --no-pager

echo ""
echo "🔄 You can either:"
echo "1. Wait 30 seconds and check if autologin happens"
echo "2. Reboot now: sudo reboot"
echo ""
echo "Expected result: Direct login as 'maggi' without password prompt"
