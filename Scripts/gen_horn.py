#!/usr/bin/env python3
"""Sinh glyph "horn" (dau moc U+031B) cho DoMoSans o du 12 master, tu 4 hinh horn ve san.

Bo cuc du lieu (Reference/horn.svg):
- File SVG co dung 4 <path>, moi path la 1 hinh horn ung voi 1 WEIGHT that cua DoMoSans,
  theo thu tu xuat hien: path1=Thin(100), path2=Light(300), path3=Regular(400), path4=ExtraBlack(1000).
- KHONG scale theo opsz: voi moi weight, ca 3 master opsz (9pt/24pt/40pt) dung chung y nguyen 1 horn.
  => 4 hinh SVG phu het 12 master (4 wght x 3 opsz).

Toa do:
- SVG la he y-down; .glyphs la y-up => lat y (y' = H_svg - y).
- SVG chi luu HINH DANG; vi tri cuoi cung do anchor quyet dinh (xem VIETHOA.md muc 2.5).
  Moi horn duoc chuan hoa ve goc trai-duoi bbox = (0, 0), roi dat anchor "_horn" tai (0, 0)
  = canh trai duoi cua horn, de khop voi anchor "horn" tren base O/o/U/u.

Ket qua: glyph "horn" (category Mark / Nonspacing), 12 layer, moi layer 1 hinh + anchor "_horn".
Composite Ohorn/ohorn/Uhorn/uhorn duoc dung rieng (glyphsLib/Glyphs) qua cap anchor horn/_horn.

Dung: python3 Scripts/gen_horn.py [--dry-run]
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
HORN_SVG = ROOT / "Reference/horn.svg"
DOMO_SOURCES = {
    "Roman": ROOT / "Sans/Source/DoMoSans.glyphs",
    "Italic": ROOT / "Sans/Source/DoMoSans-Italic.glyphs",
}

HORN_CODEPOINT = 0x031B  # COMBINING HORN

# Thu tu 4 path trong SVG -> weight that cua DoMoSans (path1..path4).
WEIGHT_ORDER = [100, 300, 400, 1000]  # Thin, Light, Regular, ExtraBlack
WGHT_BY_NAME = {"Thin": 100, "Light": 300, "Regular": 400, "ExtraBlack": 1000}

# Y cua anchor "_horn" theo tung weight = MEP TREN cua canh duoi horn (x=0), do tay tu horn.svg
# (sau khi lat y + chuan hoa goc trai-duoi ve 0). Dat o day thay vi y=0 de khi ghep horn khong
# bi le xuong duoi. Chinh tay them trong Glyphs neu can.
ANCHOR_Y_BY_WEIGHT = {100: 20, 300: 40, 400: 50, 1000: 80}


def svg_viewbox_height(svg_text):
    m = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ [\d.\-]+ ([\d.\-]+)"', svg_text)
    if not m:
        raise SystemExit("Khong doc duoc viewBox height trong horn.svg.")
    return float(m.group(1))


def svg_path_ds(svg_text):
    ds = re.findall(r'\bd="([^"]+)"', svg_text)
    if len(ds) != len(WEIGHT_ORDER):
        raise SystemExit(
            f"horn.svg co {len(ds)} path, mong doi {len(WEIGHT_ORDER)} (1 path / weight)."
        )
    return ds


def flip_and_normalize(recording, svg_h):
    """Lat y (y-down -> y-up) va dich goc trai-duoi bbox ve (0, 0).

    Tra ve (new_recording_value, width) de ve vao GSLayer qua pen.
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
    return shifted, width


def replay(pen_value, out_pen):
    for op, args in pen_value:
        getattr(out_pen, op)(*args)


def _signed_area(path):
    pts = [(n.position.x, n.position.y) for n in path.nodes]
    s = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        s += (x2 - x1) * (y2 + y1)
    return s


def ensure_ccw(layer):
    """Dam bao moi contour cua horn vẽ NGUOC CHIEU KIM (CCW, signed_area < 0) — cung chieu voi
    contour ngoai cua than chu o/u trong font nay. Neu horn nguoc chieu (CW), vung horn chong len
    than chu bi tru đi -> RONG. horn sinh tu SVG (y-down) sau khi lat y hay bi CW nen phai dao lai."""
    for p in layer.paths:
        if _signed_area(p) > 0:  # CW -> dao ve CCW
            p.reverse()


def master_weight(master_name):
    """'9pt Thin' -> 100. Xem gen_dotbelowcomb.py: ten master = '<opsz>pt <wght-name>'."""
    _, wght_name = master_name.split(" ", 1)
    wght_name = wght_name.replace("Italic", "").strip() or "Regular"
    return WGHT_BY_NAME[wght_name]


def build_horn(glyphs_path, horn_by_weight, dry_run):
    font = GSFont(str(glyphs_path))

    if font.glyphs["horn"] is not None:
        print(f"{glyphs_path.name}: glyph 'horn' da ton tai, xoa de tao lai.")
        del font.glyphs["horn"]

    new_glyph = GSGlyph("horn")
    new_glyph.unicode = f"{HORN_CODEPOINT:04X}"
    new_glyph.category = "Mark"
    new_glyph.subCategory = "Nonspacing"

    for master in font.masters:
        wght = master_weight(master.name)
        pen_value, width = horn_by_weight[wght]

        layer = GSLayer()
        layer.layerId = master.id
        layer.associatedMasterId = master.id
        layer.width = width

        replay(pen_value, layer.getPen())
        ensure_ccw(layer)  # dao chieu ve CCW -> khop winding voi than chu, tranh RONG khi ghep chong
        # Anchor "_horn" o MEP TREN cua canh duoi horn (x=0, y theo weight), khong phai day bbox,
        # de khi ghep horn khong bi le xuong duoi.
        anchor_y = ANCHOR_Y_BY_WEIGHT[wght]
        layer.anchors.append(GSAnchor("_horn", (0, anchor_y)))
        new_glyph.layers.append(layer)

        print(f"  [{glyphs_path.name}] {master.name}: wght={wght} width={width} _horn=(0,{anchor_y})")

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

    if not HORN_SVG.exists():
        sys.exit(f"Khong tim thay {HORN_SVG}")

    svg_text = HORN_SVG.read_text()
    svg_h = svg_viewbox_height(svg_text)
    ds = svg_path_ds(svg_text)

    print("=== Doc 4 hinh horn tu Reference/horn.svg (path -> weight) ===")
    horn_by_weight = {}
    for d, wght in zip(ds, WEIGHT_ORDER):
        rec = RecordingPen()
        parse_path(d, rec)
        pen_value, width = flip_and_normalize(rec, svg_h)
        horn_by_weight[wght] = (pen_value, width)
        print(f"  wght={wght:>4}: width={width}")

    for label, path in DOMO_SOURCES.items():
        if not path.exists():
            print(f"Bo qua {label}: khong tim thay {path}")
            continue
        print(f"\n=== Sinh horn cho {label} ({path.name}) ===")
        build_horn(path, horn_by_weight, args.dry_run)


if __name__ == "__main__":
    main()
