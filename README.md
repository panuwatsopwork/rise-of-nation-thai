# Rise of Nations — Thai localization (patch)

เวอร์ชันที่เก็บไว้: **แพตช์ข้อความไทยสำหรับ Rise of Nations** รวมหลักการชดเชยการแสดงผลไทยในเกม (pre-compensation ผ่าน `compensate_thai_runs_wordwise`) สำหรับเมนูสิ่งก่อสร้างและหน่วยจาก Barracks

## โครงสร้าง

- `Data/help.xml` — ไฟล์ช่วยเหลือหลักของเกม (บล็อก `<BUILDINGS>` และ `<UNITS>` ที่แพตช์แล้ว)
- `Data/ThaiPatch/` — สคริปต์และ fragment สำหรับสร้าง/อัปเดตข้อความ
- `Data/fonts.xml` — ชี้ UI เกมไปใช้ฟอนต์ **Leelawadee UI** (รองรับภาษาไทย ไม่ขึ้นเป็นช่องสี่เหลี่ยม)
- `Data/Fonts/LeelawUI.ttf`, `Data/Fonts/LeelaUIb.ttf` — ไฟล์ฟอนต์ที่ `fonts.xml` อ้างอิง (คัดลอกมาจากระบบที่ใช้งานได้)

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

หลังติดตั้งเกมบนเครื่องเป้าหมาย ให้คัดลอกจาก repo ไป **ผสมเข้า** ในโฟลเดอร์ `Data` ของเกม (อย่าลบ `Data` เดิมทั้งโฟลเดอร์) อย่างน้อยดังนี้:

| จาก repo | ไปที่เกม |
|----------|-----------|
| `Data/help.xml` | `...\Rise of Nations\Data\help.xml` |
| `Data/ThaiPatch/` (ทั้งโฟลเดอร์) | `...\Data\ThaiPatch\` |
| `Data/fonts.xml` | `...\Data\fonts.xml` |
| `Data/Fonts/LeelawUI.ttf` | `...\Data\Fonts\LeelawUI.ttf` |
| `Data/Fonts/LeelaUIb.ttf` | `...\Data\Fonts\LeelaUIb.ttf` |

ถ้าไม่คัดลอก `fonts.xml` และฟอนต์สองไฟล์นี้ ข้อความไทยในเกมอาจขึ้นเป็นช่องสี่เหลี่ยม (□) เพราะฟอนต์เดิมของเกมไม่มี glyph ไทย

## ใบอนุญาต

เนื้อหาเกมเป็นของผู้ถือลิขสิทธิ์ Rise of Nations / เจ้าของที่เกี่ยวข้อง โฟลเดอร์นี้เก็บเฉพาะไฟล์แปลและสคริปต์ที่ผู้ใช้สร้างสำหรับภาษาไทย

ฟอนต์ Leelawadee UI เป็นทรัพย์สินของ Microsoft การแจกจ่ายผ่าน repo นี้เพื่อให้ mod แสดงผลได้ครบ — หากต้องการใช้เงื่อนไขอื่น ให้ใช้ฟอนต์จากระบบปฏิบัติการของคุณแทน
