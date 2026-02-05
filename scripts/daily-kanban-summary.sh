#!/usr/bin/env bash
# Auto-Daily Summary Script
# Generates daily summary based on kanban changes and saves to memory/YYYY-MM-DD.md

KANBAN_FILE="/Users/Josh/clawd/kanban/kanban.json"
MEMORY_DIR="/Users/Josh/clawd/memory"
DATE=$(date +%Y-%m-%d)
MEMORY_FILE="$MEMORY_DIR/$DATE.md"

# Create memory directory if needed
mkdir -p "$MEMORY_DIR"

# Extract today's activity from kanban
TODAY=$(date +%Y-%m-%d)

# Count cards created today
CREATED_TODAY=$(python3 << EOF
import json
from datetime import datetime

try:
    with open('$KANBAN_FILE', 'r') as f:
        data = json.load(f)
    
    today = '$TODAY'
    count = 0
    for card in data.get('cards', []):
        created = card.get('createdAt', '')
        if today in created:
            count += 1
    print(count)
except:
    print(0)
EOF
)

# Count cards moved to Done today
COMPLETED_TODAY=$(python3 << EOF
import json
from datetime import datetime

try:
    with open('$KANBAN_FILE', 'r') as f:
        data = json.load(f)
    
    today = '$TODAY'
    completed = []
    for card in data.get('cards', []):
        for change in card.get('statusChanges', []):
            if change.get('to') == 'done' and today in change.get('timestamp', ''):
                completed.append(card['title'])
    print(len(completed))
    for title in completed[:5]:
        print(f"  - {title}")
except Exception as e:
    print(0)
EOF
)

# Count cards currently in each column
COLUMN_COUNTS=$(python3 << EOF
import json

try:
    with open('$KANBAN_FILE', 'r') as f:
        data = json.load(f)
    
    counts = {'suggestions': 0, 'todo': 0, 'inprogress': 0, 'done': 0}
    for card in data.get('cards', []):
        col = card.get('column', 'unknown')
        if col in counts:
            counts[col] += 1
    
    print(f"📊 Current Board: {counts['suggestions']} suggestions | {counts['todo']} todo | {counts['inprogress']} in progress | {counts['done']} done")
except:
    print("📊 Board stats unavailable")
EOF
)

# Generate summary
cat > "$MEMORY_FILE" << EOF
# $DATE - Daily Summary

## Activity Overview
- 📌 **$CREATED_TODAY** new cards created
- ✅ **$(echo "$COMPLETED_TODAY" | head -1)** cards completed

$(if [ "$(echo "$COMPLETED_TODAY" | head -1)" -gt 0 ]; then
    echo "### Completed Today"
    echo "$COMPLETED_TODAY" | tail -n +2 | head -10
fi)

## Board Status
$COLUMN_COUNTS

## Notes
$(if [ -f "$MEMORY_FILE" ]; then
    # Preserve existing notes if file exists
    grep -A 100 "## Notes" "$MEMORY_FILE" 2>/dev/null | tail -n +2 || echo "-"
else
    echo "-"
fi)

---
*Auto-generated at $(date)*
EOF

echo "Daily summary saved to $MEMORY_FILE"
