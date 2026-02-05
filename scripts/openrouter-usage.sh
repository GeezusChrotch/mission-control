#!/bin/bash
# OpenRouter Usage Reporter
# Tracks daily spend by monitoring usage deltas

KEY_FILE="$HOME/.openclaw/agents/main/agent/auth-profiles.json"
LOG_FILE="$HOME/clawd/data/openrouter-daily-cost.log"

# Get API key
KEY=$(cat "$KEY_FILE" | jq -r '.profiles["openrouter:default"].key')

if [ -z "$KEY" ] || [ "$KEY" = "null" ]; then
    echo "⚠️ OpenRouter API key not found"
    exit 1
fi

# Fetch credits
RESPONSE=$(curl -s "https://openrouter.ai/api/v1/credits" -H "Authorization: Bearer $KEY")

if [ -z "$RESPONSE" ] || echo "$RESPONSE" | grep -q "error"; then
    echo "⚠️ Could not fetch OpenRouter data"
    exit 1
fi

# Parse values (API returns dollars, not cents)
TOTAL_CREDITS=$(echo "$RESPONSE" | jq -r '.data.total_credits')
TOTAL_USAGE=$(echo "$RESPONSE" | jq -r '.data.total_usage')
BALANCE=$(echo "scale=2; $TOTAL_CREDITS - $TOTAL_USAGE" | bc)
TODAY=$(date +%Y-%m-%d)

# Ensure log file exists
if [ ! -f "$LOG_FILE" ]; then
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "date,total_usage,daily_cost" > "$LOG_FILE"
fi

# Get yesterday's total usage
YESTERDAY_USAGE=$(tail -n 1 "$LOG_FILE" | cut -d',' -f2)
YESTERDAY_DATE=$(tail -n 1 "$LOG_FILE" | cut -d',' -f1)

# Calculate daily cost (values are in dollars)
if [ -n "$YESTERDAY_USAGE" ] && [ "$YESTERDAY_USAGE" != "total_usage" ] && [ "$YESTERDAY_DATE" != "$TODAY" ]; then
    # New day - calculate spend from yesterday's total
    DAILY_COST=$(echo "scale=2; $TOTAL_USAGE - $YESTERDAY_USAGE" | bc)
    
    # Log today's entry
    echo "$TODAY,$TOTAL_USAGE,$DAILY_COST" >> "$LOG_FILE"
    
    echo "💰 OPENROUTER USAGE"
    echo "Current balance: \$${BALANCE}"
    echo "Yesterday's cost: \$${DAILY_COST}"
    echo "Total API usage: \$${TOTAL_USAGE}"
    echo "Dashboard: https://openrouter.ai/settings/credits"
elif [ "$YESTERDAY_DATE" = "$TODAY" ]; then
    # Already logged today - show current spend
    DAILY_COST=$(tail -n 1 "$LOG_FILE" | cut -d',' -f3)
    echo "💰 OPENROUTER USAGE"
    echo "Current balance: \$${BALANCE}"
    echo "Today's cost so far: \$${DAILY_COST}"
    echo "Total API usage: \$${TOTAL_USAGE}"
else
    # First run - just log
    echo "$TODAY,$TOTAL_USAGE,0" >> "$LOG_FILE"
    echo "💰 OPENROUTER USAGE"
    echo "Current balance: \$${BALANCE}"
    echo "Yesterday's cost: N/A (first run)"
    echo "Total API usage: \$${TOTAL_USAGE}"
fi
