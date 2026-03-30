import re
from pathlib import Path
from collections import Counter

unitrules = Path(
    r"c:\Program Files (x86)\Steam\steamapps\common\Rise of Nations\Data\unitrules.xml"
).read_text(encoding="utf-8")
graphs = set()
for b in unitrules.split("<UNIT>"):
    if "<WHERE>Barracks</WHERE>" in b:
        m = re.search(r"<GRAPH>([^<]+)</GRAPH>", b)
        if m:
            graphs.add(m.group(1).strip())

help_path = Path(
    r"c:\Program Files (x86)\Steam\steamapps\common\Rise of Nations\Data\help.xml.bak_buildings"
)
text = help_path.read_text(encoding="utf-8")
m = re.search(r"<UNITS>(.*?)</UNITS>", text, re.DOTALL)
if not m:
    raise SystemExit("no UNITS")
units_xml = m.group(1)
entries = re.findall(r'<ENTRY name="([^"]+)">\s*(.*?)</ENTRY>', units_xml, re.DOTALL)
bodies = []
for name, body in entries:
    if name not in graphs:
        continue
    sm = re.search(r"<STRING>(.*?)</STRING>", body, re.DOTALL)
    if not sm:
        continue
    inner = sm.group(1).strip()
    if not inner:
        continue
    norm = re.sub(r"\s+", " ", inner)
    bodies.append((name, norm))
print("entries with content", len(bodies))
c = Counter(n for _, n in bodies)
print("unique strings", len(c))
for s, cnt in c.most_common(20):
    print(cnt, s[:120])
