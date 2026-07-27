# PTR-AI Digital Asset Plan

**Version:** 0.1

## 1. Objective

จัดการรูป วิดีโอ เสียง CAD Render และไฟล์งานจำนวนมากให้ค้นหา ใช้ซ้ำ สำรอง และนำไปสร้างคอนเทนต์ได้ โดยรักษาไฟล์ต้นฉบับและสิทธิ์ของเจ้าของข้อมูล

## 2. Asset Types

- Video: Driving, Travel, Nature, Factory, Jewelry, CAD Screen, Teaching, B-roll
- Photo: Product, Workshop, Travel, Reference, Founder Persona
- Audio: Voice, Music, SFX, Interview
- CAD: 3DM, STEP, STL, OBJ, DWG, Vector
- Render: Still, Turntable, Animation, Technical View
- Brand: Logo, Font Reference, Color, Template
- Documents: Brief, Standard, Checklist, Script, Consent

## 3. Storage Zones

```text
01_INBOX          ไฟล์ใหม่ที่ยังไม่ตรวจ
02_ORIGINALS      ต้นฉบับ อ่านอย่างเดียว
03_WORKING        ไฟล์กำลังตัดต่อหรือแก้ไข
04_APPROVED       ผ่านการตรวจแล้ว
05_PUBLISHED      ผลงานที่เผยแพร่แล้ว
06_ARCHIVE        งานเก่าและสำรองระยะยาว
99_QUARANTINE     ไฟล์เสีย ไม่ทราบที่มา หรือเสี่ยง
```

## 4. Naming Standard

รูปแบบพื้นฐาน:

```text
YYYYMMDD_COUNTRY-LOCATION_CATEGORY_SUBJECT_SEQUENCE_STATUS.ext
```

ตัวอย่าง:

```text
20260720_TH-Yasothon_DRIVING_SunsetRoad_001_ORIGINAL.mp4
20260720_TH-Yasothon_JEWELRY_RingSetting_002_APPROVED.jpg
20260720_NA_CAD_EmeraldRing_003_WORKING.3dm
```

กรณีจำสถานที่ไม่ได้ ให้ใช้:

- `UNKNOWN-LOCATION`
- `APPROX-Yasothon`
- `ROUTE-UNKNOWN`

ห้ามเดาชื่อสถานที่ให้ดูน่าเชื่อถือเกินข้อมูลที่มี

## 5. Minimum Metadata

- Asset ID
- Original filename
- Capture date (exact or estimated)
- Location (exact, approximate, or unknown)
- Category
- Description
- People present
- Consent status
- Copyright/owner
- Camera/device when known
- Tags
- Quality rating
- Usage restrictions
- Backup status

## 6. Founder Face and Voice Policy

- ใช้ใบหน้าและเสียงคุณเทียมได้เฉพาะงานที่ได้รับอนุมัติ
- เก็บรูปอ้างอิงต้นฉบับในพื้นที่จำกัดสิทธิ์
- ห้ามสร้างเนื้อหาที่ทำให้คุณเทียมพูดหรือรับรองเรื่องสำคัญโดยไม่ได้อนุมัติ
- งานที่ใช้ใบหน้าสังเคราะห์หรือเสียงสังเคราะห์ต้องระบุสถานะใน Metadata
- ห้ามใช้ภาพบุคคลอื่นหรือลูกค้าโดยไม่มีสิทธิ์และความยินยอม

## 7. AI Analysis Workflow

1. Import แบบไม่แก้ Original
2. ตรวจไฟล์เสียและ Duplicate
3. Extract technical metadata
4. สร้าง Proxy ความละเอียดต่ำสำหรับค้นหา
5. วิเคราะห์ฉาก วัตถุ เสียง และช่วงเวลาที่น่าสนใจ
6. สร้าง Tag และ Summary
7. ให้มนุษย์ตรวจ Tag สำคัญ เช่น บุคคล สถานที่ และสิทธิ์
8. อนุมัติก่อนนำไปสร้างหรือเผยแพร่คอนเทนต์

## 8. Content Reuse Workflow

```text
Search request
→ Candidate assets
→ Rights and consent check
→ Storyboard
→ Script
→ Edit list
→ Founder review
→ Render/export
→ Publish approval
→ Record usage history
```

## 9. Backup Rule

ใช้หลัก 3-2-1 เมื่อสามารถทำได้:

- มีข้อมูลอย่างน้อย 3 ชุด
- เก็บบนสื่ออย่างน้อย 2 ประเภท
- มีอย่างน้อย 1 ชุดอยู่นอกเครื่องหลัก

ไฟล์หลาย TB ต้องเริ่มจาก Inventory ก่อนย้ายหรือเปลี่ยนชื่อครั้งใหญ่

## 10. First Practical Pilot

เลือกเพียง 1 โฟลเดอร์ขนาดเล็กประมาณ 20–50 คลิป เพื่อทดลอง:

- ตั้งชื่อ
- Metadata
- Tag
- Search
- สร้างคลิปสั้น 1 ชิ้น

เมื่อทดลองสำเร็จแล้วจึงขยายไปยังคลังทั้งหมด เพื่อลดความเสี่ยงและไม่เสียเวลาจัดระบบผิดวิธี
