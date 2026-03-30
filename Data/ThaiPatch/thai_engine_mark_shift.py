"""
ชดเชยบั๊กเรนเดอร์ไทยของ RoN:EE — สลับเครื่องหมาย/สระ (ที่อยู่หลังพยัญชนะใน Unicode)
ไปไว้ "ก่อน" พยัญชนะหนึ่งตำแหน่ง เพื่อให้เคอร์เซอร์ที่เลื่อนไปขวาไปเกาะตัวที่ถูก

ครอบคลุมตามที่ทดสอบ: ไม้หันอากาศ, สระอิ–อื, สระอุ–อู, ไม้ไต่คู้, ไม้เอก–จัตวา, การันต์, ฯลฯ
(ไม่รวม สระอา U+0E32 ในรอบนี้ — ปรับเพิ่มใน COMPENSATE ได้ถ้าจำเป็น)

หมายเหตุ: การสลับซ้ายทั้งสตริงอาจทำให้คำหลายพยางค์เพี้ยน — มีข้อยกเว้น เขตนี้ (ดู POSTFIX_*)

โหมดเริ่มต้น: ชดเชยทุกช่วงไทยในเมนูสิ่งก่อสร้างทั้งไฟล์ (buildings_th_fragment.xml)
โหมด --four-bullets: แทนที่เฉพาะ 4 บรรทัดแม่แบบเมือง (ทดสอบเดิม)

ใช้: python thai_engine_mark_shift.py [--dry-run] [--four-bullets]
     จากนั้น python apply_building_help_thai.py
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

try:
    from pythainlp import word_tokenize
except ImportError as e:
    word_tokenize = None  # type: ignore[misc, assignment]
    _PYTHAINLP_ERR = e
else:
    _PYTHAINLP_ERR = None

# เครื่องหมาย/สระที่ตามหลังพยัญชนะ (ต้องการเลื่อนไปซ้ายหนึ่งช่องในไฟล์เกม)
COMPENSATE: frozenset[str] = frozenset(
    "\u0e31"  # ไม้หันอากาศ
    "\u0e34\u0e35\u0e36\u0e37\u0e38\u0e39\u0e3a"  # สระอิ–อื, อุ–อู, พินทุ
    "\u0e47\u0e48\u0e49\u0e4a\u0e4b\u0e4c\u0e4d\u0e4e"  # ไม้ไต่คู้, ไม้เอก–จัตวา, การันต์, ฯลฯ
)

# หลังสลับซ้าย เขต + นี้ กลายเป็น เขตี้น — คืนเป็น เขตนี้ (ยังไม่ชดเชย นี้ ในเกม)
POSTFIX_FROM = "\u0e40\u0e02\u0e15\u0e35\u0e49\u0e19"  # เขตี้น
POSTFIX_TO = "\u0e40\u0e02\u0e15\u0e19\u0e35\u0e49"  # เขตนี้


def shift_marks_left(s: str) -> str:
    chars = list(s)
    i = 1
    while i < len(chars):
        if chars[i] in COMPENSATE:
            chars[i - 1], chars[i] = chars[i], chars[i - 1]
        i += 1
    return "".join(chars)


def shift_marks_left_fixed(s: str) -> str:
    """สลับซ้าย + แก้เขตนี้เมื่อสลับทั้งช่วงไทยติดกัน (ไม่ใช้ต่อคำ)"""
    return shift_marks_left(s).replace(POSTFIX_FROM, POSTFIX_TO)


def compensate_thai_runs(text: str) -> str:
    """ชดเชยทั้งช่วงไทยติดกันครั้งเดียว (ไม่แนะนำกับข้อความยาวหลายพยางค์ติดกัน)"""

    def repl(m: re.Match[str]) -> str:
        return shift_marks_left_fixed(m.group(0))

    return re.sub(r"[\u0e00-\u0e7f]+", repl, text)


def compensate_thai_runs_wordwise(text: str) -> str:
    """
    ชดเชยทีละคำด้วย pythainlp word_tokenize — เหมาะกับข้อความไทยที่ต่อกันยาวโดยไม่มีช่องว่าง
    (ต้องติดตั้ง: pip install pythainlp)
    """

    if word_tokenize is None:
        raise RuntimeError(
            "ต้องการ pythainlp สำหรับโหมดเมนูสิ่งก่อสร้างทั้งหมด: pip install pythainlp"
        ) from _PYTHAINLP_ERR

    def repl(m: re.Match[str]) -> str:
        chunk = m.group(0)
        parts = word_tokenize(chunk, engine="newmm")
        # สลับทีละคำแล้วค่อยแก้ เขตี้น→เขตนี้ ทั้งก้อน (ข้ามขอบคำ)
        out = "".join(shift_marks_left(t) for t in parts)
        return out.replace(POSTFIX_FROM, POSTFIX_TO)

    return re.sub(r"[\u0e00-\u0e7f]+", repl, text)


# ข้อความเดิมที่ซ้ำในหลาย ENTRY (เมือง/หมู่บ้าน/มหานคร) — ชดเชยเท่าที่ทดสอบจาก tooltip City
FOUR_BULLET_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("ขยาย {National Borders} ของคุณ", "ขยาย {National Borders} ของุคณ"),
    ("สร้างอาคารเศรษฐกิจในเขตนี้ได้", "ส้รางอาคารเศรษฐิกจในเขตนี้ไ้ด"),
    ("ใช้ {Citizens} ก่อสร้างและรวบรวมทรัพยากร", "ใ้ช {Citizens} ่กอส้รางและรวบรวมทัรพยากร"),
    (
        "มีรายได้ +$NUMBER1 #ICON2 และ +$NUMBER0 #ICON1",
        "ีมรายไ้ด +$NUMBER1 #ICON2 และ +$NUMBER0 #ICON1",
    ),
)


def apply_four_bullet_lines(text: str) -> str:
    for old, new in FOUR_BULLET_REPLACEMENTS:
        text = text.replace(old, new)
    return text


def undo_four_bullet_lines(text: str) -> str:
    """ย้อนการแทนที่ 4 บรรทัดแม่แบบ (ก่อนรัน compensate ทั้งไฟล์ — กันสลับซ้ำ)"""
    for old, new in FOUR_BULLET_REPLACEMENTS:
        text = text.replace(new, old)
    return text


def apply_buildings_menu_full(text: str) -> str:
    """
    ชดเชยทุกช่วงไทยในเมนูสิ่งก่อสร้าง (แบ่งคำก่อน แล้วชดเชยทีละคำ)
    ถ้าเคยรันโหมด --four-bullets แล้ว จะย้อน 4 บรรทัดนั้นเป็นข้อความมาตรฐานก่อน
    """
    text = undo_four_bullet_lines(text)
    return compensate_thai_runs_wordwise(text)


def main() -> None:
    ap = argparse.ArgumentParser(description="ชดเชยสระ/วรรณยุกต์สำหรับเอนจิน RoN")
    ap.add_argument(
        "path",
        nargs="?",
        default=str(Path(__file__).resolve().parent / "buildings_th_fragment.xml"),
        help="ไฟล์ XML (ค่าเริ่มต้น: buildings_th_fragment.xml)",
    )
    ap.add_argument("--dry-run", action="store_true", help="แสดงตัวอย่างไม่เขียนไฟล์")
    ap.add_argument(
        "--four-bullets",
        action="store_true",
        help="แทนที่เฉพาะ 4 บรรทัดแม่แบบเมือง (ไม่รันทั้งเมนู)",
    )
    args = ap.parse_args()
    path = Path(args.path)
    text = path.read_text(encoding="utf-8")
    if args.four_bullets:
        new_text = apply_four_bullet_lines(text)
    else:
        new_text = apply_buildings_menu_full(text)
    if args.dry_run:
        if new_text == text:
            print("ไม่มีการเปลี่ยนแปลง")
            return
        # แสดงบรรทัดที่ต่าง (สูงสุด 40 บรรทัด)
        old_lines, new_lines = text.splitlines(), new_text.splitlines()
        n = 0
        for i, (a, b) in enumerate(zip(old_lines, new_lines), start=1):
            if a != b:
                print(f"--- บรรทัด {i}")
                print("-", a[:120])
                print("+", b[:120])
                n += 1
                if n >= 40:
                    print("... (ตัด)")
                    break
        return
    path.write_text(new_text, encoding="utf-8")
    print("อัปเดตแล้ว:", path)


if __name__ == "__main__":
    main()
