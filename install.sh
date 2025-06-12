#!/bin/bash

set -e

APP_NAME="imei-sender"
APP_DIR="$HOME/$APP_NAME"
DESKTOP_FILE="$APP_DIR/imei-sender.desktop"
LAUNCHER_DIR="$HOME/.local/share/applications"
LAUNCHER_PATH="$LAUNCHER_DIR/imei-sender.desktop"

echo "🔧 Starting IMEI Sender installation..."

# Install dependencies
echo "📦 Installing required packages (Python GTK bindings)..."
sudo apt update
sudo apt install -y python3-gi gir1.2-gtk-3.0

# Add user to 'dialout' group for modem access
echo "🔐 Adding user to 'dialout' group (required for modem access)..."
sudo usermod -aG dialout "$USER"
echo "👉 Please log out and back in for group changes to take effect."

# Make launch script executable
chmod +x "$APP_DIR/run.sh"

# Create and install desktop launcher
echo "📁 Creating desktop launcher..."
mkdir -p "$LAUNCHER_DIR"
sed "s|Exec=.*|Exec=$APP_DIR/run.sh|" "$DESKTOP_FILE" > "$LAUNCHER_PATH"

echo "✅ Installation complete!"
echo "💡 You can launch the app from your application menu or run:"
echo "$APP_DIR/run.sh"
