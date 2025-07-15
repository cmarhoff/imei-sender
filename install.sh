#!/bin/bash

set -e

APP_NAME="imei-sender"
APP_DIR="$HOME/$APP_NAME"
DESKTOP_FILE="$APP_DIR/imei-sender.desktop"
LAUNCHER_DIR="$HOME/.local/share/applications"
LAUNCHER_PATH="$LAUNCHER_DIR/imei-sender.desktop"

echo "🔧 Starting IMEI Sender installation..."

# Add user to 'uucp' group for modem access
echo "🔐 Adding user to 'uucp' group (required for modem access)..."
sudo usermod -aG uucp "$USER"
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
