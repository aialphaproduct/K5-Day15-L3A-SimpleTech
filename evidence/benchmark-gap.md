# Bộ câu thử có phản ánh đúng cách học viên hỏi?

> Issue **#42 [P2]** · Người thực hiện: **Khổng Tiến Dương (TV4)** · Dữ liệu: `data/preclass/` (`chat.csv`, `answers.csv`, 05/11–25/11/2026; không chép file data vào repo) và [eval/benchmark.csv](../eval/benchmark.csv).
> Chạy lại để kiểm tra đúng từng con số: `python evidence/count_benchmark_gap.py "<đường dẫn tới data/preclass>"`.

---

## 1. Hành vi hỏi thật của học viên (`chat.csv` & `answers.csv`)

- **Phân bố kênh (`channel`, `n = 1.260`):** `video_question` **1.108/1.260 (87,9%)**, `video_discussion_reply` **151/1.260 (12,0%)**, `session_question` **1/1.260 (0,1%)**.
- **Phân bố loại tin (`kind`, `n = 1.260`):** `question` **1.091/1.260 (86,6%)**, `reply` **151/1.260 (12,0%)**, `mention` **18/1.260 (1,4%)**.
- **Điểm `rubric_bam_bai` (`answers.csv`, `nguon == "chat"`):** có **1.223/1.260 (97,1%)** dòng đã chấm (`da_cham`), 24 `bo_qua`, 13 `chua_cham`.
  - Toàn bộ tin đã chấm (`n = 1.223`): **0 điểm (không liên quan bài) = 261/1.223 (21,3%)** *(khớp chính xác gợi ý ban đầu)* · 1 điểm = 450/1.223 (36,8%) · 2 điểm = 512/1.223 (41,9%).
  - Riêng câu hỏi gửi trợ giảng AI (`teaching_assistant + question`, đã chấm `n = 1.061`): **0 điểm = 236/1.061 (22,2%)** · 1 điểm = 422/1.061 (39,8%) · 2 điểm = 403/1.061 (38,0%).

---

## 2. Bảng độ lệch: Hành vi thật (`chat.csv` — 1.091 câu TA) vs `eval/benchmark.csv` (23 câu)

| Chiều so sánh | Câu hỏi TA thật (`chat.csv`, `n = 1.091`) | Bộ câu thử hiện tại (`eval/benchmark.csv`, `n = 23`) | Độ lệch phát hiện |
|---|---:|---:|---|
| Độ dài min / p25 / median / p75 / max (ký tự) | 1 / 29 / **57** / 96 / 1.777 | 24 / 39 / **47** / 75 / 143 | Benchmark hẹp hơn ở cả hai đuôi (min 24 vs 1; p75 75 vs 96; max 143 vs 1.777) |
| Độ dài trung bình (ký tự) | 66,4 | 59,8 | Gần nhau về trung bình nhưng lệch mạnh về phân bố đuôi |
| Câu rất ngắn (`≤ 20` ký tự) | **173/1.091 (15,9%)** | **0/23 (0,0%)** | **Thiếu hoàn toàn** dạng hỏi cực ngắn / gõ 1–2 thuật ngữ |
| Câu ngắn (`≤ 30` ký tự) | **335/1.091 (30,7%)** | **3/23 (13,0%)** | Thiếu hơn một nửa tỷ trọng câu ngắn thực tế |
| Câu dài (`≥ 120` ký tự) | **56/1.091 (5,1%)** | **2/23 (8,7%)** | Tương đương nhẹ |
| Tỷ lệ câu không liên quan / ngoài bài | `rubric_bam_bai = 0`: **236/1.061 (22,2%)** | `kho + tu_choi`: **14/23 (60,9%)** (`kho`: 11/23 = 47,8%) | Benchmark đang nghiêng mạnh về câu ngoài bài/từ chối; chỉ có **9/23 (39,1%)** câu `thuong` (chưa đủ 20 câu `thuong` theo `metric_spec.yaml`) |

---

## 3. Đề xuất bổ sung câu thử (chưa sửa `eval/benchmark.csv` để giữ chuẩn CP2/CP3)

> **Lưu ý nguồn (luật Issue #42):** `chat.csv` không có nội dung câu hỏi thật nên **toàn bộ câu đề xuất dưới đây phải ghi nhãn `tu_viet` (hoặc `sinh_seed`)**, tuyệt đối **không ghi `nguoi_dung` hay `data_that`**. Nếu mở rộng ở vòng sau CP4 (hoặc đưa vào bộ kiểm tra bổ sung), đề xuất thêm **6 câu** để bù trực tiếp các độ lệch ở mục 2:

| Đề xuất | Kiểu bù độ lệch | Input đề xuất | `type` | `source` | Kỳ vọng kiểm tra |
|---|---|---|---|---|---|
| D01 | Câu cực ngắn (`≤ 20` ký tự, 14 ký tự — giống bôi đen thuật ngữ) | `temperature?` | `thuong` | `tu_viet` | Giải thích `temperature` kèm `[D01-02]`, không bịa ngoài đoạn |
| D02 | Câu cực ngắn (`≤ 20` ký tự, 17 ký tự) | `hallucination là gì` | `thuong` | `tu_viet` | Giải thích ảo giác LLM kèm `[D01-05]` |
| D03 | Câu `thuong` dài trung bình (70–100 ký tự) phủ Day01–Day04 | `Hạ temperature xuống thấp có giúp LLM trả lời chắc chắn đúng sự thật hơn không?` | `thuong` | `tu_viet` | Nêu rõ ổn định hơn nhưng không đảm bảo đúng sự thật, kèm `[D01-02]` |
| D04 | Câu `thuong` phủ Day03–Day04 (mật độ hỏi cao nhất khoá) | `Trong tool calling, model tự chạy hàm hay code ứng dụng mới là bên chạy hàm?` | `thuong` | `tu_viet` | Nêu rõ model đề xuất tên hàm/tham số, code ứng dụng thực thi, kèm `[D04-02]` |
| D05 | Câu dài (`≥ 120` ký tự, 149 ký tự) có nhiều ý lồng nhau | `Mình thấy chatbot nhớ được câu mình vừa hỏi ở lượt trước, vậy bản thân LLM có tự lưu bộ nhớ giữa các lần gọi API không hay ứng dụng phải gửi kèm lại?` | `thuong` | `tu_viet` | Trả lời theo `[D01-06]` (LLM không tự nhớ, app lưu và gửi lại vào context) |
| D06 | Câu rất ngắn lạc bài (`rubric_bam_bai = 0`, 13 ký tự) | `hello test bot` | `kho` | `tu_viet` | Báo không có trong bài / hướng dẫn hỏi về bài học, không gán mã đoạn sai |

---

## 4. Giới hạn

- `chat.csv` chỉ lưu độ dài ký tự (`do_dai_cau_hoi`) và điểm rubric máy chấm (`rubric_bam_bai`), **không có nội dung câu hỏi thật**, nên không kiểm được học viên hỏi sai chính tả, không dấu hay pha trộn tiếng Anh ở mức độ nào.
- Tỷ lệ `rubric_bam_bai = 0` (**22,2%**) do giám khảo AI của hệ thống pre-class chấm tự động, có thể khác định nghĩa `kho` / `tu_choi` trong `eval/benchmark.csv` (ví dụ một câu hỏi lịch học vẫn có thể bị chấm 0 điểm bám bài, trong khi một câu hỏi dài về bài nhưng dùng từ không rõ cũng có thể bị chấm 0).
