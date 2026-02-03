#!/bin/bash
# meeting-prep.sh - Research meeting attendees and generate prep brief
# Usage: ./meeting-prep.sh "Meeting Title" "YYYY-MM-DD HH:MM"

set -e

# Set PATH for cron
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:/Users/Josh/.bun/bin"

MEETING_TITLE="${1:-}"
MEETING_TIME="${2:-}"

if [ -z "$MEETING_TITLE" ] || [ -z "$MEETING_TIME" ]; then
    echo "Usage: ./meeting-prep.sh \"Meeting Title\" \"YYYY-MM-DD HH:MM\""
    echo "Example: ./meeting-prep.sh \"Production Meeting\" \"2026-02-03 14:00\""
    exit 1
fi

echo "🔍 Researching: $MEETING_TITLE at $MEETING_TIME"

# Extract potential attendee names from meeting title (basic heuristics)
# This is a placeholder - real implementation would need calendar integration

# Check recent emails related to meeting
echo ""
echo "📧 Recent emails..."
RECENT_EMAILS=$(gog gmail search "subject:$MEETING_TITLE newer_than:7d" --max 5 --json 2>/dev/null | node -e "
const fs = require('fs');
try {
  const data = JSON.parse(fs.readFileSync(0, 'utf8'));
  const threads = data.threads || data || [];
  if (!threads.length) { console.log('  No recent emails found'); }
  else threads.slice(0,5).forEach(m => {
    const from = (m.from || 'Unknown').replace(/<.*>/,'').substring(0,30);
    const subj = (m.subject || '(no subject)').substring(0,50);
    console.log('  • ' + from + ': ' + subj);
  });
} catch(e) { console.log('  No emails found'); }
" 2>/dev/null || echo "  Unable to fetch emails")

# Placeholder for attendee research
echo ""
echo "👥 Attendee research..."
echo "  (Would search LinkedIn/GitHub for attendees)"
echo "  (Would extract names from calendar invite)"

# Generate prep brief
BRIEFING="## MEETING PREP: ${MEETING_TITLE}

📅 **Time:** ${MEETING_TIME}

**Recent Emails:**
${RECENT_EMAILS}

**Attendee Research:**
- (Integrate with calendar to get attendee list)
- (Search LinkedIn for bio/background)
- (Check GitHub for relevant projects)

**Action Items to Prepare:**
- Review previous meeting notes
- Check action item completion
- Prepare status updates

---

*Generated $(date '+%Y-%m-%d %I:%M %p')*"

echo ""
echo "$BRIEFING"

# Save to file
OUTPUT_FILE="/Users/Josh/clawd/meeting-prep-$(echo "$MEETING_TITLE" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')-$(date +%Y-%m-%d).md"
echo "$BRIEFING" > "$OUTPUT_FILE"
echo ""
echo "💾 Saved to: $OUTPUT_FILE"
