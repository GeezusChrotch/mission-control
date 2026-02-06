#!/usr/bin/env python3
"""
Roboboogie Floating Avatar - Image version
Shows different states with custom robot images
"""
import tkinter as tk
import os
import time

class RoboboogieAvatar:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 Roboboogie")
        self.root.configure(bg='black')
        self.root.overrideredirect(True)
        self.root.geometry('+100+100')
        self.root.attributes('-topmost', True)
        
        # Make draggable
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        
        self.root.bind('<Button-1>', self.start_drag)
        self.root.bind('<B1-Motion>', self.do_drag)
        self.root.bind('<Double-Button-1>', self.close)
        
        # State
        self.state = 'idle'
        
        # Load images
        self.images = {}
        self.load_images()
        
        # Create image label
        self.image_label = tk.Label(self.root, image=self.images.get('idle'), bg='black')
        self.image_label.pack(padx=10, pady=(10, 0))
        
        # State label
        self.label = tk.Label(self.root, text='IDLE', font=('Arial', 12, 'bold'),
                              bg='black', fg='#00FF00')
        self.label.pack(pady=(0, 10))
        
        # Initial state
        self.update_state('idle')
        
        # Update loop
        self.update_check()
        
        print("🤖 Roboboogie Avatar started!")
        print("   - Drag to move")
        print("   - Double-click to close")
        
        self.root.mainloop()
    
    def load_images(self):
        """Load all avatar images"""
        # Images are in /Users/Josh/clawd/
        avatar_dir = '/Users/Josh/clawd'
        
        image_files = {
            'idle': 'avatar_bender_idle.png',
            'thinking': 'avatar_bender_thinking.png',
            'working': 'avatar_bender_working.png',
            'excited': 'avatar_bender_excited.png',
            'subagent': 'avatar_bender_subagent.png',
        }
        
        for state, filename in image_files.items():
            filepath = os.path.join(avatar_dir, filename)
            if os.path.exists(filepath):
                try:
                    img = tk.PhotoImage(file=filepath)
                    # Scale down to ~300px wide (crisp, not pixelated)
                    scale = max(1, int(img.width() / 300))
                    if scale > 1:
                        img = img.subsample(scale, scale)
                    self.images[state] = img
                    print(f"Loaded {state}: {img.width()}x{img.height()}")
                except Exception as e:
                    print(f"Failed to load {filename}: {e}")
                    self.images[state] = None
            else:
                print(f"Image not found: {filepath}")
                self.images[state] = None
    
    def start_drag(self, event):
        self.dragging = True
        self.offset_x = event.x
        self.offset_y = event.y
    
    def do_drag(self, event):
        if self.dragging:
            x = self.root.winfo_x() + event.x - self.offset_x
            y = self.root.winfo_y() + event.y - self.offset_y
            self.root.geometry(f'+{x}+{y}')
    
    def close(self, event=None):
        self.root.destroy()
    
    def update_state(self, new_state):
        self.state = new_state
        if new_state in self.images and self.images[new_state]:
            self.image_label.config(image=self.images[new_state])
        
        colors = {
            'idle': '#00FF00',
            'thinking': '#00BFFF',
            'working': '#FFD700',
            'excited': '#FF6B6B',
            'subagent': '#9B59B6',
        }
        self.label.config(text=new_state.upper(), fg=colors.get(new_state, '#00FF00'))
    
    def check_state(self):
        """Check OpenClaw session activity including subagents"""
        try:
            home = os.path.expanduser("~")
            sessions_path = os.path.join(home, ".openclaw", "agents", "main", "sessions")
            
            if not os.path.exists(sessions_path):
                return 'idle'
            
            current_time = time.time()
            newest_time = 0
            
            # Check all sessions for subagent activity and track newest
            for f in os.listdir(sessions_path):
                if f.endswith('.jsonl'):
                    try:
                        session_file = os.path.join(sessions_path, f)
                        mtime = os.path.getmtime(session_file)
                        age = current_time - mtime
                        
                        # Track newest file
                        if mtime > newest_time:
                            newest_time = mtime
                        
                        # Check for subagent activity in recent sessions
                        if age < 30:
                            with open(session_file, 'r') as sf:
                                content = sf.read()
                                if 'subagent' in content or 'sessions_spawn' in content:
                                    if age < 20:
                                        return 'subagent'
                    except:
                        pass
            
            if newest_time == 0:
                return 'idle'
            
            age = current_time - newest_time
            
            if age < 10:
                return 'working'
            elif age < 30:
                return 'thinking'
            elif age < 60:
                return 'excited'
            else:
                return 'idle'
                
        except Exception as e:
            return 'idle'
    
    def update_check(self):
        """Periodic state check"""
        new_state = self.check_state()
        
        if new_state != self.state:
            self.update_state(new_state)
        
        # Schedule next check
        self.root.after(2000, self.update_check)

if __name__ == '__main__':
    RoboboogieAvatar()