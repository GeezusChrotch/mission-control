#!/bin/bash
# Performance Report Extractor - Downloads PDF and extracts Audio/Sound section
# Usage: ./extract-pdf.sh <path-to-pdf>

PDF_FILE="$1"

if [ -z "$PDF_FILE" ]; then
    echo "Usage: $0 <path-to-pdf>"
    echo ""
    echo "This script extracts the Audio/Sound section from a performance report PDF"
    echo "and updates the Apple Note."
    exit 1
fi

if [ ! -f "$PDF_FILE" ]; then
    echo "Error: File not found: $PDF_FILE"
    exit 1
fi

# Extract all text from PDF
echo "Extracting text from PDF..."
PDF_TEXT=$(pdftotext -layout "$PDF_FILE" -)

# Extract date from filename or content
DATE=$(echo "$PDF_TEXT" | grep -E "(Date:|Report Date)" | head -1 | sed 's/.*: *//' || echo "$(date +%Y-%m-%d)")

# Find Audio/Sound section
echo "Finding Audio/Sound section..."
AUDIO_SECTION=$(echo "$PDF_TEXT" | awk '
/^[A-Z][a-z]+( |\/)[A-Z][a-z]+/ { section = $0 }
/Audio|Sound/ { 
    if (section ~ /Audio|Sound/) {
        print_section = 1
    }
}
print_section { print }
/^[A-Z][A-Z ]+$/ { 
    if (print_section && section !~ /Audio|Sound/) {
        print_section = 0
    }
}
')

# If no section found, show lines around Audio/Sound keywords
if [ -z "$AUDIO_SECTION" ]; then
    AUDIO_SECTION=$(echo "$PDF_TEXT" | grep -B2 -A5 -i "audio\|sound" | head -30)
fi

# Format for Apple Note
NOTE_CONTENT="Sweeney Todd - Performance Reports (Audio/Sound Section Catalog)

Date: $DATE
Extracted: $(date '+%Y-%m-%d %I:%M %p')

---

🎵 AUDIO/SOUND NOTES:
$AUDIO_SECTION

---

📋 NEXT SCAN: Tomorrow at 7:00 AM"

# Update Apple Note
osascript << APPLESCRIPT
tell application "Notes"
    set noteTitle to "Sweeney Todd - Performance Reports (Audio/Sound)"
    set noteBody to "$NOTE_CONTENT"
    
    try
        set existingNote to first note whose name is noteTitle
        set body of existingNote to noteBody
        display notification "Performance report updated" with title "Audio Notes"
    on error
        make new note with properties {name:noteTitle, body:noteBody}
        display notification "Performance report created" with title "Audio Notes"
    end try
end tell
APPLESCRIPT

echo ""
echo "✅ Audio/Sound section extracted and saved to Apple Notes"
echo ""
echo "Extracted content:"
echo "=================="
echo "$AUDIO_SECTION"
