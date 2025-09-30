"""
Interactive main loop with start/stop recording and live graphs.
Run on Mac for GUI testing, then deploy to Pi.
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

LOOP_DELAY = 1  # update every second for smoother graphs
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
    print("Starting interactive environment monitor...")
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    init_log()

    print("Press SPACE or click START to begin recording.")
    print(f"DEBUG: Initial recording state: {display.is_recording()}")

    global running
    while running:
        actions = display.handle_events()
        if actions.get('quit'):
            break
        if actions.get('toggle_record'):
            state = display.toggle_recording()
            print(f"Recording {'ENABLED' if state else 'PAUSED'}")

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

        # Update history
        for k in history.keys():
            history[k].append(merged.get(k))

        if display.is_recording():
            log_data(merged)

        display.render(merged, {k: list(v) for k, v in history.items()})

        time.sleep(LOOP_DELAY)

    print("Exiting.")


if __name__ == '__main__':
    main()
