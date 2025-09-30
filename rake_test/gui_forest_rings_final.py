#!/usr/bin/env python3
"""
Forest Rings Theme - Clean version without emojis for better compatibility
"""

import pygame
import math
import random
import os
import time
from collections import deque

# Set up display - Pi-optimized driver priority
pygame.init()

WIDTH, HEIGHT = 800, 480

# Pi-first driver order (kmsdrm works best for DSI displays)
display_drivers = ['kmsdrm', 'fbcon', 'directfb', 'x11', 'cocoa', 'dummy']
SCREEN = None

print("Trying display drivers for Pi...")
for driver in display_drivers:
    try:
        print(f"Testing {driver}...")
        os.environ['SDL_VIDEODRIVER'] = driver
        
        # Disable mouse for Pi drivers
        if driver in ['kmsdrm', 'fbcon', 'directfb']:
            os.environ['SDL_NOMOUSE'] = '1'
        else:
            os.environ.pop('SDL_NOMOUSE', None)
        
        pygame.display.quit()
        pygame.display.init()
        SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
        
        actual_driver = pygame.display.get_driver()
        print(f"SUCCESS: Using display driver: {actual_driver}")
        break
        
    except pygame.error as e:
        print(f"Failed {driver}: {e}")
        continue

if SCREEN is None:
    print("All drivers failed - using pygame default")
    os.environ.pop('SDL_VIDEODRIVER', None)
    os.environ.pop('SDL_NOMOUSE', None)
    pygame.display.init()
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Forest Monitor - Tree Rings")

