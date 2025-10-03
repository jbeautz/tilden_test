#!/usr/bin/env python3
"""
Diagnostic script to test logging independently of display.
This will help us isolate the logging issue.
"""

import os
import sys
from datetime import datetime

# Add current directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

print(f"Script directory: {SCRIPT_DIR}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python executable: {sys.executable}")
print()

# Test 1: Can we import the modules?
print("=" * 60)
print("TEST 1: Import modules")
print("=" * 60)
try:
    import logger
    print("✓ logger module imported successfully")
    print(f"  Logger module location: {logger.__file__}")
except Exception as e:
    print(f"✗ Failed to import logger: {e}")
    sys.exit(1)

try:
    import sensor
    print("✓ sensor module imported successfully")
except Exception as e:
    print(f"✗ Failed to import sensor: {e}")

try:
    import gps
    print("✓ gps module imported successfully")
except Exception as e:
    print(f"✗ Failed to import gps: {e}")

print()

# Test 2: Can we generate a log filename?
print("=" * 60)
print("TEST 2: Generate log filename")
print("=" * 60)
try:
    log_filename = logger.generate_log_filename()
    print(f"✓ Generated log filename: {log_filename}")
    
    # Check if it's an absolute path
    if os.path.isabs(log_filename):
        print(f"✓ Filename is absolute path")
        print(f"  Directory: {os.path.dirname(log_filename)}")
        print(f"  Basename: {os.path.basename(log_filename)}")
    else:
        print(f"✗ WARNING: Filename is relative: {log_filename}")
        
    # Check if directory exists
    log_dir = os.path.dirname(log_filename)
    if os.path.exists(log_dir):
        print(f"✓ Log directory exists")
        if os.access(log_dir, os.W_OK):
            print(f"✓ Log directory is writable")
        else:
            print(f"✗ Log directory is NOT writable!")
    else:
        print(f"✗ Log directory does NOT exist: {log_dir}")
except Exception as e:
    print(f"✗ Failed to generate log filename: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 3: Can we initialize logging?
print("=" * 60)
print("TEST 3: Initialize logging")
print("=" * 60)
try:
    logger.init_log()
    print("✓ Logger initialized successfully")
    
    # Check if file was created
    if os.path.exists(log_filename):
        print(f"✓ Log file created: {log_filename}")
        file_size = os.path.getsize(log_filename)
        print(f"  File size: {file_size} bytes")
        
        # Read the header
        with open(log_filename, 'r') as f:
            header = f.readline().strip()
            print(f"  Header: {header}")
    else:
        print(f"✗ Log file was NOT created: {log_filename}")
except Exception as e:
    print(f"✗ Failed to initialize logger: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 4: Can we read sensors?
print("=" * 60)
print("TEST 4: Read sensor data")
print("=" * 60)
try:
    sensor_data = sensor.read_data()
    if sensor_data:
        print(f"✓ Sensor data read successfully:")
        for key, value in sensor_data.items():
            print(f"    {key}: {value}")
    else:
        print(f"⚠ Sensor returned None/empty data")
except Exception as e:
    print(f"✗ Failed to read sensor: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 5: Can we log data?
print("=" * 60)
print("TEST 5: Log test data")
print("=" * 60)
test_data = {
    'timestamp': datetime.now().isoformat(),
    'temperature': 25.5,
    'humidity': 50.0,
    'pressure': 1013.25,
    'gas_resistance': 50000,
    'latitude': 37.7749,
    'longitude': -122.4194,
    'altitude': 10.0
}

try:
    logger.log_data(test_data)
    print("✓ Test data logged successfully")
    
    # Verify the data was written
    if os.path.exists(log_filename):
        file_size = os.path.getsize(log_filename)
        print(f"  File size after logging: {file_size} bytes")
        
        # Read last line
        with open(log_filename, 'r') as f:
            lines = f.readlines()
            if len(lines) > 1:
                last_line = lines[-1].strip()
                print(f"  Last line: {last_line}")
            else:
                print(f"⚠ File only has {len(lines)} line(s)")
    else:
        print(f"✗ Log file disappeared!")
except Exception as e:
    print(f"✗ Failed to log data: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
print(f"\nIf all tests passed, logging should work in main.py")
print(f"Log file location: {log_filename}")
