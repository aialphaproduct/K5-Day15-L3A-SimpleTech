# Chi phí khi dùng thật

> Bản hoàn thiện sau CP4: giữ nguyên các bảng mô phỏng lịch sử, bổ sung điều kiện áp dụng và giới hạn. Không đổi file `simulate-1.csv`, summary đã sinh hay trace.
> Số **không điền tay**: điền `cost/personas.yaml` → `python run.py simulate --rate-from eval/run-2.csv` → chép bảng trong `cost/simulate-1-summary.md` vào đây.
> Lúc build dùng gói miễn phí vẫn tính theo **giá gói trả phí** — đây là chi phí cho lúc đưa vào dùng thật.

## 1. Đầu vào

- **Persona** (`cost/personas.yaml`, đo bằng [evidence/count_personas.py](../evidence/count_personas.py) trên `data/preclass/chat.csv` cửa sổ 05/11–25/11/2026 = 21 ngày, ngắt phiên khi nghỉ > 30 phút, quy đổi 21 → 30 ngày bằng `× 30 / 21`):
  - `dung_it` (1–2 câu): `share 0.38` (54/143 = 37,8%), `1.5` phiên/tháng, `1` lượt/phiên.
  - `dung_vua` (3–10 câu): `share 0.43` (61/143 = 42,7%), `2.8` phiên/tháng, `3` lượt/phiên.
  - `dung_nhieu` (≥11 câu): `share 0.19` (28/143 = 19,6%), `7.0` phiên/tháng, `5` lượt/phiên.
