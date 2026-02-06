#!/usr/bin/env python3
"""
Roboboogie Floating Avatar - Qt-based floating window
Shows different states based on Clawdbot activity
"""
import sys
import time
import json
import os
import urllib.request
import urllib.error
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QColor, QPainter, QBrush, QPen, QFont, QLinearGradient

class AvatarFace(QWidget):
    """Custom painted avatar face widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = "idle"
        self.animation_angle = 0
        self.setMinimumSize(150, 150)
        
    def setState(self, state):
        self.state = state
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        radius = min(w, h) // 2 - 10
        
        # Get colors based on state
        face_color = self.get_face_color()
        eye_color = QColor(255, 255, 255)
        pupil_color = self.get_pupil_color()
        mouth_color = QColor(45, 90, 61)
        antenna_color = QColor(45, 90, 61)
        antenna_ball_color = self.get_antenna_ball_color()
        
        # Draw antenna
        painter.setPen(QPen(antenna_color, 8))
        painter.drawLine(cx, cy - radius + 20, cx, cy - radius - 10)
        
        # Antenna ball with glow effect
        ball_radius = 12
        if self.state == "working":
            glow_color = QColor(243, 156, 18)
            glow_color.setAlpha(100)
            painter.setBrush(QBrush(glow_color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(cx, cy - radius - 15, ball_radius + 10, ball_radius + 10)
            ball_radius = 15
            
        painter.setBrush(QBrush(antenna_ball_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx, cy - radius - 15, ball_radius, ball_radius)
        
        # Draw face circle with gradient
        gradient = QLinearGradient(cx, cy - radius, cx, cy + radius)
        gradient.setColorAt(0, face_color.lighter(120))
        gradient.setColorAt(1, face_color)
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(30, 30, 30), 3))
        painter.drawEllipse(cx, cy, radius, radius)
        
        # Draw eyes
        eye_offset = radius // 3
        eye_radius = 20
        
        # Eye animation for thinking state
        if self.state == "thinking":
            offset_x = int(time.time() * 50) % 10 - 5
            offset_y = int(time.time() * 30) % 10 - 5
        else:
            offset_x, offset_y = 0, 0
        
        # Left eye
        painter.setBrush(QBrush(eye_color))
        painter.setPen(QPen(QColor(30, 30, 30), 2))
        painter.drawEllipse(cx - eye_offset + offset_x, cy - 10 + offset_y, eye_radius, eye_radius)
        
        # Left pupil
        painter.setBrush(QBrush(pupil_color))
        painter.setPen(Qt.NoPen)
        pupil_radius = 10
        if self.state == "thinking":
            # Spinning pupil
            angle = time.time() * 180 % 360
            px = cx - eye_offset + offset_x + pupil_radius * 0.3
            py = cy - 10 + offset_y
            painter.save()
            painter.translate(px, py)
            painter.rotate(angle)
            painter.drawEllipse(-pupil_radius//2, -pupil_radius//2, pupil_radius, pupil_radius)
            painter.restore()
        else:
            painter.drawEllipse(cx - eye_offset + offset_x + 5, cy - 10 + offset_y + 3, pupil_radius, pupil_radius)
        
        # Right eye
        painter.setBrush(QBrush(eye_color))
        painter.setPen(QPen(QColor(30, 30, 30), 2))
        painter.drawEllipse(cx + eye_offset + offset_x, cy - 10 + offset_y, eye_radius, eye_radius)
        
        # Right pupil
        painter.setBrush(QBrush(pupil_color))
        painter.setPen(Qt.NoPen)
        if self.state == "thinking":
            px = cx + eye_offset + offset_x + pupil_radius * 0.3
            py = cy - 10 + offset_y
            painter.save()
            painter.translate(px, py)
            painter.rotate(-angle)
            painter.drawEllipse(-pupil_radius//2, -pupil_radius//2, pupil_radius, pupil_radius)
            painter.restore()
        else:
            painter.drawEllipse(cx + eye_offset + offset_x + 5, cy - 10 + offset_y + 3, pupil_radius, pupil_radius)
        
        # Draw mouth based on state
        self.draw_mouth(painter, cx, cy, radius, mouth_color)
        
    def draw_mouth(self, painter, cx, cy, radius, color):
        painter.setPen(QPen(color, 4, Qt.SolidLine, Qt.RoundCap))
        
        if self.state == "idle":
            # Small smile
            painter.drawArc(cx - 20, cy + 15, 40, 20, 180 * 16, 180 * 16)
            
        elif self.state == "thinking":
            # Neutral straight line
            painter.drawLine(cx - 15, cy + 25, cx + 15, cy + 25)
            
        elif self.state == "working":
            # Focused line
            painter.drawLine(cx - 25, cy + 30, cx + 25, cy + 30)
            
        elif self.state == "excited":
            # Big open smile
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(cx, cy + 25, 35, 25)
            
        elif self.state == "subagent":
            # Wavy line
            painter.setPen(QPen(color, 3, Qt.DashLine, Qt.RoundCap))
            painter.drawLine(cx - 25, cy + 25, cx + 25, cy + 25)
            
    def get_face_color(self):
        colors = {
            "idle": QColor(144, 238, 144),      # Light green
            "thinking": QColor(135, 206, 250),  # Light blue
            "working": QColor(255, 200, 100),   # Orange-ish
            "excited": QColor(255, 150, 150),   # Pink
            "subagent": QColor(200, 150, 255),  # Purple
        }
        return colors.get(self.state, QColor(144, 238, 144))
    
    def get_pupil_color(self):
        colors = {
            "idle": QColor(45, 90, 61),
            "thinking": QColor(70, 130, 180),
            "working": QColor(200, 120, 0),
            "excited": QColor(200, 50, 50),
            "subagent": QColor(120, 50, 150),
        }
        return colors.get(self.state, QColor(45, 90, 61))
    
    def get_antenna_ball_color(self):
        colors = {
            "idle": QColor(231, 76, 60),        # Red
            "thinking": QColor(52, 152, 219),   # Blue
            "working": QColor(243, 156, 18),    # Orange
            "excited": QColor(46, 204, 113),    # Green
            "subagent": QColor(155, 89, 182),   # Purple
        }
        return colors.get(self.state, QColor(231, 76, 60))


class RoboboogieAvatar(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("🤖 Roboboogie")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(200, 260)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(0)
        
        # Avatar face
        self.avatar = AvatarFace()
        self.avatar.setFixedSize(150, 150)
        
        # Add shadow to avatar
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 5)
        self.avatar.setGraphicsEffect(shadow)
        
        # State label
        self.state_label = QLabel("IDLE")
        self.state_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        self.state_label.setFont(font)
        self.state_label.setStyleSheet("""
            QLabel {
                color: #666;
                background: transparent;
                padding: 8px;
                border-radius: 5px;
            }
        """)
        
        # Add to layout
        self.layout.addWidget(self.avatar, 0, Qt.AlignCenter)
        self.layout.addWidget(self.state_label, 0, Qt.AlignCenter)
        
        # Allow dragging the window
        self.dragging = False
        self.offset = None
        
        # State tracking
        self.current_state = "idle"
        self.previous_state = None
        self.last_activity_time = time.time()
        self.activity_timeout = 60  # 60 seconds before idle
        
        # Timer to check Clawdbot state
        self.state_timer = QTimer(self)
        self.state_timer.timeout.connect(self.check_clawdbot_state)
        self.state_timer.start(2000)  # Check every 2 seconds
        
        # Animation timer for dynamic effects
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_avatar)
        self.anim_timer.start(100)  # Update every 100ms
        
        # Status indicator
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-size: 10px;
                background: transparent;
            }
        """)
        
        print("🤖 Roboboogie Avatar started!")
        print("   - Drag window to move")
        print("   - Double-click to close")
        print("   - Shows your current state based on Clawdbot activity")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()
        
        # Double-click to close
        elif event.button() == Qt.LeftButton and event.type() == event.DoubleClick:
            self.close()

    def mouseMoveEvent(self, event):
        if self.dragging and self.offset:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def mouseDoubleClickEvent(self, event):
        # Close on double click
        self.close()

    def update_avatar(self):
        """Update avatar animation"""
        self.avatar.update()
        
        # Check for state timeout
        if time.time() - self.last_activity_time > self.activity_timeout:
            if self.current_state != "idle":
                self.set_state("idle")

    def check_clawdbot_state(self):
        """Check Clawdbot's state by checking for recent activity"""
        try:
            # Check for recent activity in OpenClaw sessions
            home = os.path.expanduser("~")
            sessions_path = os.path.join(home, ".openclaw", "agents", "main", "sessions")
            
            if not os.path.exists(sessions_path):
                return
            
            sessions = [f for f in os.listdir(sessions_path) if f.endswith('.jsonl')]
            if not sessions:
                return
            
            current_time = time.time()
            active = False
            state = "idle"
            
            # Check session modification times
            for session_file in sessions:
                session_path = os.path.join(sessions_path, session_file)
                try:
                    mod_time = os.path.getmtime(session_path)
                    age = current_time - mod_time
                    
                    # Very recent (< 10 seconds) = working
                    if age < 10:
                        state = "working"
                        active = True
                        break
                    
                    # Recent (< 30 seconds) = thinking
                    elif age < 30 and state != "working":
                        state = "thinking"
                        active = True
                    
                    # Somewhat recent (< 60 seconds) = excited
                    elif age < 60 and state not in ["working", "thinking"]:
                        state = "excited"
                        active = True
                except:
                    continue
            
            # Also check if clawdbot process is running
            try:
                result = os.popen("pgrep -f 'clawdbot' 2>/dev/null").read()
                if result.strip() and not active:
                    state = "thinking"
                    active = True
            except:
                pass
            
            # Update state
            if active:
                self.set_state(state)
                self.last_activity_time = current_time
            elif current_time - self.last_activity_time > self.activity_timeout:
                self.set_state("idle")
                
        except Exception as e:
            pass  # Silently ignore errors

    def set_state(self, state):
        """Set avatar state"""
        if state == self.current_state:
            return
        
        self.previous_state = self.current_state
        self.current_state = state
        
        # Update avatar
        self.avatar.setState(state)
        
        # Update label
        state_text = state.upper()
        self.state_label.setText(state_text)
        
        # Update label color based on state
        colors = {
            "idle": "#666666",
            "thinking": "#3498db",
            "working": "#f39c12",
            "excited": "#e74c3c",
            "subagent": "#9b59b6",
        }
        color = colors.get(state, "#666666")
        self.state_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                background: transparent;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }}
        """)
        
        print(f"State changed: {self.previous_state} -> {state}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for better appearance
    
    window = RoboboogieAvatar()
    window.show()
    
    sys.exit(app.exec_())