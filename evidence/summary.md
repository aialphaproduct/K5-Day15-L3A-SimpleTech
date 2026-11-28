# Bằng chứng pain — A1 Trợ giảng bài học

> Số lấy từ `data/preclass/chat.csv` bằng `evidence/count_tutor.py` (chạy lại được; kết quả đầy đủ ở `evidence/tutor_counts.txt`). Không có tên, không có nội dung câu hỏi. Dữ liệu ẩn danh, 05/11 → 25/11/2026.

## Kết luận về ngưỡng (rubric R1)

| Nguồn | Trạng thái | Vai trò |
|---|---|---|
| Đào data (`chat.csv`) | Có x/N, cách đếm và script chạy lại được; chưa chứng minh phương pháp được ghi trước lần chạy đầu | **Nguồn hành vi chính**, còn giới hạn quy trình |
| Khảo sát | 17 phản hồi (15 học viên), dưới ngưỡng 20 | Nguồn thứ hai để đối chiếu |
| Phỏng vấn | Chỉ tính P1, P2; chưa đủ ngưỡng 3 người ngoài nhóm | Ví dụ minh hoạ |

Không khẳng định đã hoàn tất mọi điều kiện R1 chỉ từ bảng này: phần chọn mẫu ghi trước chưa có bằng chứng; nhật ký đo nhu cầu hỏi bài chứ không đo câu trả lời thiếu căn cứ. Hồ sơ cách đếm, năm mã dòng ví dụ và mẫu số: [data-mining.md](data-mining.md). Giả thuyết được hoàn thiện hồi cứu, không đăng ký trước: [hypothesis.md](hypothesis.md). Kiểm toán P3/P4/B17 và ngưỡng nguồn câu thử: [source-audit.md](source-audit.md).

## Cách chọn mẫu và cách đếm

*Mục này ghi bổ sung ngày 28/11, sau khi script đã chạy.*

- **File:** `data/preclass/chat.csv` của BTC, toàn bộ cửa sổ 05/11 → 25/11/2026 (1.260 dòng).
- **Lọc:** `agent_id == "teaching_assistant"` và `kind == "question"` → **1.091 câu**.
- **Mẫu số:** số câu hỏi đã lọc (N = 1.091) hoặc số học viên có ≥1 câu đã lọc (N = 143).
- **Ngày học:** lấy từ cột `transcript` (1.090/1.091 dòng có giá trị).
- **Chạy lại:** `python evidence/count_tutor.py <thư mục data/preclass>`; bản script hoàn thiện cuối chỉ dùng thư viện chuẩn Python. Data BTC giữ ở repo đề, không copy nguyên file vào repo nhóm. Trong đợt hoàn thiện cuối đã đối chiếu độc lập bằng `csv`/`collections`/`statistics`, khớp các số tổng hợp dưới đây.

## Số đo từ data

| Chỉ số | Giá trị |
|---|---|
| Câu hỏi gửi trợ giảng AI dưới video | 1.091 câu |
| Học viên có ≥1 câu hỏi | 143 học viên |
| Học viên chỉ hỏi đúng 1 câu | 38 (26,6%) |
| Median câu hỏi / học viên | 4 (max 72) |
| Top 10% học viên hỏi nhiều nhất | 43,3% câu hỏi |
| Câu hỏi ở Day01 | 333/1.091 (30,5%; làm tròn 31%) |
| 3 video Day01 có nhiều câu hỏi nhất | 269/1.091 (24,7%; làm tròn 25%) |
| Câu có ghi `ngu_canh` (BTC chỉ ghi trường này từ 25/11) | 9/1.091 |
| Câu có dùng gợi ý đã duyệt | 45,1% |

## Đọc số thế nào

- **Câu hỏi tập trung ở đầu khoá và vài video.** Day01 có nhiều câu nhất; ba video đầu của Day01 chiếm một phần lớn. Chưa biết vì sao (bài khó, video không rõ, hay chỉ là nhiều học viên mới). Cần phỏng vấn học viên để biết.
- **Một nhóm nhỏ hỏi rất nhiều.** 10% học viên hỏi gần nửa số câu. Chưa rõ họ là người cần giúp nhất hay đang dùng trợ giảng thay cho việc đọc bài.
- **`ngu_canh` không dùng để kết luận.** Từ điển cột của BTC ghi trường này để trống với mọi dòng trước 25/11. Con số 9/1.091 phản ánh thời điểm bắt đầu ghi, không cho biết trợ giảng có dựa vào đoạn bài hay không.
- **Data không có nội dung câu hỏi và câu trả lời.** Không đo được chất lượng câu trả lời từ data. Chất lượng phải đo bằng bộ câu thử (`eval/benchmark.csv`) và người chấm.

