#!/usr/bin/env python3
"""Sinh glyph "dotbelowcomb" (dau nang) cho DoMoSans, dua tren ty le do dac tu font tham khao (Inter).

Co che:
1. O font Inter (Reference/Inter-Variable.ttf), do khoang cach giua dinh stem chu "i" (dotlessi)
   va day cham tren dau chu "i" (goi la gap_above), roi do khoang cach giua baseline va dinh cham
   duoi cua "i." (U+0323 COMBINING DOT BELOW, hoac "idotbelow"/"ibelowdotcomb") (goi la gap_below).
   Ty le rieng: ratio = gap_below / gap_above, do rieng cho tung master (opsz, wght) khop voi
   12 master that cua DoMoSans, Inter la variable font nen dung fontTools varLib.instancer de
   noi suy dung toa do (co the bi clamp neu ngoai range truc cua Inter).
2. O DoMoSans (Sans/Source/DoMoSans.glyphs va -Italic.glyphs), glyph "i" da co san 2 shape trong
   1 layer: than chu (stem) + cham tron o tren (dot) -- KHONG phai component rieng. Dot nay chinh
   la hinh dang dung lai cho "dotaccentcomb" (glyph dau cham don, dang dung cho vd i, j).
   Doc truc tiep gap_above that (khong can uoc luong) tu vector that cua tung master DoMoSans,
   nhan voi ratio do duoc o buoc 1 -> ra gap_below rieng cho tung master DoMoSans.
3. Tao glyph moi "dotbelowcomb": copy nguyen hinh dang dot tu "i" (giu ty le do day net, KHONG scale),
   dich chuyen xuong duoi baseline sao cho dinh cham (diem gan baseline nhat) nam o y = -gap_below.
   Them anchor "_bottom" tai (center_x, 0) de ghep vao anchor "bottom" cua cac chu cai co san.

Dung: python3 Scripts/gen_dotbelowcomb.py [--dry-run]
Yeu cau: chay trong .venv co glyphsLib + fontTools (co san trong requirements.txt cua repo).
"""

import argparse
import copy
import sys
from pathlib import Path

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from glyphsLib import GSFont
from glyphsLib.classes import GSAnchor, GSGlyph, GSLayer, GSNode, GSPath

ROOT = Path(__file__).resolve().parent.parent
INTER_PATH = ROOT / "Reference/Inter-Variable.ttf"
DOMO_SOURCES = {
    "Roman": ROOT / "Sans/Source/DoMoSans.glyphs",
    "Italic": ROOT / "Sans/Source/DoMoSans-Italic.glyphs",
}

# 12 master that cua DoMoSans (xem VIETHOA.md muc 2.2): 3 opsz x 4 wght.
MASTER_COORDS = [
    {"opsz": opsz, "wght": wght}
    for opsz in (9, 24, 40)
    for wght in (100, 300, 400, 1000)
]

DOT_BELOW_CANDIDATES = ["dotbelowcomb", "belowdotcomb", "dotbelow"]  # Inter dung ten "dotbelow"
DOT_BELOW_CODEPOINT = 0x0323  # COMBINING DOT BELOW


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def bbox_of_contours(contours):
    """contours: list of list of (x, y) points -> overall (xmin, ymin, xmax, ymax)."""
    xs = [x for c in contours for x, y in c]
    ys = [y for c in contours for x, y in c]
    return min(xs), min(ys), max(xs), max(ys)


def glyph_contours(font, glyph_name):
    """Tra ve danh sach contour (da decompose component, vd 'i' = dotlessi + uni0307)."""
    gs = font.getGlyphSet()
    if glyph_name not in gs:
        return None
    pen = DecomposingRecordingPen(gs)
    gs[glyph_name].draw(pen)

    contours = []
    current = None
    for op, args in pen.value:
        if op == "moveTo":
            current = [args[0]]
        elif op == "lineTo":
            current.append(args[0])
        elif op == "curveTo":
            current.extend(args)
        elif op == "qCurveTo":
            current.extend(p for p in args if p is not None)
        elif op in ("closePath", "endPath"):
            if current:
                contours.append(current)
            current = None
    return contours


