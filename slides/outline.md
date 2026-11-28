# Dàn slide → lấy số từ file nào

> Làm ở guide bước 5.1. Luật: **không có bằng chứng thì không có slide** — mỗi trang ≥1 con số / trích dẫn có nguồn / kết quả đo.
> Xuất PDF thành `demo-slides.pdf` ở thư mục gốc repo, nộp tại CP4 14:30 Thứ Bảy 28/11. Định dạng nào cũng được (PDF, PPTX, HTML…); hoặc nộp link slide (Drive, Canva, Google Slides…) ở form CP4, để ai có link cũng xem được.

| # | Trang | Có gì | Số lấy từ | Xong |
|---|---|---|---|---|
| 1 | Người dùng & pain | Ai · việc gì · chỗ đau + số và trích dẫn | `evidence/summary.md` | Có nội dung PDF |
| 2 | Vì sao chọn bài này | Impact tự ước tính; ba hướng nhỏ có số được bổ sung hồi cứu | `spec.md` §2 | Có nội dung PDF |
| 3 | Giải pháp | Lát cắt · sơ đồ · mức tự động · lời fallback do code kiểm | `spec.md` §4 | Có nội dung PDF |
| 4 | Demo live | B01 thường, B08 khó, B10 làm hộ; link video dự phòng | `eval/benchmark.csv` | Có kịch bản; cần chạy trực tiếp |
| 5 | **Đánh giá thế nào** | Pass 18/23 → 22/23; lượt 3 mã 8/9 chưa đạt; đúng ý chưa đủ mẫu; nguồn 4/23 | `eval/final-audit.md`, `eval/report.md` | Có nội dung PDF |
| 6 | **Chi phí khi dùng thật** | 3 kịch bản; cấu hình lượt 2; 1 task = 1 câu, tỷ lệ cùng nhóm 19/20, ~$0.000218/câu đạt ước tính | `cost/task-cost-audit.md`, `cost/cost-estimate.md` | Có nội dung PDF |
| 7 | Kết luận | Iterate: chưa đạt chất lượng/nguồn, chưa đo lợi ích thật | `spec.md` §7–§8 | Có nội dung PDF |
| 8 | Nếu có thêm 1 tuần | Sửa truy xuất; xác minh bài; thu nguồn và dùng thử thật | `eval/report.md`, `docs/finalization.md` | Có nội dung PDF |

PDF hiện có 18 trang: tám phần cốt lõi cùng bìa và các trang bổ sung về phiên bản prompt, vận hành, cổng kiểm và đội ngũ. Bản xuất lại trên `feat/final` là thay đổi sau CP4; không khẳng định đây là PDF đã có đúng giờ nộp. Bảng trên xác nhận nội dung đã có, không xác nhận buổi demo đã diễn ra.

**Trước khi lên:** tải repo về một máy khác (hoặc thư mục mới), chạy theo mục "Chạy trong 3 phút" của `README.md` · `.env` có trên máy demo, đã gọi thử 1 câu trong vòng 1 giờ trước giờ demo · video dự phòng mở được bằng cửa sổ ẩn danh · biết bản chạy thử sẽ làm gì với **1 câu thử lạ** của giám khảo.

Phân vai đề xuất theo `TEAMS.md` (mỗi người ≥1 phần; nhóm xác nhận trước khi trình bày):

| Trang | Người nói |
|---|---|
| Pain, hướng chọn và nguồn | Nguyễn Hoa Thanh Tùng |
| Luồng trợ giảng, đoạn bài và lỗi truy xuất | Vũ Trí Dũng |
| Đánh giá, metric và chi phí | Khổng Tiến Dương |
| Demo, vận hành, kết luận và điều phối hỏi đáp | Lưu Thanh Mỹ |
