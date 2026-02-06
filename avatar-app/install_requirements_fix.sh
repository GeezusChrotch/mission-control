#!/bin/bash
# Alternative installation script for macOS with Homebrew

echo "=== Roboboogie Avatar Installation ==="
echo ""
echo "Option 1: Install PyQt5 via Homebrew (recommended for macOS)"
echo "Option 2: Create virtual environment"
echo "Option 3: Run simple webserver version (no Python install needed)"
echo ""

echo "Enter choice (1-3): "
read choice

case $choice in
    1)
        echo "Installing via Homebrew..."
        if command -v brew &> /dev/null; then
            brew install pyqt@5
            echo "Making floating_avatar.py executable..."
            chmod +x floating_avatar.py
            echo "Installation complete!"
            echo "Run: python3 floating_avatar.py"
        else
            echo "Error: Homebrew not found!"
            echo "Install Homebrew from: https://brew.sh/"
            exit 1
        fi
        ;;
    2)
        echo "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install PyQt5 PyQtWebEngine
        chmod +x floating_avatar.py
        echo "Virtual environment created!"
        echo "To use:"
        echo "1. source venv/bin/activate"
        echo "2. python3 floating_avatar.py"
        ;;
    3)
        echo "Setting up simple webserver version..."
        echo "This version will run as a simple web page you can leave open"
        echo "It won't be a floating window but you can keep it in the background"
        
        # Create a simple HTML file with auto state changes
        cp index.html simple_avatar.html
        
        echo ""
        echo "Simple webserver version ready!"
        echo "Open: file:///Users/Josh/clawd/avatar/simple_avatar.html"
        echo "Or run a quick server: python3 -m http.server 8080"
        echo "Then visit: http://localhost:8080/simple_avatar.html"
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac