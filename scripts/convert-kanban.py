#!/usr/bin/env python3
import json

# Read kanban data
with open('/Users/Josh/clawd/kanban/kanban.json', 'r') as f:
    data = json.load(f)

tasks = []

for card in data.get('cards', []):
    # Map column names to status
    column = card.get('column', 'backlog')
    status_map = {
        'todo': 'backlog',
        'inprogress': 'in_progress', 
        'review': 'review',
        'done': 'done',
        'suggestions': 'backlog'
    }
    status = status_map.get(column, column)
    
    task = {
        'id': card['id'],
        'title': card['title'],
        'description': card.get('description', ''),
        'status': status,
        'priority': 'medium',
        'createdAt': card.get('createdAt', ''),
        'statusChanges': card.get('statusChanges', [])
    }
    tasks.append(task)

# Add the onboarding guide from Mission Control
tasks.append({
    'id': 'guide_onboarding',
    'title': '🚀 Set Up Mission Control Remote Access',
    'description': 'Follow these steps to enable remote access to your Kanban board via Tailscale Funnel.',
    'status': 'backlog',
    'priority': 'high',
    'subtasks': [
        {'id': 'sub_001', 'title': 'Fix Tailscale version mismatch (update or reinstall)', 'done': False},
        {'id': 'sub_002', 'title': 'Enable Tailscale Funnel: tailscale funnel 18789', 'done': False},
        {'id': 'sub_003', 'title': 'Configure GitHub webhook for task updates', 'done': False},
        {'id': 'sub_004', 'title': 'Test remote access from another device', 'done': False}
    ],
    'createdAt': '2026-02-02T16:15:00-08:00'
})

# Write output
output = {'tasks': tasks}
with open('/Users/Josh/clawd/data/tasks.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"Created tasks.json with {len(tasks)} tasks")
