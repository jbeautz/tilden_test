#!/usr/bin/env python3
"""
Simple pygame test with SDL renderer selection
"""
import pygame
import sys
import os

def test_pygame_display():
    """Test pygame display with different renderers"""
    print("🔧 Testing pygame display capabilities...")
    
    # Initialize pygame
    pygame.init()
    
    # Set SDL video driver to use framebuffer
    os.environ['SDL_VIDEODRIVER'] = 'kmsdrm'
    
    try:
        # Create display
        screen = pygame.display.set_mode((800, 480))
        pygame.display.set_caption("Pygame Test")
        
        print("✅ Display created successfully!")
        print(f"Display size: {screen.get_size()}")
        print(f"Display flags: {pygame.display.get_surface().get_flags()}")
        
        # Fill screen with blue
        screen.fill((0, 0, 255))  # Blue
        
        # Draw a white rectangle
        pygame.draw.rect(screen, (255, 255, 255), (100, 100, 200, 150))
        
        # Draw some text
        font = pygame.font.Font(None, 36)
        text = font.render("Pygame Test!", True, (255, 255, 255))
        screen.blit(text, (250, 200))
        
        # Update display
        pygame.display.flip()
        
        print("✅ Screen updated - check your display!")
        print("Press Ctrl+C to exit...")
        
        # Keep running until interrupted
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            clock.tick(30)
        
    except Exception as e:
        print(f"❌ Display test failed: {e}")
        
        # Try different video drivers
        drivers_to_try = ['fbcon', 'directfb', 'dummy']
        for driver in drivers_to_try:
            print(f"\n🔄 Trying SDL_VIDEODRIVER={driver}...")
            os.environ['SDL_VIDEODRIVER'] = driver
            try:
                pygame.quit()
                pygame.init()
                screen = pygame.display.set_mode((800, 480))
                screen.fill((255, 0, 0))  # Red
                pygame.display.flip()
                print(f"✅ {driver} driver works!")
                
                print("Press Enter to continue...")
                input()
                break
            except Exception as e2:
                print(f"❌ {driver} failed: {e2}")
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    test_pygame_display()
