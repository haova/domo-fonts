#!/usr/bin/env python3
"""So sanh glyph tieng Viet giua font tham khao (Inter) va DM Sans.

Dung: python3 Scripts/diff_vietnamese_glyphs.py
"""

import unicodedata
from fontTools.ttLib import TTFont

REFERENCE = "Reference/Inter-Variable.ttf"
TARGET = "Sans/fonts/variable/DMSans[opsz,wght].ttf"

VIETNAMESE_CODEPOINTS = list(range(0x1EA0, 0x1EFA)) + [
    0x0309,  # hookabovecomb
    0x0323,  # dotbelowcomb
    0x01A0,  # Ohorn
    0x01A1,  # ohorn
    0x01AF,  # Uhorn
    0x01B0,  # uhorn
]


def bit9(font):
    return bool(font["OS/2"].ulUnicodeRange1 & (1 << 9))


def main():
    reference = TTFont(REFERENCE)
    target = TTFont(TARGET)
    ref_cmap = reference.getBestCmap()
    target_cmap = target.getBestCmap()

    missing = [
        cp
        for cp in VIETNAMESE_CODEPOINTS
        if cp in ref_cmap and cp not in target_cmap
    ]

    print(f"{len(missing)} glyph con thieu:\n")
    for cp in missing:
        try:
            name = unicodedata.name(chr(cp))
        except ValueError:
            name = "?"
        print(f"U+{cp:04X}  {chr(cp)}  {name}")

    print()
    print("unicodeRange bit9 (Vietnamese) - reference:", bit9(reference))
    print("unicodeRange bit9 (Vietnamese) - target:   ", bit9(target))


if __name__ == "__main__":
    main()
