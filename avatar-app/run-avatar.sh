#!/bin/bash
# Wrapper to run Roboboogie avatar with correct Qt path
export QT_QPA_PLATFORM_PLUGIN_PATH=/opt/homebrew/Cellar/qt@5/5.15.18/plugins
cd /Users/Josh/clawd/avatar
python3 floating_avatar.py