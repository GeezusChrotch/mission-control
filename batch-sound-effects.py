#!/usr/bin/env python3
"""
Batch Sound Effect Generator using ElevenLabs
Creates multiple variations of sound effects and saves them to LMT Downloads folder.

Usage: python3 batch-sound-effects.py
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Configuration
DOWNLOADS_DIR = "/Users/Josh/Library/CloudStorage/Dropbox/- LMT Audio/LMT Downloads"

# Require API key from environment
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    print("❌ ELEVENLABS_API_KEY environment variable not set")
    print("   Set it with: export ELEVENLABS_API_KEY='your-api-key'")
    sys.exit(1)

def generate_sound_effect(prompt, filename, variation_num=None):
    """Generate a single sound effect using ElevenLabs via sag"""
    try:
        # Create full filename with variation number if specified
        if variation_num is not None:
            name_parts = filename.rsplit('.', 1)
            if len(name_parts) == 2:
                full_filename = f"{name_parts[0]}_v{variation_num}.{name_parts[1]}"
            else:
                full_filename = f"{filename}_v{variation_num}.mp3"  # Default to mp3
        else:
            full_filename = filename
            
        output_path = os.path.join(DOWNLOADS_DIR, full_filename)
        
        print(f"Generating: {full_filename}")
        print(f"Prompt: {prompt}")
        
        # Set ElevenLabs API key for sag
        env = os.environ.copy()
        env['ELEVENLABS_API_KEY'] = ELEVENLABS_API_KEY
        
        # Use sag to generate the sound effect
        cmd = [
            "sag", 
            "-o", output_path,  # Output file
            prompt  # The sound effect prompt
        ]
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Generated: {output_path}")
            return True
        else:
            print(f"❌ Error generating {filename}: {result.stderr}")
            return False
        
    except Exception as e:
        print(f"❌ Error generating {filename}: {e}")
        return False

def batch_generate(sound_effects_list):
    """
    Generate multiple sound effects from a list
    
    sound_effects_list should be a list of dictionaries like:
    [
        {"prompt": "thunder clap", "filename": "thunder.wav", "variations": 3},
        {"prompt": "door creak", "filename": "door_creak.wav", "variations": 2}
    ]
    """
    
    # Ensure downloads directory exists
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    
    total_generated = 0
    total_requested = sum(effect.get('variations', 1) for effect in sound_effects_list)
    
    print(f"🎵 Starting batch generation of {total_requested} sound effects...")
    print(f"📁 Output directory: {DOWNLOADS_DIR}")
    print("-" * 60)
    
    for effect in sound_effects_list:
        prompt = effect['prompt']
        filename = effect['filename']
        variations = effect.get('variations', 1)
        
        print(f"\n🔊 Generating '{prompt}' ({variations} variation{'s' if variations > 1 else ''})")
        
        for i in range(1, variations + 1):
            if generate_sound_effect(prompt, filename, i if variations > 1 else None):
                total_generated += 1
    
    print(f"\n✅ Batch complete! Generated {total_generated}/{total_requested} sound effects")
    print(f"📁 Files saved to: {DOWNLOADS_DIR}")

if __name__ == "__main__":
    # Example usage
    example_effects = [
        {"prompt": "thunder clap", "filename": "thunder.wav", "variations": 2},
        {"prompt": "door creak", "filename": "door_creak.wav", "variations": 3},
        {"prompt": "footsteps on gravel", "filename": "footsteps_gravel.wav", "variations": 2}
    ]
    
    print("This is a template script for batch sound effect generation.")
    print("To use it, modify the sound_effects_list and run the script.")
    print("\nExample:")
    print(json.dumps(example_effects, indent=2))