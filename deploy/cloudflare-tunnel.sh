#!/usr/bin/env bash
# Đưa bản demo ra Internet qua Cloudflare Quick Tunnel (không cần tài khoản, không cần mở cổng vào).
#   sudo bash deploy/cloudflare-tunnel.sh        (sau install-rhel.sh)
# Địa chỉ https://....trycloudflare.com đổi mỗi lần dịch vụ khởi động lại. Chỉ dùng cho demo.
# Gỡ: sudo systemctl disable --now st-tunnel
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "Cần chạy bằng sudo."; exit 1; }

if ! command -v cloudflared >/dev/null; then
  curl -fsSL https://pkg.cloudflare.com/cloudflared.repo -o /etc/yum.repos.d/cloudflared.repo
  dnf install -y cloudflared
fi

# Cổng chỉ nghe nội bộ cho tunnel: giữ địa chỉ thật của người dùng để giới hạn đăng nhập sai theo từng người.
cat > /etc/nginx/conf.d/st-tunnel.conf <<'EOF'
server {
    listen 127.0.0.1:8008;
    server_name _;
    client_max_body_size 64k;
    location = /metrics { return 404; }
    location / {
        proxy_pass http://127.0.0.1:8780;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $http_cf_connecting_ip;
        proxy_set_header X-Forwarded-Proto https;
        proxy_read_timeout 120s;
    }
}
EOF
nginx -t
systemctl reload nginx

cat > /etc/systemd/system/st-tunnel.service <<EOF
[Unit]
Description=Cloudflare quick tunnel for Simple Tech demo
After=network-online.target nginx.service
Wants=network-online.target

[Service]
DynamicUser=yes
ExecStart=$(command -v cloudflared) tunnel --no-autoupdate --url http://127.0.0.1:8008
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable st-tunnel >/dev/null
SINCE="$(date '+%Y-%m-%d %H:%M:%S')"
systemctl restart st-tunnel

for _ in $(seq 1 30); do
  URL="$(journalctl -u st-tunnel --since "$SINCE" -o cat --no-pager | grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' | grep -v '//api\.' | head -1 || true)"
  [ -n "$URL" ] && break
  sleep 2
done
[ -n "${URL:-}" ] || { echo "Chưa lấy được địa chỉ, xem: journalctl -u st-tunnel"; exit 1; }
echo "ĐỊA CHỈ: $URL"
