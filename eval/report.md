# Báo cáo đánh giá — lượt 1 → một cải tiến → lượt 2

> Điền ở guide bước 4.1. Lượt 1 trước **CP3 10:00 Thứ Bảy 28/11**, lượt 2 trước **CP4 14:30 Thứ Bảy 28/11**, cùng bộ câu thử (23 câu), cùng cách chấm (`eval/metric_spec.yaml`). Chấm ở rubric R5.
> Số lấy từ `python run.py score eval/run-1.csv` và `python run.py score eval/run-2.csv` sau khi điền cột `pass`.

## 1. Kết quả

| Lượt | Run ID | Đạt / tổng | % | thuong | kho | tu_choi | So với chuẩn "đạt" |
|---|---|---|---|---|---|---|---|
| 1 | `run-1@20261127-214416` | 18/23 | 78% | 8/9 (89%) | 8/11 (73%) | 2/3 (67%) | chưa đạt |
| 2 | `run-2@20261127-215239` | 22/23 | 96% | 9/9 (100%) | 10/11 (91%) | 3/3 (100%) | đạt |

- Model đo cả 2 lượt: `gemini-3.1-flash-lite`, 0 lỗi kỹ thuật ở cả hai lượt.
- Chi tiết theo 3 metric CP2 (`eval/metric_spec.yaml`):
  - `trich_dung_ma` (ngưỡng ≥ 90% câu `thuong`): lượt 1 **8/9 (89%)** → lượt 2 **9/9 (100%)**.
  - `khong_bia` (ngưỡng ≥ 80% `kho`, 100% `tu_choi`): lượt 1 theo tiêu chí từng câu đạt `kho` **8/11 (73%)**, `tu_choi` **2/3 (67%)** → lượt 2 đạt `kho` **10/11 (91%)**, `tu_choi` **3/3 (100%)** (không có câu nào bịa ngày/điểm/lịch hay làm hộ ở cả hai lượt).
  - `dung_y_tra_loi`: rà trên 9 câu `thuong` đạt **8/9** ở lượt 1 → **9/9** ở lượt 2 *(chưa đủ mẫu 20 câu `thuong` và chờ người thứ hai — Khổng Tiến Dương — chấm độc lập 5 câu ở `#12`)*.
- Chi phí token trung bình / câu: lượt 1 `283` vào / `29` ra → lượt 2 `582` vào / `48` ra (tăng do system prompt chi tiết hơn).

Kết quả từng câu: [eval/run-1.csv](run-1.csv), [eval/run-2.csv](run-2.csv). Trace: [traces/run-1.jsonl](../traces/run-1.jsonl), [traces/run-2.jsonl](../traces/run-2.jsonl).

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
