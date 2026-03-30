"""ย้อนกลับผลจาก thai_game_compensate.py (สลับ Mn กับตัวถัดไป = inverse ของสคริปต์เดิมที่สลับ Mn กับตัวก่อนหน้า)"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

def is_thai(ch: str) -> bool:
    return 0x0E00 <= ord(ch) <= 0x0E7F

def is_mn(ch: str) -> bool:
    return is_thai(ch) and unicodedata.category(ch) in ("Mn", "Mc")

def undo_bad(s: str) -> str:
    c = list(s)
    i = 0
    while i < len(c) - 1:
        if is_mn(c[i]) and is_thai(c[i + 1]):
            c[i], c[i + 1] = c[i + 1], c[i]
            i += 2
        else:
            i += 1
    return "".join(c)

THAI_RUN = re.compile(r"[\u0e00-\u0e7f]+")

def main() -> None:
    base = Path(__file__).resolve().parent
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else base / "buildings_th_fragment.xml"
    text = path.read_text(encoding="utf-8")
    new = THAI_RUN.sub(lambda m: undo_bad(m.group(0)), text)
    path.write_text(new, encoding="utf-8")
    print("Restored:", path)

if __name__ == "__main__":
    main()
