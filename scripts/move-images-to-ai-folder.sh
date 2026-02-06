#!/bin/bash

# Move any existing images from workspace to AI Images folder
# This is a one-time cleanup script

WORKSPACE="/Users/Josh/clawd"
AI_IMAGES_DIR="/Users/Josh/Library/CloudStorage/Dropbox/AI Images"

echo "🗂️  Moving workspace images to AI Images folder..."

# Find and move all image files (excluding git folder)
find "$WORKSPACE" -maxdepth 1 \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.gif" -o -name "*.webp" \) -type f | while read -r file; do
    filename=$(basename "$file")
    echo "   Moving: $filename"
    mv "$file" "$AI_IMAGES_DIR/"
done

echo "✅ Cleanup complete!"
echo "📁 All images now in: $AI_IMAGES_DIR"