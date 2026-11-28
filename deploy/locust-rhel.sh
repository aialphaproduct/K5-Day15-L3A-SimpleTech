#!/usr/bin/env bash
# Locust có giao diện web tại https://<tên-miền>/locust/ (chỉ phiên admin). Chạy sau observability-rhel.sh:
#   sudo bash deploy/locust-rhel.sh
# Tải được bắn vào một bản chạy RIÊNG ở cổng 8790 dùng model giả: không tốn token, không lẫn số liệu demo.
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "Cần chạy bằng sudo."; exit 1; }
APP=/opt/st-tutor
LOC=/opt/st-locust

python3 -m venv "$LOC"
"$LOC/bin/pip" install -q locust==2.47.0

cat > /etc/systemd/system/st-tutor-load.service <<EOF
[Unit]
Description=Simple Tech tutor (fake model, load test target)
After=st-tutor.service

[Service]
User=sttutor
WorkingDirectory=$APP
Environment=PYTHONIOENCODING=utf-8 MODEL_PROVIDER=fake CHAT_LOG=$APP/logs/load-chat.jsonl OTLP_ENDPOINT=http://127.0.0.1:1
ExecStartPre=/usr/bin/rm -f $APP/logs/load-chat.jsonl
ExecStart=$APP/.venv/bin/python demo/preclass_demo.py --host 127.0.0.1 --port 8790
Restart=on-failure
RestartSec=10
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/st-locust.service <<EOF
[Unit]
Description=Locust web UI
After=st-tutor-load.service

[Service]
User=sttutor
WorkingDirectory=$APP
# Mật khẩu để người dùng giả đăng nhập, đọc từ file đã có (không chép sang chỗ khác).
EnvironmentFile=$APP/logs/credentials.txt
ExecStart=$LOC/bin/locust -f loadtest/locustfile.py --host http://127.0.0.1:8790 --web-host 127.0.0.1 --web-port 8089 --web-base-path /locust
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
systemctl enable st-tutor-load st-locust >/dev/null
systemctl restart st-tutor-load st-locust
systemctl reload nginx
sleep 6
systemctl is-active st-tutor-load st-locust nginx
