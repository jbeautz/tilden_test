#!/bin/bash
# Script to compare manual vs systemd environment

echo "=========================================="
echo "MANUAL RUN (user environment)"
echo "=========================================="
cd ~/tilden_test/rake_test
source myproject-venv/bin/activate
python3 diagnose_environment.py > /tmp/diag_manual.txt 2>&1

echo ""
echo "Manual diagnostic saved to: /tmp/diag_manual.txt"
echo ""
echo "Now install temporary diagnostic service to run at boot..."
echo ""

# Create temporary diagnostic service
sudo tee /etc/systemd/system/rake-diagnostic.service > /dev/null <<'EOF'
[Unit]
Description=Diagnostic - Check Environment at Boot
After=multi-user.target

[Service]
Type=oneshot
User=maggi
Group=maggi
WorkingDirectory=/home/maggi/tilden_test/rake_test
Environment=HOME=/home/maggi
Environment=SDL_VIDEODRIVER=kmsdrm
Environment=SDL_FBDEV=/dev/fb0
Environment=SDL_NOMOUSE=1

ExecStartPre=/bin/sleep 15
ExecStart=/home/maggi/tilden_test/rake_test/myproject-venv/bin/python3 /home/maggi/tilden_test/rake_test/diagnose_environment.py

StandardOutput=file:/tmp/diag_systemd.txt
StandardError=file:/tmp/diag_systemd.txt

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable rake-diagnostic.service

echo "✓ Diagnostic service installed"
echo ""
echo "REBOOT YOUR PI NOW"
echo ""
echo "After reboot, run:"
echo "  diff /tmp/diag_manual.txt /tmp/diag_systemd.txt"
echo ""
echo "This will show the EXACT differences between manual and systemd startup"
echo ""
echo "To disable diagnostic service after:"
echo "  sudo systemctl disable rake-diagnostic.service"
