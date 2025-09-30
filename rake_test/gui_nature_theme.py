#!/usr/bin/env python3
"""
Nature/Earth Theme GUI - Organic Design
Earth tones with nature-inspired colors and organic shapes
"""
import os
import pygame
import math
from typing import Dict, Any, List
from collections import deque

# Set up environment for Pi display
os.environ['SDL_VIDEODRIVER'] = 'kmsdrm'
os.environ['SDL_NOMOUSE'] = '1'

pygame.init()

WIDTH, HEIGHT = 800, 480
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Environmental Monitor - Nature Theme")

# Nature/Earth Color Palette
COLORS = {
    'bg': (245, 240, 230),        # Warm cream background
    'panel': (255, 252, 245),     # Off-white panels
    'earth_brown': (139, 69, 19), # Rich brown
    'forest_green': (34, 139, 34), # Forest green
    'sky_blue': (135, 206, 235),  # Sky blue
    'sunset_orange': (255, 140, 0), # Sunset orange
    'leaf_green': (124, 252, 0),  # Bright leaf green
    'bark_brown': (101, 67, 33),  # Tree bark
    'text_primary': (62, 39, 35), # Dark brown text
    'text_secondary': (139, 115, 85), # Medium brown
    'success': (34, 139, 34),     # Forest green
    'warning': (255, 140, 0),     # Orange
    'error': (178, 34, 34),       # Dark red
    'graph_line': (34, 139, 34),  # Green line
    'water_blue': (173, 216, 230), # Light blue
}

