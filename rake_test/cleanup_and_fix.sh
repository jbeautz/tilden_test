#!/bin/bash

# Comprehensive Cleanup and BME680 Fix Script
# This script will:
# 1. Clean up old empty log files
# 2. Update the service to use virtual environment (fixes BME680)
# 3. Archive old diagnostic/test files

set -e  # Exit on error

echo "========================================="
echo "Soil Monitor - Cleanup and BME680 Fix"
echo "========================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ==========================================
# STEP 1: Clean up old/empty log files
# ==========================================
echo "Step 1: Cleaning up old log files..."
echo ""

# Count files to be cleaned
OLD_COUNT=$(find . -name "rake_log_*.csv" -size -1k | wc -l)
echo "Found $OLD_COUNT old/empty log files (< 1KB)"

if [ $OLD_COUNT -gt 0 ]; then
    echo "Moving them to old_logs/ directory..."
    mkdir -p old_logs
    find . -name "rake_log_*.csv" -size -1k -exec mv {} old_logs/ \;
    echo "✓ Moved $OLD_COUNT files to old_logs/"
else
    echo "No old files to clean up"
fi

echo ""
echo "Current log files:"
ls -lh rake_log_*.csv 2>/dev/null | head -5 || echo "No log files found"
echo ""

# ==========================================
# STEP 2: Fix BME680 - Update Service
# ==========================================
echo "Step 2: Fixing BME680 sensor (updating service to use venv)..."
echo ""

# Update start_forest_rings.sh to activate virtual environment
echo "Updating start_forest_rings.sh..."
cat > start_forest_rings.sh << 'EOF'
#!/bin/bash

# Start script for Forest Rings GUI
# This script ensures the graphics subsystem is ready and activates the virtual environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Waiting for graphics devices to be ready..."

# Wait for framebuffer device (max 60 seconds)
COUNTER=0
while [ ! -c /dev/fb0 ] || [ ! -r /dev/fb0 ] || [ ! -w /dev/fb0 ]; do
    echo "Waiting for /dev/fb0... ($COUNTER seconds)"
    sleep 1
    COUNTER=$((COUNTER + 1))
    if [ $COUNTER -gt 60 ]; then
        echo "WARNING: /dev/fb0 not ready after 60 seconds, continuing anyway..."
        break
    fi
done

# Wait for DRM device (max 60 seconds)
COUNTER=0
while [ ! -c /dev/dri/card0 ] || [ ! -r /dev/dri/card0 ] || [ ! -w /dev/dri/card0 ]; do
    echo "Waiting for /dev/dri/card0... ($COUNTER seconds)"
    sleep 1
    COUNTER=$((COUNTER + 1))
    if [ $COUNTER -gt 60 ]; then
        echo "WARNING: /dev/dri/card0 not ready after 60 seconds, continuing anyway..."
        break
    fi
done

echo "Graphics devices ready, waiting 5 more seconds for system stabilization..."
sleep 5

# Activate virtual environment if it exists
if [ -d "$SCRIPT_DIR/myproject-venv" ]; then
    echo "Activating virtual environment..."
    source "$SCRIPT_DIR/myproject-venv/bin/activate"
    echo "Using Python: $(which python3)"
    echo "Python version: $(python3 --version)"
else
    echo "WARNING: Virtual environment not found at $SCRIPT_DIR/myproject-venv"
    echo "BME680 sensor may not work without proper libraries"
fi

# Set SDL environment variables
export SDL_VIDEODRIVER=kmsdrm
export SDL_FBDEV=/dev/fb0
export SDL_NOMOUSE=1

echo "Starting Soil Monitor GUI..."
exec python3 main.py
EOF

chmod +x start_forest_rings.sh
echo "✓ Updated start_forest_rings.sh"
echo ""

# ==========================================
# STEP 3: Archive diagnostic/test files
# ==========================================
echo "Step 3: Archiving diagnostic and test files..."
echo ""

