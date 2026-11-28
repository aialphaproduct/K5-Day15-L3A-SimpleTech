# Hoàn thiện các lỗi từ review

**Mục tiêu:** sửa công cụ kiểm và cách báo cáo để bản nộp có thể tái lập, không công nhận thiếu bằng chứng thành đã hoàn tất.

**Thiết kế:** giữ nguyên benchmark, chuẩn CP2, CSV/trace lịch sử và khung chạy. Cổng kiểm tách tiêu chí từng câu khỏi điều kiện metric. Báo cáo chi phí mới định nghĩa task là một câu hỏi, lọc tỷ lệ đạt theo đúng nhóm đầu vào mô phỏng và không gán chất lượng model nhỏ cho model lớn. Dùng Python 3.10+, thư viện chuẩn; Flask chỉ cần cho web.

## Công việc

- [x] Viết test rồi sửa `eval/gate.py`: từ chối lượt thiếu/trùng/lạ ID, dữ liệu không hợp lệ; kiểm riêng trích dẫn CP2 và ghi rõ phần cần người chấm. 12 test gate và 5 test improve đạt; lượt 3/5 bị chặn đúng.
- [x] Viết test rồi thêm `cost/audit.py`: đọc artifact đã lưu, tính USD/câu hỏi và 3 quy mô, kiểm model/token/mẫu số; chỉ xuất báo cáo mới. 10 test đạt sau hai lỗi P2 được review, sửa và review lại.
- [x] Đồng bộ README và tài liệu hoàn thiện, thêm hướng dẫn môi trường; không biến các reflection nháp thành tự thuật đã xác nhận. Có `docs/reproduce.md`, báo cáo chi phí và PDF 18 trang cập nhật.
- [x] Chạy test, kiểm toán và đối chiếu hash 21 artifact được bảo vệ; nhờ agent khác review. **50/50 test không phụ thuộc Flask đạt; 21/21 hash giữ nguyên.** Kết quả và giới hạn được cập nhật trong `docs/finalization.md`.

**Trạng thái:** phần sửa công cụ/tài liệu và review hoàn tất; kiểm chứng web/AI thật còn bị giới hạn bởi môi trường. Toàn bộ discover có 53 mục, 50 đạt và 3 module lỗi import vì thiếu Flask. Cài pip thất bại, chưa có key; không công bố toàn bộ test đạt hoặc đã chạy lượt AI thật mới. Không commit/push. Các điều kiện cần người thật vẫn mở, không thuộc trạng thái hoàn tất của bốn bước sửa mã/tài liệu trên.

## Giới hạn

- Không tạo phỏng vấn, khảo sát, xác nhận video hay điểm chấm người giả.
- Không sửa chuẩn/đáp án hoặc chạy fake để bổ sung kết quả AI thật.
- Không commit/push hay đóng issue trong đợt sửa này.
- B06 mâu thuẫn giữa tiêu chí từng câu và metric trích dẫn: công khai, không sửa hồi tố.
- Thiếu key hoặc phụ thuộc phải báo đúng giới hạn môi trường.
