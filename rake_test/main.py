"""
Continuous data logger with live display.
Logs sensor data at 1 Hz from power-on until power-off.
"""
import time
import signal
import sys
from collections import deque
from datetime import datetime
from sensor import read_sensor
from gps import read_data as read_gps
from logger import log_data, init_log
import display_forest_rings as display

LOOP_DELAY = 1.0  # Log data at 1 Hz (once per second)
DISPLAY_UPDATE_RATE = 0.1  # Update display 10x per second for smooth UI
HISTORY_LEN = 120

history = {
    'temperature': deque(maxlen=HISTORY_LEN),
    'humidity': deque(maxlen=HISTORY_LEN),
    'pressure': deque(maxlen=HISTORY_LEN)
}

running = True


def signal_handler(sig, frame):
    global running
    running = False


def _simulate_if_missing(data):
    # Provide simple synthetic values when None (for Mac testing without hardware)
    base_t = len(history['temperature'])
    if data.get('temperature') is None:
        data['temperature'] = 22.0 + 0.5 * __import__('math').sin(base_t / 15)
    if data.get('humidity') is None:
        data['humidity'] = 45.0 + 5 * __import__('math').sin(base_t / 25)
    if data.get('pressure') is None:
        data['pressure'] = 1013 + 2 * __import__('math').sin(base_t / 40)
    return data


def main():
    print("Starting continuous soil monitor...")
    print("Logging data at 1 Hz until powered off.")
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    init_log()
    
    # Set display to always be in monitoring mode
    display.set_continuous_mode()

    global running
    last_log_time = 0
    last_sensor_read = 0
    
    # Cache for sensor data between reads
    cached_merged = {
        'temperature': None,
        'humidity': None,
        'pressure': None,
        'latitude': None,
        'longitude': None,
        'altitude': None
    }
    
    while running:
        current_time = time.time()
        
        # Handle display events (but ignore quit - system runs until powered off)
        try:
            display.handle_events()
        except Exception as e:
            print(f"Display event error (ignoring): {e}")

        # Read sensors and GPS only once per second (at logging time)
        if current_time - last_sensor_read >= LOOP_DELAY:
            sensor_data = read_sensor() or {}
            gps_data = read_gps() or {}

            merged = {**sensor_data}
            for k in ['latitude', 'longitude', 'altitude']:
                if k in gps_data:
                    merged[k] = gps_data[k]
            merged.setdefault('latitude', None)
            merged.setdefault('longitude', None)
            merged.setdefault('altitude', None)
            merged = _simulate_if_missing(merged)
            
            # Update cache
            cached_merged = merged
            
            # Update history for display
            for k in history.keys():
                if k in merged:
                    history[k].append(merged.get(k))

            # Log data at 1 Hz
            if current_time - last_log_time >= LOOP_DELAY:
                print(f"DEBUG: Logging data at {datetime.now().strftime('%H:%M:%S')}")
                log_data(merged)
                last_log_time = current_time
            
            last_sensor_read = current_time

        # Update display (uses cached data)
        try:
            display.render(cached_merged, {k: list(v) for k, v in history.items()})
        except Exception as e:
            print(f"Display render error (ignoring): {e}")

        time.sleep(DISPLAY_UPDATE_RATE)

    print("Exiting - this should never happen (system runs until powered off)")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user (Ctrl+C)")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        # Exit with error code so systemd can restart if needed
        exit(1)
