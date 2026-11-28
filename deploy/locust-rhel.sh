#!/usr/bin/env bash
# Locust có giao diện web tại https://<tên-miền>/locust/ (chỉ phiên admin). Chạy sau observability-rhel.sh:
#   sudo bash deploy/locust-rhel.sh
# Tải bắn vào HỆ THỐNG THẬT (nginx → trợ giảng → model): tốn token, tính vào giới hạn của API key và hiện trên
# trang đo lường, Grafana, Jaeger. Bắt đầu với ít người dùng (3–5).
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "Cần chạy bằng sudo."; exit 1; }
APP=/opt/st-tutor
LOC=/opt/st-locust

# Bỏ bản chạy model giả của cách cài cũ.
systemctl disable --now st-tutor-load 2>/dev/null || true
rm -f /etc/systemd/system/st-tutor-load.service "$APP/logs/load-chat.jsonl"

python3 -m venv "$LOC"
"$LOC/bin/pip" install -q locust==2.47.0

cat > /etc/systemd/system/st-locust.service <<EOF
[Unit]
Description=Locust web UI
After=st-tutor.service nginx.service

[Service]
User=sttutor
WorkingDirectory=$APP
# Mật khẩu để người dùng giả đăng nhập, đọc từ file đã có (không chép sang chỗ khác).
EnvironmentFile=$APP/logs/credentials.txt
# Chứng chỉ tự ký của nginx trên chính máy này.
Environment=INSECURE_TLS=1
ExecStart=$LOC/bin/locust -f loadtest/locustfile.py --host https://127.0.0.1 --web-host 127.0.0.1 --web-port 8089 --web-base-path /locust
Restart=on-failure
RestartSec=10
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/nginx/st-tutor.d/locust.conf <<'EOF'
location /locust/ { auth_request /_admin_check; proxy_pass http://127.0.0.1:8089; proxy_set_header Host $host; }
EOF
nginx -t
systemctl daemon-reload
systemctl enable st-locust >/dev/null
systemctl restart st-locust
systemctl reload nginx
sleep 6
systemctl is-active st-locust st-tutor nginx
