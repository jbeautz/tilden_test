# BME680 VOC/Gas Sensor Fix

## Problem Identified

The BME680 sensor was reading temperature, humidity, and pressure correctly, but the **gas/VOC readings were not being logged or displayed**.

### Root Causes:

1. **Gas sensor not returning values initially**: The gas sensor's heater needs 5-10 minutes to warm up and stabilize before accurate readings are available.

2. **Code only logged "stable" readings**: The original code only returned gas values when `heat_stable` was True:
   ```python
   'gas': sensor.data.gas_resistance if sensor.data.heat_stable else None
   ```

3. **Display didn't show gas data**: The GUI only showed 3 tree rings (temperature, humidity, pressure) - no visualization for gas/VOC.

## What Was Fixed

### 1. Sensor Reading (`sensor.py`)
- ✅ Changed to **always return gas_resistance** value (even during warm-up)
- ✅ Added logging to show gas sensor status
- ✅ Added note that sensor needs 5-10 minutes to stabilize

### 2. Display (`display_forest_rings.py`)
- ✅ Added `gas_history` deque to track VOC readings
- ✅ Updated layout to **2x2 grid** showing all 4 measurements:
  - Top row: Temperature, Humidity
  - Bottom row: Pressure, Air Quality (VOC)
- ✅ Gas displayed in **kΩ** (kilohms) for better readability
- ✅ Label changed to "Air Quality" for user-friendly display

### 3. Understanding Gas Readings

**BME680 Gas Sensor Operation:**
- Measures **gas resistance** in Ohms (Ω)
- Typical range: 10,000 - 200,000 Ω (10 kΩ - 200 kΩ)
- **Lower resistance = more VOCs detected** (worse air quality)
- **Higher resistance = cleaner air** (better air quality)

**Warm-up Period:**
- Heater runs at 320°C for 150ms per reading
- Takes **5-10 minutes** of continuous operation to stabilize
- Initial readings may fluctuate until stable

## How to Deploy

### On the Pi, run:

```bash
cd ~/tilden_test/rake_test

# Stop the service
sudo systemctl stop rake-sensor.service

# Pull the updated code (if using git)
# git pull

# Or copy the files manually from your Mac
# Then restart the service
sudo systemctl start rake-sensor.service

# Check the logs to see gas readings
sudo journalctl -u rake-sensor.service -f
```

You should now see messages like:
```
Gas sensor: 45230 Ω (warming up, not stable yet)
Gas sensor: 52180 Ω (warming up, not stable yet)
...
```

After 5-10 minutes, the readings will stabilize and you'll stop seeing the "warming up" message.

## Verifying It Works

### 1. Check the log file:
```bash
tail -20 ~/tilden_test/rake_test/rake_log_$(date +%Y%m%d)_*.csv
```

You should see the **gas column filled with values** (not empty):
```csv
timestamp,temperature,humidity,pressure,gas,latitude,longitude,altitude
2025-10-07T09:30:15,22.5,48.2,1013.4,45230.5,,,
2025-10-07T09:30:16,22.5,48.3,1013.4,45890.2,,,
```

### 2. Check the display:
The GUI should now show **4 tree rings** in a 2x2 grid:
- Temperature (°C)
- Humidity (%)
- Pressure (hPa)
- Air Quality (kΩ)

### 3. Test air quality changes:
To verify the sensor is working, try:
- Breathe near the sensor → resistance should **drop** (more VOCs)
- Use hand sanitizer nearby → resistance should **drop significantly**
- Clean air → resistance should be **higher** (50-200 kΩ typically)

## Technical Notes

### Gas Resistance Interpretation:
- **> 100 kΩ**: Very clean air
- **50-100 kΩ**: Good air quality (typical indoor)
- **20-50 kΩ**: Moderate (some VOCs present)
- **< 20 kΩ**: Poor air quality (high VOC concentration)

### Why it takes time to stabilize:
The BME680 uses a **metal oxide gas sensor** that requires heating. The heater must:
1. Reach target temperature (320°C)
2. Burn off contaminants
3. Achieve thermal equilibrium
4. Stabilize chemical reactions

This is normal behavior for MOX sensors and cannot be rushed.

## Files Modified

1. **sensor.py**:
   - Always returns gas_resistance value
   - Added status logging
   - Added warm-up notification

2. **display_forest_rings.py**:
   - Added gas_history deque
   - Changed layout to 2x2 grid
   - Added "Air Quality" ring showing VOC in kΩ
   - Handles None values gracefully

## Next Steps

After deploying these changes:
1. ✅ Let the system run for 10-15 minutes
2. ✅ Verify gas column has values in the CSV logs
3. ✅ Check the display shows the 4th tree ring (Air Quality)
4. ✅ Test sensor response by introducing VOCs nearby

The system will now log complete environmental data including air quality!
