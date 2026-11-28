# Học viên vướng ở đâu: Bài ôn (`pre_post_post`) × Câu hỏi trợ giảng (`chat.csv`)

> Issue **#39 [P0]** · Người thực hiện: **Khổng Tiến Dương (TV4)** · Dữ liệu: `data/preclass/` của BTC (05/11–25/11/2026, không chép file data vào repo).
> Chạy lại để kiểm tra đúng từng con số: `python evidence/count_quiz_vs_questions.py "<đường dẫn tới data/preclass>"`.

---

## 1. Cách lọc và mẫu số

- **Bài ôn (`answers.csv`):** lọc `nguon == "pre_post_post"` (1.970 dòng) và giữ **lần trả lời đầu** `lan_thu == 1` có nhãn đúng/sai (`was_correct` là `True`/`False`) → **1.968 lượt** (tổng sai: **399/1.968 = 20,3%**). Bỏ mọi nhóm `lesson_id` hoặc `kc_code` có **n < 20 lượt**.
- **Câu hỏi trợ giảng (`chat.csv`):** dùng lại đúng bộ lọc của `evidence/count_tutor.py` (#5) — `agent_id == "teaching_assistant"` và `kind == "question"` (**1.091 câu**, trong đó **1.090/1.091** gắn được `Day` qua cột `transcript`, 1 dòng thiếu `transcript`).
- **Học viên có hoạt động mỗi Day (`events.csv`):** đếm số `hv` duy nhất có `actor == "learner"` gắn với `DayNN` (từ `lesson_id` hoặc `video`). Toàn khoá có **436** học viên hoạt động (khớp `data/preclass/README.md`).

---

## 2. Tỷ lệ sai theo `lesson_id` (`n ≥ 20`) đặt cạnh số câu hỏi / học viên hoạt động

| Day | `lesson_id` | Sai bài ôn (`pre_post_post`, lần 1) | HV làm bài ôn | Câu hỏi TA (`chat.csv`) | HV hoạt động (`events.csv`) | Câu hỏi / HV hoạt động | HV có hỏi / HV hoạt động |
|---|---|---:|---:|---:|---:|---:|---:|
| Day06 | `program-day06:data-engineering-for-agents` | **41/93 (44,1%)** | 8 | 40 | 103 | 0,39 | 14/103 (13,6%) |
| Day05 | `program-day05:ai-product-thinking-and-requirement` | **55/180 (30,6%)** | 15 | 78 | 134 | 0,58 | 20/134 (14,9%) |
| Day09 | `program-day09:evaluation-failure-analysis` | **9/36 (25,0%)** | 3 | 54 | 75 | 0,72 | 18/75 (24,0%) |
| Day11 | `program-day11:guardrails-hitl-responsible-ai` | **11/48 (22,9%)** | 4 | 13 | 43 | 0,30 | 4/43 (9,3%) |
| Day03 | `program-day03:chatbot-to-agentic-agent` | **52/230 (22,6%)** | 24 | 140 | 154 | **0,91** | 35/154 (22,7%) |
| Day07 | `program-day07:retrieval-context-engineering` | **26/123 (21,1%)** | 11 | 77 | 86 | **0,90** | 15/86 (17,4%) |
| Day12 | `program-day12:ai-sdlc-coding-agent` | **6/36 (16,7%)** | 3 | 0 | 26 | 0,00 | 0/26 (0,0%) |
| Day02 | `program-day02:ai-problem-definition` | **43/263 (16,3%)** | 25 | 113 | 180 | 0,63 | 28/180 (15,6%) |
| Day01 | `program-day01:ai-llm-foundation` | **71/439 (16,2%)** | 41 | 333 | 417 | 0,80 | 70/417 (16,8%) |
| Day04 | `program-day04:prompt-engineering-tool-calling` | **50/316 (15,8%)** | 27 | 134 | 145 | **0,92** | 28/145 (19,3%) |
| Day08 | `program-day08:from-workflows-to-agents` | **20/137 (14,6%)** | 14 | 86 | 109 | 0,79 | 21/109 (19,3%) |
| Day10 | `program-day10:poc-to-pilot` | **5/48 (10,4%)** | 4 | 5 | 44 | 0,11 | 3/44 (6,8%) |
| Day13 | `program-day13:launch-economics` | *(bỏ: 10/19 < 20)* | 2 | 17 | 50 | 0,34 | 5/50 (10,0%) |

**Quan sát từ bảng (chỉ mô tả hành vi đo được, không suy diễn nguyên nhân):**
- Khớp các số kiểm tra ban đầu: **Day06 sai 41/93 (44,1%)**, **Day05 sai 55/180 (30,6%)**, **Day01 sai 71/439 (16,2%)**; `Day13` có 10/19 lượt nên bị loại ở ngưỡng `n ≥ 20`.
- Khi chuẩn hoá theo số học viên hoạt động (`events.csv`), **Day04 (0,92 câu/hv)**, **Day03 (0,91 câu/hv)** và **Day07 (0,90 câu/hv)** có mật độ hỏi cao hơn cả **Day01 (0,80 câu/hv)** — Day01 nhiều câu hỏi nhất về số tuyệt đối (333 câu) đi kèm số học viên hoạt động lớn nhất (417 người).
- **Day03** nổi bật ở cả hai chiều: mật độ hỏi cao nhì toàn khoá (**0,91 câu/hv**, **35/154 = 22,7%** học viên có hỏi) và tỷ lệ sai bài ôn cao trong nhóm ngày đầu (**52/230 = 22,6%**).
- Ngược lại, **Day06** và **Day05** có tỷ lệ sai bài ôn cao nhất (44,1% và 30,6%) nhưng mật độ câu hỏi/học viên hoạt động thấp hơn (0,39 và 0,58 câu/hv). Dữ liệu không cho biết lý do học viên ít hỏi hơn ở hai ngày này.

---

## 3. Tỷ lệ sai theo `kc_code` (`n ≥ 20`) và đối chiếu 20 đoạn hiện có (PR #31)

Trong tổng số **156** nhóm `(lesson_id, kc_code)`, có **40/156 (25,6%)** nhóm đạt `n ≥ 20` lượt (toàn bộ thuộc Day01–Day04) và **116/156 (74,4%)** nhóm bị bỏ do `n < 20` (gồm toàn bộ KC của Day05–Day13).

### Top 10 `kc_code` có tỷ lệ sai cao nhất (`n ≥ 20`)

| Hạng | Day | `kc_code` | Tỷ lệ sai (`lan_thu=1`) | Trạng thái trong `data/lessons/passages.csv` (PR #31) |
|---:|---|---|---:|---|
| 1 | Day03 | `agentic_fit_scoring_decision` | **12/20 (60,0%)** | **Chưa có đoạn bài** |
| 2 | Day04 | `cot_task_fit` | **11/27 (40,7%)** | **Chưa có đoạn bài** |
| 3 | Day01 | `chatbot_is_app_around_model` | **16/41 (39,0%)** | Đã có (`D01-06`) |
| 4 | Day02 | `complete_ai_problem_statement` | **8/23 (34,8%)** | **Chưa có đoạn bài** |
| 5 | Day02 | `select_rule_workflow_agent_level` | **8/23 (34,8%)** | Đã có (`D02-02`) |
| 6 | Day04 | `system_prompt_contract` | **9/27 (33,3%)** | Đã có (`D04-01`) |
| 7 | Day02 | `construct_eval_plan` | **7/23 (30,4%)** | **Chưa có đoạn bài** |
| 8 | Day04 | `tool_calling_flow` | **6/26 (23,1%)** | Đã có (`D04-02`) |
| 9 | Day01 | `model_tier_selection` | **8/35 (22,9%)** | Đã có (`D01-07`) |
| 10 | Day04 | `zero_one_few_shot_selection` | **6/27 (22,2%)** | Đã có (`D04-02`) |

---

## 4. Danh sách 10 ý (`kc_code`) ưu tiên viết đoạn bài trước — giao cho Dũng (#8 / #36)

Lọc từ 40 `kc_code` đủ mẫu (`n ≥ 20`), **bỏ các ý Dũng đã viết** trong 20 đoạn của PR #31 và xếp theo tỷ lệ sai giảm dần (ưu tiên số lượt sai lớn hơn khi bằng %):

| Ưu tiên | Day | `kc_code` cần viết mới | Tỷ lệ sai (`lan_thu=1`) | Lý do ưu tiên từ số đo |
|---:|---|---|---:|---|
| **1** | Day03 | `agentic_fit_scoring_decision` | **12/20 (60,0%)** | Sai cao nhất toàn bộ nhóm đủ mẫu; Day03 có mật độ hỏi 0,91 câu/hv |
| **2** | Day04 | `cot_task_fit` | **11/27 (40,7%)** | Sai cao thứ hai; Day04 có mật độ hỏi cao nhất khoá (0,92 câu/hv) |
| **3** | Day02 | `complete_ai_problem_statement` | **8/23 (34,8%)** | Sai cao nhất nhóm chưa có đoạn ở Day02 |
| **4** | Day02 | `construct_eval_plan` | **7/23 (30,4%)** | Sai trên 30% ở Day02 |
| **5** | Day01 | `ai_boom_data_architecture_hardware` | **8/40 (20,0%)** | Nằm ở Day01 (417 hv hoạt động, 333 câu hỏi), 8 lượt sai |
| **6** | Day01 | `token_generation_loop_count` | **8/40 (20,0%)** | `GIA-01` hiện mới mô tả cơ chế dự đoán token, chưa nêu rõ cách đếm số lần lặp sinh token |
| **7** | Day03 | `agent_architecture_components` | **4/20 (20,0%)** | Day03 (0,91 câu/hv), 20% sai lần đầu |
| **8** | Day03 | `agentic_fit_criteria` | **4/21 (19,0%)** | Bổ trợ trực tiếp cho ý #1 (`agentic_fit_scoring_decision`) ở Day03 |
| **9** | Day04 | `prompt_scope_types` | **5/27 (18,5%)** | Nằm ở Day04 (0,92 câu/hv), 5 lượt sai |
| **10** | Day03 | `ai_system_spectrum_classification` | **4/24 (16,7%)** | Thuộc Day03 (0,91 câu/hv), đứng ngay sau 9 ý trên theo tỷ lệ sai |

*(Ghi chú bổ sung cho Dũng: nếu mở rộng kho đoạn bài vượt ngoài Day01–Day04, cần xem thêm **Day05** `55/180 = 30,6%` và **Day06** `41/93 = 44,1%` — hai ngày có tỷ lệ sai cấp bài cao nhất nhưng chưa lọt danh sách KC `n ≥ 20` vì số người làm bài ôn mỗi KC nhỏ hơn 20.)*

---

## 5. Giới hạn của phân tích

1. **Thiên lệch tự chọn (self-selection bias):** Làm bài ôn `pre_post_post` là tự nguyện, tỷ lệ học viên làm bài rất thấp so với tổng số học viên hoạt động — ví dụ Day01 chỉ **41/417 (9,8%)**, Day05 **15/134 (11,2%)**, Day06 **8/103 (7,8%)**, Day09 **3/75 (4,0%)**, Day12 **3/26 (11,5%)**. Vì vậy tỷ lệ sai đo được chỉ phản ánh **nhóm học viên tự chọn làm bài ôn**, không đại diện cho toàn bộ học viên học ngày đó.
2. **Ngưỡng `n ≥ 20` loại toàn bộ KC từ Day05 trở đi:** Do mỗi KC chỉ được mỗi học viên làm tối đa 1 câu ở `lan_thu = 1`, số lượt tối đa mỗi KC bằng số học viên làm bài ôn của ngày đó (Day05 tối đa 15, Day06 tối đa 8). Do đó toàn bộ 116/156 KC bị loại gồm hết Day05–Day13 dù cấp `lesson_id` của Day05–Day06 có tỷ lệ sai rất cao.
3. **Không suy diễn nguyên nhân từ tương quan:** Dữ liệu hành vi chỉ cho biết tỷ lệ sai và mật độ câu hỏi đi cùng nhau thế nào, không cho biết vì sao học viên sai (bài khó, câu hỏi trắc nghiệm gài bẫy, hay học viên làm nhanh chưa xem kỹ video) và cũng không biết nội dung câu hỏi trong `chat.csv` có khớp với các `kc_code` hay sai hay không.
4. **Một dòng chat thiếu `transcript`:** Trong 1.091 câu hỏi trợ giảng AI ở `chat.csv`, có 1 dòng không có `transcript` (1.090/1.091 dòng gắn được Day qua `transcript`, giữ đúng cách đếm của `evidence/count_tutor.py`).
