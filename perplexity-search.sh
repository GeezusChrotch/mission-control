#!/bin/bash

# Perplexity Search Wrapper for Josh
# Usage: ./perplexity-search.sh "search query"

if [ $# -eq 0 ]; then
    echo "Usage: $0 \"search query\""
    echo "Example: $0 \"latest theater sound design trends\""
    exit 1
fi

QUERY="$1"
# API Key - prefer env var, fallback to config
API_KEY="${PERPLEXITY_API_KEY:-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}"

echo "🔮 Searching with Perplexity AI..."
echo "Query: $QUERY"
echo ""

cd /Users/Josh/clawd/skills/perplexity
PERPLEXITY_API_KEY="$API_KEY" node scripts/search.mjs "$QUERY"