# PTR-AI Repository Structure

**Version:** 0.1

## Target Structure

```text
PTR-AI/
├── README.md
├── docs/
│   ├── foundation/
│   ├── architecture/
│   ├── governance/
│   ├── roadmaps/
│   └── handbooks/
├── standards/
│   ├── content/
│   ├── design/
│   ├── rhino/
│   ├── media/
│   ├── digital-assets/
│   ├── persona/
│   ├── quality/
│   └── security/
├── knowledge/
│   ├── jewelry/
│   ├── cad/
│   ├── rhino/
│   ├── matrixgold/
│   ├── gemstones/
│   ├── manufacturing/
│   ├── ai/
│   ├── business/
│   └── marketing/
├── agents/
│   ├── ceo/
│   ├── content/
│   ├── design/
│   ├── rhino/
│   ├── business/
│   ├── sales/
│   ├── support/
│   ├── research/
│   ├── veo/
│   └── automation/
├── workflows/
│   ├── n8n/
│   ├── discord/
│   └── approvals/
├── plugins/
│   ├── rhino/
│   └── shared/
├── applications/
│   ├── dashboard/
│   ├── academy/
│   ├── marketplace/
│   └── customer-portal/
├── media/
│   ├── schemas/
│   ├── naming/
│   └── templates/
├── community/
│   ├── discord/
│   ├── community-edition/
│   └── open-knowledge/
├── tests/
└── experiments/
```

## Rules

- ห้ามย้ายโค้ดเดิมครั้งใหญ่โดยไม่มี Migration Plan
- เพิ่มโครงสร้างใหม่ทีละส่วนตามการใช้งานจริง
- เอกสารและมาตรฐานต้องมี Version และ Status
- งานทดลองอยู่ใน `experiments/` และห้ามเชื่อม Production โดยอัตโนมัติ
- ไฟล์ลูกค้าและไฟล์สื่อขนาดใหญ่ไม่เก็บตรงใน Git เว้นแต่เป็นตัวอย่างที่ได้รับอนุญาต
- Secret, Token, Password และข้อมูลส่วนตัวห้าม Commit

## Naming

- เอกสารมาตรฐาน: `PTR-<DOMAIN>-STD-v<MAJOR>.<MINOR>.md`
- Knowledge ID: `KNW-<DOMAIN>-NNNN`
- Workflow: `WF-<DOMAIN>-NNN`
- Agent: `AGT-<ROLE>-v<MAJOR>.<MINOR>`
- Decision Record: `ADR-NNNN-<short-title>.md`

## Migration Approach

1. สำรวจโครงสร้างปัจจุบัน
2. สร้าง Mapping ระหว่างไฟล์เดิมและโครงสร้างใหม่
3. ย้ายทีละโมดูลใน Branch แยก
4. รัน Test และตรวจ Workflow
5. เปิด Pull Request
6. Founder Review ก่อน Merge
