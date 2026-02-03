#!/bin/bash

# ElevenLabs Sound Effects Generator using curl
# Usage: ./generate-sound-effect.sh "prompt" output_filename.mp3 [duration]

if [ $# -lt 2 ]; then
    echo "Usage: $0 'prompt' output_filename.mp3 [duration_seconds]"
    echo "Example: $0 'train whistle' train_whistle.mp3 3.0"
    exit 1
fi

PROMPT="$1"
OUTPUT_FILE="$2"
DURATION="$3"
# API Key - require env var
API_KEY="${ELEVENLABS_API_KEY}"
if [ -z "$API_KEY" ]; then
    echo "❌ ELEVENLABS_API_KEY environment variable not set"
    echo "   Set it with: export ELEVENLABS_API_KEY='your-api-key'"
    exit 1
fi
DOWNLOADS_DIR="/Users/Josh/Library/CloudStorage/Dropbox/- LMT Audio/- Generated SFX"
OUTPUT_PATH="$DOWNLOADS_DIR/$OUTPUT_FILE"

# Ensure downloads directory exists
mkdir -p "$DOWNLOADS_DIR"

echo "🎵 Generating sound effect..."
echo "   Prompt: $PROMPT"
echo "   Output: $OUTPUT_FILE"

# Build JSON payload
if [ -n "$DURATION" ]; then
    JSON_PAYLOAD=$(cat <<EOF
{
    "text": "$PROMPT",
    "model_id": "eleven_text_to_sound_v2",
    "prompt_influence": 0.3,
    "duration_seconds": $DURATION
}
EOF
)
    echo "   Duration: $DURATION seconds"
else
    JSON_PAYLOAD=$(cat <<EOF
{
    "text": "$PROMPT",
    "model_id": "eleven_text_to_sound_v2",
    "prompt_influence": 0.3
}
EOF
)
    echo "   Duration: auto"
fi

# Make API request
curl -X POST "https://api.elevenlabs.io/v1/sound-generation" \
     -H "Accept: audio/mpeg" \
     -H "Content-Type: application/json" \
     -H "xi-api-key: $API_KEY" \
     -d "$JSON_PAYLOAD" \
     -o "$OUTPUT_PATH" \
     --silent \
     --show-error

if [ $? -eq 0 ] && [ -f "$OUTPUT_PATH" ] && [ -s "$OUTPUT_PATH" ]; then
    FILE_SIZE=$(stat -f%z "$OUTPUT_PATH" 2>/dev/null || wc -c < "$OUTPUT_PATH")
    echo "   ✅ Generated: $FILE_SIZE bytes"
    echo "📁 Saved to: $OUTPUT_PATH"
else
    echo "   ❌ Failed to generate sound effect"
    if [ -f "$OUTPUT_PATH" ]; then
        echo "Error response:"
        cat "$OUTPUT_PATH"
        rm "$OUTPUT_PATH"
    fi
    exit 1
fi