#!/bin/bash

# AI Image Upscaler using Upscayl
# Usage: ./upscale.sh input.png [output.png]
# If no output specified, creates input-upscaled.png

if [ $# -lt 1 ]; then
    echo "Usage: $0 input.png [output.png]"
    echo "Example: $0 my-image.png"
    echo "Example: $0 my-image.png my-image-4x.png"
    exit 1
fi

INPUT="$1"
OUTPUT="${2:-${INPUT%.*}-upscaled.${INPUT##*.}}"

# Check if input exists
if [ ! -f "$INPUT" ]; then
    echo "❌ Input file not found: $INPUT"
    exit 1
fi

# Check if Upscayl is installed
if [ ! -d "/Applications/Upscayl.app" ]; then
    echo "❌ Upscayl not found in Applications"
    echo "   Install with: brew install --cask upscayl"
    exit 1
fi

echo "🔍 Upscaling: $INPUT"
echo "📁 Output: $OUTPUT"
echo ""
echo "Opening Upscayl..."
echo "   1. Drag '$INPUT' into Upscayl"
echo "   2. Select your upscaling model (recommended: General/Photo)"
echo "   3. Click 'Upscale'"
echo "   4. Save to: $OUTPUT"
echo ""

# Open Upscayl and the input file location
open "/Applications/Upscayl.app"
open -R "$INPUT"

echo "✅ Upscayl launched! The file location is open in Finder."
