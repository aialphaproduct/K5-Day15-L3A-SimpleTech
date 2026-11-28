# Data card — dữ liệu bản chạy thử (A1 Trợ giảng bài học)

## Dataset 1 · Nhật ký pre-class (chỉ dùng để đếm bằng chứng)

|                      |                                                                                                                   |
| -------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Dùng để làm gì       | đào bằng chứng pain (`evidence/summary.md`). **Không** đưa vào bản chạy thử                                       |
| Từ đâu               | data BTC cấp: `data/preclass/` trong repo đề (không copy vào repo này)                                            |
| Xử lý những bước gì  | đếm câu hỏi trợ giảng AI từ `chat.csv` bằng `evidence/count_tutor.py`; không mở nội dung (data không có nội dung) |
| Số dòng / số đoạn    | 1.260 dòng chat · 1.091 câu hỏi trợ giảng                                                                         |
| Phiên bản / ngày lấy | 05/11 → 25/11/2026                                                                                                |
| Nhãn                 | thật (đã ẩn danh bởi BTC)                                                                                         |
| Giới hạn             | không có nội dung câu hỏi/trả lời; `ngu_canh` gần như trống; ngày 10–13 ít dòng                                   |

## Dataset 2 · Đoạn bài cho trợ giảng (`data/lessons/passages.csv`)

|                     |                                                                                                                                                                                                                                               |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Dùng để làm gì      | căn cứ cho công cụ `search_passages` / `get_passage` (hỗ trợ ngữ cảnh video `hep` / `ca_ngay`) và bộ câu thử                                                                                                                                  |
| Từ đâu              | Nhóm tự viết lại (`tu_viet`, không copy nguyên văn tài liệu khoá) theo danh mục `lesson_id`, `kc_code` và mã video thật (`d01-r1-v01`…`d06-r1-v02`) trong `data/preclass/` (`README.md`, `answers.csv`, `chat.csv`): phủ Day01–Day04 (66% câu hỏi trợ giảng, gồm thêm 8 đoạn Day01 phần 1 & 3 từ PR #56), bổ sung Day05 (30,6% sai bài ôn) và Day06 (44,1% sai bài ôn) cùng 2 `kc_code` sai cao nhất từ phân tích `#39` (`agentic_fit_scoring_decision`, `cot_task_fit`). |
| Xử lý những bước gì | Đối chiếu top video (`tutor_counts.txt`), phân tích tỷ lệ sai bài ôn (`#39`) và danh mục `kc_code` (`answers.csv`) → tóm tắt viết lại mỗi ý kiến thức thành 1 đoạn ngắn → gắn mã đoạn, mã `video`, cột `video_timestamp` và `verify_status` → kiểm không copy nguyên tài liệu và không lộ đáp án câu `kho`. Giữ 5 mã `GIA-01`–`GIA-05` để tương thích bộ câu thử & `metric_spec.yaml` đã chốt ở CP2. |
| Số dòng / số đoạn   | **37 đoạn** (`GIA-01`–`GIA-05`: 5 đoạn nền tảng & quy tắc pre-class; `D01-01`–`D01-16`: 16 đoạn Day01, gồm `D01-09`–`D01-15` phần 1 và `D01-16` phần 3 chờ đối chiếu; `D02-01`–`D02-03`: 3 đoạn Day02; `D03-01`–`D03-03`: 3 đoạn Day03; `D04-01`–`D04-03`: 3 đoạn Day04; `D05-01`–`D05-03`: 3 đoạn Day05; `D06-01`–`D06-04`: 4 đoạn Day06). |
| Trạng thái đối chiếu | **4/37 đoạn** là `quy_tac_he_thong` (`GIA-02`–`GIA-05`, đối chiếu theo `data/preclass/README.md` và `tracks/track-a-edtech.md`); **33/37 đoạn** bài giảng đang ở trạng thái **`chua_doi_chieu_video`** (`D01-09`–`D01-16` có mốc tạm từ lời giảng phần 1/3 chờ người đối chiếu; 25 đoạn còn lại để `video_timestamp = chua_doi_chieu`). |
| Nhãn                | `tu_viet` (toàn bộ 37/37 đoạn; không còn đoạn `nhom_viet_gia` hay `(GIẢ)`)                                                                                                                                                                     |
| Giới hạn            | Mới phủ Day01–Day06 (chưa phủ Day07–Day13 hay chủ đề ML ngoài khoá); cột `video` mới gán theo mã video thật của ngày học trong `chat.csv` và các đoạn `chua_doi_chieu_video` vẫn cần người đối chiếu trực tiếp trên video gốc. |

## Dataset 3 · Bộ câu thử (`eval/benchmark.csv`)

| | |
|---|---|
| Dùng để làm gì | đo `trich_dung_ma`, `khong_bia`, `dung_y_tra_loi` |
| Từ đâu | 23 câu (9 thuong · 11 kho · 3 tu_choi). B01–B14 do nhóm tự soạn. Trong [phỏng vấn P1](../evidence/interviews/P1.md), B15 lấy câu hỏi và phương án trả lời ở câu 7, B16 trích nguyên văn câu 8. B17 được nhóm ghi nhận là câu từ người dùng tại [commit ban đầu](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/commit/a36ef5a29a5268d03995774b0cf5be976fbd4b86), chưa có biên bản để đối chiếu. B18 và B19 diễn đạt lại thắc mắc và cách kiểm chứng của [P3 ở câu 1 và 2](../evidence/interviews/P3.md). B20–B21 đến từ [P2, câu 1 và 4](../evidence/interviews/P2.md). B22–B23 trích nguyên văn hai câu hỏi ở mục Ghi chép của [biên bản phỏng vấn P4](../evidence/interviews/P4.md). Đáp án kỳ vọng và tiêu chí chấm do nhóm biên soạn. |
| Nhãn | `tu_viet` (14), `nguoi_dung` (9). Tám câu có biên bản phỏng vấn để đối chiếu; nguồn của B17 được ghi nhận trong lịch sử Git. |
