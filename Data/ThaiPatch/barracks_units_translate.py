"""
แปลคำอธิบายหน่วยที่สร้างจาก Barracks ใน <UNITS> ของ help.xml
ใช้แทนที่วลีภาษาอังกฤษยาวๆ เป็นภาษาไทย แล้วรัน compensate_thai_runs_wordwise
"""
from __future__ import annotations

import re
from pathlib import Path

# ชื่อยุค (ลำดับสำคัญ — ยาวก่อนสั้นทีหลัง)
AGE_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("Information Age", "ยุคสารสนเทศ"),
    ("Enlightenment Age", "ยุคแห่งแสงสว่าง"),
    ("Industrial Age", "ยุคอุตสาหกรรม"),
    ("Gunpowder Age", "ยุคดินปืน"),
    ("Medieval Age", "ยุคกลาง"),
    ("Classical Age", "ยุคคลาสสิก"),
    ("Ancient Age", "ยุคโบราณ"),
    ("Modern Age", "ยุคสมัยใหม่"),
)

# ชาติ / คำนำหน้า
NATION_PREFIX: tuple[tuple[str, str], ...] = (
    ("American Unique", "เฉพาะอเมริกา"),
    ("Aztec Unique", "เฉพาะแอซเท็ก"),
    ("Bantu Unique", "เฉพาะบันตู"),
    ("British Unique", "เฉพาะอังกฤษ"),
    ("Chinese Unique", "เฉพาะจีน"),
    ("Egyptian Unique", "เฉพาะอียิปต์"),
    ("French Unique", "เฉพาะฝรั่งเศส"),
    ("German Unique", "เฉพาะเยอรมัน"),
    ("Inca Unique", "เฉพาะอินคา"),
    ("Iroquois Unique", "เฉพาะอิรอกัว"),
    ("Japanese Unique", "เฉพาะญี่ปุ่น"),
    ("Korean Unique", "เฉพาะเกาหลี"),
    ("Maya Unique", "เฉพาะมายา"),
    ("Mongol Unique", "เฉพาะมองโกล"),
    ("Nubian Unique", "เฉพาะนูเบีย"),
    ("Persian unique", "เฉพาะเปอร์เซีย"),
    ("Persian Unique", "เฉพาะเปอร์เซีย"),
    ("Portuguese Unique", "เฉพาะโปรตุเกส"),
    ("Roman Unique", "เฉพาะโรมัน"),
    ("Russian Unique", "เฉพาะรัสเซีย"),
    ("Spanish Unique", "เฉพาะสเปน"),
    ("Turkish Unique", "เฉพาะตุรกี"),
)

