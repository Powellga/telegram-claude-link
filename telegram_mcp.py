"""
Telegram MCP Server
====================
An MCP server that gives Claude Code the ability to send and read
Telegram messages using your personal account via Telethon.

Usage with Claude Code:
    Add to ~/.claude/settings.json or project .mcp.json:
    {
        "mcpServers": {
            "telegram": {
                "command": "python",
                "args": ["/path/to/telegram_mcp.py"],
                "env": {
                    "TELEGRAM_API_ID": "your_api_id",
                    "TELEGRAM_API_HASH": "your_api_hash"
                }
            }
        }
    }

Before first use, run auth_telegram.py to create a session file.

Environment Variables:
    TELEGRAM_API_ID: Your Telegram API ID (from https://my.telegram.org)
    TELEGRAM_API_HASH: Your Telegram API Hash
    TELEGRAM_SESSION_PATH: Path to session file (default: ./telegram)
"""

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP
from telethon import TelegramClient
from telethon.tl.types import User, Chat, Channel

# ─── Configuration ──────────────────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION_PATH = os.getenv("TELEGRAM_SESSION_PATH", os.path.join(SCRIPT_DIR, "telegram"))


# ─── Lifespan: Manage Telegram Client ──────────────────────────────────────

@asynccontextmanager
async def telegram_lifespan(server):
    """Connect to Telegram using existing session."""
    if not API_ID or not API_HASH:
        raise RuntimeError(
            "TELEGRAM_API_ID and TELEGRAM_API_HASH environment variables are required. "
            "Get them from https://my.telegram.org"
        )

    session_file = SESSION_PATH + ".session"
    if not os.path.exists(session_file):
        raise RuntimeError(
            f"Session file not found at {session_file}. "
            "Run auth_telegram.py first to authenticate."
        )

    client = TelegramClient(SESSION_PATH, int(API_ID), API_HASH)
    await client.connect()

    if not await client.is_user_authorized():
        raise RuntimeError(
            "Telegram session expired. Run auth_telegram.py again to re-authenticate."
        )

    try:
        yield {"telegram_client": client}
    finally:
        await client.disconnect()


# ─── Server Setup ───────────────────────────────────────────────────────────

mcp = FastMCP(
    "Telegram",
    description="Send and read Telegram messages using your personal account",
    lifespan=telegram_lifespan,
)


# ─── Helpers ────────────────────────────────────────────────────────────────

def _get_client(ctx) -> TelegramClient:
    """Get the Telegram client from the MCP context."""
    return ctx.request_context.lifespan_context["telegram_client"]


def _format_entity_name(entity) -> str:
    """Get a display name for a Telegram entity."""
    if isinstance(entity, User):
        parts = []
        if entity.first_name:
            parts.append(entity.first_name)
        if entity.last_name:
            parts.append(entity.last_name)
        name = " ".join(parts) if parts else "Unknown"
        if entity.username:
            name += f" (@{entity.username})"
        return name
    elif isinstance(entity, (Chat, Channel)):
        return entity.title or "Unknown Group"
    return str(entity)


def _name_matches(entity, query: str) -> bool:
    """Check if an entity name matches a search query (case-insensitive)."""
    query_lower = query.lower().strip()

    if isinstance(entity, User):
        first = (entity.first_name or "").lower()
        last = (entity.last_name or "").lower()
        full = f"{first} {last}".strip()
        username = (entity.username or "").lower()

        return (
            query_lower == first
            or query_lower == last
            or query_lower == full
            or query_lower == username
            or query_lower in full
            or query_lower in username
        )
    elif isinstance(entity, (Chat, Channel)):
        title = (entity.title or "").lower()
        return query_lower in title

    return False


async def _find_contact(client: TelegramClient, name: str) -> list:
    """Find contacts matching a name. Returns list of (entity, dialog) tuples."""
    matches = []

    # Search through dialogs (recent chats)
    async for dialog in client.iter_dialogs(limit=None):
        entity = dialog.entity
        if _name_matches(entity, name):
            matches.append((entity, dialog))

    return matches


# ─── Tools ──────────────────────────────────────────────────────────────────

