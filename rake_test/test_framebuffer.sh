#!/bin/bash
# Test GUI with explicit framebuffer settings

echo "🖥️ Testing GUI with framebuffer display..."

# Kill any existing instances first
pkill -f "python.*main.py" 2>/dev/null || true
sleep 1

# Set framebuffer environment variables
export SDL_VIDEODRIVER=fbcon
export SDL_FBDEV=/dev/fb0
export SDL_AUDIODRIVER=dummy
export SDL_NOMOUSE=1

# Add user to video group for framebuffer access
sudo usermod -a -G video maggi

# Test framebuffer write permissions
echo "📋 Checking framebuffer permissions:"
ls -la /dev/fb0
groups maggi | grep video || echo "User not in video group yet (logout/login needed)"

# Navigate to project
cd ~/tilden_test/rake_test
source .venv/bin/activate

echo "🚀 Starting GUI with framebuffer settings..."
echo "Environment:"
echo "  SDL_VIDEODRIVER=$SDL_VIDEODRIVER"
echo "  SDL_FBDEV=$SDL_FBDEV"
echo "  SDL_AUDIODRIVER=$SDL_AUDIODRIVER"
echo ""

# Run with framebuffer
python main.py
