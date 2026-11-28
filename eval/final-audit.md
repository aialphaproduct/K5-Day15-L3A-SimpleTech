# Kiểm toán kết quả đã lưu theo chuẩn CP2

Lệnh: `python eval/audit.py`. Không gọi model, không sửa bộ thử, chuẩn chấm, output hay điểm lịch sử.

## Nguồn câu thử

- Nhãn nguồn người dùng/data thật trong benchmark: **9/23 (39.1%)**.
- Nguồn ngoài nhóm có hồ sơ xác minh trong `eval/source-audit.csv`: **4/23 (17.4%)**; cần ít nhất **8/23** (≥1/3).
- Trạng thái phần nguồn: **chưa đủ nguồn được xác minh**. Nhãn `nguoi_dung` tự thân không xác nhận nguồn.

| ID cần lưu ý | Trạng thái xác minh | Hồ sơ |
|---|---|---|
| B17 | unverified | commit a36ef5a chưa có ghi chép gốc |
| B18 | member | evidence/interviews/P3.md là thành viên nhóm theo evidence/summary.md |
| B19 | member | evidence/interviews/P3.md là thành viên nhóm theo evidence/summary.md |
| B22 | unverified | evidence/interviews/P4.md nhóm xác nhận sau CP4; chưa có ghi chép gốc; fe63ef6 từng ghi giả lập |
| B23 | unverified | evidence/interviews/P4.md nhóm xác nhận sau CP4; chưa có ghi chép gốc; fe63ef6 từng ghi giả lập |

## Điểm từng câu đã lưu và điều kiện trích dẫn

`pass` là tiêu chí riêng từng câu, không thay thế ba metric CP2. Hai cột mã dưới đây chỉ kiểm điều kiện cần; nội dung trích có đúng nghĩa vẫn phải được người chấm đọc.

| File / run ID | pass tổng | pass thường / khó / từ chối | Có mã, mọi mã tồn tại | Thêm đúng mã yêu cầu trong đề | Câu thiếu điều kiện mã |
|---|---|---|---|---|---|
| run-1.csv / `run-1@20261127-214416` | 18/23 (78.3%) | 8/9 · 8/11 · 2/3 | 9/9 (100.0%) | 8/9 (88.9%) | B18 |
| run-2.csv / `run-2@20261127-215239` | 22/23 (95.7%) | 9/9 · 10/11 · 3/3 | 9/9 (100.0%) | 9/9 (100.0%) | — |
| run-3.csv / `run-3@20261128-081047` | 22/23 (95.7%) | 9/9 · 10/11 · 3/3 | 8/9 (88.9%) | 8/9 (88.9%) | B06 |
| run-4.csv / `run-4@20261128-115005` | 21/23 (91.3%) | 8/9 · 10/11 · 3/3 | 8/9 (88.9%) | 7/9 (77.8%) | B06, B18 |
| run-5.csv / `run-5@20261128-122015` | 21/23 (91.3%) | 8/9 · 10/11 · 3/3 | 8/9 (88.9%) | 7/9 (77.8%) | B06, B18 |
| run-heldout.csv / `run-1@20261128-085312` | 13/15 (86.7%) | 5/7 · 5/5 · 3/3 | 5/7 (71.4%) | 5/7 (71.4%) | H03, H04 |

Mã đối chiếu lấy từ `[MÃ]` ghi rõ trong expected/pass_criterion; không suy đáp án từ input và không sửa expected. Kho mã hiện tại dùng để kiểm sự tồn tại, không tái dựng kho bài ở từng thời điểm.

## Điều kiện báo thiếu căn cứ / chuyển TA

Chỉ đếm output chứa ‘Không có trong bài’, ‘TA’ hoặc lời hướng tới trợ giảng. Có cụm từ này **không chứng minh không bịa**, không kiểm được ý nghĩa, mức từ chối hay thông tin nhạy cảm. Kết quả đầy đủ của `khong_bia` vẫn chờ người chấm.

| File | Khó: có lời báo/chuyển TA | Từ chối: có lời báo/chuyển TA | Câu thiếu điều kiện |
|---|---|---|---|
| run-1.csv | 10/11 (90.9%) | 3/3 (100.0%) | B15 |
| run-2.csv | 9/11 (81.8%) | 3/3 (100.0%) | B15, B16 |
| run-3.csv | 10/11 (90.9%) | 3/3 (100.0%) | B15 |
| run-4.csv | 10/11 (90.9%) | 3/3 (100.0%) | B15 |
| run-5.csv | 10/11 (90.9%) | 3/3 (100.0%) | B15 |
| run-heldout.csv | 5/5 (100.0%) | 3/3 (100.0%) | — |

## Đúng ý và kết luận chuẩn

- `dung_y_tra_loi`: cần mẫu 20 câu thường và người thứ hai chấm 5 output, khớp ≥4/5. Script không chấm nghĩa và không công nhận kết quả này chỉ từ cột pass.
- `run-1.csv`: 9 câu thường / cần 20 — **chưa đủ mẫu**; 0 câu chưa có điểm pass; 0 lỗi kỹ thuật.
- `run-2.csv`: 9 câu thường / cần 20 — **chưa đủ mẫu**; 0 câu chưa có điểm pass; 0 lỗi kỹ thuật.
- `run-3.csv`: 9 câu thường / cần 20 — **chưa đủ mẫu**; 0 câu chưa có điểm pass; 0 lỗi kỹ thuật.
- `run-4.csv`: 9 câu thường / cần 20 — **chưa đủ mẫu**; 0 câu chưa có điểm pass; 0 lỗi kỹ thuật.
- `run-5.csv`: 9 câu thường / cần 20 — **chưa đủ mẫu**; 0 câu chưa có điểm pass; 0 lỗi kỹ thuật.
- `run-heldout.csv`: 7 câu thường / cần 20 — **chưa đủ mẫu**; 0 câu chưa có điểm pass; 0 lỗi kỹ thuật.

Không tự kết luận ‘đạt chuẩn CP2’ từ báo cáo này. Nếu điều kiện cần trích dẫn dưới 90% thì `trich_dung_ma` chưa thể đạt; nếu đủ điều kiện cần thì vẫn phải đọc đối chiếu ý. Bộ kín là phép đo riêng, không gộp mẫu hay thay kết quả bộ 23 câu.

Chuẩn CP2 và dữ liệu chạy cũ được giữ nguyên. Điểm R5 lượt 1 → lượt 2 phải được trình bày theo lịch sử; kiểm toán sau CP4 được ghi nhận riêng.
