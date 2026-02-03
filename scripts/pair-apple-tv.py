#!/usr/bin/env python3
"""Pair with Apple TV non-interactively"""

import asyncio
import sys
from pyatv.scan import scan
from pyatv.pair import pair
from pyatv.const import Protocol

async def pair_device(name, pin, protocol=Protocol.AirPlay):
    print(f"Scanning for {name}...")
    
    devices = await scan()
    device = None
    for d in devices:
        if d.name == name:
            device = d
            break
    
    if not device:
        print(f"Device '{name}' not found")
        return
    
    print(f"Found {device.name} at {device.address}")
    
    print(f"Pairing via {protocol.name}...")
    pairing = await pair(device, protocol)
    
    async with pairing:
        print(f"PIN: {pin}")
        await pairing.start()
        
        # The PIN should be entered on the TV
        # This is where we'd need manual input
        
print("This script requires manual PIN entry on the TV")
print("Run this when you can see the TV screen:")
print("  python3 pair-apple-tv.py Lounge 9833")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        name = sys.argv[1]
        pin = sys.argv[2]
        asyncio.run(pair_device(name, pin))
    else:
        print("Usage: pair-apple-tv.py <device_name> <pin>")
        print("Example: pair-apple-tv.py Lounge 9833")