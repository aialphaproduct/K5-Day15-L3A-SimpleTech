# Hoàn thiện bản nộp — feat/final

Phạm vi: đối chiếu rubric và sửa tài liệu sau CP4 ngày 28/11/2026. Nhánh bắt đầu từ `develop` tại `3f51028`. Không thay chuẩn CP2, bộ câu thử, đáp án, output, token hoặc điểm lịch sử. Reflection của Mỹ được giữ nguyên theo yêu cầu; reflection Tùng được xử lý cuối.

## Những phần đã xử lý trong repo

- Điền hồ sơ giả thuyết và đào data, ghi đúng là tổng hợp hồi cứu; bổ sung ví dụ từ dòng data thật, không tạo bằng chứng đăng ký trước.
- Kiểm toán P3/P4/B17; tách nhãn nguồn lịch sử và nguồn ngoài nhóm đã có hồ sơ: **4/23**, cần **8/23**.
- Tạo `eval/audit.py` và báo cáo `eval/final-audit.md`; tách `pass` khỏi điều kiện mã CP2, không tự chấm nghĩa.
- Sửa kết luận lượt 3: mã **8/9 <90%**; lượt 4–5 có **7/9** đủ mã yêu cầu. Metric đúng ý còn **9/20** câu thường.
- Đồng bộ canvas, README, hồ sơ eval, data card, chi phí và slide với giới hạn thực tế.
- Bổ sung so sánh ba hướng có số từ khảo sát/data, ghi rõ so sánh hồi cứu và mẫu chồng nhau.
- Script `count_tutor.py` dùng thư viện chuẩn; kiểm lại số 1.091 câu, 143 người, 333 Day01, top ba video 269, top 10% người hỏi chiếm 43,3%.

## Việc cần dữ liệu hoặc xác nhận thật

| Phần | Hiện có | Cần thêm để công nhận |
|---|---|---|
| Nguồn benchmark R4 | 4/23 câu từ P1/P2; B17 chưa xác minh; P4 nhóm xác nhận lại sau CP4, chưa có ghi chép gốc (nếu chấp nhận: 6/23); P3 thuộc nhóm | Ghi chép gốc/xác nhận nguồn hợp lệ; kể cả xác minh B17 và hai câu P4 cũng chỉ 7/23, vẫn thiếu ≥1 câu ngoài nhóm |
| Ngưỡng nguồn pain R1 | Data thật có số và script; hồ sơ chọn mẫu được bổ sung sau khi chạy | Không thể tạo lại việc đăng ký trước. Để củng cố nguồn độc lập: ≥3 phỏng vấn hợp lệ hoặc ≥20 khảo sát đúng đối tượng ngoài nhóm, giữ log thật |
| Chấm metric | Mẫu 9 câu thường; lượt 2 có báo cáo người thứ hai khớp 5/5 | Mẫu đủ 20 câu thường theo chuẩn đã chốt, chấm nghĩa; lượt mới ghi riêng, không thay kết quả CP4 |
| Đoạn bài | 28 đoạn tự viết; D01-09–D01-16 chờ đối chiếu | Người có quyền truy cập video đối chiếu từng đoạn, ghi người kiểm/thời điểm/căn cứ |
| Lượt 4–5 | Điểm AI chấm tạm | Người phụ trách đọc input/output/đoạn nguồn xác nhận vào pass/ghi_chu theo luật |
| Chạy AI thật mới | Máy hoàn thiện không có `.env` hoặc API key | Cấu hình key riêng rồi chạy eval/simulate thành lượt mới; không dùng fake để điền thiếu |
| Bonus dùng thử | Chưa có phiên quan sát nào trong `validation/log.md` | ≥2 người ngoài nhóm dùng thật, ghi quan sát/trích dẫn và thay đổi; không lấy phỏng vấn pain thay thế |
| Reflection Tùng | Đã biên soạn cuối đợt sau các tài liệu/kiểm tra, bỏ chỗ trống; có phần công việc và phân tích lỗi dựa trên Git | Tùng xác nhận công cụ/thao tác cá nhân và lỗi AI đã tự sửa; không coi bản thảo là tự thuật đã duyệt |
| Reflection Mỹ | Bản nháp đã có | Giữ nguyên theo yêu cầu phiên này |
| Checkpoint và demo | CP1.md tự ghi đã nộp; repo có lịch sử, PDF, link video | Biên nhận form CP2–CP4, phát video ẩn danh và demo câu lạ tại máy trình bày; không thể suy đúng hạn từ file hiện tại |

Không tuyên bố hoàn tất các hàng cần người thật chỉ bằng việc sửa tài liệu. Kết quả thấp được công bố trung thực vẫn được chấm theo rubric.

## Kiểm tra truy cập và môi trường

- GitHub đọc công khai được tại `https://github.com/aialphaproduct/K5-Day15-L3A-SimpleTech`; trang `main` được dịch vụ đọc trả về còn nội dung bản đầu. Bản `feat/final` tại máy chưa được push; cần kiểm đúng nhánh/commit nộp sau khi xuất bản.
- Hai link YouTube có trong README; công cụ đọc web trả `Cache miss`, chưa chứng minh quyền xem hoặc phát được. Người trình bày cần thử cửa sổ ẩn danh.
- Python hiện tại thiếu Flask; cài từ mạng bị chặn. `requirements.txt` đã khai báo Flask. Test phụ thuộc Flask phải được chạy lại khi có môi trường đủ thư viện; không ghi các lỗi import này thành lỗi logic sản phẩm.
- Không có cấu hình API thật trong môi trường hoàn thiện; không tạo thêm lượt model hoặc mô phỏng giả.

## Kết quả kiểm tra bản sửa trước đợt review

