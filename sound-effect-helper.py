#!/usr/bin/env python3
"""
Sound Effect Helper - Simple interface for requesting sound effects from Roboboogie

Usage: Just run this script and it will show you how to request sound effects through chat.
"""

print("""
🎭 Sound Effect Helper for Josh

Since Clawdbot's TTS function works perfectly through the assistant interface,
the simplest way to generate your sound effects is to ask Roboboogie directly!

Example requests you can send via Telegram:

📝 Single sound effect:
"Generate a train whistle sound effect"

📝 Multiple variations:
"Generate 3 variations of thunder clap sound effects"

📝 Batch request:
"Generate these sound effects:
- 2 variations of door creak
- 3 variations of footsteps on gravel  
- 1 thunder clap
- 2 variations of wind howling"

📁 All files will be automatically saved to:
/Users/Josh/Library/CloudStorage/Dropbox/- LMT Audio/LMT Downloads/

✅ Benefits of this approach:
- Uses your working ElevenLabs API key
- No complex setup or debugging
- I can handle the file naming and organization
- You can request multiple effects in one message
- I can adjust prompts for better results

💡 Pro tip: Be specific with your requests!
Instead of: "door sound" 
Try: "old wooden door creaking slowly"
""")

# Show current status
import os
downloads_dir = "/Users/Josh/Library/CloudStorage/Dropbox/- LMT Audio/- Generated SFX"
if os.path.exists(downloads_dir):
    files = os.listdir(downloads_dir)
    if files:
        print(f"\n📂 Current files in LMT Downloads: {len(files)}")
        for file in sorted(files):
            if file.endswith(('.mp3', '.wav', '.m4a')):
                size = os.path.getsize(os.path.join(downloads_dir, file))
                print(f"  - {file} ({size:,} bytes)")
    else:
        print(f"\n📂 LMT Downloads folder is empty")
else:
    print(f"\n❌ LMT Downloads folder not found")