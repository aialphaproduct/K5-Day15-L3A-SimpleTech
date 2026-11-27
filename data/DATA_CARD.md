# Data card — dữ liệu bản chạy thử (A1 Trợ giảng bài học)

## Dataset 1 · Nhật ký pre-class (chỉ dùng để đếm bằng chứng)

| | |
|---|---|
| Dùng để làm gì | đào bằng chứng pain (`evidence/summary.md`). **Không** đưa vào bản chạy thử |
| Từ đâu | data BTC cấp: `data/preclass/` trong repo đề (không copy vào repo này) |
| Xử lý những bước gì | đếm câu hỏi trợ giảng AI từ `chat.csv` bằng `evidence/count_tutor.py`; không mở nội dung (data không có nội dung) |
| Số dòng / số đoạn | 1.260 dòng chat · 1.091 câu hỏi trợ giảng |
| Phiên bản / ngày lấy | 05/11 → 25/11/2026 |
| Nhãn | thật (đã ẩn danh bởi BTC) |
| Giới hạn | không có nội dung câu hỏi/trả lời; `ngu_canh` gần như trống; ngày 10–13 ít dòng |

## Dataset 2 · Đoạn bài cho trợ giảng (`data/lessons/passages.csv`)

| | |
|---|---|
| Dùng để làm gì | căn cứ cho công cụ `search_passages` / `get_passage` và bộ câu thử |
| Từ đâu | **GIẢ**: 5 đoạn mẫu nhóm dựng để luồng chạy được trước CP2. **Phải thay** bằng đoạn bài thật đã viết lại (không copy nguyên tài liệu khoá) |
| Xử lý những bước gì | (nhóm điền) lấy đoạn từ bài → viết lại ngắn → gắn mã → kiểm lại từng đoạn có đúng bài không |
| Số dòng / số đoạn | 5 (giả) |
| Nhãn | `synthetic` cho đoạn giả; `tu_viet` cho đoạn nhóm viết lại |
| Giới hạn | đoạn giả không phải nội dung khoá; mọi số đo trên đoạn giả chỉ để kiểm luồng |

## Dataset 3 · Bộ câu thử (`eval/benchmark.csv`)

| | |
|---|---|
| Dùng để làm gì | đo `trich_dung_ma`, `khong_bia`, `dung_y_tra_loi` |
| Từ đâu | `tu_viet`: nhóm soạn 12 câu (6 thuong · 3 kho · 3 tu_choi). **Chưa** có câu từ học viên thật |
| Nhãn | `tu_viet` |
| Giới hạn | cần thêm câu từ phỏng vấn học viên (`nguoi_dung`) để đạt độ phủ |
