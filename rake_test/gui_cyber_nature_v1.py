#!/usr/bin/env python3
"""
Cyber Nature Theme v1: Forest Rings - Clean layout with tree ring growth visualization
"""

import pygame
import math
import random
import os
import time
from collections import deque

# Set up display - auto-detect best driver
pygame.init()

WIDTH, HEIGHT = 800, 480
display_drivers = ['cocoa', 'x11', 'kmsdrm', 'fbcon', 'dummy']
SCREEN = None

for driver in display_drivers:
    try:
        os.environ['SDL_VIDEODRIVER'] = driver
        if driver in ['kmsdrm', 'fbcon']:
            os.environ['SDL_NOMOUSE'] = '1'
        pygame.display.quit()
        pygame.display.init()
        SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
        print(f"Using display driver: {driver}")
        break
    except pygame.error:
        continue

if SCREEN is None:
    os.environ.pop('SDL_VIDEODRIVER', None)
    pygame.display.init()
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Forest Monitor - Tree Rings")

# Natural Forest color palette with subtle improvements
COLORS = {
    'bg': (8, 20, 15),            # Forest night
    'bg_light': (15, 30, 22),     # Lighter forest
    'accent1': (50, 205, 50),     # Forest green
    'accent2': (255, 140, 0),     # Warm orange
    'accent3': (135, 206, 235),   # Sky blue
    'text': (240, 255, 240),      # Off-white text
    'text_warm': (255, 248, 220), # Warm text
    'gps': (255, 215, 0),         # Golden GPS
    'ring_temp': (220, 100, 80),  # Warm red-brown
    'ring_hum': (100, 149, 237),  # Cornflower blue
    'ring_press': (144, 238, 144), # Light green
    'reading_bg': (40, 50, 40),   # Dark moss green
    'reading_border': (139, 169, 19), # Olive green
}

