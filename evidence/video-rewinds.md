# Đoạn video nào khiến học viên phải xem lại?

> Issue **#41 [P1]** · Người thực hiện: **Khổng Tiến Dương (TV4)** · Dữ liệu: `data/preclass/` của BTC (`event_types.csv`, `events.csv`, `chat.csv`, 05/11–25/11/2026; không chép file data vào repo).
> Chạy lại để kiểm tra đúng từng con số: `python evidence/count_video_rewinds.py "<đường dẫn tới data/preclass>"`.

---

## 1. Cách đọc sự kiện video từ `event_types.csv`

Trước khi đếm, đã đối chiếu định nghĩa các sự kiện trong `event_types.csv`:
- `video_seeked` (4.322 dòng toàn khoá): khóa JSON `from`, `to` (giây). Lọc **tua lùi** (`to < from`) và gom theo **khung 30 giây đích `to`**.
- `video_segments_flushed` (22.751 dòng): khóa JSON `segments` (`[[start, end], ...]`). Dùng để tính **mật độ lượt xem / số học viên** ở từng khung 30 giây (phản ánh mức xem lặp lại).
- `chat_sent` (1.260 dòng): khóa JSON `video_seconds` (có ở 1.025/1.260 dòng). Chuẩn hoá tên video từ cột `video` (dạng `Day01/d01-r1-v02.txt` → `d01-r1-v02`) để đối chiếu cùng khung 30 giây.
- Chỉ giữ `actor == "learner"` trên 3 video nhiều câu hỏi nhất Day01: `d01-r1-v02`, `d01-r1-v01`, `d01-r1-v05`.

---

## 2. Mốc tua lùi, mật độ xem lặp và câu hỏi theo khung 30 giây

### Video 1: `d01-r1-v02` (thời lượng ~370s · 187 HV mở · 262 lượt tua lùi / 39 HV · 114 tin `chat_sent` có giây / 33 HV)

| Khung thời gian | Tua lùi (lượt / HV) | `chat_sent` (tin / HV) | Mật độ xem (`segments` / HV) |
|---|---:|---:|---:|
| 0:00–0:30 (0–30s) | 24 (11 HV) | 11 (6 HV) | 154/75 HV (2,05×) |
| 1:00–1:30 (60–90s) | 19 (6 HV) | 2 (2 HV) | **208/64 HV (3,25×)** |
| 1:30–2:00 (90–120s) | 28 (12 HV) | 6 (2 HV) | 132/61 HV (2,16×) |
| 2:00–2:30 (120–150s) | 25 (15 HV) | 5 (4 HV) | 143/60 HV (2,38×) |
| **3:00–3:30 (180–210s)** | **40 (17 HV)** | **44 (18 HV)** | **148/57 HV (2,60×)** |
| 3:30–4:00 (210–240s) | 33 (13 HV) | 5 (3 HV) | 145/57 HV (2,54×) |
| 4:00–4:30 (240–270s) | 31 (8 HV) | 0 (0 HV) | 126/55 HV (2,29×) |
| 5:00–5:30 (300–330s) | 22 (8 HV) | 3 (3 HV) | 147/55 HV (2,67×) |
| 5:30–6:00 (330–360s) | 1 (1 HV) | 12 (6 HV) | 92/54 HV (1,70×) |
| **6:00–6:30 (360–390s)** | 0 (0 HV) | **23 (11 HV)** | 80/53 HV (1,51×) |

→ **Tín hiệu rất rõ:** mốc **3:00–3:30 (`180–210s`)** đồng thời là đỉnh cao nhất về **tua lùi (40/262 = 15,3% lượt, 17 HV)** và **câu hỏi (44/114 = 38,6% tin, 18 HV)**; ngay sau đó là vùng tua lùi `3:30–4:30` (64 lượt) và cụm hỏi tổng kết cuối video `5:30–6:10` (35/114 = 30,7% tin).

### Video 2: `d01-r1-v01` (thời lượng ~344s · 407 HV mở · 198 lượt tua lùi / 69 HV · 92 tin `chat_sent` có giây / 39 HV)

| Khung thời gian | Tua lùi (lượt / HV) | `chat_sent` (tin / HV) | Mật độ xem (`segments` / HV) |
|---|---:|---:|---:|
| **0:00–0:30 (0–30s)** | **30 (24 HV)** | **35 (17 HV)** | 360/176 HV (2,05×) |
| 0:30–1:00 (30–60s) | 20 (18 HV) | 8 (4 HV) | 278/137 HV (2,03×) |
| 1:30–2:00 (90–120s) | 29 (15 HV) | 1 (1 HV) | 207/106 HV (1,95×) |
| 2:00–2:30 (120–150s) | 23 (17 HV) | 0 (0 HV) | 199/99 HV (2,01×) |
| **2:30–3:00 (150–180s)** | **31 (22 HV)** | 7 (4 HV) | 216/94 HV (2,30×) |
| 3:00–3:30 (180–210s) | 23 (14 HV) | 0 (0 HV) | 180/86 HV (2,09×) |
| 3:30–4:00 (210–240s) | 12 (12 HV) | 4 (4 HV) | **225/81 HV (2,78×)** |
| 5:00–5:30 (300–330s) | 7 (5 HV) | 10 (6 HV) | 132/73 HV (1,81×) |
| **5:30–6:00 (330–360s)** | 0 (0 HV) | **26 (12 HV)** | 122/73 HV (1,67×) |

