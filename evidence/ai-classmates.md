# Bạn học AI xen vào: giúp hay làm phiền?

> Issue **#40 [P1]** · Người thực hiện: **Khổng Tiến Dương (TV4)** · Dữ liệu: `data/preclass/` của BTC (05/11–25/11/2026, không chép file data vào repo).
> Chạy lại để kiểm tra đúng từng con số: `python evidence/count_interventions.py "<đường dẫn tới data/preclass>"`.

---

## 1. Kết luận ngắn (trả lời thẳng câu hỏi của issue)

- **Không thể tính chính xác tuyệt đối tỷ lệ 1-1** giữa từng lượt xen vào trong `class_events.csv` và từng lượt trả lời trong `chat.csv` vì hai bảng dùng định dạng mã khác nhau (**0/385 mã khớp trực tiếp**: `class_events.csv` dùng `ref_id` dạng `lesson@Vn:chunk`, còn `chat.csv` dùng `intervention_id` dạng `lesson:module-M:chunk-K:director`).
- **Mức ước lượng tổng thể theo mã duy nhất:** có **56 mã `intervention_id` duy nhất** được học viên đáp lại (tổng **144 lượt trả lời**) so với **385 quyết định `inserted=True`** trên tổng **761** quyết định `director_decided` (**50,6%** quyết định cho xen vào) → xấp xỉ **56/385 (~14,5%)** ở mức toàn bộ các phiên bản bài giảng.
- **Khi học viên có đáp lại, chất lượng tương tác khá bám bài:** trên **141/144** câu trả lời đã được giám khảo AI chấm (`trang_thai_cham == "da_cham"`), có **104/141 (73,8%)** đạt điểm tối đa `rubric_bam_bai = 2`, **102/141 (72,3%)** đạt `rubric_dung_ngu_canh = 2`, và **97/141 (68,8%)** có ý mới (`rubric_y_moi ≥ 1`).
- **Không thể so sánh chế độ `maic` và `tutor`:** trong toàn bộ `chat.csv` có **1.251/1.260 (99,3%)** dòng trống `learning_mode`, chỉ **9/1.260 (0,7%)** dòng `maic` và **0 dòng `tutor`**; riêng tập 144 lượt trả lời bạn học AI có **144/144 (100%)** trống `learning_mode`.

---

## 2. Phân bổ theo từng bạn học AI

Trong `class_events.csv`, 385 lượt `inserted=True` gồm các kiểu `ask_check` (212), `summarize` (155), `prompt_reflection` (16), `slow_down` (1), `explain_again` (1). Đối chiếu với `chat.csv` theo cột `addressed_agent_id`:

| Bạn học AI (`classmate_id` / `addressed_agent_id`) | Lượt `inserted=True` (`class_events.csv`) | Mã `intervention_id` có đáp lại (`chat.csv`) | Tỷ lệ ước lượng (mã có đáp / lượt xen) | Tổng lượt trả lời (`chat.csv`) | Số học viên đáp lại |
|---|---:|---:|---:|---:|---:|
| `classmate_deep_thinker` | 117/385 (30,4%) | 29 | ~24,8% | 63 | 22 |
| `classmate_inquisitive` | 112/385 (29,1%) | 25 | ~22,3% | 78 | 23 |
| `classmate_clown` | 28/385 (7,3%) | 2 | ~7,1% | 3 | 2 |
| `classmate_note_taker` | 128/385 (33,2%) | 0 | 0,0% | 0 | 0 |
| **Tổng** | **385** | **56** | **~14,5%** | **144** | — |

*Lưu ý quan sát:* `classmate_note_taker` chiếm **128/385 (33,2%)** số lượt xen nhưng có **0 lượt đáp lại** (phù hợp với việc đa số lượt xen kiểu `summarize` chỉ tóm tắt chứ không đặt câu hỏi chờ trả lời). Phần lớn tương tác tập trung vào `classmate_inquisitive` (**78/144 = 54,2%** lượt trả lời) và `classmate_deep_thinker` (**63/144 = 43,8%**).

---

## 3. Điểm `rubric_*` của các câu trả lời lại (`answers.csv`)

Trong **144** dòng `answers.csv` có `intervention_id` khác rỗng: **141/144 (97,9%)** ở trạng thái `da_cham` và **3/144 (2,1%)** ở trạng thái `bo_qua`.

| Tiêu chí (`n = 141` dòng đã chấm) | 2 điểm | 1 điểm | 0 điểm |
|---|---:|---:|---:|
| `rubric_bam_bai` (bám vào bài) | **104/141 (73,8%)** | 21/141 (14,9%) | 16/141 (11,3%) |
| `rubric_y_moi` (có ý mới của học viên) | **40/141 (28,4%)** | 57/141 (40,4%) | 44/141 (31,2%) |
| `rubric_dung_ngu_canh` (đúng ý đang bàn) | **102/141 (72,3%)** | 24/141 (17,0%) | 15/141 (10,6%) |

---

## 4. Giới hạn dữ liệu

1. **Không nối 1-1 được khóa giữa `class_events.csv` và `chat.csv`:** `ref_id` trong `class_events.csv` gắn theo phiên bản bài (`@V1`, `@V2`…), còn `intervention_id` trong `chat.csv` gắn theo `module-M:chunk-K:director` (0 mã trùng trực tiếp). Ngoài ra một mã `intervention_id` trong `chat.csv` có thể được nhiều học viên trả lời (144 lượt trên 56 mã), nên tỷ lệ `56/385 (~14,5%)` chỉ là con số ước lượng ở cấp loại đoạn, không phải tỷ lệ đáp lại theo từng lần hiển thị trên màn hình học viên.
2. **Không có mẫu `tutor` để so A/B với `maic`:** trường `learning_mode` chỉ bắt đầu ghi từ 25/11/2026 (chỉ có 9 dòng `maic` và 0 dòng `tutor` trong `chat.csv`; 22 dòng `maic` và 0 dòng `tutor` trong `answers.csv`).
3. **Không biết cảm nhận chủ quan (giúp hay làm phiền):** dữ liệu không cho biết lý do học viên bỏ qua phần lớn lượt xen (như thắc mắc của P3 về việc liên tục xuất hiện nhiều AI mới); cần phỏng vấn thêm nếu muốn đánh giá mức độ làm phiền.
