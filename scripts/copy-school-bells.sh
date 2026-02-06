#!/bin/bash
# Copy all school bell sound effects to a dedicated folder
# Run this after Dropbox has finished syncing

SFX_DIR="/Users/Josh/Library/CloudStorage/Dropbox/- LMT Audio/Audio/Sound Effects"
DEST="$SFX_DIR/School Bells"

mkdir -p "$DEST"

echo "Finding and copying school bell sound effects..."

find "$SFX_DIR" -type f \( -iname "*school*bell*" -o -iname "*bell*school*" \) ! -path "$DEST/*" | while read -r file; do
    basename=$(basename "$file")
    if cp "$file" "$DEST/$basename" 2>/dev/null; then
        echo "✓ Copied: $basename"
    else
        echo "✗ Failed: $basename (may need to download from Dropbox first)"
    fi
done

echo ""
echo "Done! Check: $DEST"
ls -la "$DEST"