- `python run.py check`: hợp lệ cấu trúc 23 câu, 3 metric, 4 thành viên. Không xác nhận chất lượng hay nguồn thật.
- 33/33 test không phụ thuộc Flask đạt, gồm các test kiểm toán và số đếm mới. Chạy toàn bộ khám phá 36 mục: 33 đạt, 3 lỗi import do thiếu Flask, không có assertion thất bại. Cần cài đúng phụ thuộc rồi chạy lại toàn bộ.
- `python eval/audit.py` tái tạo khớp nội dung `eval/final-audit.md`; counter tái lập được số liệu chính từ data BTC.
- PDF xuất lại 18 trang, trích được văn bản; đã xem tổng thể và trang đánh giá để kiểm bố cục và nội dung sửa.
- Chuẩn CP2, hai benchmark, kết quả CSV/trace lịch sử và reflection Mỹ không đổi so với đầu nhánh. Thay đổi sau CP4 được ghi trong spec §10.

## Lệnh tái lập

```powershell
python -m pip install -r requirements.txt
python run.py check
python -m unittest discover -s tests
python eval/audit.py
python evidence/count_tutor.py ../K5-L3-Day15-AI-Product-Hackathon/data/preclass
python evidence/count_personas.py ../K5-L3-Day15-AI-Product-Hackathon/data/preclass
```

`python eval/audit.py` không gọi model hoặc sửa dữ liệu. Báo cáo mới: `python eval/audit.py --output eval/final-audit-v2.md` (từ chối ghi đè). Giữ bộ 23 câu để đối chiếu các lượt trước CP4; nếu bổ sung câu hoặc xác minh nguồn thì ghi phiên bản và changelog mới.

## Đợt sửa theo review — sau CP4 ngày 28/11/2026

- Sửa `eval/gate.py` để kiểm đúng một bộ câu đầy đủ, từ chối lượt rỗng/thiếu/trùng/ID lạ, sai type/run ID hoặc lỗi kỹ thuật. Tách điều kiện mã CP2 khỏi điểm từng câu: lượt 2 qua **phần cơ học**; lượt 3 bị chặn **8/9**; lượt 5 bị chặn **7/9** và ghi nhận B18 tụt. Cổng không xác nhận ngữ nghĩa, nguồn thật hay mẫu 20 câu thường; mâu thuẫn B06 vẫn được công khai, không sửa chuẩn hồi tố.
- Thêm `cost/audit.py` và [task-cost-audit.md](../cost/task-cost-audit.md): **1 task = 1 câu hỏi**, 48 phiên hợp lệ có **122 câu**; lấy tỷ lệ eval đúng nhóm `thuong`/`kho` là **19/20**, cho **$0.00021798/câu đạt ước tính**. Kịch bản cơ sở vẫn **$0.97754625/tháng**. Đây là proxy theo cấu hình lượt 2, không phải kết quả chấm trực tiếp đầu ra mô phỏng hay chi phí đã đo của bản cuối.
- CLI chi phí đối chiếu đầy đủ ID/type với benchmark, kiểm model và usage, khai báo phiên lỗi; không tính chi phí/câu đạt cho model chỉ đổi đơn giá. Review độc lập phát hiện hai lỗi về bỏ câu trượt và gán nhầm cấu hình lượt 2 cho đầu vào tuỳ chọn; cả hai đã được sửa, thêm test và review lại.
- Đồng bộ README, khai báo AI, hướng dẫn nối model và [docs/reproduce.md](reproduce.md). Sửa mô tả phụ thuộc: web cần Flask, CLI/eval/simulate/audit dùng thư viện chuẩn. Có hướng dẫn dùng cùng interpreter và xoá override `MODEL_PROVIDER=fake` trước khi chạy AI thật.
- Xuất lại PDF **18 trang, 359.193 byte** với số chi phí/câu mới. Trang chi phí đã được kiểm bằng ảnh chụp từ HTML in PDF, không thấy tràn nội dung; đây là bản sửa sau CP4, không chứng minh thời điểm nộp.

### Kiểm tra mới nhất

- **50/50 test không phụ thuộc Flask đạt.** Toàn bộ `unittest discover` có 53 mục: 50 đạt, 3 module lỗi import do thiếu Flask (`test_auth_keys`, `test_insights`, `test_web`); chưa thể tuyên bố toàn bộ test đạt. Trong đó có 12 test gate, 10 test cost audit và 5 test improve đạt.
- `python run.py check` đạt kiểm tra cấu trúc. `git diff --check` không báo lỗi khoảng trắng. Hash SHA-256 **21/21 artifact được bảo vệ không đổi** trong đợt sửa: chuẩn/benchmark, CSV, trace và các file khung được theo dõi.
- Cài Flask bằng pip trong `.venv` vẫn thất bại vì nguồn gói hiện tại không trả về distribution phù hợp. Không sửa test để che lỗi môi trường. Chưa có `.env`/key để chạy lượt eval hoặc mô phỏng AI thật mới.
- Git còn nhiều file sửa và file mới; đợt này không stage, commit hoặc push. Cần giữ cả file mới khi chuẩn bị bản nộp, kiểm lại đúng nhánh/commit được gửi.

### Phần vẫn cần hoàn thành bằng bằng chứng thật

Nguồn benchmark mới xác minh 4/23, ngưỡng nguồn pain, đối chiếu tám đoạn bài, chấm ngữ nghĩa/mẫu 20 câu thường, xác nhận lượt 4–5, reflection của chính tác giả và bằng chứng checkpoint/demo vẫn mở như bảng trên. Bonus dùng thử chưa thực hiện. Các công cụ và tài liệu sửa xong không biến các mục này thành đã đạt; chưa đủ căn cứ tuyên bố hoàn tất toàn bộ yêu cầu hackathon.
