#!/usr/bin/env python3
"""
Direct framebuffer writing without pygame - ultimate test
"""
import os
import struct
import mmap
import time

def test_direct_framebuffer():
    """Write directly to framebuffer device"""
    fb_device = '/dev/fb0'
    
    print("🔧 Testing direct framebuffer access (no pygame)...")
    
    try:
        # Open framebuffer device
        with open(fb_device, 'r+b') as fb:
            # Get framebuffer info (assume 800x480x32bpp for now)
            width, height = 800, 480
            bytes_per_pixel = 4  # 32-bit RGBA
            screen_size = width * height * bytes_per_pixel
            
            print(f"📱 Framebuffer: {width}x{height}, {bytes_per_pixel} bytes/pixel")
            print(f"📏 Screen size: {screen_size} bytes")
            
            # Memory map the framebuffer
            fb_map = mmap.mmap(fb.fileno(), screen_size, mmap.MAP_SHARED, mmap.PROT_WRITE | mmap.PROT_READ)
            
            print("✅ Framebuffer mapped successfully")
            
            # Fill screen with blue
            blue_pixel = struct.pack('BBBB', 255, 0, 0, 0)  # BGRA format (blue)
            for i in range(width * height):
                fb_map[i*4:(i+1)*4] = blue_pixel
            
            print("🟦 Screen should be BLUE now!")
            time.sleep(3)
            
            # Draw a white rectangle in center
            rect_x, rect_y = 250, 140
            rect_w, rect_h = 300, 200
            white_pixel = struct.pack('BBBB', 255, 255, 255, 0)  # BGRA format (white)
            
            for y in range(rect_h):
                for x in range(rect_w):
                    if rect_y + y < height and rect_x + x < width:
                        pixel_offset = ((rect_y + y) * width + (rect_x + x)) * 4
                        fb_map[pixel_offset:pixel_offset+4] = white_pixel
            
            print("⬜ White rectangle should be visible!")
            time.sleep(3)
            
            # Clear screen (black)
            black_pixel = struct.pack('BBBB', 0, 0, 0, 0)  # BGRA format (black)
            for i in range(width * height):
                fb_map[i*4:(i+1)*4] = black_pixel
            
            print("⬛ Screen cleared to black")
            
            fb_map.close()
            
        print("✅ Direct framebuffer test completed successfully!")
        return True
        
    except PermissionError:
        print("❌ Permission denied - try running with sudo")
        print("Run: sudo python test_framebuffer_force.py")
        return False
    except FileNotFoundError:
        print("❌ Framebuffer device /dev/fb0 not found")
        print("Check if display is properly configured")
        return False
    except Exception as e:
        print(f"❌ Direct framebuffer test failed: {e}")
        return False

def test_pygame_with_alternative_drivers():
    """Try pygame with alternative approaches"""
    print("\n🎮 Testing pygame with alternative drivers...")
    
    # Different pygame approaches to try
    approaches = [
        ("Force fbcon", {"SDL_VIDEODRIVER": "fbcon", "SDL_FBDEV": "/dev/fb0"}),
        ("Force kmsdrm", {"SDL_VIDEODRIVER": "kmsdrm"}),
        ("X11 with DISPLAY", {"SDL_VIDEODRIVER": "x11", "DISPLAY": ":0"}),
        ("DirectFB", {"SDL_VIDEODRIVER": "directfb"}),
        ("No driver specified", {}),
    ]
    
    for name, env_vars in approaches:
        print(f"\n🔄 Trying: {name}")
        
        # Set environment
        for key, value in env_vars.items():
            os.environ[key] = value
            print(f"   {key} = {value}")
        
        try:
            import pygame
            pygame.quit()  # Clean slate
            pygame.init()
            
            screen = pygame.display.set_mode((800, 480))
            driver = pygame.display.get_driver()
            
            if driver not in ['dummy', 'offscreen']:
                print(f"✅ {name} works! Driver: {driver}")
                
                # Quick test
                screen.fill((0, 255, 0))  # Green
                pygame.display.flip()
                print("   Green screen should be visible!")
                
                time.sleep(2)
                
                screen.fill((0, 0, 0))  # Black
                pygame.display.flip()
                
                pygame.quit()
                return True
            else:
                print(f"❌ {name} gave invisible driver: {driver}")
                
        except Exception as e:
            print(f"❌ {name} failed: {e}")
    
    print("❌ All pygame approaches failed")
    return False

if __name__ == "__main__":
    print("🚀 Ultimate Display Test - Direct Framebuffer + pygame")
    print("=" * 60)
    
    # Test 1: Direct framebuffer (should work)
    direct_works = test_direct_framebuffer()
    
    # Test 2: pygame alternatives
    pygame_works = test_pygame_with_alternative_drivers()
    
    print("\n" + "=" * 60)
    print("📋 RESULTS:")
    print(f"Direct framebuffer: {'✅ Works' if direct_works else '❌ Failed'}")
    print(f"pygame: {'✅ Works' if pygame_works else '❌ Failed'}")
    
    if direct_works and not pygame_works:
        print("\n💡 SOLUTION: Use direct framebuffer rendering instead of pygame")
        print("   The display hardware works, but pygame has driver issues.")
    elif direct_works and pygame_works:
        print("\n🎉 SUCCESS: Both methods work!")
    else:
        print("\n🔧 Need to debug display configuration further")
