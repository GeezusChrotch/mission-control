#!/usr/bin/env python3
"""
Simple Sound Effects Batch Generator for Josh

Usage examples:
    python3 sound-effects-batch.py
    # Will prompt for interactive input

Or edit the SOUND_EFFECTS list below and run the script.
"""

import os
import sys
import subprocess
from pathlib import Path

# Configuration
DOWNLOADS_DIR = "/Users/Josh/Library/CloudStorage/Dropbox/- LMT Audio/- Generated SFX"

# Require API key from environment
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    print("❌ ELEVENLABS_API_KEY environment variable not set")
    print("   Set it with: export ELEVENLABS_API_KEY='your-api-key'")
    sys.exit(1)

# ADD YOUR SOUND EFFECTS HERE:
# Format: {"prompt": "description", "filename": "name.mp3", "variations": number}
SOUND_EFFECTS = [
    # EXAMPLE: Uncomment and modify these, or add your own
    # {"prompt": "thunder clap", "filename": "thunder.mp3", "variations": 3},
    # {"prompt": "door creak", "filename": "door_creak.mp3", "variations": 2},
    # {"prompt": "footsteps on gravel", "filename": "footsteps_gravel.mp3", "variations": 2},
]

def generate_sound_effect(prompt, output_path):
    """Generate a single sound effect using Clawdbot's TTS function"""
    try:
        print(f"🎵 Generating: {os.path.basename(output_path)}")
        print(f"   Prompt: {prompt}")
        
        # Use Clawdbot's TTS function (this will use the configured ElevenLabs API key)
        cmd = [
            "clawdbot", "tts", 
            "--output", output_path,
            prompt
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            print(f"   ✅ Generated: {file_size} bytes")
            return True
        else:
            print(f"   ❌ Error: {result.stderr}")
            return False
        
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def run_batch(sound_effects):
    """Generate all sound effects in the list"""
    # Ensure downloads directory exists
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
        
        print(f"\n🔊 '{prompt}' ({variations} variation{'s' if variations > 1 else ''})")
        
        for i in range(1, variations + 1):
            # Create filename with variation number if multiple variations
            if variations > 1:
                name_parts = base_filename.rsplit('.', 1)
                if len(name_parts) == 2:
                    filename = f"{name_parts[0]}_v{i}.{name_parts[1]}"
                else:
                    filename = f"{base_filename}_v{i}.mp3"
            else:
                filename = base_filename
                
            output_path = os.path.join(DOWNLOADS_DIR, filename)
            
            if generate_sound_effect(prompt, output_path):
                total_generated += 1
    
    print(f"\n✅ Batch complete! Generated {total_generated}/{total_requested} sound effects")
    print(f"📁 Files saved to: {DOWNLOADS_DIR}")

def interactive_mode():
    """Let user add sound effects interactively"""
    effects = []
    print("🎭 Interactive Sound Effects Generator")
    print("Enter sound effects one at a time. Press Enter with empty prompt to finish.\n")
    
    while True:
        prompt = input("Sound effect description (or Enter to finish): ").strip()
        if not prompt:
            break
            
        # Suggest filename based on prompt
        suggested_name = prompt.lower().replace(' ', '_').replace(',', '') + '.mp3'
        filename = input(f"Filename [{suggested_name}]: ").strip()
        if not filename:
            filename = suggested_name
            
        try:
            variations = int(input("Number of variations [1]: ") or "1")
        except ValueError:
            variations = 1
            
        effects.append({
            "prompt": prompt,
            "filename": filename,
            "variations": variations
        })
        
        print(f"✅ Added: {variations}x '{prompt}' -> {filename}\n")
    
    return effects

if __name__ == "__main__":
    if SOUND_EFFECTS:
        # Use pre-defined list
        print("Using pre-defined sound effects list:")
        for effect in SOUND_EFFECTS:
            print(f"  - {effect['variations']}x {effect['prompt']} -> {effect['filename']}")
        print()
        
        confirm = input("Continue? [y/N]: ").strip().lower()
        if confirm in ['y', 'yes']:
            run_batch(SOUND_EFFECTS)
        else:
            print("Cancelled.")
    else:
        # Interactive mode
        effects = interactive_mode()
        if effects:
            print(f"\nReady to generate {len(effects)} sound effect types:")
            for effect in effects:
                print(f"  - {effect['variations']}x {effect['prompt']} -> {effect['filename']}")
            
            confirm = input("\nProceed? [y/N]: ").strip().lower()
            if confirm in ['y', 'yes']:
                run_batch(effects)
            else:
                print("Cancelled.")
        else:
            print("No sound effects to generate.")