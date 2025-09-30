#!/usr/bin/env python3
"""
Comprehensive touch display diagnostic and fix
Tests touch input, calibration, and provides solutions
"""

import os
import subprocess
import sys
import glob
import time

def check_touch_hardware():
    """Check if touch hardware is detected"""
    print("🔍 Checking touch hardware...")
    
    # Check input devices
    input_devices = []
    try:
        with open("/proc/bus/input/devices", "r") as f:
            content = f.read()
            
        # Look for touch-related devices
        lines = content.split('\n')
        current_device = {}
        
        for line in lines:
            if line.startswith('I:'):
                if current_device:
                    input_devices.append(current_device)
                current_device = {'info': line}
            elif line.startswith('N:') and 'Name=' in line:
                current_device['name'] = line.split('Name="')[1].split('"')[0]
            elif line.startswith('H:') and 'Handlers=' in line:
                current_device['handlers'] = line.split('Handlers=')[1].strip()
        
        if current_device:
            input_devices.append(current_device)
        
        print(f"Found {len(input_devices)} input devices:")
        touch_devices = []
        
        for device in input_devices:
            name = device.get('name', 'Unknown')
            handlers = device.get('handlers', '')
            
            # Look for touch-related keywords
            if any(keyword in name.lower() for keyword in ['touch', 'ft5406', 'goodix', 'edt', 'ili', 'rpi']):
                print(f"  ✅ TOUCH: {name} -> {handlers}")
                touch_devices.append(device)
            elif 'mouse' in handlers or 'event' in handlers:
                print(f"  📱 INPUT: {name} -> {handlers}")
            else:
                print(f"  ℹ️  OTHER: {name} -> {handlers}")
        
        return len(touch_devices) > 0, touch_devices
        
    except Exception as e:
        print(f"❌ Error reading input devices: {e}")
        return False, []

def check_touch_calibration():
    """Check touch calibration settings"""
    print("\n🎯 Checking touch calibration...")
    
    # Check common calibration files
    calib_files = [
        "/etc/X11/xorg.conf.d/40-libinput.conf",
        "/etc/X11/xorg.conf.d/99-calibration.conf", 
        "/usr/share/X11/xorg.conf.d/40-libinput.conf",
        "/boot/config.txt"
    ]
    
    found_config = False
    for calib_file in calib_files:
        if os.path.exists(calib_file):
            print(f"  ✅ Found config: {calib_file}")
            found_config = True
            
            # Show relevant lines
            try:
                with open(calib_file, 'r') as f:
                    lines = f.readlines()
                    
                for i, line in enumerate(lines):
                    if any(keyword in line.lower() for keyword in ['touch', 'transform', 'calibration', 'input']):
                        print(f"    Line {i+1}: {line.strip()}")
            except:
                pass
        else:
            print(f"  ❌ Missing: {calib_file}")
    
    return found_config

def test_raw_touch_events():
    """Test raw touch events from input devices"""
    print("\n🖐️ Testing raw touch events...")
    
    # Find event devices
    event_devices = glob.glob("/dev/input/event*")
    
    if not event_devices:
        print("❌ No event devices found!")
        return False
    
    print(f"Found {len(event_devices)} event devices")
    
    # Test reading from event devices
    print("Testing each device for 5 seconds...")
    print("👆 TOUCH YOUR SCREEN NOW!")
    
    working_devices = []
    
    for device in event_devices:
        print(f"\n📱 Testing {device}...")
        
        try:
            # Test if we can read from this device
            cmd = f"timeout 2 hexdump -C {device}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 124:  # timeout occurred
                print(f"  ⏰ Timeout (no events)")
            elif result.returncode == 0 and result.stdout:
                print(f"  ✅ Events detected!")
                working_devices.append(device)
            else:
                print(f"  ❌ No access or no events")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    return len(working_devices) > 0

