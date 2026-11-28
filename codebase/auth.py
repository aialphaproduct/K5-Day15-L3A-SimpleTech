"""Đăng nhập đơn giản cho bản demo: hai tài khoản (admin, hocvien), phiên giữ trong bộ nhớ.

Mật khẩu lấy từ biến môi trường ADMIN_PASSWORD / DEMO_PASSWORD. Thiếu thì sinh ngẫu nhiên một lần và lưu ở
logs/credentials.txt (không commit). Không ghi mật khẩu ra màn hình.
"""
import hmac
import ipaddress
import os
import secrets
import threading
import time
from http.cookies import CookieError, SimpleCookie

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS = os.environ.get("CREDENTIALS_FILE") or os.path.join(ROOT, "logs", "credentials.txt")
ACCOUNTS = (("admin", "ADMIN_PASSWORD"), ("hocvien", "DEMO_PASSWORD"))
COOKIE = "st_session"
TTL = 8 * 3600
MAX_FAILS, WINDOW = 10, 300

_sessions, _fails, _passwords = {}, {}, {}
_lock = threading.Lock()


def _saved():
    try:
        with open(CREDENTIALS, encoding="utf-8") as f:
            return dict(line.rstrip("\n").split("=", 1) for line in f if "=" in line)
    except OSError:
        return {}


def load():
    """Nạp mật khẩu, sinh phần còn thiếu. Trả đường dẫn file nếu phải dùng file, không thì ''."""
    saved, changed, used_file = _saved(), False, False
    for user, variable in ACCOUNTS:
        value = os.environ.get(variable, "")
        if not value:
            used_file = True
            if len(saved.get(variable, "")) < 8:
                saved[variable] = secrets.token_urlsafe(12)
                changed = True
            value = saved[variable]
        _passwords[user] = value
    if changed:
        os.makedirs(os.path.dirname(CREDENTIALS), exist_ok=True)
        handle = os.open(CREDENTIALS, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(handle, "w", encoding="utf-8") as f:
            f.write("".join("%s=%s\n" % item for item in saved.items()))
    return CREDENTIALS if used_file else ""


def login(user, password, client):
    """Trả (mã phiên, '') hoặc (None, lý do)."""
    now = time.time()
    with _lock:
        recent = [t for t in _fails.get(client, []) if now - t < WINDOW]
        _fails[client] = recent
        if len(recent) >= MAX_FAILS:
            return None, "Sai quá nhiều lần, đợi vài phút rồi thử lại."
        expected = _passwords.get(str(user), "")
        # Luôn so sánh để thời gian trả lời không lộ tài khoản có tồn tại hay không.
        ok = hmac.compare_digest(str(password).encode("utf-8"), (expected or secrets.token_hex(16)).encode("utf-8"))
        if not (expected and ok):
            recent.append(now)
            return None, "Sai tài khoản hoặc mật khẩu."
        for token in [t for t, s in _sessions.items() if s[1] < now]:
            del _sessions[token]
        token = secrets.token_urlsafe(32)
        _sessions[token] = (user, now + TTL)
        return token, ""


def _token(cookie_header):
    try:
        jar = SimpleCookie(cookie_header or "")
    except CookieError:
        return ""
    return jar[COOKIE].value if COOKIE in jar else ""


def user_of(cookie_header):
    """Tên tài khoản của phiên còn hạn, hoặc ''."""
    session = _sessions.get(_token(cookie_header))
    return session[0] if session and session[1] > time.time() else ""


def logout(cookie_header):
    with _lock:
        _sessions.pop(_token(cookie_header), None)


def cookie(token, secure):
    return "%s=%s; Path=/; HttpOnly; SameSite=Lax; Max-Age=%d%s" % (
        COOKIE, token, TTL if token else 0, "; Secure" if secure else "")


def is_internal(address, forwarded):
    """Yêu cầu đến thẳng từ máy này hoặc mạng nội bộ (Prometheus), không đi qua proxy công khai."""
    if forwarded:
        return False
    try:
        ip = ipaddress.ip_address(address)
    except ValueError:
        return False
    return ip.is_loopback or ip.is_private
