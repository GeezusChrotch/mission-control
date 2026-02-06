#!/usr/bin/env python3
"""
Roboboogie Floating Avatar - Minimal PyObjC
Simple always-on-top floating window
"""
import sys
import time
import os
from threading import Thread

from Foundation import NSObject, NSMakeRect, NSMakeSize
from AppKit import (NSApplication, NSWindow, NSView, NSTextField, 
                     NSColor, NSFont, NSBezelBorder, NSTitledWindowMask,
                     NSClosableWindowMask, NSMiniaturizableWindowMask,
                     NSBackingStoreBuffered, NSStatusWindowLevel)

class AvatarView(NSView):
    """Simple avatar view with drawn face"""
    
    def initWithFrame_(self, frame):
        self = super(AvatarView, self).initWithFrame_(frame)
        self.state = "idle"
        return self
    
    def setState_(self, state):
        self.state = state
        self.setNeedsDisplay_(True)
    
    def drawRect_(self, rect):
        # Colors
        colors = {
            "idle": (0.56, 0.93, 0.56, 1.0),      # Green
            "thinking": (0.53, 0.81, 0.92, 1.0),  # Blue
            "working": (1.0, 0.78, 0.39, 1.0),    # Orange
            "excited": (1.0, 0.59, 0.59, 1.0),    # Pink
            "subagent": (0.78, 0.59, 1.0, 1.0)    # Purple
        }
        
        c = colors.get(self.state, colors["idle"])
        NSColor.colorWithCalibratedRed_green_blue_alpha_(c[0], c[1], c[2], c[3]).set()
        
        # Draw face circle
        bounds = self.bounds()
        w, h = bounds.size.width, bounds.size.height
        cx, cy = w/2, h/2
        r = min(w, h)/2 - 10
        
        # Simple circle
        from AppKit import NSBezierPath, NSRoundBezierStyle
        path = NSBezierPath.bezierPathWithOvalInRect_(
            NSMakeRect(cx - r, cy - r, r*2, r*2)
        )
        path.fill()
        
        # Draw eyes (two dots)
        NSColor.whiteColor().set()
        eye_r = 15
        eye_offset = r/2.5
        from AppKit import NSMakePoint
        for ox in [-eye_offset, eye_offset]:
            path = NSBezierPath.bezierPathWithOvalInRect_(
                NSMakeRect(cx + ox - eye_r, cy - 10 - eye_r, eye_r*2, eye_r*2)
            )
            path.fill()
        
        # Draw pupils
        NSColor.colorWithCalibratedRed_green_blue_alpha_(0.18, 0.35, 0.24, 1.0).set()
        pup_r = 8
        for ox in [-eye_offset, eye_offset]:
            path = NSBezierPath.bezierPathWithOvalInRect_(
                NSMakeRect(cx + ox + 2, cy - 10 + 2, pup_r, pup_r)
            )
            path.fill()
        
        # Draw mouth based on state
        NSColor.colorWithCalibratedRed_green_blue_alpha_(0.18, 0.35, 0.24, 1.0).set()
        NSBezierPath.setLineWidth_(4)
        NSBezierPath.setLineCapStyle_(1)  # NSRoundLineCapStyle
        
        if self.state == "idle":
            # Smile arc
            path = NSBezierPath.bezierPath()
            path.moveToPoint_(NSMakePoint(cx - 15, cy + 15))
            path.curveToPoint_controlPoint1_controlPoint2_(
                NSMakePoint(cx + 15, cy + 15),
                NSMakePoint(cx - 10, cy + 22),
                NSMakePoint(cx + 10, cy + 22)
            )
            path.stroke()
        elif self.state == "thinking":
            # Straight line
            NSBezierPath.bezierPathWithMoveToPoint_(
                NSMakePoint(cx - 15, cy + 20)
            ).lineToPoint_(
                NSMakePoint(cx + 15, cy + 20)
            ).stroke()
        elif self.state == "working":
            # Focused line
            NSBezierPath.bezierPathWithMoveToPoint_(
                NSMakePoint(cx - 20, cy + 25)
            ).lineToPoint_(
                NSMakePoint(cx + 20, cy + 25)
            ).stroke()
        elif self.state == "excited":
            # Open mouth
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.18, 0.35, 0.24, 1.0).set()
            path = NSBezierPath.bezierPathWithOvalInRect_(
                NSMakeRect(cx - 15, cy + 18, 30, 15)
            )
            path.fill()
        else:  # subagent
            # Wavy line
            NSBezierPath.setLineDash_count_([5, 5], 2, 0)
            NSBezierPath.bezierPathWithMoveToPoint_(
                NSMakePoint(cx - 20, cy + 20)
            ).lineToPoint_(
                NSMakePoint(cx + 20, cy + 20)
            ).stroke()
            NSBezierPath.setLineDash_count_(None, 0, 0)


class RoboboogieApp:
    def __init__(self):
        self.app = NSApplication.sharedApplication()
        self.window = None
        self.view = None
        self.current_state = "idle"
        self.running = True
        
        # Create window
        self.create_window()
        
        # Start monitoring thread
        Thread(target=self.monitor_loop, daemon=True).start()
    
    def create_window(self):
        # Window style: titled but minimal
        style = NSTitledWindowMask | NSClosableWindowMask | NSMiniaturizableWindowMask
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(200, 400, 250, 350),
            style,
            NSBackingStoreBuffered,
            False
        )
        self.window.setTitle_("🤖 Roboboogie")
        self.window.setLevel_(NSStatusWindowLevel + 1)  # Above menu bar
        self.window.setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(0.95, 0.95, 0.95, 1.0))
        
        # Create avatar view
        self.view = AvatarView.alloc().initWithFrame_(NSMakeRect(0, 60, 250, 230))
        self.window.contentView().addSubview_(self.view)
        
        # Status label
        label = NSTextField.alloc().initWithFrame_(NSMakeRect(10, 10, 230, 40))
        label.setStringValue_("IDLE 💤")
        label.setAlignment_(4)  # NSCenterTextAlignment
        label.setBezeled_(False)
        label.setDrawsBackground_(False)
        font = NSFont.fontWithName_size_("Helvetica-Bold", 18)
        if font:
            label.setFont_(font)
        self.window.contentView().addSubview_(label)
        self.status_label = label
        
        # Center on screen
        self.window.center()
        self.window.orderFrontRegardless()
    
    def set_state(self, state):
        if state == self.current_state:
            return
        self.current_state = state
        
        # Update UI
        self.view.setState_(state)
        
        icons = {"idle": "💤", "thinking": "💭", "working": "⚡", "excited": "🎉", "subagent": "🧠"}
        self.status_label.setStringValue_(f"{state.upper()} {icons.get(state, '')}")
    
    def monitor_loop(self):
        """Monitor Clawdbot activity"""
        while self.running:
            try:
                home = os.path.expanduser("~")
                sessions_path = os.path.join(home, ".clawdbot", "sessions")
                
                if os.path.exists(sessions_path):
                    sessions = [f for f in os.listdir(sessions_path) if f.endswith('.jsonl')]
                    if sessions:
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
            except:
                pass
            
            time.sleep(2)
    
    def run(self):
        self.app.run()


if __name__ == "__main__":
    app = RoboboogieApp()
    print("🤖 Roboboogie Avatar started!")
    print("   - Floating window (always on top)")
    print("   - Click X or Cmd-Q to close")
    print("   - States: IDLE 💤, THINKING 💭, WORKING ⚡, EXCITED 🎉, SUBAGENT 🧠")
    app.run()