def measure_inter_ratio(master_coord):
    """Instantiate Inter tai (opsz,wght) gan nhat, tra ve ratio = gap_below / gap_above."""
    font = TTFont(str(INTER_PATH))
    axes = {a.axisTag: (a.minValue, a.maxValue) for a in font["fvar"].axes}
    coords = {}
    for tag in ("opsz", "wght"):
        if tag in axes:
            lo, hi = axes[tag]
            coords[tag] = clamp(master_coord[tag], lo, hi)
    inst = instancer.instantiateVariableFont(font, coords)

    dot_below_name = None
    for cand in DOT_BELOW_CANDIDATES:
        if cand in inst.getGlyphOrder():
            dot_below_name = cand
            break
    if dot_below_name is None:
        cmap = inst.getBestCmap()
        dot_below_name = cmap.get(DOT_BELOW_CODEPOINT)
    if dot_below_name is None:
        raise SystemExit("Khong tim thay glyph dau-nang (dotbelow) trong Inter de do ty le.")

    i_contours = glyph_contours(inst, "i") or glyph_contours(inst, "dotlessi")
    if not i_contours or len(i_contours) < 2:
        raise SystemExit("Khong doc duoc glyph 'i' cua Inter (can >=2 contour: stem + dot).")

    # 2 contour cua "i": contour thap hon la stem, contour cao hon la cham tren.
    boxes = [bbox_of_contours([c]) for c in i_contours]
    boxes.sort(key=lambda b: b[1])  # theo ymin
    stem_box, dot_box = boxes[0], boxes[-1]
    stem_top = stem_box[3]
    dot_bottom = dot_box[1]
    gap_above = dot_bottom - stem_top

    below_contours = glyph_contours(inst, dot_below_name)
    if not below_contours:
        raise SystemExit(f"Khong doc duoc glyph '{dot_below_name}' cua Inter.")
    below_box = bbox_of_contours(below_contours)
    dot_below_top = below_box[3]
    gap_below = 0 - dot_below_top  # baseline (y=0) tru dinh cham duoi

    if gap_above <= 0:
        raise SystemExit(f"gap_above <= 0 ({gap_above}) — kiem tra lai glyph 'i' cua Inter.")

    return gap_below / gap_above


def domo_i_dot_shape(gs_layer):
    """Tra ve (stem_top, dot_path_nodes, dot_bbox) tu layer 'i' cua DoMoSans — dot la shape co
    ymin cao hon (nam phia tren stem)."""
    paths = [s for s in gs_layer.shapes if isinstance(s, GSPath)]
    if len(paths) < 2:
        raise SystemExit("Glyph 'i' trong DoMoSans khong co du 2 shape (stem + dot) o layer nay.")

    def bbox(path):
        xs = [n.position.x for n in path.nodes]
        ys = [n.position.y for n in path.nodes]
        return min(xs), min(ys), max(xs), max(ys)

    boxes = [(p, bbox(p)) for p in paths]
    boxes.sort(key=lambda pb: pb[1][1])
    stem_path, stem_box = boxes[0]
    dot_path, dot_box = boxes[-1]
    stem_top = stem_box[3]
    return stem_top, dot_path, dot_box


WGHT_BY_NAME = {"Thin": 100, "Light": 300, "Regular": 400, "ExtraBlack": 1000}


def master_coord_from_name(name):
    """'9pt Thin' -> {'opsz': 9, 'wght': 100}. master.axes tra ve gia tri design-space noi bo
    (qua Axis Mappings phi tuyen trong config.yaml), khong phai pt/wght that, nen phai suy tu ten
    master (da khop dung quy uoc dat ten trong VIETHOA.md muc 2.2: "<opsz>pt <wght-name>")."""
    opsz_str, wght_name = name.split(" ", 1)
    opsz = int(opsz_str.replace("pt", ""))
    wght_name = wght_name.replace("Italic", "").strip()
    if not wght_name:
        wght_name = "Regular"  # vd "9pt Italic" = Regular Italic, ten Regular bi luoc bo
    wght = WGHT_BY_NAME[wght_name]
    return {"opsz": opsz, "wght": wght}


