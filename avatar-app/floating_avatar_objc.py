#!/usr/bin/env python3
"""
Roboboogie Floating Avatar - PyObjC Native
A simple always-on-top floating window showing different states
"""
import objc
from Foundation import NSObject, NSThread
from AppKit import (NSApplication, NSWindow, NSView, NSButton, NSImage, 
                     NSColor, NSFont, NSRoundedBezelStyle, NSMomentaryLightButton)
from PyObjCTools import AppHelper
import threading
import time
import os
import sys

# States with visual properties
STATES = {
    "idle": {
        "color": NSColor.colorWithCalibratedRed_green_blue_alpha_(0.56, 0.93, 0.56, 1.0),  # Light green
        "icon": "💤",
        "status": "IDLE"
    },
    "thinking": {
        "color": NSColor.colorWithCalibratedRed_green_blue_alpha_(0.53, 0.81, 0.92, 1.0),  # Light blue
        "icon": "💭",
        "status": "THINKING"
    },
    "working": {
        "color": NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 0.78, 0.39, 1.0),  # Orange
        "icon": "⚡",
        "status": "WORKING"
    },
    "excited": {
        "color": NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 0.59, 0.59, 1.0),  # Pink
        "icon": "🎉",
        "status": "EXCITED"
    },
    "subagent": {
        "color": NSColor.colorWithCalibratedRed_green_blue_alpha_(0.78, 0.59, 1.0, 1.0),  # Purple
        "icon": "🧠",
        "status": "SUBAGENT"
    }
}