- **Số người dùng thật** 3 kịch bản (nguồn: `data/preclass/README.md`, `learners.csv`, `chat.csv`): thấp **143** (đã hỏi trợ giảng trong 21 ngày) · cơ sở **436** (học viên có hoạt động trên pre-class) · cao **721** (tổng tài khoản AI20K K5).
- **Giá** 2 mức model từ `further-reading/model-prices.md` trong repo đề (Google Gemini API, https://ai.google.dev/gemini-api/docs/pricing, BTC ghi ngày kiểm 25/11/2026). Đây là **ảnh chụp giá của BTC**, chưa được nhóm kiểm độc lập với bảng giá hiện hành trong đợt hoàn thiện này:
  - `gemini-3.1-flash-lite` (tầng Nhỏ): vào `$0.25` / ra `$1.50` trên 1M token.
  - `gemini-4-hydrogen` (tầng Lớn, cùng hãng Gemini): vào `$1.50` / ra `$7.50` trên 1M token.
- **Tỉ lệ đạt** dùng để tính: **22/23 (96%) theo từng câu thử** — lượt `run-2@20261127-215239` ([eval/run-2.csv](../eval/run-2.csv), chạy cùng model `gemini-3.1-flash-lite`). Không phải tỷ lệ hoàn thành trọn phiên nhiều lượt, cũng không chứng minh mọi metric CP2 đã đủ mẫu.
- **Cấu hình được đo:** prompt/công cụ lượt 2, kho **20 đoạn**, trước khi bổ sung thành 28 đoạn. Bảng này không phải mô phỏng lại bản cuối.
- **Đo token trên model `gemini-3.1-flash-lite`, tính giá model `gemini-3.1-flash-lite` và `gemini-4-hydrogen`**. Model lớn là kịch bản **chỉ đổi đơn giá**; chưa chạy model đó để đo token, tỷ lệ đạt hoặc chi phí/task thành công thực tế.

## 2. Kết quả mô phỏng

Lượt mô phỏng: [cost/simulate-1.csv](simulate-1.csv) · Run ID `simulate-1@20261128-012032` · **50 phiên** (48 phiên hợp lệ; 2 phiên lỗi kỹ thuật `S013`, `S022` không tính vào trung bình) · seed `42` · trace: [traces/simulate-1.jsonl](../traces/simulate-1.jsonl).

*(Bảng chép nguyên văn từ [cost/simulate-1-summary.md](simulate-1-summary.md))*

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| dung_it | 22 | 1 | 581 | 41 | 1.0 | 1.0 |
| dung_vua | 15 | 3 | 1734 | 126 | 3.0 | 3.0 |
| dung_nhieu | 11 | 5 | 2890 | 207 | 5.0 | 5.0 |

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (143 người) | Chi phí / tháng — cơ sở (436 người) | Chi phí / tháng — cao (721 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gemini-3.1-flash-lite (vào 0.25 · ra 1.5 $/1M) | $0.00053 | $0.00055 | $0.00022 | $0.3206 | $0.9775 | $1.62 | $0.0022 |
| gemini-4-hydrogen (vào 1.5 · ra 7.5 $/1M) | $0.0030 | $0.0031 | $0.0012 | $1.83 | $5.57 | $9.21 | $0.0128 |

**Cách đọc bảng lịch sử:** cột “Chi phí / task thành công” do khung tính bằng chi phí trung bình mỗi phiên ÷ tỷ lệ đạt **từng câu** `22/23` (hiển thị làm tròn 96%). Vì phiên có 1/3/5 lượt, đại lượng `$0.00055` chỉ là **chi phí/phiên hiệu chỉnh theo tỷ lệ câu đạt**, chưa phải chi phí cho một phiên hoàn thành thành công đã đo. Cần chấm kết quả trọn phiên hoặc định nghĩa task là một câu trước khi dùng số này để cam kết vận hành. Cột “Chi phí / câu hỏi đạt” chia thêm số lượt hỏi trung bình mỗi phiên (`2.5`); là đại lượng theo câu, không đánh đồng với thành công toàn phiên.

Hai phiên lỗi `S013`, `S022` chiếm **2/50 = 4% lượt thử**, được khai báo và loại khỏi trung bình như summary gốc. Vì thế số trung bình là trên **48 phiên hợp lệ**, không phải 50 phiên thành công; chi phí xử lý lỗi/retry và tỷ lệ hoàn thành vận hành cần được theo dõi riêng.

## 3. So với impact

**Hiệu chỉnh đơn vị sau review:** báo cáo mới [task-cost-audit.md](task-cost-audit.md), tái lập bằng `python cost/audit.py`, định nghĩa **1 task = 1 câu hỏi**. Mô phỏng lấy nhóm `thuong`/`kho`, nên dùng tỷ lệ lượt 2 **19/20 = 95%**, thay vì tỷ lệ 22/23 có cả ba câu `tu_choi`. Trên 48 phiên hợp lệ có **122 câu**, **70.581 token vào / 5.079 token ra**: **$0.00020708/câu**, chia 95% thành **$0.00021798/câu đạt ước tính**. Đây vẫn là proxy từ eval, chưa chấm đầu ra mô phỏng. Chi phí cơ sở giữ **$0.97754625/tháng** vì công thức theo persona không dùng tỷ lệ đạt. Dòng model lớn không có chi phí/câu đạt đã đo. Bảng lịch sử ở trên giữ nguyên để đối chiếu.

- **Impact / người / tháng:** Trung bình trong nhóm đã hỏi là **~3,1 phiên/tháng** (~10,9 câu/tháng từ `evidence/count_personas.py`). Khảo sát có **13/17** người mất ít nhất 5 phút cho cả lần tìm hiểu gần nhất, không tách riêng phút tìm nguồn hay phút sẽ tiết kiệm. P1 tự báo 15–30 phút cho cả lần, cũng không phải thời gian tiết kiệm. **Không dùng P3 (thành viên nhóm) hoặc P4 (chưa xác minh) làm căn cứ impact.** Nếu giảm **3–5 phút/phiên** *(tự ước tính, chưa đo trước/sau)* thì `3,1 × 3–5` = **9,3–15,5 phút/người/tháng**. Với 143 người đã hỏi, kịch bản là **22–37 giờ/tháng**; ngoại suy cho 436 người là **68–113 giờ/tháng**, với giả định chưa kiểm rằng cả nhóm hoạt động có cùng nhịp dùng. Không gọi đây là lợi ích đã đạt.
- **So sánh cùng đơn vị:** API **$0.0022/người/tháng** ở kịch bản cơ sở, cấu hình lượt 2, so với kịch bản **9,3–15,5 phút/người/tháng** tiết kiệm *(tự ước tính)*; chưa quy thời gian thành tiền. Tổng cơ sở **$0.98/tháng**; mức **$9.21/tháng** ở 721 người/model lớn là ngoại suy đơn giá, không phải chi phí đã đo của model lớn.
- **Quyết định:** **iterate — tiếp tục kiểm chứng**. Chi phí API dự kiến nhỏ, nhưng bản 28 đoạn chưa đạt chuẩn trích dẫn, lợi ích chưa đo với người thật và hosting chưa đo đầy đủ. Chưa đủ cơ sở triển khai rộng chỉ dựa vào bảng giá thấp.

## 4. Ghi chú độ nhạy & chi phí ngoài model

- **Cần gạt tối ưu chi phí:** `tokens_in` lịch sử tăng từ 283 lên ~582 token/lượt ở `run-2`, rồi giảm ở lượt 3. Rút gọn prompt, caching và chặn sớm câu ngoài bài là hướng kiểm tiếp theo; mức tiết kiệm 30–50% là *(tự ước tính)*, chưa đo bằng mô phỏng mới. Giá cache `$0.025/1M` chỉ là số từ ảnh chụp giá, chưa xác minh lại và chưa tính chi phí ghi/cache storage.
- **Chi phí ngoài model:** Hosting khoảng **$5–15/tháng** *(tự ước tính cho gói nhỏ, chưa có hoá đơn)*. Bản demo EC2 có thêm công cụ đo, logging, tên miền và vận hành; chưa có số đo để coi mức này bao trọn cấu hình đã triển khai. Không dùng tổng API làm tổng chi phí sản phẩm.
- **Việc còn mở:** đo lại cấu hình cuối bằng lượt mới; chấm trọn phiên nếu vẫn gọi một phiên là một task; kiểm giá/model thực tế trước khi triển khai; giữ nguyên artifacts lịch sử. Xem [kiểm toán cuối](../eval/final-audit.md).
