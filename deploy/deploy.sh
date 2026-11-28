#!/usr/bin/env bash
# Đóng gói mã và cài lên máy chủ qua SSH (chạy bằng Git Bash trên máy nhóm):
#   bash deploy/deploy.sh ec2-user@<IP> <đường-dẫn-file.pem>
#   bash deploy/deploy.sh --pack            chỉ tạo gói, không gửi
# Gói KHÔNG chứa .env, logs, API key, và không chứa giao diện hay bài giảng preclass.
set -euo pipefail
cd "$(dirname "$0")/.."
PACKAGE="${TMPDIR:-/tmp}/st-tutor.tar.gz"
tar --exclude=__pycache__ --exclude='*.pyc' --exclude='loadtest/result*' -czf "$PACKAGE" \
  run.py requirements.txt codebase demo data/lessons eval cost loadtest deploy observability
echo "Gói: $PACKAGE"
[ "${1:-}" = "--pack" ] && exit 0
HOST="${1:?thiếu user@IP}"
KEY="${2:?thiếu đường dẫn file .pem}"
scp -i "$KEY" "$PACKAGE" "$HOST:/tmp/st-tutor.tar.gz"
ssh -t -i "$KEY" "$HOST" 'rm -rf /tmp/st-tutor && mkdir /tmp/st-tutor && tar -xzf /tmp/st-tutor.tar.gz -C /tmp/st-tutor && sudo bash /tmp/st-tutor/deploy/install-rhel.sh'
