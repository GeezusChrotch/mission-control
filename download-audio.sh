#!/bin/bash

# YouTube Audio Downloader for Josh
# Downloads audio-only to the Generated SFX folder
# Usage: ./download-audio.sh "https://youtube.com/watch?v=..."

if [ $# -eq 0 ]; then
    echo "Usage: $0 <youtube-url> [output-filename]"
    echo "Examples:"
    echo "  $0 'https://youtube.com/watch?v=dQw4w9WgXcQ'"
    echo "  $0 'https://youtube.com/watch?v=dQw4w9WgXcQ' 'custom-name'"
    echo ""
    echo "Downloads audio-only (best quality) to:"
    echo "  /Users/Josh/Library/CloudStorage/Dropbox/- LMT Audio/- Generated SFX/"
    exit 1
fi

URL="$1"
CUSTOM_NAME="$2"
SFX_DIR="/Users/Josh/Library/CloudStorage/Dropbox/- LMT Audio/- Generated SFX"

# Ensure directory exists
mkdir -p "$SFX_DIR"

echo "🎵 Downloading audio from YouTube..."
echo "   URL: $URL"
echo "   Destination: $SFX_DIR"

# Build yt-dlp command
YT_DLP_OPTS=(
    --extract-audio
    --audio-format mp3
    --audio-quality 0
    --embed-metadata
    --add-metadata
    --no-playlist
    -o "$SFX_DIR/%(title)s.%(ext)s"
)

# If custom name provided, use it
if [ -n "$CUSTOM_NAME" ]; then
    YT_DLP_OPTS[-1]="$SFX_DIR/${CUSTOM_NAME}.%(ext)s"
    echo "   Custom filename: ${CUSTOM_NAME}.mp3"
fi

# Download the audio
if yt-dlp "${YT_DLP_OPTS[@]}" "$URL"; then
    echo ""
    echo "✅ Download complete!"
    echo "📁 Check: $SFX_DIR"
    
    # Show what was downloaded
    echo ""
    echo "Recent audio files:"
    ls -lt "$SFX_DIR"/*.mp3 2>/dev/null | head -3
else
    echo ""
    echo "❌ Download failed"
    exit 1
fi