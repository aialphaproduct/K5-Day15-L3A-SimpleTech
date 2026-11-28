# Simple Tech — Trợ giảng bài học (A1)

Nhóm **Simple Tech** · Lớp **L3A** · Track **A (EdTech)** · Khoá AI20K K5, hackathon Day 15.

Bản chạy thử trả lời câu hỏi của học viên dưới video pre-class. Mỗi câu trả lời phải kèm **mã đoạn bài** để học viên mở đúng chỗ kiểm lại. Nếu bài không nói tới, trợ giảng nói **"Không có trong bài"** và chuyển tới trợ giảng (TA), không đoán.

Thành viên, mã học viên, vai trò: [TEAMS.md](TEAMS.md). Thiết kế đầy đủ: [spec.md](spec.md).

## Vấn đề

Trong 05/11–25/11/2026, học viên gửi **1.091 câu hỏi** cho trợ giảng AI dưới video từ 143 người. 31% câu hỏi nằm ở Day01; ba video đầu của Day01 chiếm 25%. Trong khảo sát nhỏ, 12/13 người không kiểm lại được câu trả lời trong bài hoặc phải mất công tìm. Chi tiết và cách đếm: [evidence/summary.md](evidence/summary.md), chạy lại được bằng [evidence/count_tutor.py](evidence/count_tutor.py).

## Giải pháp

- Tìm đoạn bài liên quan tới câu hỏi (`search_passages`).
- Không có đoạn khớp → trả lời "Không có trong bài", không gọi model.
- Có đoạn → model trả lời, mỗi khẳng định kèm mã đoạn `[MÃ]`.
- Code kiểm lại: mã trích dẫn phải thuộc đúng các đoạn đã tìm, nếu không thì không đưa câu trả lời của model.

Không làm: chấm bài, làm bài hộ, trả lời lịch/điểm/hạn của từng học viên, gửi tin ra ngoài.

## CP2 · Bộ câu thử, chuẩn đạt và bản chạy thử

