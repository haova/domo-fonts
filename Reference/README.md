# Font tham khảo

`Inter-Variable.ttf` — tải từ [google/fonts](https://github.com/google/fonts/blob/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf) (giấy phép OFL), dùng làm tham khảo kỹ thuật khi việt hoá DM Sans.

Lý do chọn Inter thay vì Lexend/Manrope (đã thử và loại):

|                     | DM Sans   | Inter     | Lexend   | Manrope  |
| ------------------- | --------- | --------- | -------- | -------- |
| Axes                | opsz+wght | opsz+wght | chỉ wght | chỉ wght |
| Named instances     | 9         | 9         | 9        | 7        |
| Vietnamese coverage | 6/90      | 90/90     | 90/90    | 90/90    |

Inter là font duy nhất cùng cấu trúc 2 trục `opsz`+`wght` như DM Sans — phù hợp để tham khảo cách xử lý mark/anchor tiếng Việt khi nội suy qua cả optical size lẫn weight.

**Chỉ dùng để tham khảo kỹ thuật (glyph checklist, tên anchor, tỷ lệ) — không copy outline.** Xem `VIET_HOA.md` mục 1 để biết cách dùng.