class ForestRingsGUI:
    def __init__(self):
        self.font_title = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 28)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        
        # Data history for tree rings (last 50 readings)
        self.temp_history = deque(maxlen=50)
        self.humidity_history = deque(maxlen=50)
        self.pressure_history = deque(maxlen=50)
        
        self.time = 0
        self.recording = False
        
        # Initialize with some sample data
        for i in range(20):
            self.temp_history.append(22.0 + random.uniform(-2, 2))
            self.humidity_history.append(65.0 + random.uniform(-10, 10))
            self.pressure_history.append(1013.0 + random.uniform(-5, 5))
    
    def draw_glow(self, surface, color, pos, radius):
        """Subtle natural glow effect"""
        for i in range(3):
            alpha = 60 // (i + 1)
            glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*color[:3], alpha), (radius, radius), radius - i * 2)
            surface.blit(glow_surface, (pos[0] - radius, pos[1] - radius), special_flags=pygame.BLEND_ADD)
    
    def draw_tree_rings(self, surface, center_x, center_y, data_history, ring_color, current_value, unit, label, max_radius=80):
        """Draw natural tree rings with clear current reading"""
        if len(data_history) < 2:
            return
        
        # Normalize data to ring sizes
        data_list = list(data_history)
        min_val = min(data_list)
        max_val = max(data_list)
        
        if max_val == min_val:
            # Single value - draw a simple ring
            ring_radius = 25
            pygame.draw.circle(surface, ring_color, (center_x, center_y), ring_radius, 2)
        else:
            # Draw rings from oldest to newest (inside out)
            for i, value in enumerate(data_list):
                normalized = (value - min_val) / (max_val - min_val)
                ring_radius = int(10 + normalized * max_radius)
                
                # Ring opacity based on age (newer = more opaque)
                age_factor = i / len(data_list)
                alpha = int(60 + age_factor * 140)
                thickness = max(1, int(1 + age_factor * 2))
                
                # Create ring surface with alpha
                ring_surface = pygame.Surface((ring_radius * 2, ring_radius * 2), pygame.SRCALPHA)
                ring_color_alpha = (*ring_color[:3], alpha)
                pygame.draw.circle(ring_surface, ring_color_alpha, (ring_radius, ring_radius), ring_radius, thickness)
                
                # Blit ring
                surface.blit(ring_surface, (center_x - ring_radius, center_y - ring_radius))
        
        # Draw contrasting current reading display below the rings
        reading_width, reading_height = 100, 50
        reading_x = center_x - reading_width // 2
        reading_y = center_y + max_radius + 15
        
        # Reading background
        reading_rect = pygame.Rect(reading_x, reading_y, reading_width, reading_height)
        pygame.draw.rect(surface, COLORS['reading_bg'], reading_rect, border_radius=8)
        pygame.draw.rect(surface, COLORS['reading_border'], reading_rect, 2, border_radius=8)
        
        # Label
        label_surface = self.font_small.render(label, True, COLORS['text_warm'])
        label_rect = label_surface.get_rect(center=(center_x, reading_y + 12))
        surface.blit(label_surface, label_rect)
        
        # Current value
        value_text = f"{current_value:.1f}{unit}"
        value_surface = self.font_medium.render(value_text, True, COLORS['text'])
        value_rect = value_surface.get_rect(center=(center_x, reading_y + 32))
        surface.blit(value_surface, value_rect)
    
    def update_data(self, sensor_data):
        """Update sensor data history"""
        if sensor_data:
            self.temp_history.append(sensor_data.get('temperature', 22.0))
            self.humidity_history.append(sensor_data.get('humidity', 65.0))
            self.pressure_history.append(sensor_data.get('pressure', 1013.0))
    
    def render(self, sensor_data, gps_data, recording_status):
        self.recording = recording_status
        self.time += 0.05
        
        # Update data if recording
        if self.recording and sensor_data:
            # Only update occasionally to see ring growth
            if int(self.time * 10) % 30 == 0:  # Every 3 seconds
                self.update_data(sensor_data)
        
        # Background with gradient
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            bg_color = (
                int(COLORS['bg'][0] + (COLORS['bg_glow'][0] - COLORS['bg'][0]) * ratio),
                int(COLORS['bg'][1] + (COLORS['bg_glow'][1] - COLORS['bg'][1]) * ratio),
                int(COLORS['bg'][2] + (COLORS['bg_glow'][2] - COLORS['bg'][2]) * ratio)
            )
            pygame.draw.line(SCREEN, bg_color, (0, y), (WIDTH, y))
        
        # Draw cyber grid
        self.draw_cyber_grid(SCREEN)
        
        # Title with glitch effect
        self.draw_glitch_text(SCREEN, "⚡ CYBER FOREST MONITOR ⚡", self.font_title, 
                             COLORS['accent1'], WIDTH // 2 - 180, 20)
        
        # Add title glow
        self.draw_glow(SCREEN, COLORS['accent1'], (WIDTH // 2, 35), 150, intensity=2)
        
        # Status with pulsing effect
        status_text = "� GROWING" if self.recording else "⏸️ DORMANT"
        status_color = COLORS['accent2'] if self.recording else COLORS['accent3']
        
        if self.recording:
            # Pulsing effect for active status
            pulse = math.sin(self.time * 4) * 0.3 + 1
            pulse_color = tuple(max(0, min(255, int(c * pulse))) for c in status_color)
            self.draw_glitch_text(SCREEN, status_text, self.font_medium, pulse_color, WIDTH - 160, 10)
        else:
            status_surface = self.font_medium.render(status_text, True, status_color)
            SCREEN.blit(status_surface, (WIDTH - 160, 10))
        
        # GPS Display with cyberpunk styling
        if gps_data and gps_data.get('latitude'):
            gps_y = 70
            
            # GPS container with glow
            gps_rect = pygame.Rect(40, gps_y - 10, 400, 90)
            pygame.draw.rect(SCREEN, COLORS['reading_bg'], gps_rect, border_radius=15)
            pygame.draw.rect(SCREEN, COLORS['gps'], gps_rect, 3, border_radius=15)
            self.draw_glow(SCREEN, COLORS['gps'], (240, gps_y + 35), 100)
            
            # GPS Header with glitch
            self.draw_glitch_text(SCREEN, "🛰️ NEURAL LINK COORDINATES", self.font_large, 
                                 COLORS['gps_glow'], 50, gps_y)
            
            # Coordinates with high precision and glow
            lat_text = f"LAT: {gps_data['latitude']:.7f}°N"
            lon_text = f"LON: {gps_data['longitude']:.7f}°W"
            alt_text = f"ALT: {gps_data.get('altitude', 0):.1f}m"
            
            # Main coordinate text
            lat_surface = self.font_large.render(lat_text, True, COLORS['text'])
            lon_surface = self.font_large.render(lon_text, True, COLORS['text'])
            alt_surface = self.font_medium.render(alt_text, True, COLORS['accent1'])
            
            SCREEN.blit(lat_surface, (50, gps_y + 25))
            SCREEN.blit(lon_surface, (50, gps_y + 45))
            SCREEN.blit(alt_surface, (50, gps_y + 70))
            
            # Add subtle glow to coordinates
            glow_lat = self.font_large.render(lat_text, True, COLORS['gps'])
            glow_lon = self.font_large.render(lon_text, True, COLORS['gps'])
            SCREEN.blit(glow_lat, (49, gps_y + 25), special_flags=pygame.BLEND_ADD)
            SCREEN.blit(glow_lon, (49, gps_y + 45), special_flags=pygame.BLEND_ADD)
        
        # Tree Rings Visualization (main feature)
        rings_y = 180
        
        # Get current sensor values for display
        current_temp = sensor_data.get('temperature', 22.0) if sensor_data else 22.0
        current_hum = sensor_data.get('humidity', 65.0) if sensor_data else 65.0
        current_press = sensor_data.get('pressure', 1013.0) if sensor_data else 1013.0
        
        # Draw tree rings with high contrast readings
        self.draw_tree_rings(SCREEN, 150, rings_y, self.temp_history, COLORS['ring_temp'], 
                           current_temp, "°C", "🌡️ TEMPERATURE")
        self.draw_tree_rings(SCREEN, 400, rings_y, self.humidity_history, COLORS['ring_hum'],
                           current_hum, "%", "💧 HUMIDITY")
        self.draw_tree_rings(SCREEN, 650, rings_y, self.pressure_history, COLORS['ring_press'],
                           current_press, " hPa", "🌪️ PRESSURE")
        
        # Control button with cyberpunk styling
        button_text = "⏸️ PAUSE MATRIX" if self.recording else "▶️ JACK IN"
        button_rect = pygame.Rect(320, 380, 160, 50)
        
        button_color = COLORS['accent2'] if self.recording else COLORS['accent1']
        
        # Button glow
        self.draw_glow(SCREEN, button_color, (400, 405), 60, intensity=3)
        
        # Button background
        pygame.draw.rect(SCREEN, COLORS['reading_bg'], button_rect, border_radius=15)
        pygame.draw.rect(SCREEN, button_color, button_rect, 3, border_radius=15)
        
        # Button text with glow
        text_surface = self.font_medium.render(button_text, True, COLORS['text'])
        text_rect = text_surface.get_rect(center=button_rect.center)
        SCREEN.blit(text_surface, text_rect)
        
        # Instructions with cyberpunk flair
        inst1 = self.font_small.render("⚡ Neural rings expand as data flows through the matrix", True, COLORS['text_glow'])
        inst2 = self.font_small.render("💎 Newer data pulses brighter - watch the cyber-growth patterns", True, COLORS['text_glow'])
        
        SCREEN.blit(inst1, (30, 450))
        SCREEN.blit(inst2, (30, 465))
        
        return button_rect

# Sample data
sample_sensor = {
    'temperature': 22.5 + random.uniform(-1, 1),
    'humidity': 65.2 + random.uniform(-5, 5),
    'pressure': 1013.2 + random.uniform(-2, 2),
    'gas_resistance': 85000
}

sample_gps = {
    'latitude': 37.774929,
    'longitude': -122.419416,
    'altitude': 52.3
}

# Main loop
if __name__ == "__main__":
    gui = ForestRingsGUI()
    clock = pygame.time.Clock()
    running = True
    
    print("🌲 Forest Rings Theme - Watch your data grow like tree rings!")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    gui.recording = not gui.recording
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                button_rect = gui.render(sample_sensor, sample_gps, gui.recording)
                if button_rect.collidepoint(event.pos):
                    gui.recording = not gui.recording
        
        # Update sample data slightly for demo
        if gui.recording:
            sample_sensor['temperature'] += random.uniform(-0.1, 0.1)
            sample_sensor['humidity'] += random.uniform(-0.5, 0.5)
            sample_sensor['pressure'] += random.uniform(-0.2, 0.2)
        
        button_rect = gui.render(sample_sensor, sample_gps, gui.recording)
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
