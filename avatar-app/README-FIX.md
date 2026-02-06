# Fix for PyQt5 Installation on macOS

The Python installation is "externally managed" on macOS, which means you can't install packages system-wide. Here are your options:

## Option 1: Install via Homebrew (Easiest)
```bash
brew install pyqt@5
```

Then try running the avatar:
```bash
python3 floating_avatar.py
```

## Option 2: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install PyQt5
pip install PyQt5 PyQtWebEngine

# Run the avatar
python3 floating_avatar.py
```

## Option 3: Simple Webserver Version (No Python Install)
If you want something simpler that doesn't require PyQt5:
1. Run the quick fix script: `./install_requirements_fix.sh` and choose option 3
2. Then open `simple_avatar.html` in your browser
3. It will cycle through states automatically

## Alternative: Let me create a simpler Python version

Since PyQt5 can be tricky on macOS, I can create a simpler Tkinter version that doesn't need special installation:

```bash
# Try this alternative script instead
python3 simpler_avatar.py
```

I'll create that file for you now as a fallback option.