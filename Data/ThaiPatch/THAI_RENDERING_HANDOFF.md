# Thai Text Rendering Fix — Rise of Nations: Extended Edition

This document describes the **pre-compensation** approach used so Thai building help text displays correctly in-game. It is intended for **handoff to another developer or AI** continuing this mod.

## Problem

The game’s text renderer does not behave like a standard Thai shaper. Combining characters (vowels, tone marks, **mai han akat**, etc.) appear **one grapheme too far to the right**—as if the “cursor” advances before the mark is drawn, so marks attach to the **next** consonant instead of the intended one.

This cannot be fixed via `fonts.xml` alone; the workaround is to **store strings in a deliberately “wrong” Unicode order** so that, after the engine’s error, the **on-screen** result matches normal Thai.

## Core idea (“shift marks left”)

For each character in a defined set `COMPENSATE` (Thai dependent vowels / tone marks / below marks—see `thai_engine_mark_shift.py`), perform a **single left pass**:

- If `chars[i]` is in `COMPENSATE`, **swap** `chars[i-1]` and `chars[i]`.

Intuition: if the engine shifts marks **right** by one position, moving the mark **left** in the source file cancels that offset.

**Example (conceptual):** the word you want to *read* as *สร้าง* may need to be stored so the tone mark sits **before** the consonant it should visually attach to (e.g. storage resembling *ส้ราง*), because the engine will draw it one step right.

> **Important:** Raw Unicode in the XML may look incorrect in a normal text editor but **correct in-game**.

## Why word tokenization (`pythainlp`)

Applying the swap to an **entire uninterrupted Thai substring** (no spaces between words) scrambles multi-syllable / multi-word lines, because swaps cross syllable boundaries.

The default pipeline therefore:

1. Finds each maximal Thai run: `[\u0e00-\u0e7f]+` (Latin, `{tags}`, `$NUMBER`, `#ICON` stay untouched).
2. Runs **`word_tokenize(..., engine="newmm")`** on that run (requires **PyThaiNLP**).
3. Applies **`shift_marks_left`** to **each token** separately.
4. Concatenates tokens back **without** inserting spaces (game text was collapsed).

## Special case: `เขตนี้`

After per-word swaps, the sequence **`เขต` + `นี้`** can become a substring that should be normalized. The script applies a **string replace** on the **whole concatenated chunk** after token joins:

- `POSTFIX_FROM` → `POSTFIX_TO` (see script: *เขตี้น* → *เขตนี้* in storage terms).

This fixes a cross-word-boundary artifact; individual token-only postfix is not enough.

## Files and pipeline

| File | Role |
|------|------|
| `Data/ThaiPatch/buildings_th_fragment.xml` | Editable fragment: only the `<BUILDINGS>...</BUILDINGS>` block (Thai building descriptions). |
| `Data/help.xml` | Game file; the `BUILDINGS` block is replaced from the fragment. |
| `Data/help.xml.bak_buildings` | One-time backup of `help.xml` created by `apply_building_help_thai.py` if missing. |
| `Data/ThaiPatch/thai_engine_mark_shift.py` | **Main compensator**: default mode = word-wise compensation for the whole fragment; `--four-bullets` = legacy template-only replacements. |
| `Data/ThaiPatch/apply_building_help_thai.py` | Copies `buildings_th_fragment.xml` into `help.xml`’s `BUILDINGS` section. |

### Typical workflow

1. Edit Thai source in `buildings_th_fragment.xml` **in normal Thai spelling** (or restore from English fragment and translate), *before* compensation if you maintain a “clean” source elsewhere.
2. Run:

   ```bash
   python thai_engine_mark_shift.py
   python apply_building_help_thai.py
   ```

3. Test in-game tooltips.

Optional: `python thai_engine_mark_shift.py --dry-run` to preview line diffs without writing.

### Legacy mode (`--four-bullets`)

Replaces only four known duplicated city/village tooltip lines via hard-coded `FOUR_BULLET_REPLACEMENTS`. Use for quick tests; **default** full-fragment mode is preferred for the whole building menu.

### Other utilities (older / optional)

- `thai_game_compensate.py` — collapses Thai spaces only (mark-swap removed).
- `space_thai_words.py` — optional word-spacing via PyThaiNLP; not required for the mark-shift fix.

### Barracks (ฐานทหาร) and hotkey strings

- **`BARRACKS` / `BARRACKSV`** entries live in `buildings_th_fragment.xml` like other buildings: write **normal Thai**, then run `thai_engine_mark_shift.py` + `apply_building_help_thai.py` so tooltips get the same word-wise mark compensation.
- **`Data/typenames.xml`** — building label on the map/UI uses hash `3868075` (set to **ฐานทหาร**).
- **`Data/playerprofile.xml`** — hotkeys such as *Build Barracks*, *Barracks: Create …*, *Find Barracks* are translated to Thai **without** running the compensator on that file. Short UI strings (e.g. **เลือก**, **อัปเกรด**, **ไม่ซูม**) often break if the same pipeline is applied blindly; if in-game marks look wrong, try manual storage forms per line or keep English for that key.

## Dependencies

- **Python 3**
- **`pythainlp`** (for default building-menu compensation):

  ```bash
  pip install pythainlp
  ```

## Fonts

The mod also pointed game fonts at Thai-capable faces (e.g. Leelawadee UI) via `Data/fonts.xml` (see project backups like `fonts.xml.bak_thai`). Font choice affects glyph shape but **does not** remove the engine’s mark-position bug; pre-compensation is still required.

## Limitations and risks

- **Tokenization errors:** rare wrong splits can produce odd storage strings; fix by adjusting tokenizer engine, a small lexicon, or manual overrides for specific `ENTRY`s.
- **New codepoints:** If you need **sara aa** (U+0E32) or other marks in `COMPENSATE`, add them deliberately and re-test—each addition can affect many strings.
- **Idempotency:** Do **not** run the compensator twice on already compensated text without undoing first (the script undoes the four bullet template replacements before full pass; keep a clean-source copy if needed).
- **Scope:** This document focuses on **`BUILDINGS`** help. Other XML/UI strings would need the same rules applied similarly if you expand the mod.

## Extending the fix

1. Adjust **`COMPENSATE`** in `thai_engine_mark_shift.py` (Unicode ranges listed in comments).
2. Add or adjust **`POSTFIX_*`** pairs if new cross-boundary glitches appear after word join.
3. Re-run `thai_engine_mark_shift.py` and `apply_building_help_thai.py`, then verify in-game.

---

*Last updated for handoff: building help pipeline with word-wise Thai mark pre-compensation for RoN:EE.*
