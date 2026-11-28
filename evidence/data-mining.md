# Đào data — phương pháp và kết quả có thể kiểm lại

**Ghi bổ sung hồi cứu ngày 28/11/2026.** Bản mẫu trước lần hoàn thiện cuối còn trống; `summary.md` cũng ghi phương pháp được bổ sung sau khi script đã chạy. Tài liệu này làm rõ cách tái lập, không chứng minh yêu cầu “ghi cách chọn mẫu trước khi đọc/chạy”. Không sửa thời điểm hay kết quả cũ để tạo bằng chứng đăng ký trước.

## 1. Nguồn, bộ lọc và mẫu số

- Nguồn: `data/preclass/chat.csv` trong repo đề BTC, nhật ký thật đã ẩn danh từ 05/11 đến 25/11/2026, 1.260 dòng; không sao chép nguyên file vào repo nhóm.
- Phạm vi: dùng toàn bộ cửa sổ BTC cấp, không chọn riêng các học viên hay video có kết quả thuận lợi.
- Lọc: `agent_id == "teaching_assistant"` và `kind == "question"`, giữ 1.091 dòng.
- Mẫu số theo câu hỏi: **N = 1.091**, kể cả một dòng không có `transcript`. Mẫu số theo người: **N = 143** mã `hv` phân biệt trong tập đã lọc.
- Nhóm ngày: trích `DayNN` từ `transcript`; một dòng thiếu `transcript` không được gán ngày.
- Top 10% người hỏi: lấy `round(143 × 0,10) = 14` người nhiều câu nhất; chỉ công bố tổng hợp, không xếp hạng hay công bố mã học viên.
- Script tái lập: [count_tutor.py](count_tutor.py). Từ thư mục gốc repo nhóm, chạy `python evidence/count_tutor.py ../K5-L3-Day15-AI-Product-Hackathon/data/preclass`. Bản hoàn thiện cuối dùng thư viện chuẩn Python, không cần `pandas`; kết quả lịch sử giữ nguyên ở [tutor_counts.txt](tutor_counts.txt).
- Kiểm độc lập trong đợt hoàn thiện cuối bằng `csv`, `collections`, `statistics` của Python: cùng bộ lọc và mẫu số cho lại các số trong bảng dưới. Không sửa file kết quả lịch sử.

## 2. Kết quả

| Đếm gì | x / N | Tỷ lệ | Diễn giải được |
|---|---:|---:|---|
| Dòng là câu hỏi trợ giảng | 1.091 / 1.260 | 86,6% | Phân loại lượt chat trong data pack |
| Người đã hỏi / người có hoạt động | 143 / 436 | 32,8% | Mức sử dụng, không phải tỷ lệ người gặp pain |
| Người chỉ hỏi một câu | 38 / 143 | 26,6% | Tần suất sử dụng phân tán |
| Câu hỏi của 14 người hỏi nhiều nhất | 472 / 1.091 | 43,3% | Số câu tập trung vào một nhóm nhỏ |
| Câu hỏi Day01 | 333 / 1.091 | 30,5% | Tập trung ở đầu khoá; chưa biết nguyên nhân |
| Ba video Day01 nhiều câu nhất | 269 / 1.091 | 24,7% | `v02`: 115, `v01`: 86, `v05`: 68 |
| Câu có dùng gợi ý đã duyệt | 492 / 1.091 | 45,1% | `guidance_ids` khác rỗng/`[]` |
| Câu dùng cache | 15 / 1.091 | 1,4% | `cached == True` |
| Dòng có ghi `ngu_canh` | 9 / 1.091 | 0,8% | Trường chỉ bắt đầu ghi từ 25/11; không suy ra thiếu căn cứ |

Median số câu/người là **4**, tối đa **72**. Quy mô **436 người có hoạt động / 721 tài khoản** lấy từ README data pack của BTC; không thay 436 bằng 721 khi mô tả tỷ lệ sử dụng trong nhóm hoạt động.

## 3. Năm ví dụ thật để đối chiếu dòng

Năm dòng đầu sau bộ lọc, theo đúng thứ tự file BTC; đây là ví dụ metadata, không phải lời học viên hay bằng chứng câu trả lời sai. Mã đã được BTC thay mới. Chỉ giữ vài trường để kiểm bộ lọc, không công bố mã người dùng.

| Mã dòng trong `chat.csv` | `transcript` | `kind` | `agent_id` | Độ dài câu hỏi / trả lời (ký tự) |
|---|---|---|---|---:|
| C00983 | Day01/d01-r1-v05.txt | question | teaching_assistant | 29 / 182 |
| C00581 | Day01/d01-r1-v02.txt | question | teaching_assistant | 82 / 388 |
| C00499 | Day01/d01-r1-v02.txt | question | teaching_assistant | 183 / 401 |
| C01138 | Day01/d01-r1-v02.txt | question | teaching_assistant | 154 / 431 |
| C01085 | Day01/d01-r1-v02.txt | question | teaching_assistant | 37 / 379 |

Các trích dẫn nguyên văn về pain đến từ khảo sát và P2, có nguồn ở [summary.md](summary.md); không dựng nội dung từ các độ dài trong bảng này.

## 4. Giới hạn và kiểm chéo

- Nhật ký không chứa nội dung câu hỏi/trả lời, nên không đếm được tỷ lệ trả lời sai, thiếu nguồn hay học viên không hiểu.
- Ô `ngu_canh` trước 25/11 để trống do thời điểm bắt đầu ghi; 9/1.091 không phải tỷ lệ trợ giảng có căn cứ.
- Câu hỏi tập trung ở Day01 có thể do đông người học hơn, chưa cho biết bài khó hơn hay video kém hơn.
- Khảo sát hiện có 17 phản hồi, chưa đạt ngưỡng 20; P1/P2 là hai bản ghi được dùng để minh hoạ, chưa đủ ba người ngoài nhóm. P1 còn mâu thuẫn thời điểm/tần suất, không dùng hai giá trị đó để suy rộng.
- Dữ liệu thật hỗ trợ nhu cầu hỏi bài; tín hiệu khó kiểm chứng đến từ nguồn người dùng nhỏ. Chưa coi mọi học viên hỏi bài là người chịu pain hay mọi lượt hỏi là thời gian sẽ tiết kiệm.
- Chưa chứng minh được cách chọn mẫu đã ghi trước lần chạy đầu. Giới hạn này vẫn mở; không thể khắc phục bằng cách ghi lùi ngày.
