# Việt hoá DM Sans

Quy trình đầy đủ, từ đầu đến cuối, để bổ sung hỗ trợ tiếng Việt cho DM Sans, đúng chuẩn glyph-set/QA của Google Fonts và tương thích với pipeline build hiện có của repo (`gftools builder` + `config.yaml`).

## 0. Hiện trạng

`Sans/Source/DMSans.glyphs` (và `DMSans-Italic.glyphs`) hiện **chưa hỗ trợ tiếng Việt**:

- Đã có sẵn: `acutecomb`, `gravecomb`, `tildecomb`, `breve`, `circumflex` (phục vụ các ngôn ngữ Đông Âu).
- Còn thiếu:
  - `hookabovecomb` (U+0309, dấu hỏi) và `dotbelowcomb` (dấu nặng) — 2 combining mark quan trọng nhất còn thiếu.
  - Dấu móc (horn) cho `o`/`u`: `Ohorn`, `ohorn`, `Uhorn`, `uhorn`.
  - Toàn bộ 90 glyph trong khối Latin Extended Additional (U+1EA0–U+1EF9) — xem checklist đầy đủ ở mục 1.2.
  - Bit `Vietnamese` trong OS/2 `unicodeRanges` (bit 9) — hiện tại giá trị là `0,1,2,3,5,31,32,33,35,36,38,45,60,62`, chưa có 9.

## 1. Xác định glyph set bắt buộc

### 1.1. Nguồn chuẩn — không tự đoán danh sách ký tự

