# Rise of Nations — Thai localization (patch)

เวอร์ชันที่เก็บไว้: **แพตช์ข้อความไทยสำหรับ Rise of Nations** รวมหลักการชดเชยการแสดงผลไทยในเกม (pre-compensation ผ่าน `compensate_thai_runs_wordwise`) สำหรับเมนูสิ่งก่อสร้างและหน่วยจาก Barracks

## โครงสร้าง

- `Data/help.xml` — ไฟล์ช่วยเหลือหลักของเกม (บล็อก `<BUILDINGS>` และ `<UNITS>` ที่แพตช์แล้ว)
- `Data/ThaiPatch/` — สคริปต์และ fragment สำหรับสร้าง/อัปเดตข้อความ

## สคริปต์หลัก

| สคริปต์ | คำอธิบาย |
|--------|----------|
| `apply_building_help_thai.py` | แทนที่ `<BUILDINGS>` ใน `help.xml` จาก `buildings_th_fragment.xml` |
| `regenerate_buildings_th_fragment.py` | สร้าง `buildings_th_fragment.xml` จาก `buildings_en_fragment.xml` + แปล + ชดเชยเกม |
| `apply_barracks_units_help_thai.py` | แพตช์คำอธิบายหน่วย Barracks ใน `<UNITS>` |
| `thai_engine_mark_shift.py` | เครื่องมือสลับสระ/วรรณยุกต์สำหรับบั๊กเรนเดอร์ไทยในเกม |

## ความต้องการ

- Python 3 พร้อมแพ็กเกจ: `pythainlp`, `deep-translator` (สำหรับรัน regenerate ข้อความอาคาร)

## การติดตั้งในเกม

คัดลอกเนื้อหาให้ตรงกับโครงสร้างโฟลเดอร์เกม หรือซิงก์เฉพาะ `Data/help.xml` และไฟล์ที่เกมอ้างอิง

## ใบอนุญาต

เนื้อหาเกมเป็นของผู้ถือลิขสิทธิ์ Rise of Nations / เจ้าของที่เกี่ยวข้อง โฟลเดอร์นี้เก็บเฉพาะไฟล์แปลและสคริปต์ที่ผู้ใช้สร้างสำหรับภาษาไทย
