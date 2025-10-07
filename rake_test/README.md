# Soil Monitor - Automated Environmental Logger

Raspberry Pi-based continuous environmental monitoring system with touchscreen display.

## 🎯 Features

- **Continuous Logging**: Automatic sensor data logging at 1 Hz from boot to power-off
- **Visual Display**: Tree rings visualization showing environmental changes over time
- **Sensors**: BME680 (temperature, humidity, pressure) + GPS module
- **Auto-Start**: Boots automatically, no user interaction required
- **Touchscreen Support**: 5" 800x480 DSI display with touch capability

## 📋 Quick Reference

### System Status
```bash
sudo systemctl status rake-sensor.service
```

### View Live Data
```bash
sudo journalctl -u rake-sensor.service -f
```

### Check Log Files
```bash
ls -lht rake_log_*.csv | head -5
```

## 🔧 Apply Fixes

Clean up old log files and enable BME680 sensor:
```bash
cd ~/tilden_test/rake_test
./apply_fixes.sh
```

## 📚 Documentation

- **[FINAL_CONFIG.md](FINAL_CONFIG.md)** - Complete configuration guide and troubleshooting
- **[SYSTEMD_FIX.md](SYSTEMD_FIX.md)** - Original systemd configuration fixes

## ✅ System Working

- ✅ Single log file per boot
- ✅ Continuous logging at 1 Hz  
- ✅ Auto-start on boot
- ✅ Stable operation (no restart loops)
- ✅ Graphics display with kmsdrm driver

## Logging Behavior

- Each boot creates ONE new CSV file with timestamp: `rake_log_YYYYMMDD_HHMMSS.csv`
- Data is continuously logged until power-off or service stop
- Log files contain temperature, humidity, pressure, and GPS data

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
