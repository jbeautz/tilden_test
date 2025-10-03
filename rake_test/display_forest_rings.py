#!/usr/bin/env python3
"""
Forest Rings Display Module - Compatible with existing main.py
Replaces the original display.py with beautiful tree ring visualization
"""

import pygame
import math
import random
import os
import time
from collections import deque

# Try to import touch handler for dummy driver
try:
    import touch_handler
    TOUCH_HANDLER_AVAILABLE = True
except ImportError:
    TOUCH_HANDLER_AVAILABLE = False

# Global variables for display state
_screen = None
_gui = None
_recording = False
_clock = None

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

class ForestRingsDisplay:
    def __init__(self):
        # Set up display - Pi-optimized driver priority
        pygame.init()
        
        self.WIDTH, self.HEIGHT = 800, 480
        self.screen = None
        
        # Check if SDL driver already configured (e.g., by start_forest_rings.sh)
        if 'SDL_VIDEODRIVER' in os.environ:
            driver = os.environ['SDL_VIDEODRIVER']
            print(f"Forest Rings Display: Using pre-configured driver: {driver}")
            try:
                pygame.display.init()
                self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
                actual_driver = pygame.display.get_driver()
                print(f"SUCCESS: Display initialized with {actual_driver}")
            except Exception as e:
                print(f"Failed with pre-configured driver: {e}")
                print("Falling back to auto-detection...")
                os.environ.pop('SDL_VIDEODRIVER', None)
        
        # If no pre-configured driver or it failed, try auto-detection
        if self.screen is None:
            # Pi-first driver order (kmsdrm works best for DSI displays)
            display_drivers = ['kmsdrm', 'fbcon', 'directfb', 'x11', 'cocoa', 'dummy']
            
            print("Forest Rings Display: Trying display drivers for Pi...")
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
                    self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
                    
                    actual_driver = pygame.display.get_driver()
                    print(f"SUCCESS: Using display driver: {actual_driver}")
                    break
                    
                except pygame.error as e:
                    print(f"Failed {driver}: {e}")
                    continue
        
        if self.screen is None:
            print("All drivers failed - using pygame default")
            os.environ.pop('SDL_VIDEODRIVER', None)
            os.environ.pop('SDL_NOMOUSE', None)
            pygame.display.init()
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        
        pygame.display.set_caption("Soil Monitor - Growth Rings")
        
        # Initialize fonts
        self.font_title = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 28)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        
        # Data history for tree rings (last 50 readings)
        self.temp_history = deque(maxlen=50)
        self.humidity_history = deque(maxlen=50)
        self.pressure_history = deque(maxlen=50)
        
        # Initialize with some base values so rings show immediately
        self.temp_history.append(22.0)
        self.humidity_history.append(65.0)
        self.pressure_history.append(1013.0)
        
        self.time = 0
        self.recording = True  # Always recording in continuous mode
        
        # Clock for frame rate
        self.clock = pygame.time.Clock()
    
    def draw_tree_rings(self, surface, center_x, center_y, data_history, ring_color, current_value, unit, label, max_radius=70):
        """Draw tree rings with separate current reading display"""
        if len(data_history) < 1:
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
    
    def render_frame(self, sensor_data, history_data):
        """Render the complete forest rings interface"""
        self.time += 0.05
        
        # Always update data (continuous monitoring)
        if sensor_data:
            # Only update occasionally to see ring growth
            if int(self.time * 10) % 30 == 0:  # Every 3 seconds
                self.update_data(sensor_data)
        
        # Background gradient
        for y in range(self.HEIGHT):
            ratio = y / self.HEIGHT
            bg_color = (
                int(COLORS['bg'][0] + (COLORS['bg_light'][0] - COLORS['bg'][0]) * ratio),
                int(COLORS['bg'][1] + (COLORS['bg_light'][1] - COLORS['bg'][1]) * ratio),
                int(COLORS['bg'][2] + (COLORS['bg_light'][2] - COLORS['bg'][2]) * ratio)
            )
            pygame.draw.line(self.screen, bg_color, (0, y), (self.WIDTH, y))
        
        # Title
        title = self.font_title.render("Soil Monitor", True, COLORS['accent1'])
        title_rect = title.get_rect(center=(self.WIDTH // 2, 30))
        self.screen.blit(title, title_rect)
        
        # Status - Always monitoring
        status = "MONITORING"
        status_color = COLORS['accent1']
        status_surface = self.font_medium.render(status, True, status_color)
        self.screen.blit(status_surface, (self.WIDTH - 130, 10))
        
        # GPS Display (prominent and clean)
        gps_data = sensor_data
        if gps_data and gps_data.get('latitude') and gps_data.get('longitude'):
            gps_y = 70
            
            # GPS container
            gps_rect = pygame.Rect(40, gps_y - 5, 420, 80)
            pygame.draw.rect(self.screen, COLORS['card'], gps_rect, border_radius=10)
            pygame.draw.rect(self.screen, COLORS['gps'], gps_rect, 2, border_radius=10)
            
            # GPS Header
            gps_header = self.font_large.render("LOCATION", True, COLORS['gps'])
            self.screen.blit(gps_header, (50, gps_y + 5))
            
            # Coordinates (large and clear)
            lat_text = f"Lat: {gps_data['latitude']:.7f}°"
            lon_text = f"Lon: {gps_data['longitude']:.7f}°"
            alt_text = f"Alt: {gps_data.get('altitude', 0):.1f}m"
            
            lat_surface = self.font_medium.render(lat_text, True, COLORS['text'])
            lon_surface = self.font_medium.render(lon_text, True, COLORS['text'])
            alt_surface = self.font_small.render(alt_text, True, COLORS['accent3'])
            
            self.screen.blit(lat_surface, (50, gps_y + 25))
            self.screen.blit(lon_surface, (50, gps_y + 45))
            self.screen.blit(alt_surface, (350, gps_y + 35))
        
        # Tree Rings section
        rings_y = 180
        
        # Section title
        rings_title = self.font_large.render("Data Tree Rings", True, COLORS['text'])
        rings_title_rect = rings_title.get_rect(center=(self.WIDTH // 2, rings_y - 20))
        self.screen.blit(rings_title, rings_title_rect)
        
        # Get current sensor values for display
        current_temp = sensor_data.get('temperature', 22.0) if sensor_data else 22.0
        current_hum = sensor_data.get('humidity', 65.0) if sensor_data else 65.0
        current_press = sensor_data.get('pressure', 1013.0) if sensor_data else 1013.0
        
        # Draw tree rings with separate readings
        self.draw_tree_rings(self.screen, 150, rings_y + 40, self.temp_history, COLORS['ring_temp'], 
                           current_temp, "°C", "Temperature")
        self.draw_tree_rings(self.screen, 400, rings_y + 40, self.humidity_history, COLORS['ring_hum'],
                           current_hum, "%", "Humidity")
        self.draw_tree_rings(self.screen, 650, rings_y + 40, self.pressure_history, COLORS['ring_press'],
                           current_press, " hPa", "Pressure")
        
        # Instructions at bottom
        inst1 = self.font_small.render("Tree rings grow as sensor data changes over time", True, COLORS['text_dim'])
        inst2 = self.font_small.render("Continuously logging at 1 Hz until powered off", True, COLORS['text_dim'])
        
        inst1_rect = inst1.get_rect(center=(self.WIDTH // 2, 420))
        inst2_rect = inst2.get_rect(center=(self.WIDTH // 2, 445))
        
        self.screen.blit(inst1, inst1_rect)
        self.screen.blit(inst2, inst2_rect)
        
        # Update display
        pygame.display.flip()
        self.clock.tick(30)
        
        return None  # No button anymore

# Global display instance
_display = None
_recording = True  # Always recording in continuous mode

# Interface functions for main.py compatibility
def init():
    """Initialize the forest rings display"""
    global _display
    _display = ForestRingsDisplay()
    print("Forest Rings Display initialized in continuous monitoring mode")

def set_continuous_mode():
    """Set display to continuous monitoring mode (always recording)"""
    global _recording, _display
    _recording = True
    if _display:
        _display.recording = True
    print("Continuous monitoring mode enabled")

def handle_events():
    """Handle pygame events and return actions for main.py"""
    actions = {'quit': False}
    
    if _display and _display != "DISABLED":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                actions['quit'] = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    actions['quit'] = True
    
    return actions

def render(sensor_data, history_data):
    """Render the display with current data"""
    if _display and _display != "DISABLED":
        _display.render_frame(sensor_data, history_data)

# Auto-initialize when imported (with error handling)
if _display is None:
    try:
        init()
    except Exception as e:
        print(f"WARNING: Display initialization failed: {e}")
        print("Continuing without display (logging will still work)")
        _display = "DISABLED"  # Set to non-None to prevent re-init attempts
