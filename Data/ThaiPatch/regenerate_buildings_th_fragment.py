"""
สร้าง buildings_th_fragment.xml ใหม่จาก buildings_en_fragment.xml:
  1) แปลข้อความอังกฤษ → ไทย (Google + รักษาแท็กเกม)
  2) รัน compensate + strip — เหมือน thai_google_help_pipeline (หลักเดียวกับ City/Market)

รัน: python regenerate_buildings_th_fragment.py
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from thai_google_help_pipeline import clear_translate_cache, process_string_inner

DIR = Path(__file__).resolve().parent
EN_FRAG = DIR / "buildings_en_fragment.xml"
OUT_FRAG = DIR / "buildings_th_fragment.xml"
BAK_FRAG = DIR / "buildings_th_fragment.xml.bak_regen"


def main() -> None:
    clear_translate_cache()
    src = EN_FRAG.read_text(encoding="utf-8")
    m = re.search(r"(<BUILDINGS>)([\s\S]*)(</BUILDINGS>)", src)
    if not m:
        raise SystemExit("No <BUILDINGS> in buildings_en_fragment.xml")

    block = m.group(2)

    entry_re = re.compile(
        r'(<ENTRY name="([^"]+)">\s*<STRING>)([\s\S]*?)(</STRING>\s*</ENTRY>)',
        re.DOTALL,
    )

    def repl_entry(m2: re.Match[str]) -> str:
        new_inner = process_string_inner(m2.group(3))
        return m2.group(1) + new_inner + m2.group(4)

    new_block, n = entry_re.subn(repl_entry, block)
    if n == 0:
        raise SystemExit("No ENTRY/STRING matched")

    out_xml = m.group(1) + new_block + m.group(3)

    if OUT_FRAG.exists() and not BAK_FRAG.exists():
        shutil.copy2(OUT_FRAG, BAK_FRAG)
        print("Backup:", BAK_FRAG)

    OUT_FRAG.write_text(out_xml, encoding="utf-8")
    print("Wrote", OUT_FRAG, "entries:", n)


if __name__ == "__main__":
    main()
