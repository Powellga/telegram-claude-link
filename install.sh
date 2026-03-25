#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Telegram MCP Server Setup ==="
echo

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
else
    echo "Virtual environment already exists."
fi

# Activate and install
echo "Installing dependencies..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    .venv/Scripts/pip install -r requirements.txt
else
    .venv/bin/pip install -r requirements.txt
fi

echo
echo "=== Setup Complete ==="
echo
echo "Next steps:"
echo "  1. Get API credentials from https://my.telegram.org"
echo "  2. Run: python auth_telegram.py"
echo "  3. Add to Claude Code MCP config (see README)"
