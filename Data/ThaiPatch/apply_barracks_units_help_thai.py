"""
แทนที่คำอธิบายหน่วยใน <UNITS> ของ help.xml สำหรับฐานทหาร (Barracks):
  - ทุก GRAPH ใน unitrules ที่ <WHERE>Barracks</WHERE>
  - รวม ENTRY ชื่อ GRAPH+V ถ้ามีใน help (หมายเหตุหน่วย/อัปเกรดบรรทัดเดียวกัน)

เทคนิคเดียวกับ <BUILDINGS>: thai_google_help_pipeline.process_string_inner
(แปล Google + compensate_thai_runs_wordwise + strip_topmost_above_if_double_in_text)

แหล่งข้อความอังกฤษ: help.xml.bak_buildings (หรือ help.xml ถ้าไม่มี bak)

รัน: python apply_barracks_units_help_thai.py
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from thai_google_help_pipeline import clear_translate_cache, process_string_inner

DIR = Path(__file__).resolve().parent
DATA = DIR.parent
HELP = DATA / "help.xml"
HELP_BAK = DATA / "help.xml.bak_buildings"


def load_barracks_graphs() -> set[str]:
    ur = (DATA / "unitrules.xml").read_text(encoding="utf-8")
    graphs: set[str] = set()
    for b in ur.split("<UNIT>"):
        if "<WHERE>Barracks</WHERE>" in b:
            m = re.search(r"<GRAPH>([^<]+)</GRAPH>", b)
            if m:
                graphs.add(m.group(1).strip())
    return graphs


def load_barracks_entry_names(units_en: str) -> set[str]:
    """GRAPH จาก Barracks + ENTRY แบบ GRAPH+V ถ้ามีใน help (เช่น SLINGERSV)"""
    names = set(load_barracks_graphs())
    for g in list(names):
        gv = g + "V"
        if extract_string_inner(units_en, gv) is not None:
            names.add(gv)
    return names


def extract_string_inner(units_xml: str, name: str) -> str | None:
    m = re.search(
        rf'<ENTRY name="{re.escape(name)}">\s*<STRING>(.*?)</STRING>',
        units_xml,
        re.DOTALL,
    )
    if not m:
        return None
    return m.group(1)


def replace_string_inner(units_xml: str, name: str, new_inner: str) -> str:
    def repl(m: re.Match[str]) -> str:
        return f'<ENTRY name="{name}">\n\t\t\t<STRING>{new_inner}</STRING>'

    pattern = rf'<ENTRY name="{re.escape(name)}">\s*<STRING>.*?</STRING>'
    new_xml, n = re.subn(pattern, repl, units_xml, count=1, flags=re.DOTALL)
    if n != 1:
        raise RuntimeError(f"replace failed for {name}, n={n}")
    return new_xml


def main() -> None:
    clear_translate_cache()
    src_en = HELP_BAK if HELP_BAK.exists() else HELP
    full = HELP.read_text(encoding="utf-8")
    m = re.search(r"(<UNITS>)(.*?)(</UNITS>)", full, re.DOTALL)
    if not m:
        raise SystemExit("No <UNITS> in help.xml")
    units_xml = m.group(2)

    en_source = src_en.read_text(encoding="utf-8")
    m2 = re.search(r"<UNITS>(.*?)</UNITS>", en_source, re.DOTALL)
    if not m2:
        raise SystemExit("No <UNITS> in English source")
    units_en = m2.group(1)

    entry_names = load_barracks_entry_names(units_en)

    for g in sorted(entry_names):
        en_inner = extract_string_inner(units_en, g)
        if en_inner is None:
            print("skip (no STRING):", g)
            continue
        if not en_inner.strip():
            print("skip (empty):", g)
            continue
        th = process_string_inner(en_inner)
        units_xml = replace_string_inner(units_xml, g, th)

    new_full = full[: m.start()] + m.group(1) + units_xml + m.group(3) + full[m.end() :]
    bak_units = DATA / "help.xml.bak_units_barracks"
    if not bak_units.exists():
        shutil.copy2(HELP, bak_units)
        print("Backup:", bak_units)
    HELP.write_text(new_full, encoding="utf-8")
    print("Updated UNITS (Barracks) in:", HELP)


if __name__ == "__main__":
    main()
