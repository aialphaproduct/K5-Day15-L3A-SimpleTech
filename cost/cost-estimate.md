# Chi phí khi dùng thật

> Điền ở guide bước 4.2, nộp ở CP4 14:30 Thứ Bảy 28/11. Ôn lại: ngày 13, ngày 1, ngày 14 · lab ngày 13, lab ngày 14. Chấm ở rubric R6.
> Số **không điền tay**: điền `cost/personas.yaml` → `python run.py simulate --rate-from eval/run-2.csv` → chép bảng trong `cost/simulate-1-summary.md` vào đây.
> Lúc build dùng gói miễn phí vẫn tính theo **giá gói trả phí** — đây là chi phí cho lúc đưa vào dùng thật.

## 1. Đầu vào

- **Persona** (`cost/personas.yaml`, đo bằng [evidence/count_personas.py](../evidence/count_personas.py) trên `data/preclass/chat.csv` cửa sổ 05/11–25/11/2026 = 21 ngày, ngắt phiên khi nghỉ > 30 phút, quy đổi 21 → 30 ngày bằng `× 30 / 21`):
  - `dung_it` (1–2 câu): `share 0.38` (54/143 = 37,8%), `1.5` phiên/tháng, `1` lượt/phiên.
  - `dung_vua` (3–10 câu): `share 0.43` (61/143 = 42,7%), `2.8` phiên/tháng, `3` lượt/phiên.
  - `dung_nhieu` (≥11 câu): `share 0.19` (28/143 = 19,6%), `7.0` phiên/tháng, `5` lượt/phiên.
- **Số người dùng thật** 3 kịch bản (nguồn: `data/preclass/README.md`, `learners.csv`, `chat.csv`): thấp **143** (đã hỏi trợ giảng trong 21 ngày) · cơ sở **436** (học viên có hoạt động trên pre-class) · cao **721** (tổng tài khoản AI20K K5).
- **Giá** 2 mức model từ `further-reading/model-prices.md` (Google Gemini API, https://ai.google.dev/gemini-api/docs/pricing, BTC kiểm 25/11/2026):
  - `gemini-3.1-flash-lite` (tầng Nhỏ): vào `$0.25` / ra `$1.50` trên 1M token.
  - `gemini-4-hydrogen` (tầng Lớn, cùng hãng Gemini): vào `$1.50` / ra `$7.50` trên 1M token.
- **Tỉ lệ đạt** dùng để tính: **22/23 (96%)** — lượt `run-2@20261127-215239` ([eval/run-2.csv](../eval/run-2.csv), chạy cùng model `gemini-3.1-flash-lite`).
- **Đo token trên model `gemini-3.1-flash-lite`, tính giá model `gemini-3.1-flash-lite` và `gemini-4-hydrogen`** (cùng họ Google Gemini).

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

Chi phí / task thành công = chi phí trung bình mỗi phiên ÷ tỉ lệ đạt (`96%`) — **không coi như đạt 100%**. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (`2.5`) ÷ `96%`.

## 3. So với impact

- **Impact / người / tháng (đối chiếu `spec.md` §2 & phỏng vấn):** Trung bình mỗi học viên có **~3,1 phiên/tháng** (~10,9 câu/tháng từ `evidence/count_personas.py`). Theo phỏng vấn, P3 mất ~5 phút để tự đối chiếu câu trả lời ở công cụ khác, P1 mất 15–30 phút và P4 mất 15 phút để tự tua video kiểm chứng. Nếu trợ giảng kèm mã đoạn giúp giảm bảo thủ **3–5 phút/phiên** *(tự ước tính; `spec.md` §2 vẫn chờ nhóm chốt công thức impact chính thức)*, mỗi học viên tiết kiệm khoảng **9–15 phút/tháng** (toàn khoá 436 học viên cơ sở ≈ **65–109 giờ/tháng**).
- **Chi phí / người / tháng (cơ sở, model `gemini-3.1-flash-lite`):** **$0.0022 / người / tháng** (tổng **$0.98 / tháng** cho 436 học viên; ngay cả kịch bản cao 721 người dùng `gemini-4-hydrogen` cũng chỉ **$9.21 / tháng**).
- **Kết luận một dòng — đáng làm không:** **Rất đáng làm** — chi phí API cực thấp ($0.00055/task thành công và ~$0.98/tháng ở quy mô 436 học viên cơ sở) so với thời gian tự kiểm chứng bài giảng mà học viên tiết kiệm được.

## 4. Ghi chú độ nhạy & chi phí ngoài model

- **Cần gạt tối ưu chi phí:** Nếu cắt ngắn `SYSTEM` prompt ở `codebase/agent.py` (hiện `tokens_in` tăng từ 283 lên ~582 token/lượt ở `run-2`) hoặc bật prompt caching (giá cache đọc của `gemini-3.1-flash-lite` chỉ `$0.025/1M`, giảm 10× phần system prompt) và chặn sớm các câu ngoài bài ở `search_passages`, chi phí token vào có thể giảm thêm ~30–50%.
- **Chi phí ngoài model:** Hosting web Flask (`codebase/web.py`) trên AWS (EC2/App Runner/Lightsail gói nhỏ) sẽ lớn hơn chi phí API model nhiều lần (~$5–15/tháng *(tự ước tính)*), nhưng vẫn rất nhỏ cho toàn khoá 436–721 học viên.
