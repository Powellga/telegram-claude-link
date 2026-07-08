## Telegram MCP Server

This project is a Telegram MCP server. The MCP tools are registered globally and available in all Claude Code sessions.

When the user asks to send a Telegram message or interact with Telegram, use ToolSearch to find the `mcp__telegram__*` tools:
- `mcp__telegram__telegram_send_message` — send a message by contact name
- `mcp__telegram__telegram_search_contacts` — find contacts
- `mcp__telegram__telegram_list_chats` — list recent chats
- `mcp__telegram__telegram_read_messages` — read messages from a chat
- `mcp__telegram__telegram_get_unread` — check unread messages

## Client Status Alert Format

Messages are sent with Telegram **Markdown** (Telethon default). Supported:
`` `inline monospace` ``, ` ```triple-backtick code blocks``` ` (monospace,
renders as a copyable black box — Telegram adds a "copy" button automatically),
`**bold**`, `__italic__`, `[text](url)`.

When sending a client status alert, ALWAYS use this layout:

````
```
{CLIENT NAME}
```
HVA: {hva}
CAM: {cam}
Tech: {tech}

⚠️ Status: {RED|YELLOW|GREEN} | Age: {N}d

{one-paragraph summary of the situation}

**ACTION:** {what needs to happen and who owns it}
````

Rules:
- **Client name** goes in a triple-backtick code block so it renders monospace
  in a distinct box. Ignore the "copy" button Telegram adds — it is expected.
- **HVA / CAM / Tech** each on their own line.
- **Status** on its own line: `⚠️ Status: X | Age: Nd`.
- **Summary**: one concise paragraph describing the situation.
- **ACTION** line is **bold** (`**ACTION:**`). Omit the entire ACTION line when
  no action is required (e.g. a resolved / GREEN alert).