@mcp.tool()
async def telegram_send_message(
    contact_name: str,
    message: str,
    ctx: Any = None,
) -> str:
    """Send a message to a Telegram contact by name.

    Searches your contacts and recent chats for a matching name,
    then sends the message. If multiple matches are found, returns
    the list so you can be more specific.

    Args:
        contact_name: The name to search for (first name, last name, full name, or username)
        message: The message text to send
    """
    client = _get_client(ctx)
    matches = await _find_contact(client, contact_name)

    if not matches:
        return f"No contact found matching '{contact_name}'. Use telegram_search_contacts to find the right name."

    if len(matches) > 1:
        lines = [f"Multiple matches for '{contact_name}'. Please be more specific:"]
        for entity, dialog in matches:
            lines.append(f"  - {_format_entity_name(entity)}")
        return "\n".join(lines)

    entity, dialog = matches[0]
    await client.send_message(entity, message)
    return f"Message sent to {_format_entity_name(entity)}: \"{message}\""


@mcp.tool()
async def telegram_search_contacts(
    query: str = "",
    ctx: Any = None,
) -> str:
    """Search your Telegram contacts and chats by name.

    If query is empty, lists all recent contacts/chats.

    Args:
        query: Name to search for (optional — leave empty to list all)
    """
    client = _get_client(ctx)
    results = []

    async for dialog in client.iter_dialogs(limit=None):
        entity = dialog.entity
        if not query or _name_matches(entity, query):
            entity_type = "user" if isinstance(entity, User) else "group/channel"
            results.append(f"  - {_format_entity_name(entity)} [{entity_type}]")

    if not results:
        return f"No contacts or chats found matching '{query}'."

    header = f"Contacts matching '{query}':" if query else "All recent contacts/chats:"
    return header + "\n" + "\n".join(results)


@mcp.tool()
async def telegram_list_chats(
    limit: int = 20,
    ctx: Any = None,
) -> str:
    """List your most recent Telegram chats/conversations.

    Args:
        limit: Maximum number of chats to return (default: 20)
    """
    client = _get_client(ctx)
    lines = [f"Recent chats (last {limit}):"]

    count = 0
    async for dialog in client.iter_dialogs(limit=limit):
        entity = dialog.entity
        entity_type = "user" if isinstance(entity, User) else "group/channel"
        unread = f" [{dialog.unread_count} unread]" if dialog.unread_count else ""
        lines.append(f"  - {_format_entity_name(entity)} [{entity_type}]{unread}")
        count += 1

    if count == 0:
        return "No chats found."

    return "\n".join(lines)


@mcp.tool()
async def telegram_read_messages(
    contact_name: str,
    limit: int = 10,
    ctx: Any = None,
) -> str:
    """Read recent messages from a Telegram chat.

    Args:
        contact_name: The name of the contact or chat to read from
        limit: Number of recent messages to return (default: 10)
    """
    client = _get_client(ctx)
    matches = await _find_contact(client, contact_name)

    if not matches:
        return f"No contact found matching '{contact_name}'."

    if len(matches) > 1:
        lines = [f"Multiple matches for '{contact_name}'. Please be more specific:"]
        for entity, dialog in matches:
            lines.append(f"  - {_format_entity_name(entity)}")
        return "\n".join(lines)

    entity, dialog = matches[0]
    messages = []

    async for msg in client.iter_messages(entity, limit=limit):
        if msg.text:
            sender = "You" if msg.out else _format_entity_name(msg.sender) if msg.sender else "Unknown"
            time_str = msg.date.strftime("%Y-%m-%d %H:%M")
            messages.append(f"  [{time_str}] {sender}: {msg.text}")

    if not messages:
        return f"No recent text messages in chat with {_format_entity_name(entity)}."

    header = f"Recent messages with {_format_entity_name(entity)}:"
    messages.reverse()  # Show oldest first
    return header + "\n" + "\n".join(messages)


@mcp.tool()
async def telegram_get_unread(
    limit: int = 10,
    ctx: Any = None,
) -> str:
    """Get chats with unread messages.

    Args:
        limit: Maximum number of chats to check (default: 10)
    """
    client = _get_client(ctx)
    lines = ["Chats with unread messages:"]

    count = 0
    async for dialog in client.iter_dialogs(limit=None):
        if dialog.unread_count > 0:
            entity = dialog.entity
            lines.append(f"  - {_format_entity_name(entity)}: {dialog.unread_count} unread")
            count += 1
            if count >= limit:
                break

    if count == 0:
        return "No unread messages."

    return "\n".join(lines)


# ─── Main ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
