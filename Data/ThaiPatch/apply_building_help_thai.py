"""
แทนที่เฉพาะบล็อก <BUILDINGS>...</BUILDINGS> ใน Data/help.xml ด้วย buildings_th_fragment.xml
รัน: python apply_building_help_thai.py

สำรองไฟล์เดิมเป็น help.xml.bak_buildings (ครั้งเดียว ถ้ายังไม่มี)
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

DIR = Path(__file__).resolve().parent
DATA = DIR.parent
HELP = DATA / "help.xml"
FRAG = DIR / "buildings_th_fragment.xml"
BAK = DATA / "help.xml.bak_buildings"


def main() -> None:
    th = FRAG.read_text(encoding="utf-8")
    if not th.strip().startswith("<BUILDINGS"):
        raise SystemExit("buildings_th_fragment.xml must start with <BUILDINGS>")

    src = HELP.read_text(encoding="utf-8")
    if not BAK.exists():
        shutil.copy2(HELP, BAK)
        print("Backup:", BAK)

    new_src, n = re.subn(
        r"<BUILDINGS>.*?</BUILDINGS>",
        th.strip(),
        src,
        count=1,
        flags=re.DOTALL,
    )
    if n != 1:
        raise SystemExit(f"Expected 1 BUILDINGS block, replaced {n}")
    HELP.write_text(new_src, encoding="utf-8")
    print("Updated:", HELP)


if __name__ == "__main__":
    main()
