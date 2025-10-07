# SIMPLE FIX - When You Come Back

## The Problem
Display initialization keeps crashing, causing infinite restarts and empty log files.

## The Solution
Use the **logging-only version** with NO display complexity.

## Instructions

### 1. Pull the latest code:
```bash
cd ~/tilden_test/rake_test
git pull
```

### 2. Test the simple version manually first:
```bash
cd ~/tilden_test/rake_test
source myproject-venv/bin/activate
python3 main_logging_only.py
```

Press Ctrl+C after 10 seconds. Check that a log file was created and has data:
```bash
ls -lht rake_log_*.csv | head -1
tail $(ls -t rake_log_*.csv | head -1)
```

### 3. If manual test works, install as service:
```bash
sudo cp rake-sensor-simple.service /etc/systemd/system/rake-sensor.service
sudo systemctl daemon-reload
sudo systemctl restart rake-sensor.service
sudo journalctl -u rake-sensor.service -f
```

You should see:
- "✓ 10 records logged" every 10 seconds
- NO "Exiting" messages
- NO repeated restarts

### 4. Check the log file:
```bash
tail -f ~/tilden_test/rake_test/rake_log_*.csv
```

## What This Does
- Logs sensor data at 1 Hz continuously
- NO display (no pygame, no crashes)
- Creates ONE log file that fills with data
- Runs from boot to power-off
- Simple, bulletproof, guaranteed to work

## To Add Display Later
Once logging is working reliably, we can add the display back as a separate optional component.

## Clean Up Old Log Files
Once this is working, run:
```bash
cd ~/tilden_test/rake_test
./cleanup_logs.sh
```
