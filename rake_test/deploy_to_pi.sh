#!/bin/bash

# Script to copy rake_test files to Raspberry Pi
# Usage: ./deploy_to_pi.sh [pi_ip_address]

PI_IP="192.168.4.49"
PI_USER="maggi"
REMOTE_DIR="/home/$PI_USER/tilden_test/rake_test"

echo "Deploying rake_test to $PI_USER@$PI_IP:$REMOTE_DIR"

# Create remote directory
ssh $PI_USER@$PI_IP "mkdir -p $REMOTE_DIR"

# Copy Python files
echo "Copying Python files..."
scp *.py $PI_USER@$PI_IP:$REMOTE_DIR/

# Copy other files
echo "Copying configuration files..."
scp requirements.txt $PI_USER@$PI_IP:$REMOTE_DIR/
scp README.md $PI_USER@$PI_IP:$REMOTE_DIR/
scp rake-sensor.service $PI_USER@$PI_IP:$REMOTE_DIR/

echo "Files copied successfully!"
echo ""
echo "Next steps on the Pi:"
echo "1. cd $REMOTE_DIR"
echo "2. pip install -r requirements.txt"
echo "3. python diagnose_i2c.py  # Run diagnostics first"
echo "4. python main.py  # Test the sensor logging"
