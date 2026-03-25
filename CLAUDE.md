## Telegram MCP Server

This project is a Telegram MCP server. The MCP tools are registered globally and available in all Claude Code sessions.

When the user asks to send a Telegram message or interact with Telegram, use ToolSearch to find the `mcp__telegram__*` tools:
- `mcp__telegram__telegram_send_message` — send a message by contact name
- `mcp__telegram__telegram_search_contacts` — find contacts
- `mcp__telegram__telegram_list_chats` — list recent chats
- `mcp__telegram__telegram_read_messages` — read messages from a chat
- `mcp__telegram__telegram_get_unread` — check unread messages
