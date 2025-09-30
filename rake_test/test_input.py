#!/usr/bin/env python3
"""
Simple test to verify mouse clicks and SPACE bar are working
"""

import pygame
import sys

def test_input():
    pygame.init()
    screen = pygame.display.set_mode((800, 480))
    pygame.display.set_caption("Input Test - Press SPACE or click mouse")
    
    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()
    
    clicks = 0
    space_presses = 0
    
    print("Input test started - press SPACE or click mouse in the window")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    space_presses += 1
                    print(f"SPACE pressed! Count: {space_presses}")
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicks += 1
                print(f"Mouse clicked at {event.pos}! Count: {clicks}")
        
        # Draw status
        screen.fill((50, 50, 100))
        
        text1 = font.render(f"Mouse clicks: {clicks}", True, (255, 255, 255))
        text2 = font.render(f"SPACE presses: {space_presses}", True, (255, 255, 255))
        text3 = font.render("Press ESC to exit", True, (200, 200, 200))
        
        screen.blit(text1, (50, 100))
        screen.blit(text2, (50, 150))
        screen.blit(text3, (50, 200))
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    print(f"Test completed. Clicks: {clicks}, SPACE: {space_presses}")

if __name__ == "__main__":
    test_input()
