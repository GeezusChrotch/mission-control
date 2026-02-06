#!/bin/bash

# Remove existing blogs first
echo "Removing existing blogs..."
echo y | blogwatcher remove "Democracy Now" 2>/dev/null || true
echo y | blogwatcher remove "LA Times - California" 2>/dev/null || true
echo y | blogwatcher remove "The Intercept" 2>/dev/null || true

# Add with exact URLs
echo "Adding blogs with proper feeds..."
blogwatcher add "The Intercept" "https://theintercept.com/feed/"
blogwatcher add "Democracy Now" "https://www.democracynow.org/podcast.xml"
blogwatcher add "LA Times - California" "https://www.latimes.com/california/rss2.0.xml"

echo ""
echo "Current tracked blogs:"
blogwatcher blogs

echo ""
echo "Testing scan..."
blogwatcher scan