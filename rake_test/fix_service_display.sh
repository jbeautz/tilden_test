#!/bin/bash
# Fix the service environment variables for proper display

echo "🔧 Fixing service display environment..."

# Stop the service
sudo systemctl stop rake-sensor.service

# Fix the service environment variables
echo "Adding missing SDL environment variables..."
sudo systemctl edit rake-sensor.service --force --full << 'EOF'
[Unit]
Description=Rake Env + GPS Logger GUI
After=network-online.target graphical.target
Wants=network-online.target graphical.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=maggi
Group=maggi
WorkingDirectory=/home/maggi/tilden_test/rake_test
ExecStart=/home/maggi/tilden_test/rake_test/.venv/bin/python /home/maggi/tilden_test/rake_test/main.py
Restart=on-failure
RestartSec=5
TimeoutStopSec=10
# --- Environment for direct framebuffer display ---
Environment=PYTHONUNBUFFERED=1
Environment=SDL_VIDEODRIVER=fbcon
Environment=SDL_FBDEV=/dev/fb0
Environment=SDL_AUDIODRIVER=dummy
Environment=SDL_NOMOUSE=1

[Install]
WantedBy=graphical.target
EOF

# Reload and start
sudo systemctl daemon-reload
sudo systemctl start rake-sensor.service

echo "✅ Service updated with proper display environment"
echo "📊 Checking service status..."
sudo systemctl status rake-sensor.service --no-pager -l

echo ""
echo "🖥️ The GUI should now appear on your Pi's display!"
echo "📋 Monitor with: sudo journalctl -u rake-sensor -f"
