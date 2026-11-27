# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Khung code bản chạy thử A1 (`codebase/tools.py`, `codebase/agent.py`) | Claude (bản nháp) | Viết khung tìm đoạn và luồng chặn khi không có mã đoạn | Nhóm đọc, chạy thử, sửa theo thiết kế | (nhóm điền) |
| Đếm bằng chứng (`evidence/count_tutor.py`) | Claude (viết script) | Viết script đếm; số ra `evidence/tutor_counts.txt` | Nhóm chạy lại và đối chiếu số | (nhóm điền) |
| Bản nháp spec, metric, câu thử | Claude | Viết bản đầu | Nhóm sửa; câu thử `tu_viet` chưa kiểm với học viên thật | (nhóm điền) |
| Đoạn bài mẫu (`data/lessons/passages.csv`) | Claude / Antigravity | Viết 5 đoạn giả ban đầu; hỗ trợ soạn lại 20 đoạn ngắn `tu_viet` theo danh mục `lesson_id` & `kc_code` Day01–Day04 | Vũ Trí Dũng rà soát từng đoạn khớp chủ đề khoá, kiểm không copy nguyên tài liệu, cập nhật `data/DATA_CARD.md` | Vũ Trí Dũng |
| Nối model API (`codebase/ai.py`) | Antigravity | Hỗ trợ viết nhánh gọi API thật (OpenAI, Gemini, Anthropic, Ollama, OpenAI-compatible) bằng `urllib`, thêm retry lỗi mạng/429/503 và lấy token từ `usage` | Vũ Trí Dũng tạo `.env`, chạy thử `run.py eval --try` với `gemini-3.1-flash-lite` xác nhận 3/3 câu có token > 0 | Vũ Trí Dũng |
| Cải tiến truy xuất, prompt và báo cáo eval (`codebase/tools.py`, `codebase/agent.py`, `eval/report.md`) | Antigravity | Hỗ trợ phân tích lỗi lượt 1, cải tiến IDF/phân biệt dấu trong `tools.py`, cập nhật prompt 4 đường đi trong `agent.py` và tổng hợp `eval/report.md` | Vũ Trí Dũng chạy lượt 1 (`18/23`) và lượt 2 (`22/23`), rà từng dòng chấm `pass` và xác nhận `run.py score` | Vũ Trí Dũng |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).
