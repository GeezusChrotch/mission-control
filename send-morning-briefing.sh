#!/bin/bash
# Send morning briefing to Telegram

# Set PATH for cron
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin"

TODAY=$(date +"%Y-%m-%d")
BRIEFING_FILE="/tmp/morning-briefing-${TODAY}.txt"

if [ -f "$BRIEFING_FILE" ]; then
    # Read briefing content
    BRIEFING=$(cat "$BRIEFING_FILE")
    # Use clawdbot CLI to send
    /usr/local/bin/clawdbot message send --channel telegram --target 8527894183 --message "$BRIEFING"
    echo "Briefing sent at $(date)"
else
    echo "No briefing found for $TODAY"
fi
