#!/usr/bin/env bash
# Cài bản demo trên Red Hat / Rocky / Alma 8–10 (hoặc Amazon Linux 2023). Chạy lại được nhiều lần.
#   sudo bash deploy/install-rhel.sh          (chạy trong thư mục đã giải nén)
# Mở cổng 443 trong security group của EC2 (nên chỉ cho IP của nhóm).
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "Cần chạy bằng sudo."; exit 1; }
SRC="$(cd "$(dirname "$0")/.." && pwd)"
APP=/opt/st-tutor
LOAD_PORT=8790

dnf install -y nginx openssl tar
# Cần Python 3.10 trở lên: RHEL 10 có sẵn, bản cũ hơn thì cài python3.11.
if python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))' 2>/dev/null; then
  PY=python3; dnf install -y python3-pip
else
  PY=python3.11; dnf install -y python3.11 python3.11-pip
fi
id sttutor &>/dev/null || useradd --system --home-dir "$APP" --shell /sbin/nologin sttutor

mkdir -p "$APP/logs"
# Chép mã mới, giữ nguyên .env, logs (mật khẩu, key, nhật ký) của lần cài trước.
(cd "$SRC" && tar --exclude=./logs --exclude=./.env -cf - .) | (cd "$APP" && tar -xf -)
if [ ! -f "$APP/.env" ]; then
  printf 'MODEL_PROVIDER=gemini\nMODEL_NAME=gemini-3.1-flash-lite\nAPI_KEY=\n' > "$APP/.env"
fi
"$PY" -m venv "$APP/.venv"
"$APP/.venv/bin/pip" install -q -r "$APP/requirements.txt"
chown -R sttutor:sttutor "$APP"
chmod 600 "$APP/.env"
chmod 700 "$APP/logs"

# Có gói preclass (giải nén ở $PRECLASS) thì dùng giao diện và video Bài 1, không thì trang tối giản.
PRECLASS=/opt/st-tutor-preclass
DIR_ARG=""
if [ -f "$PRECLASS/backend-mock/server.py" ]; then
  chown -R sttutor:sttutor "$PRECLASS"
  DIR_ARG="--dir $PRECLASS"
fi

cat > /etc/systemd/system/st-tutor.service <<EOF
[Unit]
Description=Simple Tech tutor demo
After=network-online.target

[Service]
User=sttutor
WorkingDirectory=$APP
Environment=PYTHONIOENCODING=utf-8
ExecStart=$APP/.venv/bin/python demo/preclass_demo.py --host 127.0.0.1 --port 8780 $DIR_ARG
Restart=on-failure
NoNewPrivileges=true
ProtectSystem=full
ProtectHome=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# HTTPS tự ký: trình duyệt sẽ cảnh báo một lần. Có tên miền thì thay bằng chứng chỉ thật.
if [ ! -f /etc/pki/tls/certs/st-tutor.crt ]; then
  openssl req -x509 -newkey rsa:2048 -nodes -days 30 -subj "/CN=st-tutor" \
    -keyout /etc/pki/tls/private/st-tutor.key -out /etc/pki/tls/certs/st-tutor.crt 2>/dev/null
  chmod 600 /etc/pki/tls/private/st-tutor.key
fi

cat > /etc/nginx/conf.d/st-tutor.conf <<'EOF'
server {
    listen 443 ssl;
    server_name _;
    # Đi qua Cloudflare thì lấy địa chỉ thật của người dùng (để giới hạn đăng nhập sai theo từng người).
    set_real_ip_from 173.245.48.0/20;
    set_real_ip_from 103.21.244.0/22;
    set_real_ip_from 103.22.200.0/22;
    set_real_ip_from 103.31.4.0/22;
    set_real_ip_from 141.101.64.0/18;
    set_real_ip_from 108.162.192.0/18;
    set_real_ip_from 190.93.240.0/20;
    set_real_ip_from 188.114.96.0/20;
    set_real_ip_from 197.234.240.0/22;
    set_real_ip_from 198.41.128.0/17;
    set_real_ip_from 162.158.0.0/15;
    set_real_ip_from 104.16.0.0/13;
    set_real_ip_from 104.24.0.0/14;
    set_real_ip_from 172.64.0.0/13;
    set_real_ip_from 131.0.72.0/22;
    real_ip_header CF-Connecting-IP;
    include /etc/nginx/st-tutor.d/*.conf;
    ssl_certificate     /etc/pki/tls/certs/st-tutor.crt;
    ssl_certificate_key /etc/pki/tls/private/st-tutor.key;
    client_max_body_size 64k;
    location = /metrics { return 404; }
    location / {
        proxy_pass http://127.0.0.1:8780;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
        proxy_read_timeout 120s;
    }
}
EOF

# SELinux mặc định không cho nginx nối sang cổng nội bộ.
if command -v getenforce >/dev/null && [ "$(getenforce)" != "Disabled" ]; then
  setsebool -P httpd_can_network_connect 1
fi
if systemctl is-active --quiet firewalld; then
  firewall-cmd --permanent --add-service=https >/dev/null
  firewall-cmd --reload >/dev/null
fi

nginx -t
systemctl daemon-reload
systemctl enable --now nginx st-tutor
systemctl restart nginx st-tutor
sleep 2
systemctl is-active st-tutor nginx
echo "Xong. Mở https://<IP máy chủ>/"
echo "Mật khẩu: sudo cat $APP/logs/credentials.txt"
echo "Thêm API key ở trang https://<IP máy chủ>/admin"
echo "Giả lập tải: xem loadtest/locustfile.py (chạy máy chủ riêng cổng $LOAD_PORT với MODEL_PROVIDER=fake)."
