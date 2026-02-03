#!/bin/bash
# notification-hub.sh - Aggregate notifications from multiple sources
# Usage: ./notification-hub.sh [hours_ago]

set -e

# Set PATH for cron
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:/Users/Josh/.bun/bin"

HOURS="${1:-24}"
SINCE=$(date -v-${HOURS}h +%Y-%m-%dT%H:%M:%S 2>/dev/null || date -d "-${HOURS} hours" +%Y-%m-%dT%H:%M:%S 2>/dev/null)

echo "🔔 NOTIFICATION HUB (last ${HOURS}h)"
echo "================================"

# --- GMAIL (unread + recent) ---
echo ""
echo "📨 GMAIL:"
GMAIL_NOTIFS=$(gog gmail search "is:unread newer_than:${HOURS}h" --max 10 --json 2>/dev/null | node -e "
const fs = require('fs');
try {
  const data = JSON.parse(fs.readFileSync(0, 'utf8'));
  const threads = data.threads || data || [];
  if (!threads.length) { console.log('  No recent emails'); }
  else threads.slice(0,10).forEach(m => {
    const from = (m.from || 'Unknown').replace(/<.*>/,'').substring(0,25);
    const subj = (m.subject || '(no subject)').substring(0,45);
    console.log('  📧 ' + from + ': ' + subj);
  });
} catch(e) { console.log('  Unable to fetch'); }
" 2>/dev/null || echo "  Unable to fetch")

# --- OUTLOOK (unread) ---
echo ""
echo "📧 OUTLOOK:"
OUTLOOK_NOTIFS=$(clippy mail --unread --limit 5 2>/dev/null | grep '\[' | sed 's/\[[ 0-9]*\] • */  • /' | head -5)
[ -z "$OUTLOOK_NOTIFS" ] && echo "  No unread emails" || echo "$OUTLOOK_NOTIFS"

# --- CALENDAR (today/tomorrow) ---
TODAY=$(date +"%Y-%m-%d")
TOMORROW=$(date -v+1d +"%Y-%m-%d" 2>/dev/null || date -d "+1 day" +"%Y-%m-%d" 2>/dev/null)

echo ""
echo "📅 UPCOMING (today/tomorrow):"
CAL_NOTIFS=$(gog calendar events "590pktrelg75lbm4074hif6ad8@group.calendar.google.com" --from "${TODAY}T00:00:00" --to "${TOMORROW}T23:59:59" --json 2>/dev/null | node -e "
const fs = require('fs');
try {
  const data = JSON.parse(fs.readFileSync(0, 'utf8'));
  const events = data.events || data || [];
  if (!events.length) { console.log('  No upcoming events'); }
  else events.slice(0,5).forEach(e => {
    const t = e.start?.dateTime ? new Date(e.start.dateTime).toLocaleTimeString('en-US',{hour:'numeric',minute:'2-digit'}) : 'All day';
    console.log('  📌 ' + e.summary + ' ' + t);
  });
} catch(e) { console.log('  No events'); }
" 2>/dev/null)

# --- PRIORITY SUMMARY ---
echo ""
echo "⭐ PRIORITY ITEMS:"
echo "  (High priority: emails from known contacts, meetings in next 4h)"

# Get events in next 4 hours
NOW=$(date +%s)
FOUR_HOURS_LATER=$(($NOW + 14400))
URGENT_EVENTS=$(gog calendar events "590pktrelg75lbm4074hif6ad8@group.calendar.google.com" --from "${TODAY}T00:00:00" --to "${TOMORROW}T23:59:59" --json 2>/dev/null | node -e "
const fs = require('fs');
try {
  const data = JSON.parse(fs.readFileSync(0, 'utf8'));
  const events = data.events || data || [];
  const now = Date.now() / 1000;
  const soon = now + (4 * 3600);
  const urgent = events.filter(e => {
    if (!e.start?.dateTime) return false;
    const eventTime = new Date(e.start.dateTime).getTime() / 1000;
    return eventTime >= now && eventTime <= soon;
  });
  if (!urgent.length) { console.log('  No urgent upcoming meetings'); }
  else urgent.forEach(e => {
    const t = new Date(e.start.dateTime).toLocaleTimeString('en-US',{hour:'numeric',minute:'2-digit'});
    console.log('  🚨 ' + e.summary + ' at ' + t);
  });
} catch(e) { console.log('  Unable to check'); }
" 2>/dev/null)

echo ""
echo "================================"
echo "Updated: $(date '+%Y-%m-%d %I:%M %p')"