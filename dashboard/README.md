# PTR AI Dashboard V1

Dashboard V1 is a simple local web page for controlling PTR AI and testing the AI Designer flow.

It does not need a database or server yet.

---

## Files

```text
dashboard/
  index.html   # Main dashboard screen
  styles.css   # Dashboard design
  app.js       # Dashboard logic and n8n connection
```

---

## How to Open

1. Open the project folder on your computer.
2. Open the `dashboard` folder.
3. Double-click `index.html`.
4. The dashboard will open in your browser.

---

## How to Use

### 1. Add n8n Webhook URL

Paste your n8n webhook URL into the `n8n Webhook URL` field.

Example:

```text
https://your-n8n-domain/webhook/ptr-ai-agent
```

Then click:

```text
Save Webhook URL
```

The URL is saved in your browser local storage.

---

### 2. Use AI Designer

Fill in the jewelry design fields:

- Jewelry Type
- Style
- Metal
- Main Stone
- Accent Stones
- Target Market
- Budget Level
- Output Type
- Notes

Then click:

```text
Preview Payload
```

This shows the JSON that will be sent to n8n.

---

### 3. Send to n8n

Click:

```text
Send to n8n
```

The dashboard sends a POST request to your n8n webhook.

---

## Payload Format

The dashboard sends data like this:

```json
{
  "command": "design",
  "prompt": "You are PTR AI Designer...",
  "business": "jewelry",
  "source": "ptr_ai_dashboard",
  "mode": "ai_designer",
  "ai_designer": {
    "jewelry_type": "ring",
    "style": "luxury bridal UAE",
    "metal": "18K rose gold",
    "main_stone": "oval emerald",
    "accent_stones": "round diamonds",
    "target_market": "premium Middle East customer",
    "budget_level": "high",
    "output_type": "cad_brief",
    "notes": "hidden halo, comfortable daily wear"
  }
}
```

---

## Expected n8n Response

Recommended JSON response:

```json
{
  "reply": "Here is the jewelry design concept..."
}
```

The dashboard will show any JSON or text response in the Output panel.

---

## V1 Limitations

Dashboard V1 is intentionally simple.

It does not yet include:

- Login system
- Database
- User management
- Request history
- Image upload
- CAD file upload

These will be added in future versions.
