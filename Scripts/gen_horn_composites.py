#!/usr/bin/env python3
"""Sinh cac glyph composite co dau moc (horn) cho DoMoSans: Ohorn/ohorn/Uhorn/uhorn,
tu glyph mark `horn` (da tao boi Scripts/gen_horn.py).

Vi sao can buoc nay: `horn` chi la hinh dang con dau moc (mark U+031B); tu no khong lam
xuat hien Ơ/ơ/Ư/ư. De ghep duoc, can du 2 phia:
  - Base letter (o, u, O, U) can anchor "horn" -- diem "moc" mark toi bam (vai phai than chu).
  - Mark (horn) can anchor "_horn" -- da co san (xem gen_horn.py), dat o canh trai-duoi horn.

Script nay:
1. Them anchor "horn" vao base O/o/U/u (neu chua co), rieng cho tung master:
   - o/u DA co san anchor "topright" o dung vai phai -> dung ngay vi tri do.
   - O/U CHUA co "topright" -> do xmax that cua outline tai vung gan cap-height (dai y quanh dinh)
     lam vi tri KHOI DAU, dat "horn" o (xmax_capband, cap_height). Day chi la diem tam de composite
     hien ra dung cho, TYPE DESIGNER can soi mat va tinh chinh lai trong Glyphs (xem VIETHOA.md 2.5).
2. Tao glyph composite (Ohorn/ohorn/Uhorn/uhorn) = component base + component "horn", dich
   component horn theo offset = anchor"horn"(base) - anchor"_horn"(mark), tinh rieng tung master
   (khong dua vao Automatic Alignment vi script chay headless).
3. Gan Unicode dung cho tung composite.

Dung: python3 Scripts/gen_horn_composites.py [--dry-run]
Chay SAU Scripts/gen_horn.py.
"""

import argparse
from pathlib import Path

from glyphsLib import GSFont
from glyphsLib.classes import GSAnchor, GSComponent, GSGlyph, GSLayer
from glyphsLib.types import Point

ROOT = Path(__file__).resolve().parent.parent
DOMO_SOURCES = [
    ROOT / "Sans/Source/DoMoSans.glyphs",
    ROOT / "Sans/Source/DoMoSans-Italic.glyphs",
]

# base_name, is_upper, unicode. Or=U+01A1 or_upper=U+01A0; ur=U+01B0 ur_upper=U+01AF.
COMPOSITES = [
    ("o", False, 0x01A1, "ohorn"),
    ("O", True, 0x01A0, "Ohorn"),
    ("u", False, 0x01B0, "uhorn"),
    ("U", True, 0x01AF, "Uhorn"),
]

# Vi tri anchor "horn" tren base O/o/U/u, hard-code theo tung master. Tach rieng Roman/Italic vi
# Italic nghieng nen x lech dang ke. Toa do la DIEM KHOI DAU (o/u lay tu anchor "topright" co san;
# O/U do mep phai outline gan cap-height) -- chinh tay trong Glyphs neu can cho horn khit vai chu.
HORN_ANCHOR = {
    "Roman": {
        "o": {
            "9pt Thin": (447, 475), "9pt Light": (449, 466), "9pt Regular": (459, 462), "9pt ExtraBlack": (418, 450),
            "24pt Thin": (447, 445), "24pt Light": (449, 436), "24pt Regular": (459, 432), "24pt ExtraBlack": (418, 420),
            "40pt Thin": (427, 445), "40pt Light": (440, 436), "40pt Regular": (444, 432), "40pt ExtraBlack": (398, 420),
        },
        "O": {
            "9pt Thin": (558, 649), "9pt Light": (561, 640), "9pt Regular": (575, 636), "9pt ExtraBlack": (530, 624),
            "24pt Thin": (578, 649), "24pt Light": (599, 640), "24pt Regular": (609, 636), "24pt ExtraBlack": (565, 624),
            "40pt Thin": (558, 649), "40pt Light": (586, 640), "40pt Regular": (596, 636), "40pt ExtraBlack": (557, 624),
        },
        "u": {
            "9pt Thin": (426, 526), "9pt Light": (458, 526), "9pt Regular": (459, 526), "9pt ExtraBlack": (506, 526),
            "24pt Thin": (426, 496), "24pt Light": (457, 496), "24pt Regular": (465, 496), "24pt ExtraBlack": (470, 496),
            "40pt Thin": (403, 496), "40pt Light": (434, 496), "40pt Regular": (430, 496), "40pt ExtraBlack": (470, 496),
        },
        "U": {
            "9pt Thin": (541, 700), "9pt Light": (568, 700), "9pt Regular": (577, 700), "9pt ExtraBlack": (567, 700),
            "24pt Thin": (538, 700), "24pt Light": (568, 700), "24pt Regular": (578, 700), "24pt ExtraBlack": (567, 700),
            "40pt Thin": (508, 700), "40pt Light": (538, 700), "40pt Regular": (550, 700), "40pt ExtraBlack": (548, 700),
        },
    },
    "Italic": {
        "o": {
            "9pt Thin Italic": (493, 475), "9pt Light Italic": (480, 466), "9pt Italic": (476, 462), "9pt ExtraBlack Italic": (364, 450),
            "24pt Thin Italic": (472, 445), "24pt Light Italic": (469, 436), "24pt Italic": (467, 432), "24pt ExtraBlack Italic": (357, 420),
            "40pt Thin Italic": (453, 445), "40pt Light Italic": (426, 436), "40pt Italic": (423, 432), "40pt ExtraBlack Italic": (311, 420),
        },
        "O": {
            "9pt Thin Italic": (682, 649), "9pt Light Italic": (665, 640), "9pt Italic": (671, 636), "9pt ExtraBlack Italic": (611, 624),
            "24pt Thin Italic": (746, 649), "24pt Light Italic": (712, 640), "24pt Italic": (707, 636), "24pt ExtraBlack Italic": (583, 624),
            "40pt Thin Italic": (703, 649), "40pt Light Italic": (676, 640), "40pt Italic": (673, 636), "40pt ExtraBlack Italic": (552, 624),
        },
        "u": {
            "9pt Thin Italic": (472, 526), "9pt Light Italic": (504, 526), "9pt Italic": (505, 526), "9pt ExtraBlack Italic": (492, 526),
            "24pt Thin Italic": (443, 496), "24pt Light Italic": (464, 496), "24pt Italic": (500, 496), "24pt ExtraBlack Italic": (440, 496),
            "40pt Thin Italic": (417, 496), "40pt Light Italic": (438, 496), "40pt Italic": (443, 496), "40pt ExtraBlack Italic": (426, 496),
        },
        "U": {
            "9pt Thin Italic": (671, 700), "9pt Light Italic": (705, 700), "9pt Italic": (725, 700), "9pt ExtraBlack Italic": (840, 700),
            "24pt Thin Italic": (688, 700), "24pt Light Italic": (721, 700), "24pt Italic": (728, 700), "24pt ExtraBlack Italic": (772, 700),
            "40pt Thin Italic": (608, 700), "40pt Light Italic": (648, 700), "40pt Italic": (660, 700), "40pt ExtraBlack Italic": (728, 700),
        },
    },
}


