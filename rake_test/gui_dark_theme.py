#!/usr/bin/env python3
"""
Modern Environmental Monitor GUI - Dark Theme
Sleek dark interface with blue accents and modern typography
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
pygame.display.set_caption("Environmental Monitor - Dark Theme")

# Dark Theme Color Palette
COLORS = {
    'bg': (20, 25, 35),           # Dark blue-gray background
    'panel': (35, 42, 55),        # Darker panel background
    'accent': (64, 156, 255),     # Bright blue accent
    'text_primary': (240, 245, 250),   # Light text
    'text_secondary': (160, 170, 185), # Muted text
    'success': (76, 217, 100),    # Green for success/recording
    'warning': (255, 149, 0),     # Orange for warnings
    'error': (255, 69, 58),       # Red for errors
    'graph_line': (64, 156, 255), # Blue graph line
    'graph_bg': (25, 30, 40),     # Graph background
    'border': (55, 65, 80),       # Subtle borders
}

class ModernDarkGUI:
    def __init__(self):
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
        
        self.recording = False
        self.history = deque(maxlen=120)
        
        # UI Layout
        self.left_panel_width = 300
        self.right_panel_width = WIDTH - self.left_panel_width
        
    def draw_gradient_rect(self, surface, color1, color2, rect):
        """Draw a vertical gradient rectangle"""
        for y in range(rect.height):
            ratio = y / rect.height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surface, (r, g, b), 
                           (rect.x, rect.y + y), (rect.x + rect.width, rect.y + y))
    
    def draw_rounded_rect(self, surface, color, rect, radius=10):
        """Draw a rounded rectangle"""
        pygame.draw.rect(surface, color, rect)
        # Simple rounded corners effect
        pygame.draw.circle(surface, color, (rect.x + radius, rect.y + radius), radius)
        pygame.draw.circle(surface, color, (rect.x + rect.width - radius, rect.y + radius), radius)
        pygame.draw.circle(surface, color, (rect.x + radius, rect.y + rect.height - radius), radius)
        pygame.draw.circle(surface, color, (rect.x + rect.width - radius, rect.y + rect.height - radius), radius)
    
    def draw_sensor_card(self, surface, x, y, width, height, title, value, unit, icon="●"):
        """Draw a modern sensor data card"""
        # Card background with subtle gradient
        card_rect = pygame.Rect(x, y, width, height)
        self.draw_gradient_rect(surface, COLORS['panel'], (45, 52, 65), card_rect)
        
        # Border
        pygame.draw.rect(surface, COLORS['border'], card_rect, 2)
        
        # Icon and title
        icon_text = self.font_medium.render(icon, True, COLORS['accent'])
        title_text = self.font_small.render(title, True, COLORS['text_secondary'])
        
        surface.blit(icon_text, (x + 15, y + 10))
        surface.blit(title_text, (x + 45, y + 15))
        
        # Value
        value_text = self.font_large.render(f"{value}", True, COLORS['text_primary'])
        unit_text = self.font_small.render(unit, True, COLORS['text_secondary'])
        
        surface.blit(value_text, (x + 15, y + 40))
        surface.blit(unit_text, (x + 15 + value_text.get_width() + 5, y + 55))
        
    def draw_status_indicator(self, surface, x, y, status, text):
        """Draw a status indicator with colored dot"""
        color = COLORS['success'] if status else COLORS['error']
        pygame.draw.circle(surface, color, (x, y), 6)
        status_text = self.font_small.render(text, True, COLORS['text_secondary'])
        surface.blit(status_text, (x + 15, y - 8))
    
    def draw_modern_graph(self, surface, x, y, width, height, data_points):
        """Draw a modern line graph with glow effect"""
        if len(data_points) < 2:
            return
            
        # Graph background
        graph_rect = pygame.Rect(x, y, width, height)
        self.draw_rounded_rect(surface, COLORS['graph_bg'], graph_rect, 8)
        
        # Grid lines
        for i in range(1, 5):
            grid_y = y + (height * i // 5)
            pygame.draw.line(surface, COLORS['border'], (x, grid_y), (x + width, grid_y), 1)
        
        # Data line with glow effect
        if len(data_points) > 1:
            points = []
            min_val = min(data_points)
            max_val = max(data_points)
            val_range = max_val - min_val if max_val > min_val else 1
            
            for i, val in enumerate(data_points):
                px = x + (i * width // len(data_points))
                py = y + height - int(((val - min_val) / val_range) * height)
                points.append((px, py))
            
            # Glow effect (multiple lines with decreasing opacity)
            for thickness in [5, 3, 1]:
                alpha = 50 if thickness == 5 else (100 if thickness == 3 else 255)
                temp_surf = pygame.Surface((width + 10, height + 10), pygame.SRCALPHA)
                if len(points) > 1:
                    pygame.draw.lines(temp_surf, (*COLORS['graph_line'], alpha), False, 
                                    [(p[0] - x + 5, p[1] - y + 5) for p in points], thickness)
                surface.blit(temp_surf, (x - 5, y - 5), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    def draw_control_button(self, surface, x, y, width, height, text, active=False):
        """Draw a modern control button"""
        color = COLORS['success'] if active else COLORS['accent']
        hover_color = (color[0] + 20, color[1] + 20, color[2] + 20)
        
        # Button background
        button_rect = pygame.Rect(x, y, width, height)
        self.draw_rounded_rect(surface, color, button_rect, 12)
        
        # Button text
        text_surface = self.font_medium.render(text, True, COLORS['text_primary'])
        text_rect = text_surface.get_rect(center=button_rect.center)
        surface.blit(text_surface, text_rect)
        
        return button_rect
    
    def render(self, sensor_data, gps_data, recording_status):
        """Render the complete modern dark GUI"""
        # Background gradient
        self.draw_gradient_rect(SCREEN, COLORS['bg'], (15, 20, 30), pygame.Rect(0, 0, WIDTH, HEIGHT))
        
        # Header
        header_text = self.font_large.render("Environmental Monitor", True, COLORS['text_primary'])
        SCREEN.blit(header_text, (20, 20))
        
        # Status indicators
        self.draw_status_indicator(SCREEN, 650, 35, sensor_data is not None, "BME680")
        self.draw_status_indicator(SCREEN, 720, 35, gps_data is not None, "GPS")
        
        # Left Panel - Sensor Cards
        if sensor_data:
            self.draw_sensor_card(SCREEN, 20, 80, 130, 90, "Temperature", f"{sensor_data.get('temperature', 0):.1f}", "°C", "🌡")
            self.draw_sensor_card(SCREEN, 160, 80, 130, 90, "Humidity", f"{sensor_data.get('humidity', 0):.1f}", "%", "💧")
            self.draw_sensor_card(SCREEN, 20, 180, 130, 90, "Pressure", f"{sensor_data.get('pressure', 0):.0f}", "hPa", "📊")
            self.draw_sensor_card(SCREEN, 160, 180, 130, 90, "Gas", f"{sensor_data.get('gas', 0):.0f}", "Ω", "🌪")
        
        # GPS Section
        if gps_data:
            gps_rect = pygame.Rect(20, 290, 270, 100)
            self.draw_rounded_rect(SCREEN, COLORS['panel'], gps_rect, 8)
            pygame.draw.rect(SCREEN, COLORS['border'], gps_rect, 2)
            
            gps_title = self.font_medium.render("📍 Location", True, COLORS['accent'])
            SCREEN.blit(gps_title, (35, 305))
            
            lat_text = self.font_small.render(f"Lat: {gps_data.get('latitude', 0):.4f}°", True, COLORS['text_primary'])
            lon_text = self.font_small.render(f"Lon: {gps_data.get('longitude', 0):.4f}°", True, COLORS['text_primary'])
            alt_text = self.font_small.render(f"Alt: {gps_data.get('altitude', 0):.1f}m", True, COLORS['text_primary'])
            
            SCREEN.blit(lat_text, (35, 330))
            SCREEN.blit(lon_text, (35, 350))
            SCREEN.blit(alt_text, (35, 370))
        
        # Right Panel - Graph
        if sensor_data and 'temperature' in sensor_data:
            self.history.append(sensor_data['temperature'])
        
        if len(self.history) > 1:
            self.draw_modern_graph(SCREEN, 320, 80, 460, 200, list(self.history))
            
            # Graph title
            graph_title = self.font_medium.render("Temperature Trend", True, COLORS['text_primary'])
            SCREEN.blit(graph_title, (320, 50))
        
        # Control Button
        button_text = "⏸ STOP RECORDING" if recording_status else "▶ START RECORDING"
        button_rect = self.draw_control_button(SCREEN, 320, 320, 200, 50, button_text, recording_status)
        
        # Footer
        footer_text = self.font_tiny.render("Tap to start/stop • Data logged to CSV", True, COLORS['text_secondary'])
        SCREEN.blit(footer_text, (20, HEIGHT - 25))
        
        return button_rect

# Test the dark theme
if __name__ == "__main__":
    gui = ModernDarkGUI()
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
