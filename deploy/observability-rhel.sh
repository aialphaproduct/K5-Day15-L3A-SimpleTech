#!/usr/bin/env bash
# Prometheus, Grafana, Jaeger bằng podman trên máy chủ (nên có từ 4 GB RAM). Chạy sau install-rhel.sh:
#   sudo bash deploy/observability-rhel.sh <tên-miền>
# Cả ba chỉ nghe 127.0.0.1; xem qua https://<tên-miền>/grafana/ , /jaeger/ , /prometheus/ khi đã đăng nhập admin.
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "Cần chạy bằng sudo."; exit 1; }
DOMAIN="${1:?thiếu tên miền}"
SRC="$(cd "$(dirname "$0")/.." && pwd)"
OBS=/opt/st-observability

dnf install -y podman
mkdir -p "$OBS/grafana/provisioning/datasources" "$OBS/grafana/provisioning/dashboards" "$OBS/grafana/dashboards"
cp "$SRC/observability/grafana/provisioning/dashboards/"*.yml "$OBS/grafana/provisioning/dashboards/"
cp "$SRC/observability/grafana/dashboards/"*.json "$OBS/grafana/dashboards/"
sed -e 's#http://prometheus:9090#http://127.0.0.1:9092/prometheus#' -e 's#http://jaeger:16686#http://127.0.0.1:16686/jaeger#' \
  "$SRC/observability/grafana/provisioning/datasources/datasources.yml" > "$OBS/grafana/provisioning/datasources/datasources.yml"
cat > "$OBS/prometheus.yml" <<'EOF'
global:
  scrape_interval: 5s
scrape_configs:
  - job_name: tutor
    metrics_path: /metrics
    static_configs:
      - targets: ["127.0.0.1:8780"]
EOF
chmod -R a+rX "$OBS"
# Mật khẩu quản trị Grafana ngẫu nhiên (không dùng mặc định); người xem vào bằng chế độ chỉ đọc.
if [ ! -f "$OBS/grafana.env" ]; then
  (umask 077; echo "GF_SECURITY_ADMIN_PASSWORD=$(openssl rand -base64 18)" > "$OBS/grafana.env")
fi

podman run -d --replace --name st-prometheus --network host --restart=always \
  -v "$OBS/prometheus.yml:/etc/prometheus/prometheus.yml:ro,Z" docker.io/prom/prometheus:v3.16.0 \
  --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path=/prometheus --web.listen-address=127.0.0.1:9092 \
  --web.external-url="https://$DOMAIN/prometheus/" --web.route-prefix=/prometheus
podman run -d --replace --name st-grafana --network host --restart=always --env-file "$OBS/grafana.env" \
  -e GF_SERVER_HTTP_ADDR=127.0.0.1 -e GF_SERVER_HTTP_PORT=3002 \
  -e GF_SERVER_ROOT_URL="https://$DOMAIN/grafana/" -e GF_SERVER_SERVE_FROM_SUB_PATH=true \
  -e GF_AUTH_ANONYMOUS_ENABLED=true -e GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer -e GF_AUTH_DISABLE_LOGIN_FORM=true \
  -v "$OBS/grafana/provisioning:/etc/grafana/provisioning:ro,Z" \
  -v "$OBS/grafana/dashboards:/var/lib/grafana/dashboards:ro,Z" docker.io/grafana/grafana:13.2.4
podman run -d --replace --name st-jaeger --network host --restart=always -e JAEGER_LISTEN_HOST=127.0.0.1 \
  docker.io/jaegertracing/jaeger:2.23.0 --set=extensions.jaeger_query.base_path=/jaeger
systemctl enable --now podman-restart.service >/dev/null

# Ứng dụng gửi trace tới Jaeger trên máy này.
mkdir -p /etc/systemd/system/st-tutor.service.d
printf '[Service]\nEnvironment=OTLP_ENDPOINT=http://127.0.0.1:4318\n' > /etc/systemd/system/st-tutor.service.d/otlp.conf

mkdir -p /etc/nginx/st-tutor.d
cat > /etc/nginx/st-tutor.d/observability.conf <<'EOF'
# Chỉ phiên admin của ứng dụng mới vào được ba trang này.
location = /_admin_check {
    internal;
    proxy_pass http://127.0.0.1:8780/admin/keys;
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
}
location /grafana/ { auth_request /_admin_check; proxy_pass http://127.0.0.1:3002; proxy_set_header Host $host; }
location /jaeger/ { auth_request /_admin_check; proxy_pass http://127.0.0.1:16686; proxy_set_header Host $host; }
location /prometheus/ { auth_request /_admin_check; proxy_pass http://127.0.0.1:9092; proxy_set_header Host $host; }
EOF
grep -q 'st-tutor.d' /etc/nginx/conf.d/st-tutor.conf || \
  sed -i '/real_ip_header/a\    include /etc/nginx/st-tutor.d/*.conf;' /etc/nginx/conf.d/st-tutor.conf
nginx -t
systemctl daemon-reload
systemctl restart st-tutor nginx
sleep 8
podman ps --format '{{.Names}} {{.Status}}'
echo "--- cổng đang nghe"
ss -ltnH | awk '{print $4}' | sort -u
