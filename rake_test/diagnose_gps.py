#!/usr/bin/env python3
"""
GPS Diagnostic Script for GY-GPS6MV2 at 9600 baud
This script helps diagnose GPS sensor connection and data reception
"""

import os
import subprocess
import sys
import time
from datetime import datetime

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

def check_serial_configuration():
    """Check serial port configuration for GPS"""
    print("=" * 60)
    print("GPS SERIAL PORT DIAGNOSTIC")
    print("=" * 60)
    
    # Check if serial port exists
    run_command("ls -la /dev/serial*", "Checking serial port devices")
    
    # Check UART configuration in boot config
    print("\nChecking UART configuration in /boot/config.txt:")
    try:
        with open('/boot/config.txt', 'r') as f:
            config = f.read()
            if 'enable_uart=1' in config:
                print("✓ UART is enabled in boot config")
            else:
                print("❌ UART may not be enabled - need 'enable_uart=1'")
            
            if 'dtparam=uart0=on' in config:
                print("✓ UART0 is enabled")
            else:
                print("⚠️  UART0 parameter not explicitly set")
    except Exception as e:
        print(f"❌ Could not read boot config: {e}")
    
    # Check if serial console is disabled
    run_command("cat /proc/cmdline", "Checking kernel command line (should not have console=serial)")
    
    # Check permissions on serial port
    run_command("ls -la /dev/serial0", "Checking serial port permissions")
    
    # Check if user is in dialout group
    run_command("groups $USER", "Checking user groups (should include 'dialout')")

def test_raw_serial_data():
    """Test raw data from GPS serial port"""
    print("\n" + "=" * 60)
    print("RAW GPS DATA TEST")
    print("=" * 60)
    
    try:
        import serial
        print("✓ PySerial library is available")
        
        # Try to open serial port
        print(f"\nTrying to open /dev/serial0 at 9600 baud...")
        ser = serial.Serial('/dev/serial0', 9600, timeout=2)
        print("✓ Serial port opened successfully")
        
        print("\nReading raw GPS data for 10 seconds...")
        print("(Looking for NMEA sentences like $GPGGA, $GPRMC, etc.)")
        print("-" * 50)
        
        start_time = time.time()
        line_count = 0
        gga_count = 0
        
        while time.time() - start_time < 10:
            try:
                line = ser.readline().decode('ascii', errors='ignore').strip()
                if line:
                    line_count += 1
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] {line}")
                    
                    if 'GGA' in line:
                        gga_count += 1
                        
                    # Show first few lines then just count
                    if line_count > 20:
                        print(f"... (showing first 20 lines, total received: {line_count})")
                        break
                        
            except Exception as e:
                print(f"Error reading line: {e}")
                
        ser.close()
        
        print(f"\n📊 Summary:")
        print(f"   Total lines received: {line_count}")
        print(f"   GGA sentences (GPS fixes): {gga_count}")
        
        if line_count == 0:
            print("❌ No data received - check GPS connections and power")
            return False
        elif gga_count == 0:
            print("⚠️  Data received but no GPS fixes - GPS may need more time to acquire satellites")
            return True
        else:
            print("✅ GPS data received successfully!")
            return True
            
    except ImportError:
        print("❌ PySerial not installed - run: pip install pyserial")
        return False
    except PermissionError:
        print("❌ Permission denied - try adding user to dialout group:")
        print("   sudo usermod -a -G dialout $USER")
        print("   Then logout and login again")
        return False
    except Exception as e:
        print(f"❌ Serial test failed: {e}")
        return False

