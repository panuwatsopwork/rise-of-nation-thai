"""
Pipeline เดียวกับเมนู <BUILDINGS>: แปลอังกฤษ→ไทย (Google) + รักษาแท็กเกม +
compensate_thai_runs_wordwise + strip_topmost_above_if_double_in_text

ใช้ร่วมกับ regenerate_buildings_th_fragment.py และ apply_barracks_units_help_thai.py
"""
from __future__ import annotations

import re
import time

from deep_translator import GoogleTranslator
from thai_engine_mark_shift import (
    compensate_thai_runs_wordwise,
    strip_topmost_above_if_double_in_text,
)

# อังกฤษ → ไทยที่ชดเชยแล้ว (ใช้ตามนี้ ไม่รัน compensate ซ้ำ) — เมนูอาคาร
OVERRIDE_FINAL: dict[str, str] = {
    "Extends your {National Borders}.": "ขยาย {National Borders} ของุคณ",
    "Allows you to construct economic buildings in the area.": "ส้รางอาคารเศรษฐิกจในเขตนี้ไ้ด",
    "Creates {Citizens} to build and gather.": "ใ้ช {Citizens} ่กอส้รางและรวบรวมทัรพยากร",
    "Provides an income of +$NUMBER1 #ICON2 and +$NUMBER0 #ICON1.": "ีมรายไ้ด +$NUMBER1 #ICON2 และ +$NUMBER0 #ICON1",
    "Creates {Caravans} who collect #ICON3 {Wealth}.": "ส้ราง {Caravans} เื่พอเ็กบ #ICON3 {Wealth}",
    "Creates {Merchants} who can control {rare resources}.": "ส้ราง {Merchants} เื่พอควบุคม {rare resources}",
    "Provides an income of +$NUMBER0 #ICON3 Wealth.": "ีมรายไ้ด +$NUMBER0 #ICON3 Wealth",
    "Creates {Scholars} who gather #ICON4 {Knowledge}.": "ส้ราง {Scholars} เื่พอเ็กบ #ICON4 {Knowledge}",
}

# อังกฤษ → ไทยมาตรฐาน (จะรัน compensate อีกทีให้ตรงเอนจิน)
OVERRIDE_UNICODE: dict[str, str] = {
    "Conducts research including Age advances.": "ดำเนินการวิจัยรวมถึงการก้าวหน้ายุค",
    "Expands the City's influence on {National Borders} by +$NUMBER0.": "ขยายอิทธิพลของเมืองต่อ {National Borders} +$NUMBER0",
    "Increases the City's Hit Points by +$NUMBER1%.": "เพิ่มพลังชีวิตของเมือง +$NUMBER1%",
    "Increases the City's Attack Range by +$NUMBER2.": "เพิ่มระยะการโจมตีของเมือง +$NUMBER2",
}

PROT_RE = re.compile(
    r"\{[^}]+\}|#ICON\d+|\$NUMBER\d+|\$STRING\d+",
    re.DOTALL,
)

SPLIT_RE = re.compile(r"(<(?:BULLET|LINE)/>|<!--.*?-->)", re.DOTALL)

_tr = GoogleTranslator(source="en", target="th")
_translate_cache: dict[str, str] = {}


def clear_translate_cache() -> None:
    _translate_cache.clear()


def normalize_key(s: str) -> str:
    return " ".join(s.split()).strip()


def protect_tokens(s: str) -> tuple[str, list[str]]:
    tokens: list[str] = []

    def repl(m: re.Match[str]) -> str:
        tokens.append(m.group(0))
        return f"\ue000{len(tokens) - 1}\ue001"

    return PROT_RE.sub(repl, s), tokens


def apply_game_compensate(th: str) -> str:
    if not th or not re.search(r"[\u0e00-\u0e7f]", th):
        return th
    th = compensate_thai_runs_wordwise(th)
    return strip_topmost_above_if_double_in_text(th)


def restore_tokens(s: str, tokens: list[str]) -> str:
    out = s
    for i, tok in enumerate(tokens):
        marker = f"\ue000{i}\ue001"
        if marker in out:
            out = out.replace(marker, tok, 1)
        else:
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
        return strip_topmost_above_if_double_in_text(OVERRIDE_FINAL[nk])
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
    m = re.match(r"^(\s*)([\s\S]*?)(\s*)$", chunk)
    if not m:
        return translate_en_to_th(chunk)
    lead, core, trail = m.group(1), m.group(2), m.group(3)
    if not core.strip():
        return chunk
    return lead + translate_en_to_th(core) + trail