# Natural forest colors
COLORS = {
    'bg': (15, 25, 20),           # Deep forest
    'bg_light': (25, 35, 30),     # Lighter forest
    'card': (35, 50, 40),         # Tree bark
    'accent1': (100, 200, 120),   # Forest green
    'accent2': (180, 140, 100),   # Warm brown
    'accent3': (120, 160, 200),   # Sky blue
    'text': (240, 250, 240),      # Light text
    'text_dim': (180, 190, 180),  # Dimmer text
    'gps': (255, 200, 100),       # Golden GPS
    'ring_temp': (220, 100, 100), # Warm red rings
    'ring_hum': (100, 150, 220),  # Cool blue rings
    'ring_press': (120, 200, 120), # Green rings
    'reading_bg': (45, 60, 50),   # Reading background
    'reading_border': (150, 180, 150), # Reading border
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
    
    def draw_simple_glow(self, surface, color, pos, radius):
        """Simple glow effect"""
        for i in range(2):
            alpha = 60 // (i + 1)
            glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*color[:3], alpha), (radius, radius), radius - i * 2)
            surface.blit(glow_surface, (pos[0] - radius, pos[1] - radius), special_flags=pygame.BLEND_ADD)
    
    def draw_tree_rings(self, surface, center_x, center_y, data_history, ring_color, current_value, unit, label, max_radius=70):
        """Draw tree rings with separate current reading display"""
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
                
                # Create ring surface with alpha
                ring_surface = pygame.Surface((ring_radius * 2 + 4, ring_radius * 2 + 4), pygame.SRCALPHA)
                ring_color_alpha = (*ring_color[:3], alpha)
                thickness = 1 if i < len(data_list) - 3 else 2  # Thicker for recent rings
                pygame.draw.circle(ring_surface, ring_color_alpha, 
                                 (ring_radius + 2, ring_radius + 2), ring_radius, thickness)
                
                # Blit ring
                surface.blit(ring_surface, (center_x - ring_radius - 2, center_y - ring_radius - 2))
        
        # Draw current reading in a separate box below
        reading_width, reading_height = 100, 45
        reading_x = center_x - reading_width // 2
        reading_y = center_y + max_radius + 25
        
        # Reading background
        reading_rect = pygame.Rect(reading_x, reading_y, reading_width, reading_height)
        pygame.draw.rect(surface, COLORS['reading_bg'], reading_rect, border_radius=8)
        pygame.draw.rect(surface, COLORS['reading_border'], reading_rect, 2, border_radius=8)
        
        # Label
        label_surface = self.font_small.render(label, True, COLORS['text_dim'])
        label_rect = label_surface.get_rect(center=(center_x, reading_y + 12))
        surface.blit(label_surface, label_rect)
        
        # Current value (large and clear)
        value_text = f"{current_value:.1f}{unit}"
        value_surface = self.font_medium.render(value_text, True, COLORS['text'])
        value_rect = value_surface.get_rect(center=(center_x, reading_y + 28))
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
        
        # Background gradient
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            bg_color = (
                int(COLORS['bg'][0] + (COLORS['bg_light'][0] - COLORS['bg'][0]) * ratio),
                int(COLORS['bg'][1] + (COLORS['bg_light'][1] - COLORS['bg'][1]) * ratio),
                int(COLORS['bg'][2] + (COLORS['bg_light'][2] - COLORS['bg'][2]) * ratio)
            )
            pygame.draw.line(SCREEN, bg_color, (0, y), (WIDTH, y))
        
        # Title
        title = self.font_title.render("Forest Growth Monitor", True, COLORS['accent1'])
        title_rect = title.get_rect(center=(WIDTH // 2, 30))
        SCREEN.blit(title, title_rect)
        
        # Status
        status = "GROWING" if self.recording else "PAUSED"
        status_color = COLORS['accent1'] if self.recording else COLORS['accent2']
        status_surface = self.font_medium.render(status, True, status_color)
        SCREEN.blit(status_surface, (WIDTH - 100, 10))
        
        # GPS Display (prominent and clean)
        if gps_data and gps_data.get('latitude'):
            gps_y = 70
            
            # GPS container
            gps_rect = pygame.Rect(40, gps_y - 5, 420, 80)
            pygame.draw.rect(SCREEN, COLORS['card'], gps_rect, border_radius=10)
            pygame.draw.rect(SCREEN, COLORS['gps'], gps_rect, 2, border_radius=10)
            
            # GPS Header
            gps_header = self.font_large.render("LOCATION", True, COLORS['gps'])
            SCREEN.blit(gps_header, (50, gps_y + 5))
            
            # Coordinates (large and clear)
            lat_text = f"Lat: {gps_data['latitude']:.7f}°"
            lon_text = f"Lon: {gps_data['longitude']:.7f}°"
            alt_text = f"Alt: {gps_data.get('altitude', 0):.1f}m"
            
            lat_surface = self.font_medium.render(lat_text, True, COLORS['text'])
            lon_surface = self.font_medium.render(lon_text, True, COLORS['text'])
            alt_surface = self.font_small.render(alt_text, True, COLORS['accent3'])
            
            SCREEN.blit(lat_surface, (50, gps_y + 25))
            SCREEN.blit(lon_surface, (50, gps_y + 45))
            SCREEN.blit(alt_surface, (350, gps_y + 35))
        
        # Tree Rings section
        rings_y = 180
        
        # Section title
        rings_title = self.font_large.render("Data Tree Rings", True, COLORS['text'])
        rings_title_rect = rings_title.get_rect(center=(WIDTH // 2, rings_y - 20))
        SCREEN.blit(rings_title, rings_title_rect)
        
        # Get current sensor values for display
        current_temp = sensor_data.get('temperature', 22.0) if sensor_data else 22.0
        current_hum = sensor_data.get('humidity', 65.0) if sensor_data else 65.0
        current_press = sensor_data.get('pressure', 1013.0) if sensor_data else 1013.0
        
        # Draw tree rings with separate readings
        self.draw_tree_rings(SCREEN, 150, rings_y + 40, self.temp_history, COLORS['ring_temp'], 
                           current_temp, "°C", "Temperature")
        self.draw_tree_rings(SCREEN, 400, rings_y + 40, self.humidity_history, COLORS['ring_hum'],
                           current_hum, "%", "Humidity")
        self.draw_tree_rings(SCREEN, 650, rings_y + 40, self.pressure_history, COLORS['ring_press'],
                           current_press, " hPa", "Pressure")
        
        # Control button
        button_text = "PAUSE" if self.recording else "START"
        button_rect = pygame.Rect(350, 380, 100, 40)
        
        button_color = COLORS['accent2'] if self.recording else COLORS['accent1']
        pygame.draw.rect(SCREEN, button_color, button_rect, border_radius=10)
        
        text_surface = self.font_medium.render(button_text, True, COLORS['bg'])
        text_rect = text_surface.get_rect(center=button_rect.center)
        SCREEN.blit(text_surface, text_rect)
        
        # Instructions
        inst1 = self.font_small.render("Tree rings grow as sensor data changes over time", True, COLORS['text_dim'])
        inst2 = self.font_small.render("Each ring represents a data point - newer rings are brighter", True, COLORS['text_dim'])
        
        SCREEN.blit(inst1, (50, 450))
        SCREEN.blit(inst2, (50, 465))
        
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
    
    print("Forest Rings Theme - Watch your data grow like tree rings!")
    
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
