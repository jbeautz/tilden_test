#!/usr/bin/env python3
"""
Cyber Nature Theme v2: Data Streams - Flowing river visualization with data currents
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

pygame.display.set_caption("Forest Monitor - Data Streams")

# Stream-inspired colors
COLORS = {
    'bg': (5, 15, 25),            # Deep water
    'water': (10, 30, 50),        # River bed
    'temp_stream': (255, 120, 80), # Warm current
    'hum_stream': (80, 180, 255),  # Cool current
    'press_stream': (120, 255, 120), # Pressure current
    'text': (200, 240, 255),      # Bright text
    'gps': (255, 215, 0),         # Gold coordinates
    'accent': (0, 255, 200),      # Cyan accent
}

class DataStreamsGUI:
    def __init__(self):
        self.font_title = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 26)
        self.font_medium = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 18)
        
        # Data streams (flowing particles)
        self.temp_particles = []
        self.hum_particles = []
        self.press_particles = []
        
        # Data history for stream intensity
        self.data_history = deque(maxlen=100)
        
        self.time = 0
        self.recording = False
        
        # Initialize particles
        self.init_particles()
    
    def init_particles(self):
        """Initialize flowing particles for each data stream"""
        # Temperature stream (top)
        for i in range(20):
            self.temp_particles.append({
                'x': random.randint(-50, WIDTH),
                'y': 180 + random.randint(-10, 10),
                'speed': random.uniform(1, 3),
                'size': random.randint(3, 8),
                'intensity': random.uniform(0.5, 1.0)
            })
        
        # Humidity stream (middle)
        for i in range(20):
            self.hum_particles.append({
                'x': random.randint(-50, WIDTH),
                'y': 230 + random.randint(-10, 10),
                'speed': random.uniform(1, 3),
                'size': random.randint(3, 8),
                'intensity': random.uniform(0.5, 1.0)
            })
        
        # Pressure stream (bottom)
        for i in range(20):
            self.press_particles.append({
                'x': random.randint(-50, WIDTH),
                'y': 280 + random.randint(-10, 10),
                'speed': random.uniform(1, 3),
                'size': random.randint(3, 8),
                'intensity': random.uniform(0.5, 1.0)
            })
    
    def update_particles(self, sensor_data):
        """Update particle flow based on sensor data"""
        # Update all particle streams
        for particles in [self.temp_particles, self.hum_particles, self.press_particles]:
            for particle in particles:
                particle['x'] += particle['speed']
                
                # Reset particle when it goes off screen
                if particle['x'] > WIDTH + 50:
                    particle['x'] = -50
                    particle['y'] += random.randint(-5, 5)
        
        # Adjust flow speed based on data changes
        if sensor_data and len(self.data_history) > 1:
            # Calculate data volatility to affect stream speed
            recent_temp = [d.get('temperature', 22) for d in list(self.data_history)[-10:]]
            if len(recent_temp) > 1:
                temp_volatility = max(recent_temp) - min(recent_temp)
                speed_multiplier = 1 + temp_volatility * 0.1
                
                for particle in self.temp_particles:
                    particle['speed'] = random.uniform(1, 3) * speed_multiplier
    
    def draw_stream(self, surface, particles, color, base_y, label):
        """Draw a flowing data stream"""
        # Stream background
        stream_rect = pygame.Rect(0, base_y - 15, WIDTH, 30)
        pygame.draw.rect(surface, COLORS['water'], stream_rect, border_radius=15)
        
        # Stream particles
        for particle in particles:
            # Particle with glow effect
            particle_color = tuple(int(c * particle['intensity']) for c in color)
            
            # Main particle
            pygame.draw.circle(surface, particle_color, 
                             (int(particle['x']), int(particle['y'])), 
                             particle['size'])
            
            # Glow trail
            for i in range(3):
                trail_x = particle['x'] - i * 5
                trail_size = max(1, particle['size'] - i)
                trail_alpha = particle['intensity'] * (1 - i * 0.3)
                trail_color = tuple(int(c * trail_alpha) for c in color)
                
                if trail_x > 0:
                    pygame.draw.circle(surface, trail_color, 
                                     (int(trail_x), int(particle['y'])), 
                                     trail_size)
        
        # Stream label
        label_surface = self.font_medium.render(label, True, color)
        surface.blit(label_surface, (10, base_y - 30))
    
    def draw_data_graph(self, surface, x, y, width, height, data_history, color, title):
        """Draw a mini real-time graph"""
        if len(data_history) < 2:
            return
        
        # Graph background
        graph_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, COLORS['water'], graph_rect, border_radius=5)
        pygame.draw.rect(surface, color, graph_rect, 2, border_radius=5)
        
        # Title
        title_surface = self.font_small.render(title, True, color)
        surface.blit(title_surface, (x + 5, y - 20))
        
        # Plot data
        data_list = list(data_history)[-width//4:]  # Last N points that fit
        if len(data_list) < 2:
            return
        
        min_val = min(data_list)
        max_val = max(data_list)
        
        if max_val == min_val:
            return
        
        # Draw line graph
        points = []
        for i, value in enumerate(data_list):
            normalized = (value - min_val) / (max_val - min_val)
            point_x = x + (i / len(data_list)) * width
            point_y = y + height - (normalized * height)
            points.append((point_x, point_y))
        
        if len(points) > 1:
            pygame.draw.lines(surface, color, False, points, 2)
        
        # Current value
        current_val = data_list[-1]
        val_text = f"{current_val:.1f}"
        val_surface = self.font_small.render(val_text, True, COLORS['text'])
        surface.blit(val_surface, (x + width - 40, y + height - 15))
    
    def render(self, sensor_data, gps_data, recording_status):
        self.recording = recording_status
        self.time += 0.1
        
        # Update data history
        if sensor_data:
            self.data_history.append(sensor_data)
        
        # Update particles
        self.update_particles(sensor_data)
        
        # Background gradient
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            bg_color = (
                int(COLORS['bg'][0] + (COLORS['water'][0] - COLORS['bg'][0]) * ratio),
                int(COLORS['bg'][1] + (COLORS['water'][1] - COLORS['bg'][1]) * ratio),
                int(COLORS['bg'][2] + (COLORS['water'][2] - COLORS['bg'][2]) * ratio)
            )
            pygame.draw.line(SCREEN, bg_color, (0, y), (WIDTH, y))
        
        # Title
        title = self.font_title.render("🌊 Data Streams Monitor", True, COLORS['accent'])
        title_rect = title.get_rect(center=(WIDTH // 2, 25))
        SCREEN.blit(title, title_rect)
        
        # Status
        status = "🟢 FLOWING" if self.recording else "⏸️ STILL"
        status_surface = self.font_medium.render(status, True, COLORS['accent'])
        SCREEN.blit(status_surface, (WIDTH - 120, 10))
        
        # GPS Display (very prominent)
        if gps_data and gps_data.get('latitude'):
            # GPS box
            gps_rect = pygame.Rect(50, 60, 350, 80)
            pygame.draw.rect(SCREEN, COLORS['water'], gps_rect, border_radius=10)
            pygame.draw.rect(SCREEN, COLORS['gps'], gps_rect, 3, border_radius=10)
            
            # GPS icon and title
            gps_title = self.font_large.render("🗺️ COORDINATES", True, COLORS['gps'])
            SCREEN.blit(gps_title, (60, 70))
            
            # Large, clear coordinates
            lat_text = f"{gps_data['latitude']:.7f}° N"
            lon_text = f"{gps_data['longitude']:.7f}° W"
            
            lat_surface = self.font_large.render(lat_text, True, COLORS['text'])
            lon_surface = self.font_large.render(lon_text, True, COLORS['text'])
            
            SCREEN.blit(lat_surface, (60, 95))
            SCREEN.blit(lon_surface, (60, 115))
            
            # Altitude
            if gps_data.get('altitude'):
                alt_text = f"📏 {gps_data['altitude']:.1f}m elevation"
                alt_surface = self.font_medium.render(alt_text, True, COLORS['accent'])
                SCREEN.blit(alt_surface, (270, 105))
        
        # Data streams
        self.draw_stream(SCREEN, self.temp_particles, COLORS['temp_stream'], 180, "🌡️ Temperature Flow")
        self.draw_stream(SCREEN, self.hum_particles, COLORS['hum_stream'], 230, "💧 Humidity Current")
        self.draw_stream(SCREEN, self.press_particles, COLORS['press_stream'], 280, "🌪️ Pressure Stream")
        
        # Mini graphs
        if len(self.data_history) > 1:
            temp_data = [d.get('temperature', 22) for d in self.data_history]
            hum_data = [d.get('humidity', 65) for d in self.data_history]
            press_data = [d.get('pressure', 1013) for d in self.data_history]
            
            self.draw_data_graph(SCREEN, 450, 160, 100, 40, temp_data, COLORS['temp_stream'], "Temp")
            self.draw_data_graph(SCREEN, 570, 160, 100, 40, hum_data, COLORS['hum_stream'], "Humidity")
            self.draw_data_graph(SCREEN, 690, 160, 100, 40, press_data, COLORS['press_stream'], "Pressure")
        
        # Control button
        button_text = "⏸️ STOP FLOW" if self.recording else "▶️ START FLOW"
        button_rect = pygame.Rect(320, 380, 160, 50)
        
        button_color = COLORS['temp_stream'] if self.recording else COLORS['accent']
        pygame.draw.rect(SCREEN, button_color, button_rect, border_radius=15)
        
        text_surface = self.font_medium.render(button_text, True, COLORS['bg'])
        text_rect = text_surface.get_rect(center=button_rect.center)
        SCREEN.blit(text_surface, text_rect)
        
        # Instructions
        inst = self.font_small.render("Data flows like streams - watch particles speed up when values change rapidly", True, COLORS['text'])
        SCREEN.blit(inst, (50, 450))
        
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
    gui = DataStreamsGUI()
    clock = pygame.time.Clock()
    running = True
    
    print("🌊 Data Streams Theme - Watch your data flow like rivers!")
    
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
        
        # Update sample data with more variation for demo
        if gui.recording:
            sample_sensor['temperature'] += random.uniform(-0.2, 0.2)
            sample_sensor['humidity'] += random.uniform(-1, 1)
            sample_sensor['pressure'] += random.uniform(-0.5, 0.5)
        
        button_rect = gui.render(sample_sensor, sample_gps, gui.recording)
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
