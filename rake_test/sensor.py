"""
BME680 sensor module for reading environmental data.
"""
import time
from datetime import datetime
try:
    import bme680
except ImportError:
    print("Warning: bme680 library not found. Install with: pip install bme680")
    bme680 = None

# Initialize sensor globally
sensor = None

def initialize_sensor():
    """Initialize the BME680 sensor with I2C communication."""
    global sensor
    
    if bme680 is None:
        print("BME680 library not available")
        return False
    
    try:
        # Loop through all I2C addresses to find the sensor
        # Try 0x77 first since that's where your sensor is located
        sensor_found = False
        addresses_to_try = [0x77, 0x76]  # Try 0x77 first, then 0x76
        
        for addr in addresses_to_try:
            try:
                print(f"Trying BME680 at address {hex(addr)}")
                sensor = bme680.BME680(i2c_addr=addr)
                print(f"Found BME680 at {hex(addr)}")
                sensor_found = True
                break
            except IOError as e:
                print(f"No BME680 found at {hex(addr)}: {e}")
                continue
        
        if not sensor_found:
            # If no sensor found at any address
            print("No BME680 sensor found at any I2C address")
            print("Please check:")
            print("1. BME680 is properly connected")
            print("2. I2C is enabled: sudo raspi-config -> Interface Options -> I2C")
            print("3. Check I2C devices: sudo i2cdetect -y 1")
            return False
        
        # Configure sensor settings
        sensor.set_humidity_oversample(bme680.OS_2X)
        sensor.set_pressure_oversample(bme680.OS_4X)
        sensor.set_temperature_oversample(bme680.OS_8X)
        sensor.set_filter(bme680.FILTER_SIZE_3)
        sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
        
        # Set gas sensor settings
        # Temperature in Celsius (320°C is good for air quality sensing)
        sensor.set_gas_heater_temperature(320)
        # Duration in milliseconds (150ms per reading)
        sensor.set_gas_heater_duration(150)
        sensor.select_gas_heater_profile(0)
        
        print("BME680 sensor initialized successfully")
        print("Note: Gas sensor needs 5-10 minutes to stabilize for accurate readings")
        return True
        
    except Exception as e:
        print(f"Failed to initialize BME680 sensor: {e}")
        return False

def read_sensor():
    """
    Read data from the BME680 sensor.
    
    Returns:
        dict: Dictionary with keys: timestamp, temperature, humidity, pressure, gas
    """
    global sensor
    
    # Initialize sensor if not already done
    if sensor is None:
        if not initialize_sensor():
            return {
                'timestamp': datetime.now().isoformat(),
                'temperature': None,
                'humidity': None,
                'pressure': None,
                'gas': None
            }
    
    try:
        # Get sensor readings
        if sensor.get_sensor_data():
            timestamp = datetime.now().isoformat()
            
            # Always return gas_resistance value, even if heater not stable yet
            # Gas readings stabilize after 5-10 minutes of continuous operation
            gas_value = sensor.data.gas_resistance if hasattr(sensor.data, 'gas_resistance') else None
            heat_stable = sensor.data.heat_stable if hasattr(sensor.data, 'heat_stable') else False
            
            data = {
                'timestamp': timestamp,
                'temperature': sensor.data.temperature,
                'humidity': sensor.data.humidity,
                'pressure': sensor.data.pressure,
                'gas': gas_value
            }
            
            # Log gas sensor status occasionally (every 10th reading to avoid spam)
            import random
            if random.randint(1, 10) == 1:  # Log 10% of the time
                if gas_value is None:
                    print("Gas sensor: No reading available")
                elif not heat_stable:
                    print(f"Gas sensor: {gas_value:.0f} Ω (warming up)")
                else:
                    print(f"Gas sensor: {gas_value:.0f} Ω (stable)")
            
            return data
        else:
            print("Failed to get sensor data")
            return {
                'timestamp': datetime.now().isoformat(),
                'temperature': None,
                'humidity': None,
                'pressure': None,
                'gas': None
            }
            
    except Exception as e:
        print(f"Error reading sensor: {e}")
        return {
            'timestamp': datetime.now().isoformat(),
            'temperature': None,
            'humidity': None,
            'pressure': None,
            'gas': None
        }

# Initialize sensor on module import
initialize_sensor()
