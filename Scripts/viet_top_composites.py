#!/usr/bin/env python3
"""Logic dung chung de sinh composite dau-TREN tieng Viet (dau hoi, dau nga, ... ghep qua cap
anchor top/_top). Cac script gen_hookabove_composites.py / gen_tilde_composites.py goi ham
build_top_composites(...) o day, chi khac: ten mark, hau to ten glyph, ky tu combining.

Quy uoc vi tri dat dau-tren (giong nhau moi loai dau):
- Base don (a/e/o/u/y/i + hoa): co san anchor "top" -> dung ngay, dau nam GIUA than chu.
- Base co dau moc (horn: ohorn/uhorn): horn bam VAI PHAI, KHONG phai dau tren dinh -> dau van nam
  CHINH GIUA than chu (suy "top" tu component base o/u, bo qua horn).
- Base co dau mu (circumflex: â/ê/ô): dat dau chech vai phai dau mu -> lech phai 1/2 be rong dau,
  lech xuong 1/3 chieu cao dau (tranh dau chong qua cao). Cac dau khac (breve ...) xep thang tren.
"""

import unicodedata

from glyphsLib.classes import GSAnchor, GSComponent, GSGlyph, GSLayer
from glyphsLib.types import Point

# Danh sach base tieng Viet nhan dau-tren (chung cho moi loai dau).
BASES = [
    ("a", "A"), ("abreve", "Abreve"), ("acircumflex", "Acircumflex"),
    ("e", "E"), ("ecircumflex", "Ecircumflex"),
    ("i", "I"),
    ("o", "O"), ("ocircumflex", "Ocircumflex"), ("ohorn", "Ohorn"),
    ("u", "U"), ("uhorn", "Uhorn"),
    ("y", "Y"),
]

BASE_CHAR = {
    "a": "a", "abreve": "ă", "acircumflex": "â",
    "e": "e", "ecircumflex": "ê",
    "i": "i",
    "o": "o", "ocircumflex": "ô", "ohorn": "ơ",
    "u": "u", "uhorn": "ư",
    "y": "y",
}

# horn la dau moc bam VAI PHAI than chu (mark ngang), KHONG phai dau tren dinh -> khi suy vi tri
# dat dau-tren, bo qua component nay (dau van o giua than chu).
SIDE_MARKS = {"horn"}
CIRCUMFLEX_MARKS = {"circumflexcomb", "circumflexcomb.case"}


def composed_char(base_name, is_upper, combining):
    base_char = BASE_CHAR[base_name]
    if is_upper:
        base_char = base_char.upper()
    return unicodedata.normalize("NFC", base_char + combining)


def get_anchor(layer, name):
    for a in layer.anchors:
        if a.name == name:
            return a
    return None


def shape_bbox_top(layer):
    ys = [n.position.y for p in layer.paths for n in p.nodes]
    xs = [n.position.x for p in layer.paths for n in p.nodes]
    if not ys:
        return None
    return (min(xs) + max(xs)) / 2, max(ys)


def _derive_top_from_base_component(font, layer):
    """base co horn (ohorn/uhorn): suy 'top' tu component base o/u (giua than chu), bo qua horn."""
    base_comp = layer.components[0]  # component dau tien la base o/u
    base_layer = font.glyphs[base_comp.name].layers[layer.associatedMasterId]
    off_x = base_comp.position.x if base_comp.position else 0
    off_y = base_comp.position.y if base_comp.position else 0
    base_top = ensure_top_anchor(font, base_layer)  # o/u co san 'top'
    return base_top.position.x + off_x, base_top.position.y + off_y


def ensure_top_anchor(font, layer):
    """Tra ve anchor 'top' tren base layer (diem dat dau-tren).

    - Base don: co san 'top' -> dung.
    - Base co horn: dau o CHINH GIUA than chu -> suy tu component base o/u (bo qua horn).
    - Base dau-tren (circumflex/breve): mark do quyet dinh dinh xep chong (top cua mark hoac dinh bbox).
    'top' tren base composite luon do script sinh (goc khong co) nen XOA-suy-lai moi lan de khong
    dong bang gia tri cu. Base don giu 'top' goc cua designer."""
    if layer.components:
        layer.anchors = [a for a in layer.anchors if a.name != "top"]
    else:
        top = get_anchor(layer, "top")
        if top is not None:
            return top

    if layer.components:
        if any(c.name in SIDE_MARKS for c in layer.components):
            x, y = _derive_top_from_base_component(font, layer)
            top = GSAnchor("top", Point(round(x), round(y)))
            layer.anchors.append(top)
            return top

        mark_comp = layer.components[-1]  # mark tren dinh (circumflex/breve) la component cuoi
        mark_layer = font.glyphs[mark_comp.name].layers[layer.associatedMasterId]
        off_x = mark_comp.position.x if mark_comp.position else 0
        off_y = mark_comp.position.y if mark_comp.position else 0
        mark_top = get_anchor(mark_layer, "top")
        if mark_top is not None:
            x = mark_top.position.x + off_x
            y = mark_top.position.y + off_y
        else:
            bt = shape_bbox_top(mark_layer)
            mark_uptop = get_anchor(mark_layer, "_top")
            cx = mark_uptop.position.x if mark_uptop is not None else (bt[0] if bt else 0)
            x = cx + off_x
            y = (bt[1] if bt else 0) + off_y
        top = GSAnchor("top", Point(round(x), round(y)))
        layer.anchors.append(top)
        return top

    # base don khong co 'top' (vd 'i' thuong): lay giua width, dinh bbox
    bt = shape_bbox_top(layer)
    x = bt[0] if bt else round(layer.width / 2)
    y = bt[1] if bt else 0
    top = GSAnchor("top", Point(round(x), round(y)))
    layer.anchors.append(top)
    return top


