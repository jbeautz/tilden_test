"""
CSV logging module for sensor + GPS data.
"""
import csv
import os
from datetime import datetime

# Field names for CSV (extended with GPS)
FIELD_NAMES = ['timestamp', 'temperature', 'humidity', 'pressure', 'gas', 'latitude', 'longitude', 'altitude']

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Generate unique log file name based on boot time
def generate_log_filename():
    """Generate a unique log filename with absolute path based on current timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rake_log_{timestamp}.csv"
    # Return absolute path in the same directory as this script
    return os.path.join(SCRIPT_DIR, filename)

# Log file will be set when init_log() is called
LOG_FILE = None
_initialized = False

def init_log():
    """
    Initialize a new log file for this boot session.
    - Creates a new CSV file with timestamp in filename
    - Writes header row and session marker
    - Only initializes once per process (prevents multiple file creation)
    """
    global LOG_FILE, _initialized
    
    # Prevent multiple initializations
    if _initialized and LOG_FILE and os.path.exists(LOG_FILE):
        print(f"Log already initialized: {LOG_FILE}")
        return
    
    # Force re-initialization if file doesn't exist
    if _initialized and LOG_FILE and not os.path.exists(LOG_FILE):
        print(f"Warning: Previous log file {LOG_FILE} not found, reinitializing...")
        _initialized = False
    
    # Generate unique filename for this session
    LOG_FILE = generate_log_filename()
    _initialized = True
    
    try:
        # Ensure directory exists
        os.makedirs(SCRIPT_DIR, exist_ok=True)
        
        with open(LOG_FILE, 'w', newline='') as f:
            w = csv.writer(f)
            
            # Write header row
            w.writerow(FIELD_NAMES)
            
            session_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Session marker row (first cell only, rest blank)
            w.writerow([f"# New session {session_time}"] + ["" for _ in FIELD_NAMES[1:]])
            
        print(f"✓ Created new log file: {LOG_FILE}")
        print(f"✓ Session started at {session_time}")
        print(f"✓ Logging to: {os.path.abspath(LOG_FILE)}")
        
    except Exception as e:
        print(f"ERROR initializing log file: {e}")
        import traceback
        traceback.print_exc()
        LOG_FILE = None
        _initialized = False

def log_data(data: dict):
    """
    Log sensor data to CSV file.
    
    Args:
        data (dict): Dictionary containing sensor readings with keys matching FIELD_NAMES
    """
    global LOG_FILE
    
    if LOG_FILE is None:
        print("ERROR: Log file not initialized. Call init_log() first.")
        print("Attempting to initialize now...")
        init_log()
        if LOG_FILE is None:
            print("ERROR: Failed to initialize log file")
            return
        
    # Check if log file still exists
    if not os.path.exists(LOG_FILE):
        print(f"WARNING: Log file {LOG_FILE} disappeared, reinitializing...")
        global _initialized
        _initialized = False
        init_log()
        if LOG_FILE is None:
            print("ERROR: Failed to reinitialize log file")
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
            print(f"✓ Logged: T={row.get('temperature', 'N/A')}°C H={row.get('humidity', 'N/A')}% P={row.get('pressure', 'N/A')}hPa")
            
    except Exception as e:
        print(f"ERROR logging data to {LOG_FILE}: {e}")
        import traceback
        traceback.print_exc()