## Nguồn thứ hai: khảo sát (n = 17)

Log từng câu trả lời: [survey/result-survey1.md](survey/result-survey1.md). Thu ngày 27/11. Người trả lời: 13 L3A, 2 L3B, 2 lab coach (gồm 1 ghi "LC"); Nhóm xác nhận (28/11) tất cả người trả lời đã học khoá và do thành viên nhóm trực tiếp đi khảo sát.

| Câu hỏi | Kết quả |
|---|---|
| Kiểm lại câu trả lời trong bài: "có nhưng mất công tìm" hoặc "không" | 15/17 (13 + 2); tính riêng học viên: 14/15 |
| Mất từ 5 phút trở lên để hiểu ở lần gần nhất | 13/17 |
| Chỉ hiểu một phần | 11/17 |
| Đã hỏi trợ giảng AI dưới video ở lần gần nhất | 6/17 |
| Đã tua lại video | 12/17 |

**Khớp và lệch so với data:** data cho thấy học viên hỏi trợ giảng nhiều (1.091 câu trong 21 ngày); khảo sát cho thấy phải tốn công tìm lại chỗ trong bài để kiểm là phổ biến. Khảo sát cũng cho thấy phần lớn người trả lời (11/17) không dùng trợ giảng AI ở lần gần nhất, nên không quy khó khăn này thành lỗi của trợ giảng.

## Trích dẫn nguyên văn (giữ nguyên chính tả)

1. "ngoài câu trả lời sẵn có, nó ko giải thích sâu về điều tôi định hỏi ." (khảo sát, dòng 2, L3A)
2. "Câu trả lời dùng những thuật ngữ mình chưa biết, khiến mình cần phải tìm hiểu thuật ngữ đó rồi mới tiếp tục đọc để hiểu câu trả lời." (khảo sát, dòng 3, L3A; cùng người với [P1](interviews/P1.md))
3. "nội dung chưa khái quát" (khảo sát, dòng 8, L3A)
4. "Khi chưa tìm ra được đáp án chính xác trong bài giảng/video" (khảo sát, dòng 9, L3A)
5. "Mình lười gõ lại công thức lắm, chụp bụp cái màn hình slide ném sang Claude hỏi cho nhanh, chứ gõ chữ dưới video không biết nó có nhìn thấy hình trên slide không." ([P2](interviews/P2.md), L3B)
6. "chưa chắc thông tin được học có đúng so với khóa chính thức của chương trình không" (khảo sát, dòng 14, L3A)
7. "Khổ lắm không dùng ạ" (khảo sát, dòng 16, L3A)

## Giới hạn

- Data không có nội dung câu hỏi và câu trả lời, cũng không cho biết câu trả lời đúng hay sai. Chất lượng đo bằng bộ câu thử và người chấm.
- Một nhóm nhỏ hỏi rất nhiều: 10% học viên hỏi 43,3% số câu. Chưa biết vì sao.
- Câu hỏi tập trung ở Day01; có thể do đông học viên hơn, không hẳn do bài khó.
- [P3](interviews/P3.md) là tự thuật của thành viên nhóm nên **không tính** là bằng chứng.
- [P4](interviews/P4.md): nhóm xác nhận lại ngày 28/11 sau CP4 là phỏng vấn thật. Commit `fe63ef6` từng ghi dữ liệu giả lập, `5275583` đổi sang xác nhận của nhóm; repo chưa có ghi chép gốc. Số đã công bố trong tài liệu này **chưa cộng P4** để không đổi số bằng chứng sau CP4; nếu người chấm chấp nhận thì bản ghi phỏng vấn là P1, P2, P4 (P1 trùng khảo sát dòng 3). Xem [source-audit.md](source-audit.md).
- P1 trùng người trả lời khảo sát dòng 3, không đếm hai lần; hai giá trị thời điểm/tần suất của P1 đang mâu thuẫn nên không dùng cho công thức impact.
- Việc chọn mẫu được ghi lại sau lần chạy đầu; chưa có hồ sơ đăng ký trước. Không sửa lịch sử để che giới hạn này.