# วลีอธิบาย (ยาวก่อน)
PHRASES: tuple[tuple[str, str], ...] = (
    (
        "medium-ranged foot infantry with little armor; superior in almost every way to normal Crossbows.",
        "ทหารราบระยะกลาง เกราะบาง; ดีกว่าหน้าไม้ทั่วไปเกือบทุกด้าน",
    ),
    (
        "medium-ranged foot infantry with little armor; superior in almost every way to normal Archers.",
        "ทหารราบระยะกลาง เกราะบาง; ดีกว่าทหารธนูทั่วไปเกือบทุกด้าน",
    ),
    (
        "medium-ranged foot infantry with little armor; highly effective against all enemy archers.",
        "ทหารราบระยะกลาง เกราะบาง; ได้เปรียบทหารธนูศัตรูทุกประเภท",
    ),
    (
        "long-ranged foot infantry with little armor; stronger and cheaper than Arquebusiers.",
        "ทหารราบระยะไกล เกราะบาง; แข็งแกร่งและถูกกว่าทหารอาร์คิบัสทั่วไป",
    ),
    (
        "long-ranged foot infantry with little armor; stronger, tougher than all bow-armed units.",
        "ทหารราบระยะไกล เกราะบาง; แข็งแกร่งและทนทานกว่าหน่วยธนูทุกแบบ",
    ),
    (
        "medium-ranged foot infantry with little armor; stronger, tougher than normal Crossbowmen.",
        "ทหารราบระยะกลาง เกราะบาง; แข็งแกร่งและทนทานกว่าหน้าไม้ทั่วไป",
    ),
    (
        "medium-ranged foot infantry with little armor; stronger, tougher than normal Archers.",
        "ทหารราบระยะกลาง เกราะบาง; แข็งแกร่งและทนทานกว่าทหารธนูทั่วไป",
    ),
    (
        "medium-ranged foot infantry with little armor; stronger, tougher than normal Bowmen.",
        "ทหารราบระยะกลาง เกราะบาง; แข็งแกร่งและทนทานกว่าทหารธนูทั่วไป",
    ),
    (
        "medium-ranged foot infantry with little armor.",
        "ทหารราบระยะกลาง เกราะบาง",
    ),
    (
        "fast, cheap melee troops effective against enemy mounted troops.",
        "ทหารประชิดราคาถูก เคลื่อนที่เร็ว ได้เปรียบทหารม้าศัตรู",
    ),
    (
        "fast, cheap, and short-ranged. Extremely effective against enemy light infantry.",
        "เคลื่อนที่เร็ว ราคาถูก และระยะยิงสั้น; ได้เปรียบทหารราบเบาศัตรูอย่างมาก",
    ),
    (
        "fast, cheap, and short-ranged. Quicker and tougher than Elite Javelineers.",
        "เคลื่อนที่เร็ว ราคาถูก และระยะยิงสั้น; ว่องไวและทนทานกว่าทหารขวานทองระดับสูง",
    ),
    (
        "fast, cheap, and short-ranged. Quicker and tougher than Javelineers.",
        "เคลื่อนที่เร็ว ราคาถูก และระยะยิงสั้น; ว่องไวและทนทานกว่าทหารขวานทอง",
    ),
    (
        "fast, cheap, and short-ranged. Quicker and tougher than Slingers.",
        "เคลื่อนที่เร็ว ราคาถูก และระยะยิงสั้น; ว่องไวและทนทานกว่าทหารหน้าไม้",
    ),
    (
        "fast, cheap, and short-ranged. Slightly stronger than Elite Javelineers; faster to create.",
        "เคลื่อนที่เร็ว ราคาถูก และระยะยิงสั้น; แรงกว่าทหารขวานทองระดับสูงเล็กน้อย; สร้างเร็วขึ้น",
    ),
    (
        "fast, cheap, and short-ranged. Slightly stronger than Javelineers; faster to create.",
        "เคลื่อนที่เร็ว ราคาถูก และระยะยิงสั้น; แรงกว่าทหารขวานทองเล็กน้อย; สร้างเร็วขึ้น",
    ),
    (
        "fast, cheap, and short-ranged. Slightly stronger than Slingers; faster to create.",
        "เคลื่อนที่เร็ว ราคาถูก และระยะยิงสั้น; แรงกว่าทหารหน้าไม้เล็กน้อย; สร้างเร็วขึ้น",
    ),
    ("fast, cheap, and short-ranged.", "เคลื่อนที่เร็ว ราคาถูก และระยะยิงสั้น"),
    ("fast, cheap, and short-ranged", "เคลื่อนที่เร็ว ราคาถูก และระยะยิงสั้น"),
    ("powerful, slow, melee units. Extremely effective against enemy Heavy Infantry.", "ทหารประชิดที่แข็งแกร่งแต่เคลื่อนที่ช้า; ได้เปรียบทหารราบหนักศัตรูอย่างมาก"),
    ("powerful, slow, melee units.", "ทหารประชิดที่แข็งแกร่งแต่เคลื่อนที่ช้า"),
    ("powerful, slow melee units.", "ทหารประชิดที่แข็งแกร่งแต่เคลื่อนที่ช้า"),
    ("powerful, slow melee units; tougher and faster to build than normal Elite Pikemen.", "ทหารประชิดที่แข็งแกร่งแต่เคลื่อนที่ช้า; ทนทานและสร้างเร็วกว่าทหารหอกระดับสูงทั่วไป"),
    ("powerful, slow melee units; tougher and faster to build than normal Pikemen.", "ทหารประชิดที่แข็งแกร่งแต่เคลื่อนที่ช้า; ทนทานและสร้างเร็วกว่าทหารหอกทั่วไป"),
    ("powerful, slow melee units; tougher and faster to build than normal Phalanx.", "ทหารประชิดที่แข็งแกร่งแต่เคลื่อนที่ช้า; ทนทานและสร้างเร็วกว่าแถวทหารทั่วไป"),
    ("powerful, slow melee units; tougher and faster to build than normal Hoplites.", "ทหารประชิดที่แข็งแกร่งแต่เคลื่อนที่ช้า; ทนทานและสร้างเร็วกว่าฮอพไลต์ทั่วไป"),
    ("powerful, slow melee units; stronger and tougher than normal Elite Pikemen.", "ทหารประชิดที่แข็งแกร่งแต่เคลื่อนที่ช้า; แข็งแกร่งและทนทานกว่าทหารหอกระดับสูงทั่วไป"),
    ("powerful, slow melee units; stronger and tougher than normal Pikemen.", "ทหารประชิดที่แข็งแกร่งแต่เคลื่อนที่ช้า; แข็งแกร่งและทนทานกว่าทหารหอกทั่วไป"),
    ("powerful, slow melee units; stronger and tougher than normal Phalanx.", "ทหารประชิดที่แข็งแกร่งแต่เคลื่อนที่ช้า; แข็งแกร่งและทนทานกว่าแถวทหารทั่วไป"),
    ("powerful, slow melee units; stronger and tougher than normal Hoplites.", "ทหารประชิดที่แข็งแกร่งแต่เคลื่อนที่ช้า; แข็งแกร่งและทนทานกว่าฮอพไลต์ทั่วไป"),
    ("powerful, slow melee units; stronger and tougher than normal Fusiliers.", "ทหารประชิดที่แข็งแกร่งแต่เคลื่อนที่ช้า; แข็งแกร่งและทนทานกว่าฟิวซิลเยอร์ทั่วไป"),
    ("powerful, slow, melee units; extremely effective against mounted troops.", "ทหารประชิดที่แข็งแกร่งแต่เคลื่อนที่ช้า; ได้เปรียบทหารม้าอย่างมาก"),
    ("powerful, slow, melee units; extremely effective against mounted troops.", "ทหารประชิดที่แข็งแกร่งแต่เคลื่อนที่ช้า; ได้เปรียบทหารม้าอย่างมาก"),
    ("slow, powerful short-ranged gunpowder units; extremely effective against mounted troops.", "ทหารดินปืนระยะสั้นที่แข็งแกร่งแต่เคลื่อนที่ช้า; ได้เปรียบทหารม้าอย่างมาก"),
    (
        "slow, powerful, short-ranged gunpowder units; extremely effective against mounted troops.",
        "ทหารดินปืนระยะสั้นที่แข็งแกร่งแต่เคลื่อนที่ช้า; ได้เปรียบทหารม้าอย่างมาก",
    ),
    ("slow, powerful short-ranged gunpowder units useful for close-in defense.", "ทหารดินปืนระยะสั้นที่แข็งแกร่งแต่เคลื่อนที่ช้า; เหมาะป้องกันประชิด"),
    ("slow with a powerful armor-piercing attack at short range.", "เคลื่อนที่ช้า แต่โจมตีทะลุเกราะระยะใกล้ได้รุนแรง"),
    ("slow with an extremely powerful armor-piercing attack at short range.", "เคลื่อนที่ช้า แต่โจมตีทะลุเกราะระยะใกล้ได้รุนแรงมาก"),
    ("slow with a powerful and accurate long-range armor-piercing attack.", "เคลื่อนที่ช้า แต่โจมตีทะลุเกราะระยะไกลได้แม่นและรุนแรง"),
    ("powerful in quantity but somewhat slow-firing.", "ยิงรุนแรงเมื่อรวมกลุ่ม แต่ยิงช้าพอสมควร"),
    ("powerful in quantity but somewhat slow-firing; cheap and quick to create.", "ยิงรุนแรงเมื่อรวมกลุ่มแต่ยิงช้าพอสมควร; ราคาถูกและสร้างเร็ว"),
    ("powerful and accurate foot troops; cheap and quick to create.", "ทหารราบแม่นและแรง; ราคาถูกและสร้างเร็ว"),
    ("powerful and accurate foot troops.", "ทหารราบแม่นและแรง"),
    ("powerful and accurate foot troops; cheap and quick to create. <!--Manchu Riflemen-->", "ทหารราบแม่นและแรง; ราคาถูกและสร้างเร็ว"),
    (
        "slow, powerful short-ranged gunpowder units; stronger and tougher than normal Fusiliers.",
        "ทหารดินปืนระยะสั้นที่แข็งแกร่งแต่เคลื่อนที่ช้า; แข็งแกร่งและทนทานกว่าฟิวซิลเยอร์ทั่วไป",
    ),
    (
        "fast, powerful, rapid-firing foot troops; slightly tougher and faster than normal Infantry.",
        "ทหารราบยิงถี่ แรง และเคลื่อนที่เร็ว; ทนทานและเร็วกว่าทหารราบทั่วไปเล็กน้อย",
    ),
    (
        "fast, powerful, rapid-firing foot troops; slightly cheaper than normal Infantry.",
        "ทหารราบยิงถี่ แรง และเคลื่อนที่เร็ว; ถูกกว่าทหารราบทั่วไปเล็กน้อย",
    ),
    (
        "fast, powerful, rapid-firing foot troops; cheaper and stronger than normal Assault Infantry.",
        "ทหารราบยิงถี่ แรง และเคลื่อนที่เร็ว; ถูกและแรงกว่าทหารจู่โจมทั่วไป",
    ),
    ("rapid fire, small arms with excellent firepower; cheap and quick to create.", "ปืนเล็กยิงถี่ พลังทำลายสูง; ราคาถูกและสร้างเร็ว"),
    ("earliest gunpowder unit; effective against Heavy Infantry.", "หน่วยดินปืนเร็วที่สุด; ได้เปรียบทหารราบหนัก"),
    ("early gunpowder weapons with significant range; better range than ordinary Gunpowder Infantry.", "อาวุธดินปืนระยะไกล; ยิงไกลกว่าทหารดินปืนทั่วไป"),
    ("moves slowly; devastating against enemy foot troops.", "เคลื่อนที่ช้า; ทำลายทหารราบศัตรูได้รุนแรง"),
    ("fast, powerful, rapid-firing foot troops.", "ทหารราบยิงถี่ แรง และเคลื่อนที่เร็ว"),
    ("fast, powerful, rapid-firing, foot troops accurate even at long range.", "ทหารราบยิงถี่ แรง และแม่นแม้ระยะไกล"),
    ("faster and with a stronger attack than ordinary Modern Infantry.", "เร็วและโจมตีแรงกว่าทหารสมัยใหม่ทั่วไป"),
    ("stronger and faster than ordinary Gunpowder Infantry.", "แข็งแกร่งและว่องไวกว่าทหารดินปืนทั่วไป"),
    ("particularly effective against all forms of enemy infantry.", "ได้เปรียบทหารราบศัตรูทุกแบบ"),
    ("particularly effective against all types of vehicles.", "ได้เปรียบยานพาหนะทุกประเภท"),
    ("cheap, slow, melee units.", "ทหารประชิดราคาถูกแต่เคลื่อนที่ช้า"),
)


