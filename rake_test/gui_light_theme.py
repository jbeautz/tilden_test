#!/usr/bin/env python3
"""
Clean Light Theme GUI - Minimalist Design
Clean white interface with subtle shadows and green accents
"""
import os
import pygame
import math
from typing import Dict, Any, List
from collections import deque

# Set up display - auto-detect best driver
pygame.init()

WIDTH, HEIGHT = 800, 480

# Try different display drivers for compatibility
# Mac drivers first, then Pi drivers, then fallbacks
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
    # Fallback - let pygame choose
    os.environ.pop('SDL_VIDEODRIVER', None)
    pygame.display.init()
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Environmental Monitor - Light Theme")

# Light Theme Color Palette
COLORS = {
    'bg': (248, 250, 252),        # Very light gray background
    'panel': (255, 255, 255),     # Pure white panels
    'accent': (52, 199, 89),      # Fresh green accent
    'text_primary': (28, 28, 30), # Dark text
    'text_secondary': (99, 99, 102), # Gray text
    'success': (52, 199, 89),     # Green for recording
    'warning': (255, 149, 0),     # Orange for warnings
    'error': (255, 59, 48),       # Red for errors
    'graph_line': (52, 199, 89),  # Green graph line
    'graph_bg': (245, 245, 247),  # Light graph background
    'border': (229, 229, 234),    # Light borders
    'shadow': (0, 0, 0, 20),      # Subtle shadow
}

