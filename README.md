# PTR AI Agent for Jewelry Business

PTR AI is a Discord bot for jewelry design, CAD briefs, customer/project memory, n8n AI workflows, business support, content, video prompts, Rhino guidance, and automation.

## Commands

| Command | Use case |
| --- | --- |
| `!design` | Jewelry concepts, collections, stone/metal ideas, and product design briefs via n8n. |
| `!cadbrief` | Convert Thai or English jewelry text into structured CAD fields and save JSON locally. |
| `!content` | Captions, ads, product descriptions, launch posts, and email copy. |
| `!business` | Pricing, customer service, sales scripts, and operations prompts. |
| `!customer` | Create or update a customer profile. |
| `!findcustomer` | Find a stored customer profile. |
| `!project` | Create a customer project folder and production stages. |
| `!veo` | Video generation prompts for jewelry showcases and campaigns. |
| `!rhino` | Rhino/3D/CAD workflow prompts. |
| `!automation` | n8n workflow ideas and operational automations. |

Examples:

```text
!design Create a luxury bridal ring concept with an oval emerald.
!cadbrief แหวนไซซ์ 52 ทอง 18K มรกต Oval 8x6 มม. หนามเตย 4 เตย
!customer Ahmed country=UAE budget=500000 stone=Emerald metal=22K notes="Royal client"
!project Ahmed Royal_Ring
```

## CAD Brief Output

The `!cadbrief` command extracts:

- jewelry type and ring size
- metal
- center-stone type, shape, and dimensions
- setting type and prong count
- missing required information
- readiness status: `ready_for_cad` or `needs_information`

Briefs are saved under:

```text
MEMORY_ROOT/
└── CAD_Briefs/
    └── YYYY-MM-DD_HH-MM-SS-ffffff_cadbrief.json
```

The portable data contract is defined in `schemas/cad_brief.schema.json`.

## Project Structure

```text
main.py                 # Discord bot entry point
requirements.txt        # Python dependencies
.env.example            # Environment variable template
commands/               # Discord command handlers
webhook/                # Async n8n webhook client
utils/                  # Configuration, parser, and memory helpers
schemas/                # Structured Jewelry CAD data contracts
tests/                  # Parser tests
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env`.
4. Set the required values:

   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   N8N_WEBHOOK_URL=http://localhost:5678/webhook/ptr-ai
   MEMORY_ROOT=C:\Users\YOUR_NAME\Desktop\PTR_AI_COMPANY\Memory
   ```

5. Enable **Message Content Intent** in the Discord Developer Portal.
6. Run:

   ```bash
   python main.py
   ```

## Validation

Run the standard-library tests:

```bash
python -m unittest discover -s tests -v
```
