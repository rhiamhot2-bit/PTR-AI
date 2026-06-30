# PTR AI Version 1.0 Plan

PTR AI Version 1.0 is the first usable release of the jewelry-business AI agent system.

The goal of this version is simple:

> Discord command → PTR AI bot → n8n webhook → AI workflow → reply back to Discord

---

## 1. Version 1.0 Mission

PTR AI V1 helps a jewelry business owner, designer, or content creator send structured requests from Discord into automation workflows.

It focuses on 6 core work areas:

1. Jewelry design ideas
2. Content and marketing copy
3. Business and sales support
4. Video prompt generation
5. Rhino / 3D / CAD workflow help
6. Automation planning through n8n

---

## 2. Discord Commands

| Command | Purpose | Example |
| --- | --- | --- |
| `!design` | Jewelry concepts and product ideas | `!design Create a luxury emerald bridal ring concept.` |
| `!content` | Captions, ads, product descriptions | `!content Write a Thai Facebook caption for a diamond pendant.` |
| `!business` | Pricing, sales scripts, customer replies | `!business Help me price a custom 18K gold ring.` |
| `!veo` | Video generation prompts | `!veo Create a luxury jewelry showcase video prompt.` |
| `!rhino` | Rhino / Matrix / CAD help | `!rhino Explain the steps to model a pavé ring.` |
| `!automation` | n8n, lead handling, reports | `!automation Create a workflow for customer order updates.` |

---

## 3. Current Bot Flow

1. User types a command in Discord.
2. The bot checks the command prefix, normally `!`.
3. The bot builds a JSON payload.
4. The payload is sent to `N8N_WEBHOOK_URL`.
5. n8n processes the request.
6. n8n returns JSON with `reply` or `message`.
7. The bot posts the result back to Discord.

---

## 4. Payload Sent to n8n

```json
{
  "command": "design",
  "prompt": "Create a luxury emerald bridal ring concept.",
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

---

## 5. Expected n8n Response

Recommended response format:

```json
{
  "reply": "Here is the jewelry design concept..."
}
```

Alternative supported response:

```json
{
  "message": "Workflow completed successfully."
}
```

Plain text responses are also supported.

---

## 6. Version 1.0 Checklist

### GitHub

- [x] README created
- [x] `main.py` bot entry point created
- [x] Command handlers created
- [x] Webhook client created
- [x] Config helper created
- [x] `.env.example` created
- [x] `requirements.txt` created
- [x] Version 1.0 plan created

### Discord

- [ ] Bot token added to `.env`
- [ ] Message Content Intent enabled
- [ ] Bot invited to the correct Discord server
- [ ] Test channel created, for example `ptr-ai-test`

### n8n

- [ ] Webhook node created
- [ ] Webhook URL copied to `.env`
- [ ] Test response returns `reply` or `message`
- [ ] Each command routed to the correct AI workflow

### Local Computer

- [ ] Python virtual environment created
- [ ] Dependencies installed
- [ ] Bot started with `python main.py`
- [ ] Test command works in Discord

---

## 7. First Test Commands

Use these commands in Discord after the bot is running:

```text
!design ออกแบบแหวนเพชรหรูสำหรับลูกค้า UAE ใช้มรกตตรงกลาง
```

```text
!content เขียนแคปชั่นขายจี้ทอง 18K ฝังเพชร แนวหรูสายมู
```

```text
!business ช่วยคิดราคาและสคริปต์ตอบลูกค้างานแหวนสั่งทำ
```

```text
!veo สร้าง prompt วิดีโอเครื่องประดับหรู 8 วินาที ภาษาไทย
```

```text
!rhino อธิบายขั้นตอนทำแหวนฝังเพชรหนามเตยใน Rhino
```

```text
!automation วาง workflow n8n รับลูกค้าจาก Discord แล้วบันทึกลง Google Sheet
```

---

## 8. Definition of Done

PTR AI Version 1.0 is complete when:

1. The Discord bot can run without errors.
2. All 6 commands can send requests to n8n.
3. n8n can return a useful response to Discord.
4. The README explains how to install and run the project.
5. A beginner can understand the project purpose and next steps.

---

## 9. Next Version Ideas

After V1 works, future versions may add:

- Separate n8n workflow for each command
- Google Sheets customer/order logging
- Image prompt library for jewelry design
- Rhino script generator
- Customer lead form
- Admin report command
- Multi-brand content system for PTR JEW3D, ช่างทองยุค AI, and PTR Royal Gem Art
