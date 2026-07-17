#!/usr/bin/env python3
"""Sinh cac glyph composite dau sac (acute) CON THIEU cho DoMoSans, tu mark `acutecomb` (U+0301).

Sac tren base don (a/o/u/e/i/y -> á ó ú é í ý + hoa) da co san (designer lam) nen KHONG dung toi;
script chi sinh phan con thieu (only_missing=True): sac tren base co dau phu —
  breve (ă -> ắ), circumflex (â/ê/ô -> ấ/ế/ố), horn (ơ/ư -> ớ/ứ) + hoa.

Quy uoc dat dau (xem Scripts/viet_top_composites.py):
- horn (ơ/ư): dau sac CHINH GIUA than chu (khong lech theo horn).
- circumflex (â/ê/ô): dau sac chech VAI TRAI dau mu.
- breve (ă) va base con lai: xep thang tren, giua than chu.

Dung: python3 Scripts/gen_acute_composites.py [--dry-run]
Chay SAU gen_horn_composites.py (can ohorn/uhorn de ra ớ/ứ).
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

ACUTE_COMBINING = "́"  # COMBINING ACUTE ACCENT (U+0301)


def process_font(path, dry_run):
    print(f"=== {path.name} ===")
    font = GSFont(str(path))
    build_top_composites(font, "acutecomb", "acute", ACUTE_COMBINING,
                         circumflex_dir="left", only_missing=True, circumflex_drop=3,
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
