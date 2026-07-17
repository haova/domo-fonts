#!/usr/bin/env python3
"""Sinh cac glyph composite dau nga (tilde) cho DoMoSans, tu glyph mark `tildecomb` (U+0303) da co
san trong font.

Dung chung logic dat dau-tren voi dau hoi (xem Scripts/viet_top_composites.py):
- Dau nga LUON CAN GIUA than chu tren moi base (khac hookabove): ke ca base co dau mu (â/ê/ô)
  hay dau moc (horn: ơ/ư) -> khong lech vai phai.

Ket qua: ã Ã ẫ Ẫ ẵ Ẵ ẽ Ẽ ễ Ễ ĩ Ĩ õ Õ ỗ Ỗ ỡ Ỡ ũ Ũ ữ Ữ ỹ Ỹ (thuong + hoa).

Dung: python3 Scripts/gen_tilde_composites.py [--dry-run]
Chay SAU gen_horn_composites.py (can ohorn/uhorn de ra ỡ/ữ).
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

TILDE_COMBINING = "̃"  # COMBINING TILDE


def process_font(path, dry_run):
    print(f"=== {path.name} ===")
    font = GSFont(str(path))
    build_top_composites(font, "tildecomb", "tilde", TILDE_COMBINING)

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
