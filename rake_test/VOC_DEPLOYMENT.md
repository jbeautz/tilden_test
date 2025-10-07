# Deployment Instructions - VOC Sensor Fix

## Quick Summary

**Problem**: Gas/VOC column in logs was empty, no air quality display  
**Solution**: Updated sensor.py and display_forest_rings.py to properly read and show VOC data  
**Result**: 4 tree rings now show: Temperature, Humidity, Pressure, and Air Quality (VOC)

## Deploy to Raspberry Pi

### Option 1: Copy Files from Mac (Easiest)

```bash
# From your Mac, copy the updated files to the Pi:
scp ~/tilden_test/rake_test/sensor.py maggi@maggi.local:~/tilden_test/rake_test/
scp ~/tilden_test/rake_test/display_forest_rings.py maggi@maggi.local:~/tilden_test/rake_test/
scp ~/tilden_test/rake_test/apply_voc_fix.sh maggi@maggi.local:~/tilden_test/rake_test/

# Then SSH to the Pi and run:
ssh maggi@maggi.local
cd ~/tilden_test/rake_test
chmod +x apply_voc_fix.sh
./apply_voc_fix.sh
```

### Option 2: Manual Steps on Pi

```bash
# SSH to the Pi
ssh maggi@maggi.local

# Copy the updated files (you'll need to transfer them first)
cd ~/tilden_test/rake_test

# Stop the service
sudo systemctl stop rake-sensor.service

# Restart the service with new code
sudo systemctl start rake-sensor.service

# Watch the logs
sudo journalctl -u rake-sensor.service -f
```

## What to Expect

### 1. During First 5-10 Minutes (Warm-up):
```
Gas sensor: 45230 Ω (warming up, not stable yet)
Gas sensor: 48120 Ω (warming up, not stable yet)
...
```

### 2. After Stabilization:
- No more "warming up" messages
- Steady gas resistance readings (typically 50-150 kΩ)
- Log file will have values in the `gas` column

### 3. Display Changes:
- **Before**: 3 tree rings in a row
- **After**: 4 tree rings in 2x2 grid
  ```
  [Temperature]  [Humidity]
  [Pressure]     [Air Quality]
  ```

## Verify It's Working

### Check the logs:
```bash
# View recent log entries
tail -20 ~/tilden_test/rake_test/rake_log_$(date +%Y%m%d)_*.csv

# Should see gas column filled (5th column):
# timestamp,temperature,humidity,pressure,gas,latitude,longitude,altitude
# 2025-10-07...,22.5,48.2,1013.4,52340.5,,,
```

### Test the sensor:
- **Breathe near it** → Gas resistance drops (20-40 kΩ)
- **Hand sanitizer** → Gas resistance drops significantly (< 20 kΩ)
- **Clean air** → Gas resistance increases (50-150+ kΩ)

## Files Changed

- ✅ `sensor.py` - Always returns gas_resistance (even during warm-up)
- ✅ `display_forest_rings.py` - Added 4th tree ring for Air Quality
- ✅ `apply_voc_fix.sh` - Deployment script
- ✅ `VOC_SENSOR_FIX.md` - Complete technical documentation

## Troubleshooting

### If gas column is still empty:
1. Check if BME680 library is installed in venv:
   ```bash
   source ~/tilden_test/rake_test/myproject-venv/bin/activate
   pip list | grep bme680
   ```

2. Check service is using the venv:
   ```bash
   sudo journalctl -u rake-sensor.service | grep "BME680"
   ```

### If display doesn't show 4 rings:
- Make sure display_forest_rings.py was updated
- Check for errors in journal: `sudo journalctl -u rake-sensor.service -p err`

## Understanding Gas Readings

**Gas Resistance (Ohms/kΩ):**
- Higher = Better air quality (fewer VOCs)
- Lower = Worse air quality (more VOCs)

**Typical Indoor Values:**
- 100-200 kΩ: Excellent air quality
- 50-100 kΩ: Good (normal indoor)
- 20-50 kΩ: Moderate (cooking, cleaning products)
- < 20 kΩ: Poor (strong chemical smells, alcohol)

The BME680 measures **volatile organic compounds** (VOCs) from:
- Human breath
- Cleaning products
- Cooking
- Perfumes/aerosols
- Paint/solvents
- General indoor air quality

---

**All done!** Deploy the changes and watch your air quality data start flowing! 🌲