def get_anchor(layer, name):
    for a in layer.anchors:
        if a.name == name:
            return a
    return None


def ensure_horn_anchor(style, base_name, layer, master_name):
    """Dat anchor 'horn' tren base layer theo bang hard-code HORN_ANCHOR. Tra ve anchor 'horn'.
    LUON ghi de: xoa 'horn' cu (neu co) roi ghi lai dung theo bang, de moi lan chay bang moi
    (hoac chinh sua) deu duoc ap lai hoan toan."""
    layer.anchors = [a for a in layer.anchors if a.name != "horn"]

    try:
        x, y = HORN_ANCHOR[style][base_name][master_name]
    except KeyError:
        raise SystemExit(
            f"HORN_ANCHOR thieu vi tri cho style={style} base={base_name} master={master_name!r}"
        )
    horn = GSAnchor("horn", Point(x, y))
    layer.anchors.append(horn)
    return horn


def build_composite(font, style, base_name, is_upper, uni, comp_name, horn_glyph):
    base_glyph = font.glyphs[base_name]
    if base_glyph is None:
        print(f"  [bo qua] khong co glyph base '{base_name}'")
        return

    if font.glyphs[comp_name] is not None:
        del font.glyphs[comp_name]

    new_glyph = GSGlyph(comp_name)
    new_glyph.category = "Letter"
    new_glyph.unicode = f"{uni:04X}"

    for master in font.masters:
        base_layer = base_glyph.layers[master.id]
        horn_layer = horn_glyph.layers[master.id]

        horn_anchor = ensure_horn_anchor(style, base_name, base_layer, master.name)
        mark_horn = get_anchor(horn_layer, "_horn")
        if mark_horn is None:
            raise SystemExit(f"'horn' thieu anchor '_horn' o master {master.name}")

        dx = round(horn_anchor.position.x - mark_horn.position.x)
        dy = round(horn_anchor.position.y - mark_horn.position.y)

        layer = GSLayer()
        layer.layerId = master.id
        layer.associatedMasterId = master.id
        layer.width = base_layer.width
        layer.components.append(GSComponent(base_name, (0, 0)))
        layer.components.append(GSComponent("horn", (dx, dy)))
        new_glyph.layers.append(layer)

    font.glyphs.append(new_glyph)
    print(f"  + {comp_name} (U+{uni:04X}) = {base_name} + horn")


def process_font(path, dry_run):
    print(f"=== {path.name} ===")
    font = GSFont(str(path))

    horn_glyph = font.glyphs["horn"]
    if horn_glyph is None:
        raise SystemExit(
            f"{path.name}: khong co glyph 'horn' -- chay Scripts/gen_horn.py truoc."
        )

    # Phan biet Roman/Italic qua ten master (Italic co hau to " Italic").
    style = "Italic" if any("Italic" in m.name for m in font.masters) else "Roman"

    # Luon ghi de: anchor 'horn' tren base va 4 composite duoc tao lai tu dau moi lan chay,
    # de bang HORN_ANCHOR moi/chinh sua luon duoc ap day du.
    for base_name, is_upper, uni, comp_name in COMPOSITES:
        build_composite(font, style, base_name, is_upper, uni, comp_name, horn_glyph)

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
