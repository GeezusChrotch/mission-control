# MEMORY.md - Long-term memory

## 2026-02-04
- **CODING PREFERENCE**: For complex coding projects, spawn Antigravity CLI as a sub-agent. It handles deep coding work, reports back when done. Use for anything beyond quick scripts.

## 2026-01-28
- Named "Roboboogie" by Josh.
- Had formatting issues in WhatsApp replies (returning code structure instead of plain text).
- Fixed IDENTITY.md with name, creature: assistant, vibe: friendly/whimsical, emoji: 🤖.
- **LESSON LEARNED**: Josh was using direct Claude connection this morning (faster responses, more emojis), but I incorrectly told him he was on OpenRouter. When he tried to "fix" this based on my wrong info, it broke his working setup and led to an hour of troubleshooting Auth issues before settling on OpenRouter. Must accurately identify current provider/model, not guess.
- **AI IMAGE WORKFLOW**: Josh wants ALL generated images automatically saved to "/Users/Josh/Library/CloudStorage/Dropbox/AI Images/". Use ./generate-ai-image.sh script which saves directly there. Don't save to workspace anymore.
- **AUDIO DOWNLOAD WORKFLOW**: Added yt-dlp scripts for downloading YouTube audio to same folder as sound effects ("/Users/Josh/Library/CloudStorage/Dropbox/- LMT Audio/- Generated SFX"). Use ./download-audio.sh for simple downloads or ./yt-audio-batch.sh for advanced options.