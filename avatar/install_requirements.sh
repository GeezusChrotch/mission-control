#!/bin/bash
# Install required Python packages for the floating avatar

echo "Installing PyQt5 requirements..."
echo "Attempting to install with pipx (recommended for macOS)..."

# Check if pipx is installed
if command -v pipx &> /dev/null; then
    echo "Using pipx..."
    pipx install PyQt5 PyQtWebEngine
elif command -v brew &> /dev/null; then
    echo "Using Homebrew to install PyQt..."
    brew install pyqt@5
else
    echo "Using pip with --break-system-packages flag (use with caution)..."
    python3 -m pip install --break-system-packages PyQt5 PyQtWebEngine
fi

echo "Making floating_avatar.py executable..."
chmod +x floating_avatar.py

echo "Installation complete!"
echo "To run the avatar: python3 floating_avatar.py"