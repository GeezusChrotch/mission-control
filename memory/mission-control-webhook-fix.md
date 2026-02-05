# Mission Control Webhook Fix - 2026-02-04

## Problem
Mission Control webhooks were not working. The issue was a port mismatch between OpenClaw gateway and Tailscale funnel configuration.

## Root Cause
- OpenClaw gateway was configured on port 8080
- Mission Control expected port 18789
- Tailscale funnel had stale config pointing to port 8080
- Zombie tailscale processes were holding port 443

## Solution Applied
1. **Changed OpenClaw gateway port** from 8080 to 18789 (in `~/.openclaw/openclaw.json`)
2. **Reset Tailscale funnel config** using `tailscale funnel reset`
3. **Killed zombie processes** using `pkill -9 -f "tailscale (funnel|serve)"`
4. **Started Tailscale funnel** on port 18789: `tailscale funnel 18789`

## Current Configuration
- **OpenClaw Gateway**: Port 18789
- **Mission Control Config**: `~/.clawdbot/mission-control.json` points to `http://127.0.0.1:18789`
- **Tailscale Funnel**: `https://dm-studio.tail43f9ee.ts.net/` → `http://127.0.0.1:18789`
- **Webhook Transform**: `~/.clawdbot/hooks-transforms/github-mission-control.mjs`

## GitHub Webhook URL
```
https://dm-studio.tail43f9ee.ts.net/hooks/github?token=c42c95ffb81c515fd5ef4a4ff44ade352a654a674e1c9eca
```

## How It Works
1. GitHub sends webhook on push events to `data/tasks.json`
2. Tailscale funnel receives at `https://dm-studio.tail43f9ee.ts.net/`
3. Forwards to OpenClaw gateway at `http://127.0.0.1:18789`
4. Gateway invokes `github-mission-control.mjs` transform
5. Transform detects tasks moved to "in_progress"
6. Transform wakes agent via `/hooks/agent` endpoint
7. Agent receives work order and executes task

## Important Notes
- **DON'T change Mission Control port** - keep it at 18789 (standard)
- **If funnel stops working**: Check for zombie processes with `ps aux | grep tailscale`
- **If port 443 conflict**: Run `pkill -9 -f "tailscale (funnel|serve)"` then `tailscale funnel reset`
- **Funnel must stay running** - use `nohup` or run in background screen/tmux

## Testing
To test: Move a task to "In Progress" in Mission Control dashboard. The agent should receive a notification within seconds.
