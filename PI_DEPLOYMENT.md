# Pi Deployment Instructions

## Deploy Forest Rings GUI to Raspberry Pi

### 1. Pull Latest Changes on Pi
```bash
cd ~/tilden_test
git stash  # Save any local changes
git pull origin main
```

### 2. Test Touch Input First
```bash
cd ~/tilden_test/rake_test
python3 test_pi_touch.py
```
**Expected**: Touch the screen and verify touch events are detected.

### 3. Run Forest Rings GUI
```bash
cd ~/tilden_test/rake_test
python3 main.py
```

### 4. Test Features
- **Tree Rings**: Should appear immediately with initial data
- **Touch Button**: Touch the START/PAUSE button to toggle recording
- **SPACE Key**: Press SPACE bar (if keyboard connected) to toggle
- **Data Logging**: Check CSV files are created and populated when recording

### 5. Troubleshooting Touch Issues

If touch doesn't work, try these solutions:

#### Option A: Enable Touch in Boot Config
```bash
sudo nano /boot/config.txt
```
Add/uncomment:
```
dtoverlay=vc4-kms-v3d
dtoverlay=rpi-ft5406  # For official 7" display
# OR
dtoverlay=rpi-display  # For other displays
```

#### Option B: Install Touch Drivers
```bash
sudo apt update
sudo apt install xserver-xorg-input-evdev
```

#### Option C: Check Touch Device
```bash
ls /dev/input/
cat /proc/bus/input/devices | grep -A 5 -B 5 Touch
```

#### Option D: Manual Touch Calibration
```bash
sudo apt install xinput-calibrator
xinput_calibrator
```

### 6. Expected Behavior

**✅ Working System:**
- Display shows Forest Rings GUI immediately
- Tree rings visible from startup (3 rings for temp/humidity/pressure)
- Status shows "PAUSED" initially
- Touch START button → Status changes to "GROWING" 
- CSV logging starts when recording enabled
- Touch PAUSE button → Status changes to "PAUSED"
- CSV logging stops

**❌ Touch Issues:**
- Can see GUI but touch doesn't respond
- No debug output for touch events
- Button doesn't toggle recording state

### 7. Debug Mode

For troubleshooting, the GUI includes debug output:
- Mouse/touch events print to terminal
- Recording state changes print confirmation
- Check terminal for "DEBUG: Mouse clicked at..." messages
