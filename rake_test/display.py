"""Interactive display using pygame with Start/Stop control and mini graphs.
Compatible with Mac (development) and Pi 800x480 DSI screen.
"""
import os
import pygame
from typing import Dict, Any, List

# Set up environment for Pi display access - KMSDRM works!
os.environ['SDL_VIDEODRIVER'] = 'kmsdrm'
os.environ['SDL_NOMOUSE'] = '1'

# Initialize pygame with multiple fallbacks
pygame.init()

WIDTH, HEIGHT = 800, 480
SCREEN = None
driver_used = None

# Try different display methods in order of preference - KMSDRM WORKS!
display_methods = [
    ("kmsdrm", {"SDL_VIDEODRIVER": "kmsdrm", "SDL_NOMOUSE": "1"}),  # WORKING! Modern DRM
    ("fbcon", {"SDL_VIDEODRIVER": "fbcon", "SDL_FBDEV": "/dev/fb0", "SDL_NOMOUSE": "1"}),  # Framebuffer fallback
    ("directfb", {"SDL_VIDEODRIVER": "directfb", "SDL_NOMOUSE": "1"}),  # DirectFB fallback
    ("x11", {"SDL_VIDEODRIVER": "x11", "DISPLAY": ":0"}),  # X11 if available  
    ("auto", {"SDL_NOMOUSE": "1"}),  # Let pygame choose
    ("dummy", {"SDL_VIDEODRIVER": "dummy"}),  # Headless fallback
]

for method_name, env_vars in display_methods:
    try:
        # Set environment variables for this method
        for key, value in env_vars.items():
            os.environ[key] = value
        
        # Reinitialize display subsystem
        if SCREEN:
            pygame.display.quit()
        pygame.display.init()
        
        SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
        driver_used = pygame.display.get_driver()
        print(f"Display initialized: {WIDTH}x{HEIGHT} (method: {method_name}, driver: {driver_used})")
        print(f"Display info: {pygame.display.get_surface()}")
        
        # Check if we got an invisible driver and reject it
        if driver_used in ['dummy', 'offscreen']:
            print(f"WARNING: Got invisible driver '{driver_used}', trying next method...")
            continue
        
        break
        
    except pygame.error as e:
        print(f"Display method '{method_name}' failed: {e}")
        continue

if not SCREEN:
    # Last resort - create dummy display
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.display.quit()
    pygame.display.init()
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
    print("Using dummy display as last resort - GUI will run but not be visible")
pygame.display.set_caption("Env + GPS Monitor")
FONT_MAIN = pygame.font.SysFont("monospace", 26)
FONT_BTN = pygame.font.SysFont("monospace", 30, bold=True)
BG = (5, 5, 5)
FG = (0, 255, 0)
BTN_IDLE = (40, 120, 40)
BTN_ACTIVE = (160, 40, 40)
BTN_TEXT = (255, 255, 255)
GRID = (40, 40, 40)
GRAPH_COLORS = {
    'temperature': (255, 140, 0),
    'humidity': (30, 144, 255),
    'pressure': (186, 85, 211)
}
BUTTON_RECT = pygame.Rect(WIDTH - 190, HEIGHT - 80, 170, 60)
HISTORY_KEYS = ['temperature', 'humidity', 'pressure']
MAX_POINTS = 120  # last N samples

class UIDisplay:
    def __init__(self):
        self.recording = False

    def toggle_recording(self):
        self.recording = not self.recording
        return self.recording

    def handle_events(self):
        """Process pygame events. Returns dict with actions."""
        actions = {"quit": False, "toggle_record": False}
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                actions["quit"] = True
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    actions["quit"] = True
                if event.key == pygame.K_SPACE:
                    actions["toggle_record"] = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if BUTTON_RECT.collidepoint(event.pos):
                    actions["toggle_record"] = True
        return actions

    def _draw_text_block(self, data: Dict[str, Any]):
        lines = []
        ordered = [
            'timestamp', 'temperature', 'humidity', 'pressure', 'gas',
            'latitude', 'longitude', 'altitude'
        ]
        for k in ordered:
            if k in data:
                v = data.get(k)
                if isinstance(v, float):
                    lines.append(f"{k}: {v:.3f}")
                else:
                    lines.append(f"{k}: {v if v is not None else '--'}")
        y = 10
        for line in lines[:12]:  # limit
            surf = FONT_MAIN.render(line, True, FG)
            SCREEN.blit(surf, (10, y))
            y += surf.get_height() + 4

    def _draw_button(self):
        color = BTN_ACTIVE if self.recording else BTN_IDLE
        pygame.draw.rect(SCREEN, color, BUTTON_RECT, border_radius=8)
        label = "STOP" if self.recording else "START"
        surf = FONT_BTN.render(label, True, BTN_TEXT)
        SCREEN.blit(surf, (BUTTON_RECT.x + (BUTTON_RECT.w - surf.get_width()) // 2,
                           BUTTON_RECT.y + (BUTTON_RECT.h - surf.get_height()) // 2))

    def _draw_graphs(self, history: Dict[str, List[float]]):
        # Graph area rectangle
        graph_rect = pygame.Rect(300, 10, WIDTH - 310, 250)
        pygame.draw.rect(SCREEN, (15, 15, 15), graph_rect)
        # Grid lines
        for i in range(6):
            y = graph_rect.y + i * graph_rect.height / 5
            pygame.draw.line(SCREEN, GRID, (graph_rect.x, y), (graph_rect.right, y), 1)
        for i in range(6):
            x = graph_rect.x + i * graph_rect.width / 5
            pygame.draw.line(SCREEN, GRID, (x, graph_rect.y), (x, graph_rect.bottom), 1)
        # Determine ranges per key
        legend_y = graph_rect.bottom + 5
        for key in HISTORY_KEYS:
            series = [v for v in history.get(key, []) if isinstance(v, (int, float))]
            if len(series) < 2:
                continue
            min_v = min(series)
            max_v = max(series)
            rng = (max_v - min_v) or 1.0
            scaled = [graph_rect.bottom - (v - min_v) / rng * graph_rect.height for v in series]
            step = graph_rect.width / (MAX_POINTS - 1 if MAX_POINTS > 1 else 1)
            points = [
                (graph_rect.x + idx * step, scaled[idx]) for idx in range(len(scaled))
            ]
            pygame.draw.lines(SCREEN, GRAPH_COLORS[key], False, points, 2)
            # Legend
            leg = FONT_MAIN.render(f"{key} ({min_v:.1f}-{max_v:.1f})", True, GRAPH_COLORS[key])
            SCREEN.blit(leg, (graph_rect.x, legend_y))
            legend_y += leg.get_height() + 2

    def render(self, data: Dict[str, Any], history: Dict[str, List[float]]):
        SCREEN.fill(BG)
        self._draw_text_block(data)
        self._draw_graphs(history)
        self._draw_button()
        pygame.display.flip()

# Convenience singleton
ui = UIDisplay()

def handle_events():
    return ui.handle_events()

def render(data, history):
    ui.render(data, history)

def is_recording():
    return ui.recording

def toggle_recording():
    return ui.toggle_recording()
