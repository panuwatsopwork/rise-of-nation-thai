"""Extract <BUILDINGS>...</BUILDINGS> from help.xml for offline editing."""
import re
import shutil

src = r"c:\Program Files (x86)\Steam\steamapps\common\Rise of Nations\Data\help.xml"
out = r"c:\Program Files (x86)\Steam\steamapps\common\Rise of Nations\Data\ThaiPatch\buildings_en_fragment.xml"

with open(src, encoding="utf-8") as f:
    s = f.read()
m = re.search(r"(<BUILDINGS>.*?</BUILDINGS>)", s, re.DOTALL)
if not m:
    raise SystemExit("BUILDINGS not found")
with open(out, "w", encoding="utf-8") as f:
    f.write(m.group(1))
print("Wrote", out, "chars", len(m.group(1)))
