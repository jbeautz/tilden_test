#!/bin/bash
# Final autologin fix - force it to work

echo "🔧 Final Getty Autologin Fix"
echo "============================"

# Stop getty service completely
sudo systemctl stop getty@tty1.service
sudo systemctl disable getty@tty1.service

# Remove any existing overrides that aren't working
sudo rm -rf /etc/systemd/system/getty@tty1.service.d/
sudo rm -f /etc/systemd/system/getty@tty1.service

# Create a custom autologin service
sudo tee /etc/systemd/system/autologin@.service > /dev/null << 'EOF'
[Unit]
Description=Autologin getty on %i
Documentation=man:agetty(8)
After=systemd-user-sessions.service plymouth-quit-wait.service
Before=getty@%i.service
Conflicts=getty@%i.service
ConditionPathExists=/dev/%i

[Service]
Environment=TERM=linux
ExecStart=-/sbin/agetty --autologin maggi --noclear %I linux
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

# Enable and start the custom autologin service
sudo systemctl daemon-reload
sudo systemctl enable autologin@tty1.service
sudo systemctl start autologin@tty1.service

echo ""
echo "📊 New autologin service status:"
sudo systemctl status autologin@tty1.service --no-pager

echo ""
echo "🔍 Process check:"
ps aux | grep -E "(getty|autologin)" | grep -v grep

echo ""
echo "✅ Custom autologin service created and started"
echo "🔄 Test by switching to tty1: sudo chvt 1"
echo "   (Or reboot to test full boot sequence)"

# Also ensure the target is set correctly
sudo systemctl set-default multi-user.target

echo ""
echo "System will now boot to console with automatic login as 'maggi'"
