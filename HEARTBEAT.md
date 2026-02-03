# Morning Briefing - 6 AM Daily

Generate and send a comprehensive morning briefing to iMessage (jbessom@me.com) and Telegram.

## Data Sources

1. **Weather** - Open-Meteo API for Buena Park, CA
2. **Work Email** - Clippy (Outlook) unread count + recent subjects
3. **Personal Email** - gog (Gmail) unread count + recent subjects  
4. **Work Calendar** - Clippy (Outlook) today's events
5. **Personal Calendar** - gog (Google Calendar) today's events
6. **News** - blogwatcher recent articles
7. **Tasks** - Mission Control due/overdue tasks
8. **OpenRouter Usage** - Daily API costs and usage stats

## Template

```
🌅 GOOD MORNING! Tuesday, Feb 3

☀️ BUENA PARK WEATHER
Current: XX°F, [conditions]
Today: High XX°F / Low XX°F

📅 TODAY'S SCHEDULE
🎭 WORK:
  • [Outlook events]

🏠 PERSONAL:
  • [Google Calendar events]

✉️ EMAIL SUMMARY
📧 WORK OUTLOOK: X unread
📧 PERSONAL GMAIL: X unread

🎯 MISSION CONTROL
[Tasks in progress or due today]

💰 OPENROUTER USAGE
Yesterday's costs: $X.XX
[Usage summary if available]

📰 NEWS HEADLINES
• [blogwatcher articles]

---
Last updated: [time]
🤖 From Roboboogie
```

## Tools to Use

- `curl` for weather API
- `clippy mail --unread --json` for work email
- `clippy calendar --json` for work calendar
- `gog gmail search "is:unread" --json` for personal email
- `gog calendar events primary --from TODAY --to TODAY --json` for personal calendar
- `blogwatcher articles --limit 5` for news
- `cat /Users/Josh/clawd/data/tasks.json` for tasks
- OpenRouter API key from `~/.openclaw/config.json` or env - use curl to fetch usage: `curl -s "https://openrouter.ai/api/v1/credits" -H "Authorization: Bearer $OPENROUTER_API_KEY"`

## Instructions

Gather all data, format cleanly (no markdown tables, iMessage-friendly), and send via:
1. iMessage to jbessom@me.com
2. Telegram to last used chat

If any tool fails (auth needed), note it in the briefing and suggest fix.