def create_touch_fixes():
    """Create various touch fix scripts"""
    print("\n🔧 Creating touch fix scripts...")
    
    # Fix 1: Basic touch calibration
    touch_calib_script = """#!/bin/bash
# Basic touch screen fixes for Pi

echo "🔧 Applying touch screen fixes..."

# Enable touch screen in config.txt
if ! grep -q "dtoverlay=rpi-ft5406" /boot/config.txt; then
    echo "dtoverlay=rpi-ft5406" | sudo tee -a /boot/config.txt
    echo "✅ Added touch overlay to config.txt"
fi

# Set proper permissions for input devices
sudo chmod 666 /dev/input/event*
sudo chmod 666 /dev/input/mouse*
echo "✅ Set input device permissions"

# Create X11 touch configuration
sudo mkdir -p /etc/X11/xorg.conf.d
sudo tee /etc/X11/xorg.conf.d/99-calibration.conf > /dev/null << 'EOF'
Section "InputClass"
    Identifier "calibration"
    MatchProduct "FT5406 memory based driver"
    Option "Calibration" "0 800 0 480"
    Option "SwapAxes" "1"
EOF

echo "✅ Created X11 touch configuration"
echo "🔄 Reboot required for changes to take effect"
"""
    
    with open("fix_touch_basic.sh", "w") as f:
        f.write(touch_calib_script)
    os.chmod("fix_touch_basic.sh", 0o755)
    
    # Fix 2: Advanced pygame touch test
    pygame_touch_test = """#!/usr/bin/env python3
import pygame
import os
import sys

# Force framebuffer driver
os.environ['SDL_VIDEODRIVER'] = 'fbdev'  
os.environ['SDL_FBDEV'] = '/dev/fb0'
os.environ['SDL_MOUSEDRV'] = 'TSLIB'
os.environ['SDL_MOUSEDEV'] = '/dev/input/touchscreen'

print("🎮 Testing pygame touch with fbdev driver...")

try:
    pygame.init()
    screen = pygame.display.set_mode((800, 480))
    pygame.display.set_caption("Touch Test")
    
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    print("✅ Display initialized")
    print("👆 Touch the screen to test...")
    
    running = True
    touch_count = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                touch_count += 1
                pos = event.pos
                print(f"✅ TOUCH {touch_count}: {pos}")
            elif event.type == pygame.FINGERDOWN:
                touch_count += 1
                pos = (int(event.x * 800), int(event.y * 480))
                print(f"✅ FINGER {touch_count}: {pos}")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Show instructions
        text1 = font.render("Touch Test - Touch anywhere", True, (255, 255, 255))
        text2 = font.render(f"Touches detected: {touch_count}", True, (0, 255, 0))
        text3 = font.render("Press ESC to exit", True, (255, 255, 255))
        
        screen.blit(text1, (10, 10))
        screen.blit(text2, (10, 50))  
        screen.blit(text3, (10, 400))
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    print(f"🎯 Test complete - {touch_count} touches detected")
    
except Exception as e:
    print(f"❌ Error: {e}")
    pygame.quit()
"""
    
    with open("test_pygame_touch.py", "w") as f:
        f.write(pygame_touch_test)
    os.chmod("test_pygame_touch.py", 0o755)
    
    print("✅ Created fix_touch_basic.sh")
    print("✅ Created test_pygame_touch.py")

def main():
    """Main diagnostic function"""
    print("🔧 Touch Display Diagnostic")
    print("=" * 40)
    
    # Check if running as root (needed for some tests)
    if os.geteuid() != 0:
        print("⚠️  Running as user - some tests may need sudo")
    
    # Test 1: Hardware detection
    has_touch, touch_devices = check_touch_hardware()
    
    # Test 2: Calibration settings
    has_config = check_touch_calibration()
    
    # Test 3: Raw events (requires sudo for some devices)
    has_events = test_raw_touch_events()
    
    # Create fix scripts
    create_touch_fixes()
    
    print("\n📊 DIAGNOSIS RESULTS:")
    print("=" * 40)
    print(f"Touch hardware detected: {'✅ YES' if has_touch else '❌ NO'}")
    print(f"Configuration found: {'✅ YES' if has_config else '❌ NO'}")
    print(f"Raw events working: {'✅ YES' if has_events else '❌ NO'}")
    
    print("\n🔧 RECOMMENDED FIXES:")
    print("=" * 40)
    
    if not has_touch:
        print("1. ❌ CRITICAL: Touch hardware not detected")
        print("   - Check display connection")
        print("   - Run: sudo ./fix_touch_basic.sh")
        print("   - Reboot Pi")
    
    if not has_config:
        print("2. ⚠️  Touch configuration missing")
        print("   - Run: sudo ./fix_touch_basic.sh") 
        print("   - Reboot Pi")
    
    if not has_events:
        print("3. ⚠️  Touch events not working")
        print("   - Try: sudo python3 test_pygame_touch.py")
        print("   - Check permissions: sudo chmod 666 /dev/input/event*")
    
    print("\n🚀 TESTING STEPS:")
    print("1. sudo ./fix_touch_basic.sh")
    print("2. sudo reboot")
    print("3. python3 test_pygame_touch.py")
    print("4. If working, try: ./start_forest_rings.sh")

if __name__ == "__main__":
    main()
