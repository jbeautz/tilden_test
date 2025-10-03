#!/bin/bash
# Fix framebuffer permissions for pygame display access

echo "🔐 Fixing framebuffer permissions..."

# Check if user is in video group
if groups | grep -q video; then
    echo "✅ User already in video group"
else
    echo "➕ Adding user to video group..."
    sudo usermod -a -G video $USER
    echo "⚠️  You'll need to log out and back in for group change to take effect"
fi

# Set temporary permissions
echo "🔧 Setting temporary permissions on /dev/fb0..."
sudo chmod 666 /dev/fb0

# Create persistent udev rule
echo "📝 Creating persistent udev rule..."
sudo tee /etc/udev/rules.d/99-framebuffer.rules << 'EOF'
SUBSYSTEM=="graphics", KERNEL=="fb0", MODE="0666"
EOF

echo "♻️  Reloading udev rules..."
sudo udevadm control --reload-rules
sudo udevadm trigger

echo ""
echo "✅ Permissions fix complete!"
echo ""
echo "🧪 Test now with: python3 main.py"
echo "If still using dummy driver, try Option 2 (KMS fix)"
