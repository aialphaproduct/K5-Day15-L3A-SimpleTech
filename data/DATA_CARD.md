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
| Giới hạn             | không có nội dung câu hỏi/trả lời; `ngu_canh` chỉ bắt đầu ghi từ 25/11, ô trống trước đó không chứng minh thiếu căn cứ; ngày 10–13 ít dòng; cách chọn mẫu được ghi hồi cứu, chưa có bằng chứng đăng ký trước |

## Dataset 2 · Đoạn bài cho trợ giảng (`data/lessons/passages.csv`)

|                     |                                                                                                                                                                                                                                               |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Dùng để làm gì      | căn cứ cho công cụ `search_passages` / `get_passage` và bộ câu thử                                                                                                                                                                            |
| Từ đâu              | Nhóm tự viết lại (`tu_viet`, không copy nguyên văn tài liệu khoá) theo cấu trúc bài học thật (`lesson_id`, `kc_code`) và quy trình học của khoá AI20K K5 trong `data/preclass/` (`README.md`, `answers.csv`, `chat.csv`): tập trung Day01–Day04 (chiếm 66% tổng số câu hỏi trợ giảng) và quy tắc trang pre-class. |
| Xử lý những bước gì | Đối chiếu top bài/video nhiều câu hỏi (`tutor_counts.txt`) và danh mục `kc_code` trong `answers.csv` → tóm tắt viết lại mỗi ý kiến thức thành 1 đoạn ngắn 2 câu → gắn mã đoạn (`GIA-01`–`GIA-05`, `D01-01`–`D04-02`) → kiểm lại không chứa nội dung tài liệu nguyên văn và không lộ đáp án câu `kho`. Giữ 5 mã `GIA-01`–`GIA-05` (đã thay hoàn toàn chữ `(GIẢ)` bằng nội dung viết lại) để tương thích bộ câu thử và `metric_spec.yaml` đã chốt ở CP2. |
| Số dòng / số đoạn   | 28 đoạn (`GIA-01`–`GIA-05`: 5 đoạn nền tảng & quy tắc pre-class; `D01-01`–`D01-16`: 16 đoạn Day01 (`D01-16` viết lại từ lời giảng phần 3, chờ đối chiếu), trong đó `D01-09`–`D01-15` viết lại từ lời giảng phần 1, Claude soạn, chờ người đối chiếu video; `D02-01`–`D02-03`: 3 đoạn Day02; `D03-01`–`D03-02`: 2 đoạn Day03; `D04-01`–`D04-02`: 2 đoạn Day04)                                          |
| Nhãn                | `tu_viet` (toàn bộ 28/28 đoạn; không còn đoạn `nhom_viet_gia` hay `(GIẢ)`)                                                                                                                                                                     |
| Giới hạn            | Mới bao phủ Day01–Day04 và quy tắc chung pre-class, chưa phủ Day05–Day13. **Tám đoạn `D01-09`–`D01-16` còn chờ người đối chiếu video**, chưa chứng thực nội dung, không suy rằng mã hợp lệ bảo đảm ý đúng. Tìm theo từ khoá có thể lấy nhầm đoạn nên câu ngoài kho chưa chắc luôn được nhận diện đúng; xem lỗi trong `eval/report.md`. |

## Dataset 3 · Bộ câu thử (`eval/benchmark.csv`)

| | |
|---|---|
| Dùng để làm gì | đo `trich_dung_ma`, `khong_bia`, `dung_y_tra_loi` |
| Từ đâu | 23 câu (9 thuong · 11 kho · 3 tu_choi). B01–B14 do nhóm tự soạn. Trong [phỏng vấn P1](../evidence/interviews/P1.md), B15 lấy câu hỏi và phương án trả lời ở câu 7, B16 trích nguyên văn câu 8. B17 được nhóm ghi nhận là câu từ người dùng tại [commit ban đầu](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/commit/a36ef5a29a5268d03995774b0cf5be976fbd4b86), chưa có biên bản để đối chiếu. B18 và B19 diễn đạt lại thắc mắc và cách kiểm chứng của [P3 ở câu 1 và 2](../evidence/interviews/P3.md). B20–B21 đến từ [P2, câu 1 và 4](../evidence/interviews/P2.md). B22–B23 trích nguyên văn hai câu hỏi ở mục Ghi chép của [biên bản phỏng vấn P4](../evidence/interviews/P4.md). Đáp án kỳ vọng và tiêu chí chấm do nhóm biên soạn. |
| Nhãn lịch sử | File gốc giữ `tu_viet` (14), `nguoi_dung` (9) để bảo toàn bộ CP2 và các lượt đã chạy. **Nhãn không đồng nghĩa đã xác minh nguồn**: chỉ 4/23 câu B15/B16/B20/B21 đối chiếu bản ghi P1/P2 đang được chấp nhận; B18/B19 từ thành viên nhóm P3, B22/B23 dựa vào P4 từng là bản nháp giả lập, B17 chưa có bản ghi gốc. Xem [kiểm toán nguồn](../evidence/source-audit.md). |
| Điều kiện đánh giá | 9 câu thường hiện chưa đủ mẫu 20 câu thường của `dung_y_tra_loi`; ≥1/3 nguồn người dùng thật chưa chứng minh. Không sửa input/expected/tiêu chí hay kết quả lịch sử để đạt chuẩn; xem [kiểm toán cuối](../eval/final-audit.md). |

## Dataset 4 · Bộ bổ sung giữ kín tương đối (`eval/benchmark_heldout.csv`)

- **Mục đích và quy mô:** 15 câu: 7 thường, 5 khó, 3 từ chối; dùng kiểm tra cách diễn đạt khác, không cộng vào bộ 23 câu để che kết quả cũ.
- **Nguồn/cách sinh:** Claude soạn nháp từ kho 20 đoạn `passages.csv` sau khi đã đọc code và bộ 23 câu cũ. Nhãn file là `sinh_seed` nhưng **không tìm thấy seed số hay quy trình sinh tất định được ghi lại**, nên chưa đáp ứng điều kiện tái sinh bằng seed. Không tự điền seed sau khi đã sinh.
- **Giới hạn:** không phải câu thu mới từ người dùng, không kín hoàn toàn với người tạo câu; không tính vào tỷ lệ nguồn người dùng thật. Đã dùng trong vòng kiểm prompt nên không tiếp tục gọi là bộ chưa từng xem. Nội dung và lượt chạy lịch sử giữ nguyên.
- **Kết quả lịch sử:** `run-heldout.csv`, 13/15 theo `pass`, model `gemini-3.1-flash-lite`, run ID `run-1@20261128-085312`; chi tiết và hash LF trong `eval/report.md`.

## Hồ sơ nguồn bổ sung

Khảo sát gốc có 17 dòng phản hồi trong `evidence/survey/result-survey1.md`; P1 trùng dòng 3 nên không tính thành một người khác khi kết hợp nguồn. Nhật ký BTC không chứa câu chữ người dùng. Trích dẫn khảo sát đã ẩn danh chỉ đưa vào bộ thử theo mục đích đánh giá; không kèm danh tính/liên hệ hay sao chép toàn bộ data pack. Các nguồn P3/P4/B17 được công khai riêng ở `evidence/source-audit.md`; việc kiểm toán không xác nhận thay người tham gia.
