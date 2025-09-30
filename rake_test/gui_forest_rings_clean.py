#!/usr/bin/env python3
"""
Natural Tree Rings Theme - Simple and clean forest growth visualization
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

# Natural Forest color palette
COLORS = {
    'bg': (8, 20, 15),            # Forest night
    'bg_light': (15, 30, 22),     # Lighter forest areas
    'accent1': (50, 205, 50),     # Forest green
    'accent2': (255, 140, 0),     # Warm orange
    'accent3': (135, 206, 235),   # Sky blue
    'text': (240, 255, 240),      # Off-white text
    'text_warm': (255, 248, 220), # Warm text for readings
    'gps': (255, 215, 0),         # Golden GPS
    'ring_temp': (205, 92, 92),   # Indian red for temperature
    'ring_hum': (100, 149, 237),  # Cornflower blue for humidity
    'ring_press': (144, 238, 144), # Light green for pressure
    'reading_bg': (40, 50, 40),   # Dark moss green background
    'reading_border': (139, 169, 19), # Olive green border
}

class NaturalTreeRingsGUI:
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
    
    def draw_tree_rings(self, surface, center_x, center_y, data_history, ring_color, max_radius=70):
        """Draw natural tree rings based on sensor data history"""
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
            return
        
        # Draw rings from oldest to newest (inside out)
        for i, value in enumerate(data_list):
            normalized = (value - min_val) / (max_val - min_val)
            ring_radius = int(8 + normalized * max_radius)
            
            # Ring opacity based on age (newer = more opaque)
            age_factor = i / len(data_list)
            alpha = int(50 + age_factor * 150)
            thickness = max(1, int(1 + age_factor * 2))
            
            # Create ring surface with alpha
            ring_surface = pygame.Surface((ring_radius * 2, ring_radius * 2), pygame.SRCALPHA)
            ring_color_alpha = (*ring_color[:3], alpha)
            pygame.draw.circle(ring_surface, ring_color_alpha, (ring_radius, ring_radius), ring_radius, thickness)
            
            # Blit ring
            surface.blit(ring_surface, (center_x - ring_radius, center_y - ring_radius))
    
    def draw_reading_box(self, surface, x, y, width, height, label, value, unit, color):
        """Draw a contrasting reading display box"""
        # Background box
        reading_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, COLORS['reading_bg'], reading_rect, border_radius=8)
        pygame.draw.rect(surface, color, reading_rect, 2, border_radius=8)
        
        # Label
        label_surface = self.font_small.render(label, True, COLORS['text_warm'])
        label_rect = label_surface.get_rect(center=(x + width // 2, y + 15))
        surface.blit(label_surface, label_rect)
        
        # Current value (prominent and clear)
        value_text = f"{value:.1f}{unit}"
        value_surface = self.font_large.render(value_text, True, COLORS['text'])
        value_rect = value_surface.get_rect(center=(x + width // 2, y + 35))
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
        
        # Natural background gradient
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            bg_color = (
                int(COLORS['bg'][0] + (COLORS['bg_light'][0] - COLORS['bg'][0]) * ratio),
                int(COLORS['bg'][1] + (COLORS['bg_light'][1] - COLORS['bg'][1]) * ratio),
                int(COLORS['bg'][2] + (COLORS['bg_light'][2] - COLORS['bg'][2]) * ratio)
            )
            pygame.draw.line(SCREEN, bg_color, (0, y), (WIDTH, y))
        
        # Title
        title = self.font_title.render("🌲 Forest Growth Monitor", True, COLORS['accent1'])
        title_rect = title.get_rect(center=(WIDTH // 2, 30))
        SCREEN.blit(title, title_rect)
        
        # Status
        status_text = "🌿 GROWING" if self.recording else "⏸️ PAUSED"
        status_color = COLORS['accent2'] if self.recording else COLORS['accent3']
        status_surface = self.font_medium.render(status_text, True, status_color)
        SCREEN.blit(status_surface, (WIDTH - 140, 10))
        
        # GPS Display (prominent and clear)
        if gps_data and gps_data.get('latitude'):
            gps_y = 70
            
            # GPS container
            gps_rect = pygame.Rect(50, gps_y - 5, 400, 80)
            pygame.draw.rect(SCREEN, COLORS['reading_bg'], gps_rect, border_radius=10)
            pygame.draw.rect(SCREEN, COLORS['gps'], gps_rect, 2, border_radius=10)
            
            # GPS Header
            gps_header = self.font_large.render("📍 CURRENT LOCATION", True, COLORS['gps'])
            SCREEN.blit(gps_header, (60, gps_y + 5))
            
            # Coordinates (clean and readable)
            lat_text = f"Latitude:  {gps_data['latitude']:.7f}°"
            lon_text = f"Longitude: {gps_data['longitude']:.7f}°"
            alt_text = f"Alt: {gps_data.get('altitude', 0):.1f}m"
            
            lat_surface = self.font_medium.render(lat_text, True, COLORS['text'])
            lon_surface = self.font_medium.render(lon_text, True, COLORS['text'])
            alt_surface = self.font_medium.render(alt_text, True, COLORS['accent1'])
            
            SCREEN.blit(lat_surface, (60, gps_y + 25))
            SCREEN.blit(lon_surface, (60, gps_y + 40))
            SCREEN.blit(alt_surface, (320, gps_y + 55))
        
        # Tree Rings Visualization (main feature)
        rings_y = 200
        
        # Draw tree rings for each sensor
        self.draw_tree_rings(SCREEN, 150, rings_y, self.temp_history, COLORS['ring_temp'])
        self.draw_tree_rings(SCREEN, 400, rings_y, self.humidity_history, COLORS['ring_hum'])  
        self.draw_tree_rings(SCREEN, 650, rings_y, self.pressure_history, COLORS['ring_press'])
        
        # Current readings in contrasting boxes below rings
        if sensor_data:
            current_temp = sensor_data.get('temperature', 22.0)
            current_hum = sensor_data.get('humidity', 65.0)
            current_press = sensor_data.get('pressure', 1013.0)
            
            # Reading boxes positioned below each tree ring
            self.draw_reading_box(SCREEN, 100, rings_y + 90, 100, 55, 
                                "🌡️ Temperature", current_temp, "°C", COLORS['ring_temp'])
            self.draw_reading_box(SCREEN, 350, rings_y + 90, 100, 55,
                                "💧 Humidity", current_hum, "%", COLORS['ring_hum'])
            self.draw_reading_box(SCREEN, 600, rings_y + 90, 100, 55,
                                "🌪️ Pressure", current_press, " hPa", COLORS['ring_press'])
        
        # Control button
        button_text = "⏸️ PAUSE" if self.recording else "▶️ START"
        button_rect = pygame.Rect(350, 380, 100, 40)
        
        button_color = COLORS['accent2'] if self.recording else COLORS['accent1']
        pygame.draw.rect(SCREEN, button_color, button_rect, border_radius=10)
        
        text_surface = self.font_medium.render(button_text, True, COLORS['bg'])
        text_rect = text_surface.get_rect(center=button_rect.center)
        SCREEN.blit(text_surface, text_rect)
        
        # Instructions (simple and clear)
        inst1 = self.font_small.render("🌳 Watch the tree rings grow as sensor data changes over time", True, COLORS['text_warm'])
        inst2 = self.font_small.render("🍃 Each ring represents a data reading - newer rings appear brighter", True, COLORS['text_warm'])
        
        SCREEN.blit(inst1, (50, 440))
        SCREEN.blit(inst2, (50, 455))
        
        return button_rect

# Sample data
sample_sensor = {
    'temperature': 22.5,
    'humidity': 65.2,
    'pressure': 1013.2,
    'gas_resistance': 85000
}

sample_gps = {
    'latitude': 37.774929,
    'longitude': -122.419416,
    'altitude': 52.3
}

# Main loop
if __name__ == "__main__":
    gui = NaturalTreeRingsGUI()
    clock = pygame.time.Clock()
    running = True
    
    print("🌲 Natural Tree Rings Theme - Clean forest growth visualization!")
    
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
