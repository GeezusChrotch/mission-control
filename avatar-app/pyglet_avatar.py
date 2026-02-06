#!/usr/bin/env python3
"""
Roboboogie Floating Avatar - Pyglet
Simple always-on-top floating window
"""
import pyglet
from pyglet.window import Window
from pyglet.shapes import Circle, Rectangle, Line
from pyglet.text import Label
from pyglet import clock
import threading
import time
import os

# State colors and settings
STATES = {
    "idle": {"color": (144, 238, 144, 255), "icon": "💤", "status": "IDLE"},
    "thinking": {"color": (135, 206, 250, 255), "icon": "💭", "status": "THINKING"},
    "working": {"color": (255, 200, 100, 255), "icon": "⚡", "status": "WORKING"},
    "excited": {"color": (255, 150, 150, 255), "icon": "🎉", "status": "EXCITED"},
    "subagent": {"color": (200, 150, 255, 255), "icon": "🧠", "status": "SUBAGENT"}
}

class RoboboogieWindow(Window):
    def __init__(self):
        super().__init__(width=220, height=280, caption="🤖 Roboboogie",
                        resizable=False, vsync=True)
        
        # Make floating and always on top
        self.set_location(100, 400)
        
        # State
        self.current_state = "idle"
        self.last_activity = time.time()
        
        # Batch for drawing
        self.batch = pyglet.graphics.Batch()
        
        # Create UI elements
        self.create_ui()
        
        # Start monitoring thread
        self.running = True
        self.thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.thread.start()
        
        # Schedule update
        clock.schedule_interval(self.update, 1/30.0)
        
        print("🤖 Roboboogie Avatar started!")
        print("  - Floating window (always on top)")
        print("  - Close window to exit")
        print("  - States: 💤 Idle, 💭 Thinking, ⚡ Working, 🎉 Excited, 🧠 Subagent")
    
    def create_ui(self):
        """Create all UI elements"""
        self.update_ui()
    
    def update_ui(self):
        """Update UI elements based on current state"""
        config = STATES.get(self.current_state, STATES["idle"])
        color = config["color"]
        
        # Clear old shapes
        self.batch = pyglet.graphics.Batch()
        
        # Face background (shadow)
        cx, cy = 110, 150
        r = 90
        
        # Shadow
        shadow = Circle(cx, cy - 10, r + 5, color=(0, 0, 0, 50), batch=self.batch)
        
        # Face
        face = Circle(cx, cy, r, color=color[:3], batch=self.batch)
        
        # Eyes (white background)
        eye_r = 20
        eye_offset = 35
        left_eye_bg = Circle(cx - eye_offset, cy - 10, eye_r, color=(255, 255, 255), batch=self.batch)
        right_eye_bg = Circle(cx + eye_offset, cy - 10, eye_r, color=(255, 255, 255), batch=self.batch)
        
        # Pupils
        pupil_r = 10
        pupil_color = (45, 90, 61)
        
        # Eye animation for thinking
        if self.current_state == "thinking":
            offset_x = int(time.time() * 50) % 10 - 5
        else:
            offset_x = 0
        
        left_pupil = Circle(cx - eye_offset + 5 + offset_x, cy - 10 + 3, pupil_r, color=pupil_color, batch=self.batch)
        right_pupil = Circle(cx + eye_offset + 5 + offset_x, cy - 10 + 3, pupil_r, color=pupil_color, batch=self.batch)
        
        # Antenna (thicker line using multiple lines)
        antenna_color = (45, 90, 61)
        antenna = Rectangle(cx - 4, cy + r - 20, 8, 30, color=antenna_color, batch=self.batch)
        
        # Antenna ball
        ball_colors = {
            "idle": (231, 76, 60),
            "thinking": (52, 152, 219),
            "working": (243, 156, 18),
            "excited": (46, 204, 113),
            "subagent": (155, 89, 182)
        }
        ball_color = ball_colors.get(self.current_state, ball_colors["idle"])
        ball_radius = 12
        if self.current_state == "working":
            ball_radius = 15  # Larger when working
        antenna_ball = Circle(cx, cy + r + 5, ball_radius, color=ball_color, batch=self.batch)
        
        # Mouth based on state
        mouth_y = cy + 25
        if self.current_state == "idle":
            # Small smile arc
            mouth = Rectangle(cx - 15, mouth_y + 5, 30, 4, color=pupil_color, batch=self.batch)
        elif self.current_state == "thinking":
            # Straight line
            mouth = Rectangle(cx - 15, mouth_y, 30, 4, color=pupil_color, batch=self.batch)
        elif self.current_state == "working":
            # Focused line
            mouth = Rectangle(cx - 20, mouth_y + 5, 40, 4, color=pupil_color, batch=self.batch)
        elif self.current_state == "excited":
            # Open mouth (ellipse-ish)
            mouth_bg = Circle(cx, mouth_y + 10, 15, color=(45, 90, 61), batch=self.batch)
            mouth_bg.opacity = 255
        else:  # subagent
            # Wavy line
            mouth = Rectangle(cx - 20, mouth_y, 40, 3, color=pupil_color, batch=self.batch)
        
        # Status label (below face)
        status_text = f"{config['status']} {config['icon']}"
        self.status_label = Label(
            status_text,
            font_name='Arial',
            font_size=16,
            x=self.width // 2,
            y=35,
            anchor_x='center',
            anchor_y='center',
            color=(50, 50, 50, 255),
            batch=self.batch
        )
        
        # Title bar replacement (simple border at top)
        title_bg = Rectangle(0, self.height - 25, self.width, 25, color=(240, 240, 240), batch=self.batch)
        self.close_btn = Label(
            "✕",
            font_name='Arial',
            font_size=14,
            x=self.width - 15,
            y=self.height - 13,
            anchor_x='center',
            anchor_y='center',
            color=(100, 100, 100, 255),
            batch=self.batch
        )
    
    def on_draw(self):
        """Render the window"""
        self.clear()
        self.batch.draw()
    
    def update(self, dt):
        """Called every frame"""
        # Check for close button hover/click (simple version)
        pass
    
    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse clicks"""
        # Close button area (top right)
        if (self.width - 30 < x < self.width and 
            self.height - 25 < y < self.height):
            self.close()
    
    def on_close(self):
        """Handle window close"""
        self.running = False
        super().on_close()
    
    def set_state(self, state):
        """Update the avatar state"""
        if state == self.current_state:
            return
        self.current_state = state
        self.update_ui()
    
    def monitor_loop(self):
        """Background monitoring of Clawdbot state"""
        while self.running:
            try:
                new_state = self._check_clawdbot()
                if new_state != self.current_state:
                    print(f"State: {self.current_state} -> {new_state}")
                    pyglet.clock.schedule_once(lambda dt: self.set_state(new_state), 0)
            except:
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


def main():
    # Create window with specific options
    config = pyglet.gl.Config(sample_buffers=1, samples=4)
    window = RoboboogieWindow()
    pyglet.app.run()


if __name__ == "__main__":
    main()
