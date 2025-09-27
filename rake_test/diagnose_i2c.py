#!/usr/bin/env python3
"""
I2C diagnostic script for BME680 sensor troubleshooting.
"""

import os
import subprocess
import sys

def run_command(cmd):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def check_i2c_enabled():
    """Check if I2C is enabled."""
    print("=== Checking I2C Configuration ===")
    
    # Check if i2c modules are loaded
    returncode, stdout, stderr = run_command("lsmod | grep i2c")
    if returncode == 0 and stdout:
        print("✓ I2C modules are loaded:")
        print(stdout)
    else:
        print("✗ I2C modules not found. I2C might not be enabled.")
        print("Enable with: sudo raspi-config -> Interface Options -> I2C")
        return False
    
    # Check if i2c devices exist
    if os.path.exists("/dev/i2c-1"):
        print("✓ I2C device /dev/i2c-1 exists")
    else:
        print("✗ I2C device /dev/i2c-1 not found")
        return False
    
    return True

def scan_i2c_devices():
    """Scan for I2C devices."""
    print("\n=== Scanning I2C Bus ===")
    
    # Try i2cdetect
    returncode, stdout, stderr = run_command("i2cdetect -y 1")
    if returncode == 0:
        print("I2C devices found on bus 1:")
        print(stdout)
        
        # Look for common BME680 addresses
        if "76" in stdout:
            print("✓ Device found at 0x76 (BME680 secondary address)")
        if "77" in stdout:
            print("✓ Device found at 0x77 (BME680 primary address)")
        
        if "76" not in stdout and "77" not in stdout:
            print("✗ No BME680 found at expected addresses (0x76, 0x77)")
            print("Check wiring and connections")
    else:
        print("✗ Could not scan I2C bus. Install i2c-tools:")
        print("sudo apt-get install i2c-tools")

def check_python_libraries():
    """Check if required Python libraries are installed."""
    print("\n=== Checking Python Libraries ===")
    
    try:
        import bme680
        print("✓ bme680 library is installed")
        print(f"  Version: {bme680.__version__ if hasattr(bme680, '__version__') else 'unknown'}")
    except ImportError:
        print("✗ bme680 library not found")
        print("Install with: pip install bme680")
        return False
    
    try:
        import smbus
        print("✓ smbus library is available")
    except ImportError:
        try:
            import smbus2
            print("✓ smbus2 library is available")
        except ImportError:
            print("✗ Neither smbus nor smbus2 found")
            print("Install with: sudo apt-get install python3-smbus")
            return False
    
    return True

def test_bme680_connection():
    """Try to connect to BME680 sensor."""
    print("\n=== Testing BME680 Connection ===")
    
    try:
        import bme680
        
        addresses = [bme680.I2C_ADDR_PRIMARY, bme680.I2C_ADDR_SECONDARY]
        for addr in addresses:
            try:
                print(f"Trying BME680 at {hex(addr)}...")
                sensor = bme680.BME680(i2c_addr=addr)
                print(f"✓ BME680 found and initialized at {hex(addr)}")
                
                # Try to read data
                if sensor.get_sensor_data():
                    print(f"  Temperature: {sensor.data.temperature:.2f}°C")
                    print(f"  Humidity: {sensor.data.humidity:.2f}%")
                    print(f"  Pressure: {sensor.data.pressure:.2f} hPa")
                    if sensor.data.heat_stable:
                        print(f"  Gas: {sensor.data.gas_resistance} Ohms")
                    else:
                        print("  Gas: heating up...")
                    return True
                else:
                    print(f"  BME680 found at {hex(addr)} but failed to read data")
                    
            except Exception as e:
                print(f"✗ No BME680 at {hex(addr)}: {e}")
                continue
        
        print("✗ No working BME680 sensor found")
        return False
        
    except ImportError:
        print("✗ Cannot test BME680 - library not installed")
        return False

def main():
    """Main diagnostic function."""
    print("BME680 I2C Diagnostic Tool")
    print("=" * 40)
    
    # Check if running as root for some operations
    if os.geteuid() != 0:
        print("Note: Some checks may require sudo privileges")
    
    success = True
    success &= check_i2c_enabled()
    scan_i2c_devices()
    success &= check_python_libraries()
    success &= test_bme680_connection()
    
    print("\n" + "=" * 40)
    if success:
        print("✓ All checks passed! BME680 should work.")
    else:
        print("✗ Some issues found. Please address the problems above.")
        print("\nCommon solutions:")
        print("1. Enable I2C: sudo raspi-config -> Interface Options -> I2C")
        print("2. Install tools: sudo apt-get install i2c-tools python3-smbus")
        print("3. Install BME680: pip install bme680")
        print("4. Check wiring: VCC->3.3V, GND->GND, SDA->GPIO2, SCL->GPIO3")
    
    return success

if __name__ == "__main__":
    main()
