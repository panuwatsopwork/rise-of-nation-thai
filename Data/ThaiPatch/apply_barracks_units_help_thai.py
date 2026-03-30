"""
แทนที่คำอธิบายหน่วยใน <UNITS> ของ help.xml เฉพาะหน่วยที่สร้างจาก Barracks
แหล่งข้อความอังกฤษ: help.xml.bak_buildings (หรือ help.xml ถ้าไม่มี bak)
จากนั้นแปลด้วย barracks_units_translate เท่านั้น (ไม่รัน mark compensation —
compensate_thai_runs_wordwise ทำลายข้อความไทย Unicode ที่ถูกต้อง; เมนูอาคารใช้ fragment จูนมือแทน)

รัน: python apply_barracks_units_help_thai.py
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from barracks_units_translate import translate_english_unit_string

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
    src_en = HELP_BAK if HELP_BAK.exists() else HELP
    graphs = load_barracks_graphs()
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

    for g in sorted(graphs):
        en_inner = extract_string_inner(units_en, g)
        if en_inner is None:
            print("skip (no STRING):", g)
            continue
        en_stripped = en_inner.strip()
        if not en_stripped:
            print("skip (empty):", g)
            continue
        th = translate_english_unit_string(en_stripped)
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
