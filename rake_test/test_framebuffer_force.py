#!/usr/bin/env python3
"""
Force pygame to use framebuffer - simple test
"""
import os
import pygame
import sys

# Force framebuffer settings
os.environ['SDL_VIDEODRIVER'] = 'fbcon'
os.environ['SDL_FBDEV'] = '/dev/fb0'
os.environ['SDL_NOMOUSE'] = '1'

print("🔧 Testing forced framebuffer pygame display...")
print(f"Environment settings:")
print(f"  SDL_VIDEODRIVER = {os.environ.get('SDL_VIDEODRIVER')}")
print(f"  SDL_FBDEV = {os.environ.get('SDL_FBDEV')}")
print(f"  SDL_NOMOUSE = {os.environ.get('SDL_NOMOUSE')}")

try:
    pygame.init()
    screen = pygame.display.set_mode((800, 480))
    driver = pygame.display.get_driver()
    
    print(f"✅ Display created successfully!")
    print(f"  Driver: {driver}")
    print(f"  Size: {screen.get_size()}")
    print(f"  Surface: {screen}")
    
    # Fill with green and draw test pattern
    screen.fill((0, 255, 0))  # Green background
    
    # Draw white circle in center
    pygame.draw.circle(screen, (255, 255, 255), (400, 240), 100)
    
    # Draw text
    font = pygame.font.Font(None, 48)
    text = font.render("FRAMEBUFFER TEST", True, (0, 0, 0))
    text_rect = text.get_rect(center=(400, 240))
    screen.blit(text, text_rect)
    
    # Update display
    pygame.display.flip()
    
    print("✅ Green screen with white circle should be visible!")
    print("Press Enter to clear and exit...")
    input()
    
    # Clear screen
    screen.fill((0, 0, 0))
    pygame.display.flip()
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1)
finally:
    pygame.quit()

print("✅ Test completed successfully!")
