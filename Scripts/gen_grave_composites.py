#!/usr/bin/env python3
"""Sinh cac glyph composite dau huyen (grave) CON THIEU cho DoMoSans, tu mark `gravecomb` (U+0300).

Huyen tren base don (a/o/u/e/i/y -> à ò ù è ì ỳ + hoa) da co san (designer lam) nen KHONG dung toi;
script chi sinh phan con thieu (only_missing=True): huyen tren base co dau phu —
  breve (ă -> ằ), circumflex (â/ê/ô -> ầ/ề/ồ), horn (ơ/ư -> ờ/ừ) + hoa.

Quy uoc dat dau (xem Scripts/viet_top_composites.py):
- horn (ơ/ư): dau huyen CHINH GIUA than chu (khong lech theo horn).
- circumflex (â/ê/ô): dau huyen chech VAI PHAI dau mu.
- breve (ă) va base con lai: xep thang tren, giua than chu.

Dung: python3 Scripts/gen_grave_composites.py [--dry-run]
Chay SAU gen_horn_composites.py (can ohorn/uhorn de ra ờ/ừ).
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

GRAVE_COMBINING = "̀"  # COMBINING GRAVE ACCENT (U+0300)


def process_font(path, dry_run):
    print(f"=== {path.name} ===")
    font = GSFont(str(path))
    build_top_composites(font, "gravecomb", "grave", GRAVE_COMBINING,
                         circumflex_dir="right", only_missing=True, circumflex_drop=3,
                         circumflex_shift=0.4)

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
