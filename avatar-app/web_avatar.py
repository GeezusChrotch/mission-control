#!/usr/bin/env python3
"""
Roboboogie Web Avatar Server
Simple HTTP server for the avatar without GUI dependencies
"""

import http.server
import socketserver
import json
import time
import threading
import webbrowser
from datetime import datetime

PORT = 8080
STATE = "idle"
LAST_ACTIVITY = time.time()
ACTIVITY_TIMEOUT = 60  # seconds before going idle

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Roboboogie Avatar</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            background: #222;
            color: #fff;
            font-family: system-ui, -apple-system, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }
        
        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 30px;
        }
        
        .avatar {
            width: 200px;
            height: 200px;
            position: relative;
            margin: 10px;
        }
        
        .face {
            width: 100%;
            height: 100%;
            background-color: #90EE90;
            border-radius: 50%;
            position: relative;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            overflow: hidden;
            transition: background-color 0.5s;
        }
        
        .eyes {
            position: absolute;
            top: 30%;
            width: 100%;
            display: flex;
            justify-content: space-evenly;
        }
        
        .eye {
            width: 30px;
            height: 30px;
            background-color: white;
            border-radius: 50%;
            position: relative;
            border: 2px solid #2d5a3d;
            transition: height 0.3s;
        }
        
        .pupil {
            width: 15px;
            height: 15px;
            background-color: #2d5a3d;
            border-radius: 50%;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
        
        .mouth {
            position: absolute;
            bottom: 30%;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 40px;
            border-radius: 50%;
            border-bottom: 5px solid #2d5a3d;
            transition: height 0.3s, width 0.3s;
        }
        
        .antenna {
            position: absolute;
            top: -20px;
            left: 50%;
            transform: translateX(-50%);
            width: 10px;
            height: 30px;
            background-color: #2d5a3d;
            border-radius: 5px;
        }
        
        .antenna-ball {
            position: absolute;
            top: -30px;
            left: 50%;
            transform: translateX(-50%);
            width: 15px;
            height: 15px;
            background-color: #e74c3c;
            border-radius: 50%;
            animation: glow 2s infinite alternate;
        }
        
        @keyframes glow {
            0% { box-shadow: 0 0 5px 1px rgba(231, 76, 60, 0.5); }
            100% { box-shadow: 0 0 20px 4px rgba(231, 76, 60, 0.8); }
        }
        
        /* States */
        
        .thinking .pupil {
            animation: thinking 1.5s infinite;
        }
        
        @keyframes thinking {
            0% { transform: translate(-50%, -50%) rotate(0deg) translateX(0); }
            25% { transform: translate(-50%, -50%) rotate(90deg) translateX(2px); }
            50% { transform: translate(-50%, -50%) rotate(180deg) translateX(0); }
            75% { transform: translate(-50%, -50%) rotate(270deg) translateX(2px); }
            100% { transform: translate(-50%, -50%) rotate(360deg) translateX(0); }
        }
        
        .working .antenna-ball {
            animation: working 0.7s infinite alternate;
            background-color: #f39c12;
        }
        
        @keyframes working {
            0% { transform: translateX(-50%) scale(1); box-shadow: 0 0 5px 1px rgba(243, 156, 18, 0.5); }
            100% { transform: translateX(-50%) scale(1.3); box-shadow: 0 0 20px 4px rgba(243, 156, 18, 0.8); }
        }
        
        .excited .mouth {
            height: 50px;
            width: 90px;
            border-radius: 50%;
        }
        
        .excited .eye {
            height: 35px;
        }
        
        .excited .antenna-ball {
            background-color: #3498db;
            animation: excited 0.5s infinite alternate;
        }
        
        @keyframes excited {
            0% { transform: translateX(-50%) scale(1); box-shadow: 0 0 5px 1px rgba(52, 152, 219, 0.5); }
            100% { transform: translateX(-50%) scale(1.5); box-shadow: 0 0 20px 4px rgba(52, 152, 219, 0.8); }
        }
        
        .subagent .face {
            background-color: #9b59b6;
        }
        
        .subagent .antenna-ball {
            background-color: #8e44ad;
            animation: subagent 1s infinite alternate;
        }
        
        @keyframes subagent {
            0% { transform: translateX(-50%) scale(1) rotate(0deg); box-shadow: 0 0 5px 1px rgba(142, 68, 173, 0.5); }
            100% { transform: translateX(-50%) scale(1.2) rotate(180deg); box-shadow: 0 0 20px 4px rgba(142, 68, 173, 0.8); }
        }
        
        .status-box {
            background: #333;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            min-width: 200px;
        }
        
        .status-title {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #90EE90;
        }
        
        .status-text {
            font-size: 1.5em;
            font-weight: bold;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .control-btn {
            background: #444;
            border: none;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .control-btn:hover {
            background: #555;
        }
        
        .info {
            font-size: 0.9em;
            color: #888;
            text-align: center;
            max-width: 500px;
            line-height: 1.4;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="avatar">
            <div class="face" id="robo-face">
                <div class="antenna"></div>
                <div class="antenna-ball"></div>
                <div class="eyes">
                    <div class="eye">
                        <div class="pupil"></div>
                    </div>
                    <div class="eye">
                        <div class="pupil"></div>
                    </div>
                </div>
                <div class="mouth"></div>
            </div>
        </div>
        
        <div class="status-box">
            <div class="status-title">CURRENT STATE</div>
            <div class="status-text" id="status-text">idle</div>
        </div>
        
        <div class="controls">
            <button class="control-btn" onclick="setState('idle')">Idle</button>
            <button class="control-btn" onclick="setState('thinking')">Thinking</button>
            <button class="control-btn" onclick="setState('working')">Working</button>
            <button class="control-btn" onclick="setState('excited')">Excited</button>
            <button class="control-btn" onclick="setState('subagent')">Subagent</button>
        </div>
        
        <div class="info">
            <p>Roboboogie Avatar Server • <span id="last-updated">Just started</span></p>
            <p>This avatar shows different states based on my activity:</p>
            <ul>
                <li><strong>Idle</strong>: No recent activity</li>
                <li><strong>Thinking</strong>: Processing, analyzing</li>
                <li><strong>Working</strong>: Actively executing tasks</li>
                <li><strong>Excited</strong>: Something interesting happening!</li>
                <li><strong>Subagent</strong>: Running a sub-agent</li>
            </ul>
        </div>
    </div>
    
    <script>
        const face = document.getElementById('robo-face');
        const statusText = document.getElementById('status-text');
        const lastUpdated = document.getElementById('last-updated');
        
        // Function to set the state
        function setState(state) {
            resetState();
            
            switch(state) {
                case 'idle':
                    // Default state
                    break;
                case 'thinking':
                    face.classList.add('thinking');
                    break;
                case 'working':
                    face.classList.add('working');
                    break;
                case 'excited':
                    face.classList.add('excited');
                    break;
                case 'subagent':
                    face.classList.add('subagent');
                    break;
                default:
                    // Default to idle
                    break;
            }
            
            statusText.textContent = state;
            lastUpdated.textContent = new Date().toLocaleTimeString();
            
            // Send state to server
            fetch('/state', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ state: state })
            });
        }
        
        function resetState() {
            face.className = 'face';
        }
        
        // Initialize to idle state
        setState('idle');
        
        // Auto-update every 5 seconds
        async function updateState() {
            try {
                const response = await fetch('/state');
                if (response.ok) {
                    const data = await response.json();
                    if (data.state !== statusText.textContent) {
                        setState(data.state);
                    }
                }
            } catch (error) {
                console.error('Failed to update state:', error);
            }
        }
        
        // Check for updates every 5 seconds
        setInterval(updateState, 5000);
    </script>
</body>
</html>
"""

class AvatarHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global STATE, LAST_ACTIVITY
        
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode())
        
        elif self.path == '/state':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Check if we should auto-update to idle due to timeout
            current_time = time.time()
            if current_time - LAST_ACTIVITY > ACTIVITY_TIMEOUT and STATE != "idle":
                STATE = "idle"
            
            response = {
                'state': STATE,
                'last_activity': LAST_ACTIVITY,
                'timestamp': datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        global STATE, LAST_ACTIVITY
        
        if self.path == '/state':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode())
                if 'state' in data:
                    STATE = data['state']
                    LAST_ACTIVITY = time.time()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'success': True, 'state': STATE}
                self.wfile.write(json.dumps(response).encode())
            except:
                self.send_response(400)
                self.end_headers()
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress log messages
        pass

def start_server():
    """Start the avatar web server"""
    with socketserver.TCPServer(("", PORT), AvatarHandler) as httpd:
        print(f"Roboboogie Avatar Server running on http://localhost:{PORT}")
        print("Press Ctrl+C to stop")
        print("\nThe avatar will automatically show different states:")
        print("- Idle: No recent activity")
        print("- Thinking: Processing, analyzing")
        print("- Working: Actively executing tasks")
        print("- Excited: Something interesting!")
        print("- Subagent: Running a sub-agent")
        
        # Try to open browser automatically
        try:
            webbrowser.open(f"http://localhost:{PORT}")
        except:
            print(f"\nOpen your browser to: http://localhost:{PORT}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.server_close()

def set_avatar_state(state):
    """Update the avatar state from external scripts"""
    global STATE, LAST_ACTIVITY
    STATE = state
    LAST_ACTIVITY = time.time()
    
    # Try to send update via HTTP
    try:
        import urllib.request
        import json
        
        data = json.dumps({'state': state}).encode()
        req = urllib.request.Request(
            f"http://localhost:{PORT}/state",
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req)
        return True
    except:
        return False

if __name__ == "__main__":
    start_server()