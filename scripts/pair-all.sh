#!/bin/bash
# Pair with Apple TVs - run this when you can see the TV screen

echo "=== Apple TV Pairing Script ==="
echo ""
echo "Make sure you can see the PIN on your TV screen"
echo ""

DEVICE=$1
PIN=$2

if [ -z "$DEVICE" ] || [ -z "$PIN" ]; then
    echo "Usage: ./pair-all.sh <device_name> <pin>"
    echo ""
    echo "Available Apple TVs:"
    atvremote scan 2>/dev/null | grep -A3 "Apple TV" | grep "Name:" | awk '{print "  " $2}'
    echo ""
    echo "Examples:"
    echo "  ./pair-all.sh Lounge 9833"
    echo "  ./pair-all.sh Den 1234"
    echo "  ./pair-all.sh 'Bedroom TV' 5678"
    exit 1
fi

echo "Pairing with $DEVICE using PIN $PIN..."
echo "Press Ctrl+C to cancel"
sleep 2

atvremote -n "$DEVICE" --protocol airplay pair --pin $PIN