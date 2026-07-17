#!/usr/bin/env python3
"""Sinh glyph "hookabovecomb" (dau hoi U+0309) cho DoMoSans o du 12 master, tu 4 hinh ve san.

Bo cuc du lieu (Reference/hookabovecomb.svg): giong horn.svg — dung 4 <path>, moi path la 1 hinh
dau hoi ung voi 1 WEIGHT that cua DoMoSans, theo thu tu xuat hien:
  path1=Thin(100), path2=Light(300), path3=Regular(400), path4=ExtraBlack(1000).
KHONG scale theo opsz: voi moi weight, ca 3 master opsz (9/24/40pt) dung chung 1 hinh.
=> 4 hinh SVG phu het 12 master (4 wght x 3 opsz).

Vi tri (khac horn — hookabove la dau TREN dinh chu, ghep qua cap anchor top/_top co san,
GIONG acutecomb/gravecomb/tildecomb da co trong font, KHONG can bang hard-code hay type designer
tinh chinh anchor tren base):
- Doc quy uoc san co tu acutecomb: anchor "_top" dat tai (center_x, connect_y) voi
  connect_y = 526 (opsz 9pt) / 496 (opsz 24&40pt) = do cao anchor "top" tren base (x-height),
  va hinh dau cach connect_y mot GAP = 43 (do tu acutecomb) — tuc shape_ymin = connect_y + 43.
- Anchor "top" dat tai (center_x, shape_ymax) de xep chong dau (khong dung cho tieng Viet nhung
  giu dung quy uoc chung, an toan).

Toa do: SVG la he y-down; .glyphs la y-up => lat y (y' = H_svg - y). Chuan hoa left-edge ve x=0,
canh giua theo be rong, dat day hinh (ymin) tai connect_y + GAP.

Ket qua: glyph "hookabovecomb" (Mark/Nonspacing), 12 layer, moi layer 1 hinh + anchor _top, top.
Sau do dung composite qtam (obreve... khong — cac composite tieng Viet ơ hỏi/... dung anchor san).

Dung: python3 Scripts/gen_hookabovecomb.py [--dry-run]
Yeu cau: glyphsLib + fontTools (co san trong requirements.txt cua repo).
"""

import argparse
import re
import sys
from pathlib import Path

from fontTools.pens.recordingPen import RecordingPen
from fontTools.svgLib.path import parse_path
from glyphsLib import GSFont
from glyphsLib.classes import GSAnchor, GSGlyph, GSLayer

ROOT = Path(__file__).resolve().parent.parent
HOOK_SVG = ROOT / "Reference/hookabovecomb.svg"
DOMO_SOURCES = {
    "Roman": ROOT / "Sans/Source/DoMoSans.glyphs",
    "Italic": ROOT / "Sans/Source/DoMoSans-Italic.glyphs",
}

HOOK_CODEPOINT = 0x0309  # COMBINING HOOK ABOVE

# Thu tu 4 path trong SVG -> weight that (path1..path4). Giong gen_horn.py.
WEIGHT_ORDER = [100, 300, 400, 1000]  # Thin, Light, Regular, ExtraBlack
WGHT_BY_NAME = {"Thin": 100, "Light": 300, "Regular": 400, "ExtraBlack": 1000}

# Quy uoc dau-tren co san trong font (do tu acutecomb, dong nhat moi master):
#   connect_y = do cao anchor "top" tren base = x-height (9pt: 526; 24&40pt: 496)
#   GAP = khoang tu connect_y len day hinh dau = 43
GAP_ABOVE = 43
CONNECT_Y_BY_OPSZ = {9: 526, 24: 496, 40: 496}


def svg_viewbox_height(svg_text):
    m = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ [\d.\-]+ ([\d.\-]+)"', svg_text)
    if not m:
        raise SystemExit("Khong doc duoc viewBox height trong hookabovecomb.svg.")
    return float(m.group(1))


def svg_path_ds(svg_text):
    ds = re.findall(r'\bd="([^"]+)"', svg_text)
    if len(ds) != len(WEIGHT_ORDER):
        raise SystemExit(
            f"hookabovecomb.svg co {len(ds)} path, mong doi {len(WEIGHT_ORDER)} (1 path / weight)."
        )
    return ds


def flip_and_normalize(recording, svg_h):
    """Lat y (y-down -> y-up), dich left-edge ve x=0 va bottom (ymin) ve y=0.

    Tra ve (new_recording_value, width, height). Vi tri y that duoc dat khi ve (theo connect_y+GAP).
    """
    def fy(pt):
        return (pt[0], svg_h - pt[1])

    flipped = []
    for op, args in recording.value:
        flipped.append((op, tuple(fy(a) if isinstance(a, tuple) else a for a in args)))

    pts = [a for op, args in flipped for a in args if isinstance(a, tuple)]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    xmin, ymin = min(xs), min(ys)

    shifted = []
    for op, args in flipped:
        shifted.append(
            (op, tuple((a[0] - xmin, a[1] - ymin) if isinstance(a, tuple) else a for a in args))
        )
    width = round(max(xs) - xmin)
    height = round(max(ys) - ymin)
    return shifted, width, height


