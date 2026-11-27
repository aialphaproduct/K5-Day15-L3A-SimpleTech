# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Khung code bản chạy thử A1 (`codebase/tools.py`, `codebase/agent.py`) | Claude (bản nháp) | Viết khung tìm đoạn và luồng chặn khi không có mã đoạn | Nhóm đọc, chạy thử, sửa theo thiết kế | (nhóm điền) |
| Đếm bằng chứng (`evidence/count_tutor.py`) | Claude (viết script) | Viết script đếm; số ra `evidence/tutor_counts.txt` | Nhóm chạy lại và đối chiếu số | (nhóm điền) |
| Bản nháp spec, metric, câu thử | Claude | Viết bản đầu | Nhóm sửa; câu thử `tu_viet` chưa kiểm với học viên thật | (nhóm điền) |
| Đoạn bài mẫu (`data/lessons/passages.csv`) | Claude | Viết 5 đoạn **giả** để chạy thử | **Phải thay** bằng đoạn bài thật đã viết lại | (nhóm điền) |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).
