#!/usr/bin/env python3
"""
Roboboogie Floating Avatar - Status Bar + Popup Window
Uses rumps for status bar and creates a simple always-on-top window
"""
import rumps
import threading
import time
import os
import sys
from rumps import timer

class RoboboogieAvatar(rumps.App):
    def __init__(self):
        super().__init__("🤖", "Roboboogie")
        self.state = "idle"
        self.window_visible = False
        self.window_process = None
        
        # State configuration
        self.state_config = {
            "idle": {"icon": "💤", "color": "#90EE90", "desc": "Idle - No recent activity"},
            "thinking": {"icon": "💭", "color": "#87CEEB", "desc": "Thinking - Processing..."},
            "working": {"icon": "⚡", "color": "#FFC864", "desc": "Working - Active tasks"},
            "excited": {"icon": "🎉", "color": "#FF9999", "desc": "Excited - Something interesting!"},
            "subagent": {"icon": "🧠", "color": "#CC99FF", "desc": "Subagent - Running background agent"}
        }
        
        # Menu items
        self.show_btn = rumps.MenuItem("Show Window", callback=self.toggle_window)
        self.status_item = rumps.MenuItem("Status: IDLE 💤")
        self.quit_btn = rumps.MenuItem("Quit", callback=self.quit_app)
        
        self.menu = [self.show_btn, self.status_item, None, self.quit_btn]
        
        # Start monitoring
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        
        print("🤖 Roboboogie Avatar started!")
        print("  - Click 'Show Window' in menu to see avatar")
        print("  - States: 💤 Idle, 💭 Thinking, ⚡ Working, 🎉 Excited, 🧠 Subagent")
    
    def _monitor_loop(self):
        """Background loop to check Clawdbot state"""
        while self.running:
            try:
                new_state = self._check_clawdbot()
                if new_state != self.state:
                    self._update_state(new_state)
            except Exception as e:
                pass
            time.sleep(2)
    
    def _check_clawdbot(self):
        """Check Clawdbot session activity"""
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
    
    def _update_state(self, new_state):
        """Update state on main thread"""
        self.state = new_state
        config = self.state_config.get(new_state, self.state_config["idle"])
        
        self.title = config["icon"]
        self.status_item.title = f"Status: {new_state.upper()} {config['icon']}"
        
        print(f"State: {new_state} {config['icon']}")
    
    def toggle_window(self, sender):
        """Toggle floating window"""
        if self.window_visible:
            self._hide_window()
        else:
            self._show_window()
    
    def _show_window(self):
        """Show the floating avatar window using rumps.Alert as a popup"""
        self.window_visible = True
        self.show_btn.title = "Hide Window"
        
        config = self.state_config.get(self.state, self.state_config["idle"])
        icon = config["icon"]
        
        # Create a visual popup using rumps
        alert = rumps.Alert(
            title=f"🤖 Roboboogie Avatar",
            message=f"Current State: {self.state.upper()}\n{icon} {config['desc']}"
        )
        alert.add_button("OK - Keep Running")
        alert.add_button("Close")
        
        result = alert.run()
        
        if result.clicked == 1:  # Close button
            self._hide_window()
        # If OK clicked, window stays visible (next update will show)
        
        # For now, just close since rumps doesn't support persistent windows
        self.window_visible = False
        self.show_btn.title = "Show Window"
    
    def _hide_window(self):
        """Hide the window"""
        self.window_visible = False
        self.show_btn.title = "Show Window"
    
    def quit_app(self, sender):
        """Quit the application"""
        self.running = False
        rumps.quit_application()


if __name__ == "__main__":
    app = RoboboogieAvatar()
    app.run()
