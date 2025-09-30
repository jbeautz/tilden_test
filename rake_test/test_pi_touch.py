#!/usr/bin/env python3
"""
Pi Touchscreen Test - Verify touch input works on DSI display
Tests both pygame mouse events and touchscreen events
"""

import pygame
import sys
import os

def test_pi_touch():
    """Test touchscreen input on Raspberry Pi DSI display"""
    
    # Set up Pi-optimized pygame
    pygame.init()
    
    # Pi display drivers in priority order
    display_drivers = ['kmsdrm', 'fbcon', 'directfb', 'x11', 'dummy']
    screen = None
    
    print("🍓 Pi Touch Test - Testing display drivers...")
    
    for driver in display_drivers:
        try:
            print(f"Testing {driver}...")
            os.environ['SDL_VIDEODRIVER'] = driver
            
            # Enable mouse/touch for Pi drivers
            if driver in ['kmsdrm', 'fbcon', 'directfb']:
                # Don't disable mouse - we need touch events
                os.environ.pop('SDL_NOMOUSE', None)
            
            pygame.display.quit()
            pygame.display.init()
            screen = pygame.display.set_mode((800, 480))
            
            actual_driver = pygame.display.get_driver()
            print(f"✅ SUCCESS: Using {actual_driver}")
            break
            
        except pygame.error as e:
            print(f"❌ Failed {driver}: {e}")
            continue
    
    if screen is None:
        print("❌ All display drivers failed!")
        return False
    
    pygame.display.set_caption("Pi Touch Test")
    font = pygame.font.Font(None, 48)
    clock = pygame.time.Clock()
    
    # Touch tracking
    touches = 0
    mouse_clicks = 0
    last_touch_pos = (0, 0)
    
    print("🔴 Touch test running - touch the screen!")
    print("Press any key or touch to exit")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                print("Key pressed - exiting")
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_clicks += 1
                last_touch_pos = event.pos
                print(f"TOUCH detected at {event.pos} (click #{mouse_clicks})")
                
            elif event.type == pygame.FINGERDOWN:
                touches += 1
                # Convert finger coordinates (0-1) to screen coordinates
                x = int(event.x * 800)
                y = int(event.y * 480)
                last_touch_pos = (x, y)
                print(f"FINGER touch at ({x}, {y}) (touch #{touches})")
        
        # Draw interface
        screen.fill((20, 50, 100))  # Dark blue background
        
        # Title
        title = font.render("Pi Touch Test", True, (255, 255, 255))
        screen.blit(title, (250, 50))
        
        # Touch counters
        mouse_text = font.render(f"Mouse events: {mouse_clicks}", True, (255, 255, 255))
        finger_text = font.render(f"Finger events: {touches}", True, (255, 255, 255))
        screen.blit(mouse_text, (50, 150))
        screen.blit(finger_text, (50, 200))
        
        # Last touch position
        if mouse_clicks > 0 or touches > 0:
            pos_text = font.render(f"Last touch: {last_touch_pos}", True, (0, 255, 0))
            screen.blit(pos_text, (50, 250))
            
            # Draw a circle at last touch position
            pygame.draw.circle(screen, (255, 0, 0), last_touch_pos, 20)
        
        # Instructions
        inst = font.render("Touch screen to test", True, (200, 200, 200))
        screen.blit(inst, (50, 350))
        
        # Big touch target area
        target_rect = pygame.Rect(300, 300, 200, 100)
        pygame.draw.rect(screen, (0, 150, 0), target_rect)
        target_text = font.render("TOUCH HERE", True, (255, 255, 255))
        screen.blit(target_text, (320, 335))
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    
    print(f"\n📊 Touch Test Results:")
    print(f"Mouse events detected: {mouse_clicks}")
    print(f"Finger events detected: {touches}")
    print(f"Total touch events: {mouse_clicks + touches}")
    
    if mouse_clicks > 0 or touches > 0:
        print("✅ Touch input is working!")
        return True
    else:
        print("❌ No touch input detected")
        return False

if __name__ == "__main__":
    print("🍓 Raspberry Pi Touch Test")
    print("=" * 40)
    
    success = test_pi_touch()
    
    if success:
        print("\n🎉 Touch input working - Forest Rings GUI should work!")
    else:
        print("\n🔧 Touch input issues - may need driver configuration")
