#!/bin/sh
# Build toan bo DM Sans: variable font + static ttf/otf + webfonts.
# Dung: ./Scripts/build_sans.sh  (chay tu thu muc goc repo)
# Tu dong tao .venv va cai requirements.txt neu chua co.
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv"

# gftools yeu cau Python >=3.10 - tim ban Python phu hop tren may (uu tien ban moi nhat)
PYTHON_BIN=""
for candidate in python3.13 python3.12 python3.11 python3.10 /opt/homebrew/bin/python3.12 /opt/homebrew/bin/python3.13 python3; do
  if command -v "$candidate" >/dev/null 2>&1; then
    version="$("$candidate" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
    major="$(echo "$version" | cut -d. -f1)"
    minor="$(echo "$version" | cut -d. -f2)"
    if [ "$major" -eq 3 ] && [ "$minor" -ge 10 ]; then
      PYTHON_BIN="$(command -v "$candidate")"
      break
    fi
  fi
done

if [ -z "$PYTHON_BIN" ]; then
  echo "Loi: khong tim thay Python >=3.10 tren may (gftools yeu cau ban nay)."
  echo "Cai bang: brew install python@3.12"
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "=== Khong tim thay .venv, dang tao moi bang $PYTHON_BIN va cai dependencies ==="
  "$PYTHON_BIN" -m venv "$VENV_DIR"
  "$VENV_DIR/bin/pip" install --upgrade pip
  "$VENV_DIR/bin/pip" install -r "$ROOT_DIR/requirements.txt"
fi

# shellcheck disable=SC1091
. "$VENV_DIR/bin/activate"

# generate glyphs — THU TU QUAN TRONG (composite phu thuoc mark + composite ghep lop):
#   1. Sinh cac MARK truoc (horn / dotbelowcomb / hookabovecomb).
#   2. Sinh horn composite (ohorn/uhorn...) — vi dotbelow & hookabove con ghep len ohorn/uhorn
#      de ra ợ/ự, ở/ử -> phai co ohorn/uhorn TRUOC.
#   3. Sinh dotbelow & hookabove composite (chay sau cung).
# Chay bang python cua .venv (dam bao co glyphsLib/fontTools tren may sach).
python3 Scripts/gen_horn.py
python3 Scripts/gen_dotbelowcomb.py
python3 Scripts/gen_hookabovecomb.py
python3 Scripts/gen_horn_composites.py
python3 Scripts/gen_dotbelow_composites.py
python3 Scripts/gen_hookabove_composites.py
python3 Scripts/gen_tilde_composites.py
python3 Scripts/gen_acute_composites.py
python3 Scripts/gen_grave_composites.py

cd "$ROOT_DIR/Sans/Source"
gftools builder config.yaml

echo
echo "=== Cap nhat unicode-range trong preview.html theo cmap that vua build ==="
"$VENV_DIR/bin/python" "$ROOT_DIR/Scripts/gen_preview_unicode_range.py"

echo
echo "=== Cap nhat FONT_METRICS trong preview.html theo bang metrics that vua build ==="
"$VENV_DIR/bin/python" "$ROOT_DIR/Scripts/gen_preview_font_metrics.py"

echo
echo "=== Xong. Output: ==="
echo "  Sans/fonts/variable/"
echo "  Sans/fonts/ttf/"
echo "  Sans/fonts/otf/"
echo "  Sans/fonts/webfonts/"
echo "  preview.html (unicode-range + font metrics da dong bo)"
