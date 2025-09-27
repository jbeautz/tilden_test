#!/usr/bin/env python3
"""
BME680 I2C Diagnostic Script
This script helps diagnose BME680 sensor connection issues
"""

import os
import subprocess
import sys

def run_command(cmd, description):
    """Run a command and return its output"""
    print(f"\n{description}:")
    print(f"Running: {cmd}")
    print("-" * 50)
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Failed to run command: {e}")
        return False

def check_i2c_status():
    """Check I2C interface status"""
    print("=" * 60)
    print("BME680 I2C DIAGNOSTIC SCRIPT")
    print("=" * 60)
    
    # Check if I2C is enabled
    run_command("sudo raspi-config nonint get_i2c", "Checking if I2C is enabled")
    
    # List loaded I2C modules
    run_command("lsmod | grep i2c", "Checking loaded I2C modules")
    
    # Check I2C devices
    run_command("ls -la /dev/i2c*", "Checking I2C device files")
    
    # Detect I2C devices on bus 1 (most common for Pi)
    print("\nScanning I2C bus 1 for devices...")
    run_command("sudo i2cdetect -y 1", "I2C device scan (bus 1)")
    
    # If bus 1 doesn't work, try bus 0
    print("\nScanning I2C bus 0 for devices...")
    run_command("sudo i2cdetect -y 0", "I2C device scan (bus 0)")
    
    # Check GPIO configuration
    run_command("gpio readall | grep -E 'SDA|SCL'", "Checking GPIO pins for I2C")

def test_bme680_library():
    """Test BME680 library import and basic functionality"""
    print("\n" + "=" * 60)
    print("TESTING BME680 LIBRARY")
    print("=" * 60)
    
    try:
        import bme680
        print(f"✓ BME680 library imported successfully")
        print(f"  Primary I2C address: {hex(bme680.I2C_ADDR_PRIMARY)}")
        print(f"  Secondary I2C address: {hex(bme680.I2C_ADDR_SECONDARY)}")
        
        # Try to initialize sensor at both addresses (0x77 first)
        for addr in [0x77, 0x76]:
            print(f"\nTrying to initialize BME680 at {hex(addr)}...")
            try:
                sensor = bme680.BME680(i2c_addr=addr)
                print(f"✓ BME680 successfully initialized at {hex(addr)}")
                
                # Try to get sensor data
                if sensor.get_sensor_data():
                    print(f"✓ Sensor data retrieved successfully")
                    print(f"  Temperature: {sensor.data.temperature:.2f}°C")
                    print(f"  Humidity: {sensor.data.humidity:.2f}%")
                    print(f"  Pressure: {sensor.data.pressure:.2f}hPa")
                    if sensor.data.heat_stable:
                        print(f"  Gas resistance: {sensor.data.gas_resistance}Ω")
                    else:
                        print(f"  Gas sensor heating up...")
                    return True
                else:
                    print(f"✗ Failed to get sensor data")
            except Exception as e:
                print(f"✗ Failed to initialize at {hex(addr)}: {e}")
        
        print(f"\n✗ No BME680 sensor found at any address")
        return False
        
    except ImportError as e:
        print(f"✗ Failed to import BME680 library: {e}")
        print("  Install with: pip3 install bme680")
        return False

def provide_recommendations():
    """Provide troubleshooting recommendations"""
    print("\n" + "=" * 60)
    print("TROUBLESHOOTING RECOMMENDATIONS")
    print("=" * 60)
    
    print("\n1. Enable I2C interface:")
    print("   sudo raspi-config")
    print("   → Interface Options → I2C → Enable")
    print("   → Reboot required after enabling")
    
    print("\n2. Check physical connections:")
    print("   BME680 VCC  → Pi 3.3V (Pin 1 or 17)")
    print("   BME680 GND  → Pi GND  (Pin 6, 9, 14, 20, 25, 30, 34, 39)")
    print("   BME680 SDA  → Pi SDA  (Pin 3, GPIO 2)")
    print("   BME680 SCL  → Pi SCL  (Pin 5, GPIO 3)")
    
    print("\n3. Install required packages:")
    print("   sudo apt update")
    print("   sudo apt install -y python3-pip i2c-tools")
    print("   pip3 install bme680")
    
    print("\n4. Test I2C communication:")
    print("   sudo i2cdetect -y 1")
    print("   (Should show device at 0x76 or 0x77)")
    
    print("\n5. Check for hardware issues:")
    print("   - Try different jumper wires")
    print("   - Check soldering connections")
    print("   - Verify sensor board is not damaged")
    print("   - Try a different I2C address (if jumper available)")

if __name__ == "__main__":
    check_i2c_status()
    sensor_working = test_bme680_library()
    provide_recommendations()
    
    if sensor_working:
        print(f"\n🎉 BME680 sensor is working correctly!")
        sys.exit(0)
    else:
        print(f"\n❌ BME680 sensor is not working. Check the recommendations above.")
        sys.exit(1)
