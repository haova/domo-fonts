#!/usr/bin/env python3
"""Sinh cac glyph composite dau nang (dotbelow) cho DoMoSans, tu glyph mark `dotbelowcomb`
(da tao boi Scripts/gen_dotbelowcomb.py).

Vi sao can them buoc nay: `dotbelowcomb` chi la hinh dang con dau (mark), tu no khong lam
xuat hien ky tu co dau. De ghep duoc, can du 2 phia:
  - Base letter (a, i, o...) can anchor "bottom" (khong gach duoi) -- diem "moi" mark toi bam.
  - Mark (dotbelowcomb) can anchor "_bottom" (co gach duoi) -- diem tren mark ap vao dung vi tri do.
  Da co "_bottom" o mark (xem gen_dotbelowcomb.py), nhung CHUA co "bottom" o base letter nao ca
  -- day la ly do build xong van khong ra ky tu dau nang.

Script nay:
1. Voi moi base letter trong BASES, them anchor "bottom" tai (x cua anchor "top" co san, y=0)
   -- dung chung x voi "top" de dau tren/duoi thang hang, quy uoc pho bien trong thiet ke font.
   Neu base da co anchor "bottom" thi giu nguyen (khong ghi de tay nguoi khac da chinh).
2. Tao glyph composite moi (vd "adotbelow") = component base + component "dotbelowcomb", dich
   component dotbelowcomb theo dung offset = anchor"bottom"(base) - anchor"_bottom"(mark), tinh
   rieng cho tung master (khong dua vao Automatic Alignment cua Glyphs app vi script chay headless).
3. Gan Unicode dung cho glyph composite (ghep base char + U+0323, normalize NFC).

CHU Y ve pham vi: o+moc (ohorn) va u+moc (uhorn) CHUA co glyph base rieng trong font (da xac
nhan bang grep, khong ra ket qua) nen KHONG the tu sinh "ohorndotbelow"/"uhorndotbelow" o day --
day la phan ve glyph con thieu, thuoc viec cua type designer (xem VIETHOA.md).

Dung: python3 Scripts/gen_dotbelow_composites.py [--dry-run]
"""

import argparse
import unicodedata
from pathlib import Path

from glyphsLib import GSFont
from glyphsLib.classes import GSAnchor, GSComponent, GSGlyph, GSLayer
from glyphsLib.types import Point

ROOT = Path(__file__).resolve().parent.parent
DOMO_SOURCES = [
    ROOT / "Sans/Source/DoMoSans.glyphs",
    ROOT / "Sans/Source/DoMoSans-Italic.glyphs",
]

# Base letter co san trong font -> co so de ghep dotbelow. "ohorn"/"uhorn" (o+moc, u+moc) da duoc
# tao boi Scripts/gen_horn_composites.py nen gio ghep duoc ợ/Ợ/ự/Ự (horn + dot below).
BASES = [
    ("a", "A"), ("abreve", "Abreve"), ("acircumflex", "Acircumflex"),
    ("e", "E"), ("ecircumflex", "Ecircumflex"),
    ("i", "I"),
    ("o", "O"), ("ocircumflex", "Ocircumflex"), ("ohorn", "Ohorn"),
    ("u", "U"), ("uhorn", "Uhorn"),
    ("y", "Y"),
]

# Ky tu goc (khong dau) tuong ung voi tung base name, dung de tinh Unicode composite qua NFC.
BASE_CHAR = {
    "a": "a", "abreve": "ă", "acircumflex": "â",
    "e": "e", "ecircumflex": "ê",
    "i": "i",
    "o": "o", "ocircumflex": "ô", "ohorn": "ơ",
    "u": "u", "uhorn": "ư",
    "y": "y",
}

DOT_BELOW_COMBINING = "̣"


def composed_char(base_name, is_upper):
    base_char = BASE_CHAR[base_name]
    if is_upper:
        base_char = base_char.upper()
    return unicodedata.normalize("NFC", base_char + DOT_BELOW_COMBINING)


def get_anchor(layer, name):
    for a in layer.anchors:
        if a.name == name:
            return a
    return None


