#!/bin/bash
# Comprehensive touch screen diagnostic and fix for Raspberry Pi DSI display

echo "🔍 TOUCH SCREEN DIAGNOSTIC"
echo "=========================="
echo ""

# Step 1: Check touch input devices
echo "📋 Step 1: Checking input devices..."
echo ""
ls -la /dev/input/event* 2>/dev/null
echo ""

# Check for touch devices
echo "Touch input devices:"
for device in /dev/input/event*; do
    if [ -e "$device" ]; then
        echo "  $device:"
        sudo evtest --query "$device" EV_ABS ABS_X 2>/dev/null && echo "    ✅ Has touch X axis" || true
        sudo evtest --query "$device" EV_ABS ABS_Y 2>/dev/null && echo "    ✅ Has touch Y axis" || true
    fi
done
echo ""

# Step 2: Check permissions
echo "📋 Step 2: Checking input device permissions..."
ls -la /dev/input/event* /dev/input/mice /dev/input/mouse* 2>/dev/null
echo ""
echo "Current user groups:"
groups
echo ""

# Step 3: Test pygame input detection
echo "📋 Step 3: Testing pygame touch/mouse detection..."
python3 << 'PYEOF'
import pygame
import sys

pygame.init()

# Get current display driver
driver = pygame.display.get_driver()
print(f"Display driver: {driver}")

# Check for input devices
print(f"\nJoysticks (touch devices): {pygame.joystick.get_count()}")

# List all event types pygame can see
screen = pygame.display.set_mode((100, 100))
print("\nPygame event types available:")
print(f"  MOUSEMOTION: {pygame.MOUSEMOTION}")
print(f"  MOUSEBUTTONDOWN: {pygame.MOUSEBUTTONDOWN}")
print(f"  MOUSEBUTTONUP: {pygame.MOUSEBUTTONUP}")
print(f"  FINGERDOWN: {pygame.FINGERDOWN if hasattr(pygame, 'FINGERDOWN') else 'Not available'}")
print(f"  FINGERUP: {pygame.FINGERUP if hasattr(pygame, 'FINGERUP') else 'Not available'}")
print(f"  FINGERMOTION: {pygame.FINGERMOTION if hasattr(pygame, 'FINGERMOTION') else 'Not available'}")

pygame.quit()
PYEOF
echo ""

# Step 4: Check SDL environment variables
echo "📋 Step 4: Checking SDL input configuration..."
echo "Current SDL environment variables:"
env | grep SDL || echo "  (none set)"
echo ""

# Step 5: Test raw touch input
echo "📋 Step 5: Testing raw touch input (5 seconds)..."
echo "Touch the screen now..."
timeout 5 sudo evtest /dev/input/event0 2>/dev/null | head -20 || echo "  No input detected"
echo ""

# Step 6: Recommendations
echo "🔧 TOUCH SCREEN FIX OPTIONS:"
echo "============================"
echo ""

# Create fix script 1: Input device permissions
cat > fix_touch_permissions.sh << 'FIXEOF1'
#!/bin/bash
echo "🔧 Fixing input device permissions..."

# Add user to input group
sudo usermod -a -G input $USER

# Create udev rule for input devices
sudo tee /etc/udev/rules.d/99-input.rules > /dev/null << 'EOF'
# Input device permissions
SUBSYSTEM=="input", MODE="0666", GROUP="input"
KERNEL=="event*", SUBSYSTEM=="input", MODE="0666", GROUP="input"
KERNEL=="mice", MODE="0666", GROUP="input"
KERNEL=="mouse*", MODE="0666", GROUP="input"
EOF

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Set immediate permissions
sudo chmod 666 /dev/input/event* /dev/input/mice /dev/input/mouse* 2>/dev/null

echo "✅ Input permissions configured"
echo "✅ Added user to input group"
echo "ℹ️  Log out and back in for group changes to take effect"
FIXEOF1
chmod +x fix_touch_permissions.sh

# Create fix script 2: SDL input configuration
cat > fix_touch_sdl.sh << 'FIXEOF2'
#!/bin/bash
echo "🔧 Configuring SDL for touch input..."

# Create SDL configuration for touch
cat > start_with_touch.sh << 'STARTEOF'
#!/bin/bash
# Start Forest Rings with touch input enabled

# Enable touch input in SDL
export SDL_VIDEODRIVER=kmsdrm
export SDL_FBDEV=/dev/fb0

# Try different mouse/touch modes
export SDL_MOUSEDRV=TSLIB
export SDL_MOUSEDEV=/dev/input/event0

# Enable debug for troubleshooting (optional)
# export SDL_DEBUG=1

cd ~/tilden_test/rake_test
python3 main.py "$@"
STARTEOF

chmod +x start_with_touch.sh

echo "✅ Created start_with_touch.sh"
echo ""
echo "To run with touch support:"
echo "  ./start_with_touch.sh"
FIXEOF2
chmod +x fix_touch_sdl.sh

# Create fix script 3: Test touch with pygame
cat > test_touch_pygame.sh << 'FIXEOF3'
#!/bin/bash
echo "🧪 Testing touch input with pygame..."

python3 << 'PYTESTEOF'
import pygame
import sys
import os

# Set up display
os.environ['SDL_VIDEODRIVER'] = 'kmsdrm'
os.environ['SDL_FBDEV'] = '/dev/fb0'

pygame.init()
screen = pygame.display.set_mode((800, 480))
pygame.display.set_caption("Touch Test")

# Fill screen with colors
screen.fill((50, 50, 50))
font = pygame.font.Font(None, 36)
text = font.render("Touch anywhere on screen", True, (255, 255, 255))
screen.blit(text, (200, 220))
pygame.display.flip()

print("\n🧪 Touch Test Running...")
print("Touch the screen - events will appear below")
print("Press Ctrl+C to exit\n")

clock = pygame.time.Clock()
running = True
touch_count = 0

try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                touch_count += 1
                print(f"✅ TOUCH #{touch_count}: MOUSEBUTTONDOWN at {event.pos}")
                # Draw a circle where touched
                pygame.draw.circle(screen, (0, 255, 0), event.pos, 20)
                pygame.display.flip()
            elif event.type == pygame.MOUSEBUTTONUP:
                print(f"   TOUCH #{touch_count}: MOUSEBUTTONUP at {event.pos}")
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:  # Left button pressed
                    print(f"   TOUCH #{touch_count}: MOTION at {event.pos}")
                    pygame.draw.circle(screen, (255, 255, 0), event.pos, 5)
                    pygame.display.flip()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False
        
        clock.tick(60)
except KeyboardInterrupt:
    print("\n\nTest interrupted")

pygame.quit()
print(f"\n✅ Touch test complete - detected {touch_count} touches")
PYTESTEOF
FIXEOF3
chmod +x test_touch_pygame.sh

echo ""
echo "💡 Option 1: Fix input permissions (recommended first)"
echo "   Run: ./fix_touch_permissions.sh"
echo "   Then log out and back in"
echo ""
echo "💡 Option 2: Configure SDL for touch input"
echo "   Run: ./fix_touch_sdl.sh"
echo "   Then use: ./start_with_touch.sh"
echo ""
echo "💡 Option 3: Test touch input detection"
echo "   Run: ./test_touch_pygame.sh"
echo "   This will show if touch is being detected"
echo ""
echo "📝 Created fix scripts:"
echo "   ✅ fix_touch_permissions.sh"
echo "   ✅ fix_touch_sdl.sh"
echo "   ✅ test_touch_pygame.sh"
