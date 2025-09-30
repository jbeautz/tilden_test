"""
CSV logging module for sensor + GPS data.
"""
import csv
import os
from datetime import datetime

# Field names for CSV (extended with GPS)
FIELD_NAMES = ['timestamp', 'temperature', 'humidity', 'pressure', 'gas', 'latitude', 'longitude', 'altitude']

# Generate unique log file name based on boot time
def generate_log_filename():
    """Generate a unique log filename based on current timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"rake_log_{timestamp}.csv"

# Log file will be set when init_log() is called
LOG_FILE = None

def init_log():
    """
    Initialize a new log file for this boot session.
    - Creates a new CSV file with timestamp in filename
    - Writes header row and session marker
    """
    global LOG_FILE
    
    # Generate unique filename for this session
    LOG_FILE = generate_log_filename()
    
    try:
        with open(LOG_FILE, 'w', newline='') as f:
            w = csv.writer(f)
            
            # Write header row
            w.writerow(FIELD_NAMES)
            
            session_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Session marker row (first cell only, rest blank)
            w.writerow([f"# New session {session_time}"] + ["" for _ in FIELD_NAMES[1:]])
            
        print(f"Created new log file: {LOG_FILE}")
        print(f"Session started at {session_time}")
        
    except Exception as e:
        print(f"Error initializing log file: {e}")
        LOG_FILE = None

def log_data(data: dict):
    """
    Log sensor data to CSV file.
    
    Args:
        data (dict): Dictionary containing sensor readings with keys matching FIELD_NAMES
    """
    global LOG_FILE
    
    if LOG_FILE is None:
        print("Error: Log file not initialized. Call init_log() first.")
        return
        
    # Add timestamp if not present
    data_with_timestamp = dict(data)
    if 'timestamp' not in data_with_timestamp or data_with_timestamp['timestamp'] is None:
        data_with_timestamp['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Prepare row data, filling missing fields with blank string
    row = {k: ("" if data_with_timestamp.get(k) is None else data_with_timestamp.get(k)) for k in FIELD_NAMES}
    
    try:
        with open(LOG_FILE, 'a', newline='') as f:
            w = csv.DictWriter(f, fieldnames=FIELD_NAMES)
            w.writerow(row)
# Removed debug output
            
    except Exception as e:
        print(f"Error logging data: {e}")
