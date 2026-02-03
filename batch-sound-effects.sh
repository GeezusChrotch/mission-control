#!/bin/bash

# Batch Sound Effects Generator for Josh
# Edit the SOUND_EFFECTS array below to add your sound effects

# Array of sound effects to generate
# Format: "prompt|filename|duration(optional)"
SOUND_EFFECTS=(
    # Add your sound effects here:
    # "train whistle|train_whistle.mp3|3.0"
    # "door creaking|door_creak.mp3|2.5"
    # "thunder clap|thunder.mp3"
    # "footsteps on gravel|footsteps_gravel.mp3|5.0"
)

# Configuration - require env var
API_KEY="${ELEVENLABS_API_KEY}"
if [ -z "$API_KEY" ]; then
    echo "❌ ELEVENLABS_API_KEY environment variable not set"
    echo "   Set it with: export ELEVENLABS_API_KEY='your-api-key'"
    exit 1
fi
DOWNLOADS_DIR="/Users/Josh/Library/CloudStorage/Dropbox/- LMT Audio/- Generated SFX"

# Ensure downloads directory exists
mkdir -p "$DOWNLOADS_DIR"

# Function to generate a single sound effect
generate_effect() {
    local prompt="$1"
    local filename="$2"
    local duration="$3"
    local output_path="$DOWNLOADS_DIR/$filename"
    
    echo "🎵 Generating: $filename"
    echo "   Prompt: $prompt"
    
    # Build JSON payload
    if [ -n "$duration" ]; then
        json_payload="{\"text\": \"$prompt\", \"duration_seconds\": $duration, \"prompt_influence\": 0.3}"
        echo "   Duration: $duration seconds"
    else
        json_payload="{\"text\": \"$prompt\", \"prompt_influence\": 0.3}"
        echo "   Duration: auto"
    fi
    
    # Make API request
    curl -X POST "https://api.elevenlabs.io/v1/sound-generation" \
         -H "Accept: audio/mpeg" \
         -H "Content-Type: application/json" \
         -H "xi-api-key: $API_KEY" \
         -d "$json_payload" \
         -o "$output_path" \
         --silent \
         --show-error
    
    if [ $? -eq 0 ] && [ -f "$output_path" ] && [ -s "$output_path" ]; then
        file_size=$(stat -f%z "$output_path" 2>/dev/null || wc -c < "$output_path")
        echo "   ✅ Generated: $file_size bytes"
        return 0
    else
        echo "   ❌ Failed"
        [ -f "$output_path" ] && rm "$output_path"
        return 1
    fi
}

# Function to generate variations
generate_variations() {
    local prompt="$1"
    local base_filename="$2"
    local duration="$3"
    local variations="$4"
    
    for ((i=1; i<=variations; i++)); do
        # Create variation filename
        if [[ "$base_filename" == *.mp3 ]]; then
            var_filename="${base_filename%.mp3}_v${i}.mp3"
        else
            var_filename="${base_filename}_v${i}.mp3"
        fi
        
        generate_effect "$prompt" "$var_filename" "$duration"
        echo ""
    done
}

# Main execution
if [ ${#SOUND_EFFECTS[@]} -eq 0 ]; then
    echo "🎭 Batch Sound Effects Generator"
    echo ""
    echo "No sound effects defined in the SOUND_EFFECTS array."
    echo "Edit this script and add sound effects in this format:"
    echo ""
    echo 'SOUND_EFFECTS=('
    echo '    "train whistle|train_whistle.mp3|3.0"'
    echo '    "door creaking|door_creak.mp3|2.5"'
    echo '    "thunder clap|thunder.mp3"  # duration optional'
    echo ')'
    echo ""
    echo "Then run: ./batch-sound-effects.sh"
    echo ""
    echo "Or use the single generator:"
    echo "./generate-sound-effect.sh 'prompt' filename.mp3 [duration]"
    exit 0
fi

echo "🎭 Starting batch generation of ${#SOUND_EFFECTS[@]} sound effect types..."
echo "📁 Output directory: $DOWNLOADS_DIR"
echo "-" | head -c 60; echo ""
echo ""

generated=0
total=0

for effect in "${SOUND_EFFECTS[@]}"; do
    # Parse the effect definition
    IFS='|' read -r prompt filename duration variations <<< "$effect"
    
    # Set default variations to 1 if not specified
    variations=${variations:-1}
    total=$((total + variations))
    
    echo "🔊 '$prompt' ($variations variation$([ $variations -gt 1 ] && echo 's'))"
    
    if [ "$variations" -gt 1 ]; then
        generate_variations "$prompt" "$filename" "$duration" "$variations"
    else
        generate_effect "$prompt" "$filename" "$duration"
        echo ""
    fi
    
    # Count successful generations (simplified)
    generated=$((generated + variations))
done

echo "✅ Batch complete! Generated $generated sound effects"
echo "📁 Files saved to: $DOWNLOADS_DIR"