class NatureGUI:
    def __init__(self):
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
        
        self.recording = False
        self.history = deque(maxlen=120)
        
    def draw_organic_shape(self, surface, color, center, size, points=8):
        """Draw organic, leaf-like shapes"""
        cx, cy = center
        vertices = []
        for i in range(points):
            angle = (2 * math.pi * i) / points
            # Add some randomness for organic feel
            variation = 0.8 + 0.4 * math.sin(angle * 3)
            radius = size * variation
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            vertices.append((x, y))
        
        if len(vertices) > 2:
            pygame.draw.polygon(surface, color, vertices)
    
    def draw_wood_texture_rect(self, surface, color, rect):
        """Draw rectangle with wood-like texture"""
        pygame.draw.rect(surface, color, rect)
        
        # Add wood grain lines
        grain_color = (color[0] - 20, color[1] - 15, color[2] - 10)
        for i in range(0, rect.height, 8):
            y = rect.y + i
            # Wavy grain lines
            points = []
            for x in range(rect.x, rect.x + rect.width, 4):
                wave_y = y + 2 * math.sin((x - rect.x) * 0.02)
                points.append((x, wave_y))
            if len(points) > 1:
                pygame.draw.lines(surface, grain_color, False, points, 1)
    
    def draw_nature_card(self, surface, x, y, width, height, title, value, unit, icon_color):
        """Draw nature-themed data card"""
        card_rect = pygame.Rect(x, y, width, height)
        
        # Wooden card background
        self.draw_wood_texture_rect(surface, COLORS['panel'], card_rect)
        
        # Organic border
        pygame.draw.rect(surface, COLORS['bark_brown'], card_rect, 3)
        
        # Nature icon (organic circle)
        self.draw_organic_shape(surface, icon_color, (x + 25, y + 25), 12)
        
        # Title
        title_text = self.font_small.render(title, True, COLORS['text_secondary'])
        surface.blit(title_text, (x + 45, y + 18))
        
        # Value with nature styling
        value_text = self.font_large.render(f"{value}", True, COLORS['text_primary'])
        unit_text = self.font_small.render(unit, True, COLORS['text_secondary'])
        
        surface.blit(value_text, (x + 15, y + 45))
        surface.blit(unit_text, (x + 15 + value_text.get_width() + 5, y + 60))
        
        # Decorative leaf in corner
        leaf_points = [
            (x + width - 15, y + 10),
            (x + width - 8, y + 5),
            (x + width - 5, y + 12),
            (x + width - 12, y + 18)
        ]
        pygame.draw.polygon(surface, COLORS['leaf_green'], leaf_points)
    
    def draw_tree_status(self, surface, x, y, active, label):
        """Draw tree-like status indicator"""
        # Tree trunk
        trunk_color = COLORS['bark_brown']
        trunk_rect = pygame.Rect(x - 3, y + 5, 6, 8)
        pygame.draw.rect(surface, trunk_color, trunk_rect)
        
        # Tree crown
        crown_color = COLORS['forest_green'] if active else COLORS['text_secondary']
        self.draw_organic_shape(surface, crown_color, (x, y), 8, 6)
        
        # Label
        label_text = self.font_small.render(label, True, COLORS['text_secondary'])
        surface.blit(label_text, (x + 20, y - 8))
    
    def draw_nature_graph(self, surface, x, y, width, height, data_points):
        """Draw nature-themed graph like rolling hills"""
        if len(data_points) < 2:
            return
        
        graph_rect = pygame.Rect(x, y, width, height)
        
        # Sky background
        pygame.draw.rect(surface, COLORS['water_blue'], graph_rect)
        
        # Wooden frame
        pygame.draw.rect(surface, COLORS['bark_brown'], graph_rect, 4)
        
        # Ground line
        ground_y = y + height - 20
        pygame.draw.line(surface, COLORS['earth_brown'], (x, ground_y), (x + width, ground_y), 3)
        
        # Data visualization as rolling hills
        if len(data_points) > 1:
            points = [(x, ground_y)]  # Start at ground level
            
            min_val = min(data_points)
            max_val = max(data_points)
            val_range = max_val - min_val if max_val > min_val else 1
            
            for i, val in enumerate(data_points):
                px = x + (i * width // len(data_points))
                py = y + height - 20 - int(((val - min_val) / val_range) * (height - 40))
                points.append((px, py))
            
            points.append((x + width, ground_y))  # End at ground level
            
            # Fill area like hills
            if len(points) > 2:
                pygame.draw.polygon(surface, COLORS['forest_green'], points)
                
                # Add some trees on the hills
                for i in range(0, len(data_points), 10):
                    if i < len(points) - 2:
                        tree_x, tree_y = points[i + 1]
                        if tree_y < ground_y - 10:  # Only on higher hills
                            # Tree trunk
                            pygame.draw.line(surface, COLORS['bark_brown'], 
                                           (tree_x, tree_y), (tree_x, tree_y + 15), 3)
                            # Tree crown
                            self.draw_organic_shape(surface, COLORS['leaf_green'], 
                                                  (tree_x, tree_y - 5), 6, 5)
        
        # Sun in corner
        sun_center = (x + width - 30, y + 30)
        pygame.draw.circle(surface, COLORS['sunset_orange'], sun_center, 15)
        # Sun rays
        for angle in range(0, 360, 45):
            ray_end_x = sun_center[0] + 25 * math.cos(math.radians(angle))
            ray_end_y = sun_center[1] + 25 * math.sin(math.radians(angle))
            pygame.draw.line(surface, COLORS['sunset_orange'], sun_center, 
                           (ray_end_x, ray_end_y), 2)
    
    def draw_wooden_button(self, surface, x, y, width, height, text, active=False):
        """Draw wooden-style button"""
        button_rect = pygame.Rect(x, y, width, height)
        
        # Wooden background
        wood_color = COLORS['earth_brown'] if active else COLORS['bark_brown']
        self.draw_wood_texture_rect(surface, wood_color, button_rect)
        
        # Raised edge effect
        pygame.draw.rect(surface, COLORS['panel'], button_rect, 2)
        
        # Button text
        text_color = COLORS['panel']
        text_surface = self.font_medium.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        surface.blit(text_surface, text_rect)
        
        # Decorative corners
        corner_size = 8
        corner_color = COLORS['leaf_green']
        # Top left leaf
        leaf_tl = [(x, y + corner_size), (x, y), (x + corner_size, y)]
        pygame.draw.lines(surface, corner_color, False, leaf_tl, 2)
        # Bottom right leaf
        leaf_br = [(x + width - corner_size, y + height), (x + width, y + height), (x + width, y + height - corner_size)]
        pygame.draw.lines(surface, corner_color, False, leaf_br, 2)
        
        return button_rect
    
    def render(self, sensor_data, gps_data, recording_status):
        """Render the complete nature-themed GUI"""
        # Background gradient like sunrise
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(245 + 10 * ratio)
            g = int(240 + 15 * ratio)
            b = int(230 + 20 * ratio)
            pygame.draw.line(SCREEN, (r, g, b), (0, y), (WIDTH, y))
        
        # Header with nature styling
        header_text = self.font_large.render("🌿 Environmental Monitor", True, COLORS['text_primary'])
        SCREEN.blit(header_text, (30, 25))
        
        # Status trees
        self.draw_tree_status(SCREEN, 650, 40, sensor_data is not None, "BME680")
        self.draw_tree_status(SCREEN, 720, 40, gps_data is not None, "GPS")
        
        # Sensor cards with nature themes
        if sensor_data:
            self.draw_nature_card(SCREEN, 30, 90, 140, 85, "Temperature", f"{sensor_data.get('temperature', 0):.1f}", "°C", COLORS['sunset_orange'])
            self.draw_nature_card(SCREEN, 180, 90, 140, 85, "Humidity", f"{sensor_data.get('humidity', 0):.1f}", "%", COLORS['water_blue'])
            self.draw_nature_card(SCREEN, 330, 90, 140, 85, "Pressure", f"{sensor_data.get('pressure', 0):.0f}", "hPa", COLORS['sky_blue'])
            self.draw_nature_card(SCREEN, 480, 90, 140, 85, "Air Quality", f"{sensor_data.get('gas', 0):.0f}", "Ω", COLORS['leaf_green'])
        
        # GPS section styled like a compass
        if gps_data:
            compass_rect = pygame.Rect(30, 195, 280, 110)
            self.draw_wood_texture_rect(SCREEN, COLORS['panel'], compass_rect)
            pygame.draw.rect(SCREEN, COLORS['bark_brown'], compass_rect, 3)
            
            # Compass rose decoration
            center = (80, 250)
            pygame.draw.circle(SCREEN, COLORS['earth_brown'], center, 25, 3)
            # Cardinal directions
            pygame.draw.line(SCREEN, COLORS['earth_brown'], (center[0], center[1] - 20), (center[0], center[1] - 30), 2)  # N
            pygame.draw.line(SCREEN, COLORS['earth_brown'], (center[0] + 20, center[1]), (center[0] + 30, center[1]), 2)  # E
            
            # Compass title
            compass_title = self.font_medium.render("🧭 Location", True, COLORS['text_primary'])
            SCREEN.blit(compass_title, (120, 210))
            
            # GPS coordinates
            lat_text = self.font_small.render(f"Latitude: {gps_data.get('latitude', 0):.4f}°", True, COLORS['text_primary'])
            lon_text = self.font_small.render(f"Longitude: {gps_data.get('longitude', 0):.4f}°", True, COLORS['text_primary'])
            alt_text = self.font_small.render(f"Elevation: {gps_data.get('altitude', 0):.1f} m", True, COLORS['text_primary'])
            
            SCREEN.blit(lat_text, (120, 235))
            SCREEN.blit(lon_text, (120, 255))
            SCREEN.blit(alt_text, (120, 275))
        
        # Nature graph
        if sensor_data and 'temperature' in sensor_data:
            self.history.append(sensor_data['temperature'])
        
        if len(self.history) > 1:
            # Graph title
            graph_title = self.font_medium.render("🌡️ Temperature Landscape", True, COLORS['text_primary'])
            SCREEN.blit(graph_title, (330, 200))
            
            self.draw_nature_graph(SCREEN, 330, 230, 440, 140, list(self.history))
        
        # Wooden control button
        button_text = "🛑 Stop Recording" if recording_status else "🌱 Start Recording"
        button_rect = self.draw_wooden_button(SCREEN, 30, 400, 200, 50, button_text, recording_status)
        
        # Recording indicator like growing plant
        if recording_status:
            # Animated growing plant
            growth = 1.0 + 0.3 * math.sin(pygame.time.get_ticks() * 0.005)
            plant_x, plant_y = 250, 425
            
            # Stem
            pygame.draw.line(SCREEN, COLORS['forest_green'], 
                           (plant_x, plant_y + 15), (plant_x, plant_y - int(10 * growth)), 3)
            # Leaves
            leaf_size = int(6 * growth)
            self.draw_organic_shape(SCREEN, COLORS['leaf_green'], 
                                  (plant_x - 8, plant_y - int(5 * growth)), leaf_size, 4)
            self.draw_organic_shape(SCREEN, COLORS['leaf_green'], 
                                  (plant_x + 8, plant_y - int(8 * growth)), leaf_size, 4)
            
            # Status text
            rec_text = self.font_small.render("Growing data...", True, COLORS['forest_green'])
            SCREEN.blit(rec_text, (270, 415))
        
        # Footer with nature elements
        footer_text = self.font_tiny.render("🌍 Monitoring our environment • Preserving nature's data", True, COLORS['text_secondary'])
        SCREEN.blit(footer_text, (30, HEIGHT - 25))
        
        # Small decorative elements
        # Butterflies or leaves floating
        for i in range(3):
            x = 700 + 20 * math.sin(pygame.time.get_ticks() * 0.002 + i)
            y = 350 + i * 30 + 10 * math.cos(pygame.time.get_ticks() * 0.003 + i)
            self.draw_organic_shape(SCREEN, COLORS['leaf_green'], (x, y), 4, 4)
        
        return button_rect

# Test the nature theme
if __name__ == "__main__":
    gui = NatureGUI()
    clock = pygame.time.Clock()
    running = True
    
    # Sample data for demo
    sample_sensor = {'temperature': 23.5, 'humidity': 65.2, 'pressure': 1013, 'gas': 50000}
    sample_gps = {'latitude': 37.8776, 'longitude': -122.2664, 'altitude': 87.1}
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        button_rect = gui.render(sample_sensor, sample_gps, gui.recording)
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
