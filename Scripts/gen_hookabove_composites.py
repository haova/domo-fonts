#!/usr/bin/env python3
"""Sinh cac glyph composite dau hoi (hookabove) cho DoMoSans, tu glyph mark `hookabovecomb`
(da tao boi Scripts/gen_hookabovecomb.py).

Dung chung logic dat dau-tren voi dau nga (xem Scripts/viet_top_composites.py):
- Base co dau moc (horn: ơ/ư) -> dau hoi nam CHINH GIUA than chu (khong lech theo horn).
- Base co dau mu (circumflex: â/ê/ô) -> dau hoi chech vai phai dau mu (lech phai 1/2 be rong dau,
  xuong 1/3 chieu cao dau).
- Base con lai -> dau hoi xep thang tren, giua than chu.

Ket qua: ả Ả ẩ Ẩ ẳ Ẳ ẻ Ẻ ể Ể ỉ Ỉ ỏ Ỏ ổ Ổ ở Ở ủ Ủ ử Ử ỷ Ỷ (thuong + hoa).

Dung: python3 Scripts/gen_hookabove_composites.py [--dry-run]
Chay SAU Scripts/gen_hookabovecomb.py (va gen_horn_composites.py de ra ở/ử).
"""

import argparse
from pathlib import Path

from glyphsLib import GSFont

from viet_top_composites import build_top_composites

ROOT = Path(__file__).resolve().parent.parent
DOMO_SOURCES = [
    ROOT / "Sans/Source/DoMoSans.glyphs",
    ROOT / "Sans/Source/DoMoSans-Italic.glyphs",
]

HOOK_ABOVE_COMBINING = "̉"  # COMBINING HOOK ABOVE


def process_font(path, dry_run):
    print(f"=== {path.name} ===")
    font = GSFont(str(path))
    build_top_composites(font, "hookabovecomb", "hookabove", HOOK_ABOVE_COMBINING,
                         circumflex_dir="right")

    if dry_run:
        print(f"{path.name}: --dry-run, khong ghi file.")
        return
    font.save(str(path))
    print(f"Da ghi {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    for path in DOMO_SOURCES:
        if not path.exists():
            print(f"Bo qua: khong tim thay {path}")
            continue
        process_font(path, args.dry_run)


if __name__ == "__main__":
    main()
