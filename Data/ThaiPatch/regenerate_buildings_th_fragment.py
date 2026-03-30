"""
สร้าง buildings_th_fragment.xml ใหม่จาก buildings_en_fragment.xml:
  1) แปลข้อความอังกฤษ → ไทยที่ถูกต้อง (รักษา {tag}, #ICON, $NUMBER, $STRING)
  2) รัน compensate_thai_runs_wordwise ทุกช่วง (หลักเดียวกับ City/Market) เพื่อให้เอนจินเกมแสดงสระ/วรรณยุกต์ตรงจุด
  3) ข้อความที่จูนมือแล้วใน OVERRIDE_FINAL ใช้ตามนั้นโดยไม่รันซ้ำ (กันชดเชยสองชั้น)

รัน: python regenerate_buildings_th_fragment.py
"""
from __future__ import annotations

import re
import shutil
import time
from pathlib import Path

from deep_translator import GoogleTranslator
from thai_engine_mark_shift import compensate_thai_runs_wordwise

DIR = Path(__file__).resolve().parent
EN_FRAG = DIR / "buildings_en_fragment.xml"
OUT_FRAG = DIR / "buildings_th_fragment.xml"
BAK_FRAG = DIR / "buildings_th_fragment.xml.bak_regen"

# อังกฤษ → ไทยที่ชดเชยแล้ว (ใช้ตามนี้ ไม่รัน compensate ซ้ำ)
OVERRIDE_FINAL: dict[str, str] = {
    # บรรทัดเมือง (FOUR_BULLET)
    "Extends your {National Borders}.": "ขยาย {National Borders} ของุคณ",
    "Allows you to construct economic buildings in the area.": "ส้รางอาคารเศรษฐิกจในเขตนี้ไ้ด",
    "Creates {Citizens} to build and gather.": "ใ้ช {Citizens} ่กอส้รางและรวบรวมทัรพยากร",
    "Provides an income of +$NUMBER1 #ICON2 and +$NUMBER0 #ICON1.": "ีมรายไ้ด +$NUMBER1 #ICON2 และ +$NUMBER0 #ICON1",
    # ตลาด
    "Creates {Caravans} who collect #ICON3 {Wealth}.": "ส้ราง {Caravans} เื่พอเ็กบ #ICON3 {Wealth}",
    "Creates {Merchants} who can control {rare resources}.": "ส้ราง {Merchants} เื่พอควบุคม {rare resources}",
    "Provides an income of +$NUMBER0 #ICON3 Wealth.": "ีมรายไ้ด +$NUMBER0 #ICON3 Wealth",
    # มหาวิทยาลัย บรรทัดแรก
    "Creates {Scholars} who gather #ICON4 {Knowledge}.": "ส้ราง {Scholars} เื่พอเ็กบ #ICON4 {Knowledge}",
}

# อังกฤษ → ไทยมาตรฐาน (จะรัน compensate อีกทีให้ตรงเอนจิน)
OVERRIDE_UNICODE: dict[str, str] = {
    "Conducts research including Age advances.": "ดำเนินการวิจัยรวมถึงการก้าวหน้ายุค",
    "Expands the City's influence on {National Borders} by +$NUMBER0.": "ขยายอิทธิพลของเมืองต่อ {National Borders} +$NUMBER0",
    "Increases the City's Hit Points by +$NUMBER1%.": "เพิ่มพลังชีวิตของเมือง +$NUMBER1%",
    "Increases the City's Attack Range by +$NUMBER2.": "เพิ่มระยะการโจมตีของเมือง +$NUMBER2",
}

# แท็กตัวยึดเกม — ไม่ส่งแปล
PROT_RE = re.compile(
    r"\{[^}]+\}|#ICON\d+|\$NUMBER\d+|\$STRING\d+",
    re.DOTALL,
)

SPLIT_RE = re.compile(r"(<(?:BULLET|LINE)/>|<!--.*?-->)", re.DOTALL)

_tr = GoogleTranslator(source="en", target="th")
_translate_cache: dict[str, str] = {}


def normalize_key(s: str) -> str:
    return " ".join(s.split()).strip()


def protect_tokens(s: str) -> tuple[str, list[str]]:
    """ใช้ตัวอักษร Private Use เพื่อไม่ให้บริการแปลไปแตะต้อง"""
    tokens: list[str] = []

    def repl(m: re.Match[str]) -> str:
        tokens.append(m.group(0))
        return f"\ue000{len(tokens) - 1}\ue001"

    return PROT_RE.sub(repl, s), tokens


def apply_game_compensate(th: str) -> str:
    """หลักเดียวกับ City/Market: ชดเชยบั๊กเรนเดอร์ไทยของเกม"""
    if not th or not re.search(r"[\u0e00-\u0e7f]", th):
        return th
    return compensate_thai_runs_wordwise(th)


def restore_tokens(s: str, tokens: list[str]) -> str:
    out = s
    for i, tok in enumerate(tokens):
        marker = f"\ue000{i}\ue001"
        if marker in out:
            out = out.replace(marker, tok, 1)
        else:
            # บริการแปลอาจลบ PUA — ลองแทนที่แบบเก่า
            legacy = f" __K{i}__ "
            if legacy in out:
                out = out.replace(legacy, tok, 1)
    return out


def translate_en_to_th(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    nk = normalize_key(text)
    if nk in OVERRIDE_FINAL:
        return OVERRIDE_FINAL[nk]
    if nk in _translate_cache:
        return _translate_cache[nk]
    if nk in OVERRIDE_UNICODE:
        th = OVERRIDE_UNICODE[nk]
        out = apply_game_compensate(th)
        _translate_cache[nk] = out
        return out
    prot, tokens = protect_tokens(text)
    time.sleep(0.12)
    for attempt in range(3):
        try:
            th = _tr.translate(prot)
            break
        except Exception:
            time.sleep(0.8 * (attempt + 1))
            th = prot
    else:
        th = prot
    th = restore_tokens(th, tokens)
    out = apply_game_compensate(th)
    _translate_cache[nk] = out
    return out


def process_string_inner(inner_en: str) -> str:
    parts = SPLIT_RE.split(inner_en)
    out: list[str] = []
    for part in parts:
        if not part:
            continue
        if SPLIT_RE.fullmatch(part):
            out.append(part)
        else:
            out.append(translate_chunk_preserving_edges(part))
    return "".join(out)


def translate_chunk_preserving_edges(chunk: str) -> str:
    """แปลเฉพาะส่วนที่มีตัวอักษร; คงช่องว่าง/ขึ้นบรรทัดรอบไว้"""
    m = re.match(r"^(\s*)([\s\S]*?)(\s*)$", chunk)
    if not m:
        return translate_en_to_th(chunk)
    lead, core, trail = m.group(1), m.group(2), m.group(3)
    if not core.strip():
        return chunk
    return lead + translate_en_to_th(core) + trail


def main() -> None:
    _translate_cache.clear()
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
