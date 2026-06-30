# PTR AI Dashboard and AI Designer

This document defines the next major step for PTR AI Version 1.0:

> Discord Bot + n8n + Dashboard + AI Designer

The goal is to make PTR AI easier to control, easier to test, and smarter for jewelry design work.

---

## 1. Big Picture

PTR AI currently works as a Discord command bot that forwards requests to n8n.

The new system adds two important parts:

1. **Dashboard** — a simple control screen for the PTR AI system.
2. **AI Designer** — a specialized jewelry design brain for concepts, CAD briefs, stone maps, and premium product storytelling.

---

## 2. Dashboard Purpose

The Dashboard is the control room for PTR AI.

It should help the owner see:

- Which commands are available
- What each command does
- Current system status
- Example prompts
- n8n webhook connection status
- Future customer/order/design records

Version 1 Dashboard should be simple and easy to understand.

---

## 3. Dashboard V1 Sections

### 3.1 System Status

Shows:

- Bot status: planned / running / error
- n8n webhook: configured / not configured
- Discord command prefix
- Current PTR AI version

### 3.2 Command Center

Shows all 6 commands:

- `!design`
- `!content`
- `!business`
- `!veo`
- `!rhino`
- `!automation`

Each command should include:

- Purpose
- Example prompt
- Expected output

### 3.3 AI Designer Panel

A special panel for jewelry design requests.

Inputs:

- Jewelry type
- Customer style
- Metal
- Main stone
- Accent stones
- Target market
- Budget level
- Output type

Example output types:

- Design concept
- CAD brief
- Stone map
- Product story
- Sales caption
- Veo video prompt

### 3.4 Workflow Log

Future section for storing:

- Recent requests
- Discord user
- Command used
- n8n result
- Timestamp

For V1, this can be a placeholder.

---

## 4. AI Designer Role

AI Designer is the jewelry-specialist brain inside PTR AI.

It should think like:

- Jewelry designer
- CAD/CAM planner
- Gemstone stylist
- Luxury brand storyteller
- Sales assistant
- Rhino/MatrixGold assistant

---

## 5. AI Designer Core Tasks

AI Designer should help with:

1. Jewelry concept design
2. Luxury collection planning
3. Bridal and engagement jewelry
4. UAE / Arab luxury style concepts
5. Sacred geometry and spiritual jewelry
6. Stone and metal selection
7. CAD modeling brief creation
8. Rhino / MatrixGold step planning
9. Product storytelling
10. Sales and marketing content

---

## 6. AI Designer Input Format

Recommended JSON input from Dashboard or n8n:

```json
{
  "mode": "ai_designer",
  "jewelry_type": "ring",
  "style": "luxury bridal UAE",
  "metal": "18K rose gold",
  "main_stone": "emerald oval",
  "accent_stones": "round diamonds",
  "target_market": "premium Middle East customer",
  "budget_level": "high",
  "output_type": "cad_brief",
  "notes": "hidden halo, comfortable daily wear"
}
```

---

## 7. AI Designer Output Format

Recommended response:

```json
{
  "title": "Emerald Royal Bridal Ring",
  "concept": "A luxury bridal ring inspired by Middle East royal elegance.",
  "materials": ["18K rose gold", "oval emerald", "round diamonds"],
  "design_details": [
    "Oval emerald center stone",
    "Hidden halo under the main stone",
    "Pave diamond shoulders",
    "Comfort-fit ring band"
  ],
  "cad_brief": "Model an oval center setting, hidden halo, tapered shank, and pave shoulders.",
  "stone_map": "1 oval emerald center, 24 round diamonds on halo, 30 round diamonds on shank.",
  "sales_story": "Designed for a bride who wants royal elegance, spiritual beauty, and timeless value."
}
```

---

## 8. First Dashboard Technology Choice

For beginner-friendly V1, use a simple local web dashboard first.

Recommended first version:

- HTML
- CSS
- JavaScript
- No database yet
- No login yet
- Can open directly in browser

Later versions can use:

- Flask / FastAPI
- SQLite
- Google Sheets
- n8n dashboard API
- Customer/order database

---

## 9. New Project Structure

Recommended additions:

```text
dashboard/
  index.html
  styles.css
  app.js

docs/
  DASHBOARD_AND_AI_DESIGNER.md
  AI_DESIGNER_PROMPT.md
```

---

## 10. Build Order

### Step 1
Create Dashboard V1 static screen.

### Step 2
Create AI Designer prompt and output format.

### Step 3
Connect Dashboard form to n8n webhook.

### Step 4
Send Dashboard requests into the same PTR AI flow.

### Step 5
Store request history.

### Step 6
Add customer/order/design records.

---

## 11. Definition of Done for This Phase

This phase is complete when:

1. A dashboard page exists.
2. The dashboard explains PTR AI commands.
3. AI Designer has a clear prompt and JSON structure.
4. A beginner can understand what to build next.
5. The current Discord bot still works.
