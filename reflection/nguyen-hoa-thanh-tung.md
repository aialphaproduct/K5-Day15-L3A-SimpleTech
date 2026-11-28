# Reflection — Nguyễn Hoa Thanh Tùng

> Bản thảo được biên soạn cuối đợt hoàn thiện `feat/final`, sau các tài liệu và kiểm tra. Phần công việc đối chiếu lịch sử Git; phần trải nghiệm cá nhân cần chính Tùng xác nhận. Không coi bản thảo AI là lời tự thuật đã được tác giả duyệt.

1. **Vai trò + phần mình làm (trỏ tới file / commit):**
   Mình là thành viên nhóm Simple Tech, mã học viên `2A202603519`, phụ trách bằng chứng và chuẩn đo. Mình chỉnh hồ sơ CP1 `canvas.md` (`66ed1a0`), thêm sơ đồ luồng vào `spec.md` (`a356079`), cập nhật hướng dẫn chấm trong `eval/metric_spec.yaml` (`f4f10dd`), đưa và chỉnh các biên bản phỏng vấn cùng câu thử liên quan, `data/DATA_CARD.md`, `evidence/summary.md` (`8f51511`, `d8505ee`, `5275583`), chốt bản CP2 (`3ea187d`), gộp nhánh `develop` và review PR.

2. **AI hỗ trợ mình thế nào (việc gì, công cụ gì, chỗ nào phải sửa lại output AI):**
   Hồ sơ nhóm ghi Claude hỗ trợ bản nháp spec, metric và câu thử; phiên hoàn thiện này dùng Codex để đối chiếu rubric, dữ liệu và lịch sử, bổ sung kiểm toán và sửa tài liệu. Các thay đổi metric ở `f4f10dd` và biên bản ở `8f51511`, `d8505ee`, `5275583` là phần có thể truy lại từ Git. Một thiếu sót của bản nháp đã được chỉ ra rõ là gắn nguồn P3/P4 thành người dùng thật và suy `pass` thành đạt metric; bản cuối tách nguồn chưa xác minh, giữ nguyên chuẩn và các lượt cũ. Repo chưa đủ căn cứ xác định công cụ AI cá nhân Tùng đã trực tiếp dùng hoặc chính Tùng đã sửa lỗi nào; phần này vẫn cần Tùng xác nhận, không gán việc của nhóm hay Codex thành trải nghiệm cá nhân.

3. **Một câu thử trượt của nhóm và mình học được gì từ nó:**
   `B15` (học viên nói có kiểm lại được nhưng mất công tìm) trượt ở cả năm lượt: mong đợi là hỏi lại học viên muốn kiểm ý nào, nhưng trợ giảng tự trả lời và gán `[GIA-05]` hoặc đoạn khác. Lỗi này cho thấy cần viết rõ hành vi kiểm được, gồm hỏi lại và không tự gán mã khi thiếu nội dung. Việc có mã tồn tại trong kho chưa bảo đảm trả lời đúng ý; cũng không được nới tiêu chí để biến câu trượt thành đạt. Đây là phân tích từ `eval/report.md` và `eval/final-audit.md`; cảm nhận và bài học cá nhân cuối cùng cần Tùng đọc, sửa và xác nhận.
