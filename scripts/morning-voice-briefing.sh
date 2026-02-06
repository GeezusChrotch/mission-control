#!/bin/bash
# Morning Voice Briefing for Josh & Jane
# Runs at 6 AM - plays on Bedroom Speaker

set -e

# Get weather for Buena Park
WEATHER_JSON=$(curl -s "https://api.open-meteo.com/v1/forecast?latitude=33.8675&longitude=-118.0098&current=temperature_2m,weather_code&daily=temperature_2m_max,temperature_2m_min&timezone=America%2FLos_Angeles&forecast_days=1&temperature_unit=fahrenheit")
CURRENT_TEMP=$(echo "$WEATHER_JSON" | jq -r '.current.temperature_2m')
HIGH_TEMP=$(echo "$WEATHER_JSON" | jq -r '.daily.temperature_2m_max[0]')
LOW_TEMP=$(echo "$WEATHER_JSON" | jq -r '.daily.temperature_2m_min[0]')

# Get calendar events for today
TODAY=$(date +%Y-%m-%d)
TOMORROW=$(date -v+1d +%Y-%m-%d 2>/dev/null || date -d "+1 day" +%Y-%m-%d)

# Personal calendar (Josh)
JOSH_EVENTS=$(cd /Users/Josh/clawd && gog calendar events jbessom@gmail.com --from "$TODAY" --to "$TOMORROW" 2>/dev/null | tail -n +2 | head -5)

# Family calendar
FAMILY_EVENTS=$(cd /Users/Josh/clawd && gog calendar events "11db48b25a66a05addce37f816e1cfeb215dcf8be41bb602d4cb76bd4340566c@group.calendar.google.com" --from "$TODAY" --to "$TOMORROW" 2>/dev/null | tail -n +2 | head -3)

# Build calendar section
CALENDAR_TEXT=""
if [ -n "$JOSH_EVENTS" ] || [ -n "$FAMILY_EVENTS" ]; then
    CALENDAR_TEXT=" Here's your schedule for today:"
    if [ -n "$JOSH_EVENTS" ]; then
        CALENDAR_TEXT="${CALENDAR_TEXT} Josh has: ${JOSH_EVENTS}."
    fi
    if [ -n "$FAMILY_EVENTS" ]; then
        CALENDAR_TEXT="${CALENDAR_TEXT} Family events: ${FAMILY_EVENTS}."
    fi
else
    CALENDAR_TEXT=" You have no calendar events scheduled for today."
fi

# Create the message
MESSAGE="Good morning! It's $(date '+%A, %B %d'). The current temperature is ${CURRENT_TEMP} degrees Fahrenheit, with a high of ${HIGH_TEMP} and a low of ${LOW_TEMP} degrees.${CALENDAR_TEXT} Have a wonderful day!"

# Generate TTS audio using sag skill (using default voice)
sag "$MESSAGE" --output /tmp/morning-briefing.mp3 --api-key "sk_58c07ebe1a86a60558382737f5cdfc6cb9338bd7e3400330"

# Stream to Bedroom Speaker
atvremote -n "Bedroom Speaker" stream_file=/tmp/morning-briefing.mp3

# Cleanup
rm -f /tmp/morning-briefing.mp3