class CleanLightGUI:
    def __init__(self):
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
        
        self.recording = False
        self.history = deque(maxlen=120)
        
    def draw_shadow(self, surface, rect, offset=3):
        """Draw a subtle drop shadow"""
        shadow_rect = pygame.Rect(rect.x + offset, rect.y + offset, rect.width, rect.height)
        shadow_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 15))
        surface.blit(shadow_surf, shadow_rect)
    
    def draw_card(self, surface, x, y, width, height, title, value, unit, icon="●"):
        """Draw a clean card with shadow"""
        card_rect = pygame.Rect(x, y, width, height)
        
        # Shadow
        self.draw_shadow(surface, card_rect)
        
        # Card background
        pygame.draw.rect(surface, COLORS['panel'], card_rect)
        pygame.draw.rect(surface, COLORS['border'], card_rect, 1)
        
        # Icon (using colored circle)
        pygame.draw.circle(surface, COLORS['accent'], (x + 20, y + 20), 8)
        
        # Title
        title_text = self.font_small.render(title, True, COLORS['text_secondary'])
        surface.blit(title_text, (x + 35, y + 15))
        
        # Value
        value_text = self.font_large.render(f"{value}", True, COLORS['text_primary'])
        unit_text = self.font_small.render(unit, True, COLORS['text_secondary'])
        
        surface.blit(value_text, (x + 15, y + 40))
        surface.blit(unit_text, (x + 15 + value_text.get_width() + 5, y + 55))
    
    def draw_status_dot(self, surface, x, y, active, label):
        """Draw a status indicator dot"""
        color = COLORS['success'] if active else COLORS['error']
        pygame.draw.circle(surface, color, (x, y), 5)
        
        # White center for active status
        if active:
            pygame.draw.circle(surface, COLORS['panel'], (x, y), 2)
        
        label_text = self.font_small.render(label, True, COLORS['text_secondary'])
        surface.blit(label_text, (x + 15, y - 8))
    
    def draw_clean_graph(self, surface, x, y, width, height, data_points):
        """Draw a clean line graph"""
        if len(data_points) < 2:
            return
        
        graph_rect = pygame.Rect(x, y, width, height)
        
        # Shadow and background
        self.draw_shadow(surface, graph_rect)
        pygame.draw.rect(surface, COLORS['graph_bg'], graph_rect)
        pygame.draw.rect(surface, COLORS['border'], graph_rect, 1)
        
        # Grid lines (very subtle)
        for i in range(1, 5):
            grid_y = y + (height * i // 5)
            pygame.draw.line(surface, COLORS['border'], (x + 10, grid_y), (x + width - 10, grid_y), 1)
        
        # Data line
        if len(data_points) > 1:
            points = []
            min_val = min(data_points)
            max_val = max(data_points)
            val_range = max_val - min_val if max_val > min_val else 1
            
            for i, val in enumerate(data_points):
                px = x + 10 + ((i * (width - 20)) // len(data_points))
                py = y + height - 10 - int(((val - min_val) / val_range) * (height - 20))
                points.append((px, py))
            
            # Draw smooth line
            if len(points) > 1:
                pygame.draw.lines(surface, COLORS['graph_line'], False, points, 3)
                
                # Draw dots at data points
                for point in points[-10::2]:  # Show some dots
                    pygame.draw.circle(surface, COLORS['graph_line'], point, 4)
                    pygame.draw.circle(surface, COLORS['panel'], point, 2)
    
    def draw_button(self, surface, x, y, width, height, text, active=False):
        """Draw a clean button"""
        button_rect = pygame.Rect(x, y, width, height)
        
        # Shadow
        self.draw_shadow(surface, button_rect)
        
        # Button background
        bg_color = COLORS['success'] if active else COLORS['accent']
        pygame.draw.rect(surface, bg_color, button_rect)
        
        # Button text
        text_color = COLORS['panel']
        text_surface = self.font_medium.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        surface.blit(text_surface, text_rect)
        
        return button_rect
    
    def render(self, sensor_data, gps_data, recording_status):
        """Render the complete clean light GUI"""
        # Background
        SCREEN.fill(COLORS['bg'])
        
        # Header
        header_text = self.font_large.render("Environmental Monitor", True, COLORS['text_primary'])
        SCREEN.blit(header_text, (30, 30))
        
        # Status indicators
        self.draw_status_dot(SCREEN, 650, 45, sensor_data is not None, "BME680")
        self.draw_status_dot(SCREEN, 720, 45, gps_data is not None, "GPS")
        
        # Sensor Cards Grid
        if sensor_data:
            self.draw_card(SCREEN, 30, 90, 140, 90, "Temperature", f"{sensor_data.get('temperature', 0):.1f}", "°C")
            self.draw_card(SCREEN, 180, 90, 140, 90, "Humidity", f"{sensor_data.get('humidity', 0):.1f}", "%")
            self.draw_card(SCREEN, 330, 90, 140, 90, "Pressure", f"{sensor_data.get('pressure', 0):.0f}", "hPa")
            self.draw_card(SCREEN, 480, 90, 140, 90, "Gas Quality", f"{sensor_data.get('gas', 0):.0f}", "Ω")
        
        # GPS Card
        if gps_data:
            gps_rect = pygame.Rect(30, 200, 290, 120)
            self.draw_shadow(SCREEN, gps_rect)
            pygame.draw.rect(SCREEN, COLORS['panel'], gps_rect)
            pygame.draw.rect(SCREEN, COLORS['border'], gps_rect, 1)
            
            # GPS header
            pygame.draw.circle(SCREEN, COLORS['accent'], (50, 220), 8)
            gps_title = self.font_medium.render("Location", True, COLORS['text_primary'])
            SCREEN.blit(gps_title, (65, 213))
            
            # GPS data
            lat_text = self.font_small.render(f"Latitude: {gps_data.get('latitude', 0):.4f}°", True, COLORS['text_primary'])
            lon_text = self.font_small.render(f"Longitude: {gps_data.get('longitude', 0):.4f}°", True, COLORS['text_primary'])
            alt_text = self.font_small.render(f"Altitude: {gps_data.get('altitude', 0):.1f} m", True, COLORS['text_primary'])
            
            SCREEN.blit(lat_text, (45, 245))
            SCREEN.blit(lon_text, (45, 265))
            SCREEN.blit(alt_text, (45, 285))
        
        # Temperature History Graph
        if sensor_data and 'temperature' in sensor_data:
            self.history.append(sensor_data['temperature'])
        
        if len(self.history) > 1:
            # Graph title
            graph_title = self.font_medium.render("Temperature History", True, COLORS['text_primary'])
            SCREEN.blit(graph_title, (340, 205))
            
            self.draw_clean_graph(SCREEN, 340, 235, 430, 150, list(self.history))
        
        # Control Button
        button_text = "⏹ Stop Recording" if recording_status else "⏺ Start Recording"
        button_rect = self.draw_button(SCREEN, 30, 400, 180, 50, button_text, recording_status)
        
        # Recording indicator
        if recording_status:
            # Pulsing red dot
            pulse = int(50 + 30 * math.sin(pygame.time.get_ticks() * 0.01))
            pygame.draw.circle(SCREEN, (255, pulse, pulse), (230, 425), 8)
            rec_text = self.font_small.render("Recording...", True, COLORS['error'])
            SCREEN.blit(rec_text, (250, 420))
        
        # Footer
        footer_text = self.font_tiny.render("Touch controls • Auto-logging environmental data with GPS coordinates", True, COLORS['text_secondary'])
        SCREEN.blit(footer_text, (30, HEIGHT - 25))
        
        return button_rect

# Test the light theme
if __name__ == "__main__":
    gui = CleanLightGUI()
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
