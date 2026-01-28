#!/usr/bin/env python3
"""
Single sound effect generator using Clawdbot's TTS function
This creates a Python script that can access Clawdbot's TTS functionality
"""

import os
import sys
import tempfile
import subprocess
import json

def generate_sound_effect(prompt, output_path):
    """Generate a sound effect by calling Clawdbot agent with TTS request"""
    try:
        print(f"🎵 Generating: {os.path.basename(output_path)}")
        print(f"   Prompt: {prompt}")
        
        # Create a message for the agent requesting TTS generation
        message = f"Generate a sound effect audio file for: {prompt}. Use the tts tool and tell me the MEDIA path."
        
        # Use clawdbot agent command to generate the TTS
        cmd = [
            "clawdbot", "agent", 
            "--message", message,
            "--json"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Parse the JSON response to find the MEDIA path
            try:
                response = json.loads(result.stdout)
                content = response.get('content', '')
                
                # Look for MEDIA: path in the response
                if 'MEDIA:' in content:
                    media_path = content.split('MEDIA:')[1].strip().split('\n')[0]
                    
                    # Copy the generated file to the desired location
                    import shutil
                    shutil.copy2(media_path, output_path)
                    
                    file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
                    print(f"   ✅ Generated: {file_size} bytes")
                    return True
                else:
                    print(f"   ❌ No MEDIA path found in response: {content}")
                    return False
                    
            except json.JSONDecodeError:
                print(f"   ❌ Could not parse JSON response: {result.stdout}")
                return False
        else:
            print(f"   ❌ Agent command failed: {result.stderr}")
            return False
        
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 generate-sound-effect.py 'prompt' output_file.mp3")
        sys.exit(1)
        
    prompt = sys.argv[1]
    output_path = sys.argv[2]
    
    if generate_sound_effect(prompt, output_path):
        print(f"✅ Sound effect saved to: {output_path}")
    else:
        print("❌ Failed to generate sound effect")
        sys.exit(1)