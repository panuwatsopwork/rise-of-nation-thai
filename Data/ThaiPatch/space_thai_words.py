"""
(ออปชัน/ทดลอง) แทรกช่องว่างระหว่างคำด้วย pythainlp — ในการใช้งานจริงไม่ได้ช่วยแก้การเพี้ยนของเอนจิน
ไม่ใช้ในลำดับงานหลัก; ถ้าต้องการลบช่องว่างระหว่างตัวอักษรไทย ใช้ thai_game_compensate.py แทน

ใช้: python space_thai_words.py [path/to/file.xml]
ค่าเริ่มต้น: buildings_th_fragment.xml ในโฟลเดอร์เดียวกัน
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    from pythainlp import word_tokenize
except ImportError:
    print("Install: pip install pythainlp")
    raise

THAI_RUN = re.compile(r"[\u0e00-\u0e7f]+")


def tokenize_thai(text: str) -> str:
    return " ".join(word_tokenize(text, engine="newmm"))


def main() -> None:
    base = Path(__file__).resolve().parent
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else base / "buildings_th_fragment.xml"
    s = path.read_text(encoding="utf-8")

    def repl(m: re.Match[str]) -> str:
        return tokenize_thai(m.group(0))

    new_s, n = THAI_RUN.subn(repl, s)
    path.write_text(new_s, encoding="utf-8")
    print(path, "replaced", n, "Thai segments")


if __name__ == "__main__":
    main()
