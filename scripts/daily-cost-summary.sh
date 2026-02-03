#!/bin/bash
# Daily Cost Summary Script
# Calculates API spend across providers and logs to file
# Run via cron at midnight: 0 0 * * * /Users/Josh/clawd/scripts/daily-cost-summary.sh

TODAY=$(date +"%Y-%m-%d")
LOG_FILE="/Users/Josh/clawd/.cost-history.log"
OPENROUTER_API_KEY="sk-or-v1-b415fc3ebc3cdacbcef90b4c68f55424c515648c2b6fd66c"

echo "=== Daily Cost Summary for $TODAY ===" >> "$LOG_FILE"

# OpenRouter - Check balance and estimate spend
echo -n "OpenRouter: " >> "$LOG_FILE"
if command -v curl &> /dev/null; then
    BALANCE=$(curl -s -H "Authorization: Bearer $OPENROUTER_API_KEY" \
        "https://openrouter.ai/api/v1/account" | \
        python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('credits', 'N/A'))" 2>/dev/null)
    echo "Balance: $BALANCE credits" >> "$LOG_FILE"
else
    echo "curl not available" >> "$LOG_FILE"
fi

# ElevenLabs - Check API status (can't get balance without admin)
echo "ElevenLabs: Check ElevenLabs dashboard for current usage" >> "$LOG_FILE"

# Perplexity - Check API status
echo "Perplexity: Usage tracked via OpenRouter billing" >> "$LOG_FILE"

echo "" >> "$LOG_FILE"

# Output to console as well
echo "Daily cost summary logged to $LOG_FILE"
cat "$LOG_FILE" | tail -10