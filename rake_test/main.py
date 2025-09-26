"""
Main application for BME680 sensor data logging.
"""
import time
import signal
import sys
from sensor import read_sensor
from logger import log_data, init_log

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\nReceived interrupt signal. Shutting down gracefully...")
    sys.exit(0)

def main():
    """Main application loop."""
    print("Starting BME680 sensor logging...")
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize logging
    init_log()
    
    print("Starting data collection loop. Press Ctrl+C to stop.")
    print("-" * 50)
    
    try:
        while True:
            # Read sensor data
            sensor_data = read_sensor()
            
            # Log the data
            log_data(sensor_data)
            
            # Print the logged data
            print(f"Logged: {sensor_data}")
            
            # Sleep for 1 second
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received. Exiting gracefully...")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        print("Data logging stopped.")

if __name__ == "__main__":
    main()
