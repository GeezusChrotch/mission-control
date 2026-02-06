#!/bin/bash

# Browser Use API wrapper for Josh
# Usage: ./browser-use-wrapper.sh "task description"

export BROWSER_USE_API_KEY="bu_uARq8de-VBvWKKTO_odO18j2aP-RiWrY6RCylQYnvB4"

if [ $# -eq 0 ]; then
    echo "Usage: $0 \"task description\""
    echo "Example: $0 \"Go to the La Mirada Theatre website and find upcoming shows\""
    exit 1
fi

cd /Users/Josh/clawd/skills/browser-use-api
./scripts/browser-use.sh "$1"