def has_circumflex(base_layer):
    return any(c.name in CIRCUMFLEX_MARKS for c in base_layer.components)


def mark_size(mark_layer):
    """(width, height) bbox cua hinh dau o master nay (to dan theo weight)."""
    xs = [n.position.x for p in mark_layer.paths for n in p.nodes]
    ys = [n.position.y for p in mark_layer.paths for n in p.nodes]
    if not xs:
        return 0, 0
    return max(xs) - min(xs), max(ys) - min(ys)


def build_one(font, base_name, char_key, is_upper, mark_name, mark_glyph, suffix, combining,
              circumflex_dir, only_missing, circumflex_drop, circumflex_shift):
    base_glyph = font.glyphs[base_name]
    if base_glyph is None:
        print(f"  [bo qua] khong co glyph base '{base_name}'")
        return

    composite_char = composed_char(char_key, is_upper, combining)
    composite_name = f"{base_name}{suffix}"
    uni = f"{ord(composite_char):04X}"

    # only_missing (sac/huyen): dau tren BASE DON (a/e/i/o/u/y — layer khong co component) da duoc
    # designer lam san (á/à/ó/ò...) nen GIU NGUYEN, khong dung toi. Chi sinh dau tren BASE COMPOSITE
    # (breve/circumflex/horn — layer co component) la phan con thieu. Phan biet theo LOAI base
    # (co component hay khong), khong theo "unicode da ton tai" — vi base composite do chinh script
    # nay sinh cung da ton tai o lan chay truoc, van phai ghi de lai.
    if only_missing:
        first_master_layer = base_glyph.layers[font.masters[0].id]
        is_simple_base = not first_master_layer.components
        if is_simple_base:
            print(f"  [giu nguyen] {composite_name}: base don do designer lam, bo qua")
            return

    if font.glyphs[composite_name] is not None:
        del font.glyphs[composite_name]

    new_glyph = GSGlyph(composite_name)
    new_glyph.category = "Letter"
    new_glyph.unicode = uni

    for master in font.masters:
        base_layer = base_glyph.layers[master.id]
        mark_layer = mark_glyph.layers[master.id]

        top = ensure_top_anchor(font, base_layer)
        mark_top = get_anchor(mark_layer, "_top")
        if mark_top is None:
            raise SystemExit(f"'{mark_name}' thieu anchor '_top' o master {master.name}")

        dx = round(top.position.x - mark_top.position.x)
        dy = round(top.position.y - mark_top.position.y)

        # Base co dau mu (â/ê/ô): dat dau chech vai dau mu theo circumflex_dir:
        #   "right" -> vai phai (hoi, sac);  "left" -> vai trai (huyen);  None -> can giua (nga).
        # Lech ngang (circumflex_shift x be rong dau) sang vai phai/trai, keo XUONG (1/circumflex_drop)
        # chieu cao dau (mac dinh 1/3 — nep vai mu ma khong trung len dau mu).
        if circumflex_dir and has_circumflex(base_layer):
            mw, mh = mark_size(mark_layer)
            shift = round(mw * circumflex_shift)
            dx += shift if circumflex_dir == "right" else -shift
            dy -= round(mh / circumflex_drop)

        layer = GSLayer()
        layer.layerId = master.id
        layer.associatedMasterId = master.id
        layer.width = base_layer.width
        layer.components.append(GSComponent(base_name, (0, 0)))
        layer.components.append(GSComponent(mark_name, (dx, dy)))
        new_glyph.layers.append(layer)

    font.glyphs.append(new_glyph)
    print(f"  + {composite_name} (U+{ord(composite_char):04X}) = {base_name} + {mark_name}")


def build_top_composites(font, mark_name, suffix, combining, circumflex_dir=None,
                         only_missing=False, circumflex_drop=3, circumflex_shift=0.5):
    """Sinh composite dau-tren cho font: mark_name (vd 'tildecomb'), suffix ('tilde'),
    combining (chu combining tuong ung, vd '\\u0303').

    circumflex_dir: tren base dau mu (â/ê/ô) dat dau chech vai nao —
        "right" (hoi, sac) | "left" (huyen) | None (nga: can giua).
    circumflex_drop: keo dau xuong 1/circumflex_drop chieu cao dau tren base mu (mac dinh 3).
    circumflex_shift: lech ngang = circumflex_shift x be rong dau (mac dinh 0.5). Sac/huyen dat lon
        hon de chech vai ro rang hon.
    only_missing: True -> chi sinh dau tren BASE COMPOSITE (breve/circumflex/horn); giu nguyen dau
        tren base don do designer lam san (sac/huyen). False -> sinh/ghi de tat ca (hoi, nga)."""
    mark_glyph = font.glyphs[mark_name]
    if mark_glyph is None:
        raise SystemExit(f"khong co glyph mark '{mark_name}' trong font.")
    for lower_name, upper_name in BASES:
        build_one(font, lower_name, lower_name, False, mark_name, mark_glyph, suffix, combining,
                  circumflex_dir, only_missing, circumflex_drop, circumflex_shift)
        build_one(font, upper_name, lower_name, True, mark_name, mark_glyph, suffix, combining,
                  circumflex_dir, only_missing, circumflex_drop, circumflex_shift)