def build_dotbelowcomb(glyphs_path, ratio_by_master, dry_run):
    font = GSFont(str(glyphs_path))
    i_glyph = font.glyphs["i"]
    if i_glyph is None:
        raise SystemExit(f"{glyphs_path}: khong tim thay glyph 'i'.")

    existing = font.glyphs["dotbelowcomb"]
    if existing is not None:
        print(f"{glyphs_path.name}: glyph 'dotbelowcomb' da ton tai, xoa de tao lai.")
        font.glyphs.remove(existing)

    new_glyph = GSGlyph("dotbelowcomb")
    new_glyph.category = "Mark"
    new_glyph.subCategory = "Nonspacing"

    for master in font.masters:
        coord = master_coord_from_name(master.name)
        ratio = ratio_by_master.get(_coord_key(coord))
        if ratio is None:
            raise SystemExit(f"Khong co ratio do duoc cho master {master.name} ({coord}).")

        i_layer = i_glyph.layers[master.id]
        stem_top, dot_path, dot_box = domo_i_dot_shape(i_layer)
        dot_xmin, dot_ymin, dot_xmax, dot_ymax = dot_box
        gap_above = dot_ymin - stem_top
        gap_below = ratio * gap_above
        dot_height = dot_ymax - dot_ymin

        new_top = round(-gap_below)
        new_bottom = round(new_top - dot_height)
        dy = new_bottom - dot_ymin
        dx = -dot_xmin  # dua left-edge ve x=0, giu nguyen be rong/hinh dang (khong scale)

        new_path = copy.deepcopy(dot_path)
        for node in new_path.nodes:
            node.position = (node.position.x + dx, node.position.y + dy)

        layer = GSLayer()
        layer.layerId = master.id
        layer.associatedMasterId = master.id
        layer.shapes.append(new_path)
        layer.width = round(dot_xmax - dot_xmin)
        center_x = round(layer.width / 2)
        layer.anchors.append(GSAnchor("_bottom", (center_x, 0)))
        new_glyph.layers.append(layer)

        print(
            f"  [{glyphs_path.name}] {master.name}: gap_above={gap_above:.1f} "
            f"ratio={ratio:.3f} -> gap_below={gap_below:.1f} (dinh cham o y={new_top})"
        )

    font.glyphs.append(new_glyph)

    if dry_run:
        print(f"{glyphs_path.name}: --dry-run, khong ghi file.")
        return
    font.save(str(glyphs_path))
    print(f"Da ghi {glyphs_path}")


def _coord_key(coord):
    return (coord["opsz"], coord["wght"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Chi in ket qua do, khong ghi file .glyphs")
    args = ap.parse_args()

    if not INTER_PATH.exists():
        sys.exit(f"Khong tim thay font tham khao: {INTER_PATH}")

    print("=== Do ty le gap_below/gap_above tu Inter (font tham khao) ===")
    ratio_by_master = {}
    for coord in MASTER_COORDS:
        ratio = measure_inter_ratio(coord)
        ratio_by_master[_coord_key(coord)] = ratio
        print(f"  opsz={coord['opsz']:>3} wght={coord['wght']:>4}: ratio={ratio:.4f}")

    for label, path in DOMO_SOURCES.items():
        if not path.exists():
            print(f"Bo qua {label}: khong tim thay {path}")
            continue
        print(f"\n=== Sinh dotbelowcomb cho {label} ({path.name}) ===")
        build_dotbelowcomb(path, ratio_by_master, args.dry_run)


if __name__ == "__main__":
    main()
