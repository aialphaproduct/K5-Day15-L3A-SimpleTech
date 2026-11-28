# Triển khai bản demo lên AWS

Bản demo hackathon: trợ giảng có đăng nhập, trang đo lường, Prometheus / Grafana / Jaeger và Locust trên **một máy EC2**. Không kết nối trang pre-class thật.

## Kiến trúc

```
Người dùng ─HTTPS─> Cloudflare ─HTTPS 443─> EC2 (Red Hat)
                                             nginx ─> trợ giảng        127.0.0.1:8780  (st-tutor)
                                                   ─> /grafana/        127.0.0.1:3002  (podman)
                                                   ─> /jaeger/         127.0.0.1:16686 (podman)
                                                   ─> /prometheus/     127.0.0.1:9092  (podman)
                                                   ─> /locust/         127.0.0.1:8089  (st-locust)
                                             Locust ─> bản chạy model giả 127.0.0.1:8790 (st-tutor-load)
```

Chỉ nginx nhận kết nối từ ngoài. `/grafana/`, `/jaeger/`, `/prometheus/`, `/locust/` chỉ mở cho phiên đăng nhập `admin`.

## Cần có

| Thứ | Ghi chú |
|---|---|
| EC2 Red Hat 8–10 (đã chạy trên RHEL 10.2) | `t3.medium` nếu bật đủ công cụ đo; chỉ chạy trợ giảng thì `t3.micro` được |
| File `.pem` của máy | Không đưa vào repo |
| Tên miền quản lý ở Cloudflare | Dùng một tên con riêng |
| API key model | Thêm ở trang admin sau khi cài, hoặc đặt `API_KEY` trong `/opt/st-tutor/.env` |
| Git Bash (nếu triển khai từ Windows) | Các lệnh dưới chạy trong Git Bash, ở thư mục gốc repo |

## Bước 1. Mạng

1. **Security group:** inbound `443` chỉ cho [dải IP của Cloudflare](https://www.cloudflare.com/ips-v4); inbound `22` chỉ cho IP của người quản trị.
2. **DNS Cloudflare:** bản ghi `A`, tên con tuỳ chọn, trỏ IP công khai của máy, bật Proxied. Chế độ SSL **Full** (máy chủ dùng chứng chỉ tự ký). Nếu zone đặt Full (strict) thì phải cài Origin Certificate.
3. Máy chưa gắn Elastic IP thì dừng rồi bật lại sẽ đổi IP, phải sửa bản ghi.

## Bước 2. Cài trợ giảng

```bash
bash deploy/deploy.sh ec2-user@<IP> <đường-dẫn.pem>
```

`deploy.sh` đóng gói mã (không có `.env`, `logs/`, key) rồi chạy `install-rhel.sh` trên máy: cài Python, nginx, tạo dịch vụ `st-tutor`, chứng chỉ tự ký 30 ngày, bật `httpd_can_network_connect` (SELinux) và mở HTTPS trên firewalld nếu đang chạy. Chạy lại được; `.env` và `logs/` trên máy được giữ nguyên.

## Bước 3. Đăng nhập và API key

```bash
ssh -i <pem> ec2-user@<IP> "sudo cat /opt/st-tutor/logs/credentials.txt"
```

| Tài khoản | Mật khẩu | Quyền |
|---|---|---|
| `admin` | `ADMIN_PASSWORD` | Trang đo lường, API key, tự cải thiện, công cụ đo |
| `hocvien` | `DEMO_PASSWORD` | Trang bài học và khung hỏi đáp |

Mật khẩu sinh ngẫu nhiên ở lần chạy đầu. Vào `/admin`, mục **API key**: thêm tối đa 5 key, bấm **Thử**. Key bị 429, 401/403 hoặc 5xx thì tự chuyển sang key kế. Key lưu ở `logs/api-keys.json` (quyền 600).

## Bước 4. Công cụ đo (tuỳ chọn)

Trên máy chủ, trong thư mục mã đã giải nén (`/tmp/st-tutor`):

```bash
sudo bash deploy/observability-rhel.sh <tên-miền>
sudo bash deploy/locust-rhel.sh
```

- Grafana `https://<tên-miền>/grafana/d/st-tutor`, Jaeger `/jaeger/`, Prometheus `/prometheus/`.
- Locust `/locust/`: nhập số người dùng, giữ nguyên Host `http://127.0.0.1:8790`. Tải bắn vào bản chạy **model giả**: không tốn token, không lên số liệu demo. Đổi Host sang 8780 sẽ gọi model thật.

Kết quả đã đo ngày 28/11 (model giả, 30 người dùng, khoảng 45 giây): 323 yêu cầu, 0 lỗi, p95 37 ms.

## Giao diện bài học

Mặc định máy chủ dùng **trang bài học tối giản** của nhóm (không có video).

Trên máy của nhóm, `demo/preclass_demo.py --dir <thư mục>` có thể đọc một bản preclass offline để hiện giao diện và video Bài 1. **Bản đó không thuộc repo này** và là tài liệu của khoá học: không commit, chỉ đưa lên máy chủ khi được phép. `pack-preclass.py` gói phần tối thiểu (bỏ `.env`, lời giảng, bài khác, đáp án); giải nén vào `/opt/st-tutor-preclass` rồi chạy lại bước 2.

## Kiểm tra và xử lý lỗi

| Hiện tượng | Xem |
|---|---|
| Cloudflare 522 | Sai IP trong DNS, hoặc security group chưa cho Cloudflare vào 443 |
| Cloudflare 526 | Zone đặt Full (strict) mà máy dùng chứng chỉ tự ký |
| Trợ giảng báo lỗi khi hỏi | Chưa có key, hoặc mọi key hết lượt |
| Dịch vụ không chạy | `sudo journalctl -u st-tutor -n 50` |

## Gỡ sau khi demo

```bash
sudo systemctl disable --now st-tutor st-tutor-load st-locust
sudo podman rm -f st-prometheus st-grafana st-jaeger
sudo rm -rf /opt/st-tutor /opt/st-tutor-preclass /opt/st-observability /opt/st-locust
```

Sau đó xoá rule 443, xoá bản ghi DNS, thu hồi API key và dừng hoặc xoá máy EC2.

## Giới hạn

- Một máy, không dự phòng. Chứng chỉ tự ký 30 ngày.
- Phiên đăng nhập giữ trong bộ nhớ: khởi động lại dịch vụ thì phải đăng nhập lại.
- Các lượt gọi model xử lý lần lượt (đo token theo biến dùng chung), nên thông lượng với model thật thấp.
- `cloudflare-tunnel.sh` là phương án dùng địa chỉ tạm `trycloudflare.com` khi chưa có tên miền.