def replay_shifted(pen_value, out_pen, dy):
    """Ve lai, dich toan bo len dy (dat day hinh tai y=dy)."""
    for op, args in pen_value:
        new_args = tuple((a[0], a[1] + dy) if isinstance(a, tuple) else a for a in args)
        getattr(out_pen, op)(*new_args)


def _signed_area(path):
    pts = [(n.position.x, n.position.y) for n in path.nodes]
    s = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        s += (x2 - x1) * (y2 + y1)
    return s


def ensure_ccw(layer):
    """Dam bao moi contour ve NGUOC CHIEU KIM (CCW) — cung chieu contour ngoai than chu, tranh RONG
    khi net dau chong len than chu. Hinh sinh tu SVG (y-down) sau khi lat y hay bi CW nen dao lai."""
    for p in layer.paths:
        if _signed_area(p) > 0:
            p.reverse()


def master_opsz_wght(master_name):
    """'9pt Thin' -> (9, 100). Ten master = '<opsz>pt <wght-name>' (xem VIETHOA.md 2.2)."""
    opsz_str, wght_name = master_name.split(" ", 1)
    opsz = int(opsz_str.replace("pt", ""))
    wght_name = wght_name.replace("Italic", "").strip() or "Regular"
    return opsz, WGHT_BY_NAME[wght_name]


def build_hook(glyphs_path, hook_by_weight, dry_run):
    font = GSFont(str(glyphs_path))

    if font.glyphs["hookabovecomb"] is not None:
        print(f"{glyphs_path.name}: glyph 'hookabovecomb' da ton tai, xoa de tao lai.")
        del font.glyphs["hookabovecomb"]

    new_glyph = GSGlyph("hookabovecomb")
    new_glyph.unicode = f"{HOOK_CODEPOINT:04X}"
    new_glyph.category = "Mark"
    new_glyph.subCategory = "Nonspacing"

    for master in font.masters:
        opsz, wght = master_opsz_wght(master.name)
        pen_value, width, height = hook_by_weight[wght]
        connect_y = CONNECT_Y_BY_OPSZ[opsz]
        shape_ymin = connect_y + GAP_ABOVE  # day hinh dat tai day (giong acutecomb)

        layer = GSLayer()
        layer.layerId = master.id
        layer.associatedMasterId = master.id
        layer.width = width

        replay_shifted(pen_value, layer.getPen(), dy=shape_ymin)
        ensure_ccw(layer)

        center_x = round(width / 2)
        shape_ymax = shape_ymin + height
        layer.anchors.append(GSAnchor("_top", (center_x, connect_y)))
        layer.anchors.append(GSAnchor("top", (center_x, shape_ymax)))
        new_glyph.layers.append(layer)

        print(
            f"  [{glyphs_path.name}] {master.name}: wght={wght} w={width} "
            f"_top=({center_x},{connect_y}) top=({center_x},{shape_ymax})"
        )

    font.glyphs.append(new_glyph)

    if dry_run:
        print(f"{glyphs_path.name}: --dry-run, khong ghi file.")
        return
    font.save(str(glyphs_path))
    print(f"Da ghi {glyphs_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Chi in, khong ghi file .glyphs")
    args = ap.parse_args()

    if not HOOK_SVG.exists():
        sys.exit(f"Khong tim thay {HOOK_SVG}")

    svg_text = HOOK_SVG.read_text()
    svg_h = svg_viewbox_height(svg_text)
    ds = svg_path_ds(svg_text)

    print("=== Doc 4 hinh dau hoi tu Reference/hookabovecomb.svg (path -> weight) ===")
    hook_by_weight = {}
    for d, wght in zip(ds, WEIGHT_ORDER):
        rec = RecordingPen()
        parse_path(d, rec)
        pen_value, width, height = flip_and_normalize(rec, svg_h)
        hook_by_weight[wght] = (pen_value, width, height)
        print(f"  wght={wght:>4}: width={width} height={height}")

    for label, path in DOMO_SOURCES.items():
        if not path.exists():
            print(f"Bo qua {label}: khong tim thay {path}")
            continue
        print(f"\n=== Sinh hookabovecomb cho {label} ({path.name}) ===")
        build_hook(path, hook_by_weight, args.dry_run)


if __name__ == "__main__":
    main()
