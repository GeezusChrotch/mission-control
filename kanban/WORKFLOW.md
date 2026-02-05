# Kanban Workflow Documentation

## Overview
Local kanban board for task management with real-time webhook notifications to Mr. Clawncy.

## Access
- **URL:** https://dm-studio.tail43f9ee.ts.net:8443/kanban.html
- **Server:** localhost:8000 (Python HTTP server)
- **Tailscale:** Port 8443 proxied to localhost:8000

## Column Workflow

### 1. Suggestions (Purple)
- **Who adds:** Mr. Clawncy (AI assistant)
- **Purpose:** Ideas for projects, improvements, automations
- **Action:** Review and move to To Do if interested

### 2. To Do (Blue)
- **Who adds:** Josh (user) or Mr. Clawncy
- **Purpose:** Approved projects ready to start
- **Action:** Mr. Clawncy starts working immediately when cards appear here

### 3. In Progress (Orange)
- **Who moves:** Mr. Clawncy
- **Purpose:** Currently active work
- **Action:** Mr. Clawncy provides updates, moves to Done when complete

### 4. Done (Green)
- **Who moves:** Josh or Mr. Clawncy
- **Purpose:** Completed projects
- **Note:** Moving back to To Do means "not actually done, needs more work"

## Webhook Notifications
Every change triggers instant notification:
- 📌 Created
- 🗑️ Deleted
- 📍 Moved
- ✏️ Renamed
- 📝 Edited

## Server Details
- **Script:** /Users/Josh/clawd/kanban/server.py
- **Data:** /Users/Josh/clawd/kanban/kanban.json
- **Port:** 8000 (local) → 8443 (Tailscale)
- **Auto-start:** Via launchd (com.josh.kanban-server.plist)

## Files
- kanban.html - Main UI
- kanban.css - Styling (black bg, orange text/buttons)
- kanban.js - Client-side logic
- server.py - Python HTTP server with webhooks
- kanban.json - Card data
- mr-clawncy.jpg - Avatar/favicon

## Backup
Data backed up to: ~/kanban-backup-YYYYMMDD-HHMMSS/
