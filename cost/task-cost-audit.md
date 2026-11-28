# Kiểm toán chi phí — task là một câu hỏi

Báo cáo sau CP4, tính lại artifact đã lưu, không gọi AI hoặc sửa kết quả lịch sử.

- Mô phỏng: `simulate-1.csv` (`simulate-1@20261128-012032`).
- Đánh giá: `run-2.csv` (`run-2@20261127-215239`), model `gemini-3.1-flash-lite`.
- 50 phiên thử; 48 hợp lệ; 2 lỗi. Trên phiên hợp lệ: 122 câu hỏi, 70581 token vào / 5079 token ra.
- Tỷ lệ câu đạt dùng trong công thức: **19/20 = 95.00%**, chỉ nhóm `kho, thuong` mà mô phỏng sử dụng. Tỷ lệ toàn benchmark là 22/23, có cả nhóm khác.

## Công thức và đơn vị

1 task = 1 câu hỏi. USD/câu = tổng chi phí token của phiên hợp lệ / tổng số lượt hỏi của các phiên đó. USD/câu đạt ước tính = USD/câu / tỷ lệ đạt eval cùng model và nhóm đầu vào. Không dùng chi phí một phiên nhiều câu để gọi là chi phí một câu thành công.

Tỷ lệ eval là giả định chuyển sang mẫu mô phỏng, chưa phải tỷ lệ thành công quan sát trực tiếp trên các câu mô phỏng. Không suy ra tỷ lệ thành công trọn phiên hoặc đạt mọi metric CP2.

Chi phí/tháng = số người × tổng theo persona (share chuẩn hoá × phiên/người/tháng × chi phí token TB/phiên hợp lệ của persona). Quy mô thấp/cơ sở/cao: 143 / 436 / 721 người.

| Model / cơ sở | USD/câu | USD/câu đạt ước tính | USD/tháng thấp | cơ sở | cao | USD/người/tháng |
|---|---:|---:|---:|---:|---:|---:|
| gemini-3.1-flash-lite (đã đo token, proxy tỷ lệ eval) | $0.00020708 | $0.00021798 | $0.32061723 | $0.97754625 | $1.61653864 | $0.00224208 |
| gemini-4-hydrogen (chỉ đổi đơn giá, chưa đo chất lượng) | $0.00118003 | — | $1.82695884 | $5.57030807 | $9.21144982 | $0.01277594 |

## Giới hạn

- Các phiên lỗi có log 1732 token vào / 182 token ra, không nằm trong trung bình trên. Lỗi API không trả usage có thể còn chi phí chưa quan sát; không coi lỗi là miễn phí. Chưa tính retry, hosting và vận hành.
- Cấu hình lịch sử: lượt 2, kho 20 đoạn. Không đại diện tự động cho bản cuối 28 đoạn; cần mô phỏng lượt mới bằng AI thật sau khi có cấu hình.
- Hai mức giá là ảnh chụp BTC ngày 25/11/2026 trong `cost/personas.yaml`, không phải xác minh giá hiện hành. Dòng model khác chỉ ngoại suy đơn giá; để trống USD/câu đạt vì chưa đo model đó.
- `cost/simulate.py`, CSV, summary và trace gốc giữ nguyên. Báo cáo này sửa cách đọc đơn vị, không thay số liệu nộp CP4.
