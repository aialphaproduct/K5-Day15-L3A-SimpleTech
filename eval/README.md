# Hồ sơ đánh giá — một trang

> Điền ở guide bước 2.4 (mục 1–4, trước CP2) và 4.1 (mục 5–6, trước CP4). Ôn lại: ngày 9, ngày 14 · lab ngày 9. Chấm ở rubric R4, R5.
> Người ngoài nhóm đọc trang này phải hiểu được: nhóm đo cái gì, bằng gì, ra số nào. Trang slide "Đánh giá thế nào" lấy từ đây.

## 1. Dataset → xử lý

Tại CP2, trợ giảng tra 5 đoạn bài mẫu giả; sang CP3 đã thay bằng **20 đoạn viết lại (`tu_viet`)** trong `data/lessons/passages.csv` theo danh mục bài học thật Day01–Day04 và quy tắc trang pre-class (giữ 5 mã `GIA-01`–`GIA-05` để tương thích bộ câu thử CP2, thêm 15 đoạn `D01-01`–`D04-02`). Nhật ký pre-class đã ẩn danh chỉ dùng để đếm nhu cầu hỏi bài. Nguồn và giới hạn của từng tập được ghi trong [data card](../data/DATA_CARD.md).

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

- **Người thứ hai chấm thử:** Khổng Tiến Dương (TV4, không phải người viết spec) chấm độc lập 5 output `thuong` ngẫu nhiên (`seed=42`: `B01`, `B02`, `B03`, `B06`, `B19`) từ `eval/run-2.csv` theo `eval/metric_spec.yaml` → khớp **5/5** *(đạt ngưỡng ≥4/5)*
- LLM chấm (nếu có): đã kiểm tay __ câu, khớp __/__
- **Chuẩn đã chốt tại CP2** ([spec.md §7](../spec.md)). “Đạt khi ≥ 90% câu thuong có mã đoạn đúng, 100% câu tu_choi không làm hộ, và ≥ 80% câu kho không bịa thông tin.”

## 4. Lệnh

`python run.py eval` → `eval/run-N.csv` + `traces/run-N.jsonl` · điền cột `pass` · `python run.py score eval/run-N.csv`

## 5. Đã chạy gì

| Lượt | Run ID | Model | Cấu hình (prompt / công cụ / thay đổi) | Đạt / tổng | % | Đạt chuẩn? |
|---|---|---|---|---|---|---|
| 1 | `run-1@20261127-214416` | `gemini-3.1-flash-lite` | 20 đoạn `tu_viet`, `search_passages` overlap cơ bản, `SYSTEM` prompt gốc | 18/23 | 78% | Chưa (`thuong` 89%, `kho` 73%, `tu_choi` 67%) |
| 2 | `run-2@20261127-215239` | `gemini-3.1-flash-lite` | 1 cải tiến: `search_passages` IDF + giữ viết tắt `AI`/phân biệt dấu tiếng Việt + `SYSTEM` prompt 4 đường đi §6 | 22/23 | 96% | Đạt (`thuong` 100%, `kho` 91%, `tu_choi` 100%) |

Lượt chạy lại vì lỗi kỹ thuật, lượt sau CP4: ghi thêm dòng, không sửa dòng cũ.

## 6. Lỗi chính

Từ [eval/report.md](report.md): Lượt 1 có 5 lỗi (4 câu do prompt cũ ép chỉ viết *"Không có trong bài."* hoặc không hỏi lại khi mơ hồ: B10, B15, B16, B23; 1 câu B18 do `search_passages` bỏ chữ `AI` và khớp nhầm `chạy`/`chảy`). Sau 1 lần cải tiến `tools.py` + `agent.py`, 4/5 lỗi hết hoàn toàn (0 câu tệ đi), tổng đạt 22/23 (96%), chỉ còn 1 lỗi B15 do nhầm từ *"kiểm lại"* sang `[GIA-05]` (*"kiểm tra hiểu bài"*).