def translate_english_unit_string(s: str) -> str:
    """แปลข้อความอังกฤษเป็นภาษาไทย โดยเก็บแท็ก XML และ {Tag} ไว้"""
    t = s
    # "Medieval #ICON..." โดยไม่มีคำว่า Age (พบใน Foot Archers)
    t = re.sub(r"Medieval\s+#ICON", "ยุคกลาง #ICON", t)
    for eng, th in NATION_PREFIX:
        t = t.replace(eng, th)
    for eng, th in AGE_REPLACEMENTS:
        t = t.replace(eng, th)
    for eng, th in PHRASES:
        t = t.replace(eng, th)
    # วลีที่เหลือ (สั้น)
    extra = (
        ("Medieval #ICON29 and Gunpowder Age #ICON30", "ยุคกลาง #ICON29 และยุคดินปืน #ICON30"),
        ("Faster, tougher, better Line-of-Sight than normal Commandos.", "เร็วกว่า ทนทานกว่า และมองเห็นไกลกว่าคอมมานโดทั่วไป"),
        ("Faster, tougher, better Line-of-Sight than normal Explorers.", "เร็วกว่า ทนทานกว่า และมองเห็นไกลกว่านักสำรวจทั่วไป"),
        ("Faster, tougher, better Line-of-Sight than normal Scouts.", "เร็วกว่า ทนทานกว่า และมองเห็นไกลกว่าหน่วยสอดแนมทั่วไป"),
        ("Available one age earlier.", "ปลดล็อกเร็วกว่าหนึ่งยุค"),
        ("good for exploring the map and finding enemies.", "เหมาะสำรวจแผนที่และค้นหาศัตรู"),
        ("good for exploring the map and scouting enemy positions.", "เหมาะสำรวจแผนที่และดูตำแหน่งศัตรู"),
        ("Scouts are cheap and expendable;", "หน่วยสอดแนมราคาถูกและใช้แลกได้;"),
        ("Explorers are cheap and expendable;", "นักสำรวจราคาถูกและใช้แลกได้;"),
        ("Slow-moving and short-ranged; highly effective against buildings and entrenchments.", "เคลื่อนที่ช้าและระยะสั้น; ได้เปรียบอาคารและค่ายสังเคราะห์"),
        ("A building attacked by a Flamethrower immediately ejects any garrisoned units.", "อาคารที่ถูกพ่นไฟจะขับหน่วยในป้อมออกทันที"),
        ("An entrenched unit attacked by a Flamethrower is forced out of its entrenchments.", "หน่วยในค่ายสังเคราะห์ที่ถูกพ่นไฟจะถูกบังคับออกจากค่าย"),
        ("Marine Transports are faster and tougher than normal, and Marine units automatically Entrench after 5 seconds of being idle.", "เรือขนส่งนาวิกโจมตีเร็วและทนทานกว่าทั่วไป และหน่วยนาวิกจะขุดสังเคราะห์อัตโนมัติหลังหยุดนิ่ง 5 วินาที"),
        ("Use {Sniper} ability to destroy enemy units.", "ใช้ความสามารถ {Sniper} เพื่อทำลายหน่วยศัตรู"),
        ("Use {Sabotage} ability to damage enemy buildings.", "ใช้ความสามารถ {Sabotage} เพื่อทำลายอาคารศัตรู"),
        ("Use {Counterintelligence} to destroy enemy Spies and to remove Informers.", "ใช้ {Counterintelligence} เพื่อทำลายสายลับและลบผู้ให้ข่าว"),
        ("Use {Counterintelligence} ability to destroy enemy Spies and to remove Informers.", "ใช้ {Counterintelligence} เพื่อทำลายสายลับและลบผู้ให้ข่าว"),
        ("Can spot hidden enemy units, such as Spies and Commandos.", "มองเห็นหน่วยซ่อนเร้น เช่น สายลับและคอมมานโด"),
        ("When Commando units aren't moving or attacking, they normally cannot be seen by most enemy units.", "เมื่อคอมมานโดไม่เคลื่อนที่หรือโจมตี ศัตรูส่วนใหญ่มักมองไม่เห็น"),
        ("When Explorers aren't moving they can't normally be seen by most enemy units.", "เมื่อนักสำรวจไม่เคลื่อนที่ ศัตรูส่วนใหญ่มักมองไม่เห็น"),
        ("When Explorers aren't moving or attacking, they cannot normally be seen by most enemy units.", "เมื่อนักสำรวจไม่เคลื่อนที่หรือโจมตี ศัตรูส่วนใหญ่มักมองไม่เห็น"),
        ("When Okwari units aren't moving or attacking, they cannot normally be seen by most enemy units.", "เมื่อโอควารีไม่เคลื่อนที่หรือโจมตี ศัตรูส่วนใหญ่มักมองไม่เห็น"),
        ("When Akweks aren't moving or attacking, they cannot normally be seen by most enemy units.", "เมื่ออัควเคสไม่เคลื่อนที่หรือโจมตี ศัตรูส่วนใหญ่มักมองไม่เห็น"),
        ("When Elite Special Forces units aren't moving or attacking they can't normally be seen by most enemy units.", "เมื่อหน่วยซีลไม่เคลื่อนที่หรือโจมตี ศัตรูส่วนใหญ่มักมองไม่เห็น"),
        ("When Special Forces units aren't moving or attacking they can't normally be seen by most enemy units.", "เมื่อหน่วยซีลไม่เคลื่อนที่หรือโจมตี ศัตรูส่วนใหญ่มักมองไม่เห็น"),
        ("All anti-aircraft emplacements are automatically jammed within range of Elite Special Forces.", "ปืนต่อสู้เครื่องบินในระยะถูกรบกวนโดยอัตโนมัติ"),
        ("All anti-aircraft emplacements are automatically jammed within range of Special Forces.", "ปืนต่อสู้เครื่องบินในระยะถูกรบกวนโดยอัตโนมัติ"),
        ("Can also destroy enemy Spies.", "ทำลายสายลับศัตรูได้"),
        ("a specialized Scout with many special abilities.", "หน่วยสอดแนมเฉพาะทางที่มีความสามารถหลากหลาย"),
        ("fast, but unarmed.", "เร็วแต่ไม่มีอาวุธ"),
        ("fast, but unarmed; good for exploring the map and finding enemies.", "เร็วแต่ไม่มีอาวุธ; เหมาะสำรวจแผนที่และค้นหาศัตรู"),
        ("cheaper and stronger than normal Assault Infantry.", "ถูกและแรงกว่าทหารจู่โจมทั่วไป"),
        ("slightly cheaper than normal Infantry.", "ถูกกว่าทหารราบทั่วไปเล็กน้อย"),
        ("slightly tougher and faster than normal Infantry.", "ทนทานและเร็วกว่าทหารราบทั่วไปเล็กน้อย"),
        ("powerful, slow, units. Slightly weaker than normal Phalanx, but can fire at range.", "แข็งแกร่งแต่ช้า; อ่อนกว่าแถวทหารทั่วไปเล็กน้อยแต่ยิงระยะได้"),
        ("powerful, slow, units. Slightly weaker than normal Pikemen, but can fire at range.", "แข็งแกร่งแต่ช้า; อ่อนกว่าทหารหอกทั่วไปเล็กน้อยแต่ยิงระยะได้"),
        ("powerful, slow, units. Slightly weaker than normal Elite Pikemen, but can fire at range.", "แข็งแกร่งแต่ช้า; อ่อนกว่าทหารหอกระดับสูงทั่วไปเล็กน้อยแต่ยิงระยะได้"),
        ("powerful, slow units. Slightly weaker than normal Hoplites, but can fire at range.", "แข็งแกร่งแต่ช้า; อ่อนกว่าฮอพไลต์ทั่วไปเล็กน้อยแต่ยิงระยะได้"),
        ("powerful, slow, units. Faster than normal Phalanx while in friendly territory.", "แข็งแกร่งแต่ช้า; ในเขตพันธมิตรจะเร็วกว่าแถวทหารทั่วไป"),
        ("powerful, slow, units. Faster than normal Pikemen while in friendly territory.", "แข็งแกร่งแต่ช้า; ในเขตพันธมิตรจะเร็วกว่าทหารหอกทั่วไป"),
        ("powerful, slow, units. Faster than normal Elite Pikemen while in friendly territory.", "แข็งแกร่งแต่ช้า; ในเขตพันธมิตรจะเร็วกว่าทหารหอกระดับสูงทั่วไป"),
        ("powerful, slow, units. Faster than normal Hoplites while in friendly territory.", "แข็งแกร่งแต่ช้า; ในเขตพันธมิตรจะเร็วกว่าฮอพไลต์ทั่วไป"),
        ("fast, but unarmed; good for exploring the map and finding enemies.", "เร็วแต่ไม่มีอาวุธ; เหมาะสำรวจแผนที่และค้นหาศัตรู"),
        ("than normal Commandos.", "กว่าคอมมานโดทั่วไป"),
        ("than normal Explorers.", "กว่านักสำรวจทั่วไป"),
        ("than normal Scouts.", "กว่าหน่วยสอดแนมทั่วไป"),
        ("such as Spies and Commandos.", "เช่น สายลับและคอมมานโด"),
    )
    for eng, th in extra:
        t = t.replace(eng, th)
    # กรณีที่เหลือท้ายบรรทัด
    t = t.replace("fast, but unarmed;", "เร็วแต่ไม่มีอาวุธ;")
    t = t.replace("fast, but unarmed.", "เร็วแต่ไม่มีอาวุธ.")
    return t


def has_untranslated_latin_words(t: str) -> bool:
    """ตรวจว่ามีคำอังกฤษยาวๆ เหลือหรือไม่ (ไม่นับแท็กและชื่อยุคที่แปลแล้ว)"""
    # ลบ comment และ tag
    s = re.sub(r"<!--.*?-->", "", t)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\{[^}]+\}", " ", s)
    s = re.sub(r"#ICON\d+", " ", s)
    # คำอังกฤษยาว 5 ตัวอักษรขึ้นไป
    return bool(re.search(r"[A-Za-z]{5,}", s))
