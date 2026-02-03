#!/bin/bash

# AI Image Generator - saves directly to Dropbox AI Images folder
# Usage: ./generate-ai-image.sh "prompt description" [resolution]

if [ $# -lt 1 ]; then
    echo "Usage: $0 'image description' [1K|2K|4K]"
    echo "Example: $0 'a cat wearing a top hat' 2K"
    exit 1
fi

PROMPT="$1"
RESOLUTION="${2:-1K}"
TIMESTAMP=$(date +"%Y-%m-%d-%H-%M-%S")
SAFE_PROMPT=$(echo "$PROMPT" | sed 's/[^a-zA-Z0-9 ]//g' | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | cut -c1-30)
FILENAME="${TIMESTAMP}-${SAFE_PROMPT}.png"
AI_IMAGES_DIR="/Users/Josh/Library/CloudStorage/Dropbox/AI Images"
OUTPUT_PATH="$AI_IMAGES_DIR/$FILENAME"

echo "🎨 Generating AI image..."
echo "   Prompt: $PROMPT"
echo "   Resolution: $RESOLUTION"
echo "   Filename: $FILENAME"

# Ensure AI Images directory exists
mkdir -p "$AI_IMAGES_DIR"

# Generate image directly to AI Images folder
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY environment variable not set"
    echo "   Set it with: export GEMINI_API_KEY='your-api-key'"
    exit 1
fi

uv run /usr/local/lib/node_modules/clawdbot/skills/nano-banana-pro/scripts/generate_image.py \
    --prompt "$PROMPT" \
    --filename "$FILENAME" \
    --resolution "$RESOLUTION"

# Move from workspace to AI Images if it was generated in workspace
if [ -f "/Users/Josh/clawd/$FILENAME" ]; then
    mv "/Users/Josh/clawd/$FILENAME" "$OUTPUT_PATH"
fi

if [ -f "$OUTPUT_PATH" ]; then
    FILE_SIZE=$(stat -f%z "$OUTPUT_PATH" 2>/dev/null || wc -c < "$OUTPUT_PATH")
    echo "✅ Generated: $FILENAME ($FILE_SIZE bytes)"
    echo "📁 Saved to: $OUTPUT_PATH"
    echo "MEDIA: $OUTPUT_PATH"
else
    echo "❌ Failed to generate image"
    exit 1
fi