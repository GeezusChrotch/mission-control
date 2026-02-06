#!/bin/bash
# Check for new vegan restaurants within 10 miles of Buena Park
# Compares against previously seen spots and reports new ones

# API key from OpenClaw config (skills.local-places.apiKey)
API_KEY="${GOOGLE_PLACES_API_KEY}"
DATA_DIR="/Users/Josh/clawd/data"
KNOWN_FILE="$DATA_DIR/known-vegan-spots.json"

# Buena Park coordinates
LAT="33.8675"
LNG="-118.0103"
RADIUS="16093"  # 10 miles in meters

mkdir -p "$DATA_DIR"

# Query Google Places API for vegan restaurants
RESPONSE=$(curl -s -X POST "https://places.googleapis.com/v1/places:searchText" \
  -H "Content-Type: application/json" \
  -H "X-Goog-Api-Key: $API_KEY" \
  -H "X-Goog-FieldMask: places.id,places.displayName,places.formattedAddress,places.rating,places.googleMapsUri" \
  -d "{
    \"textQuery\": \"vegan restaurant\",
    \"locationBias\": {
      \"circle\": {
        \"center\": {\"latitude\": $LAT, \"longitude\": $LNG},
        \"radius\": $RADIUS
      }
    },
    \"maxResultCount\": 20
  }")

# Extract place IDs and names
CURRENT=$(echo "$RESPONSE" | jq -r '.places[] | {id: .id, name: .displayName.text, address: .formattedAddress, rating: .rating, url: .googleMapsUri}' | jq -s '.')

# Initialize known file if it doesn't exist
if [ ! -f "$KNOWN_FILE" ]; then
  echo "[]" > "$KNOWN_FILE"
fi

# Get known place IDs
KNOWN_IDS=$(jq -r '.[].id' "$KNOWN_FILE" 2>/dev/null | sort -u)

# Find new spots
NEW_SPOTS=""
while read -r place; do
  ID=$(echo "$place" | jq -r '.id')
  if ! echo "$KNOWN_IDS" | grep -q "^$ID$"; then
    if [ -z "$NEW_SPOTS" ]; then
      NEW_SPOTS="$place"
    else
      NEW_SPOTS="$NEW_SPOTS
$place"
    fi
  fi
done < <(echo "$CURRENT" | jq -c '.[]')

# Update known spots file with current list
echo "$CURRENT" > "$KNOWN_FILE"

# Output results
if [ -n "$NEW_SPOTS" ]; then
  echo "🌱 NEW VEGAN SPOTS FOUND!"
  echo ""
  echo "$NEW_SPOTS" | jq -r '"• \(.name) (⭐\(.rating // "N/A"))\n  📍 \(.address)\n  🔗 \(.url)\n"'
else
  echo "No new vegan spots found (tracking $(echo "$CURRENT" | jq length) locations)"
fi
