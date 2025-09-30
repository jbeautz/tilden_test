#!/usr/bin/env python3
"""
Cyber Nature GUI Theme - Bioluminescent forest meets digital world
Combines cyberpunk's bold neon colors with nature's organic shapes and cute imagery
"""

import pygame
import math
import random
import os
import time

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

pygame.display.set_caption("Rake Environmental Monitor - Cyber Nature Theme")

# Cyber Nature Color Palette - Bioluminescent and electric
COLORS = {
    'bg_dark': (8, 15, 25),           # Deep night forest
    'bg_mid': (15, 25, 35),           # Forest shadows
    'card_bg': (20, 35, 45),          # Tree bark with glow
    'accent_cyan': (0, 255, 200),     # Electric cyan glow
    'accent_pink': (255, 20, 147),    # Neon pink flowers
    'accent_green': (50, 255, 100),   # Bioluminescent green
    'accent_purple': (138, 43, 226),  # Digital purple
    'text_bright': (220, 255, 240),   # Bright mint text
    'text_glow': (100, 255, 180),     # Glowing text
    'warning': (255, 100, 50),        # Electric orange
    'good': (100, 255, 150),          # Healthy green glow
    'leaf_green': (34, 139, 34),      # Natural leaf
    'branch_brown': (101, 67, 33),    # Digital wood
}

