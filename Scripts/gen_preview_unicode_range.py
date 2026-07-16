#!/usr/bin/env python3
"""Cap nhat unicode-range trong preview.html cho khop cmap that cua font vua build.

Doc cmap thuc te tu Sans/fonts/variable/DoMoSans[opsz,wght].ttf (va ban -Italic),
sinh chuoi unicode-range CSS, roi thay the dung phan giua marker
/* AUTOGEN:ROMAN:START */.../* AUTOGEN:ROMAN:END */ (va ITALIC tuong ung) trong preview.html.

Dung: python3 Scripts/gen_preview_unicode_range.py
Duoc goi tu dong o cuoi Scripts/build_sans.sh sau moi lan build.
"""

import re
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
PREVIEW_HTML = ROOT / "preview.html"

FONTS = {
    "ROMAN": ROOT / "Sans/fonts/variable/DoMoSans[opsz,wght].ttf",
    "ITALIC": ROOT / "Sans/fonts/variable/DoMoSans-Italic[opsz,wght].ttf",
}


def ranges_to_css(codepoints):
    cps = sorted(codepoints)
    ranges = []
    start = prev = cps[0]
    for cp in cps[1:]:
        if cp == prev + 1:
            prev = cp
            continue
        ranges.append((start, prev))
        start = prev = cp
    ranges.append((start, prev))

    parts = []
    for a, b in ranges:
        parts.append(f"U+{a:X}" if a == b else f"U+{a:X}-{b:X}")
    return ", ".join(parts)


def main():
    html = PREVIEW_HTML.read_text(encoding="utf-8")

    for label, font_path in FONTS.items():
        font = TTFont(str(font_path))
        cmap = font.getBestCmap()
        css_range = ranges_to_css(cmap.keys())

        pattern = re.compile(
            rf"(/\* AUTOGEN:{label}:START \*/).*?(/\* AUTOGEN:{label}:END \*/)",
            re.DOTALL,
        )
        if not pattern.search(html):
            raise SystemExit(f"Khong tim thay marker AUTOGEN:{label} trong preview.html")
        html = pattern.sub(lambda m: f"{m.group(1)}{css_range}{m.group(2)}", html)
        print(f"{label}: {len(cmap)} codepoint -> da cap nhat unicode-range")

    PREVIEW_HTML.write_text(html, encoding="utf-8")
    print(f"Da ghi lai {PREVIEW_HTML}")


if __name__ == "__main__":
    main()
