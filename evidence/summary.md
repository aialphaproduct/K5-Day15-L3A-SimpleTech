# Bằng chứng pain — A1 Trợ giảng bài học

> Số lấy từ `data/preclass/chat.csv` bằng `evidence/count_tutor.py` (chạy lại được; kết quả đầy đủ ở `evidence/tutor_counts.txt`). Không có tên, không có nội dung câu hỏi. Dữ liệu ẩn danh, 05/11 → 25/11/2026.

## Số đo từ data

| Chỉ số | Giá trị |
|---|---|
| Câu hỏi gửi trợ giảng AI dưới video | 1.091 câu |
| Học viên có ≥1 câu hỏi | 143 học viên |
| Học viên chỉ hỏi đúng 1 câu | 38 (26,6%) |
| Median câu hỏi / học viên | 4 (max 72) |
| Top 10% học viên hỏi nhiều nhất | 43,3% câu hỏi |
| Câu hỏi ở Day01 | 333 (31%) |
| 3 video Day01 có nhiều câu hỏi nhất | 269 câu (25%) |
| Câu có dòng ghi rõ đoạn bài AI đã dựa vào (`ngu_canh`) | 9 / 1.091 |
| Câu có dùng gợi ý đã duyệt | 45,1% |

## Đọc số thế nào

- **Câu hỏi tập trung ở đầu khoá và vài video.** Day01 có nhiều câu nhất; ba video đầu của Day01 chiếm một phần lớn. Chưa biết vì sao (bài khó, video không rõ, hay chỉ là nhiều học viên mới). Cần phỏng vấn học viên để biết.
- **Một nhóm nhỏ hỏi rất nhiều.** 10% học viên hỏi gần nửa số câu. Chưa rõ họ là người cần giúp nhất hay đang dùng trợ giảng thay cho việc đọc bài.
- **Gần như không ghi được đoạn bài AI đã dựa vào.** Chỉ 9/1.091 dòng có `ngu_canh`. Nghĩa là hiện không ai kiểm lại được câu trả lời có căn cứ trong bài hay không. Đây là lý do thiết kế đòi mã đoạn trong mỗi câu trả lời.
- **Data không có nội dung câu hỏi và câu trả lời.** Không đo được chất lượng câu trả lời từ data. Chất lượng phải đo bằng bộ câu thử (`eval/benchmark.csv`) và người chấm.

## Giới hạn: chưa đủ làm bằng chứng

- Đã ghi nhận [phỏng vấn P1](interviews/P1.md). Ở câu 8, P1 cho biết phải tra thêm thuật ngữ mới đọc tiếp được lời giải. Bản ghi chưa có nguyên văn câu hỏi P1 từng gửi dưới video.
- Trong [phỏng vấn P3](interviews/P3.md), học viên kể đã nhận câu trả lời sau khoảng 30 giây rồi dành thêm khoảng 5 phút để đối chiếu với một AI khác. B18 lấy từ thắc mắc về cách AI hoạt động, B19 lấy từ trải nghiệm kiểm chứng này.
- [P4](interviews/P4.md) kể đã tua lại video 2–3 lần để tìm căn cứ cho lời giải, và hỏi TA qua Discord khi chưa rõ quy định nộp lab trễ. Hai câu hỏi trong mục Ghi chép được dùng cho B22–B23.
- Ngày 10–13 có ít câu hỏi; có thể do ít học viên hơn chứ không phải do học viên ít cần hỏi.
- Không có dữ liệu về câu trả lời đúng hay sai, nên chưa biết trợ giảng đang sai ở đâu.