class AvatarView(NSView):
    """Custom view for the avatar face"""
    
    def initWithFrame_(self, frame):
        self = super(AvatarView, self).initWithFrame_(frame)
        self.current_state = "idle"
        return self
    
    def setState_(self, state):
        self.current_state = state
        self.setNeedsDisplay_(True)
    
    def drawRect_(self, rect):
        # Get current state properties
        state = STATES.get(self.current_state, STATES["idle"])
        face_color = state["color"]
        
        # Draw face circle
        bounds = self.bounds()
        center_x = bounds.size.width / 2
        center_y = bounds.size.height / 2
        radius = min(bounds.size.width, bounds.size.height) / 2 - 20
        
        # Face background
        NSColor.colorWithCalibratedRed_green_blue_alpha_(0.9, 0.9, 0.9, 1.0).set()
        NSBezierPath.bezierPathWithOvalInRect_(
            NSMakeRect(center_x - radius - 3, center_y - radius - 3, (radius + 3) * 2, (radius + 3) * 2)
        ).fill()
        
        face_color.set()
        NSBezierPath.bezelPath_(
            NSBezierPath.bezierPathWithOvalInRect_(
                NSMakeRect(center_x - radius, center_y - radius, radius * 2, radius * 2)
            )
        )
        NSBezierPath.fill()
        
        # Draw eyes
        eye_offset = radius / 3
        eye_radius = 20
        
        NSColor.whiteColor().set()
        NSBezierPath.bezelPath_(
            NSBezierPath.bezierPathWithOvalInRect_(
                NSMakeRect(center_x - eye_offset - eye_radius, center_y - 10 - eye_radius, eye_radius * 2, eye_radius * 2)
            )
        ).fill()
        NSBezierPath.bezelPath_(
            NSBezierPath.bezierPathWithOvalInRect_(
                NSMakeRect(center_x + eye_offset - eye_radius, center_y - 10 - eye_radius, eye_radius * 2, eye_radius * 2)
            )
        ).fill()
        
        # Draw pupils
        NSColor.colorWithCalibratedRed_green_blue_alpha_(0.18, 0.35, 0.24, 1.0).set()
        NSBezierPath.bezelPath_(
            NSBezierPath.bezierPathWithOvalInRect_(
                NSMakeRect(center_x - eye_offset - 5, center_y - 10 + 3, 10, 10)
            )
        ).fill()
        NSBezierPath.bezelPath_(
            NSBezierPath.bezierPathWithOvalInRect_(
                NSMakeRect(center_x + eye_offset - 5, center_y - 10 + 3, 10, 10)
            )
        ).fill()
        
        # Draw mouth based on state
        self.drawMouthForState_(state["status"], center_x, center_y, radius)
        
        # Draw antenna
        NSColor.colorWithCalibratedRed_green_blue_alpha_(0.18, 0.35, 0.24, 1.0).set()
        NSBezierPath.setLineWidth_(8)
        NSBezierPath.bezierPath_(
            NSBezierPath.bezierPathWithMoveToPoint_(
                NSMakePoint(center_x, center_y - radius + 20)
            ).lineToPoint_(
                NSMakePoint(center_x, center_y - radius - 10)
            )
        ).stroke()
        
        # Antenna ball
        antenna_colors = {
            "IDLE": NSColor.colorWithCalibratedRed_green_blue_alpha_(0.91, 0.3, 0.24, 1.0),
            "THINKING": NSColor.colorWithCalibratedRed_green_blue_alpha_(0.2, 0.6, 0.86, 1.0),
            "WORKING": NSColor.colorWithCalibratedRed_green_blue_alpha_(0.95, 0.61, 0.07, 1.0),
            "EXCITED": NSColor.colorWithCalibratedRed_green_blue_alpha_(0.18, 0.8, 0.44, 1.0),
            "SUBAGENT": NSColor.colorWithCalibratedRed_green_blue_alpha_(0.61, 0.35, 0.71, 1.0),
        }
        ball_color = antenna_colors.get(state["status"], antenna_colors["IDLE"])
        ball_color.set()
        NSBezierPath.bezelPath_(
            NSBezierPath.bezierPathWithOvalInRect_(
                NSMakeRect(center_x - 8, center_y - radius - 20, 16, 16)
            )
        ).fill()
    
    def drawMouthForState_(self, state, center_x, center_y, radius):
        """Draw mouth based on state"""
        NSColor.colorWithCalibratedRed_green_blue_alpha_(0.18, 0.35, 0.24, 1.0).set()
        NSBezierPath.setLineWidth_(4)
        NSBezierPath.setLineCapStyle_(NSRoundLineCapStyle)
        
        if state == "IDLE":
            # Small smile arc
            path = NSBezierPath.bezierPath()
            path.moveToPoint_(NSMakePoint(center_x - 15, center_y + 15))
            path.curveToPoint_controlPoint1_controlPoint2_(
                NSMakePoint(center_x + 15, center_y + 15),
                NSMakePoint(center_x - 10, center_y + 25),
                NSMakePoint(center_x + 10, center_y + 25)
            )
            path.stroke()
            
        elif state == "THINKING":
            # Neutral line
            NSBezierPath.bezelPath_(
                NSBezierPath.bezierPathWithMoveToPoint_(
                    NSMakePoint(center_x - 15, center_y + 25)
                ).lineToPoint_(
                    NSMakePoint(center_x + 15, center_y + 25)
                )
            ).stroke()
            
        elif state == "WORKING":
            # Focused line
            NSBezierPath.bezelPath_(
                NSBezierPath.bezierPathWithMoveToPoint_(
                    NSMakePoint(center_x - 25, center_y + 30)
                ).lineToPoint_(
                    NSMakePoint(center_x + 25, center_y + 30)
                )
            ).stroke()
            
        elif state == "EXCITED":
            # Open smile
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.18, 0.35, 0.24, 1.0).set()
            NSBezierPath.bezelPath_(
                NSBezierPath.bezierPathWithOvalInRect_(
                    NSMakeRect(center_x - 20, center_y + 20, 40, 20)
                )
            ).fill()
            
        elif state == "SUBAGENT":
            # Wavy line
            NSBezierPath.setLineWidth_(3)
            NSBezierPath.setLineDash_phase_count_([5, 5], 2, 0)
            NSBezierPath.bezelPath_(
                NSBezierPath.bezierPathWithMoveToPoint_(
                    NSMakePoint(center_x - 25, center_y + 25)
                ).lineToPoint_(
                    NSMakePoint(center_x + 25, center_y + 25)
                )
            ).stroke()
            NSBezierPath.setLineDash_count_(None, 0, 0)


