#!/usr/bin/env python3
"""
SIMPLE LOGGING ONLY VERSION
No display, no complexity - just logs sensor data at 1 Hz.
This WILL work.
"""
import time
import os
from datetime import datetime
from sensor import read_sensor
from gps import read_data as read_gps
from logger import log_data, init_log

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

print("Starting simple soil monitor (logging only)...")
print("No display - just continuous 1 Hz logging.")

init_log()
print("Logger initialized successfully")

count = 0
while True:
    try:
        # Read sensors
        sensor_data = read_sensor() or {}
        gps_data = read_gps() or {}
        
        # Merge data
        data = {**sensor_data}
        for k in ['latitude', 'longitude', 'altitude']:
            if k in gps_data:
                data[k] = gps_data[k]
        
        # Log it
        log_data(data)
        count += 1
        
        if count % 10 == 0:
            print(f"✓ {count} records logged")
        
        # Wait 1 second
        time.sleep(1.0)
        
    except KeyboardInterrupt:
        print(f"\nStopped by user. Total records: {count}")
        break
    except Exception as e:
        print(f"Error (continuing): {e}")
        time.sleep(1.0)
