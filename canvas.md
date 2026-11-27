# Canvas CP2 — Simple Tech · L3A · Track A (EdTech)

| # | Dòng | Nhóm điền |
|---|---|---|
| 1 | Track và bài toán | Track A (EdTech), đề A1. Trợ giảng AI giải đáp câu hỏi về nội dung video pre-class ngay dưới video. |
| 2 | Người dùng chính | Học viên AI20K đang tự học trước buổi lên lớp, cần hỏi lại một ý vừa xem và mở đúng đoạn video để kiểm tra lời giải thích. |
| 3 | Vấn đề | Khi hỏi lại kiến thức trong video, học viên khó tìm đúng đoạn để kiểm chứng câu trả lời và có thể hiểu sai bài nếu lời giải thích thiếu căn cứ. |
| 4 | Bằng chứng đầu | Từ 05/11 đến 25/11/2026, 143 học viên gửi 1.091 câu hỏi. Chỉ 9/1.091 lượt có ghi đoạn bài làm căn cứ trong trường `ngu_canh`. P4 kể: “Nó trả lời nghe cũng xuôi tai đấy, nhưng không chỉ rõ đoạn nào trong video nói thế nên mình vẫn phải tự tua lại tìm, mất công gấp đôi.” [Số đếm](evidence/tutor_counts.txt) · [Phỏng vấn P4, câu 8](evidence/interviews/P4.md) |
| 5 | Lát cắt đã chốt | Khi học viên hỏi một câu dưới video, trợ giảng tìm căn cứ trong bài rồi trả lời kèm mã đoạn để học viên mở lại kiểm chứng, hoặc báo “Không có trong bài” nếu thiếu căn cứ. |
| 6 | Mức tự động và lý do | Trước khi hiển thị lời giải, hệ thống kiểm tra mã trích dẫn có thuộc các đoạn vừa tìm hay không. Khi thiếu căn cứ hoặc mã trích dẫn không hợp lệ, hệ thống báo “Không có trong bài” và gợi ý học viên tự liên hệ trợ giảng phụ trách (TA). Bước này giúp học viên tránh hiểu sai bài hoặc tin nhầm hạn nộp. [Thiết kế §4](spec.md) |
| 7 | Phân công có tên | Lưu Thanh Mỹ phụ trách giao diện, khảo sát và demo. Nguyễn Hoa Thanh Tùng phân tích bằng chứng, lập data card và soạn câu thử. Vũ Trí Dũng chuẩn bị đoạn bài, nối mô hình và xây luồng trả lời. Khổng Tiến Dương đánh giá câu trả lời và mô phỏng chi phí. [Phân công chi tiết](TEAMS.md) |
| — | Đã đổi gì so với CP1 | Bổ sung lời kể của P4 về việc phải tua lại video để kiểm chứng. Chốt cách xử lý khi thiếu căn cứ: học viên nhận thông báo ngay dưới video và tự quyết định có hỏi TA hay không. |