- **Bộ câu thử** gồm 23 câu (9 `thuong`, 11 `kho`, 3 `tu_choi`), trong đó 9/23 câu có nguồn `nguoi_dung`. [eval/benchmark.csv](eval/benchmark.csv)
- **Cách chấm và dữ liệu** gồm ba metric và data card bản đầu. [eval/metric_spec.yaml](eval/metric_spec.yaml) · [data/DATA_CARD.md](data/DATA_CARD.md)
- **Bản chạy thử** dùng AI giả qua giao diện web và có hai câu mẫu để kiểm tra nhánh có đoạn bài và nhánh thiếu căn cứ. [Cách chạy](#chạy-bản-chạy-thử)

**Chuẩn đạt đã chốt tại CP2**, chép nguyên văn từ [spec.md §7](spec.md#7-đánh-giá--chuẩn-đạt).

> Đạt khi ≥ 90% câu thuong có mã đoạn đúng, 100% câu tu_choi không làm hộ, và ≥ 80% câu kho không bịa thông tin.

## CP3 · Bằng chứng, video và kết quả lượt 1

- **Bằng chứng pain** (data, khảo sát, trích dẫn nguyên văn): [evidence/summary.md](evidence/summary.md)
- **Bộ câu thử:** 23 câu (9 `thuong`, 11 `kho`, 3 `tu_choi`): [eval/benchmark.csv](eval/benchmark.csv)
- **Video bản chạy thử gọi AI thật:** https://youtu.be/FQgcYPckG4Y — quay trên bản demo offline tham khảo giao diện pre-class, không phải trang thật.
- **Lượt 1:** 18/23 (78%), run ID `run-1@20261127-214416`: [eval/report.md](eval/report.md)
- **Thiết kế §0–§7:** [spec.md](spec.md)
- **Chưa xong:** bộ kín 15 câu đạt 13/15, nhóm `thuong` 5/7 chưa đạt chuẩn; khảo sát 13 phản hồi, dưới ngưỡng 20; phỏng vấn chưa đủ 3 người ngoài nhóm; chưa có `demo-slides.pdf`; reflection chưa đủ người.

## Trạng thái

| Phần | Trạng thái |
|---|---|
| Khung luồng trả lời và kiểm mã | Đã cải tiến (`codebase/agent.py`, `codebase/tools.py`: IDF, phân biệt dấu, prompt 4 đường đi) |
| Đoạn bài | **Đã xong** (`data/lessons/passages.csv`, 20 đoạn `tu_viet` cho Day01–Day04 và quy tắc pre-class) |
| Nối model thật | **Đã xong** (`codebase/ai.py` hỗ trợ Gemini/OpenAI/Anthropic/Ollama qua `.env`, đã đo với `gemini-3.1-flash-lite`) |
| Đánh giá | **Đã chạy 2 lượt** ([eval/report.md](eval/report.md)): lượt 1 `18/23 (78%)` → lượt 2 `22/23 (96%)` (**đạt chuẩn §7**) |
| Khảo sát / phỏng vấn học viên | Đang làm |
| Chi phí khi dùng thật | Chưa mô phỏng |
| Slide, demo, triển khai AWS | Đang làm |

Việc đang mở: [Issues](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues).

## Phân công

Mỗi người làm xong phần của mình trong hôm nay theo thứ tự dưới đây. Việc của người sau phụ thuộc người trước: Tùng → Dũng → Dương (chấm, chi phí). Mỹ làm song song. Mỗi việc có một issue; tick trong issue khi xong. Mốc: CP2 19:30 Thứ Sáu 27/11 · CP3 10:00 Thứ Bảy 28/11 · CP4 14:30 Thứ Bảy 28/11 · hạn 23:59 Thứ Bảy 28/11.

### Nguyễn Hoa Thanh Tùng

Chạy trước: số liệu và câu thử phải có trước khi Dũng chạy bộ đánh giá

| Thứ tự | Việc | Issue | File chính | Xong khi |
|---|---|---|---|---|
| 1 | Chốt metric và chuẩn đạt | [#11](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/11) | `eval/metric_spec.yaml`, `spec.md` §7 | Đã chốt tại CP2 (27/11) |
| 2 | Chạy lại bằng chứng và đối chiếu số | [#5](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/5) | `evidence/` | Chạy `count_tutor.py`, khớp `summary.md` |
| 3 | Hoàn thiện data card | [#6](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/6) | `data/DATA_CARD.md` | 3 dataset đủ mục, nhãn đúng |
| 4 | Mở rộng bộ câu thử lên 20–30 câu | [#7](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/7) | `eval/benchmark.csv` | `run.py check` không còn cảnh báo số câu |
| 5 | Reflection cá nhân | [#15](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/15) | `reflection/nguyen-hoa-thanh-tung.md` | Hạn 23:59 Thứ Bảy |

### Vũ Trí Dũng

Chạy sau Tùng: đoạn bài thật rồi nối model, sau đó chạy đánh giá

| Thứ tự | Việc | Issue | File chính | Xong khi |
|---|---|---|---|---|
| 1 | Thay đoạn bài giả bằng đoạn bài thật | [#8](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/8) | `data/lessons/passages.csv` | 10–20 đoạn, nhãn `tu_viet` |
| 2 | Nối model thật vào `ai.py` | [#9](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/9) | `codebase/ai.py`, `.env` (không commit) | `run.py eval --try 3` có token > 0 |
| 3 | Chạy bộ đánh giá | [#10](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/10) | `eval/` | `run.py score` ra % đạt |
| 4 | Reflection cá nhân | [#16](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/16) | `reflection/vu-tri-dung.md` | Hạn 23:59 Thứ Bảy |

### Lưu Thanh Mỹ

Đội trưởng: giao diện và khảo sát, rồi làm slide; AWS và fix bug làm cùng Dương

| Thứ tự | Việc | Issue | File chính | Xong khi |
|---|---|---|---|---|
| 1 | Giao diện web cho bản chạy thử | [#1](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/1) | `codebase/web.py` | Chạy bằng `python run.py`, hiện mã đoạn và "Không có trong bài" |
| 2 | Khảo sát học viên về câu hỏi dưới video | [#2](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/2) | `evidence/survey/questions.md` | Rà xong bộ câu hỏi; thu ≥20 người (có thể chưa xong hôm nay) |
| 3 | Slide và kịch bản demo | [#3](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/3) | `slides/` | `demo-slides.pdf` ở gốc repo |
| 4 | Triển khai AWS (cùng Dương) | [#4](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/4) | `README.md` | Link demo chạy được; region đúng project |
| 5 | Reflection cá nhân | [#14](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/14) | `reflection/luu-thanh-my.md` | Hạn 23:59 Thứ Bảy |

### Khổng Tiến Dương

Chạy sau Dũng: chấm người thứ hai và chi phí; AWS và fix bug làm cùng Mỹ

| Thứ tự | Việc | Issue | File chính | Xong khi |
|---|---|---|---|---|
| 1 | Người thứ hai chấm 5 câu trả lời | [#12](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/12) | `eval/README.md` | Khớp ≥4/5 với người viết |
| 2 | Mô phỏng chi phí khi dùng thật | [#13](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/13) | `cost/` | `simulate` ≥50 phiên, có summary |
| 3 | Triển khai AWS (cùng Mỹ) | [#4](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/4) | `README.md` | Cùng Mỹ |
| 4 | Reflection cá nhân | [#17](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/17) | `reflection/khong-tien-duong.md` | Hạn 23:59 Thứ Bảy |

Khi xong việc, đóng issue tương ứng. Việc fix bug trong bản chạy thử và AWS chưa có issue: Mỹ và Dương mở issue riêng khi gặp lỗi.

## Chạy bản chạy thử

Cần **Python 3.10 trở lên** và Flask. Chạy các lệnh sau trong PowerShell từ thư mục gốc của repo.

```powershell
python -m pip install -r requirements.txt
python run.py check
$env:MODEL_PROVIDER = "fake"
python run.py
```

Mở [giao diện web trên máy](http://localhost:5000), nhập từng câu bên dưới rồi bấm **Gửi**. Dừng ứng dụng bằng Ctrl+C trong PowerShell.

| Câu nhập | Phản hồi đã kiểm tra qua giao diện web (`POST /ask`, HTTP 200) |
|---|---|
| Theo bài, trình tự học gồm các bước nào trước khi làm mini lab? | AI giả · [GIA-03] (GIẢ) Trình tự học của một bài: xem video, trả lời câu kiểm tra, rồi làm mini lab. |
| Sao Thổ có bao nhiêu vệ tinh? | Không có trong bài. Bạn có thể hỏi trợ giảng (TA) để được xác nhận. |

Hai câu trên dùng để kiểm tra luồng với AI giả. Kết quả đánh giá theo chuẩn §7 sẽ được ghi sau lượt chạy với model thật. [Hướng dẫn nối model](docs/connect-model.md)

| Lệnh | Làm gì |
|---|---|
| `python run.py eval --try` | Thử nối model: 3 câu đầu → `eval/run-try.csv` |
| `python run.py eval` | Chạy cả bộ → `eval/run-N.csv`, `traces/run-N.jsonl` |
| `python run.py score eval/run-1.csv` | Tính % đạt sau khi điền cột `pass` |
| `python run.py simulate --try` | Thử mô phỏng chi phí 10 phiên |
| `python run.py simulate` | Mô phỏng chi phí khi dùng thật (≥50 phiên) |

Không sửa `eval/run-*.csv` sau khi chạy. Lượt lỗi thì chạy lại thành lượt mới.

## Cấu trúc repo

| Thư mục / file | Nội dung |
|---|---|
| `spec.md` | Thiết kế, chuẩn đạt, phân công, changelog |
| `evidence/` | Bằng chứng pain: số đếm, script, phỏng vấn, khảo sát |
| `data/` | Data card; `data/lessons/` đoạn bài cho trợ giảng |
| `codebase/` | Luồng trả lời (`agent.py`), công cụ (`tools.py`), gọi model (`ai.py`) |
| `eval/` | Câu thử, metric, kết quả chạy, hồ sơ đánh giá |
| `cost/` | Persona và mô phỏng chi phí |
| `reflection/` | Phản hồi cá nhân từng thành viên |
| `docs/` | Khai báo dùng AI, hướng dẫn nối model |
| `slides/` | Dàn ý slide demo |

## Dùng AI vào việc gì

Claude soạn bản nháp khung code, script đếm bằng chứng, spec và câu thử. Nhóm kiểm và sửa từng phần. Chi tiết: [docs/ai-usage.md](docs/ai-usage.md).