mkdir -p archive/diagnostic_scripts
mkdir -p archive/test_scripts
mkdir -p archive/old_gui_themes
mkdir -p archive/fix_scripts
mkdir -p archive/old_services

# Move diagnostic scripts
echo "Archiving diagnostic scripts..."
mv diagnose_*.py diagnose_*.sh compare_environments.sh archive/diagnostic_scripts/ 2>/dev/null || true

# Move test scripts
echo "Archiving test scripts..."
mv test_*.py test_*.sh archive/test_scripts/ 2>/dev/null || true

# Move old GUI themes
echo "Archiving old GUI theme experiments..."
mv gui_cyberpunk_theme.py gui_dark_theme.py gui_light_theme.py gui_nature_theme.py \
   gui_direct_framebuffer.py gui_forest_rings_final.py archive/old_gui_themes/ 2>/dev/null || true

# Move fix scripts
echo "Archiving fix scripts..."
mv apply_fixes.sh fix_*.sh fix_*.py enable_autologin.sh final_autologin_fix.sh \
   configure_display.sh archive/fix_scripts/ 2>/dev/null || true

# Move old service files
echo "Archiving old service files..."
mv rake-sensor-simple.service rake_logger.service archive/old_services/ 2>/dev/null || true

# Move old cleanup scripts
echo "Archiving old cleanup scripts..."
mv cleanup_gui.sh cleanup_old_logs.sh archive/fix_scripts/ 2>/dev/null || true

# Move old setup scripts
echo "Archiving old setup scripts..."
mv setup_boot_gui.sh setup_gps.sh deploy_to_pi.sh archive/fix_scripts/ 2>/dev/null || true

# Move old start scripts
echo "Archiving old start scripts..."
mv start_gui_with_x11.sh start_local_gui.sh archive/fix_scripts/ 2>/dev/null || true

# Move old main files
echo "Archiving old main files..."
mv main_logging_only.py display.py fix_pi_display.py archive/old_gui_themes/ 2>/dev/null || true

echo "✓ Archived diagnostic and test files"
echo ""

# ==========================================
# STEP 4: Apply the fix
# ==========================================
echo "Step 4: Applying the fix to systemd service..."
echo ""

# Stop the service
echo "Stopping service..."
sudo systemctl stop rake-sensor.service

# Copy the fixed service file
echo "Updating service configuration..."
sudo cp rake-sensor-fixed.service /etc/systemd/system/rake-sensor.service

# Reload systemd
echo "Reloading systemd..."
sudo systemctl daemon-reload

# Start the service
echo "Starting service..."
sudo systemctl start rake-sensor.service

echo ""
echo "✓ Service restarted with virtual environment support"
echo ""

# ==========================================
# FINAL STATUS
# ==========================================
echo "========================================="
echo "Cleanup and Fix Complete!"
echo "========================================="
echo ""
echo "Summary:"
echo "  • Cleaned up $OLD_COUNT old log files"
echo "  • Updated service to use virtual environment"
echo "  • Archived diagnostic/test files to archive/"
echo ""
echo "Checking service status..."
sleep 3
sudo systemctl status rake-sensor.service --no-pager -l | head -20

echo ""
echo "========================================="
echo "Next Steps:"
echo "========================================="
echo "1. Watch the logs to verify BME680 is working:"
echo "   sudo journalctl -u rake-sensor.service -f"
echo ""
echo "2. You should now see real sensor readings instead of 'BME680 library not available'"
echo ""
echo "3. Your clean working directory now contains only:"
echo "   • Core files: main.py, sensor.py, gps.py, logger.py, touch_handler.py"
echo "   • GUI: display_forest_rings.py"
echo "   • Service: rake-sensor-fixed.service, rake-sensor.service, start_forest_rings.sh"
echo "   • Config: requirements.txt, setup_pi.sh"
echo "   • Docs: README.md, FINAL_CONFIG.md, etc."
echo ""
echo "4. All old test/diagnostic files are in archive/ if you need them"
echo "========================================="
