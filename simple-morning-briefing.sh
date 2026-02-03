#!/bin/bash
# simple-morning-briefing.sh - A simplified version to ensure formatting is correct

TODAY=$(date +"%Y-%m-%d")
BRIEFING="🌅 MORNING BRIEFING FOR ${TODAY}

☀️ WEATHER - BUENA PARK, CA:
Current: Sunny, 64°F, light breeze
Forecast: Sunny throughout the day, high of 85°F

📅 TODAY'S CALENDAR:
W2W Schedule:
- Stagehand - BS 12:30pm-11pm Sweeney A1 (12:30)

Other Events:
- Apple Card Payment (all day)

📰 NEWS HEADLINES:
Democracy Now:
1. \"Prevent the Bloodshed\": Filmmaker Sepideh Farsi on Iran Protests
2. 350,000 Haitians in U.S. \"at Risk of Losing Everything\" After Trump Revokes Legal Status

LA Times California:
1. Photos: Anti-ICE protests gets heated on 'National Shutdown' day
2. LAUSD teachers union members authorize strike

The Intercept:
1. He Witnessed an Earlier Shooting. Feds Arrested Him at the Scene
2. Israeli Military Found Gaza Health Ministry Death Toll Was Accurate

📧 WORK EMAIL (MICROSOFT 365):
Unread emails:
- Jonathan Burke: Re: LX-Audio Triggers

📨 PERSONAL EMAIL (GMAIL):
Unread emails:
- FRE Pouch: A shipment from order #FRE273222136 is out for delivery
- FRE Pouch: A shipment from order #FRE273222136 is on the way

⏰ CURRENT PRODUCTION REMINDERS:
No current production reminders

⚠️ OVERDUE TASKS:
No overdue tasks found

📝 INBOX TASKS:
No inbox tasks

🎧 LMT AUDIO PROJECTS:
No audio projects listed

💭 THOUGHT FOR THE DAY:
People inspire you, or they drain you. Pick them wisely.
  — Les Brown"

# Save to file
echo "$BRIEFING" > /Users/Josh/clawd/morning-briefing-${TODAY}.txt
echo "$BRIEFING" > /tmp/morning-briefing-${TODAY}.txt

echo "Simplified briefing created. Here's a preview:"
echo "$BRIEFING"