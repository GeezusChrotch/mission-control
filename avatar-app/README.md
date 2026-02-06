# Roboboogie Animated Avatar

This is a floating, always-on-top avatar that shows Roboboogie's current state:

## States
- **Idle**: Default green face, gentle pulsing antenna
- **Thinking**: Spinning pupils, searching for information
- **Working**: Orange pulsing antenna, actively processing
- **Excited**: Wider mouth, bigger eyes, blue pulsing antenna
- **Subagent**: Purple face with rotating antenna

## Setup

1. Run the installation script:
```bash
./install_requirements.sh
```

2. Start the floating avatar:
```bash
python3 floating_avatar.py
```

## Features

- **Frameless window**: No window borders or title bar
- **Always on top**: Stays above other windows
- **Draggable**: Click and drag to position anywhere on screen
- **Transparent background**: Only the avatar is visible
- **Automatic state detection**: Changes state based on Clawdbot's activity

## How It Works

The avatar automatically detects Clawdbot's state by:
1. Monitoring session files for recent modifications
2. Tracking activity timing to determine idle state
3. Transitioning between states based on detected activity

## Manual Testing

You can also view the static demo version:
```bash
open index.html
```

This version has buttons to manually switch between states.