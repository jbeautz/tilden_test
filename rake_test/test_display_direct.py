#!/usr/bin/env python3
"""
Direct framebuffer test - bypass pygame completely
This tests if we can draw directly to the framebuffer
"""

import os
import struct
import mmap

def test_framebuffer():
    """Test direct framebuffer access"""
    print("🧪 Testing direct framebuffer access...")
    
    fb_path = "/dev/fb0"
    
    try:
        # Get framebuffer info
        with open("/sys/class/graphics/fb0/virtual_size", "r") as f:
            width, height = map(int, f.read().strip().split(","))
        
        print(f"Framebuffer: {width}x{height}")
        
        # Open framebuffer device
        with open(fb_path, "r+b") as fb:
            # Map framebuffer to memory
            fb_size = width * height * 2  # 16 bits per pixel
            fb_map = mmap.mmap(fb.fileno(), fb_size)
            
            print("✅ Framebuffer mapped successfully")
            
            # Fill screen with test pattern (red color in RGB565)
            red_color = struct.pack("H", 0xF800)  # Red in RGB565 format
            
            # Draw a red rectangle in top-left corner
            for y in range(100):
                for x in range(100):
                    pos = (y * width + x) * 2
                    if pos < fb_size - 2:
                        fb_map[pos:pos+2] = red_color
            
            print("✅ Drew red square - check your display!")
            input("Press Enter after checking display...")
            
            # Clear screen (black)
            fb_map[:] = b'\x00' * fb_size
            print("✅ Screen cleared")
            
            fb_map.close()
            
        return True
        
    except Exception as e:
        print(f"❌ Framebuffer test failed: {e}")
        return False

def test_pygame_installation():
    """Test if pygame is properly installed with video support"""
    print("\n🔍 Testing pygame installation...")
    
    try:
        import pygame
        print("✅ pygame imported")
        
        # Check what video drivers are available
        pygame.init()
        
        print("Available video drivers:")
        # Try to get available drivers (this might not work on all pygame versions)
        try:
            import pygame._sdl2.video
            drivers = pygame._sdl2.video.get_drivers()
            for driver in drivers:
                print(f"  - {driver}")
        except:
            print("  (Cannot enumerate drivers)")
        
        # Test each driver manually
        test_drivers = ['fbcon', 'kmsdrm', 'directfb', 'x11', 'dummy']
        working_drivers = []
        
        for driver in test_drivers:
            try:
                os.environ['SDL_VIDEODRIVER'] = driver
                pygame.display.quit()
                pygame.display.init()
                screen = pygame.display.set_mode((100, 100))
                actual_driver = pygame.display.get_driver()
                print(f"  ✅ {driver} -> {actual_driver}")
                working_drivers.append(actual_driver)
                pygame.display.quit()
            except Exception as e:
                print(f"  ❌ {driver}: {e}")
        
        pygame.quit()
        
        if working_drivers:
            print(f"\nWorking drivers: {working_drivers}")
        else:
            print("\n❌ No working video drivers found!")
            
        return len(working_drivers) > 0
        
    except Exception as e:
        print(f"❌ pygame test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Display Troubleshooting")
    print("=" * 40)
    
    # Test 1: Direct framebuffer access
    fb_works = test_framebuffer()
    
    # Test 2: pygame video driver support  
    pygame_works = test_pygame_installation()
    
    print("\n📊 Results:")
    print(f"Direct framebuffer: {'✅ Works' if fb_works else '❌ Failed'}")
    print(f"pygame video drivers: {'✅ Works' if pygame_works else '❌ Failed'}")
    
    if fb_works and not pygame_works:
        print("\n💡 Solution: pygame needs to be reinstalled with proper video support")
        print("Try: pip install --force-reinstall pygame")
    elif not fb_works:
        print("\n💡 Solution: System-level framebuffer issue")
        print("Check display configuration and drivers")
    else:
        print("\n✅ Both should work - check GUI code")
