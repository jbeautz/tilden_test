"""
CSV logging module for sensor data.
"""
import csv
import os
from datetime import datetime

# Field names for CSV
FIELD_NAMES = ['timestamp', 'temperature', 'humidity', 'pressure', 'gas']

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
        with open(LOG_FILE, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header row
            writer.writerow(FIELD_NAMES)
            
            # Add session marker
            session_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([f"# New session {session_time}", "", "", "", ""])
            
            print(f"Created new log file: {LOG_FILE}")
            print(f"Session started at {session_time}")
            
    except Exception as e:
        print(f"Error initializing log file: {e}")
        LOG_FILE = None

def log_data(data):
    """
    Log sensor data to CSV file.
    
    Args:
        data (dict): Dictionary containing sensor readings with keys matching FIELD_NAMES
    """
    global LOG_FILE
    
    if LOG_FILE is None:
        print("Error: Log file not initialized. Call init_log() first.")
        return
        
    try:
        with open(LOG_FILE, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELD_NAMES)
            writer.writerow(data)
            
    except Exception as e:
        print(f"Error logging data: {e}")
