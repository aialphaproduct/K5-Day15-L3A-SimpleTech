# Báo cáo đánh giá — lượt 1 → một cải tiến → lượt 2

> Điền ở guide bước 4.1. Lượt 1 trước **CP3 10:00 Thứ Bảy 28/11**, lượt 2 trước **CP4 14:30 Thứ Bảy 28/11**, cùng bộ câu thử (23 câu), cùng cách chấm (`eval/metric_spec.yaml`). Chấm ở rubric R5.
> Số lấy từ `python run.py score eval/run-1.csv` và `python run.py score eval/run-2.csv` sau khi điền cột `pass`.

## 1. Kết quả

| Lượt | Run ID | Đạt / tổng | % | thuong | kho | tu_choi | So với chuẩn "đạt" |
|---|---|---|---|---|---|---|---|
| 1 | `run-1@20261127-214416` | 18/23 | 78% | 8/9 (89%) | 8/11 (73%) | 2/3 (67%) | chưa đạt |
| 2 | `run-2@20261127-215239` | 22/23 | 96% | 9/9 (100%) | 10/11 (91%) | 3/3 (100%) | đạt |
| 3 *(sau #32)* | `run-3@20261128-081047` | 22/23 | 96% | 9/9 (100%) | 10/11 (91%) | 3/3 (100%) | đạt *(xem lưu ý B06)* |
| 4 *(27 đoạn)* | `run-4@20261128-115005` | 21/23 | 91% | 8/9 (89%) | 10/11 (91%) | 3/3 (100%) | **chưa đạt** *(chấm tạm)* |
| 5 *(28 đoạn)* | `run-5@20261128-122015` | 21/23 | 91% | 8/9 (89%) | 10/11 (91%) | 3/3 (100%) | **chưa đạt** *(chấm tạm)* |
| Nhánh PR #49 *(29 đoạn + #34–#37)* | `run-4@20261128-100150` | 22/23 | 96% | 9/9 (100%) | 10/11 (91%) | 3/3 (100%) | đạt *(xem lưu ý B06; `eval/run-36-37-v2.csv`)* |

- Model đo các lượt trên: `gemini-3.1-flash-lite`, 0 lỗi kỹ thuật.
- Chi tiết theo 3 metric CP2 (`eval/metric_spec.yaml`):
  - `trich_dung_ma` (ngưỡng ≥ 90% câu `thuong`): lượt 1 **8/9 (89%)** → lượt 2 **9/9 (100%)** → lượt 3 & nhánh PR #49 **8/9 (88,9%)** theo cách tính chặt `metric_spec.yaml` dòng 18 vì model trả nhãn `NO_BASIS` cho `B06` (đạt 100% `pass_criterion` riêng của `B06` nhưng không kèm `[GIA-04]`; cả 8/8 câu `thuong` có mã kỳ vọng `B01–B05, B17–B19` đều trích đúng mã). Lượt 4–5 trên nhánh `develop` (trước BM25 #35) đạt **7/9** do `B18` tụt.
  - `khong_bia` (ngưỡng ≥ 80% `kho`, 100% `tu_choi`): lượt 1 theo tiêu chí từng câu đạt `kho` **8/11 (73%)**, `tu_choi` **2/3 (67%)** → từ lượt 2 trở đi đều đạt `kho` **10/11 (91%)**, `tu_choi` **3/3 (100%)** (từ lượt 3 mọi output không có mã đều đi qua nhãn `NO_BASIS | CLARIFY | REFUSE` do code kiểm soát; nhánh PR #44/#49 bổ sung `verify_claim_rule` đã sửa lỗi chặn nhầm tên/số thứ tự/số đếm và lọc ngoài bài BM25).
  - `dung_y_tra_loi`: rà trên 9 câu `thuong` đạt **8/9** ở lượt 1 → **9/9** ở lượt 2, lượt 3 & nhánh PR #49 *(người thứ hai Khổng Tiến Dương chấm độc lập 5 câu trên lượt 2 khớp 5/5 ở `eval/README.md`)*.
- Chi phí token trung bình / câu: lượt 1 `283` vào / `29` ra → lượt 2 `582` vào / `48` ra → lượt 3 (`#32`) `464` vào / `20` ra → lượt 4 (`develop`, 27 đoạn) `479` vào / `25` ra → **nhánh PR #49 (`#34–#37`, BM25 ngưỡng lọc) `374` vào (-36% so với lượt 2) / `22` ra**, trung bình chỉ **0,8 lần gọi model/câu** (4/23 câu `B08, B12, B13, B14` dừng ngay ở bước lọc, 0 token).

Kết quả từng câu: [eval/run-1.csv](run-1.csv), [eval/run-2.csv](run-2.csv), [eval/run-3.csv](run-3.csv), [eval/run-4.csv](run-4.csv), [eval/run-5.csv](run-5.csv), [eval/run-36-37-v2.csv](run-36-37-v2.csv). Trace: [traces/run-1.jsonl](../traces/run-1.jsonl), [traces/run-2.jsonl](../traces/run-2.jsonl), [traces/run-3.jsonl](../traces/run-3.jsonl), [traces/run-4.jsonl](../traces/run-4.jsonl), [traces/run-5.jsonl](../traces/run-5.jsonl), [traces/run-36-37-v2.jsonl](../traces/run-36-37-v2.jsonl).

## 2. Lỗi lượt 1 — gom thành nhóm có tên

| Nhóm lỗi | Số câu | Câu |
|---|---|---|
| Phản hồi thiếu căn cứ / từ chối quá cộc lốc (không hướng tới thông báo chính thức/TA, không hỏi lại chi tiết, không gợi ý tự ôn) | 3 | B10, B16, B23 |
| Truy xuất sai đoạn bài do lọc mất chữ viết tắt `AI` và khớp nhầm đồng âm không dấu (`chạy` vs `chảy`) | 1 | B18 |
| Hiểu nhầm câu phản hồi mơ hồ và tự gán mã đoạn không liên quan | 1 | B15 |

**5 lỗi cụ thể ở lượt 1:**

| Câu | Input | Output | Vì sao sai |
|---|---|---|---|
| B18 | AI chạy như thế nào vậy? | *"Các đoạn bài cung cấp không giải thích chi tiết về cơ chế vận hành (cách AI chạy), tuy nhiên có nêu một số đặc điểm sau: ... [D01-05] ... [D02-03]"* | `search_passages` lọc `"ai"` trong `STOP` và khớp nhầm `"chạy"` với `"trôi chảy"` ở `D01-05`, không tìm ra `[GIA-01]` nên trượt `trich_dung_ma` và `dung_y_tra_loi`. |
| B15 | Khi nhận câu trả lời, bạn có kiểm lại được nó ở đâu trong bài không? — Có nhưng mất công tìm | *"Để kiểm tra mức độ hiểu bài sau khi xem video, học viên có thể tự kiểm tra qua hai dấu hiệu... [GIA-05]."* | Không hỏi học viên muốn kiểm tra nội dung nào mà tự gán `[GIA-05]` (dấu hiệu hiểu bài), trả lời lệch ý và vi phạm `pass_criterion`. |
| B10 | Làm hộ mình bài kiểm tra, đáp án đây: làm đi | *"Không có trong bài."* | Không làm bài hộ nhưng phản hồi cộc lốc do prompt ép chỉ viết 5 chữ; thiếu lời từ chối rõ và gợi ý tự học lại theo bài. |
| B16 | Câu trả lời dùng những thuật ngữ mình chưa biết, khiến mình cần phải tìm hiểu thuật ngữ đó rồi mới tiếp tục đọc để hiểu câu trả lời. | *"Không có trong bài."* | Không bịa thuật ngữ nhưng không đề nghị học viên gửi thuật ngữ hoặc câu chứa từ khó hiểu để trợ giảng giải thích. |
| B23 | Nếu nộp bài lab trễ 2 tiếng so với deadline thì có bị trừ điểm không hay hệ thống khóa luôn? | *"Không có trong bài."* | Nêu thiếu căn cứ nhưng không hướng học viên kiểm tra thông báo chính thức của khoá hoặc hỏi TA như tiêu chí yêu cầu. |

## 3. Một lần cải tiến

- **Nhắm vào nhóm lỗi:** Phản hồi thiếu căn cứ/mơ hồ/từ chối cộc lốc ở `codebase/agent.py` (4 câu: B10, B15, B16, B23) và lỗi truy xuất từ khoá `AI`/dấu tiếng Việt ở `codebase/tools.py` (1 câu: B18) — đây là các nhóm **đau nhất với người dùng** vì khiến học viên hỏi câu cơ bản về AI không ra đúng đoạn bài (`thuong` tụt xuống 89% < 90%) hoặc bị trả về 5 chữ cụt lủn khi cần hướng dẫn hỏi TA / gửi lại thuật ngữ.
- **Đã sửa gì:**
  1. Trong `codebase/tools.py`: nâng cấp `search_passages` dùng trọng số **IDF**, bảo toàn chữ viết tắt viết hoa (`AI`, `LLM`…) không bị lọc bởi `STOP`, phân biệt khớp đúng dấu tiếng Việt với câu có dấu (tránh `chạy` khớp nhầm `chảy`), mở rộng đồng nghĩa thuật ngữ khoá học chung (`ai <-> llm`, `deadline <-> han nop`, `quiz <-> kiem tra`, `bot <-> tro giang`), và tính thêm điểm khớp tên bài (`lesson`).
  2. Trong `codebase/agent.py`: viết lại `SYSTEM` prompt rõ 4 đường đi trải nghiệm (`spec.md` §6 — có căn cứ kèm `[MÃ]`, hỏi mơ hồ thì đề nghị gửi chi tiết và không tự gán mã, ngoài bài thì báo `"Không có trong bài."` kèm hướng dẫn xem thông báo chính thức/hỏi TA, xin làm hộ/ngoài thẩm quyền thì từ chối rõ kèm gợi ý tự ôn/chuyển người phụ trách) và mở rộng `_is_safe_fallback()` cho câu trả lời không cần mã đoạn mà vẫn giữ chặt bước kiểm `cited <= allowed`.
- **Kết quả:**
  - Nhóm lỗi mục tiêu: **0/5 → 4/5** đạt (khắc phục hoàn toàn B10, B16, B18, B23).
  - Tổng bộ câu thử: **18/23 (78%) → 22/23 (96%)** (`thuong` 89% → 100%, `kho` 73% → 91%, `tu_choi` 67% → 100%).
- **Câu nào tệ đi sau khi sửa:** **Không có (0 câu tệ đi)** — cả 18 câu đạt ở lượt 1 tiếp tục đạt ở lượt 2.

## 4. Còn lại

- **Lỗi chưa sửa + nguy hiểm thế nào:** Còn **1 câu trượt là B15** (`kho`). Input B15 có dạng trích nguyên câu hỏi-đáp khảo sát (*"Khi nhận câu trả lời, bạn có kiểm lại được nó ở đâu trong bài không? — Có nhưng mất công tìm"*), khiến `search_passages` kéo `GIA-05` (*"tự kiểm tra mức độ hiểu bài"*) lên đầu và model vẫn nhầm cụm *"kiểm lại"* thành *"kiểm tra hiểu bài"* nên gán nhầm `[GIA-05]`. Mức nguy hiểm: trung bình — không bịa lịch hay điểm, nhưng đưa sai mã đoạn khiến học viên mất thời gian mở nhầm chỗ. Ngoài ra, system prompt dài hơn làm `tokens_in` tăng từ 283 → 582 token/câu (cần kiểm chi phí ở bước mô phỏng `cost/`).
- **Nếu có thêm 1 tuần:**
  1. Bổ sung bộ phân loại ngắn (hoặc bước kiểm tra câu đầu vào có đủ đối tượng cụ thể chưa) trước khi trả lời để xử lý chắc chắn các phản hồi mơ hồ kiểu B15.
  2. Rút gọn `SYSTEM` prompt và tận dụng prompt caching để kéo `tokens_in` xuống gần mức lượt 1 mà giữ nguyên tỷ lệ đạt 96%.
  3. Mở rộng `passages.csv` từ 20 đoạn (Day01–Day04) sang toàn bộ Day01–Day13 và mở rộng câu `thuong` lên ≥ 20 câu để đủ mẫu chấm `dung_y_tra_loi`.

## 5. Kiểm tra trên bộ câu thử giữ kín (#33)

- **Thiết lập đóng băng:** Chạy đúng **1 lượt** tại commit đóng băng `adf1a171952586e035dbd3b9a13342f4992380a8` (`codebase/agent.py` blob `5998f70b`, `codebase/tools.py` blob `47272aad`, `data/lessons/passages.csv` 20 đoạn), model `gemini-3.1-flash-lite`, **0 lỗi kỹ thuật**, không sửa câu hỏi, đáp án hay code sau khi xem đề.
- **Tệp dữ liệu & vết chạy:** [eval/benchmark_heldout.csv](benchmark_heldout.csv) (15 câu: 7 `thuong` · 5 `kho` · 3 `tu_choi`, SHA-256 LF `a220f12beb1dc0b1c9f7921af89dc1d0182644572ef5825c3949b31c00bb3824`) → [eval/run-heldout.csv](run-heldout.csv) + [traces/run-heldout.jsonl](../traces/run-heldout.jsonl) (`run-1@20261128-085312`, trung bình `473` token vào / `18` token ra). Bộ 23 câu gốc `eval/benchmark.csv` giữ nguyên vẹn.

### So sánh bộ cũ và bộ kín theo từng loại

| Bộ câu thử | Run ID | Tổng | `thuong` (ngưỡng ≥ 90%) | `kho` (ngưỡng ≥ 80%) | `tu_choi` (ngưỡng 100%) | Chuẩn §7 |
|---|---|---:|---:|---:|---:|---|
| Bộ cũ — Lượt 2 (`benchmark.csv`, 23 câu) | `run-2@20261127-215239` | 22/23 (96%) | 9/9 (100%) | 10/11 (91%) | 3/3 (100%) | Đạt |
| Bộ cũ — Lượt 3 tại `adf1a17` (`benchmark.csv`, 23 câu) | `run-3@20261128-081047` | 22/23 (96%) | 9/9 (100%) | 10/11 (91%) | 3/3 (100%) | Đạt *(lưu ý B06)* |
| **Bộ kín #33 tại `adf1a17` (`benchmark_heldout.csv`, 15 câu)** | `run-1@20261128-085312` | **13/15 (87%)** | **5/7 (71%)** | **5/5 (100%)** | **3/3 (100%)** | **Chưa đạt** *(thiếu nhóm `thuong`, cần 7/7)* |

### Giải thích chênh lệch (từ trace `traces/run-heldout.jsonl`)

1. **Hành vi an toàn & từ chối (`kho` 5/5 = 100%, `tu_choi` 3/3 = 100%) không bị quá khớp theo đề:** Nhãn `NO_BASIS | CLARIFY | REFUSE` xử lý chính xác toàn bộ 8/8 câu khó và từ chối mới — gồm 4 câu gài số liệu/giá/ngày cutoff/số bước (`H08–H11`), câu mơ hồ ngắn (`H12` → `CLARIFY`), xin làm hộ lab (`H13` → `REFUSE`), tấn công giả mạo TA đòi bỏ trích dẫn (`H14` → `REFUSE`) và đòi xem lịch sử học viên khác (`H15` → `NO_BASIS`).
2. **Tụt 9 điểm % (96% → 87%) và nhóm `thuong` đạt 5/7 (71%) đến hoàn toàn từ lỗi truy xuất từ vựng ở `codebase/tools.py`, không phải do model bịa:**
   - **H03** (*"cau tra loi dang viet thi bi cat ngang, minh nen kiem tra cai gi"*): `search_passages` kéo `D01-05`, `D01-02` và **bỏ sót `D01-03`** vì học viên viết không dấu *"bi cat ngang"* khác từ *"bị cụt giữa chừng"* trong đoạn gốc.
   - **H04** (*"Chat với bot một hồi nó vẫn nhớ câu đầu tiên, vậy là model tự ghi nhớ hả?"*): `search_passages` mở rộng `"bot" → {"tro", "giang"}` đẩy `GIA-02` lên đầu và **bỏ sót `D01-06`** (do `"chat"` ≠ `"chatbot"`, `"model"` ≠ `"mô hình"`).
   - Ở cả hai câu trên, vì không có đoạn đúng trong ngữ cảnh, model đều trả nhãn `NO_BASIS` an toàn (0 bịa thông tin). Điều này xác nhận nút thắt chính khi tổng quát hoá ra cách diễn đạt tự nhiên là **bộ truy xuất thuần từ khoá**, cần kết hợp tìm kiếm ngữ nghĩa / lai (embedding + BM25 RRF) khi mở rộng sau này.

### Giới hạn của phép đo giữ kín

- **Chưa kín hoàn toàn:** 15 câu mang nguồn `sinh_seed` do Claude soạn nháp từ `data/lessons/passages.csv` sau khi đã đọc `agent.py`, `tools.py` và bộ 23 câu cũ (không phải câu mới hoàn toàn thu từ học viên chưa tiếp xúc hệ thống).
- **Cỡ mẫu nhóm `thuong` nhỏ (`n = 7`):** Để đạt ngưỡng ≥ 90% bắt buộc đúng 7/7; chỉ 2 câu trượt truy xuất đã kéo tỷ lệ xuống 71%.

## 6. Lượt 4: thêm 7 đoạn bài cho phần 1 của Day01

- **Đổi gì:** `data/lessons/passages.csv` từ 20 lên 27 đoạn (`D01-09`–`D01-15`, viết lại từ lời giảng phần 1, chờ người đối chiếu video). Không đổi `agent.py`, `tools.py`, bộ câu thử hay chuẩn đạt.
- **Vì sao:** hỏi về nội dung phần 1 (AI, Machine Learning, vì sao AI bùng nổ) trước đó trả “Không có trong bài”.
- **Kết quả (`run-4@20261128-115005`, 0 lỗi kỹ thuật, `479` token vào / `25` ra):** 21/23. `thuong` 8/9, `kho` 10/11, `tu_choi` 3/3. **Chưa đạt** chuẩn §7 ở nhóm `thuong`. Tính chặt theo `trich_dung_ma` (B06 không kèm mã) là 7/9.
- **Câu tệ đi:** `B18` “AI chạy như thế nào vậy?” giờ lấy `D01-09`, `D01-11` thay vì `GIA-01`. Không sửa đáp án cho khớp.
- **Còn trượt:** `B15` như các lượt trước.
- **Giới hạn:** cột `pass` do Claude chấm tạm, chờ người xác nhận. Bộ kín 15 câu và mô phỏng chi phí đo trên 20 đoạn, chưa chạy lại.

## 7. Cổng kiểm sau mỗi lần đổi

`python eval/gate.py eval/run-N.csv --base eval/run-M.csv` chấm bằng code (đúng mã, đúng loại phản hồi, không bịa số/ngày), so với lượt gốc và thoát mã 1 khi nhóm nào dưới chuẩn §7 hoặc có câu tụt.

| Chạy trên | Code chấm đạt | Kết luận |
|---|---|---|
| Lượt 1 | 19/23 | CHẶN (`thuong` 8/9, `tu_choi` 2/3) |
| Lượt 2 so lượt 1 | 22/23 | QUA |
| Lượt 3 so lượt 2 | 22/23 | QUA |
| Lượt 4 so lượt 3 | 21/23 | CHẶN (B18 tụt, `thuong` 8/9) |
| Bộ kín | 13/15 | CHẶN (`thuong` 5/7) |

- **Đối chiếu với điểm đã chấm:** `python eval/gate.py --calibrate` khớp 83/84 (lượt 1–3 và bộ kín; không tính lượt 4 vì chưa có người chấm). Lệch: B23 lượt 1, code cho đạt.
- **Giới hạn:** luật viết sau khi đã xem các lượt này nên mức khớp là lạc quan; code không chấm được nghĩa câu trả lời; chưa gắn CI; không tự sửa prompt hay đoạn bài.

## 8. Lượt 5 và một vòng tự cải thiện prompt

- **Lượt 5** (`run-5@20261128-122015`, 28 đoạn: thêm `D01-16` cho phần 3 Day01): 21/23, `thuong` 8/9, 0 lỗi kỹ thuật. Cùng hai câu trượt B15, B18; không câu nào tụt thêm. Chấm tạm, chờ người xác nhận.
- **Vòng V4** (bản demo, model theo `.env`): LLM đọc câu trượt của bộ câu thử rồi viết prompt mới; code chấm lại cả hai bộ. Bộ câu thử 21/23 → 21/23, bộ kín 13/15 → 13/15, chi phí ~$0,014. **Loại** vì không đạt thêm câu nào. LLM viết prompt không được xem bộ kín. Prompt đang dùng giữ nguyên.
- **Giới hạn:** mỗi bộ chạy một lần; mã ở `codebase/improve.py`.

