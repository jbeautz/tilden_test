#!/usr/bin/env python3
"""
Test GUI themes on macOS - optimized for Mac display drivers
"""

import pygame
import sys
import os

def test_display_drivers():
    """Test what display drivers work on this system"""
    pygame.init()
    
    # Mac-friendly drivers in priority order
    mac_drivers = ['cocoa', 'x11', 'windib', 'directx']
    
    print("Testing display drivers...")
    for driver in mac_drivers:
        try:
            os.environ['SDL_VIDEODRIVER'] = driver
            pygame.display.quit()
            pygame.display.init()
            screen = pygame.display.set_mode((800, 480))
            print(f"✓ {driver} driver works!")
            return driver, screen
        except pygame.error as e:
            print(f"✗ {driver} driver failed: {e}")
            continue
    
    # Fallback - let pygame choose
    print("Trying pygame default...")
    try:
        os.environ.pop('SDL_VIDEODRIVER', None)
        pygame.display.quit()
        pygame.display.init()
        screen = pygame.display.set_mode((800, 480))
        print("✓ Default pygame driver works!")
        return "default", screen
    except pygame.error as e:
        print(f"✗ All drivers failed: {e}")
        return None, None

def create_mac_optimized_theme():
    """Create a simple theme optimized for Mac testing"""
    driver, screen = test_display_drivers()
    
    if not screen:
        print("No working display driver found!")
        return
    
    pygame.display.set_caption(f"Rake Test GUI - {driver} driver")
    
    # Colors
    DARK_BLUE = (20, 30, 50)
    LIGHT_BLUE = (70, 130, 180)
    WHITE = (255, 255, 255)
    GREEN = (50, 205, 50)
    
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    print(f"GUI opened with {driver} driver - you should see a window!")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Fill background
        screen.fill(DARK_BLUE)
        
        # Title
        title = font.render("Rake Environmental Monitor", True, WHITE)
        screen.blit(title, (50, 50))
        
        # Status indicator
        pygame.draw.circle(screen, GREEN, (750, 70), 20)
        status_text = font.render("ACTIVE", True, WHITE)
        screen.blit(status_text, (650, 55))
        
        # Sample data display
        temp_text = font.render("Temperature: 22.5°C", True, WHITE)
        screen.blit(temp_text, (50, 150))
        
        humidity_text = font.render("Humidity: 65.2%", True, WHITE)
        screen.blit(humidity_text, (50, 200))
        
        pressure_text = font.render("Pressure: 1013.2 hPa", True, WHITE)
        screen.blit(pressure_text, (50, 250))
        
        # Instructions
        instruction = font.render("Press ESC to close", True, LIGHT_BLUE)
        screen.blit(instruction, (50, 400))
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    print("GUI closed successfully!")

if __name__ == "__main__":
    create_mac_optimized_theme()
