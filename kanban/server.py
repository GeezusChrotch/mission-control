#!/usr/bin/env python3
"""Simple Kanban server with auto-save to disk and webhook notifications."""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import urllib.request
import threading
import time
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), 'kanban.json')
WEBHOOK_URL = "http://127.0.0.1:18789/hooks/wake"
HOOK_TOKEN = "c42c95ffb81c515fd5ef4a4ff44ade352a654a674e1c9eca"

# Store previous state for comparison
_previous_state = None

def load_previous_state():
    """Load the previous state from disk."""
    global _previous_state
    try:
        with open(DATA_FILE, 'r') as f:
            _previous_state = json.load(f)
    except:
        _previous_state = {"cards": []}

def detect_changes(old_data, new_data):
    """Detect what changed between old and new state."""
    changes = []
    
    old_cards = {c['id']: c for c in old_data.get('cards', [])}
    new_cards = {c['id']: c for c in new_data.get('cards', [])}
    
    # Check for created cards
    for card_id, card in new_cards.items():
        if card_id not in old_cards:
            changes.append(f"📌 Created '{card['title']}'")
    
    # Check for deleted cards
    for card_id, card in old_cards.items():
        if card_id not in new_cards:
            changes.append(f"🗑️ Deleted '{card['title']}'")
    
    # Check for moved or edited cards
    for card_id, new_card in new_cards.items():
        if card_id in old_cards:
            old_card = old_cards[card_id]
            # Check for column move
            if new_card.get('column') != old_card.get('column'):
                changes.append(f"📍 Moved '{new_card['title']}' → {new_card.get('column', 'unknown')}")
            # Check for title/description edits
            elif new_card.get('title') != old_card.get('title'):
                changes.append(f"✏️ Renamed '{old_card['title']}' → '{new_card['title']}'")
            elif new_card.get('description') != old_card.get('description'):
                changes.append(f"📝 Edited '{new_card['title']}'")
    
    return changes

def send_webhook(data):
    """Send kanban data to OpenClaw webhook in background."""
    def _send():
        try:
            global _previous_state
            
            # Detect what changed
            if _previous_state is None:
                load_previous_state()
            
            changes = detect_changes(_previous_state, data)
            
            # Update previous state for next time
            _previous_state = data
            
            if changes:
                message = "🎯 Kanban: " + " | ".join(changes[:3])  # Max 3 changes shown
            else:
                card_count = len(data.get('cards', []))
                message = f"🎯 Kanban updated! {card_count} cards on board"
            
            payload = json.dumps({
                "text": message,
                "mode": "now"
            }).encode('utf-8')
            
            req = urllib.request.Request(
                WEBHOOK_URL,
                data=payload,
                headers={
                    'Content-Type': 'application/json',
                    'x-openclaw-token': HOOK_TOKEN
                },
                method='POST'
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception as e:
            print(f"Webhook warning: {e}")
    
    # Run webhook in background thread to not block response
    threading.Thread(target=_send, daemon=True).start()

class KanbanHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/save':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                # Validate JSON
                data = json.loads(post_data)
                
                # Save to file
                with open(DATA_FILE, 'w') as f:
                    json.dump(data, f, indent=2)
                
                # Send webhook to OpenClaw
                send_webhook(data)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok'}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/api/load':
            try:
                with open(DATA_FILE, 'r') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(data.encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            super().do_GET()

if __name__ == '__main__':
    # Load initial state
    load_previous_state()
    
    os.chdir(os.path.dirname(__file__) or '.')
    server = HTTPServer(('localhost', 8000), KanbanHandler)
    print('Kanban server running at http://localhost:8000/kanban.html')
    print('Press Ctrl+C to stop')
    server.serve_forever()