class RoboboogieWindow(NSObject):
    """Main window controller"""
    
    window = objc.ivar('window', objc._C_ID)
    avatar_view = objc.ivar('avatar_view', objc._C_ID)
    status_label = objc.ivar('status_label', objc._C_ID)
    current_state = objc.ivar('current_state', objc._C_ID)
    
    def init(self):
        self = super(RoboboogieWindow, self).init()
        self.current_state = "idle"
        return self
    
    def awakeFromNib(self):
        pass  # We'll create window programmatically
    
    def createWindow(self):
        # Create window
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(100, 100, 220, 280),
            NSWindowStyleMask | NSWindowStyleMask | NSWindowStyleMask,
            NSBackingStoreBuffered,
            False
        )
        self.window.setTitle_("🤖 Roboboogie")
        self.window.setLevel_(NSFloatingWindowLevel)  # Always on top
        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(NSColor.clearColor())
        self.window.setHasShadow_(False)
        
        # Create content view
        content_view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 220, 280))
        self.window.setContentView_(content_view)
        
        # Create avatar view
        self.avatar_view = AvatarView.alloc().initWithFrame_(NSMakeRect(10, 100, 200, 200))
        content_view.addSubview_(self.avatar_view)
        
        # Create close button
        close_btn = NSButton.alloc().initWithFrame_(NSMakeRect(180, 250, 30, 30))
        close_btn.setTitle_("✕")
        close_btn.setBezelStyle_(NSRoundedBezelStyle)
        close_btn.setTarget_(self)
        close_btn.setAction_("closeWindow:")
        content_view.addSubview_(close_btn)
        
        # Create status label
        self.status_label = NSTextField.alloc().initWithFrame_(NSMakeRect(10, 60, 200, 30))
        self.status_label.setStringValue_("IDLE 💤")
        self.status_label.setAlignment_(NSCenterTextAlignment)
        self.status_label.setBezeled_(False)
        self.status_label.setDrawsBackground_(False)
        font = NSFont.fontWithName_size_("Helvetica-Bold", 16)
        if font:
            self.status_label.setFont_(font)
        content_view.addSubview_(self.status_label)
        
        # Center window on screen
        self.window.center()
        
        self.window.orderFrontRegardless()
    
    def closeWindow_(self, sender):
        NSApp().terminate_(None)
    
    def setState_(self, state):
        if state == self.current_state:
            return
        self.current_state = state
        
        # Update UI
        self.avatar_view.setState_(state)
        state_info = STATES.get(state, STATES["idle"])
        self.status_label.setStringValue_(f"{state_info['status']} {state_info['icon']}")
    
    def checkClawdbotState(self):
        """Check Clawdbot activity"""
        try:
            home = os.path.expanduser("~")
            sessions_path = os.path.join(home, ".clawdbot", "sessions")
            
            if not os.path.exists(sessions_path):
                self.setState_("idle")
                return
            
            sessions = [f for f in os.listdir(sessions_path) if f.endswith('.jsonl')]
            if not sessions:
                self.setState_("idle")
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
            
            self.setState_(state)
            
        except Exception as e:
            self.setState_("idle")


class RoboboogieAppDelegate(NSObject):
    """App delegate"""
    
    def applicationDidFinishLaunching_(self, notification):
        self.window_controller = RoboboogieWindow.alloc().init()
        self.window_controller.createWindow()
        
        # Start state checking thread
        self.check_timer = threading.Timer(2.0, self.check_loop)
        self.check_timer.daemon = True
        self.check_timer.start()
        
        print("🤖 Roboboogie Avatar started!")
        print("   - Floating window (always on top)")
        print("   - Click X to close")
        print("   - States: Idle 💤, Thinking 💭, Working ⚡, Excited 🎉, Subagent 🧠")
    
    def check_loop(self):
        """Background loop to check state"""
        while True:
            try:
                self.window_controller.checkClawdbotState()
            except:
                pass
            time.sleep(2)


def main():
    app = NSApplication.sharedApplication()
    
    delegate = RoboboogieAppDelegate.alloc().init()
    app.setDelegate_(delegate)
    
    NSApp().activateIgnoringOtherApps_(True)
    app.run()


if __name__ == "__main__":
    main()