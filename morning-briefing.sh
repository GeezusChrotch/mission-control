#!/bin/bash
# morning-briefing.sh - Real-time briefing with live data

# Set PATH for cron
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:/Users/Josh/.bun/bin"
export GOG_ACCOUNT=jbessom@gmail.com

TODAY=$(date +"%Y-%m-%d")
TOMORROW=$(date -v+1d +"%Y-%m-%d" 2>/dev/null || date -d "+1 day" +"%Y-%m-%d" 2>/dev/null)

# Always regenerate - no cached data
rm -f /tmp/morning-briefing-${TODAY}.txt /Users/Josh/clawd/morning-briefing-${TODAY}.txt

echo "Building briefing for $TODAY..."

# --- WEATHER (Open-Meteo API) ---
WEATHER_JSON=$(curl -s --connect-timeout 5 --max-time 10 "https://api.open-meteo.com/v1/forecast?latitude=33.87&longitude=-118.01&current_weather=true" 2>&1)
if [ $? -eq 0 ] && [ -n "$WEATHER_JSON" ]; then
  # More robust extraction
  TEMP_C=$(echo "$WEATHER_JSON" | sed -n 's/.*"temperature":\([0-9.]*\).*/\1/p' | tail -1)
  CODE=$(echo "$WEATHER_JSON" | sed -n 's/.*"weathercode":\([0-9]*\).*/\1/p' | head -1)
  if [ -n "$TEMP_C" ] && [ -n "$CODE" ]; then
    TEMP_F=$(awk "BEGIN {printf \"%.0f\", $TEMP_C * 9/5 + 32}")
    case $CODE in
      0) DESC="Sunny" ;;
      1|2|3) DESC="Partly Cloudy" ;;
      *) DESC="Clear" ;;
    esac
    WEATHER="${DESC} ${TEMP_F}°F"
  else
    WEATHER="Unable to parse (temp=$TEMP_C, code=$CODE)"
  fi
else
  WEATHER="Unable to fetch"
fi

# Tomorrow forecast
WEATHER_TOMORROW=$(curl -s --connect-timeout 3 --max-time 5 "https://api.open-meteo.com/v1/forecast?latitude=33.87&longitude=-118.01&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=America/Los_Angeles" 2>/dev/null)
if [ -n "$WEATHER_TOMORROW" ]; then
  MAX=$(echo "$WEATHER_TOMORROW" | sed 's/.*"temperature_2m_max":\([^}]*\).*/\1/' | tr -d '[]' | tr ',' '\n' | head -1 | xargs)
  MIN=$(echo "$WEATHER_TOMORROW" | sed 's/.*"temperature_2m_min":\([^}]*\).*/\1/' | tr -d '[]' | tr ',' '\n' | head -1 | xargs)
  CODE_TOM=$(echo "$WEATHER_TOMORROW" | sed 's/.*"weathercode":\([^}]*\).*/\1/' | tr -d '[]' | tr ',' '\n' | head -1 | xargs)
  if [ -n "$MAX" ]; then
    MAX_F=$(awk "BEGIN {printf \"%.0f\", $MAX * 9/5 + 32}")
    MIN_F=$(awk "BEGIN {printf \"%.0f\", $MIN * 9/5 + 32}")
    case $CODE_TOM in
      0) DESC_TOM="Sunny" ;;
      1|2|3) DESC_TOM="Partly Cloudy" ;;
      *) DESC_TOM="Cloudy" ;;
    esac
    WEATHER_TOMORROW="${DESC_TOM} ${MAX_F}°F / ${MIN_F}°F"
  else
    WEATHER_TOMORROW="Unable to fetch"
  fi
else
  WEATHER_TOMORROW="Unable to fetch"
fi

