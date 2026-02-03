#!/usr/bin/env python3
"""Simpler avatar using Tkinter that works on macOS without PyQt5 installation."""

import tkinter as tk
import json
import time
import os
from tkinter import font
from PIL import Image, ImageDraw, ImageTk
import math

class SimpleRoboboogieAvatar:
    def __init__(self):
        self.root = tk.Tk()
        
        # Set window properties
        self.root.title("Roboboogie Avatar")
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.attributes('-topmost', True)  # Always on top
        self.root.attributes('-transparentcolor', '#FFFFFF')  # White is transparent
        
        # Set size
        self.root.geometry('200x200')
        
        # Create canvas for drawing
        self.canvas = tk.Canvas(self.root, width=200, height=200, bg='white', highlightthickness=0)
        self.canvas.pack()
        
        # Colors for different states
        self.state_colors = {
            'idle': '#90EE90',      # Light green
            'thinking': '#FFD700',  # Gold
            'working': '#FF8C00',   # Dark orange
            'excited': '#3498db',   # Blue
            'subagent': '#9b59b6'   # Purple
        }
        
        # State properties
        self.current_state = 'idle'
        self.face_center = (100, 100)
        self.face_radius = 80
        
        # Animation variables
        self.antenna_ball_size = 15
        self.antenna_ball_color = '#e74c3c'
        self.pupil_offset = 0
        self.mouth_width = 60
        self.mouth_height = 30
        
        # Antenna animation
        self.antenna_animation = 0
        self.antenna_ball_y_offset = 0
        
        # Dragging
        self.dragging = False
        self.start_x = 0
        self.start_y = 0
        
        # Bind mouse events for dragging
        self.canvas.bind('<Button-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.drag)
        self.canvas.bind('<ButtonRelease-1>', self.stop_drag)
        
        # Draw initial state
        self.draw_face()
        
        # State timer
        self.root.after(1000, self.animate)
        
        # Quit on escape key
        self.root.bind('<Escape>', lambda e: self.root.destroy())
    
    def start_drag(self, event):
        self.dragging = True
        self.start_x = event.x
        self.start_y = event.y
    
    def drag(self, event):
        if self.dragging:
            x = self.root.winfo_x() + (event.x - self.start_x)
            y = self.root.winfo_y() + (event.y - self.start_y)
            self.root.geometry(f'+{x}+{y}')
    
    def stop_drag(self, event):
        self.dragging = False
    
    def draw_face(self):
        # Clear canvas
        self.canvas.delete('all')
        
        # Get face color for current state
        face_color = self.state_colors.get(self.current_state, '#90EE90')
        
        # Draw face (circle)
        self.canvas.create_oval(
            20, 20, 180, 180,
            fill=face_color,
            outline='#2d5a3d',
            width=3
        )
        
        # Draw antenna
        self.canvas.create_line(
            100, 20, 100, 40,
            fill='#2d5a3d',
            width=3
        )
        
        # Draw antenna ball with animation
        antenna_y = 40 + self.antenna_ball_y_offset
        self.canvas.create_oval(
            100 - self.antenna_ball_size,
            antenna_y - self.antenna_ball_size,
            100 + self.antenna_ball_size,
            antenna_y + self.antenna_ball_size,
            fill=self.antenna_ball_color,
            outline='#c0392b',
            width=2
        )
        
        # Draw eyes
        eye_y = 70
        left_eye_x = 65
        right_eye_x = 135
        eye_size = 20
        
        # Left eye
        self.canvas.create_oval(
            left_eye_x - eye_size, eye_y - eye_size,
            left_eye_x + eye_size, eye_y + eye_size,
            fill='white',
            outline='#2d5a3d',
            width=2
        )
        
        # Left pupil with animation
        pupil_x = left_eye_x + self.pupil_offset
        self.canvas.create_oval(
            pupil_x - 8, eye_y - 8,
            pupil_x + 8, eye_y + 8,
            fill='#2d5a3d',
            outline='#1a472a'
        )
        
        # Right eye
        self.canvas.create_oval(
            right_eye_x - eye_size, eye_y - eye_size,
            right_eye_x + eye_size, eye_y + eye_size,
            fill='white',
            outline='#2d5a3d',
            width=2
        )
        
        # Right pupil with animation
        pupil_x = right_eye_x - self.pupil_offset
        self.canvas.create_oval(
            pupil_x - 8, eye_y - 8,
            pupil_x + 8, eye_y + 8,
            fill='#2d5a3d',
            outline='#1a472a'
        )
        
        # Draw mouth based on state
        mouth_y = 130
        
        if self.current_state == 'excited':
            # Happy/smiling mouth for excited
            self.canvas.create_arc(
                100 - self.mouth_width, mouth_y - self.mouth_height,
                100 + self.mouth_width, mouth_y + self.mouth_height,
                start=0, extent=-180,
                style='arc',
                width=3,
                outline='#2d5a3d'
            )
        else:
            # Normal mouth
            self.canvas.create_arc(
                100 - self.mouth_width, mouth_y - self.mouth_height,
                100 + self.mouth_width, mouth_y + self.mouth_height,
                start=0, extent=180,
                style='arc',
                width=3,
                outline='#2d5a3d'
            )
        
        # Draw state label (temporary for debugging)
        self.canvas.create_text(
            100, 10,
            text=self.current_state.upper(),
            fill='white',
            font=('Arial', 8, 'bold')
        )
    
    def set_state(self, state):
        if state != self.current_state:
            self.current_state = state
            
            # Update antenna ball color based on state
            if state == 'idle':
                self.antenna_ball_color = '#e74c3c'  # Red
            elif state == 'thinking':
                self.antenna_ball_color = '#FFD700'  # Gold
            elif state == 'working':
                self.antenna_ball_color = '#FF8C00'  # Orange
            elif state == 'excited':
                self.antenna_ball_color = '#3498db'  # Blue
            elif state == 'subagent':
                self.antenna_ball_color = '#9b59b6'  # Purple
    
    def animate(self):
        # Update animation based on state
        if self.current_state == 'thinking':
            # Pupils move side to side
            self.pupil_offset = math.sin(self.antenna_animation * 2) * 5
            self.antenna_animation += 0.2
        elif self.current_state == 'working':
            # Antenna ball bounces
            self.antenna_ball_y_offset = math.sin(self.antenna_animation * 3) * 5
            self.antenna_animation += 0.3
        elif self.current_state == 'excited':
            # Fast antenna bounce and mouth changes
            self.antenna_ball_y_offset = math.sin(self.antenna_animation * 5) * 3
            self.mouth_height = 40 + math.sin(self.antenna_animation * 4) * 10
            self.antenna_animation += 0.4
        elif self.current_state == 'subagent':
            # Antenna ball rotates (changing offset)
            self.antenna_ball_y_offset = math.sin(self.antenna_animation) * 5
            self.pupil_offset = math.cos(self.antenna_animation) * 3
            self.antenna_animation += 0.25
        else:
            # Idle: gentle breathing
            self.antenna_ball_y_offset = math.sin(self.antenna_animation * 0.5) * 2
            self.antenna_animation += 0.1
        
        # Redraw face
        self.draw_face()
        
        # Schedule next animation frame
        self.root.after(50, self.animate)
    
    def cycle_states(self):
        """Cycle through states for demo purposes"""
        states = ['idle', 'thinking', 'working', 'excited', 'subagent']
        current_index = states.index(self.current_state) if self.current_state in states else 0
        next_index = (current_index + 1) % len(states)
        self.set_state(states[next_index])
        
        # Schedule next state change
        self.root.after(3000, self.cycle_states)
    
    def run(self):
        # Start state cycling for demo
        self.root.after(3000, self.cycle_states)
        self.root.mainloop()

if __name__ == '__main__':
    avatar = SimpleRoboboogieAvatar()
    
    # Instructions
    print("=== Simple Roboboogie Avatar ===")
    print("Features:")
    print("• Floating window without borders")
    print("• Always on top")
    print("• Click and drag to move")
    print("• Cycles through states every 3 seconds")
    print("• Press ESC to quit")
    print("")
    print("Starting avatar...")
    
    avatar.run()