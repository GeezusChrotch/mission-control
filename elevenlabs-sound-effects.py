#!/usr/bin/env python3
"""
ElevenLabs Sound Effects Generator
Uses the proper text-to-sound-effects API endpoint
"""

import os
import sys
import requests
import json

# Configuration
DOWNLOADS_DIR = "/Users/Josh/Library/CloudStorage/Dropbox/- LMT Audio/- Generated SFX"
ELEVENLABS_API_KEY = "sk_b415fc3ebc3cdacbcef90b4c68f55424c515648c2b6fd66c"
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-sound-effects/convert"

def generate_sound_effect(prompt, output_path, duration=None, loop=False):
    """Generate a sound effect using ElevenLabs text-to-sound-effects API"""
    try:
        print(f"🎵 Generating: {os.path.basename(output_path)}")
        print(f"   Prompt: {prompt}")
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        data = {
            "text": prompt,
            "model_id": "eleven_text_to_sound_v2",
            "prompt_influence": 0.3,
            "loop": loop
        }
        
        if duration:
            data["duration_seconds"] = duration
            
        print(f"   Duration: {duration or 'auto'} seconds")
        print(f"   Loop: {loop}")
        
        response = requests.post(ELEVENLABS_API_URL, json=data, headers=headers)
        
        if response.status_code == 200:
            # Save the audio file
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            file_size = os.path.getsize(output_path)
            character_cost = response.headers.get('character-cost', 'unknown')
            print(f"   ✅ Generated: {file_size:,} bytes (cost: {character_cost} chars)")
            return True
        else:
            print(f"   ❌ API Error {response.status_code}: {response.text}")
            return False
        
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def batch_generate(sound_effects):
    """Generate multiple sound effects"""
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    
    total_requested = sum(effect.get('variations', 1) for effect in sound_effects)
    total_generated = 0
    
    print(f"🎭 Starting batch generation of {total_requested} sound effects...")
    print(f"📁 Output directory: {DOWNLOADS_DIR}")
    print("-" * 60)
    
    for effect in sound_effects:
        prompt = effect['prompt']
        base_filename = effect['filename']
        variations = effect.get('variations', 1)
        duration = effect.get('duration')
        loop = effect.get('loop', False)
        
        print(f"\n🔊 '{prompt}' ({variations} variation{'s' if variations > 1 else ''})")
        
        for i in range(1, variations + 1):
            if variations > 1:
                name_parts = base_filename.rsplit('.', 1)
                if len(name_parts) == 2:
                    filename = f"{name_parts[0]}_v{i}.{name_parts[1]}"
                else:
                    filename = f"{base_filename}_v{i}.mp3"
            else:
                filename = base_filename if base_filename.endswith('.mp3') else f"{base_filename}.mp3"
                
            output_path = os.path.join(DOWNLOADS_DIR, filename)
            
            if generate_sound_effect(prompt, output_path, duration, loop):
                total_generated += 1
    
    print(f"\n✅ Batch complete! Generated {total_generated}/{total_requested} sound effects")
    print(f"📁 Files saved to: {DOWNLOADS_DIR}")

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) == 1:
        # Interactive mode
        print("🎭 ElevenLabs Sound Effects Generator")
        prompt = input("Sound effect description: ").strip()
        if not prompt:
            print("No prompt provided")
            sys.exit(1)
            
        filename = input(f"Filename (default: {prompt.lower().replace(' ', '_')}.mp3): ").strip()
        if not filename:
            filename = f"{prompt.lower().replace(' ', '_')}.mp3"
            
        duration_input = input("Duration in seconds (0.5-30, or enter for auto): ").strip()
        duration = float(duration_input) if duration_input else None
        
        loop_input = input("Should it loop? (y/N): ").strip().lower()
        loop = loop_input in ['y', 'yes']
        
        output_path = os.path.join(DOWNLOADS_DIR, filename)
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)
        
        if generate_sound_effect(prompt, output_path, duration, loop):
            print(f"\n✅ Sound effect saved to: {output_path}")
        else:
            print("\n❌ Failed to generate sound effect")
    
    elif len(sys.argv) >= 3:
        # Command line mode
        prompt = sys.argv[1]
        filename = sys.argv[2]
        duration = float(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].replace('.', '').isdigit() else None
        
        output_path = os.path.join(DOWNLOADS_DIR, filename)
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)
        
        if generate_sound_effect(prompt, output_path, duration):
            print(f"\n✅ Sound effect saved to: {output_path}")
        else:
            print("\n❌ Failed to generate sound effect")
            sys.exit(1)
    
    else:
        print("Usage:")
        print("  python3 elevenlabs-sound-effects.py  # Interactive mode")
        print("  python3 elevenlabs-sound-effects.py 'prompt' filename.mp3 [duration]")
        print("Examples:")
        print("  python3 elevenlabs-sound-effects.py 'train whistle' train_whistle.mp3 3.0")
        print("  python3 elevenlabs-sound-effects.py 'door creaking' door_creak.mp3")