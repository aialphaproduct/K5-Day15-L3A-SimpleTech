# Kiểm toán nguồn — bản hoàn thiện cuối ngày 28/11/2026

Mục đích: phân biệt nguồn quan sát được, lời nhóm ghi nhận và nguồn đang tranh chấp. Không thay nội dung benchmark hay kết quả lịch sử; không biến bản nháp thành phỏng vấn thật chỉ bằng đổi nhãn.

| Nguồn | Có gì kiểm được trong repo/lịch sử | Cách dùng ở bản cuối |
|---|---|---|
| Nhật ký BTC `data/preclass/` | README BTC mô tả dữ liệu hành vi thật đã ẩn danh; đếm lại 1.260 dòng chat, 1.091 câu hỏi trợ giảng, 143 người | Nguồn hành vi chính; không suy ra chất lượng câu trả lời |
| Khảo sát `survey/result-survey1.md` | 17 dòng trả lời có thời điểm, vai và các câu trả lời; 15 học viên, 2 lab coach | Nguồn kiểm chéo nhỏ; chưa đạt ngưỡng 20 người ngoài nhóm, file ẩn danh không tự chứng minh điều kiện ngoài nhóm |
| P1 | Bản ghi khảo sát dòng 3 trùng trích dẫn và phản hồi trong `interviews/P1.md` | Dùng lời về thuật ngữ và công tìm bài; không đếm P1 lần nữa như một người độc lập với khảo sát. Thời điểm/tần suất còn chờ xác nhận |
| P2 | `interviews/P2.md`, commit `28f0d38`: ví dụ câu hỏi, cách xoay xở, 6–7 phút, một lời trích | Ví dụ người dùng được nhóm ghi nhận; câu B20/B21 có chỗ đối chiếu |
| P3 | `summary.md` và `spec.md` xác định là tự thuật thành viên nhóm; benchmark B18/B19 trỏ về P3 | Giữ làm tình huống thử của nhóm; không dùng để chứng minh ngưỡng nguồn người dùng ngoài nhóm hay thời gian tiết kiệm |
| P4 | Commit `fe63ef6` ngày 27/11 18:44:41 +07:00 ghi rõ “dữ liệu giả lập … chưa phải bản ghi phỏng vấn học viên thật”; commit `5275583` 18:54:51 đổi sang lời xác nhận của nhóm | Ngày 28/11 sau CP4, nhóm xác nhận lại đây là phỏng vấn thật. Chưa có ghi chép gốc/xác nhận độc lập nên số đã công bố giữ nguyên, chưa cộng P4 (xem mục dưới); giữ lịch sử |
| B17 | Commit `a36ef5a` 27/11 18:01:25 thêm dòng có nhãn `nguoi_dung`, chưa có mã người/ghi chép gốc | Chưa đủ căn cứ độc lập để bảo đảm nguồn người dùng thật; cần bổ sung bản ghi ẩn danh hoặc dẫn nguồn gốc |

## Hệ quả cho tỷ lệ nguồn benchmark

Bộ lịch sử 23 câu ghi nhãn `nguoi_dung` cho chín câu B15–B23. B15/B16 đối chiếu P1, B20/B21 đối chiếu P2: **4/23 câu có nguồn người dùng có bản ghi đang được chấp nhận**. B17 chưa đủ hồ sơ; B18/B19 thuộc thành viên nhóm; B22/B23 dựa vào P4, nhóm đã xác nhận lại sau CP4 nhưng chưa có ghi chép gốc. Nếu người chấm chấp nhận xác nhận này thì là **6/23 câu**. Mốc ≥1/3 của 23 câu cần ít nhất **8 câu**. Không dùng nhãn 9/23 để khẳng định đã đáp ứng tiêu chí nguồn sau kiểm toán.

Nếu nhóm bổ sung xác nhận nguồn, cần ghi ngày xác nhận thật, ai giữ bản ghi và vị trí trích tương ứng, giữ ẩn danh người tham gia. Việc bổ sung sau CP4 không được trình bày như đã có từ CP2/CP4. Câu thử bổ sung cần tách phiên bản và chạy lượt mới; không sửa đáp án/kết quả lịch sử để đạt tỷ lệ.

## Giới hạn không thể sửa bằng tài liệu

- File giả thuyết và phương pháp chọn mẫu trước đợt hoàn thiện còn là mẫu trống; không có bằng chứng đăng ký trước từ hai file này.
- Khảo sát chưa đủ 20, phỏng vấn ngoài nhóm chưa đủ ba bản ghi được chấp nhận.
- Chưa có log dùng thử của ít nhất hai người ngoài nhóm cho bonus. Không thay bằng người giả lập hay vai diễn AI.
- Xác nhận người ngoài nhóm, phỏng vấn bổ sung và trải nghiệm dùng thử cần người thật cung cấp; không tự tạo để hoàn thiện hồ sơ.
