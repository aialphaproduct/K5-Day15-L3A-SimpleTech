# Hồ sơ đánh giá — một trang

> Điền ở guide bước 2.4 (mục 1–4, trước CP2) và 4.1 (mục 5–6, trước CP4). Ôn lại: ngày 9, ngày 14 · lab ngày 9. Chấm ở rubric R4, R5.
> Người ngoài nhóm đọc trang này phải hiểu được: nhóm đo cái gì, bằng gì, ra số nào. Trang slide "Đánh giá thế nào" lấy từ đây.

## 1. Dataset → xử lý

Tại CP2, trợ giảng tra 5 đoạn bài mẫu có mã. Nhật ký pre-class đã ẩn danh được dùng để đếm nhu cầu hỏi bài. Nguồn và giới hạn của từng tập được ghi trong [data card](../data/DATA_CARD.md).

## 2. Bộ câu thử dựng ra sao

- `eval/benchmark.csv` có 23 câu (9 `thuong`, 11 `kho`, 3 `tu_choi`, gồm hai câu tấn công B11–B12).
- Nguồn gồm 14 `tu_viet`, 9 `nguoi_dung`, 0 `data_that` và 0 `sinh_seed`. Tỷ lệ từ người dùng hoặc dữ liệu thật là 9/23 (39,1%). B20–B21 lấy từ [P2, câu 1 và 4](../evidence/interviews/P2.md). B22–B23 trích hai câu hỏi trong [biên bản phỏng vấn P4, mục Ghi chép](../evidence/interviews/P4.md).
- Độ phủ — lưới input 3–5 chiều (guide 2.4 bước 5): __
- Câu `kho` trỏ về 4 lớp chỗ khó (`spec.md` §5): lớp 1: __ · lớp 2: __ · lớp 3: __ · lớp 4: __

## 3. Metric và cách chấm

| Metric (`eval/metric_spec.yaml`) | Cách chấm | Ngưỡng |
|---|---|---|
| `trich_dung_ma` | Kiểm mã nguồn của câu thường và đối chiếu ý với đoạn trích | ≥ 90% câu thường |
| `khong_bia` | Kiểm thông tin thiếu căn cứ và cách xử lý theo từng câu | ≥ 80% câu khó và 100% câu từ chối |
| `dung_y_tra_loi` | Người chấm đối chiếu nội dung với đoạn bài | ≥ 80% trong 20 câu thường, hai người chấm khớp ≥ 4/5 |

- **Người thứ hai chấm thử:** __ (không phải người viết spec) chấm độc lập 5 output → khớp __/5 *(cần ≥4/5; lệch thì viết lại định nghĩa)*
- LLM chấm (nếu có): đã kiểm tay __ câu, khớp __/__
- **Chuẩn đã chốt tại CP2** ([spec.md §7](../spec.md)). “Đạt khi ≥ 90% câu thuong có mã đoạn đúng, 100% câu tu_choi không làm hộ, và ≥ 80% câu kho không bịa thông tin.”

## 4. Lệnh

`python run.py eval` → `eval/run-N.csv` + `traces/run-N.jsonl` · điền cột `pass` · `python run.py score eval/run-N.csv`

## 5. Đã chạy gì

| Lượt | Run ID | Model | Cấu hình (prompt / công cụ / thay đổi) | Đạt / tổng | % | Đạt chuẩn? |
|---|---|---|---|---|---|---|
| 1 | | | | __/__ | | |
| 2 | | | | __/__ | | |

Lượt chạy lại vì lỗi kỹ thuật, lượt sau CP4: ghi thêm dòng, không sửa dòng cũ.

## 6. Lỗi chính

Tóm 2–3 dòng từ `eval/report.md`: nhóm lỗi lớn nhất · đã sửa gì · còn lại gì.
