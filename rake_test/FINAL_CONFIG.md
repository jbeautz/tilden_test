# Soil Monitor - Final Configuration Guide

## 🎉 System Status: WORKING!

The system now boots automatically, creates ONE log file, and logs continuously at 1 Hz.

## What Was Fixed

### Root Cause
Two systemd services were running simultaneously:
- **User-level service** (`~/.config/systemd/user/rake-sensor.service`)
  - Not using virtual environment
  - Missing BME680 library (pyserial)
  - Crashing every 1-2 seconds
  - Creating empty log files on each restart
  
- **System-level service** (`/etc/systemd/system/rake-sensor.service`)
  - Properly configured
  - Running successfully
  - Creating good log files

### Solution
Disabled the user-level service:
```bash
systemctl --user stop rake-sensor.service
systemctl --user disable rake-sensor.service
```

## Current Configuration

### Service File: `/etc/systemd/system/rake-sensor.service`
```ini
[Unit]
Description=Soil Monitor - Continuous Environmental Sensor Logger
After=multi-user.target
Wants=multi-user.target

[Service]
Type=simple
User=maggi
WorkingDirectory=/home/maggi/tilden_test/rake_test
ExecStart=/home/maggi/tilden_test/rake_test/start_forest_rings.sh
Restart=on-failure
RestartSec=10
StartLimitBurst=3
StartLimitIntervalSec=300
```

### Start Script: `start_forest_rings.sh`
- Waits for graphics subsystem (`/dev/fb0`, `/dev/dri/card0`)
- Sets SDL environment variables
- Activates virtual environment (for BME680 library)
- Runs `main.py`

### Main Script: `main.py`
- Continuous logging mode (no start/stop button)
- Reads sensors at 1 Hz
- Updates display at 10 Hz
- Ignores pygame QUIT events
- Exits with code 1 on fatal errors (triggers systemd restart)

## Optional Improvements

### 1. Clean Up Old Log Files

Run this script to remove empty/failed log files:
```bash
cd ~/tilden_test/rake_test
./cleanup_old_logs.sh
```

This removes files smaller than 10KB (empty or partial files from failed starts).

### 2. Fix BME680 Sensor Reading

If you see "BME680 library not available" in the logs, apply the fix:
```bash
cd ~/tilden_test/rake_test
./apply_fixes.sh
```

This updates the service to use the virtual environment where BME680 library is installed.

## Monitoring

### Check Service Status
```bash
sudo systemctl status rake-sensor.service
```

### View Live Logs
```bash
sudo journalctl -u rake-sensor.service -f
```

### Check Log Files
```bash
# List recent log files
ls -lht ~/tilden_test/rake_test/rake_log_*.csv | head -5

# View current log file
tail -f ~/tilden_test/rake_test/rake_log_$(date +%Y%m%d)_*.csv
```

### Verify Single Log File Creation
After reboot, only ONE new log file should be created:
```bash
ls -lt ~/tilden_test/rake_test/rake_log_*.csv | head -3
```

## Troubleshooting

### Multiple Log Files Still Being Created
Check for other auto-start mechanisms:
```bash
# Check user-level services
systemctl --user list-units --type=service | grep rake

# Check cron jobs
crontab -l

# Check rc.local
cat /etc/rc.local

# Check .bashrc auto-start
grep -i rake ~/.bashrc
```

### Service Not Starting at Boot
```bash
# Re-enable the service
sudo systemctl enable rake-sensor.service

# Check if it's in the right target
sudo systemctl list-dependencies multi-user.target | grep rake
```

### Display Not Showing Graphics
Check the SDL driver and device access:
```bash
# Check framebuffer
ls -l /dev/fb0

# Check DRM device
ls -l /dev/dri/card0

# View display initialization in logs
sudo journalctl -u rake-sensor.service | grep -i "display\|sdl\|video"
```

### Sensor Reading Errors
```bash
# Check I2C bus for BME680
i2cdetect -y 1

# Check serial port for GPS
ls -l /dev/serial0 /dev/ttyS0

# Verify virtual environment has libraries
source ~/tilden_test/rake_test/myproject-venv/bin/activate
pip list | grep -E "bme680|serial|pygame"
```

## Service Commands

```bash
# Stop the service
sudo systemctl stop rake-sensor.service

# Start the service
sudo systemctl start rake-sensor.service

# Restart the service
sudo systemctl restart rake-sensor.service

# Disable auto-start
sudo systemctl disable rake-sensor.service

# Enable auto-start
sudo systemctl enable rake-sensor.service

# View service configuration
sudo systemctl cat rake-sensor.service

# Reload after editing service file
sudo systemctl daemon-reload
```

## Manual Testing

To test without systemd:
```bash
cd ~/tilden_test/rake_test
./start_forest_rings.sh
```

To test with specific Python version:
```bash
cd ~/tilden_test/rake_test
source myproject-venv/bin/activate
python main.py
```

## File Locations

- **Service file**: `/etc/systemd/system/rake-sensor.service`
- **Start script**: `~/tilden_test/rake_test/start_forest_rings.sh`
- **Main script**: `~/tilden_test/rake_test/main.py`
- **Log files**: `~/tilden_test/rake_test/rake_log_*.csv`
- **Virtual env**: `~/tilden_test/rake_test/myproject-venv/`

## Success Indicators

✅ Service shows "active (running)" for extended periods  
✅ Only ONE log file created per boot  
✅ Log file size grows continuously (~1KB per minute)  
✅ Display shows tree rings graphics (not terminal text)  
✅ Temperature, humidity, pressure readings in logs  
✅ No "Start request repeated too quickly" errors  
✅ No "module 'serial' has no attribute 'Serial'" errors  

## Next Steps

1. Run `./apply_fixes.sh` to clean up logs and enable BME680 sensor
2. Verify the display shows graphics (tree rings visualization)
3. Let it run for a few hours to verify stability
4. Once stable, the system is ready for field deployment! 🌲
