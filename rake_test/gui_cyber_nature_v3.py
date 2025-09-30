#!/usr/bin/env python3
"""
Cyber Nature Theme v3: Living Garden - Organic growth visualization with blooming flowers
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

pygame.display.set_caption("Forest Monitor - Living Garden")

# Garden-inspired colors
COLORS = {
    'bg': (8, 20, 15),            # Rich soil
    'soil': (15, 35, 25),         # Garden bed
    'stem': (34, 139, 34),        # Green stems
    'flower1': (255, 105, 180),   # Pink flowers (temp)
    'flower2': (135, 206, 250),   # Blue flowers (humidity)
    'flower3': (255, 215, 0),     # Yellow flowers (pressure)
    'text': (240, 255, 240),      # Bright text
    'gps': (255, 140, 0),         # Orange GPS
    'accent': (50, 255, 150),     # Bright green
    'leaf': (60, 179, 113),       # Medium sea green
}

class LivingGardenGUI:
    def __init__(self):
        self.font_title = pygame.font.Font(None, 34)
        self.font_large = pygame.font.Font(None, 28)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        
        # Garden elements
        self.flowers = []
        self.leaves = []
        self.data_history = deque(maxlen=60)
        
        self.time = 0
        self.recording = False
        self.garden_energy = 0
        
        # Initialize garden
        self.init_garden()
    
    def init_garden(self):
        """Initialize the living garden elements"""
        # Create flower beds for each sensor type
        positions = [
            (150, 300),  # Temperature flowers
            (400, 320),  # Humidity flowers  
            (650, 310),  # Pressure flowers
        ]
        
        colors = [COLORS['flower1'], COLORS['flower2'], COLORS['flower3']]
        
        for i, (pos, color) in enumerate(zip(positions, colors)):
            for j in range(8):  # 8 flowers per sensor
                angle = (j / 8) * 2 * math.pi
                radius = 30 + random.randint(-10, 20)
                
                flower_x = pos[0] + math.cos(angle) * radius
                flower_y = pos[1] + math.sin(angle) * radius
                
                self.flowers.append({
                    'x': flower_x,
                    'y': flower_y,
                    'sensor_type': i,  # 0=temp, 1=humidity, 2=pressure
                    'base_size': random.randint(8, 15),
                    'current_size': random.randint(3, 8),
                    'bloom_progress': random.uniform(0.3, 0.7),
                    'color': color,
                    'petals': random.randint(5, 8),
                    'growth_rate': random.uniform(0.01, 0.03)
                })
        
        # Add decorative leaves
        for _ in range(15):
            self.leaves.append({
                'x': random.randint(50, WIDTH - 50),
                'y': random.randint(200, HEIGHT - 100),
                'size': random.randint(10, 20),
                'rotation': random.uniform(0, 2 * math.pi),
                'sway_offset': random.uniform(0, 2 * math.pi),
                'sway_speed': random.uniform(0.02, 0.05)
            })
    
    def update_garden(self, sensor_data):
        """Update garden growth based on sensor data"""
        if not sensor_data:
            return
        
        # Calculate garden energy from data changes
        if len(self.data_history) > 1:
            prev_data = self.data_history[-1]
            temp_change = abs(sensor_data.get('temperature', 22) - prev_data.get('temperature', 22))
            hum_change = abs(sensor_data.get('humidity', 65) - prev_data.get('humidity', 65))
            press_change = abs(sensor_data.get('pressure', 1013) - prev_data.get('pressure', 1013))
            
            # More change = more garden energy
            self.garden_energy = (temp_change * 2) + (hum_change * 0.2) + (press_change * 0.1)
        
        # Update flowers based on their sensor data
        current_values = [
            sensor_data.get('temperature', 22),
            sensor_data.get('humidity', 65), 
            sensor_data.get('pressure', 1013)
        ]
        
        # Normalize values for flower size (0-1 range)
        normalized_values = [
            (current_values[0] - 10) / 30,  # Temp: 10-40°C range
            current_values[1] / 100,        # Humidity: 0-100%
            (current_values[2] - 990) / 50  # Pressure: 990-1040 hPa range
        ]
        
        for flower in self.flowers:
            sensor_idx = flower['sensor_type']
            target_bloom = max(0.2, min(1.0, normalized_values[sensor_idx]))
            
            # Grow towards target bloom level
            if flower['bloom_progress'] < target_bloom:
                flower['bloom_progress'] += flower['growth_rate'] * (1 + self.garden_energy)
            elif flower['bloom_progress'] > target_bloom:
                flower['bloom_progress'] -= flower['growth_rate'] * 0.5
            
            flower['bloom_progress'] = max(0.1, min(1.0, flower['bloom_progress']))
            flower['current_size'] = flower['base_size'] * flower['bloom_progress']
    
    def draw_flower(self, surface, flower):
        """Draw a blooming flower"""
        x, y = int(flower['x']), int(flower['y'])
        size = flower['current_size']
        color = flower['color']
        petals = flower['petals']
        
        # Draw stem
        stem_height = 20 + size * 2
        pygame.draw.line(surface, COLORS['stem'], (x, y), (x, y + stem_height), 3)
        
        # Draw petals
        for i in range(petals):
            angle = (i / petals) * 2 * math.pi + self.time * 0.5
            petal_x = x + math.cos(angle) * size * 0.8
            petal_y = y + math.sin(angle) * size * 0.8
            
            # Petal as small circle
            pygame.draw.circle(surface, color, (int(petal_x), int(petal_y)), max(3, int(size * 0.4)))
        
        # Draw flower center
        center_color = (255, 255, 150)  # Yellow center
        pygame.draw.circle(surface, center_color, (x, y), max(2, int(size * 0.3)))
        
        # Glow effect for healthy flowers
        if flower['bloom_progress'] > 0.7:
            glow_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
            glow_color = (*color[:3], 50)
            pygame.draw.circle(glow_surface, glow_color, (size * 2, size * 2), size * 2)
            surface.blit(glow_surface, (x - size * 2, y - size * 2), special_flags=pygame.BLEND_ADD)
    
    def draw_leaf(self, surface, leaf):
        """Draw a swaying leaf"""
        # Calculate sway motion
        sway = math.sin(self.time * leaf['sway_speed'] + leaf['sway_offset']) * 5
        
        x = int(leaf['x'] + sway)
        y = int(leaf['y'])
        size = leaf['size']
        
        # Leaf shape (ellipse)
        leaf_rect = pygame.Rect(x - size//2, y - size//4, size, size//2)
        pygame.draw.ellipse(surface, COLORS['leaf'], leaf_rect)
        
        # Leaf vein
        pygame.draw.line(surface, COLORS['stem'], (x, y - size//4), (x, y + size//4), 1)
    
    def draw_sensor_garden(self, surface, x, y, flowers, title, current_value, unit):
        """Draw a sensor's flower garden with current reading"""
        # Garden bed background
        bed_rect = pygame.Rect(x - 60, y - 40, 120, 100)
        pygame.draw.ellipse(surface, COLORS['soil'], bed_rect)
        
        # Title above garden
        title_surface = self.font_medium.render(title, True, COLORS['text'])
        title_rect = title_surface.get_rect(center=(x, y - 60))
        surface.blit(title_surface, title_rect)
        
        # Current value
        value_text = f"{current_value:.1f}{unit}"
        value_surface = self.font_large.render(value_text, True, COLORS['accent'])
        value_rect = value_surface.get_rect(center=(x, y + 50))
        surface.blit(value_surface, value_rect)
        
        # Health indicator based on flower bloom
        avg_bloom = sum(f['bloom_progress'] for f in flowers if abs(f['x'] - x) < 80) / max(1, len([f for f in flowers if abs(f['x'] - x) < 80]))
        
        if avg_bloom > 0.8:
            health = "🌺 Thriving"
            health_color = COLORS['accent']
        elif avg_bloom > 0.5:
            health = "🌻 Growing" 
            health_color = COLORS['flower3']
        else:
            health = "🌱 Sprouting"
            health_color = COLORS['flower1']
        
        health_surface = self.font_small.render(health, True, health_color)
        health_rect = health_surface.get_rect(center=(x, y + 70))
        surface.blit(health_surface, health_rect)
    
    def render(self, sensor_data, gps_data, recording_status):
        self.recording = recording_status
        self.time += 0.03
        
        # Update data history and garden
        if sensor_data:
            self.data_history.append(sensor_data)
            if self.recording:
                self.update_garden(sensor_data)
        
        # Background gradient (soil to sky)
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            if y < HEIGHT * 0.7:  # Soil area
                bg_color = (
                    int(COLORS['bg'][0] + (COLORS['soil'][0] - COLORS['bg'][0]) * ratio),
                    int(COLORS['bg'][1] + (COLORS['soil'][1] - COLORS['bg'][1]) * ratio),
                    int(COLORS['bg'][2] + (COLORS['soil'][2] - COLORS['bg'][2]) * ratio)
                )
            else:  # Sky area
                sky_ratio = (y - HEIGHT * 0.7) / (HEIGHT * 0.3)
                bg_color = (
                    int(COLORS['soil'][0] + (20 - COLORS['soil'][0]) * sky_ratio),
                    int(COLORS['soil'][1] + (40 - COLORS['soil'][1]) * sky_ratio),
                    int(COLORS['soil'][2] + (60 - COLORS['soil'][2]) * sky_ratio)
                )
            pygame.draw.line(SCREEN, bg_color, (0, y), (WIDTH, y))
        
        # Title
        title = self.font_title.render("🌺 Living Sensor Garden", True, COLORS['accent'])
        title_rect = title.get_rect(center=(WIDTH // 2, 30))
        SCREEN.blit(title, title_rect)
        
        # Status
        status_text = "🌿 BLOOMING" if self.recording else "🌱 DORMANT"
        status_surface = self.font_medium.render(status_text, True, COLORS['flower1'])
        SCREEN.blit(status_surface, (WIDTH - 150, 10))
        
        # GPS Display (top section, very clear)
        if gps_data and gps_data.get('latitude'):
            # GPS container
            gps_rect = pygame.Rect(50, 60, 400, 90)
            pygame.draw.rect(SCREEN, COLORS['soil'], gps_rect, border_radius=15)
            pygame.draw.rect(SCREEN, COLORS['gps'], gps_rect, 3, border_radius=15)
            
            # GPS header
            gps_title = self.font_large.render("🗺️ GARDEN LOCATION", True, COLORS['gps'])
            SCREEN.blit(gps_title, (60, 70))
            
            # Coordinates with high precision
            lat_text = f"📍 {gps_data['latitude']:.8f}° North"
            lon_text = f"🧭 {gps_data['longitude']:.8f}° West"
            
            lat_surface = self.font_medium.render(lat_text, True, COLORS['text'])
            lon_surface = self.font_medium.render(lon_text, True, COLORS['text'])
            
            SCREEN.blit(lat_surface, (60, 95))
            SCREEN.blit(lon_surface, (60, 115))
            
            # Altitude and garden info
            alt_text = f"🏔️ {gps_data.get('altitude', 0):.1f}m • Garden Energy: {self.garden_energy:.2f}"
            alt_surface = self.font_small.render(alt_text, True, COLORS['accent'])
            SCREEN.blit(alt_surface, (60, 135))
        
        # Draw leaves first (background)
        for leaf in self.leaves:
            self.draw_leaf(SCREEN, leaf)
        
        # Draw flowers
        for flower in self.flowers:
            self.draw_flower(SCREEN, flower)
        
        # Draw sensor gardens with current readings
        if sensor_data:
            temp_flowers = [f for f in self.flowers if f['sensor_type'] == 0]
            hum_flowers = [f for f in self.flowers if f['sensor_type'] == 1] 
            press_flowers = [f for f in self.flowers if f['sensor_type'] == 2]
            
            self.draw_sensor_garden(SCREEN, 150, 300, temp_flowers, "🌡️ Temperature", 
                                  sensor_data.get('temperature', 22), "°C")
            self.draw_sensor_garden(SCREEN, 400, 320, hum_flowers, "💧 Humidity",
                                  sensor_data.get('humidity', 65), "%") 
            self.draw_sensor_garden(SCREEN, 650, 310, press_flowers, "🌪️ Pressure",
                                  sensor_data.get('pressure', 1013), " hPa")
        
        # Control button
        button_text = "⏸️ REST GARDEN" if self.recording else "▶️ GROW GARDEN"
        button_rect = pygame.Rect(300, 420, 200, 45)
        
        button_color = COLORS['flower2'] if self.recording else COLORS['accent']
        pygame.draw.rect(SCREEN, button_color, button_rect, border_radius=20)
        
        text_surface = self.font_medium.render(button_text, True, COLORS['bg'])
        text_rect = text_surface.get_rect(center=button_rect.center)
        SCREEN.blit(text_surface, text_rect)
        
        # Instructions
        inst = self.font_small.render("🌸 Flowers bloom bigger with higher sensor values • Changes create garden energy", True, COLORS['text'])
        SCREEN.blit(inst, (20, 450))
        
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
    gui = LivingGardenGUI()
    clock = pygame.time.Clock()
    running = True
    
    print("🌺 Living Garden Theme - Watch your sensor garden bloom and grow!")
    
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
        
        # Gradually change sample data for garden demo
        if gui.recording:
            sample_sensor['temperature'] += random.uniform(-0.3, 0.3)
            sample_sensor['humidity'] += random.uniform(-2, 2)
            sample_sensor['pressure'] += random.uniform(-1, 1)
            
            # Keep values in reasonable ranges
            sample_sensor['temperature'] = max(15, min(35, sample_sensor['temperature']))
            sample_sensor['humidity'] = max(30, min(90, sample_sensor['humidity']))
            sample_sensor['pressure'] = max(995, min(1030, sample_sensor['pressure']))
        
        button_rect = gui.render(sample_sensor, sample_gps, gui.recording)
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
