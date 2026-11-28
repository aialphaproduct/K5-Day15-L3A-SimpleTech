# Tóm tắt mô phỏng simulate-1@20261128-012032

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| dung_it | 22 | 1 | 581 | 41 | 1.0 | 1.0 |
| dung_vua | 15 | 3 | 1734 | 126 | 3.0 | 3.0 |
| dung_nhieu | 11 | 5 | 2890 | 207 | 5.0 | 5.0 |

Tỉ lệ đạt dùng để tính: 22/23 (96%) — lượt run-2@20261127-215239

- Tỉ lệ đạt lấy từ lượt nhóm chọn: eval/run-2.csv (--rate-from).

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (143 người) | Chi phí / tháng — cơ sở (436 người) | Chi phí / tháng — cao (721 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gemini-3.1-flash-lite (vào 0.25 · ra 1.5 $/1M) | $0.00053 | $0.00055 | $0.00022 | $0.3206 | $0.9775 | $1.62 | $0.0022 |
| gemini-4-hydrogen (vào 1.5 · ra 7.5 $/1M) | $0.0030 | $0.0031 | $0.0012 | $1.83 | $5.57 | $9.21 | $0.0128 |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (2.5) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: gemini-3.1-flash-lite. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 2/50.