# --- CALENDAR W2W (2 days) ---
W2W_EVENTS=$(gog calendar events "590pktrelg75lbm4074hif6ad8@group.calendar.google.com" --from "${TODAY}T00:00:00" --to "${TOMORROW}T23:59:59" --json 2>/dev/null | node -e "
const fs = require('fs');
try {
  const data = JSON.parse(fs.readFileSync(0, 'utf8'));
  const events = data.events || data || [];
  if (!events.length) { console.log('  No events'); }
  else events.forEach(e => {
    const t = e.start?.dateTime ? new Date(e.start.dateTime).toLocaleTimeString('en-US',{hour:'numeric',minute:'2-digit'}) : 'All day';
    console.log('  • ' + e.summary + ' ' + t);
  });
} catch(e) { console.log('  No events'); }
" 2>/dev/null)

# --- CALENDAR FAMILY (2 days) ---
OTHER_EVENTS=$(gog calendar events "11db48b25a66a05addce37f816e1cfeb215dcf8be41bb602d4cb76bd4340566c@group.calendar.google.com" --from "${TODAY}T00:00:00" --to "${TOMORROW}T23:59:59" --json 2>/dev/null | node -e "
const fs = require('fs');
try {
  const data = JSON.parse(fs.readFileSync(0, 'utf8'));
  const events = data.events || data || [];
  if (!events.length) { console.log('  No events'); }
  else events.forEach(e => {
    const t = e.start?.dateTime ? new Date(e.start.dateTime).toLocaleTimeString('en-US',{hour:'numeric',minute:'2-digit'}) : 'All day';
    console.log('  • ' + e.summary + ' ' + t);
  });
} catch(e) { console.log('  No events'); }
" 2>/dev/null)

# --- OUTLOOK EMAILS (unread) ---
# New clippy format: [ 1] • Sender Subject Date
OUTLOOK_UNREAD=$(clippy mail --unread --limit 5 2>/dev/null | grep '\[' | sed 's/\[[ 0-9]*\] • */  • /' | head -5)
[ -z "$OUTLOOK_UNREAD" ] && OUTLOOK_UNREAD="  No unread emails"

# --- GMAIL (unread) ---
GMAIL_RAW=$(gog gmail search "is:unread newer_than:1d" --max 5 --json 2>/dev/null)
GMAIL_UNREAD=$(echo "$GMAIL_RAW" | node -e "
const fs = require('fs');
try {
  const data = JSON.parse(fs.readFileSync(0, 'utf8'));
  const threads = data.threads || data || [];
  if (!threads.length) { console.log('  No unread emails'); }
  else threads.slice(0,5).forEach(m => {
    const from = (m.from || 'Unknown').replace(/<.*>/,'').substring(0,25);
    const subj = (m.subject || '(no subject)').substring(0,40);
    console.log('  • ' + from + ': ' + subj);
  });
} catch(e) { console.log('  No unread emails'); }
" 2>/dev/null)

# --- NEWS (RSS) ---
NEWS=$(python3 /Users/Josh/clawd/morning-rss.py 3 2>/dev/null)

# --- OPENROUTER BALANCE ---
# Check balance from OpenRouter API
OPENROUTER_BALANCE="  Unable to check"
if [ -n "$OPENROUTER_API_KEY" ]; then
  BALANCE_JSON=$(curl -s --connect-timeout 5 --max-time 10 \
    -H "Authorization: Bearer $OPENROUTER_API_KEY" \
    "https://api.openrouter.ai/v1/credits" 2>/dev/null)
  if [ -n "$BALANCE_JSON" ]; then
    BALANCE=$(echo "$BALANCE_JSON" | sed -n 's/.*"total_credits":\([0-9.]*\).*/\1/p' | head -1)
    if [ -n "$BALANCE" ]; then
      if (( $(echo "$BALANCE < 40" | bc -l) )); then
        OPENROUTER_BALANCE="⚠️ Low balance: \$${BALANCE}"
      else
        OPENROUTER_BALANCE="\$${BALANCE}"
      fi
    fi
  fi
fi

# --- BUILD BRIEFING ---
BRIEFING="🌅 MORNING BRIEFING FOR ${TODAY}

☀️ WEATHER - BUENA PARK, CA:
${WEATHER}

TOMORROW: ${WEATHER_TOMORROW}

---

📅 TODAY'S CALENDAR:

W2W Schedule:
${W2W_EVENTS}

Other Events:
${OTHER_EVENTS}

---

📰 NEWS:

${NEWS}

---

📧 WORK EMAIL (OUTLOOK):
${OUTLOOK_UNREAD}

📨 PERSONAL EMAIL (GMAIL):
${GMAIL_UNREAD}

---

💰 OPENROUTER BALANCE:
${OPENROUTER_BALANCE}

---

💭 THOUGHT FOR THE DAY:
The best way to predict the future is to create it.
  — Peter Drucker"

echo "$BRIEFING" > /Users/Josh/clawd/morning-briefing-${TODAY}.txt
echo "$BRIEFING" > /tmp/morning-briefing-${TODAY}.txt
rm -f /tmp/morning-briefing-${TODAY}.done

echo "Briefing ready."