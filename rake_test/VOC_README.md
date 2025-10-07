# VOC Sensor Fix - Quick Start

## What Was Fixed
The BME680 gas/VOC sensor was not logging or displaying air quality data. This has been fixed!

## Files Updated
- ✅ **sensor.py** - Now always returns gas resistance values
- ✅ **display_forest_rings.py** - Added 4th tree ring for Air Quality display
- ✅ **apply_voc_fix.sh** - Deployment script
- ✅ **verify_voc.sh** - Verification script

## Deploy to Raspberry Pi

### Step 1: Copy files to Pi
```bash
# From your Mac:
cd ~/tilden_test
scp rake_test/sensor.py maggi@maggi.local:~/tilden_test/rake_test/
scp rake_test/display_forest_rings.py maggi@maggi.local:~/tilden_test/rake_test/
scp rake_test/apply_voc_fix.sh maggi@maggi.local:~/tilden_test/rake_test/
scp rake_test/verify_voc.sh maggi@maggi.local:~/tilden_test/rake_test/
```

### Step 2: Apply the fix on Pi
```bash
# SSH to Pi:
ssh maggi@maggi.local

# Run deployment script:
cd ~/tilden_test/rake_test
./apply_voc_fix.sh
```

This will:
1. Stop the service
2. Verify files are updated
3. Restart the service
4. Show live logs

### Step 3: Verify (after 10 minutes)
```bash
# Run verification script:
./verify_voc.sh
```

This checks:
- Service is running
- Gas sensor is reporting values
- Log file has gas data
- Display is configured correctly

## What to Expect

### Display Changes
**Before:** 3 rings in a row (Temperature, Humidity, Pressure)  
**After:** 4 rings in 2x2 grid:
```
[Temperature °C]    [Humidity %]
[Pressure hPa]      [Air Quality kΩ]
```

### Log File Changes
**Before:**
```csv
timestamp,temperature,humidity,pressure,gas,latitude,longitude,altitude
2025-10-07...,22.5,48.2,1013.4,,,,
```

**After:**
```csv
timestamp,temperature,humidity,pressure,gas,latitude,longitude,altitude
2025-10-07...,22.5,48.2,1013.4,52340.5,,,
```

### Console Output
During warm-up (first 5-10 minutes):
```
Gas sensor: 45230 Ω (warming up, not stable yet)
```

After stabilization:
- No more "warming up" messages
- Steady readings (typically 50-150 kΩ)

## Understanding Gas/VOC Readings

**Gas Resistance Values:**
- **100+ kΩ**: Excellent air (clean outdoor air)
- **50-100 kΩ**: Good air (typical indoor)
- **20-50 kΩ**: Moderate (cooking, cleaning)
- **< 20 kΩ**: Poor (strong VOCs present)

**Lower resistance = More VOCs detected = Worse air quality**

### Test the Sensor:
- Breathe near it → resistance drops to 20-40 kΩ
- Hand sanitizer → drops below 20 kΩ
- Clean air → rises to 50-150+ kΩ

## Important Notes

1. **Warm-up Time**: The gas sensor needs **5-10 minutes** to warm up after power-on or service restart. This is normal for MOX sensors.

2. **Continuous Operation**: Once warmed up, the sensor maintains stable readings as long as the service keeps running.

3. **Heater Settings**: The sensor heats to 320°C for 150ms per reading. This is optimal for detecting general VOCs.

## Documentation

- **VOC_SENSOR_FIX.md** - Complete technical details
- **VOC_DEPLOYMENT.md** - Deployment instructions and troubleshooting

## Quick Commands

```bash
# Watch live logs
sudo journalctl -u rake-sensor.service -f

# Check service status
sudo systemctl status rake-sensor.service

# View recent gas readings
tail -20 ~/tilden_test/rake_test/rake_log_$(date +%Y%m%d)_*.csv

# Restart service
sudo systemctl restart rake-sensor.service
```

---

**Ready to deploy!** 🌲 Your soil monitor will now track complete environmental data including air quality!
