#!/usr/bin/env python3
"""
Fix Pi display by setting the correct SDL video driver
Run this before starting main.py
"""

import os
import subprocess
import sys

def fix_pi_display():
    """Set environment variables for Pi display"""
    print("🔧 Configuring Pi display...")
    
    # Try different SDL video drivers for Pi
    drivers_to_try = [
        'fbdev',    # Framebuffer device (most common for Pi)
        'fbcon',    # Framebuffer console
        'kmsdrm',   # Kernel Mode Setting Direct Rendering Manager
        'directfb'  # Direct framebuffer
    ]
    
    for driver in drivers_to_try:
        print(f"\n🧪 Testing SDL_VIDEODRIVER={driver}")
        
        # Set environment variable
        env = os.environ.copy()
        env['SDL_VIDEODRIVER'] = driver
        env['SDL_FBDEV'] = '/dev/fb0'  # Point to framebuffer device
        
        # Test pygame with this driver
        test_code = f"""
import pygame
import os
os.environ['SDL_VIDEODRIVER'] = '{driver}'
os.environ['SDL_FBDEV'] = '/dev/fb0'
try:
    pygame.init()
    pygame.display.init()
    screen = pygame.display.set_mode((100, 100))
    actual_driver = pygame.display.get_driver()
    print(f"✅ SUCCESS: {driver} -> {{actual_driver}}")
    pygame.quit()
    exit(0)
except Exception as e:
    print(f"❌ FAILED: {{e}}")
    pygame.quit()
    exit(1)
"""
        
        try:
            result = subprocess.run([
                sys.executable, '-c', test_code
            ], env=env, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(result.stdout.strip())
                print(f"\n🎉 SOLUTION FOUND: Use SDL_VIDEODRIVER={driver}")
                
                # Create startup script
                startup_script = f"""#!/bin/bash
export SDL_VIDEODRIVER={driver}
export SDL_FBDEV=/dev/fb0
python3 main.py "$@"
"""
                
                with open("start_forest_rings.sh", "w") as f:
                    f.write(startup_script)
                
                os.chmod("start_forest_rings.sh", 0o755)
                print("✅ Created start_forest_rings.sh script")
                print("\nTo run Forest Rings GUI:")
                print("  ./start_forest_rings.sh")
                return True
            else:
                print(result.stdout.strip() if result.stdout else result.stderr.strip())
                
        except subprocess.TimeoutExpired:
            print("❌ TIMEOUT")
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n❌ No working SDL video drivers found!")
    print("Try running with sudo or check Pi display configuration.")
    return False

if __name__ == "__main__":
    if fix_pi_display():
        print("\n🚀 Ready to test Forest Rings GUI!")
    else:
        print("\n💡 Alternative: Try running main.py with sudo")
        print("   sudo python3 main.py")
