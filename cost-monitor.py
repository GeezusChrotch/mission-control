#!/usr/bin/env python3
"""
Simple cost monitoring for Clawdbot API usage.
Tracks token usage and estimates costs.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Claude 3.5 Sonnet pricing (as of Jan 2026)
PRICING = {
    "input_per_million": 3.00,    # $3 per 1M input tokens
    "output_per_million": 15.00   # $15 per 1M output tokens
}

def get_session_status():
    """Get current session token usage from Clawdbot."""
    import subprocess
    try:
        # This would need to be implemented to get actual usage stats
        # For now, return mock data
        return {
            "input_tokens": 149000,
            "output_tokens": 796,
            "model": "anthropic/claude-3-5-sonnet-20241022"
        }
    except:
        return None

def calculate_cost(input_tokens, output_tokens):
    """Calculate estimated cost based on token usage."""
    input_cost = (input_tokens / 1_000_000) * PRICING["input_per_million"]
    output_cost = (output_tokens / 1_000_000) * PRICING["output_per_million"]
    return input_cost + output_cost

def load_usage_history():
    """Load historical usage data."""
    cache_file = Path.home() / ".clawd-usage-history.json"
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_usage_snapshot(data):
    """Save current usage snapshot."""
    cache_file = Path.home() / ".clawd-usage-history.json"
    history = load_usage_history()
    
    today = datetime.now().strftime('%Y-%m-%d')
    history[today] = {
        "timestamp": datetime.now().isoformat(),
        "input_tokens": data["input_tokens"],
        "output_tokens": data["output_tokens"],
        "estimated_cost": calculate_cost(data["input_tokens"], data["output_tokens"])
    }
    
    # Keep last 30 days
    cutoff = datetime.now() - timedelta(days=30)
    history = {k: v for k, v in history.items() 
              if datetime.fromisoformat(v["timestamp"]) > cutoff}
    
    try:
        with open(cache_file, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save usage history: {e}")

def show_usage_report():
    """Display usage report."""
    print("🔍 Clawdbot API Usage Report")
    print("=" * 40)
    
    # Current session
    status = get_session_status()
    if status:
        cost = calculate_cost(status["input_tokens"], status["output_tokens"])
        print(f"📊 Current Session:")
        print(f"   Input tokens:  {status['input_tokens']:,}")
        print(f"   Output tokens: {status['output_tokens']:,}")
        print(f"   Model: {status['model']}")
        print(f"   Estimated cost: ${cost:.4f}")
        print()
        
        # Save snapshot
        save_usage_snapshot(status)
    
    # Historical data
    history = load_usage_history()
    if history:
        print(f"📈 Recent Usage (last {len(history)} days):")
        total_cost = 0
        for date, data in sorted(history.items()):
            total_cost += data["estimated_cost"]
            print(f"   {date}: ${data['estimated_cost']:.4f}")
        
        print(f"\n💰 Total estimated cost: ${total_cost:.2f}")
        print(f"📅 Average per day: ${total_cost/len(history):.4f}")
        
        # Monthly projection
        if len(history) > 0:
            avg_daily = total_cost / len(history)
            monthly_projection = avg_daily * 30
            print(f"📊 Monthly projection: ${monthly_projection:.2f}")
    
    print(f"\n💡 Tips:")
    print(f"   - Claude Pro ($20/mo) vs API (current ~${total_cost/len(history)*30:.2f}/mo)")
    print(f"   - Check console.anthropic.com for detailed billing")
    print(f"   - Morning summaries use ~1k-3k tokens daily")

if __name__ == "__main__":
    show_usage_report()