- Chuẩn glyph-set của Google: [googlefonts/glyphsets](https://github.com/googlefonts/glyphsets), file [GLYPHSETS.md](https://github.com/googlefonts/glyphsets/blob/main/GLYPHSETS.md), cấp **`GF_Latin_Vietnamese`** (186 glyph chữ cái + 16 combining mark).
- Cấp này **mở rộng từ `GF_Latin_Core`** — phải đảm bảo DM Sans đã đạt đủ `GF_Latin_Core` trước (baseline bắt buộc cho mọi font Latin của Google Fonts, theo [gf-guide/requirements](https://googlefonts.github.io/gf-guide/requirements.html)).
- Đây cũng là glyph-list mà fontbakery check `com.google.fonts/check/glyph_coverage` đối chiếu khi duyệt font.

Lấy danh sách bằng package chính thức:

```sh
pip install glyphsets
python3 -c "
from glyphsets import GFGlyphData
data = GFGlyphData()
print(data.get_glyphset('GF_Latin_Vietnamese'))
"
```

### 1.2. Font tham khảo — đối chiếu chéo để ra checklist thực tế

Ngoài glyph-list lý thuyết ở trên, nên đối chiếu thêm với 1 font Google Fonts đã việt hoá tốt để có checklist cụ thể, đồng thời tham khảo cách họ đặt tên anchor/xử lý mark chồng.

**Font được chọn: Inter** (`Reference/Inter-Variable.ttf`, tải từ [google/fonts](https://github.com/google/fonts/blob/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf), giấy phép OFL).

Đã thử so sánh 3 ứng viên trước khi chọn — tiêu chí quyết định là **cấu trúc axis/master phải giống DM Sans**, không phải số lượng glyph tổng:

|                                   | DM Sans                         | Inter                           | Lexend     | Manrope    |
| --------------------------------- | ------------------------------- | ------------------------------- | ---------- | ---------- |
| Axes                              | `opsz`(9–40) + `wght`(100–1000) | `opsz`(14–32) + `wght`(100–900) | chỉ `wght` | chỉ `wght` |
| Named instances                   | 9                               | 9                               | 9          | 7          |
| Tổng glyph                        | 511                             | 2933                            | 850        | 742        |
| Vietnamese coverage (U+1EA0–1EF9) | 6/90                            | 90/90                           | 90/90      | 90/90      |

→ Chỉ Inter có cùng 2 trục `opsz`+`wght` như DM Sans — dùng được để tham khảo cách mark/anchor tiếng Việt hoạt động khi nội suy qua **cả optical size lẫn weight**, đúng bài toán của DM Sans. Lexend/Manrope thiếu hẳn trục `opsz` nên không phù hợp cho việc này dù cũng hỗ trợ Vietnamese đầy đủ.

**Được phép**: dùng Inter để (a) lấy checklist glyph chính xác qua diff, (b) tham khảo tên anchor/tỷ lệ scale dấu chồng bằng mắt hoặc mở source nếu có.
**Không được phép**: copy trực tiếp outline từ Inter sang DM Sans, kể cả khi Inter là OFL — chỉ dùng làm tham chiếu kỹ thuật/thị giác, mọi outline của DM Sans vẫn phải vẽ riêng.

### 1.3. Checklist glyph còn thiếu (đã chạy diff thực tế)

Script dùng để tạo checklist (đối chiếu theo mã Unicode, không theo tên glyph, để tránh sai lệch do khác quy ước đặt tên): [`Scripts/diff_vietnamese_glyphs.py`](Scripts/diff_vietnamese_glyphs.py).

```sh
pip install fonttools
python3 Scripts/diff_vietnamese_glyphs.py
```

Kết quả: **90 glyph** còn thiếu, gồm:

- 2 combining mark: `hookabovecomb` (U+0309), `dotbelowcomb` (U+0323).
- 4 chữ horn gốc: `Ơ` `ơ` `Ư` `ư` (U+01A0, U+01A1, U+01AF, U+01B0).
- 84 chữ ghép dấu thanh trong khối U+1EA0–U+1EF7, ví dụ: Ạ ạ Ả ả Ấ ấ Ầ ầ Ẩ ẩ Ẫ ẫ Ậ ậ Ắ ắ Ằ ằ Ẳ ẳ Ẵ ẵ Ặ ặ Ẹ ẹ Ẻ ẻ Ế ế Ề ề Ể ể Ễ ễ Ệ ệ Ỉ ỉ Ị ị Ọ ọ Ỏ ỏ Ố ố Ồ ồ Ổ ổ Ỗ ỗ Ộ ộ Ớ ớ Ờ ờ Ở ở Ỡ ỡ Ợ ợ Ụ ụ Ủ ủ Ứ ứ Ừ ừ Ử ử Ữ ữ Ự ự Ỵ ỵ Ỷ ỷ.
- Đã xác nhận `Inter` bật bit 9 (`Vietnamese`) trong OS/2 `unicodeRanges`, `DM Sans` chưa bật — khớp với hiện trạng đã nêu ở mục 0.

## 2. Thiết kế trong Glyphs (việc của type designer)

### 2.1. Công cụ và nơi ghi

- **Công cụ: chỉ dùng [Glyphs App](https://glyphsapp.com) (Glyphs 3, macOS)** — đây là app đã tạo ra 2 file nguồn hiện có của repo, giữ nguyên vẹn Automatic Alignment (mark/component tự bám theo anchor của base) và Smart Components cần cho phần anchor/dấu chồng ở mục 2.3–2.4. Vẽ tay outline trực tiếp trong app, không phải viết code/script.
  - Không dùng FontForge: chuyển `.glyphs` sang UFO để sửa bằng FontForge sẽ "đóng băng" Automatic Alignment thành toạ độ cố định, mất khả năng mark tự cập nhật khi sửa lại outline base — ngược với mục đích tự động hoá đã thiết kế ở mục 2.3.
  - FontLab 8 về lý thuyết cũng đọc/ghi được `.glyphs`, nhưng để tránh rủi ro round-trip giữa 2 app (khác cách serialize file), quy trình này **chốt dùng 1 app duy nhất là Glyphs**.
- **Ghi vào đâu**: sửa trực tiếp trong 2 file nguồn đang có sẵn — không tạo file mới:
  - `Sans/Source/DMSans.glyphs`
  - `Sans/Source/DMSans-Italic.glyphs`

  Glyph, master, anchor đều lưu chung trong 1 file `.glyphs` (dạng plist text) theo từng khối `glyphname = ...` / `layers = (...)` / `anchors = (...)`. Vì `Sans/Source/config.yaml` đã khai báo đúng 2 file này ở mục `sources`, chỉ cần lưu file là bước build (mục 4) tự đọc glyph mới, không cần sửa `config.yaml`.

### 2.2. Vẽ 2 combining mark còn thiếu

Vẽ `hookabovecomb`, `dotbelowcomb`, đồng bộ phong cách (độ dày nét, khoảng cách, chiều cao) với mark có sẵn (`acutecomb`, `gravecomb`, `tildecomb`).

- Phải vẽ ở **đủ các master cực trị** của designspace hiện tại: Thin/ExtraBlack × 9pt/40pt × Roman/Italic — để nội suy đúng trên toàn bộ trục `opsz`/`wght`/`ital`, không chỉ vẽ 1 master rồi để tool tự suy diễn sai ở các trục còn lại.
- **Điều kiện bắt buộc để nội suy khớp (interpolation-compatible)**: cùng số lượng path/điểm, cùng thứ tự điểm, cùng hướng vẽ, cùng số lượng và tên anchor ở **mọi master**. Sai 1 điểm ở 1 master là đủ để các instance trung gian bị méo hoặc build lỗi.
- Kiểm tra bằng công cụ có sẵn trong app (Glyphs: "Show Interpolation" / cảnh báo ngoặc đỏ khi kéo thanh trượt giữa các master) trước khi build, không đợi build xong mới phát hiện.

### 2.3. Thiết lập anchor system

- Anchor cơ bản: `top`, `bottom`, `_top`, `_bottom` cho mark đơn (hookabovecomb, dotbelowcomb gắn thẳng lên base).
- Anchor riêng cho tổ hợp dấu chồng tiếng Việt: **`top_viet` / `_top_viet`** — khuyến nghị chính thức của Google tại [gf-guide/diacritics](https://googlefonts.github.io/gf-guide/diacritics.html), dùng cho trường hợp chồng 2 dấu (circumflex+tone, breve+tone), ví dụ ậ = a + circumflex + dotbelow, ẫ = a + circumflex + tilde.
  - Tách riêng khỏi `top`/`_top` để tránh xung đột vị trí với tổ hợp dấu của ngôn ngữ khác dùng chung base.
  - Mark vừa làm "base" cho mark khác vừa là "mark" gắn lên chữ cái (ví dụ circumflex phải nhận dotbelow chồng lên) cần có **cả hai** anchor: `top_viet` (để mark khác gắn vào) và `_top_viet` (để gắn vào base bên dưới).
- **Tự động hoá để tránh sai số khi đặt tay**:
  - Glyphs có sẵn lệnh `Glyph → Set Anchors` — tự tính vị trí `top`/`bottom` theo bounding box, áp dụng hàng loạt cho mọi glyph đã chọn, ở từng master.
  - Component dùng chế độ **Automatic Alignment** — mark tự bám theo anchor của base, tự cập nhật nếu sau này sửa lại outline base.
  - Với 2 mark hoàn toàn mới (`hookabovecomb`, `dotbelowcomb`), không có công thức sẵn để "Set Anchors" tự suy — nên đặt tay 1 lần ở 1 master chuẩn (dựa theo offset của `acutecomb`/`gravecomb` đã có), rồi dùng script Python trong Macro Panel (hoặc bộ [mekkablue scripts](https://github.com/mekkablue/Glyphs-Scripts), thư mục _Anchors_: "Add Anchors", "Check Anchors") để nhân bản sang các master còn lại và tự động rà soát anchor thiếu/lệch tên giữa các master.

### 2.4. Dấu chồng cần thu nhỏ — ví dụ ắ = ă + dấu sắc

Nếu giữ nguyên `brevecomb` full-size rồi chồng `acutecomb` lên trên, tổng chiều cao 2 dấu vượt x-height quá nhiều, nhìn mất cân đối. Google Fonts xác nhận chính thức: _"smaller shapes than stand-alone marks can be used to ensure visual balance"_ ([gf-guide/diacritics](https://googlefonts.github.io/gf-guide/diacritics.html)) — tức đây là khuyến nghị thật, không phải suy diễn.

Cách làm — **vẽ riêng outline dẹt hơn, không scale toán học**:

1. Vẽ thêm biến thể `brevecomb.viet` (và tương tự `circumflexcomb.viet`) — outline mới, thấp/dẹt hơn bản gốc, nhưng **giữ nguyên tỷ lệ độ dày nét** như bản gốc. Không dùng scale % dọc trên outline có sẵn — scale tuyến tính làm méo độ cong và làm nét mỏng/dày sai so với phong cách chung của bộ font.
2. Anchor 2 tầng: `a` có `top_viet` → `brevecomb.viet` nhận qua `_top_viet`, đồng thời có `top_viet` riêng (thấp hơn vị trí `top` của bản gốc) để `acutecomb` gắn tiếp lên qua `_top_viet` của nó.
3. Composite `ắ` được ghép tự động từ 3 component: `a` + `brevecomb.viet` + `acutecomb`, theo đúng chuỗi anchor trên.
4. Áp dụng tương tự cho mọi tổ hợp cần chồng 2 tầng: `â/ê/ô` (circumflex) và `ă` (breve) × 5 thanh mỗi loại.
5. Việc này vẫn phải tuân thủ yêu cầu compatible giữa các master ở mục 2.2 — vẽ đủ ở mọi master, không chỉ 1 lần.

Áp dụng logic tương tự cho chữ hoa: dấu trên chữ hoa cần **rộng hơn, thấp hơn, dẹt hơn** so với chữ thường — dùng đúng pattern `.case` đã có sẵn trong font (`acutecomb.case`, `circumflexcomb.case`...), không scale từ bản chữ thường.

### 2.5. Ơ/Ư — vẽ horn qua component hay vẽ hẳn glyph riêng

Có 2 cách, cả hai đều được Google chấp nhận (Google không quy định cách nào, chỉ quan tâm kết quả qua được QA):

- **Component + anchor** (nhanh, dùng để thử nghiệm/nháp sớm): vẽ 1 `horn` component, gắn vào `o`/`u` qua anchor như mọi mark khác.
  - Rủi ro đã được cộng đồng ghi nhận thực tế: dùng Automatic Alignment cho horn dễ bị **overlap và sidebearing sai** ở các weight đậm, vì horn cần "hàn" liền vào bụng/thân chữ chứ không chỉ đặt cạnh (xem thảo luận thực tế tại [Glyphs Forum](https://forum.glyphsapp.com/t/horn-diacritics-and-sidebearings/3563)).
- **Vẽ hẳn glyph riêng** (khuyến nghị cho bản phát hành chính thức): vẽ `Ohorn`, `ohorn`, `Uhorn`, `uhorn` như 4 glyph độc lập, outline hoàn chỉnh ở mọi master — cho phép horn hoà liền vào thân chữ đúng theo từng weight, tránh vấn đề overlap nêu trên.
  - Vẫn giữ anchor `top`/`top_viet` bình thường trên 4 glyph này, để 10 chữ ghép dấu thanh còn lại (`ớ ờ ở ỡ ợ`, `ứ ừ ử ữ ự` + bản hoa) vẫn tự ghép qua component+anchor như bình thường — không phải vẽ tay toàn bộ 20 chữ đó, chỉ 4 chữ gốc cần vẽ full outline.

### 2.6. Sinh composite glyphs tự động

Để Glyphs/glyphsLib tự dựng các glyph ghép (`uni1EA0`...`uni1EF9`) từ base + accent qua anchor đã thiết lập ở 2.3–2.5, không vẽ tay từng ký tự ghép riêng lẻ.

## 3. Cập nhật metadata trong source

- Thêm bit **9 (Vietnamese)** vào `unicodeRanges` trong `customParameters` của cả `DMSans.glyphs` và `DMSans-Italic.glyphs`:

  ```
  value = (0, 1, 2, 3, 5, 9, 31, 32, 33, 35, 36, 38, 45, 60, 62);
  ```

  Đây là yêu cầu của spec OS/2 table (OpenType) nói chung — không thuộc fontbakery `glyph_coverage` check — nhưng cần để hệ điều hành/trình duyệt/ứng dụng nhận diện đúng font có hỗ trợ Vietnamese. Inter (font tham khảo) đã bật bit này.

- Không cần sửa `Sans/Source/config.yaml` — `sources`, `axisOrder`, `stat` giữ nguyên vì không thêm trục mới, chỉ thêm glyph vào 2 nguồn đã khai báo sẵn.

## 4. Build

Dùng đúng pipeline hiện có của repo, không đổi gì:

```sh
cd Sans/Source
gftools builder config.yaml
```

Lệnh này build lại toàn bộ: variable font (`Sans/fonts/variable/`), static instances (`ttf/`, `otf/`), và webfont (`webfonts/`), giờ đã bao gồm glyph tiếng Việt.

## 5. QA theo chuẩn Google Fonts

Bắt buộc chạy đủ 3 bước sau trước khi coi font là "hỗ trợ tiếng Việt":

1. **`fontbakery check-googlefonts fonts/variable/*.ttf`** — chạy đúng profile Google Fonts dùng để duyệt font. Quan trọng nhất:
   - `com.google.fonts/check/glyph_coverage` — xác nhận đủ glyph theo `GF_Latin_Vietnamese`.
   - Các check liên quan `mark`/`mkmk` GPOS — xác nhận anchor gắn đúng, không lỗi vị trí.

2. **Kiểm tra shaping thực tế bằng `hb-shape`** với văn bản mẫu tiếng Việt đầy đủ dấu, đặc biệt tổ hợp dấu đôi khó (ẫ, ề, ộ, ử, ẵ, ẫu, ẩy):

   ```sh
   hb-shape "Sans/fonts/variable/DMSans[opsz,wght].ttf" "Tiếng Việt: ẫ ề ộ ử ẵ" --variations=wght=900,opsz=9
   ```

   Chạy ở nhiều instance khác nhau (Thin 9pt, ExtraBlack 40pt, Italic) để đảm bảo mark không lệch khi nội suy giữa các master.

3. **`gftools qa`** (diffenator2/diffbrowsers) — so sánh trực quan trước/sau khi thêm glyph tiếng Việt, để phát hiện lỗi nội suy hoặc regression ở các glyph không liên quan. Có thể dùng `Reference/Inter-Variable.ttf` làm đối chứng hiển thị song song.

## Tóm tắt các bước

| Bước | Nội dung                                                                                            | Ai làm        |
| ---- | --------------------------------------------------------------------------------------------------- | ------------- |
| 1    | Lấy glyph-list `GF_Latin_Vietnamese` + đối chiếu Inter → checklist 90 glyph                         | Kỹ thuật      |
| 2    | Vẽ mark, horn, dấu chồng thu nhỏ, anchor (`top_viet`/`_top_viet`) trong Glyphs/FontLab, ở đủ master | Type designer |
| 3    | Thêm bit 9 vào `unicodeRanges` trong `.glyphs`                                                      | Kỹ thuật      |
| 4    | `gftools builder config.yaml`                                                                       | Kỹ thuật      |
| 5    | fontbakery + hb-shape + gftools qa                                                                  | Kỹ thuật/QA   |

## Ghi chú xác minh nguồn

Các phần đã đối chiếu trực tiếp với tài liệu chính thức của Google (không phải suy diễn):

- Glyph-set `GF_Latin_Vietnamese`, yêu cầu `GF_Latin_Core` làm nền — [googlefonts/glyphsets](https://github.com/googlefonts/glyphsets).
- Anchor 2 tầng và khuyến nghị thu nhỏ dấu chồng (`top_viet`/`_top_viet`, "smaller shapes for stacked marks") — [gf-guide/diacritics](https://googlefonts.github.io/gf-guide/diacritics.html).
- `glyph_coverage` check — [fontbakery googlefonts profile](https://fontbakery.readthedocs.io/en/latest/fontbakery/profiles/googlefonts.html).

Các phần là kinh nghiệm thiết kế chung, Google không quy định bắt buộc:

- Chọn vẽ horn standalone hay qua component+anchor (mục 2.5).
- Dùng FontLab 8 thay Glyphs App, dùng script mekkablue để tự động hoá anchor.
