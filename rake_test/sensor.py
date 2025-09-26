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
        sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
        
        # Configure sensor settings
        sensor.set_humidity_oversample(bme680.OS_2X)
        sensor.set_pressure_oversample(bme680.OS_4X)
        sensor.set_temperature_oversample(bme680.OS_8X)
        sensor.set_filter(bme680.FILTER_SIZE_3)
        sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
        
        # Set gas sensor settings
        sensor.set_gas_heater_temperature(320)
        sensor.set_gas_heater_duration(150)
        sensor.select_gas_heater_profile(0)
        
        print("BME680 sensor initialized successfully")
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
            
            data = {
                'timestamp': timestamp,
                'temperature': sensor.data.temperature,
                'humidity': sensor.data.humidity,
                'pressure': sensor.data.pressure,
                'gas': sensor.data.gas_resistance if sensor.data.heat_stable else None
            }
            
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
