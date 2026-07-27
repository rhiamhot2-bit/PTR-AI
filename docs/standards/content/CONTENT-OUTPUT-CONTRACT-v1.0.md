# CONTENT-OUTPUT-CONTRACT v1.0

## Purpose
กำหนดโครงสร้างผลลัพธ์มาตรฐานสำหรับ Content Agent และ Workflow เพื่อให้ Discord, n8n, Dashboard และผู้ตรวจอ่านผลลัพธ์ได้ตรงกัน

## Required fields

```yaml
request_id: string
mode: jewelry_expert | founder_presenter | ai_partner | asset_reuse
platform: facebook | tiktok | youtube | shorts | reels | discord | blog | email | other
objective: string
audience: string
language: th | en | bilingual
status: draft | needs_review | needs_expert_review | approved | published | archived

core_message: string
hook: string
script: string
caption: string
cta: string
keywords: []
hashtags: []

scene_plan: []
asset_requirements: []
image_prompt: string
thumbnail_prompt: string
video_prompt: string
production_notes: []

accuracy_notes: []
risks: []
human_approval_required: true
approval_reason: []
```

## Rules
- ฟิลด์ที่ไม่เกี่ยวข้องให้ส่งเป็นค่าว่างหรือรายการว่าง ห้ามสร้างข้อมูลขึ้นมาเพื่อให้ครบ
- `human_approval_required` ต้องเป็น `true` จนกว่าจะมีระบบอนุมัติที่ตรวจสอบได้
- ห้ามส่ง Token, Password, Secret, ข้อมูลลูกค้า หรือพาธไฟล์ส่วนตัวในผลลัพธ์สาธารณะ
- งานด้าน CAD การผลิต ราคา และคำรับรองต้องใส่ `accuracy_notes` หรือ `risks` ตามความเหมาะสม
- เนื้อหาที่ใช้หน้าหรือเสียงผู้ก่อตั้งต้องระบุเหตุผลการอนุมัติ

## Minimum Discord response
เมื่อช่องทางแสดงผลมีพื้นที่จำกัด ให้แสดงอย่างน้อย:
1. หัวข้อ
2. Hook
3. Script / Caption
4. CTA
5. Production notes
6. Review status

## Machine-readable principle
โครงสร้างต้องอ่านได้ทั้งโดยมนุษย์และระบบอัตโนมัติ เพื่อให้สามารถบันทึกลงฐานข้อมูล ส่งต่อ Agent หรือแสดงบน Dashboard ได้โดยไม่ต้องเดาความหมายใหม่
