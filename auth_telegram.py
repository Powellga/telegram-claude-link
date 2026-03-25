"""
Telegram Authentication Script
==============================
Run this ONCE to authenticate your Telegram account.
Creates a session file that the MCP server uses to send messages.

Usage:
    python auth_telegram.py

You'll need:
    1. API ID and API Hash from https://my.telegram.org
    2. Your phone number (with country code, e.g. +1234567890)
    3. The verification code Telegram sends you

The session file is saved next to this script as 'telegram.session'.
"""

import asyncio
import os
import sys

from telethon import TelegramClient

# Session file lives next to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_PATH = os.path.join(SCRIPT_DIR, "telegram")


async def main():
    print("=" * 50)
    print("  Telegram Authentication Setup")
    print("=" * 50)
    print()

    # Check for env vars first, then prompt
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")

    if not api_id:
        print("Get your API ID and Hash from https://my.telegram.org")
        print()
        api_id = input("API ID: ").strip()

    if not api_hash:
        api_hash = input("API Hash: ").strip()

    if not api_id or not api_hash:
        print("Error: API ID and API Hash are required.")
        sys.exit(1)

    api_id = int(api_id)

    client = TelegramClient(SESSION_PATH, api_id, api_hash)
    await client.start()

    me = await client.get_me()
    print()
    print(f"Authenticated as: {me.first_name} {me.last_name or ''}")
    print(f"Phone: {me.phone}")
    print(f"Username: @{me.username or 'none'}")
    print()
    print(f"Session saved to: {SESSION_PATH}.session")
    print()
    print("You can now use the Telegram MCP server.")
    print("Make sure to set these environment variables in your MCP config:")
    print(f"  TELEGRAM_API_ID={api_id}")
    print(f"  TELEGRAM_API_HASH={api_hash}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
