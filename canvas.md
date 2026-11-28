# Canvas — bản cập nhật cuối · Simple Tech · L3A · Track A (EdTech)

> Cập nhật ngày 28/11/2026 sau CP4. Bản CP2 nằm trong lịch sử Git (commit `3ea187d`); bản này sửa diễn giải bằng chứng, không ghi đè nội dung đã nộp tại thời điểm CP2.

| # | Dòng | Nhóm điền |
|---|---|---|
| 1 | Track và bài toán | Track A (EdTech), đề A1. Học viên tự xem video pre-class, gặp một ý chưa hiểu và mất công tìm đúng đoạn để kiểm lại lời giải thích. |
| 2 | Người dùng chính | Học viên AI20K đang tự học trước buổi lên lớp, cần hỏi lại một ý vừa xem và mở đúng đoạn video để kiểm tra lời giải thích. |
| 3 | Vấn đề | Khi hỏi lại kiến thức trong video, học viên khó tìm đúng đoạn để kiểm chứng câu trả lời và có thể hiểu sai bài nếu lời giải thích thiếu căn cứ. |
| 4 | Bằng chứng hiện có | Từ 05/11 đến 25/11/2026, 143 học viên gửi 1.091 câu hỏi. Khảo sát có 15/17 phản hồi không kiểm lại được hoặc mất công tìm, riêng học viên là 14/15. P1 nói: “Câu trả lời dùng những thuật ngữ mình chưa biết, khiến mình cần phải tìm hiểu thuật ngữ đó rồi mới tiếp tục đọc để hiểu câu trả lời.” Nhật ký không có nội dung hỏi/đáp nên không đo được chất lượng; khảo sát chưa đủ 20 người. [Tổng hợp và giới hạn](evidence/summary.md) · [Kiểm toán nguồn](evidence/source-audit.md) |
| 5 | Lát cắt đã chốt | Khi học viên hỏi một câu dưới video, trợ giảng tìm căn cứ trong bài rồi trả lời kèm mã đoạn để học viên mở lại kiểm chứng, hoặc báo “Không có trong bài” nếu thiếu căn cứ. |
| 6 | Mức tự động và lý do | Trước khi hiển thị lời giải, hệ thống kiểm tra mã trích dẫn có thuộc các đoạn vừa tìm hay không. Khi thiếu căn cứ hoặc mã trích dẫn không hợp lệ, hệ thống báo “Không có trong bài” và gợi ý học viên tự liên hệ trợ giảng phụ trách (TA). Bước này giúp học viên tránh hiểu sai bài hoặc tin nhầm hạn nộp. [Thiết kế §4](spec.md) |
| 7 | Phân công có tên | Lưu Thanh Mỹ phụ trách giao diện, khảo sát và demo. Nguyễn Hoa Thanh Tùng phân tích bằng chứng, lập data card và soạn câu thử. Vũ Trí Dũng chuẩn bị đoạn bài, nối mô hình và xây luồng trả lời. Khổng Tiến Dương đánh giá câu trả lời và mô phỏng chi phí. [Phân công chi tiết](TEAMS.md) |
| — | Đã đổi gì so với CP1 | Bổ sung lời kể của P4 về việc phải tua lại video để kiểm chứng. Chốt cách xử lý khi thiếu căn cứ: học viên nhận thông báo ngay dưới video và tự quyết định có hỏi TA hay không. |
| — | Đã sửa trong bản cuối | Không dùng trường `ngu_canh` để kết luận trợ giảng thiếu căn cứ; chưa dùng P4 làm nguồn thật khi còn thiếu xác minh. Thay bằng số khảo sát có log và lời P1; công khai giới hạn mẫu và việc ghi phương pháp hồi cứu. |