def ensure_bottom_anchor(font, layer):
    """Them anchor 'bottom' tai (x cua 'top', y=0) neu chua co. Tra ve anchor 'bottom'.

    Voi composite trong (vd ohorn/uhorn = o/u + horn, chua co anchor rieng): lay anchor 'bottom'
    tu component base dau tien (o/u) — dotbelow bam TAM THAN CHU nen dung 'bottom' cua o/u la dung,
    horn o vai phai khong anh huong."""
    bottom = get_anchor(layer, "bottom")
    if bottom is not None:
        return bottom
    top = get_anchor(layer, "top")
    if top is not None:
        x = top.position.x
    elif layer.components:
        # Composite thieu anchor: suy 'bottom' tu component base dau tien.
        base_comp = layer.components[0]
        base_layer = font.glyphs[base_comp.name].layers[layer.associatedMasterId]
        base_bottom = get_anchor(base_layer, "bottom") or get_anchor(base_layer, "top")
        off_x = base_comp.position.x if base_comp.position else 0
        x = (base_bottom.position.x + off_x) if base_bottom is not None else round(layer.width / 2)
    else:
        x = round(layer.width / 2)
    bottom = GSAnchor("bottom", Point(round(x), 0))
    layer.anchors.append(bottom)
    return bottom


def dot_below_width(mark_layer):
    """Be rong bbox cua hinh dot trong glyph 'dotbelowcomb' o master nay (dot to dan theo weight)."""
    xs = [n.position.x for p in mark_layer.paths for n in p.nodes]
    if not xs:
        return 0
    return max(xs) - min(xs)


def build_composite(font, base_name, char_key, is_upper, mark_glyph):
    base_glyph = font.glyphs[base_name]
    if base_glyph is None:
        print(f"  [bo qua] khong co glyph base '{base_name}'")
        return

    composite_char = composed_char(char_key, is_upper)
    composite_name = f"{base_name}dotbelow"

    if font.glyphs[composite_name] is not None:
        del font.glyphs[composite_name]

    new_glyph = GSGlyph(composite_name)
    new_glyph.category = "Letter"
    new_glyph.unicode = f"{ord(composite_char):04X}"

    for master in font.masters:
        base_layer = base_glyph.layers[master.id]
        mark_layer = mark_glyph.layers[master.id]

        bottom = ensure_bottom_anchor(font, base_layer)
        mark_bottom = get_anchor(mark_layer, "_bottom")
        if mark_bottom is None:
            raise SystemExit(f"'dotbelowcomb' thieu anchor '_bottom' o master {master.name}")

        dx = round(bottom.position.x - mark_bottom.position.x)
        dy = round(bottom.position.y - mark_bottom.position.y)

        # Truong hop dac biet cho 'y' thuong: 'y' co than cheo/duoi lech nen dot dat theo anchor
        # 'bottom' trong bi lech trai so voi tam thi giac -> dich dot sang phai 1 be rong dot
        # (do rieng tung master vi dot to dan theo weight).
        if base_name == "y":
            dx += round(dot_below_width(mark_layer))

        layer = GSLayer()
        layer.layerId = master.id
        layer.associatedMasterId = master.id
        layer.width = base_layer.width
        layer.components.append(GSComponent(base_name, (0, 0)))
        layer.components.append(GSComponent("dotbelowcomb", (dx, dy)))
        new_glyph.layers.append(layer)

    font.glyphs.append(new_glyph)
    print(f"  + {composite_name} (U+{ord(composite_char):04X}) = {base_name} + dotbelowcomb")


def process_font(path, dry_run):
    print(f"=== {path.name} ===")
    font = GSFont(str(path))

    mark_glyph = font.glyphs["dotbelowcomb"]
    if mark_glyph is None:
        raise SystemExit(
            f"{path.name}: khong co glyph 'dotbelowcomb' -- chay "
            f"Scripts/gen_dotbelowcomb.py truoc."
        )

    for lower_name, upper_name in BASES:
        build_composite(font, lower_name, lower_name, False, mark_glyph)
        build_composite(font, upper_name, lower_name, True, mark_glyph)

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
