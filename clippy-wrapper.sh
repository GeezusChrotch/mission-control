#!/bin/bash

# Clippy wrapper for Josh's Microsoft 365 access
# Usage: ./clippy-wrapper.sh [clippy-command] [options]

CLIPPY_DIR="/tmp/clippy"

if [ ! -d "$CLIPPY_DIR" ]; then
    echo "Error: Clippy not found at $CLIPPY_DIR"
    exit 1
fi

cd "$CLIPPY_DIR"

if [ $# -eq 0 ]; then
    echo "Usage: $0 [clippy-command] [options]"
    echo "Examples:"
    echo "  $0 login --interactive    # First-time setup"
    echo "  $0 whoami                 # Check auth status"
    echo "  $0 mail                   # View inbox"
    echo "  $0 mail --unread          # Unread emails"
    echo "  $0 calendar               # Today's calendar"
    echo "  $0 calendar --week        # Week view"
    echo "  $0 keepalive --interval 600  # Keepalive every 10 minutes"
    exit 1
fi

# Run clippy with all passed arguments
bun run src/cli.ts "$@"