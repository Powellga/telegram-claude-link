# telegram-claude-link

A Telegram MCP server for [Claude Code](https://claude.com/claude-code). Lets Claude send and read messages on your **personal** Telegram account via [Telethon](https://docs.telethon.dev), so the assistant can search contacts, read chats, check unread messages, and send replies on your behalf.

## What it gives Claude

Five tools, registered under the `mcp__telegram__*` namespace:

| Tool | Purpose |
|------|---------|
| `telegram_send_message` | Send a message to a contact/chat by name |
| `telegram_search_contacts` | Find contacts/chats matching a name (or list all) |
| `telegram_list_chats` | List the most recent chats |
| `telegram_read_messages` | Read recent messages from a chat |
| `telegram_get_unread` | Show chats with unread messages |

The Telegram client uses a lazy-connect pattern so the MCP server starts instantly and only connects to Telegram on the first tool call (avoids MCP startup timeouts).

## Requirements

- Python 3.10+
- A Telegram account
- API ID + API Hash from https://my.telegram.org
- Claude Code (or any other MCP client)

Python dependencies (`requirements.txt`):

```
mcp[cli]>=1.26.0
telethon>=1.36.0
pydantic>=2.0.0
```

## Install

```bash
./install.sh
```

This creates a `.venv`, installs requirements, and prints next steps. On Windows the same script works under Git Bash; otherwise create a venv manually and `pip install -r requirements.txt`.

## Authenticate (one time)

```bash
python auth_telegram.py        # macOS/Linux/Git Bash
auth.bat                       # Windows convenience wrapper
```

You'll be prompted for your API ID, API Hash (or set `TELEGRAM_API_ID` / `TELEGRAM_API_HASH` in the environment), phone number, and the verification code Telegram sends you. A `telegram.session` file is written next to the script - this is what the MCP server uses for subsequent runs. Keep it private.

## Wire it into Claude Code

Add to `~/.claude/settings.json` (global) or your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "telegram": {
      "command": "python",
      "args": ["/absolute/path/to/telegram_mcp.py"],
      "env": {
        "TELEGRAM_API_ID": "your_api_id",
        "TELEGRAM_API_HASH": "your_api_hash"
      }
    }
  }
}
```

Optional: set `TELEGRAM_SESSION_PATH` to point at a session file in a different location (defaults to `./telegram` next to `telegram_mcp.py`).

## Files

| File | Purpose |
|------|---------|
| `telegram_mcp.py` | The MCP server (FastMCP + Telethon) |
| `auth_telegram.py` | One-time interactive Telegram login |
| `auth.bat` | Windows wrapper that activates `.venv` and runs `auth_telegram.py` |
| `install.sh` | Creates `.venv` and installs `requirements.txt` |
| `requirements.txt` | Python dependencies |
| `CLAUDE.md` | Hint to Claude Code about the available tools |

## Security notes

- This server uses your **personal** Telegram account, not a bot account. Anything Claude sends will appear to come from you.
- The `telegram.session` file is the equivalent of a logged-in session - do not commit it or share it.
- Telethon will respect Telegram's rate limits; very high call volumes may trigger temporary throttling.
