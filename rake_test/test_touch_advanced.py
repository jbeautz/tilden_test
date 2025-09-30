#!/usr/bin/env python3
"""
Advanced pygame touch test - tries multiple display drivers
"""

import pygame
import os
import sys

def test_touch_with_driver(driver_name):
    """Test touch with a specific display driver"""
    print(f"\n🧪 Testing touch with {driver_name} driver...")
    
    # Set environment variables
    old_driver = os.environ.get('SDL_VIDEODRIVER', '')
    old_fbdev = os.environ.get('SDL_FBDEV', '')
    
    try:
        os.environ['SDL_VIDEODRIVER'] = driver_name
        os.environ['SDL_FBDEV'] = '/dev/fb0'
        
        pygame.quit()  # Clean slate
        pygame.init()
        
        screen = pygame.display.set_mode((800, 480))
        pygame.display.set_caption(f"Touch Test - {driver_name}")
        
        actual_driver = pygame.display.get_driver()
        print(f"✅ Display initialized: {driver_name} -> {actual_driver}")
        
        # If we get dummy driver, it's not really working
        if actual_driver == 'dummy':
            print("⚠️  Warning: Using dummy driver (no actual display)")
            if driver_name != 'dummy':
                raise Exception("Fell back to dummy driver")
        
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 36)
        
        print("👆 Touch the screen to test input...")
        print("Press ESC or Ctrl+C to exit")
        
        running = True
        touch_count = 0
        last_pos = None
        
        for test_round in range(300):  # Run for 10 seconds max
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    touch_count += 1
                    pos = event.pos
                    last_pos = pos
                    print(f"✅ MOUSE TOUCH {touch_count}: {pos}")
                elif event.type == pygame.FINGERDOWN:
                    touch_count += 1
                    pos = (int(event.x * 800), int(event.y * 480))
                    last_pos = pos
                    print(f"✅ FINGER TOUCH {touch_count}: {pos}")
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            if not running:
                break
            
            # Clear screen
            screen.fill((0, 0, 0))
            
            # Show instructions
            text1 = font.render(f"Touch Test - {actual_driver}", True, (255, 255, 255))
            text2 = font.render(f"Touches: {touch_count}", True, (0, 255, 0))
            text3 = font.render("Press ESC to exit", True, (200, 200, 200))
            
            screen.blit(text1, (10, 10))
            screen.blit(text2, (10, 50))
            screen.blit(text3, (10, 400))
            
            # Show last touch position
            if last_pos:
                text4 = font.render(f"Last: {last_pos}", True, (255, 255, 0))
                screen.blit(text4, (10, 90))
                
                # Draw a circle at touch position
                pygame.draw.circle(screen, (255, 0, 0), last_pos, 20, 3)
            
            pygame.display.flip()
            clock.tick(30)
        
        pygame.quit()
        
        # Restore environment
        if old_driver:
            os.environ['SDL_VIDEODRIVER'] = old_driver
        else:
            os.environ.pop('SDL_VIDEODRIVER', None)
            
        if old_fbdev:
            os.environ['SDL_FBDEV'] = old_fbdev
        else:
            os.environ.pop('SDL_FBDEV', None)
        
        print(f"🎯 {driver_name} test complete - {touch_count} touches detected")
        return touch_count > 0, actual_driver
        
    except KeyboardInterrupt:
        print(f"\n⏹️  {driver_name} test interrupted by user")
        pygame.quit()
        return False, None
    except Exception as e:
        print(f"❌ {driver_name} failed: {e}")
        pygame.quit()
        return False, None

def main():
    """Test touch with different display drivers"""
    print("🎮 Advanced Touch Test")
    print("=" * 40)
    
    # Try different drivers in order of preference
    drivers_to_try = [
        'fbdev',     # Framebuffer device
        'fbcon',     # Console framebuffer  
        'kmsdrm',    # KMS Direct Rendering
        'directfb',  # Direct framebuffer
        'dummy'      # Last resort (no actual display)
    ]
    
    working_drivers = []
    
    for driver in drivers_to_try:
        success, actual_driver = test_touch_with_driver(driver)
        
        if success:
            working_drivers.append((driver, actual_driver))
            print(f"✅ {driver} -> {actual_driver}: TOUCH WORKING!")
            
            # Create startup script for this driver
            startup_script = f"""#!/bin/bash
export SDL_VIDEODRIVER={driver}
export SDL_FBDEV=/dev/fb0
python3 main.py "$@"
"""
            script_name = f"start_forest_rings_{driver}.sh"
            with open(script_name, "w") as f:
                f.write(startup_script)
            os.chmod(script_name, 0o755)
            print(f"✅ Created {script_name}")
            
        else:
            print(f"❌ {driver}: No touch response")
    
    print("\n📊 RESULTS:")
    print("=" * 40)
    
    if working_drivers:
        print("✅ Working drivers with touch:")
        for req_driver, actual_driver in working_drivers:
            print(f"  - {req_driver} -> {actual_driver}")
        
        best_driver = working_drivers[0][0]
        print(f"\n🚀 RECOMMENDED: Use {best_driver}")
        print(f"   ./start_forest_rings_{best_driver}.sh")
        
    else:
        print("❌ NO WORKING TOUCH DRIVERS FOUND!")
        print("\n💡 Try these solutions:")
        print("1. sudo python3 test_touch_advanced.py")
        print("2. Check /boot/config.txt for dtoverlay=rpi-ft5406")
        print("3. Verify touch hardware connection")
        print("4. Try: sudo chmod 666 /dev/input/event*")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        pygame.quit()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        pygame.quit()
