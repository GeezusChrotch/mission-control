#!/bin/bash
# OpenClaw Usage Reporter
# Aggregates costs from all session files

SESSIONS_DIR="$HOME/.openclaw/agents/main/sessions"
LOG_FILE="$HOME/clawd/data/openclaw-daily-cost.log"

# Get today's date
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d)

# Calculate cost for a specific date
calculate_day_cost() {
    local target_date=$1
    local total=0
    
    for session in "$SESSIONS_DIR"/*.jsonl; do
        if [ -f "$session" ]; then
            local cost=$(grep "\"$target_date" "$session" 2>/dev/null | \
                grep -o '"cost":{[^}]*}' | \
                grep -o '"total":[0-9.]*' | \
                cut -d: -f2 | \
                awk '{sum+=$1} END {printf "%.4f\n", sum}')
            if [ -n "$cost" ] && [ "$cost" != "0.0000" ]; then
                total=$(echo "$total + $cost" | bc)
            fi
        fi
    done
    
    echo "$total"
}

# Calculate today's cost
TODAY_COST=$(calculate_day_cost "$TODAY")

# Ensure log file exists
if [ ! -f "$LOG_FILE" ]; then
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "date,cost" > "$LOG_FILE"
fi

# Log today's cost
LAST_DATE=$(tail -n 1 "$LOG_FILE" | cut -d',' -f1)
if [ "$LAST_DATE" != "$TODAY" ] && [ "$TODAY_COST" != "0" ]; then
    echo "$TODAY,$TODAY_COST" >> "$LOG_FILE"
fi

# Get yesterday's cost from log
YESTERDAY_COST=$(grep "^$YESTERDAY," "$LOG_FILE" | cut -d',' -f2)
if [ -z "$YESTERDAY_COST" ]; then
    YESTERDAY_COST=$(calculate_day_cost "$YESTERDAY")
fi

# Calculate last 30 days
LAST_30D=0
for i in {0..29}; do
    CHECK_DATE=$(date -v-${i}d +%Y-%m-%d 2>/dev/null || date -d "-$i days" +%Y-%m-%d)
    DAY_COST=$(grep "^$CHECK_DATE," "$LOG_FILE" | cut -d',' -f2)
    if [ -z "$DAY_COST" ]; then
        DAY_COST=$(calculate_day_cost "$CHECK_DATE")
    fi
    if [ -n "$DAY_COST" ]; then
        LAST_30D=$(echo "$LAST_30D + $DAY_COST" | bc)
    fi
done

# Output formatted report
echo "💰 OPENCLAW USAGE"
echo "Today's cost: \$$(echo "scale=2; $TODAY_COST" | bc)"
if [ -n "$YESTERDAY_COST" ] && [ "$YESTERDAY_COST" != "0" ]; then
    echo "Yesterday's cost: \$$(echo "scale=2; $YESTERDAY_COST" | bc)"
fi
echo "Last 30 days: \$$(echo "scale=2; $LAST_30D" | bc)"
