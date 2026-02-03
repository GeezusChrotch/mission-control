# Morning Briefing - 6 AM Daily

Generate and send a comprehensive morning briefing to iMessage (jbessom@me.com) and Telegram.

## Data Sources

1. **Weather** - Open-Meteo API for Buena Park, CA
2. **Work Email** - Clippy (Outlook) unread count + recent subjects
3. **Personal Email** - gog (Gmail) unread count + recent subjects  
4. **Work Calendars** - gog Google Calendar: W2W Schedule + LMT VOps
5. **Personal Calendars** - gog (Google Calendar) Josh + Family calendars
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
  • W2W Schedule: [events or "No events"]
  • LMT VOps: [events or "No events"]

🏠 PERSONAL:
  • Josh:
    [events with time + summary, or "No events"]
  • Family:
    [events with time + summary, or "No events"]

✉️ EMAIL SUMMARY
📧 WORK OUTLOOK (X unread):
  1. [sender]: [subject]
  2. [sender]: [subject]
  ... (up to 10)
📧 PERSONAL GMAIL (X unread):
  1. [sender]: [subject]
  2. [sender]: [subject]
  ... (up to 10)

🎯 MISSION CONTROL
[Tasks in progress or due today]

💰 OPENROUTER USAGE
Yesterday's costs: $X.XX
[Usage summary if available]

📰 NEWS HEADLINES
• [blogwatcher articles]

---
Last updated: [time]
🤖 From Mr. Clawncy

Note: For iMessage, include "—Mr. Clawncy 🤖\n\n" at the start of the message body
```

## Tools to Use

- **Weather**: `curl` with `&forecast_days=2&temperature_unit=fahrenheit` for today + tomorrow in °F
- **Work Email**: `clippy mail --unread --json | jq -r '.emails[:10] | .[] | "\(.fromName): \(.subject)"'`
- **Work Calendars**: `gog calendar events 590pktrelg75lbm4074hif6ad8@group.calendar.google.com --from TODAY --to TOMORROW | tail -n +2` (W2W) AND `gog calendar events be8908a17c93a4f56d328554f4b3cdabc9be9c6ec6291f90b636da30d1c51da6@group.calendar.google.com --from TODAY --to TOMORROW | tail -n +2` (LMT VOps)
- **Personal Email**: `gog gmail search "is:unread" --json | jq -r '.threads[:10] | .[] | "\(.from): \(.subject)"'`
- **Personal Calendars**: `gog calendar events jbessom@gmail.com --from TODAY --to TOMORROW | tail -n +2` (Josh) AND `gog calendar events 11db48b25a66a05addce37f816e1cfeb215dcf8be41bb602d4cb76bd4340566c@group.calendar.google.com --from TODAY --to TOMORROW | tail -n +2` (Family)
- **News**: `python3 /Users/Josh/clawd/morning-rss.py` (Democracy Now, LA Times, The Intercept)
- **Tasks**: `cat /Users/Josh/clawd/data/tasks.json` (filter for status: in-progress, todo, not "permanent")
- **OpenRouter Costs**: Extract key from `~/.openclaw/openclaw.json` auth profiles, then `curl -s "https://openrouter.ai/api/v1/auth/key" -H "Authorization: Bearer $KEY"`

## Instructions

Gather all data, format cleanly (no markdown tables, iMessage-friendly), and send via:
1. iMessage to jbessom@me.com
2. Telegram to last used chat

If any tool fails (auth needed), note it in the briefing and suggest fix.

---

## Periodic Backup Check (Daily/Weekly)

Check if workspace needs backing up to GitHub:

```bash
cd /Users/Josh/clawd && git status --short && git log --oneline origin/main..HEAD
```

**If uncommitted changes found:**
- Summarize what's changed (files, lines added/removed)
- Ask if user wants to commit
- Suggest commit message based on changes
- Remind to run: `git push` after committing

**If commits ahead of origin/main:**
- Alert: "X commits not backed up to GitHub"
- Suggest: `git push origin main`

**Why this matters:**
- Laptop could die → lose everything not pushed
- Manual sync = intentional, safe from accidental commits
- I can help craft good commit messages