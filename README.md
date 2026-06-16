# PTR AI Agent for Jewelry Business

PTR AI is a Discord bot that forwards jewelry-business AI requests to an n8n webhook. It is designed for jewelry design, marketing content, business support, video prompting, Rhino/CAD support, and automation workflows.

## Commands

| Command | Use case |
| --- | --- |
| `!design` | Jewelry concepts, collections, stone/metal ideas, product design briefs. |
| `!content` | Captions, ads, product descriptions, launch posts, email copy. |
| `!business` | Pricing ideas, customer service responses, sales scripts, operations prompts. |
| `!veo` | Video generation prompts for jewelry showcases and campaigns. |
| `!rhino` | Rhino/3D/CAD workflow prompts for jewelry modeling. |
| `!automation` | n8n workflow ideas, lead handling, order updates, reporting automations. |

Example:

```text
!design Create a luxury bridal ring concept with an oval emerald and hidden halo.
```

## Project Structure

```text
main.py                 # Discord bot entry point
requirements.txt        # Python dependencies
.env.example            # Environment variable template
commands/               # Discord command handlers
webhook/                # n8n webhook client
utils/                  # Configuration helpers
```

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy the example environment file and edit it:

   ```bash
   cp .env.example .env
   ```

4. Set the required values in `.env`:

   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   N8N_WEBHOOK_URL=https://your-n8n-domain/webhook/ptr-ai-agent
   ```

5. Run the bot:

   ```bash
   python main.py
   ```

## n8n Webhook Payload

Every command sends a `POST` request to `N8N_WEBHOOK_URL` with JSON similar to:

```json
{
  "command": "design",
  "prompt": "Create a luxury bridal ring concept with an oval emerald.",
  "business": "jewelry",
  "discord": {
    "user_id": "123",
    "user_name": "designer#0001",
    "channel_id": "456",
    "guild_id": "789",
    "message_id": "101112"
  }
}
```

If n8n returns JSON with a `reply` or `message` field, the bot posts it back into Discord. Plain text responses are also supported.

## Discord Bot Requirements

Enable the **Message Content Intent** for your bot in the Discord Developer Portal because this bot uses text commands such as `!design`.
