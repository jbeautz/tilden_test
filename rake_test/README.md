# BME680 Sensor Logger

This project logs environmental data from a BME680 sensor to CSV files. Each boot session creates a new CSV file with a unique timestamp in the filename.

## Files

- `sensor.py`: BME680 sensor interface module
- `logger.py`: CSV logging functionality (creates unique files per boot)
- `main.py`: Main application loop
- `requirements.txt`: Python dependencies
- `rake-sensor.service`: Systemd service file for auto-start on boot

## Logging Behavior

- Each time the system boots and the service starts, a new CSV file is created
- Files are named with timestamp: `rake_log_YYYYMMDD_HHMMSS.csv`
- Each file contains its own header row and session marker
- Data is continuously logged until power-off or service stop
- Upon reboot, a new file is automatically created for the new session

## Setup

1. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

2. Enable I2C on Raspberry Pi:
   ```bash
   sudo raspi-config
   # Navigate to Interfacing Options > I2C > Enable
   ```

3. Test the application:
   ```bash
   python3 main.py
   ```

## Running on Boot (Optional)

### Method 1: Systemd Service

1. Copy the service file:
   ```bash
   sudo cp rake-sensor.service /etc/systemd/system/
   ```

2. Update the paths in the service file if needed:
   ```bash
   sudo nano /etc/systemd/system/rake-sensor.service
   # Change /home/pi/rake_test to your actual project path
   ```

3. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable rake-sensor.service
   sudo systemctl start rake-sensor.service
   ```

4. Check service status:
   ```bash
   sudo systemctl status rake-sensor.service
   ```

5. View logs:
   ```bash
   sudo journalctl -u rake-sensor.service -f
   ```

4. Check service status:
   ```bash
   sudo systemctl status rake_logger.service
   ```

### Method 2: Crontab

1. Edit crontab:
   ```bash
   crontab -e
   ```

2. Add this line:
   ```
   @reboot cd /home/pi/rake_test && python3 main.py >> /tmp/rake_logger.log 2>&1
   ```

## Data Format

The CSV file `rake_log.csv` contains the following columns:
- `timestamp`: ISO format timestamp
- `temperature`: Temperature in Celsius
- `humidity`: Relative humidity percentage
- `pressure`: Atmospheric pressure in hPa
- `gas`: Gas resistance in Ohms (when heat stable)

## Hardware Setup

Connect the BME680 sensor to your Raspberry Pi:
- VCC → 3.3V
- GND → Ground
- SDA → GPIO 2 (SDA)
- SCL → GPIO 3 (SCL)
