"""Export English help STRING inner text for Barracks units (one per line, base64 optional)."""
import re
from pathlib import Path

unitrules = Path(__file__).resolve().parent.parent / "unitrules.xml"
help_path = Path(__file__).resolve().parent.parent / "help.xml.bak_buildings"

graphs = set()
for b in unitrules.read_text(encoding="utf-8").split("<UNIT>"):
    if "<WHERE>Barracks</WHERE>" in b:
        m = re.search(r"<GRAPH>([^<]+)</GRAPH>", b)
        if m:
            graphs.add(m.group(1).strip())

text = help_path.read_text(encoding="utf-8")
m = re.search(r"<UNITS>(.*?)</UNITS>", text, re.DOTALL)
units_xml = m.group(1)
entries = re.findall(r'<ENTRY name="([^"]+)">\s*(.*?)</ENTRY>', units_xml, re.DOTALL)
out_lines = []
for name, body in sorted(entries, key=lambda x: x[0]):
    if name not in graphs:
        continue
    sm = re.search(r"<STRING>(.*?)</STRING>", body, re.DOTALL)
    if not sm:
        out_lines.append(f"{name}\t<EMPTY>")
        continue
    inner = sm.group(1).strip()
    if not inner:
        out_lines.append(f"{name}\t<EMPTY>")
        continue
    one = re.sub(r"\s+", " ", inner)
    out_lines.append(f"{name}\t{one}")

out_path = Path(__file__).resolve().parent / "barracks_units_en_export.txt"
out_path.write_text("\n".join(out_lines), encoding="utf-8")
print("Wrote", len(out_lines), "lines to", out_path)