def test_gps_library():
    """Test GPS using our gps.py library"""
    print("\n" + "=" * 60)
    print("TESTING GPS LIBRARY")
    print("=" * 60)
    
    try:
        # Import our GPS module
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        import gps
        
        print("✓ GPS module imported successfully")
        
        # Initialize GPS
        if gps.init_gps():
            print("✓ GPS initialized successfully")
        else:
            print("❌ GPS initialization failed")
            return False
        
        # Try to read GPS data
        print("\nReading GPS data for 15 seconds...")
        print("(Waiting for valid GPS fix...)")
        
        for i in range(15):
            data = gps.read_data()
            if data:
                print(f"✅ GPS fix received!")
                print(f"   Timestamp: {data.get('timestamp')}")
                print(f"   Latitude: {data.get('latitude')}")
                print(f"   Longitude: {data.get('longitude')}")
                print(f"   Altitude: {data.get('altitude')} m")
                return True
            else:
                print(f"   Attempt {i+1}/15: No fix yet...")
                time.sleep(1)
        
        print("⚠️  No GPS fix received - GPS may need more time or better satellite view")
        return False
        
    except ImportError as e:
        print(f"❌ Failed to import GPS module: {e}")
        return False
    except Exception as e:
        print(f"❌ GPS library test failed: {e}")
        return False

def provide_gps_recommendations():
    """Provide GPS troubleshooting recommendations"""
    print("\n" + "=" * 60)
    print("GPS TROUBLESHOOTING RECOMMENDATIONS")
    print("=" * 60)
    
    print("\n1. Hardware Connections:")
    print("   GPS VCC  → Pi 3.3V or 5V (Pin 2 or 4)")
    print("   GPS GND  → Pi GND (Pin 6)")
    print("   GPS TXD  → Pi RXD (Pin 10, GPIO 15)")
    print("   GPS RXD  → Pi TXD (Pin 8, GPIO 14)")
    
    print("\n2. Enable UART in Raspberry Pi:")
    print("   sudo raspi-config")
    print("   → Interface Options → Serial Port")
    print("   → Enable serial port hardware: YES")
    print("   → Enable serial console over serial port: NO")
    print("   → Reboot required")
    
    print("\n3. Manual configuration (if raspi-config doesn't work):")
    print("   Add to /boot/config.txt:")
    print("     enable_uart=1")
    print("     dtparam=uart0=on")
    print("   Remove 'console=serial0,115200' from /boot/cmdline.txt")
    
    print("\n4. Install required packages:")
    print("   sudo apt update")
    print("   sudo apt install -y python3-pip")
    print("   pip install pyserial pynmea2")
    
    print("\n5. Add user to dialout group:")
    print("   sudo usermod -a -G dialout $USER")
    print("   Logout and login again")
    
    print("\n6. GPS troubleshooting:")
    print("   - Move GPS to location with clear sky view")
    print("   - Wait 5-15 minutes for initial satellite acquisition")
    print("   - Check GPS LED (should blink when receiving data)")
    print("   - Verify 3.3V or 5V power supply to GPS")
    
    print("\n7. Test commands:")
    print("   # Check raw GPS data:")
    print("   sudo cat /dev/serial0")
    print("   # Should show NMEA sentences like $GPGGA,$GPRMC,etc.")

if __name__ == "__main__":
    print("🛰️  GPS DIAGNOSTIC SCRIPT (9600 BAUD)")
    print("=" * 60)
    
    # Run diagnostics
    check_serial_configuration()
    raw_serial_works = test_raw_serial_data()
    gps_library_works = test_gps_library()
    provide_gps_recommendations()
    
    print("\n" + "=" * 60)
    print("📋 DIAGNOSTIC RESULTS:")
    print(f"Raw serial data: {'✅ Works' if raw_serial_works else '❌ Failed'}")
    print(f"GPS library: {'✅ Works' if gps_library_works else '❌ Failed'}")
    
    if raw_serial_works and gps_library_works:
        print("\n🎉 GPS sensor is working correctly!")
        print("   Your GPS is ready to use with the environmental monitor.")
    elif raw_serial_works:
        print("\n⚠️  GPS hardware works but library needs attention")
        print("   Check the recommendations above.")
    else:
        print("\n❌ GPS sensor needs configuration")
        print("   Follow the troubleshooting recommendations above.")
    
    sys.exit(0 if (raw_serial_works and gps_library_works) else 1)