class CyberNatureGUI:
    def __init__(self):
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Animation state
        self.time = 0
        self.particles = []
        self.leaves = []
        self.digital_vines = []
        
        # Initialize particles and elements
        self.init_cyber_nature_elements()
        
        # Recording state
        self.recording = False
    
    def init_cyber_nature_elements(self):
        """Initialize floating particles, leaves, and digital vines"""
        # Glowing particles (like fireflies/digital sprites)
        for _ in range(15):
            self.particles.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'dx': random.uniform(-0.5, 0.5),
                'dy': random.uniform(-0.5, 0.5),
                'size': random.randint(2, 4),
                'color': random.choice([COLORS['accent_cyan'], COLORS['accent_green'], COLORS['accent_pink']]),
                'pulse': random.uniform(0, math.pi * 2)
            })
        
        # Digital leaves
        for _ in range(8):
            self.leaves.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'rotation': random.uniform(0, math.pi * 2),
                'rot_speed': random.uniform(-0.02, 0.02),
                'drift_x': random.uniform(-0.3, 0.3),
                'drift_y': random.uniform(-0.2, 0.2),
                'size': random.randint(15, 25),
                'color': random.choice([COLORS['accent_green'], COLORS['leaf_green']])
            })
        
        # Digital vine circuits
        for _ in range(3):
            points = []
            start_x = random.randint(0, WIDTH // 4)
            start_y = random.randint(HEIGHT // 4, HEIGHT * 3 // 4)
            
            for i in range(6):
                points.append((
                    start_x + i * 40 + random.randint(-20, 20),
                    start_y + random.randint(-30, 30)
                ))
            
            self.digital_vines.append({
                'points': points,
                'glow_offset': random.uniform(0, math.pi * 2),
                'color': random.choice([COLORS['accent_cyan'], COLORS['accent_purple']])
            })
    
    def draw_glow_effect(self, surface, color, pos, radius, intensity=3):
        """Draw a glowing effect around a point"""
        for i in range(intensity):
            alpha = 255 // (i + 1)
            glow_color = (*color, alpha)
            glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, glow_color, (radius, radius), radius - i * 2)
            surface.blit(glow_surface, (pos[0] - radius, pos[1] - radius), special_flags=pygame.BLEND_ADD)
    
    def draw_digital_leaf(self, surface, x, y, size, rotation, color):
        """Draw a stylized digital leaf with circuit patterns"""
        # Create leaf surface
        leaf_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        
        # Main leaf shape (ellipse)
        pygame.draw.ellipse(leaf_surface, color, (size // 4, 0, size * 3 // 2, size * 2))
        
        # Digital vein pattern
        vein_color = tuple(min(255, c + 50) for c in color[:3])
        center_x, center_y = size, size
        
        # Main vein
        pygame.draw.line(leaf_surface, vein_color, (center_x, size // 4), (center_x, size * 7 // 4), 2)
        
        # Side veins
        for i in range(3):
            offset = size // 3 * i
            pygame.draw.line(leaf_surface, vein_color, 
                           (center_x, size // 2 + offset), 
                           (center_x - size // 3, size // 2 + offset + size // 6), 1)
            pygame.draw.line(leaf_surface, vein_color, 
                           (center_x, size // 2 + offset), 
                           (center_x + size // 3, size // 2 + offset + size // 6), 1)
        
        # Rotate the leaf
        rotated_leaf = pygame.transform.rotate(leaf_surface, math.degrees(rotation))
        rect = rotated_leaf.get_rect(center=(x, y))
        surface.blit(rotated_leaf, rect)
        
        # Add glow effect
        self.draw_glow_effect(surface, color, (x, y), size // 2)
    
    def draw_digital_vine(self, surface, points, color, glow_offset):
        """Draw a glowing digital vine with circuit-like patterns"""
        if len(points) < 2:
            return
        
        # Draw main vine line with glow
        for i in range(len(points) - 1):
            # Pulsing glow intensity
            glow_intensity = (math.sin(self.time * 2 + glow_offset) + 1) * 0.5
            
            # Draw glow
            for thickness in range(8, 0, -1):
                alpha = int(glow_intensity * 100 // thickness)
                glow_color = (*color, alpha)
                glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.line(glow_surface, glow_color, points[i], points[i + 1], thickness)
                surface.blit(glow_surface, (0, 0), special_flags=pygame.BLEND_ADD)
            
            # Main vine line
            pygame.draw.line(surface, color, points[i], points[i + 1], 2)
        
        # Add digital nodes at connection points
        for point in points:
            pygame.draw.circle(surface, color, point, 4)
            self.draw_glow_effect(surface, color, point, 8)
    
    def draw_cyber_card(self, surface, x, y, width, height, title, value, unit, color):
        """Draw a card with cyber-nature styling"""
        # Organic rounded rectangle with glow
        card_rect = pygame.Rect(x, y, width, height)
        
        # Glow effect
        self.draw_glow_effect(surface, color, (x + width // 2, y + height // 2), width // 2)
        
        # Main card with rounded corners (simulate with multiple rects)
        pygame.draw.rect(surface, COLORS['card_bg'], card_rect, border_radius=15)
        pygame.draw.rect(surface, color, card_rect, 3, border_radius=15)
        
        # Decorative corner elements (like leaves)
        corner_size = 8
        pygame.draw.circle(surface, color, (x + corner_size, y + corner_size), corner_size // 2)
        pygame.draw.circle(surface, color, (x + width - corner_size, y + corner_size), corner_size // 2)
        
        # Title with glow
        title_surface = self.font_small.render(title, True, COLORS['text_glow'])
        title_rect = title_surface.get_rect()
        surface.blit(title_surface, (x + 15, y + 10))
        
        # Value with larger glow text
        value_text = f"{value:.1f}{unit}"
        value_surface = self.font_medium.render(value_text, True, color)
        surface.blit(value_surface, (x + 15, y + 35))
        
        # Add small decorative circuit pattern
        circuit_y = y + height - 15
        for i in range(3):
            circuit_x = x + 15 + i * 20
            pygame.draw.circle(surface, color, (circuit_x, circuit_y), 2)
            if i < 2:
                pygame.draw.line(surface, color, (circuit_x + 2, circuit_y), (circuit_x + 18, circuit_y), 1)
    
    def draw_cyber_button(self, surface, x, y, width, height, text, is_active):
        """Draw a cyber-nature styled button"""
        button_rect = pygame.Rect(x, y, width, height)
        
        # Color based on state
        if is_active:
            bg_color = COLORS['accent_pink']
            border_color = COLORS['accent_cyan']
            text_color = COLORS['bg_dark']
        else:
            bg_color = COLORS['card_bg']
            border_color = COLORS['accent_green']
            text_color = COLORS['text_bright']
        
        # Pulsing glow for active state
        if is_active:
            glow_intensity = (math.sin(self.time * 4) + 1) * 0.5
            glow_size = int(20 + glow_intensity * 10)
            self.draw_glow_effect(surface, border_color, (x + width // 2, y + height // 2), glow_size)
        
        # Main button - organic rounded shape
        pygame.draw.rect(surface, bg_color, button_rect, border_radius=20)
        pygame.draw.rect(surface, border_color, button_rect, 3, border_radius=20)
        
        # Decorative vine-like pattern on button
        vine_points = [
            (x + 10, y + height // 2),
            (x + 25, y + height // 2 - 5),
            (x + 40, y + height // 2),
            (x + 55, y + height // 2 + 5)
        ]
        
        for i in range(len(vine_points) - 1):
            pygame.draw.line(surface, border_color, vine_points[i], vine_points[i + 1], 2)
        
        # Button text
        text_surface = self.font_medium.render(text, True, text_color)
        text_rect = text_surface.get_rect()
        text_x = x + width // 2 - text_rect.width // 2
        text_y = y + height // 2 - text_rect.height // 2
        surface.blit(text_surface, (text_x, text_y))
        
        return button_rect
    
    def update_animations(self, dt):
        """Update all animation elements"""
        self.time += dt
        
        # Update floating particles
        for particle in self.particles:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['pulse'] += 0.1
            
            # Wrap around screen
            if particle['x'] < 0:
                particle['x'] = WIDTH
            elif particle['x'] > WIDTH:
                particle['x'] = 0
            if particle['y'] < 0:
                particle['y'] = HEIGHT
            elif particle['y'] > HEIGHT:
                particle['y'] = 0
        
        # Update digital leaves
        for leaf in self.leaves:
            leaf['x'] += leaf['drift_x']
            leaf['y'] += leaf['drift_y']
            leaf['rotation'] += leaf['rot_speed']
            
            # Wrap around screen
            if leaf['x'] < -50:
                leaf['x'] = WIDTH + 50
            elif leaf['x'] > WIDTH + 50:
                leaf['x'] = -50
            if leaf['y'] < -50:
                leaf['y'] = HEIGHT + 50
            elif leaf['y'] > HEIGHT + 50:
                leaf['y'] = -50
    
    def draw_background_elements(self, surface):
        """Draw all background cyber-nature elements"""
        # Draw digital vines
        for vine in self.digital_vines:
            self.draw_digital_vine(surface, vine['points'], vine['color'], vine['glow_offset'])
        
        # Draw floating digital leaves
        for leaf in self.leaves:
            self.draw_digital_leaf(surface, int(leaf['x']), int(leaf['y']), 
                                 leaf['size'], leaf['rotation'], leaf['color'])
        
        # Draw glowing particles
        for particle in self.particles:
            # Pulsing effect
            pulse_size = particle['size'] + math.sin(particle['pulse']) * 2
            alpha = int(150 + math.sin(particle['pulse']) * 100)
            
            # Draw particle with glow
            self.draw_glow_effect(surface, particle['color'], 
                                (int(particle['x']), int(particle['y'])), int(pulse_size * 2))
            pygame.draw.circle(surface, particle['color'], 
                             (int(particle['x']), int(particle['y'])), int(pulse_size))
    
    def render(self, sensor_data, gps_data, recording_status):
        """Render the complete cyber-nature interface"""
        # Update recording state
        self.recording = recording_status
        
        # Fill background with gradient effect
        for y in range(HEIGHT):
            color_ratio = y / HEIGHT
            bg_color = (
                int(COLORS['bg_dark'][0] + (COLORS['bg_mid'][0] - COLORS['bg_dark'][0]) * color_ratio),
                int(COLORS['bg_dark'][1] + (COLORS['bg_mid'][1] - COLORS['bg_dark'][1]) * color_ratio),
                int(COLORS['bg_dark'][2] + (COLORS['bg_mid'][2] - COLORS['bg_dark'][2]) * color_ratio)
            )
            pygame.draw.line(SCREEN, bg_color, (0, y), (WIDTH, y))
        
        # Draw background elements
        self.draw_background_elements(SCREEN)
        
        # Title with cyber-nature styling
        title = self.font_large.render("🌿 CYBER FOREST MONITOR 🌿", True, COLORS['accent_cyan'])
        title_rect = title.get_rect()
        title_x = (WIDTH - title_rect.width) // 2
        SCREEN.blit(title, (title_x, 20))
        
        # Add glow to title
        self.draw_glow_effect(SCREEN, COLORS['accent_cyan'], (title_x + title_rect.width // 2, 35), 100)
        
        # Status indicator - like a glowing flower
        status_x, status_y = WIDTH - 80, 30
        status_color = COLORS['good'] if self.recording else COLORS['warning']
        
        # Flower petals (5 circles around center)
        for i in range(5):
            angle = i * (2 * math.pi / 5) + self.time * 2
            petal_x = status_x + math.cos(angle) * 15
            petal_y = status_y + math.sin(angle) * 15
            pygame.draw.circle(SCREEN, status_color, (int(petal_x), int(petal_y)), 8)
        
        # Center of flower
        pygame.draw.circle(SCREEN, COLORS['accent_pink'], (status_x, status_y), 10)
        self.draw_glow_effect(SCREEN, status_color, (status_x, status_y), 25)
        
        # Status text
        status_text = "ACTIVE" if self.recording else "READY"
        status_surface = self.font_small.render(status_text, True, COLORS['text_bright'])
        SCREEN.blit(status_surface, (status_x - 25, status_y + 25))
        
        # Sensor data cards with different cyber-nature colors
        if sensor_data:
            self.draw_cyber_card(SCREEN, 50, 120, 160, 80, "Temperature", 
                               sensor_data.get('temperature', 0), "°C", COLORS['accent_pink'])
            self.draw_cyber_card(SCREEN, 230, 120, 160, 80, "Humidity", 
                               sensor_data.get('humidity', 0), "%", COLORS['accent_cyan'])
            self.draw_cyber_card(SCREEN, 410, 120, 160, 80, "Pressure", 
                               sensor_data.get('pressure', 0), " hPa", COLORS['accent_green'])
            self.draw_cyber_card(SCREEN, 590, 120, 160, 80, "Air Quality", 
                               sensor_data.get('gas_resistance', 0) / 1000, "kΩ", COLORS['accent_purple'])
        
        # GPS data with nature-inspired icons
        if gps_data and gps_data.get('latitude') and gps_data.get('longitude'):
            gps_y = 230
            
            # Location pin with glow
            pin_x, pin_y = 70, gps_y + 20
            pygame.draw.circle(SCREEN, COLORS['accent_pink'], (pin_x, pin_y), 12)
            pygame.draw.circle(SCREEN, COLORS['accent_cyan'], (pin_x, pin_y), 6)
            self.draw_glow_effect(SCREEN, COLORS['accent_pink'], (pin_x, pin_y), 20)
            
            # GPS coordinates
            lat_text = f"🌍 Lat: {gps_data['latitude']:.6f}°"
            lon_text = f"🧭 Lon: {gps_data['longitude']:.6f}°"
            alt_text = f"⛰️  Alt: {gps_data.get('altitude', 0):.1f}m"
            
            lat_surface = self.font_small.render(lat_text, True, COLORS['text_glow'])
            lon_surface = self.font_small.render(lon_text, True, COLORS['text_glow'])
            alt_surface = self.font_small.render(alt_text, True, COLORS['text_glow'])
            
            SCREEN.blit(lat_surface, (110, gps_y))
            SCREEN.blit(lon_surface, (110, gps_y + 25))
            SCREEN.blit(alt_surface, (110, gps_y + 50))
        
        # Control button - cyber-nature hybrid
        button_text = "⏸️ PAUSE FOREST" if self.recording else "▶️ START FOREST"
        button_rect = self.draw_cyber_button(SCREEN, 550, 340, 180, 60, button_text, self.recording)
        
        # Instructions with nature emojis
        instructions = [
            "🌿 Touch screen or press SPACE to toggle recording",
            "🍃 ESC to exit the cyber forest",
            "✨ Watch the bioluminescent data flow"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = self.font_small.render(instruction, True, COLORS['text_glow'])
            SCREEN.blit(inst_surface, (50, 360 + i * 25))
        
        return button_rect

# Sample data for testing
sample_sensor = {
    'temperature': 22.5,
    'humidity': 65.2,
    'pressure': 1013.2,
    'gas_resistance': 85000
}

sample_gps = {
    'latitude': 37.7749,
    'longitude': -122.4194,
    'altitude': 52.3
}

# Main loop
if __name__ == "__main__":
    gui = CyberNatureGUI()
    clock = pygame.time.Clock()
    running = True
    
    print("🌿✨ Cyber Nature GUI Theme - Where technology meets nature! ✨🌿")
    
    while running:
        dt = clock.tick(30) / 1000.0  # Delta time in seconds
        
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
        
        # Update animations
        gui.update_animations(dt)
        
        # Render frame
        button_rect = gui.render(sample_sensor, sample_gps, gui.recording)
        
        pygame.display.flip()
    
    pygame.quit()
