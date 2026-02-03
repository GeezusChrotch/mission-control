#!/usr/bin/env python3
"""
Roboboogie Status Bar Avatar
Shows different states based on Clawdbot activity in macOS menu bar
"""
import rumps
import time
import os
import json
from threading import Thread

class RoboboogieStatusBar(rumps.App):
    def __init__(self):
        super().__init__("🤖", "Roboboogie")
        self.state = "idle"
        self.last_activity = time.time()
        self.timeout = 60
        
        # State icons (emoji)
        self.icons = {
            "idle": "💤",
            "thinking": "💭",
            "working": "⚡",
            "excited": "🎉",
            "subagent": "🧠"
        }
        
        # State colors
        self.colors = {
            "idle": "⚪",
            "thinking": "🔵",
            "working": "🟠",
            "excited": "🔴",
            "subagent": "🟣"
        }
        
        # Timer to check Clawdbot state
        self.timer = rumps.Timer(self.check_state, 2)
        self.timer.start()
        
        # Status menu items
        self.status_item = rumps.MenuItem("Status: IDLE")
        self.activity_item = rumps.MenuItem("Last activity: Just now")
        self.quit_btn = rumps.MenuItem("Quit", callback=self.quit_app)
        
        self.menu = [
            self.status_item,
            self.activity_item,
            None,
            self.quit_btn
        ]
        
        print("🤖 Roboboogie Status Bar started!")
        print("   - Icon shows in menu bar")
        print("   - Updates based on Clawdbot activity")
        print("   - States: Idle 💤, Thinking 💭, Working ⚡, Excited 🎉, Subagent 🧠")
    
    def check_state(self, _):
        """Check Clawdbot state"""
        try:
            home = os.path.expanduser("~")
            sessions_path = os.path.join(home, ".clawdbot", "sessions")
            
            if not os.path.exists(sessions_path):
                return
            
            sessions = [f for f in os.listdir(sessions_path) if f.endswith('.jsonl')]
            if not sessions:
                return
            
            current_time = time.time()
            state = "idle"
            
            for session_file in sessions:
                session_path = os.path.join(sessions_path, session_file)
                try:
                    mod_time = os.path.getmtime(session_path)
                    age = current_time - mod_time
                    
                    if age < 10:
                        state = "working"
                        break
                    elif age < 30 and state != "working":
                        state = "thinking"
                    elif age < 60 and state not in ["working", "thinking"]:
                        state = "excited"
                except:
                    continue
            
            self.set_state(state)
            
        except Exception as e:
            pass
    
    def set_state(self, state):
        """Update the status bar state"""
        if state == self.current_state:
            return
        
        self.current_state = state
        icon = self.icons.get(state, "💤")
        color = self.colors.get(state, "⚪")
        
        self.title = icon
        self.status_item.title = f"Status: {state.upper()} {icon}"
        
        time_ago = int(time.time() - self.last_activity)
        if time_ago < 60:
            time_str = f"{time_ago}s ago"
        else:
            time_str = f"{time_ago//60}m ago"
        self.activity_item.title = f"Last activity: {time_str}"
        
        print(f"State: {state} {icon}")
    
    def quit_app(self, _):
        """Quit the application"""
        self.timer.stop()
        rumps.quit_application()


if __name__ == "__main__":
    app = RoboboogieStatusBar()
    app.run()