#!/usr/bin/env python3
"""
Direct DRM/KMS Display for Pi - Bypass pygame video driver issues
Works directly with DRM framebuffer for DSI displays
"""

import pygame
import os
import time
import math
import random
from collections import deque

# Force pygame to use dummy driver but capture the surface
os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()

WIDTH, HEIGHT = 800, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Forest Monitor - Direct Display")

print("Using direct DRM framebuffer method...")

# Forest colors (same as before)
COLORS = {
    'bg': (15, 25, 20),
    'bg_light': (25, 35, 30),
    'accent1': (100, 200, 120),
    'accent2': (180, 140, 100),
    'text': (240, 250, 240),
    'text_dim': (180, 190, 180),
    'gps': (255, 200, 100),
    'ring_temp': (220, 100, 100),
    'ring_hum': (100, 150, 220),
    'ring_press': (120, 200, 120),
    'reading_bg': (45, 60, 50),
    'reading_border': (150, 180, 150),
}

class DirectDisplayGUI:
    def __init__(self):
        self.font_title = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 28)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        
        # Data history
        self.temp_history = deque(maxlen=50)
        self.humidity_history = deque(maxlen=50)
        self.pressure_history = deque(maxlen=50)
        
        self.time = 0
        self.recording = False
        
        # Initialize with sample data
        for i in range(20):
            self.temp_history.append(22.0 + random.uniform(-2, 2))
            self.humidity_history.append(65.0 + random.uniform(-10, 10))
            self.pressure_history.append(1013.0 + random.uniform(-5, 5))
    
    def draw_tree_rings(self, surface, center_x, center_y, data_history, ring_color, current_value, unit, label, max_radius=70):
        """Draw tree rings with separate readings"""
        if len(data_history) < 2:
            return
        
        data_list = list(data_history)
        min_val = min(data_list)
        max_val = max(data_list)
        
        if max_val != min_val:
            for i, value in enumerate(data_list):
                normalized = (value - min_val) / (max_val - min_val)
                ring_radius = int(10 + normalized * max_radius)
                age_factor = i / len(data_list)
                alpha = int(60 + age_factor * 140)
                thickness = 1 if i < len(data_list) - 3 else 2
                
                # Create ring with alpha
                ring_surface = pygame.Surface((ring_radius * 2 + 4, ring_radius * 2 + 4), pygame.SRCALPHA)
                ring_color_alpha = (*ring_color[:3], alpha)
                pygame.draw.circle(ring_surface, ring_color_alpha, 
                                 (ring_radius + 2, ring_radius + 2), ring_radius, thickness)
                surface.blit(ring_surface, (center_x - ring_radius - 2, center_y - ring_radius - 2))
        
        # Reading box
        reading_width, reading_height = 100, 45
        reading_x = center_x - reading_width // 2
        reading_y = center_y + max_radius + 25
        
        reading_rect = pygame.Rect(reading_x, reading_y, reading_width, reading_height)
        pygame.draw.rect(surface, COLORS['reading_bg'], reading_rect, border_radius=8)
        pygame.draw.rect(surface, COLORS['reading_border'], reading_rect, 2, border_radius=8)
        
        # Text
        label_surface = self.font_small.render(label, True, COLORS['text_dim'])
        label_rect = label_surface.get_rect(center=(center_x, reading_y + 12))
        surface.blit(label_surface, label_rect)
        
        value_text = f"{current_value:.1f}{unit}"
        value_surface = self.font_medium.render(value_text, True, COLORS['text'])
        value_rect = value_surface.get_rect(center=(center_x, reading_y + 28))
        surface.blit(value_surface, value_rect)
    
    def update_data(self, sensor_data):
        if sensor_data:
            self.temp_history.append(sensor_data.get('temperature', 22.0))
            self.humidity_history.append(sensor_data.get('humidity', 65.0))
            self.pressure_history.append(sensor_data.get('pressure', 1013.0))
    
    def write_to_framebuffer(self, surface):
        """Write pygame surface directly to framebuffer"""
        try:
            # Convert pygame surface to raw RGB data
            raw_data = pygame.image.tostring(surface, 'RGB')
            
            # Write to framebuffer
            with open('/dev/fb0', 'wb') as fb:
                # Convert RGB to framebuffer format (assuming RGB565)
                fb_data = bytearray()
                for i in range(0, len(raw_data), 3):
                    if i + 2 < len(raw_data):
                        r = raw_data[i] >> 3      # 5 bits
                        g = raw_data[i+1] >> 2    # 6 bits  
                        b = raw_data[i+2] >> 3    # 5 bits
                        
                        # Pack into RGB565
                        rgb565 = (r << 11) | (g << 5) | b
                        fb_data.append(rgb565 & 0xFF)
                        fb_data.append((rgb565 >> 8) & 0xFF)
                
                fb.write(fb_data)
                
        except Exception as e:
            print(f"Framebuffer write failed: {e}")
    
    def render(self, sensor_data, gps_data, recording_status):
        self.recording = recording_status
        self.time += 0.05
        
        if self.recording and sensor_data:
            if int(self.time * 10) % 30 == 0:
                self.update_data(sensor_data)
        
        # Draw background gradient
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            bg_color = (
                int(COLORS['bg'][0] + (COLORS['bg_light'][0] - COLORS['bg'][0]) * ratio),
                int(COLORS['bg'][1] + (COLORS['bg_light'][1] - COLORS['bg'][1]) * ratio),
                int(COLORS['bg'][2] + (COLORS['bg_light'][2] - COLORS['bg'][2]) * ratio)
            )
            pygame.draw.line(screen, bg_color, (0, y), (WIDTH, y))
        
        # Title
        title = self.font_title.render("Forest Growth Monitor", True, COLORS['accent1'])
        title_rect = title.get_rect(center=(WIDTH // 2, 30))
        screen.blit(title, title_rect)
        
        # Status
        status = "GROWING" if self.recording else "PAUSED"
        status_color = COLORS['accent1'] if self.recording else COLORS['accent2']
        status_surface = self.font_medium.render(status, True, status_color)
        screen.blit(status_surface, (WIDTH - 100, 10))
        
        # GPS Display
        if gps_data and gps_data.get('latitude'):
            gps_y = 70
            gps_rect = pygame.Rect(40, gps_y - 5, 420, 80)
            pygame.draw.rect(screen, COLORS['reading_bg'], gps_rect, border_radius=10)
            pygame.draw.rect(screen, COLORS['gps'], gps_rect, 2, border_radius=10)
            
            gps_header = self.font_large.render("LOCATION", True, COLORS['gps'])
            screen.blit(gps_header, (50, gps_y + 5))
            
            lat_text = f"Lat: {gps_data['latitude']:.7f}°"
            lon_text = f"Lon: {gps_data['longitude']:.7f}°"
            alt_text = f"Alt: {gps_data.get('altitude', 0):.1f}m"
            
            lat_surface = self.font_medium.render(lat_text, True, COLORS['text'])
            lon_surface = self.font_medium.render(lon_text, True, COLORS['text'])
            alt_surface = self.font_small.render(alt_text, True, COLORS['accent1'])
            
            screen.blit(lat_surface, (50, gps_y + 25))
            screen.blit(lon_surface, (50, gps_y + 45))
            screen.blit(alt_surface, (350, gps_y + 35))
        
        # Tree rings
        rings_y = 180
        rings_title = self.font_large.render("Data Tree Rings", True, COLORS['text'])
        rings_title_rect = rings_title.get_rect(center=(WIDTH // 2, rings_y - 20))
        screen.blit(rings_title, rings_title_rect)
        
        current_temp = sensor_data.get('temperature', 22.0) if sensor_data else 22.0
        current_hum = sensor_data.get('humidity', 65.0) if sensor_data else 65.0
        current_press = sensor_data.get('pressure', 1013.0) if sensor_data else 1013.0
        
        self.draw_tree_rings(screen, 150, rings_y + 40, self.temp_history, COLORS['ring_temp'], 
                           current_temp, "°C", "Temperature")
        self.draw_tree_rings(screen, 400, rings_y + 40, self.humidity_history, COLORS['ring_hum'],
                           current_hum, "%", "Humidity")
        self.draw_tree_rings(screen, 650, rings_y + 40, self.pressure_history, COLORS['ring_press'],
                           current_press, " hPa", "Pressure")
        
        # Control button
        button_text = "PAUSE" if self.recording else "START"
        button_rect = pygame.Rect(350, 380, 100, 40)
        button_color = COLORS['accent2'] if self.recording else COLORS['accent1']
        pygame.draw.rect(screen, button_color, button_rect, border_radius=10)
        
        text_surface = self.font_medium.render(button_text, True, COLORS['bg'])
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)
        
        # Instructions
        inst1 = self.font_small.render("Tree rings grow as sensor data changes", True, COLORS['text_dim'])
        inst2 = self.font_small.render("Direct framebuffer display - should be visible!", True, COLORS['text_dim'])
        screen.blit(inst1, (50, 450))
        screen.blit(inst2, (50, 465))
        
        # Write to framebuffer
        self.write_to_framebuffer(screen)
        
        return button_rect

# Sample data
sample_sensor = {
    'temperature': 22.5,
    'humidity': 65.2,
    'pressure': 1013.2,
}

sample_gps = {
    'latitude': 37.774929,
    'longitude': -122.419416,
    'altitude': 52.3
}

# Main loop
if __name__ == "__main__":
    gui = DirectDisplayGUI()
    clock = pygame.time.Clock()
    running = True
    
    print("Direct framebuffer GUI - should appear on your DSI display!")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    gui.recording = not gui.recording
                elif event.key == pygame.K_ESCAPE:
                    running = False
        
        # Update sample data
        if gui.recording:
            sample_sensor['temperature'] += random.uniform(-0.1, 0.1)
            sample_sensor['humidity'] += random.uniform(-0.5, 0.5)
            sample_sensor['pressure'] += random.uniform(-0.2, 0.2)
        
        button_rect = gui.render(sample_sensor, sample_gps, gui.recording)
        clock.tick(30)
    
    pygame.quit()
