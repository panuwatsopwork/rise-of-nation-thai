"""
หลังทดสอบแล้ว: การ "ย้ายสระ/วรรณยุกต์ไปก่อนพยัญชนะ" แบบอัตโนมัติ
ทำให้คำหลายพยางค์เพี้ยน (เช่น เพื่อเก็บ, เศรษฐกิจ) และย้อนกลับไม่สมบูรณ์
จึงไม่ใช้กฎสลับ Mn/Mc อีกต่อไป

สคริปต์นี้ทำได้แค่: ลบช่องว่างระหว่างตัวอักษรไทยที่ติดกัน (ตามที่ต้องการเลิกใช้การแบ่งคำด้วยช่องว่าง)

ใช้: python thai_game_compensate.py [buildings_th_fragment.xml]
จากนั้นรัน apply_building_help_thai.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

def collapse_thai_spaces(text: str) -> str:
    """ลบช่องว่างระหว่างตัวอักษรไทย (ทั้งไฟล์ ไม่ใช่แค่ช่วงไทยติดกัน)."""
    while True:
        new = re.sub(r"([\u0e00-\u0e7f]) +([\u0e00-\u0e7f])", r"\1\2", text)
        if new == text:
            return text
        text = new


def process_file(path: Path) -> tuple[int, int]:
    text = path.read_text(encoding="utf-8")
    new_text = collapse_thai_spaces(text)
    path.write_text(new_text, encoding="utf-8")
    return len(text), len(new_text)


def main() -> None:
    base = Path(__file__).resolve().parent
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else base / "buildings_th_fragment.xml"
    before, after = process_file(path)
    print(path, "— chars before/after:", before, after, "(removed", before - after, "chars)")


if __name__ == "__main__":
    main()
