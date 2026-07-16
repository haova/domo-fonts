#!/usr/bin/env python3
"""Cap nhat FONT_METRICS trong preview.html cho khop bang metrics THAT trong font vua build.

Doc truc tiep tu bang head/hhea/OS2 cua font (fontTools) -- KHONG do qua DOM/Canvas o runtime
trinh duyet nua, vi cach do gian tiep do de sai lech (khac API, khac cach browser layout text)
va da gay lech guideline trong preview.html truoc do. Day la nguon du lieu chuan nhat: dung con
so thiet ke that ma type designer da dat trong font (unitsPerEm, hhea ascent/descent,
OS/2 sCapHeight/sxHeight).

Sinh object JS { ascent, descent, capHeight, xHeight } (don vi: phan cua em, tuc da chia
cho unitsPerEm) cho ca "DoMoSans" va "Inter", roi thay the dung phan giua marker
/* AUTOGEN:METRICS:START */.../* AUTOGEN:METRICS:END */ trong preview.html.

Dung: python3 Scripts/gen_preview_font_metrics.py
Duoc goi tu dong o cuoi Scripts/build_sans.sh sau moi lan build.
"""

import json
import re
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
PREVIEW_HTML = ROOT / "preview.html"

FONTS = {
    "DoMoSans": ROOT / "Sans/fonts/variable/DoMoSans[opsz,wght].ttf",
    "Inter": ROOT / "Reference/Inter-Variable.ttf",
}


def read_metrics(font_path):
    font = TTFont(str(font_path))
    upm = font["head"].unitsPerEm
    hhea = font["hhea"]
    os2 = font["OS/2"]
    return {
        "ascent": hhea.ascent / upm,
        "descent": hhea.descent / upm,
        "capHeight": os2.sCapHeight / upm,
        "xHeight": os2.sxHeight / upm,
    }


def main():
    html = PREVIEW_HTML.read_text(encoding="utf-8")

    metrics = {label: read_metrics(path) for label, path in FONTS.items()}
    js_obj = json.dumps(metrics, indent=2)

    pattern = re.compile(
        r"(/\* AUTOGEN:METRICS:START \*/).*?(/\* AUTOGEN:METRICS:END \*/)",
        re.DOTALL,
    )
    if not pattern.search(html):
        raise SystemExit("Khong tim thay marker AUTOGEN:METRICS trong preview.html")
    html = pattern.sub(lambda m: f"{m.group(1)}\n{js_obj}\n{m.group(2)}", html)

    PREVIEW_HTML.write_text(html, encoding="utf-8")
    for label, m in metrics.items():
        print(f"{label}: ascent={m['ascent']:.4f} descent={m['descent']:.4f} "
              f"capHeight={m['capHeight']:.4f} xHeight={m['xHeight']:.4f}")
    print(f"Da ghi lai {PREVIEW_HTML}")


if __name__ == "__main__":
    main()
