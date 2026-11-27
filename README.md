# Simple Tech — Trợ giảng bài học (A1)

Nhóm **Simple Tech** · Lớp **L3A** · Track **A (EdTech)** · Khoá AI20K K5, hackathon Day 15.

Bản chạy thử trả lời câu hỏi của học viên dưới video pre-class. Mỗi câu trả lời phải kèm **mã đoạn bài** để học viên mở đúng chỗ kiểm lại. Nếu bài không nói tới, trợ giảng nói **"Không có trong bài"** và chuyển tới trợ giảng (TA), không đoán.

Thành viên, mã học viên, vai trò: [TEAMS.md](TEAMS.md). Thiết kế đầy đủ: [spec.md](spec.md).

## Vấn đề

Trong 05/11–25/11/2026, học viên gửi **1.091 câu hỏi** cho trợ giảng AI dưới video từ 143 người. 31% câu hỏi nằm ở Day01; ba video đầu của Day01 chiếm 25%. Chỉ 9/1.091 lượt có ghi đoạn bài AI đã dựa vào, nên gần như không kiểm lại được câu trả lời. Chi tiết và cách đếm: [evidence/summary.md](evidence/summary.md), chạy lại được bằng [evidence/count_tutor.py](evidence/count_tutor.py).

## Giải pháp

- Tìm đoạn bài liên quan tới câu hỏi (`search_passages`).
- Không có đoạn khớp → trả lời "Không có trong bài", không gọi model.
- Có đoạn → model trả lời, mỗi khẳng định kèm mã đoạn `[MÃ]`.
- Code kiểm lại: mã trích dẫn phải thuộc đúng các đoạn đã tìm, nếu không thì không đưa câu trả lời của model.

Không làm: chấm bài, làm bài hộ, trả lời lịch/điểm/hạn của từng học viên, gửi tin ra ngoài.

## Đo chất lượng

- Bộ câu thử: [eval/benchmark.csv](eval/benchmark.csv) (thuong / kho / tu_choi).
- Metric: [eval/metric_spec.yaml](eval/metric_spec.yaml) — `trich_dung_ma`, `khong_bia`, `dung_y_tra_loi`.
- Chuẩn "đạt" (đề xuất, chốt trước CP2): ≥90% câu thuong có mã đúng; 100% câu tu_choi không làm hộ; ≥80% câu kho không bịa.

## Trạng thái

| Phần | Trạng thái |
|---|---|
| Khung luồng trả lời và kiểm mã | Có (`codebase/agent.py`, `codebase/tools.py`) |
| Đoạn bài | **Giả** (`data/lessons/passages.csv`, 5 đoạn). Đang thay bằng đoạn bài thật đã viết lại |
| Nối model thật | **Chưa.** Đang chạy chế độ giả (`codebase/ai.py`) |
| Bộ câu thử | 14 câu, toàn `tu_viet`. Cần 20–30 câu, ≥1/3 từ người dùng hoặc data thật |
| Khảo sát / phỏng vấn học viên | Đang làm |
| Chi phí khi dùng thật | Chưa mô phỏng |
| Slide, demo, triển khai AWS | Đang làm |

Việc đang mở: [Issues](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues).

## Phân công

Sắp theo thứ tự hạn: CP2 → CP3 → CP4 → reflection. Mỗi việc có một issue; tick việc trong issue khi xong. Mốc: CP2 19:30 Thứ Sáu 27/11 · CP3 10:00 Thứ Bảy 28/11 · CP4 14:30 Thứ Bảy 28/11 · hạn 23:59 Thứ Bảy 28/11.

