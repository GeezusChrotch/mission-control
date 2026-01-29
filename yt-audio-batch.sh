#!/bin/bash

# YouTube Audio Batch Downloader for Josh
# Advanced options for downloading audio content for theater work

SFX_DIR="/Users/Josh/Library/CloudStorage/Dropbox/- LMT Audio/- Generated SFX"

show_help() {
    echo "YouTube Audio Downloader for Theater Work"
    echo ""
    echo "Usage: $0 [options] <url>"
    echo ""
    echo "Options:"
    echo "  --playlist          Download entire playlist (default: single video)"
    echo "  --name <filename>   Custom filename (single videos only)"
    echo "  --format <format>   Audio format: mp3, wav, m4a (default: mp3)"
    echo "  --quality <0-9>     Audio quality: 0=best, 9=worst (default: 0)"
    echo "  --start <time>      Start time (e.g., 1:30 or 90)"
    echo "  --end <time>        End time (e.g., 2:45 or 165)"
    echo "  --help              Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 'https://youtube.com/watch?v=...'                    # Single video"
    echo "  $0 --name 'thunder-sound' 'https://youtube.com/...'    # Custom name"
    echo "  $0 --playlist 'https://youtube.com/playlist?list=...'  # Entire playlist"
    echo "  $0 --start 30 --end 60 'https://youtube.com/...'       # 30s clip"
    echo "  $0 --format wav 'https://youtube.com/...'              # WAV format"
    echo ""
    echo "Output directory: $SFX_DIR"
}

# Default options
PLAYLIST=false
CUSTOM_NAME=""
FORMAT="mp3"
QUALITY="0"
START_TIME=""
END_TIME=""

# Parse options
while [[ $# -gt 0 ]]; do
    case $1 in
        --playlist)
            PLAYLIST=true
            shift
            ;;
        --name)
            CUSTOM_NAME="$2"
            shift 2
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --quality)
            QUALITY="$2"
            shift 2
            ;;
        --start)
            START_TIME="$2"
            shift 2
            ;;
        --end)
            END_TIME="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        --)
            shift
            break
            ;;
        -*)
            echo "Unknown option: $1" >&2
            echo "Use --help for usage information"
            exit 1
            ;;
        *)
            URL="$1"
            break
            ;;
    esac
done

if [ -z "$URL" ]; then
    echo "Error: No URL provided"
    echo "Use --help for usage information"
    exit 1
fi

# Ensure directory exists
mkdir -p "$SFX_DIR"

echo "🎵 Downloading audio from YouTube..."
echo "   URL: $URL"
echo "   Format: $FORMAT"
echo "   Quality: $QUALITY (0=best)"
[ "$PLAYLIST" = true ] && echo "   Mode: Playlist"
[ -n "$CUSTOM_NAME" ] && echo "   Custom name: $CUSTOM_NAME"
[ -n "$START_TIME" ] && echo "   Start time: ${START_TIME}s"
[ -n "$END_TIME" ] && echo "   End time: ${END_TIME}s"
echo "   Destination: $SFX_DIR"

# Build yt-dlp command
YT_DLP_OPTS=(
    --extract-audio
    --audio-format "$FORMAT"
    --audio-quality "$QUALITY"
    --embed-metadata
    --add-metadata
)

# Playlist handling
if [ "$PLAYLIST" = true ]; then
    YT_DLP_OPTS+=(--yes-playlist)
    YT_DLP_OPTS+=(-o "$SFX_DIR/%(playlist_index)02d-%(title)s.%(ext)s")
else
    YT_DLP_OPTS+=(--no-playlist)
    if [ -n "$CUSTOM_NAME" ]; then
        YT_DLP_OPTS+=(-o "$SFX_DIR/${CUSTOM_NAME}.%(ext)s")
    else
        YT_DLP_OPTS+=(-o "$SFX_DIR/%(title)s.%(ext)s")
    fi
fi

# Time-based clipping
if [ -n "$START_TIME" ] || [ -n "$END_TIME" ]; then
    POSTPROCESSOR="--postprocessor-args"
    FFMPEG_ARGS=""
    
    if [ -n "$START_TIME" ]; then
        FFMPEG_ARGS="$FFMPEG_ARGS -ss $START_TIME"
    fi
    
    if [ -n "$END_TIME" ]; then
        FFMPEG_ARGS="$FFMPEG_ARGS -to $END_TIME"
    fi
    
    YT_DLP_OPTS+=("$POSTPROCESSOR" "$FFMPEG_ARGS")
fi

# Download the audio
echo ""
if yt-dlp "${YT_DLP_OPTS[@]}" "$URL"; then
    echo ""
    echo "✅ Download complete!"
    echo "📁 Files saved to: $SFX_DIR"
    
    # Show what was downloaded
    echo ""
    echo "Recent downloads:"
    find "$SFX_DIR" -name "*.$FORMAT" -type f -exec ls -lt {} + 2>/dev/null | head -5
else
    echo ""
    echo "❌ Download failed"
    exit 1
fi