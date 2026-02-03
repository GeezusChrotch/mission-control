#!/usr/bin/env python3
"""
Roboboogie Avatar - AppleScript Floating Window
Creates an AppleScript dialog that updates in real-time
"""
import subprocess
import threading
import time
import os
import sys
import tempfile

class RoboboogieAppleScript:
    def __init__(self):
        self.state = "idle"
        self.running = True
        self.script_process = None
        
        self.states = {
            "idle": {"icon": "💤", "color": "green", "desc": "Idle - No recent activity"},
            "thinking": {"icon": "💭", "color": "blue", "desc": "Thinking - Processing..."},
            "working": {"icon": "⚡", "color": "orange", "desc": "Working - Active tasks"},
            "excited": {"icon": "🎉", "color": "red", "desc": "Excited - Something interesting!"},
            "subagent": {"icon": "🧠", "color": "purple", "desc": "Subagent - Running background agent"}
        }
    
    def create_applescript(self, state):
        """Generate AppleScript for current state"""
        config = self.states.get(state, self.states["idle"])
        icon = config["icon"]
        
        # AppleScript that shows a floating dialog
        script = f'''
tell application "System Events"
    -- Try to close any existing dialog
    try
        tell window "🤖 Roboboogie" of process "osascript"
            click button "Close" of it
        end tell
    end try
    
    -- Create new dialog using AppleScript's display dialog
    tell application "AppleScript Editor"
        activate
        display dialog "🤖 Roboboogie" & return & return & "{state.upper()} {icon}" with title "🤖 Roboboogie Avatar" with icon note buttons {{"Close"}} default button "Close" giving up after 60
    end tell
end tell
'''
        return script
    
    def update_display(self, state):
        """Update the AppleScript display"""
        try:
            # Kill any existing osascript process
            subprocess.run(["pkill", "-f", "osascript.*Roboboogie"], capture_output=True)
            time.sleep(0.1)
            
            config = self.states.get(state, self.states["idle"])
            icon = config["icon"]
            
            # Create a simple notification-style AppleScript
            script = f'''
tell application "System Events"
    tell application "AppleScript Editor" to activate
    display dialog "🤖 Roboboogie" & return & return & "{state.upper()} {icon}" with title "🤖 Roboboogie Avatar" with icon note buttons {{"Close"}} default button "Close" giving up after 30
end tell
'''
            
            # Run AppleScript (this will block until dialog closes or times out)
            proc = subprocess.Popen(
                ["osascript", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = proc.communicate(input=script, timeout=5)
            
        except Exception as e:
            pass  # Dialog likely closed or timed out
    
    def monitor_loop(self):
        """Background monitoring loop"""
        while self.running:
            try:
                new_state = self._check_clawdbot()
                if new_state != self.state:
                    old_state = self.state
                    self.state = new_state
                    print(f"State: {old_state} -> {new_state}")
                    self.update_display(new_state)
            except Exception as e:
                pass
            time.sleep(2)
    
    def _check_clawdbot(self):
        """Check Clawdbot activity"""
        home = os.path.expanduser("~")
        sessions_path = os.path.join(home, ".clawdbot", "sessions")
        
        if not os.path.exists(sessions_path):
            return "idle"
        
        sessions = [f for f in os.listdir(sessions_path) if f.endswith('.jsonl')]
        if not sessions:
            return "idle"
        
        current_time = time.time()
        state = "idle"
        
        for session_file in sessions:
            try:
                session_path = os.path.join(sessions_path, session_file)
                mod_time = os.path.getmtime(session_path)
                age = current_time - mod_time
                
                if age < 10:
                    return "working"
                elif age < 30 and state != "working":
                    state = "thinking"
                elif age < 60 and state not in ["working", "thinking"]:
                    state = "excited"
            except:
                continue
        
        return state
    
    def run(self):
        """Start the avatar"""
        print("🤖 Roboboogie AppleScript Avatar started!")
        print("  - Shows dialog popup on state change")
        print("  - Auto-closes after 30 seconds")
        print("  - States: 💤 Idle, 💭 Thinking, ⚡ Working, 🎉 Excited, 🧠 Subagent")
        print()
        
        # Initial display
        self.update_display(self.state)
        
        # Start background monitoring
        self.monitor_loop()


if __name__ == "__main__":
    avatar = RoboboogieAppleScript()
    avatar.run()
