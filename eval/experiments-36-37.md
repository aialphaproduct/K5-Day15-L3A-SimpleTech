# Báo cáo mở rộng đoạn bài (#36) và ngữ cảnh video đang xem (#37)

> Tác giả: Vũ Trí Dũng (TV3) · Nhánh: `feat/issue-36-37-passages-video`  
> Không thay đổi chuẩn "đạt" đã chốt tại CP2 (`spec.md` §7) hay `eval/metric_spec.yaml`.

---

## 1. Issue #36 — Mở rộng kho đoạn bài và gắn trạng thái đối chiếu

### 1.1. Những gì đã làm trên `data/lessons/passages.csv` và `data/DATA_CARD.md`
- Mở rộng từ **20 đoạn → 29 đoạn** (`tu_viet`, không chép nguyên văn tài liệu khoá), phủ thêm đúng các nhóm sai bài ôn cao nhất từ số liệu `data/preclass/answers.csv` và phân tích `#39` (PR #45):
  - **Day06** (sai lần đầu 44,1%): thêm 4 đoạn `D06-01`–`D06-04` (`document_identity_and_effective_date`, `gate_severity_and_strictness`, `raw_clean_serve_layers` & `lineage_trace_to_source`, `more_data_amplifies_stale_copies` & `silent_data_failure_cascade`).
  - **Day05** (sai lần đầu 30,6%): thêm 3 đoạn `D05-01`–`D05-03` (`autonomy_by_confidence_and_error_cost`, `ai_four_path_behavior`, `ai_requirement_outcome_threshold_fallback`).
  - **Day03 & Day04** (2 `kc_code` sai cao nhất trong bảng ưu tiên `#39`): thêm `D03-03` (`agentic_fit_scoring_decision`) và `D04-03` (`cot_task_fit`).
- Bổ sung 3 cột mới trong `data/lessons/passages.csv`:
  - `video`: mã video thật trích từ `data/preclass/chat.csv` (`d01-r1-v01`…`d06-r1-v02`, 16 video bài giảng; 4 đoạn quy tắc chung `GIA-02`–`GIA-05` mang nhãn `preclass-chung`).
  - `video_timestamp`: mốc phút:giây trong video gốc.
  - `verify_status`: trạng thái đối chiếu rõ ràng cho từng đoạn.

### 1.2. Trạng thái đối chiếu trung thực (không bịa mốc video)

| Trạng thái (`verify_status`) | Số đoạn | Mã đoạn | Ghi chú |
|---|---:|---|---|
| `quy_tac_he_thong` | 4/29 | `GIA-02`–`GIA-05` | Đối chiếu theo `data/preclass/README.md` và `tracks/track-a-edtech.md`; `video_timestamp = khong_ap_dung` |
| `chua_doi_chieu_video` | 25/29 | `GIA-01`, `D01-01`–`D06-04` | Dữ liệu BTC không chứa lời giảng gốc hay mốc thời gian; `video_timestamp = chua_doi_chieu`. Cần mở trực tiếp video trên trang pre-class (ưu tiên `d01-r1-v02` — 133 câu hỏi, `d01-r1-v01` — 102 câu hỏi) để rà nội dung và điền mốc phút:giây thật. |
| `da_doi_chieu_video` | 0/29 | — | Sẽ cập nhật sau khi đối chiếu trực tiếp trên video pre-class |

---

## 2. Issue #37 — Trợ giảng biết học viên đang xem video nào

### 2.1. Thay đổi trong mã nguồn (tương thích ngược 100%)
- `codebase/tools.py`:
  - `_load()` đọc thêm `video`, `video_timestamp`, `verify_status`; thêm `list_videos()` trả danh sách 16 video bài giảng cho giao diện.
  - `search_passages(query, video="", scope="hep")`: tính điểm BM25 lai trên toàn kho 29 đoạn (giữ IDF ổn định và vẫn chặn câu ngoài bài bằng ngưỡng điểm/độ phủ + lọc trùng đơn âm tiếng Việt), sau đó áp ngữ cảnh video:
    - `video=""` hoặc `scope="toan_kho"`: giữ nguyên hành vi toàn kho của `#35`.
    - `scope="hep"` (mặc định khi có `video`): ưu tiên đoạn thuộc đúng `video` đang xem; nếu video hiện tại không có đoạn khớp hoặc phạm vi rộng hơn (`ca_ngay` / `preclass-chung`) khớp mạnh vượt trội (`>= 2.0×` điểm), tự động mở rộng sang cùng ngày học (`ca_ngay`) rồi sang quy tắc chung (`preclass-chung`).
    - `scope="ca_ngay"`: tìm trong tất cả video của cùng ngày học trước, rồi mở sang `preclass-chung`.
- `codebase/agent.py`:
  - `answer(text: str, video: str = "", scope: str = "hep") -> {"output": str}` giữ nguyên hợp đồng `answer(text)` cho `run_eval.py`, `simulate.py` và `app.py`.
  - Khi có `video`, ghi `note("ngữ cảnh video=... scope=...")` vào trace, gọi `search_passages(text, video=..., scope=...)` và gắn dòng `Video đang xem: <mã>` vào prompt; vẫn giữ nguyên kiểm nhãn `#32` và `verify_claim_rule` `#34`.
- `codebase/web.py`:
  - Thêm bộ chọn `Video đang xem` (`<select id="videoSelect">`) lấy động từ `tools.list_videos()`, hỗ trợ query string `/?video=d01-r1-v02` để nhúng dưới từng video pre-class.
  - `POST /ask` nhận thêm trường tuỳ chọn `video` (và `scope`), vẫn tương thích khi client cũ chỉ gửi `{"text": "..."}`.

### 2.2. Kết quả đo `hep` vs `ca_ngay` vs `toan_kho`

Lệnh chạy lại (0 token, chạy offline):

```bash
python eval/bench_video_context.py
```

Bộ đo gồm: **8 cặp (16 câu)** đặt **cùng một câu hỏi ở 2 video khác nhau** (5 cặp cùng ngày học `Day01`, `Day03`, `Day06` + 3 cặp khác ngày `Day01–Day05`), **4 câu mở rộng** khi video đang xem không chứa câu trả lời, và **3 câu ngoài bài** khi đã chọn video.

| Chế độ tìm | Cùng ngày khác video (Top-1) | Khác ngày (Top-1) | Đạt trọn cặp (2/2 video) | Mở rộng khi video chưa đủ | Lọc ngoài bài | Độ trễ TB |
|---|---:|---:|---:|---:|---:|---:|
| `toan_kho` (không biết video) | 5/10 (50%) | 1/6 (17%) | 0/8 (0%) | 4/4 (100%) | 3/3 (100%) | 5.0 ms |
| `ca_ngay` (lọc theo ngày học) | 5/10 (50%) | 4/6 (67%) | 1/8 (12%) | 4/4 (100%) | 3/3 (100%) | 5.6 ms |
| **`hep` (ưu tiên video → mở rộng ngày)** | **10/10 (100%)** | **6/6 (100%)** | **8/8 (100%)** | **4/4 (100%)** | **3/3 (100%)** | **5.1 ms** |

**Nhận xét:**
- `toan_kho` không đạt cặp nào (0/8) vì cùng một câu hỏi luôn trả cùng 1 đoạn Top-1 bất kể học viên đang xem video nào.
- `ca_ngay` tách được một phần câu hỏi khác ngày (4/6), nhưng hoàn toàn không phân biệt được hai video trong **cùng một ngày** (ví dụ `d01-r1-v02` về *temperature* vs `d01-r1-v03` về *hallucination* khi học viên hỏi *"Tại sao câu trả lời của LLM có thể sai sự thật?"*; hoặc `d06-r1-v01` vs `d06-r1-v02` khi hỏi về dữ liệu cũ).
- **`hep` đạt 8/8 cặp (100%)** lấy đúng đoạn của từng video, đồng thời vẫn mở rộng trơn tru sang cả ngày / quy tắc chung (4/4) và giữ nguyên khả năng lọc câu ngoài bài (3/3, 0 gọi model). Chọn **`hep`** làm chế độ mặc định khi có `video`.

---

## 3. Kiểm không hồi quy (Retrieval + Unit Test + Eval 23 câu model thật)

1. **Truy xuất 30 câu + 6 câu ngoài bài (`python eval/bench_retrieval.py --no-embed`, kho 29 đoạn):**
   - `bm25_hybrid`: **Recall@1 = 30/30 (100%)**, **Recall@3 = 30/30 (100%)**, **Lọc ngoài bài = 6/6 (100%)** (0 token thêm, 5.0 ms/câu).
   - Trong quá trình mở rộng lên 29 đoạn, phát hiện 1 ca ngoài bài (`N02`: *"Thời tiết Hà Nội cuối tuần này có mưa không?"*) từng trùng ngẫu nhiên 2 đơn âm (`thời` + `cuối`) với `D06-04`; đã thêm điều kiện yêu cầu bigram hoặc độ phủ trong `tools.py` giúp khôi phục 6/6 (100%) mà không ảnh hưởng câu trong bài.
2. **Unit test (`python -m unittest discover -s tests -v`):** **16/16 đạt** (gồm test sửa `verify_claim_rule` từ PR #44 và 4 test cho `#36`, `#37`, Flask `web.py`).
3. **Eval 23 câu CP2 trên model thật sau khi gộp fix PR #44 (`gemini-3.1-flash-lite`, `eval/run-36-37-v2.csv`, `run-4@20261128-100150`, `video=""`):**
   - **Tổng đạt: 22/23 (96%)** — `thuong 9/9 (100%)`, `kho 10/11 (91%)`, `tu_choi 3/3 (100%)`, lỗi kỹ thuật: `0` → **đạt chuẩn `spec.md` §7, không hồi quy** so với lượt 2 & lượt 3 (`22/23 = 96%`).
   - Hiệu quả gọi model cải thiện rõ: trung bình còn **0,8 lần gọi model/câu** (4/23 câu `B08, B12, B13, B14` dừng ngay ở bước tìm đoạn, tốn 0 token) và **374 token vào / 22 token ra** (giảm so với 582/48 ở lượt 2 và 464/20 ở lượt 3).
   - Câu duy nhất chưa đạt vẫn là `B15` (cùng nguyên nhân đã ghi nhận ở lượt 2). *(Ghi nhận: file lưu dưới tên `eval/run-36-37-v2.csv` để giữ nguyên vẹn `eval/run-4.csv` và `eval/run-5.csv` của PR #56 trên `develop`; lượt kiểm sơ bộ trước fix PR #44 nằm ở `eval/run-36-37.csv`, cũng đạt 22/23 = 96%.)*