| Người | Vai trò | Việc | Issue | File chính | Hạn | Trạng thái |
|---|---|---|---|---|---|---|
| Khổng Tiến Dương | Thành viên | Chốt metric và chuẩn đạt | [#11](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/11) | `eval/metric_spec.yaml`, `spec.md` §7 | CP2 19:30 Thứ Sáu | Chưa bắt đầu |
| Lưu Thanh Mỹ | Đội trưởng | Khảo sát học viên về câu hỏi dưới video | [#2](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/2) | `evidence/survey/` | CP2 (bắt đầu sớm) | Chưa bắt đầu |
| Lưu Thanh Mỹ | Đội trưởng | Giao diện web cho bản chạy thử | [#1](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/1) | `codebase/app.py` | CP3 | Chưa bắt đầu |
| Nguyễn Hoa Thanh Tùng | Thành viên | Chạy lại bằng chứng và đối chiếu số | [#5](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/5) | `evidence/` | CP3 | Chưa bắt đầu |
| Nguyễn Hoa Thanh Tùng | Thành viên | Hoàn thiện data card | [#6](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/6) | `data/DATA_CARD.md` | CP3 | Chưa bắt đầu |
| Nguyễn Hoa Thanh Tùng | Thành viên | Mở rộng bộ câu thử lên 20–30 câu | [#7](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/7) | `eval/benchmark.csv` | CP3 | Chưa bắt đầu |
| Vũ Trí Dũng | Thành viên | Thay đoạn bài giả bằng đoạn bài thật | [#8](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/8) | `data/lessons/passages.csv` | CP3 (nên sớm) | Chưa bắt đầu |
| Vũ Trí Dũng | Thành viên | Nối model thật vào `ai.py` | [#9](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/9) | `codebase/ai.py` | CP3 | Chưa bắt đầu |
| Khổng Tiến Dương | Thành viên | Người thứ hai chấm 5 câu trả lời | [#12](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/12) | `eval/README.md` | CP3 | Chưa bắt đầu |
| Lưu Thanh Mỹ | Đội trưởng | Slide và kịch bản demo | [#3](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/3) | `slides/` | CP4 | Chưa bắt đầu |
| Lưu Thanh Mỹ | Đội trưởng | Triển khai AWS (theo region của project) | [#4](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/4) | `README.md` | CP4 | Chưa bắt đầu |
| Vũ Trí Dũng | Thành viên | Chạy bộ đánh giá | [#10](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/10) | `eval/` | CP4 (lượt 2) | Chưa bắt đầu |
| Khổng Tiến Dương | Thành viên | Mô phỏng chi phí khi dùng thật | [#13](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/13) | `cost/` | CP4 | Chưa bắt đầu |
| Lưu Thanh Mỹ | Đội trưởng | Reflection cá nhân | [#14](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/14) | `reflection/luu-thanh-my.md` | 23:59 Thứ Bảy | Chưa bắt đầu |
| Nguyễn Hoa Thanh Tùng | Thành viên | Reflection cá nhân | [#15](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/15) | `reflection/nguyen-hoa-thanh-tung.md` | 23:59 Thứ Bảy | Chưa bắt đầu |
| Vũ Trí Dũng | Thành viên | Reflection cá nhân | [#16](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/16) | `reflection/vu-tri-dung.md` | 23:59 Thứ Bảy | Chưa bắt đầu |
| Khổng Tiến Dương | Thành viên | Reflection cá nhân | [#17](https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech/issues/17) | `reflection/khong-tien-duong.md` | 23:59 Thứ Bảy | Chưa bắt đầu |

Ghi chú: Khi xong việc, đổi trạng thái trong bảng và đóng issue tương ứng.

## Chạy bản chạy thử

Cần **Python 3.10 trở lên**. Không cần `pip install`.

```powershell
python run.py                 # chạy thử: gõ câu hỏi, nhận trả lời (chế độ giả, chưa gọi model)
python run.py check           # kiểm bộ câu thử, metric và TEAMS.md
python run.py eval --fake     # thử bộ chạy, không gọi agent
```

Máy dùng `python3` (macOS/Linux) hoặc `py` (Windows) thì gõ thay. Nối model thật: chép `.env.example` thành `.env`, điền khoá của nhóm theo [docs/connect-model.md](docs/connect-model.md). **Không commit `.env` hay key.**

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
