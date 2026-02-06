#!/bin/bash
# Automated Performance Report Scanner
# Scans Apple Mail's local cache for PDF attachments and extracts Audio/Sound section
# Uses HTML formatting for Apple Notes

export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin"

MAIL_DIR="$HOME/Library/Mail/V10"
PROCESSED_FILE="$HOME/.config/performance-reports-processed.txt"
touch "$PROCESSED_FILE"

echo "=== Performance Report Scanner ==="
echo "Date: $(date)"
echo ""

# Find performance report PDFs from last 3 days
find "$MAIL_DIR" -name "*Performance*Report*.pdf" -mtime -3 2>/dev/null | while read PDF_PATH; do
    PDF_HASH=$(echo "$PDF_PATH" | md5)
    
    if grep -q "$PDF_HASH" "$PROCESSED_FILE" 2>/dev/null; then
        continue
    fi
    
    echo "📄 Found: $(basename "$PDF_PATH")"
    
    PDF_TEXT=$(pdftotext -layout "$PDF_PATH" - 2>/dev/null)
    
    if [ -z "$PDF_TEXT" ]; then
        echo "   ⚠️ Could not extract text"
        continue
    fi
    
    REPORT_DATE=$(echo "$PDF_TEXT" | grep -E "^Date:" | head -1 | sed 's/Date: *//' | xargs)
    [ -z "$REPORT_DATE" ] && REPORT_DATE=$(date +%Y-%m-%d)
    
    PERFORMANCE=$(echo "$PDF_TEXT" | grep -E "^Performance:" | head -1 | sed 's/Performance: *//' | xargs)
    SHOW_NUM=$(echo "$PDF_TEXT" | grep -oE "SHOW #[0-9]+" | head -1)
    HOUSE_COUNT=$(echo "$PDF_TEXT" | grep -E "^House Count:" | head -1 | sed 's/House Count: *//' | xargs)
    MIX=$(echo "$PDF_TEXT" | grep -E "Mix:" | head -1 | sed 's/.*Mix: *//' | xargs)
    
    AUDIO_SECTION=$(echo "$PDF_TEXT" | sed -n '/- AUDIO:/,/^- [A-Z]/p' | head -n -1 | sed 's/^- AUDIO: *//')
    
    if [ -z "$AUDIO_SECTION" ]; then
        AUDIO_SECTION=$(echo "$PDF_TEXT" | grep -A15 "AUDIO:" | grep -v "^--$" | head -15)
    fi
    
    if [ -z "$AUDIO_SECTION" ]; then
        echo "   ℹ️ No Audio section found"
        echo "$PDF_HASH" >> "$PROCESSED_FILE"
        continue
    fi
    
    # Escape for AppleScript and convert to HTML
    AUDIO_HTML=$(echo "$AUDIO_SECTION" | sed "s/'/\\\\'/g" | sed 's/$/<br>/' | tr -d '\n')
    
    echo "   ✅ Extracted Audio section"
    
    TIMESTAMP=$(date '+%B %d, %Y at %I:%M %p')
    
    osascript << EOF
tell application "Notes"
    set noteTitle to "Sweeney Todd - Audio/Sound Notes"
    set newEntry to "<h2>📅 $REPORT_DATE ($PERFORMANCE) - $SHOW_NUM</h2>
<p><b>🎵 AUDIO NOTES:</b></p>
<p>$AUDIO_HTML</p>
<p><i>Mix: $MIX | House Count: $HOUSE_COUNT</i></p>
<hr>"
    
    try
        set existingNote to first note whose name is noteTitle
        set currentBody to body of existingNote
        
        -- Insert after first <hr>
        set insertPoint to offset of "</hr>" in currentBody
        if insertPoint > 0 then
            set newBody to (text 1 thru (insertPoint + 4) of currentBody) & "
" & newEntry & (text (insertPoint + 5) thru -1 of currentBody)
            set body of existingNote to newBody
        end if
    on error
        set noteBody to "<h1>Sweeney Todd - Audio/Sound Notes</h1>
<p><i>Last Updated: $TIMESTAMP</i></p>
<hr>
" & newEntry & "
<p><i>📋 Next scan: Tomorrow at 7:00 AM</i></p>"
        make new note with properties {name:noteTitle, body:noteBody}
    end try
end tell
EOF
    
    echo "   📝 Apple Note updated"
    osascript -e "display notification \"Audio notes from $REPORT_DATE\" with title \"Performance Report\" sound name \"Glass\""
    echo "$PDF_HASH" >> "$PROCESSED_FILE"
done

echo "=== Scan Complete ==="
