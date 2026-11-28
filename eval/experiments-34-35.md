# Thử nghiệm kỹ thuật — Kiểm chứng nội dung (#34) & Truy xuất đoạn bài (#35)

> Báo cáo số liệu so sánh cho Issue **#34** và **#35**. Mọi số liệu đều chạy lại được bằng 1 lệnh trên cùng bộ 20 đoạn bài (`data/lessons/passages.csv`).

---

## 1. Issue #35 — Truy xuất: đo Recall@1, Recall@3, tìm kiếm lai & ngưỡng điểm

- **Bộ dữ liệu đo:** [eval/retrieval_queries.csv](retrieval_queries.csv) — **30 câu có nhãn** phủ đều các đoạn bài (gồm câu chuẩn, câu **không dấu** và câu **diễn đạt khác từ trong đoạn**) + **6 câu ngoài bài** (`N01`–`N06`, `expected_code = NONE`) để kiểm tra ngưỡng lọc không gọi model.
- **Lệnh chạy lại:**
  - Đầy đủ cả 4 cách (có gọi `gemini-embedding-001`): `python eval/bench_retrieval.py`
  - Chỉ chạy 2 cách thuần code (0 token, chạy offline): `python eval/bench_retrieval.py --no-embed`

### Bảng so sánh

| Phương pháp | Recall@1 | Recall@3 | Lọc ngoài bài (không gọi model) | Độ trễ TB | Chi phí thêm |
|---|---|---|---|---|---|
| `idf_current` (trước #35) | 30/30 (100,0%) | 30/30 (100,0%) | 1/6 (16,7%) | 1,5 ms | 0 token (thuần code) |
| **`bm25_hybrid` (`min=2.5`) — Chọn** | **30/30 (100,0%)** | **30/30 (100,0%)** | **6/6 (100,0%)** | **3,2 ms** | **0 token (thuần code)** |
| `gemini_embedding` (`sim>=0.68`) | 30/30 (100,0%) | 30/30 (100,0%) | 6/6 (100,0%) | 69,7 ms | +1 lượt API embedding (~15 tok/câu) + 1.514 ms embed 20 đoạn |
| `hybrid_bm25_embed` (RRF) | 30/30 (100,0%) | 30/30 (100,0%) | 6/6 (100,0%) | 78,8 ms | +1 lượt API embedding (~15 tok/câu) + 1.514 ms embed 20 đoạn |

### Quyết định tích hợp vào `codebase/tools.py`

- **Chọn `bm25_hybrid` (`MIN_SCORE = 2.5`, `MIN_COVERAGE = 0.45`):**
  - Bằng `gemini_embedding` và `hybrid_bm25_embed` về cả Recall@1 (**100%**), Recall@3 (**100%**) lẫn tỷ lệ lọc ngoài bài (**6/6 = 100%** so với 1/6 ở bản IDF cũ), đồng thời đưa đúng `[GIA-01]` lên top-1 cho câu `B18` (*"AI chạy như thế nào vậy?"*).
  - **Nhanh hơn ~22–25 lần** (3,2 ms so với 69,7–78,8 ms), **0 token thêm**, không phụ thuộc API embedding khi chạy offline hoặc bị giới hạn rate limit.
  - Khi kho bài tăng từ 20 lên hàng trăm đoạn (Day01–Day13), có thể bật `hybrid_bm25_embed` (RRF) đã kiểm chứng ở trên.

---

## 2. Issue #34 — Kiểm câu trả lời có thật sự được đoạn trích chứng minh

- **Bộ dữ liệu đo:** [eval/claim_verify_cases.csv](claim_verify_cases.csv) — **20 ví dụ** gồm **10 câu đúng** (`V01`–`V10`, `supported`) và **10 câu "mã đúng, ý sai"** (`V11`–`V20`, `unsupported`: 5 câu bịa số/ngày/giờ/điểm/tên học viên `V11`–`V15` và 5 câu đảo nghĩa thuần ngữ nghĩa `V16`–`V20`).
- **Lệnh chạy lại:**
  - Đầy đủ cả 2 cách (có gọi `gemini-3.1-flash-lite`): `python eval/bench_claim_verify.py --wait 4.5`
  - Chỉ chạy luật rẻ (0 token): `python eval/bench_claim_verify.py --no-llm`

### Bảng so sánh

| Cách kiểm chứng | Bắt đúng câu sai | Chặn nhầm câu đúng | Độ trễ TB | Token TB thêm (vào/ra) |
|---|---|---|---|---|
| **`cheap_rule` (luật code) — Chọn mặc định** | **5/10 (50%)** *(5/5 = 100% nhóm bịa số/ngày/giờ/tên; bỏ sót 5/5 nhóm đảo nghĩa)* | **0/10 (0%)** | **0,0 ms** | **0 / 0** |
| `llm_verify` (`gemini-3.1-flash-lite`) *(tuỳ chọn `ENABLE_LLM_VERIFY=1`)* | **10/10 (100%)** | **0/10 (0%)** | **7.176,7 ms** | **233 / 2** |

### Quyết định tích hợp vào `codebase/agent.py`

- **Chọn `verify_claim_rule` chạy mặc định** sau bước kiểm mã `cited <= allowed`:
  - Chặn **100% lỗi rủi ro cao nhất** theo `spec.md` §9 (bịa ngày nộp, giờ, điểm số, tên học viên không có trong đoạn trích) với **0% chặn nhầm**, **0 ms độ trễ thêm**, **0 token thêm** — giữ nguyên chi phí đơn vị khi mô phỏng 50 phiên (`cost/`).
  - Bổ sung kiểm Unicode (`isupper`/`islower` sau chuẩn hoá NFC thay cho khoảng `À-Ỹ`) để không bắt nhầm `"bạn đã…"`, `"bạn được…"`, và bỏ qua số thứ tự danh sách (`1.`, `(1)`, `bước 1`) cùng số đếm cấu trúc (`3 bước`, `2 dấu hiệu`) khi không đi kèm từ chỉ giới hạn (như `"tối đa 5 bước"`).
  - Bổ sung công tắc môi trường **`ENABLE_LLM_VERIFY=1`** (mặc định tắt) cho phép bật thêm lượt LLM chấm (đạt 10/10 gồm cả lỗi đảo nghĩa `V16`–`V20`) khi triển khai trên tài khoản trả phí chịu được thêm ~235 token và độ trễ 1 lượt gọi model.
