#!/bin/bash
# Daily Performance Report Check - Run at 7 AM
# Checks for new performance reports and alerts if found

export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:/Users/Josh/.bun/bin"

echo "Checking for Performance Reports..."

# Search for unread performance reports
REPORTS=$(/Users/Josh/clawd/clippy-wrapper.sh mail -s "Performance Report" --unread --json 2>/dev/null | jq -r '.emails // [] | .[] | "\(.received) | \(.subject) | \(.id)"' 2>/dev/null)

if [ -z "$REPORTS" ]; then
    echo "No new performance reports found"
    exit 0
fi

# Process each report
echo "$REPORTS" | while IFS="|" read -r DATE SUBJECT MSG_ID; do
    DATE=$(echo "$DATE" | xargs)
    SUBJECT=$(echo "$SUBJECT" | xargs)
    MSG_ID=$(echo "$MSG_ID" | xargs)
    
    echo "Found: $SUBJECT ($DATE)"
    
    # Check if already processed
    PROCESSED_FILE="/tmp/processed-reports.txt"
    if grep -q "$MSG_ID" "$PROCESSED_FILE" 2>/dev/null; then
        echo "  Already processed, skipping"
        continue
    fi
    
    # Alert user
    osascript << APPLESCRIPT
display notification "New performance report: $SUBJECT" with title "Performance Report Alert" sound name "Glass"
APPLESCRIPT
    
    # Mark as processed
    echo "$MSG_ID" >> "$PROCESSED_FILE"
done

echo ""
echo "To extract Audio/Sound section:"
echo "1. Open the email in Outlook"
echo "2. Download the PDF attachment"
echo "3. Run: /Users/Josh/clawd/scripts/extract-pdf.sh <path-to-downloaded-pdf>"
