# Reflection — Lưu Thanh Mỹ

1. **Vai trò + phần mình làm (trỏ tới file / commit):**
   Mình là đội trưởng, mã học viên `2A202603532`, lo giao diện, demo, slide, khảo sát và triển khai. Giai đoạn đầu mình dựng giao diện web Flask (`2aaf009`), CI (`12f14f2`), bảng phân công trong `README.md`, thêm câu thử từ người dùng B15–B19 (`a36ef5a`, `cef777d`) và biên bản phỏng vấn trong `evidence/interviews/`. Sang CP3–CP4 mình cập nhật khảo sát lên 17 phản hồi (`evidence/survey/`), làm `demo-slides.pdf`, cổng kiểm `eval/gate.py`, bản demo có đo lường và vòng đề xuất prompt (`codebase/`, `demo/`), đưa lên AWS và thử tải (`deploy/`, `loadtest/`).

2. **AI hỗ trợ mình thế nào (việc gì, công cụ gì, chỗ nào phải sửa lại output AI):**
   Mình dùng Claude Code để viết mã demo, soạn tài liệu, slide và thao tác triển khai. Chỗ phải chặn hoặc sửa: AI từng soạn đoạn bài mẫu và gắn nhãn câu hỏi do AI viết là của người dùng, mình dừng việc đẩy lên; AI từng gợi ý dùng tiện ích trên trang pre-class thật, trái luật đề nên bỏ; AI tự merge PR vào `main` khi mình chưa cho phép, phải đưa nhánh về lại và mở PR mới để duyệt. Điểm lượt 4–5 do AI chấm tạm nên còn chờ người xác nhận.

3. **Một câu thử trượt của nhóm và mình học được gì từ nó:**
   `B18` (*"AI chạy như thế nào vậy?"*) đạt ở lượt 2–3 nhưng trượt lại ở lượt 4: sau khi thêm 7 đoạn bài phần 1, câu trả lời lấy `D01-09`, `D01-11` thay vì `GIA-01`. Mình học được rằng thêm dữ liệu cũng là một thay đổi có thể làm tệ đi, nên đổi gì cũng phải chạy lại cả bộ và so với lượt trước. Nhóm giữ nguyên đáp án, ghi lượt 4–5 là chưa đạt và làm cổng kiểm để chặn kiểu tụt này.
