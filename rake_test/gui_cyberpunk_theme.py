#!/usr/bin/env python3
"""
Cyberpunk Neon Theme GUI - Futuristic Style
Dark background with bright neon accents and glowing effects
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
pygame.display.set_caption("Environmental Monitor - Cyberpunk Theme")

# Cyberpunk Neon Color Palette
COLORS = {
    'bg': (10, 10, 15),           # Deep dark background
    'panel': (20, 20, 30),        # Dark panels
    'neon_cyan': (0, 255, 255),   # Bright cyan
    'neon_pink': (255, 20, 147),  # Hot pink
    'neon_green': (57, 255, 20),  # Bright green
    'neon_purple': (138, 43, 226), # Purple
    'neon_orange': (255, 165, 0), # Orange
    'text_primary': (255, 255, 255), # White text
    'text_secondary': (150, 150, 200), # Light purple text
    'success': (57, 255, 20),     # Neon green
    'warning': (255, 165, 0),     # Neon orange
    'error': (255, 20, 147),      # Neon pink
    'graph_line': (0, 255, 255),  # Cyan graph
    'grid': (40, 40, 60),         # Dark grid
}

class CyberpunkGUI:
    def __init__(self):
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
        
        self.recording = False
        self.history = deque(maxlen=120)
        self.time_offset = 0
        
    def draw_glow_text(self, surface, text, font, color, x, y, glow_size=3):
        """Draw text with neon glow effect"""
        # Create glow layers
        for size in range(glow_size, 0, -1):
            glow_surf = font.render(text, True, (*color[:3], 100 // size))
            for dx in range(-size, size + 1):
                for dy in range(-size, size + 1):
                    if dx * dx + dy * dy <= size * size:
                        surface.blit(glow_surf, (x + dx, y + dy), special_flags=pygame.BLEND_ADD)
        
        # Main text
        text_surf = font.render(text, True, color)
        surface.blit(text_surf, (x, y))
        return text_surf.get_width()
    
    def draw_neon_rect(self, surface, color, rect, thickness=2):
        """Draw rectangle with neon glow effect"""
        # Outer glow
        for i in range(3, 0, -1):
            glow_rect = pygame.Rect(rect.x - i, rect.y - i, rect.width + 2*i, rect.height + 2*i)
            pygame.draw.rect(surface, (*color[:3], 50 // i), glow_rect, thickness + i)
        
        # Main border
        pygame.draw.rect(surface, color, rect, thickness)
    
    def draw_cyber_card(self, surface, x, y, width, height, title, value, unit, neon_color):
        """Draw a cyberpunk-style data card"""
        card_rect = pygame.Rect(x, y, width, height)
        
        # Card background
        pygame.draw.rect(surface, COLORS['panel'], card_rect)
        
        # Neon border with corners
        self.draw_neon_rect(surface, neon_color, card_rect, 2)
        
        # Corner decorations
        corner_size = 15
        pygame.draw.lines(surface, neon_color, False, [
            (x, y + corner_size), (x, y), (x + corner_size, y)
        ], 3)
        pygame.draw.lines(surface, neon_color, False, [
            (x + width - corner_size, y), (x + width, y), (x + width, y + corner_size)
        ], 3)
        
        # Title with glow
        self.draw_glow_text(surface, title, self.font_small, COLORS['text_secondary'], x + 10, y + 8)
        
        # Value with strong glow
        self.draw_glow_text(surface, f"{value}", self.font_large, neon_color, x + 10, y + 35, 4)
        
        # Unit
        unit_text = self.font_small.render(unit, True, COLORS['text_secondary'])
        surface.blit(unit_text, (x + 10, y + height - 25))
    
    def draw_hologram_effect(self, surface, rect):
        """Draw scanning line effect"""
        scan_y = int(rect.y + (rect.height * (0.5 + 0.4 * math.sin(pygame.time.get_ticks() * 0.005))))
        
        # Scanning line
        scan_color = (*COLORS['neon_cyan'][:3], 100)
        temp_surf = pygame.Surface((rect.width, 3), pygame.SRCALPHA)
        temp_surf.fill(scan_color)
        surface.blit(temp_surf, (rect.x, scan_y), special_flags=pygame.BLEND_ADD)
        
        # Grid overlay
        for i in range(0, rect.height, 20):
            alpha = 30
            pygame.draw.line(surface, (*COLORS['grid'][:3], alpha), 
                           (rect.x, rect.y + i), (rect.x + rect.width, rect.y + i))
    
    def draw_cyber_graph(self, surface, x, y, width, height, data_points):
        """Draw cyberpunk-style graph with effects"""
        if len(data_points) < 2:
            return
        
        graph_rect = pygame.Rect(x, y, width, height)
        
        # Background
        pygame.draw.rect(surface, COLORS['panel'], graph_rect)
        self.draw_neon_rect(surface, COLORS['neon_cyan'], graph_rect, 2)
        
        # Grid
        for i in range(1, 6):
            grid_y = y + (height * i // 6)
            pygame.draw.line(surface, COLORS['grid'], (x, grid_y), (x + width, grid_y))
        for i in range(1, 8):
            grid_x = x + (width * i // 8)
            pygame.draw.line(surface, COLORS['grid'], (grid_x, y), (grid_x, y + height))
        
        # Data visualization
        if len(data_points) > 1:
            points = []
            min_val = min(data_points)
            max_val = max(data_points)
            val_range = max_val - min_val if max_val > min_val else 1
            
            for i, val in enumerate(data_points):
                px = x + (i * width // len(data_points))
                py = y + height - int(((val - min_val) / val_range) * height)
                points.append((px, py))
            
            # Glow effect for line
            for thickness in [8, 5, 3, 1]:
                alpha = 50 if thickness == 8 else (100 if thickness == 5 else 255)
                temp_surf = pygame.Surface((width + 10, height + 10), pygame.SRCALPHA)
                if len(points) > 1:
                    pygame.draw.lines(temp_surf, (*COLORS['graph_line'][:3], alpha), False, 
                                    [(p[0] - x + 5, p[1] - y + 5) for p in points], thickness)
                surface.blit(temp_surf, (x - 5, y - 5), special_flags=pygame.BLEND_ADD)
            
            # Data points with pulse effect
            pulse = 1.0 + 0.3 * math.sin(pygame.time.get_ticks() * 0.01)
            for i, point in enumerate(points[-20::3]):  # Show subset of points
                radius = int(4 * pulse)
                pygame.draw.circle(surface, COLORS['neon_cyan'], point, radius)
                pygame.draw.circle(surface, COLORS['text_primary'], point, 2)
        
        # Hologram scanning effect
        self.draw_hologram_effect(surface, graph_rect)
    
    def draw_cyber_button(self, surface, x, y, width, height, text, active=False):
        """Draw cyberpunk-style button"""
        button_rect = pygame.Rect(x, y, width, height)
        
        # Button background
        bg_color = COLORS['panel']
        pygame.draw.rect(surface, bg_color, button_rect)
        
        # Animated border
        border_color = COLORS['neon_green'] if active else COLORS['neon_pink']
        self.draw_neon_rect(surface, border_color, button_rect, 3)
        
        # Corner brackets
        bracket_size = 12
        bracket_color = border_color
        
        # Top corners
        pygame.draw.lines(surface, bracket_color, False, [
            (x - 5, y + bracket_size), (x - 5, y - 5), (x + bracket_size, y - 5)
        ], 3)
        pygame.draw.lines(surface, bracket_color, False, [
            (x + width - bracket_size, y - 5), (x + width + 5, y - 5), (x + width + 5, y + bracket_size)
        ], 3)
        
        # Bottom corners
        pygame.draw.lines(surface, bracket_color, False, [
            (x - 5, y + height - bracket_size), (x - 5, y + height + 5), (x + bracket_size, y + height + 5)
        ], 3)
        pygame.draw.lines(surface, bracket_color, False, [
            (x + width - bracket_size, y + height + 5), (x + width + 5, y + height + 5), (x + width + 5, y + height - bracket_size)
        ], 3)
        
        # Button text with glow
        text_surface = self.font_medium.render(text, True, border_color)
        text_rect = text_surface.get_rect()
        text_x = x + width // 2 - text_rect.width // 2
        text_y = y + height // 2 - text_rect.height // 2
        self.draw_glow_text(surface, text, self.font_medium, border_color, text_x, text_y, 3)
        
        return button_rect
    
    def render(self, sensor_data, gps_data, recording_status):
        """Render the complete cyberpunk GUI"""
        # Animated background
        SCREEN.fill(COLORS['bg'])
        
        # Matrix-style background lines
        for i in range(0, WIDTH, 40):
            alpha = int(20 + 15 * math.sin(pygame.time.get_ticks() * 0.003 + i * 0.1))
            pygame.draw.line(SCREEN, (*COLORS['grid'][:3], alpha), (i, 0), (i, HEIGHT))
        
        # Header with glow
        header_width = self.draw_glow_text(SCREEN, "ENVIRONMENTAL", self.font_large, COLORS['neon_cyan'], 30, 20, 4)
        self.draw_glow_text(SCREEN, " MONITOR", self.font_large, COLORS['neon_pink'], 30 + header_width, 20, 4)
        
        # Current time display (top right)
        import datetime
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.draw_glow_text(SCREEN, current_time, self.font_medium, COLORS['neon_cyan'], 630, 20, 3)
        self.draw_glow_text(SCREEN, current_date, self.font_tiny, COLORS['text_secondary'], 640, 50)
        
        # System status
        status_y = 70
        self.draw_glow_text(SCREEN, "BME680:", self.font_small, COLORS['text_secondary'], 30, status_y)
        status_color = COLORS['neon_green'] if sensor_data and sensor_data.get('temperature') else COLORS['error']
        self.draw_glow_text(SCREEN, "ONLINE" if sensor_data and sensor_data.get('temperature') else "OFFLINE", self.font_small, status_color, 100, status_y)
        
        # GPS status
        has_gps = gps_data and gps_data.get('latitude') and gps_data.get('longitude')
        gps_color = COLORS['neon_green'] if has_gps else COLORS['error']
        self.draw_glow_text(SCREEN, "GPS:", self.font_small, COLORS['text_secondary'], 200, status_y)
        self.draw_glow_text(SCREEN, "LOCKED" if has_gps else "SEARCHING", self.font_small, gps_color, 240, status_y)
        
        # Sensor data cards
        if sensor_data:
            temp_val = sensor_data.get('temperature', 0) if sensor_data.get('temperature') is not None else 0
            hum_val = sensor_data.get('humidity', 0) if sensor_data.get('humidity') is not None else 0
            press_val = sensor_data.get('pressure', 0) if sensor_data.get('pressure') is not None else 0
            gas_val = sensor_data.get('gas', 0) if sensor_data.get('gas') is not None else 0
            
            self.draw_cyber_card(SCREEN, 30, 100, 120, 80, "TEMP", f"{temp_val:.1f}", "°C", COLORS['neon_orange'])
            self.draw_cyber_card(SCREEN, 160, 100, 120, 80, "HUMID", f"{hum_val:.0f}", "%", COLORS['neon_cyan'])
            self.draw_cyber_card(SCREEN, 290, 100, 120, 80, "PRESS", f"{press_val:.0f}", "hPa", COLORS['neon_purple'])
            self.draw_cyber_card(SCREEN, 420, 100, 120, 80, "VOC", f"{gas_val/1000:.1f}", "kΩ", COLORS['neon_green'])
        
        # GPS display
        if sensor_data and sensor_data.get('latitude') and sensor_data.get('longitude'):
            gps_rect = pygame.Rect(550, 100, 220, 80)
            pygame.draw.rect(SCREEN, COLORS['panel'], gps_rect)
            self.draw_neon_rect(SCREEN, COLORS['neon_pink'], gps_rect, 2)
            
            self.draw_glow_text(SCREEN, "COORDINATES", self.font_small, COLORS['neon_pink'], 560, 110)
            self.draw_glow_text(SCREEN, f"{sensor_data['latitude']:.5f}°", self.font_small, COLORS['text_primary'], 560, 130)
            self.draw_glow_text(SCREEN, f"{sensor_data['longitude']:.5f}°", self.font_small, COLORS['text_primary'], 560, 145)
            alt_val = sensor_data.get('altitude', 0) if sensor_data.get('altitude') is not None else 0
            self.draw_glow_text(SCREEN, f"ALT: {alt_val:.0f}m", self.font_small, COLORS['text_secondary'], 560, 160)
        
        # Graph section
        if sensor_data and 'temperature' in sensor_data:
            self.history.append(sensor_data['temperature'])
        
        if len(self.history) > 1:
            self.draw_glow_text(SCREEN, "THERMAL ANALYSIS", self.font_medium, COLORS['neon_cyan'], 30, 200)
            self.draw_cyber_graph(SCREEN, 30, 230, 500, 120, list(self.history))
        
        # Control interface
        button_text = "[STOP_REC]" if recording_status else "[START_REC]"
        button_rect = self.draw_cyber_button(SCREEN, 550, 230, 150, 50, button_text, recording_status)
        
        # Recording status
        if recording_status:
            pulse = int(100 + 155 * abs(math.sin(pygame.time.get_ticks() * 0.01)))
            rec_color = (255, pulse // 3, pulse // 3)
            self.draw_glow_text(SCREEN, "● REC", self.font_medium, rec_color, 550, 290, 5)
        
        # Data stream effect
        stream_y = 390
        self.draw_glow_text(SCREEN, "> DATA_STREAM_ACTIVE", self.font_tiny, COLORS['neon_green'], 30, stream_y)
        self.draw_glow_text(SCREEN, "> LOGGING_1HZ_CONTINUOUS", self.font_tiny, COLORS['neon_cyan'], 30, stream_y + 15)
        self.draw_glow_text(SCREEN, "> SENSORS_MONITORING", self.font_tiny, COLORS['neon_pink'], 30, stream_y + 30)
        
        # Update display
        pygame.display.flip()
        
        return button_rect

# Global display instance and compatibility interface for main.py
_gui = None
_recording = True

def init():
    """Initialize the cyberpunk display"""
    global _gui
    _gui = CyberpunkGUI()
    print("Cyberpunk Display initialized in continuous monitoring mode")

def set_continuous_mode():
    """Set display to continuous monitoring mode (always recording)"""
    global _recording
    _recording = True
    print("Continuous monitoring mode enabled")

def handle_events():
    """Handle pygame events"""
    actions = {'quit': False}
    
    if _gui and _gui != "DISABLED":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                actions['quit'] = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    actions['quit'] = True
    
    return actions

def render(sensor_data, history_data):
    """Render the display with current data - compatible with main.py"""
    if _gui and _gui != "DISABLED":
        # Merge sensor and GPS data (main.py passes them combined)
        _gui.render(sensor_data, sensor_data, _recording)

# Auto-initialize when imported (with error handling)
if _gui is None:
    try:
        init()
    except Exception as e:
        print(f"WARNING: Display initialization failed: {e}")
        print("Continuing without display (logging will still work)")
        _gui = "DISABLED"

# Test the cyberpunk theme
if __name__ == "__main__":
    gui = CyberpunkGUI()
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
