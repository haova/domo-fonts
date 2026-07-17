#!/usr/bin/env python3
"""Sinh glyph "dotbelowcomb" (dau nang) cho DoMoSans.

Ty le dat cham (ratio = gap_below / gap_above) da duoc do MOT LAN tu font tham khao Inter va
HARD-CODE trong RATIO_BY_MASTER duoi day — do la hang so hinh hoc, khong doi qua moi lan chay, nen
khong can doc/instantiate Inter luc build nua (bo phu thuoc fontTools + Reference/Inter-Variable.ttf).

Cach do goc (chi de tham chieu, KHONG chay luc build):
  O Inter, gap_above = khoang tu dinh stem chu "i" (dotlessi) den day cham tren "i"; gap_below =
  khoang tu baseline den dinh cham duoi cua dot-below. ratio = gap_below / gap_above, do rieng tung
  master (opsz, wght) khop 12 master that cua DoMoSans (Inter la VF nen dung varLib.instancer;
  co the bi clamp neu ngoai range truc cua Inter). Muon do lai: xem lich su git ban truoc file nay.

Cach dung ratio (chay luc build):
  O DoMoSans, glyph "i" co san 2 shape trong 1 layer: than chu (stem) + cham tron o tren (dot).
  Doc gap_above THAT tu vector tung master, nhan ratio -> gap_below rieng tung master. Copy nguyen
  hinh dot (KHONG scale), dich xuong duoi baseline sao cho dinh cham nam o y = -gap_below. Them
  anchor "_bottom" tai (center_x, 0) de ghep vao anchor "bottom" cac chu cai.

Dung: python3 Scripts/gen_dotbelowcomb.py [--dry-run]
Yeu cau: chay trong .venv co glyphsLib (co san trong requirements.txt cua repo).
"""

import argparse
import copy
from pathlib import Path

from glyphsLib import GSFont
from glyphsLib.classes import GSAnchor, GSGlyph, GSLayer, GSPath

ROOT = Path(__file__).resolve().parent.parent
DOMO_SOURCES = {
    "Roman": ROOT / "Sans/Source/DoMoSans.glyphs",
    "Italic": ROOT / "Sans/Source/DoMoSans-Italic.glyphs",
}

# Ty le gap_below/gap_above do MOT LAN tu Inter (xem docstring), hard-code theo (opsz, wght) cho
# 12 master that cua DoMoSans (3 opsz x 4 wght). Hang so hinh hoc — khong doi qua moi lan chay.
RATIO_BY_MASTER = {
    (9, 100): 0.8588235294117647,
    (9, 300): 0.9420321135651153,
    (9, 400): 1.0,
    (9, 1000): 1.0,
    (24, 100): 0.9398728428701181,
    (24, 300): 0.9756721167230895,
    (24, 400): 1.0,
    (24, 1000): 1.2729443708392627,
    (40, 100): 1.0,
    (40, 300): 1.0,
    (40, 400): 1.0,
    (40, 1000): 1.6285714285714286,
}

WGHT_BY_NAME = {"Thin": 100, "Light": 300, "Regular": 400, "ExtraBlack": 1000}


def master_coord_from_name(name):
    """'9pt Thin' -> (9, 100). master.axes tra ve gia tri design-space noi bo (qua Axis Mappings
    phi tuyen trong config.yaml), khong phai pt/wght that, nen phai suy tu ten master (da khop dung
    quy uoc dat ten trong VIETHOA.md muc 2.2: "<opsz>pt <wght-name>")."""
    opsz_str, wght_name = name.split(" ", 1)
    opsz = int(opsz_str.replace("pt", ""))
    wght_name = wght_name.replace("Italic", "").strip()
    if not wght_name:
        wght_name = "Regular"  # vd "9pt Italic" = Regular Italic, ten Regular bi luoc bo
    return (opsz, WGHT_BY_NAME[wght_name])


def domo_i_dot_shape(gs_layer):
    """Tra ve (stem_top, dot_path, dot_bbox) tu layer 'i' cua DoMoSans — dot la shape co ymin cao
    hon (nam phia tren stem)."""
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


def build_dotbelowcomb(glyphs_path, dry_run):
    font = GSFont(str(glyphs_path))
    i_glyph = font.glyphs["i"]
    if i_glyph is None:
        raise SystemExit(f"{glyphs_path}: khong tim thay glyph 'i'.")

    if font.glyphs["dotbelowcomb"] is not None:
        print(f"{glyphs_path.name}: glyph 'dotbelowcomb' da ton tai, xoa de tao lai.")
        del font.glyphs["dotbelowcomb"]

    new_glyph = GSGlyph("dotbelowcomb")
    new_glyph.category = "Mark"
    new_glyph.subCategory = "Nonspacing"

    for master in font.masters:
        coord = master_coord_from_name(master.name)
        ratio = RATIO_BY_MASTER.get(coord)
        if ratio is None:
            raise SystemExit(f"Khong co ratio hard-code cho master {master.name} ({coord}).")

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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Chi in, khong ghi file .glyphs")
    args = ap.parse_args()

    for label, path in DOMO_SOURCES.items():
        if not path.exists():
            print(f"Bo qua {label}: khong tim thay {path}")
            continue
        print(f"=== Sinh dotbelowcomb cho {label} ({path.name}) ===")
        build_dotbelowcomb(path, args.dry_run)


if __name__ == "__main__":
    main()
