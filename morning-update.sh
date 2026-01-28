#!/bin/bash
# Morning RSS update script

cd "$(dirname "$0")"

echo "🌅 Good morning! Here's your news update:"
echo ""

python3 morning-rss.py

echo ""
echo "📅 Generated on $(date)"