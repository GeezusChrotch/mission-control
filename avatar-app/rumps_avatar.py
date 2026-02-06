#!/usr/bin/env python3
"""
Roboboogie Avatar - Rumps with floating window
Status bar icon that shows a floating window on click
"""
import rumps
import threading
import time
import os
import json

class RoboboogieAvatar(rumps.App):
    def __init__(self):
        super().__init__("🤖", "Roboboogie")
        self.state = "idle"
        self.window = None
        self.visible = False
        
        # State icons and colors
        self.states = {
            "idle": ("💤", "Idle - No recent activity"),
            "thinking": ("💭", "Thinking - Processing..."),
            "working": ("⚡", "Working - Active tasks"),
            "excited": ("🎉", "Excited - Something interesting!"),
            "subagent": ("🧠", "Subagent - Running background agent")
        }
        
        # Setup menu
        self.show_window_item = rumps.MenuItem("Show Avatar", callback=self.toggle_window)
        self.quit_item = rumps.MenuItem("Quit", callback=self.quit)
        
        self.menu = [
            self.show_window_item,
            None,
            self.quit_item
        ]
        
        # Start monitoring thread
        self.running = True
        self.thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.thread.start()
        
        print("🤖 Roboboogie Avatar started!")
        print("   - Click menu bar icon to show/hide floating window")
        print("   - States: 💤 Idle, 💭 Thinking, ⚡ Working, 🎉 Excited, 🧠 Subagent")
    
    def monitor_loop(self):
        """Background monitoring of Clawdbot state"""
        while self.running:
            try:
                self.check_state()
            except:
                pass
            time.sleep(2)
    
    def check_state(self):
        """Check Clawdbot activity"""
        try:
            home = os.path.expanduser("~")
            sessions_path = os.path.join(home, ".clawdbot", "sessions")
            
            if not os.path.exists(sessions_path):
                new_state = "idle"
            else:
                sessions = [f for f in os.listdir(sessions_path) if f.endswith('.jsonl')]
                if not sessions:
                    new_state = "idle"
                else:
                    current_time = time.time()
                    new_state = "idle"
                    
                    for session_file in sessions:
                        session_path = os.path.join(sessions_path, session_file)
                        try:
                            mod_time = os.path.getmtime(session_path)
                            age = current_time - mod_time
                            
                            if age < 10:
                                new_state = "working"
                                break
                            elif age < 30 and new_state != "working":
                                new_state = "thinking"
                            elif age < 60 and new_state not in ["working", "thinking"]:
                                new_state = "excited"
                        except:
                            continue
            
            # Update UI on main thread
            def update():
                self.update_state(new_state)
            
            rumps Timer(0, update).start()
            
        except Exception as e:
            print(f"Error: {e}")
    
    def update_state(self, new_state):
        """Update the current state"""
        if new_state == self.state:
            return
        
        self.state = new_state
        icon, desc = self.states.get(new_state, self.states["idle"])
        self.title = icon
        
        # Update window if visible
        if self.visible and self.window:
            self.window.set_label(f"{new_state.upper()} {icon}")
            self.window.set_color(self.get_color_for_state(new_state))
        
        print(f"State: {new_state} {icon}")
    
    def get_color_for_state(self, state):
        """Get color hex for state"""
        colors = {
            "idle": "#90EE90",      # Light green
            "thinking": "#87CEEB",  # Light blue
            "working": "#FFC864",   # Orange
            "excited": "#FF9999",   # Pink
            "subagent": "#CC99FF"   # Purple
        }
        return colors.get(state, "#90EE90")
    
    def toggle_window(self, sender):
        """Toggle floating window visibility"""
        if self.visible:
            self.hide_window()
        else:
            self.show_window()
    
    def show_window(self):
        """Show the floating window"""
        if self.visible:
            return
        
        self.visible = True
        self.show_window_item.title = "Hide Avatar"
        
        # Create a simple notification-style window
        icon, desc = self.states.get(self.state, self.states["idle"])
        
        self.window = rumps.Window(
            message=f"Roboboogie Status",
            title=f"🤖 {self.state.upper()} {icon}",
            default_text="",
            dimensions=(200, 100)
        )
        
        # Make it float and add custom styling
        self.window.icon = None  # Will use title instead
        
        # Show as alert (modal but with custom appearance)
        response = self.window.run(show=False)
        
        # Don't close - create a persistent window-like effect
        # For now, just show a notification-style alert
        alert = rumps.Alert(
            title=f"🤖 Roboboogie",
            message=f"Current State: {self.state.upper()} {icon}\n\n{desc}"
        )
        alert.add_button("OK")
        alert.add_button("Keep Open")
        
        result = alert.run()
        if result.clicked == 1:
            # Keep showing updates in terminal
            print("Keeping avatar active...")
        else:
            self.visible = False
            self.show_window_item.title = "Show Avatar"
    
    def hide_window(self):
        """Hide the floating window"""
        self.visible = False
        self.show_window_item.title = "Show Avatar"
        self.window = None
    
    def quit(self, sender):
        """Quit the application"""
        self.running = False
        rumps.quit_application()


if __name__ == "__main__":
    app = RoboboogieAvatar()
    app.run()