→ Ba cụm đáng chú ý: **0:00–0:30** (30 lượt tua lùi / 24 HV và 35/92 = 38,0% tin hỏi — lưu ý có thể gồm học viên hỏi ngay khi vừa mở video, trước khi phát tiếp), **2:30–3:00** (đỉnh tua lùi **31/198 = 15,7%**, 22 HV; liền kề `3:30–4:00` có mật độ xem lặp 2,78×), và **5:00–5:44** (36/92 = 39,1% tin hỏi ở cuối video).

### Video 3: `d01-r1-v05` (thời lượng ~277s · 96 HV mở · 43 lượt tua lùi / 11 HV · 42 tin `chat_sent` có giây / 17 HV)

| Khung thời gian | Tua lùi (lượt / HV) | `chat_sent` (tin / HV) | Mật độ xem (`segments` / HV) |
|---|---:|---:|---:|
| 0:00–0:30 (0–30s) | **9 (6 HV)** | 4 (1 HV) | 77/47 HV (1,64×) |
| **2:00–2:30 (120–150s)** | 3 (2 HV) | **15 (6 HV)** | **119/41 HV (2,90×)** |
| 3:00–3:30 (180–210s) | **7 (3 HV)** | 3 (3 HV) | **102/40 HV (2,55×)** |
| **3:30–4:00 (210–240s)** | 4 (2 HV) | **15 (9 HV)** | 64/39 HV (1,64×) |

→ Hai cụm nổi bật: **2:00–2:30** (15/42 = 35,7% tin hỏi và mật độ xem lặp cao nhất 2,90×) và **3:00–4:00** (7 lượt tua lùi + 2,55× mật độ xem ở 3:00–3:30, kéo theo 15/42 = 35,7% tin hỏi / 9 HV ở 3:30–4:00).

---

## 3. Mốc video đề xuất ưu tiên giao cho Dũng (#36)

1. **`d01-r1-v02` · 3:00–4:30** (đỉnh trùng khít cả tua lùi và câu hỏi ở `3:00–3:30`) và đoạn tổng kết cuối video **`5:30–6:10`**.
2. **`d01-r1-v01` · 2:30–4:00** (đỉnh tua lùi `2:30–3:00` + xem lặp `3:30–4:00`) và đoạn tổng kết **`5:00–5:44`**.
3. **`d01-r1-v05` · 2:00–2:30** và **`3:00–4:00`** (hai cụm gom 30/42 = 71,4% số tin hỏi có mốc giây của video này).

---

## 4. Làm rõ cặp `quiz_item_opened` (2.153) / `quiz_item_dismissed` (2.099)

Khớp chính xác con số kiểm tra ban đầu: `quiz_item_opened = 2.153`, `quiz_item_dismissed = 2.099`. Tuy nhiên **KHÔNG được suy luận** là 2.099/2.153 (97,5%) học viên bỏ qua câu hỏi giữa video:
- Khi tách theo trường JSON `skipped_stop` của `quiz_item_dismissed`:
  - **`skipped_stop == True`** (thực sự bỏ qua điểm dừng quiz): chỉ **21/2.099 (1,0%)**.
  - **`skipped_stop == False`** (đóng hộp thoại quiz sau khi xem/tương tác): **2.078/2.099 (99,0%)**.
- Trong khi đó, `answer_submitted` với `nguon == "video_quiz"` chỉ có **7 dòng** trong toàn bộ `events.csv` (trùng với 7 dòng `video_quiz` trong `answers.csv`).
- **Kết luận về dữ liệu quiz giữa video:** sự kiện `quiz_item_dismissed (skipped_stop=False)` là thao tác đóng thẻ câu hỏi giữa video sau khi dừng lại xem/tương tác, không phải tỷ lệ bỏ qua; dữ liệu không ghi nội dung/kết quả trả lời cho đa số các thẻ quiz này vào `answers.csv` (chỉ có 7 dòng được lưu).

---

## 5. Giới hạn

- `video_seeked` và `chat_sent` chỉ cho biết **mốc giây học viên dừng/tua/hỏi**, không có transcript nguyên văn trong bộ data BTC nên cần Dũng mở đúng mốc giây trên video bài giảng gốc để xác định nội dung tương ứng.
- Số câu hỏi ở mốc `0:00–0:30` (nhất là ở `d01-r1-v01`: 35 tin) có thể do học viên gõ câu hỏi khi player đang ở giây 0 trước khi bấm chạy video, không nhất thiết vướng nội dung 30 giây đầu.
- Cột `video` ở `quiz_item_opened` và `quiz_item_dismissed` bị để trống toàn bộ (`2.153/2.153`), mã video nằm trong khóa JSON `quiz_key`.
