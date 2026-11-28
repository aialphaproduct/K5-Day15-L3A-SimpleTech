# Chạy lại và hoàn thiện bản nộp

Từ thư mục gốc repo, dùng Python 3.10+. Không cần truy cập hệ thống pre-class thật.

## Môi trường web và test đầy đủ

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe run.py
```

Nếu `.venv` đã có, bỏ lệnh tạo. Không cần activate hoặc đổi ExecutionPolicy. Dùng cùng interpreter cho cài và chạy. `ModuleNotFoundError: flask` nghĩa là Python đang chạy chưa có phụ thuộc; không sửa test bằng cách bỏ qua lỗi này. Máy hoàn thiện không tải được gói Flask từ nguồn pip hiện tại nên chưa xác minh test web.

Không có Flask vẫn chạy CLI `python codebase/app.py` (Enter hai lần để thoát), eval/simulate và audit; đây là đường kiểm lõi, không thay test giao diện.

## Kiểm lại bằng chứng đã lưu — không gọi model

```powershell
python run.py check
python eval/audit.py
python cost/audit.py
python evidence/count_tutor.py ../K5-L3-Day15-AI-Product-Hackathon/data/preclass
python eval/gate.py eval/run-5.csv --base eval/run-2.csv
```

Lệnh gate cuối **phải trả exit 1** cho lượt 5: 7/9 đủ điều kiện mã yêu cầu, B18 tụt; exit 1 này là phát hiện đúng, không phải test công cụ bị hỏng. Lượt 3 cũng bị chặn 8/9. Lượt 2 qua phần cơ học, chưa chứng nhận nghĩa hoặc cỡ mẫu 20 câu thường. `check` chỉ kiểm định dạng/nhãn nguồn, không xác nhận nguồn thật.

Hai script audit in ra stdout; muốn lưu thì dùng `--output <tên-mới>.md`. Chúng từ chối ghi đè. Không sửa artifacts lịch sử để đồng bộ với kết luận mới.

## Chạy một lượt AI thật mới

1. Nếu chưa có `.env`, chép `.env.example`, điền provider/model/key riêng. `codebase/ai.py` đã có phần gọi API, không cần chép lại code từ tài liệu starter.
2. Trong PowerShell, xoá override từ lúc thử fake: `Remove-Item Env:MODEL_PROVIDER -ErrorAction SilentlyContinue`. `load_env()` không ghi đè biến môi trường đã có.
3. Chạy `python run.py eval --try`; kiểm model thật và usage. Lượt thử không tính vào kết quả nộp.
4. Chạy `python run.py eval`. Giữ file mới, người phụ trách đọc output/đoạn nguồn và chỉ điền `pass`, `ghi_chu`; không sửa output, expected, token hoặc kết quả lượt cũ.
5. Chạy `python eval/gate.py eval/run-N.csv --base eval/run-5.csv` và ghi riêng các metric trong báo cáo mới. Không coi cổng cơ học là người chấm thứ hai.
6. Khi có lượt cùng cấu hình đã chấm, chạy `python run.py simulate --rate-from eval/run-N.csv` thành artifact mới; dùng audit với `--simulation`, `--evaluation`, `--benchmark` tương ứng. Tham số `--types` phải đúng nhóm đầu vào mô phỏng; mặc định `thuong kho` như khung gốc. Báo cáo không xác minh thay người dùng rằng prompt/kho đoạn của các lượt tuỳ chọn giống nhau.

Không sửa chuẩn CP2 hoặc benchmark cũ để giải quyết mâu thuẫn B06. Nếu thu thêm bộ câu để đủ mẫu/ngưỡng nguồn, lưu phiên bản mới riêng và ghi ngày thật; không gọi nó là chứng cứ đã có tại CP4. Nguồn ngoài nhóm, đoạn bài đối chiếu video, chấm nghĩa, reflection và biên nhận nộp vẫn cần người phụ trách xác nhận.
