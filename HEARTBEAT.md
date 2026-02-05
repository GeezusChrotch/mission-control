# Morning Briefing - 6 AM Daily

Generate and send a comprehensive morning briefing to iMessage (jbessom@me.com) and Telegram.

## Data Sources

1. **Weather** - Open-Meteo API for Buena Park, CA (include sunrise/sunset)
2. **Work Email** - Clippy (Outlook) unread count + recent subjects
3. **Personal Email** - gog (Gmail) unread count + recent subjects + package tracking
4. **All Google Calendars** - Events from ALL calendars for today + next 7 days for birthdays
5. **News** - blogwatcher/RSS recent articles (3 per source)
6. **Kanban Board** - Check kanban.json for in-progress tasks, todo items, and overdue items

## Google Calendars (All)

| Calendar | ID |
|----------|-----|
| Josh (primary) | jbessom@gmail.com |
| Family | 11db48b25a66a05addce37f816e1cfeb215dcf8be41bb602d4cb76bd4340566c@group.calendar.google.com |
| W2W Schedule | 590pktrelg75lbm4074hif6ad8@group.calendar.google.com |
| LMT VOps | be8908a17c93a4f56d328554f4b3cdabc9be9c6ec6291f90b636da30d1c51da6@group.calendar.google.com |
| LMT IATSE | c8509e30517403971284d40b3cf123b307d280870189ca98ac6f9e199cd00b7e@group.calendar.google.com |
| Hours | 4542c622ff207b79a9cc2858ee6f2e16d6cb8cadb0bb8d6b7af4f0f2ce6f0d8a@group.calendar.google.com |
| LzPr | laf9krvoe31vdud6otg33i2100@group.calendar.google.com |
| Jane | fancyjane@gmail.com |

## Template

```
🌅 GOOD MORNING! [Day], [Date]

☀️ BUENA PARK WEATHER
Current: XX°F, [conditions]
Today: High XX°F / Low XX°F
Tomorrow: High XX°F / Low XX°F
🌅 Sunrise: X:XX AM | 🌇 Sunset: X:XX PM

📅 TODAY'S SCHEDULE
[List events from ALL calendars with calendar name prefix]
• [Calendar]: [time] - [event]
(or "No events scheduled for today")

🎂 UPCOMING BIRTHDAYS/ANNIVERSARIES (Next 7 Days)
[Scan all calendars for events containing "birthday", "bday", "anniversary"]
• [Date]: [event name]
(or "None in the next 7 days")

✉️ EMAIL SUMMARY
📧 WORK OUTLOOK (X unread):
  1. [sender]: [subject]
  ... (up to 10)

📧 PERSONAL GMAIL (X unread):
  1. [sender]: [subject]
  ... (up to 10)

📦 PACKAGES
[Parse Amazon/shipping emails for deliveries arriving today/soon]
• [carrier]: [item/tracking] - [status]
(or "No packages expected")

🎯 KANBAN BOARD
🔄 IN PROGRESS:
  • [task] - [column]
📋 TODO:
  • [task]
⚠️ OVERDUE (check timestamps):
  • [task] - [age]
(Skip sections if empty)

📰 NEWS — 9 stories (3 per source)

**Democracy Now:**
• [Headline as clickable link]
  [1-2 sentence summary]
  
**LA Times California:**
• [Headline as clickable link]
  [1-2 sentence summary]

**The Intercept:**
• [Headline as clickable link]
  [1-2 sentence summary]

IMPORTANT: Each news item MUST include:
1. Headline text linked to the article URL
2. A 1-2 sentence summary below it
Do NOT abbreviate or skip summaries!

---
🤖 Mr. Clawncy | [time]
```

## Tools to Use

### Weather (with sunrise/sunset)
```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=33.8675&longitude=-118.0103&current=temperature_2m,weather_code&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset&temperature_unit=fahrenheit&timezone=America/Los_Angeles&forecast_days=2"
```

### Work Email (Outlook)
```bash
clippy mail --unread --json | jq -r '.emails[:10] | .[] | "\(.fromName): \(.subject)"'
```

### Personal Email (Gmail)
```bash
gog gmail search "is:unread" --json | jq -r '.threads[:10] | .[] | "\(.from): \(.subject)"'
```

### Package Tracking (Gmail - Amazon/shipping)
```bash
gog gmail search "is:unread (from:amazon OR from:ups OR from:fedex OR from:usps) subject:(delivered OR arriving OR shipment OR out for delivery)" --json | jq -r '.threads[:5] | .[] | "\(.from): \(.subject)"'
```

### All Calendars - Today's Events
```bash
# Run for each calendar, combine results:
gog calendar events jbessom@gmail.com --from TODAY --to TOMORROW | tail -n +2
gog calendar events 11db48b25a66a05addce37f816e1cfeb215dcf8be41bb602d4cb76bd4340566c@group.calendar.google.com --from TODAY --to TOMORROW | tail -n +2
gog calendar events 590pktrelg75lbm4074hif6ad8@group.calendar.google.com --from TODAY --to TOMORROW | tail -n +2
gog calendar events be8908a17c93a4f56d328554f4b3cdabc9be9c6ec6291f90b636da30d1c51da6@group.calendar.google.com --from TODAY --to TOMORROW | tail -n +2
gog calendar events c8509e30517403971284d40b3cf123b307d280870189ca98ac6f9e199cd00b7e@group.calendar.google.com --from TODAY --to TOMORROW | tail -n +2
gog calendar events 4542c622ff207b79a9cc2858ee6f2e16d6cb8cadb0bb8d6b7af4f0f2ce6f0d8a@group.calendar.google.com --from TODAY --to TOMORROW | tail -n +2
gog calendar events laf9krvoe31vdud6otg33i2100@group.calendar.google.com --from TODAY --to TOMORROW | tail -n +2
gog calendar events fancyjane@gmail.com --from TODAY --to TOMORROW | tail -n +2
```

### Birthdays/Anniversaries (Next 7 Days)
```bash
# Search all calendars for next 7 days, filter for birthday/anniversary keywords
gog calendar events jbessom@gmail.com --from TODAY --to "+7 days" | grep -i -E "(birthday|bday|anniversary)"
# (repeat for each calendar)
```

### Tasks (Kanban Board)
```bash
cat /Users/Josh/clawd/kanban/kanban.json
# Filter for: in-progress tasks, overdue items (check description for dates), todo items
# Columns: todo, inprogress, done, suggestions, info, permanent
```

### News
```bash
python3 /Users/Josh/clawd/morning-rss-json.py 3
# Outputs 3 articles each from Democracy Now, LA Times, The Intercept
```

## Instructions

1. Gather all data using the tools above
2. Format cleanly (no markdown tables - iMessage doesn't render them)
3. Use bullet points and emoji for visual organization
4. Send via iMessage to jbessom@me.com first, then Telegram
5. If any tool fails, note it briefly and continue with other sections

## Notes

- Start iMessage body with "—Mr. Clawncy 🤖\n\n" 
- Keep it scannable - busy mornings mean quick reads
- Bold headlines in news section with links
- Times in 12-hour format with AM/PM
