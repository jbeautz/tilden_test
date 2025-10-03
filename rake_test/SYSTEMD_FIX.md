# Fixing the Systemd Service

## Problem
The service was configured with `Restart=always` which caused it to restart every time it exited or crashed, creating multiple log files.

## Solution

### 1. Copy the fixed service file:
```bash
cd ~/tilden_test/rake_test
sudo cp rake-sensor-fixed.service /etc/systemd/system/rake-sensor.service
```

### 2. Reload systemd and restart the service:
```bash
sudo systemctl daemon-reload
sudo systemctl restart rake-sensor.service
```

### 3. Check the service status:
```bash
sudo systemctl status rake-sensor.service
```

### 4. View logs to see what's happening:
```bash
sudo journalctl -u rake-sensor.service -f
```

## What Changed

- **Restart policy**: Changed from `Restart=always` to `Restart=on-failure`
  - Now only restarts if the script crashes, not on clean exit
  
- **Start limit**: Added `StartLimitBurst=3` and `StartLimitIntervalSec=300`
  - If it fails 3 times in 5 minutes, systemd will stop trying
  
- **Longer wait**: Changed `ExecStartPre` from 10 to 15 seconds
  - Gives the system more time to fully boot
  
- **Uses start script**: Changed to use `start_forest_rings.sh` instead of calling Python directly
  - This ensures SDL environment variables are set correctly
  
- **SDL driver**: Changed to `dummy` driver (what actually works)
  - Your display works with the dummy driver + framebuffer

## Debugging

If the service still has issues, check the logs:
```bash
# View full log
sudo journalctl -u rake-sensor.service --no-pager

# View just errors
sudo journalctl -u rake-sensor.service -p err --no-pager

# Follow live log
sudo journalctl -u rake-sensor.service -f
```

## If You Need to Disable Auto-Start

```bash
sudo systemctl disable rake-sensor.service
sudo systemctl stop rake-sensor.service
```

Then you can run manually with:
```bash
cd ~/tilden_test/rake_test
./start_forest_rings.sh
```
