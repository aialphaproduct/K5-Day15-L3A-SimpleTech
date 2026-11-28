"""Demo tích hợp: chạy bản preclass offline trên máy, mở sẵn Bài 1 và gắn trợ giảng của nhóm.

Chạy: python demo/preclass_demo.py --dir <thư mục bản preclass offline>   (mở http://localhost:8780/)
Không có --dir thì dùng trang bài học tối giản của nhóm (dùng khi đưa lên máy chủ). Mọi trang đều phải đăng nhập.

Repo này KHÔNG chứa giao diện hay bài giảng của preclass; mọi file đó được đọc từ thư mục --dir.
Đăng nhập, tiến độ và danh sách video của demo lưu ở file tạm. Bản offline vẫn tự ghi lại
data/day_videos.json lúc khởi động, và có thể ghi nhật ký khi dùng trợ giảng của nó.
"""
import argparse
import importlib.util
import json
import os
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
CODEBASE = os.path.join(os.path.dirname(HERE), "codebase")
sys.path.insert(0, HERE)

import pages  # noqa: E402
import video_hints  # noqa: E402

DAY1 = "program-day01:ai-llm-foundation"
OUR_FILES = {
    "/st/widget.js": os.path.join(CODEBASE, "extension", "widget.js"),
    "/st/demo.js": os.path.join(HERE, "demo.js"),
}
INJECT = '<script src="/st/demo.js"></script>\n    <script src="/st/widget.js" data-embed="1" defer></script>\n    '
MAX_BODY = 20000
# Người ngoài phiên đăng nhập chỉ chạm được /login. Bản preclass offline chỉ được đọc, trừ đăng nhập giả của nó.
WRITES = ("/ask", "/admin/analyze", "/admin/improve", "/admin/apply", "/admin/keys", "/api/auth/login")
HIDDEN = ("/backend-mock", "/transcripts", "/logs")


class PlainPages(BaseHTTPRequestHandler):
    """Thay cho máy chủ preclass khi không có --dir."""

    def _static(self, head_only=False):
        self.send_error(404)

    def do_GET(self):
        self._static()

    def do_HEAD(self):
        self._static(head_only=True)

    def do_POST(self):
        self.send_error(404)


def load_preclass(folder):
    backend = os.path.join(folder, "backend-mock")
    path = os.path.join(backend, "server.py")
    if not os.path.isfile(path):
        raise SystemExit("Không thấy backend-mock/server.py trong %s" % folder)
    sys.path.insert(0, backend)
    sys.dont_write_bytecode = True  # không sinh __pycache__ trong thư mục preclass
    spec = importlib.util.spec_from_file_location("preclass_server", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.STATE_FILE = os.path.join(tempfile.gettempdir(), "st-preclass-demo-state.json")
    module.VIDEOS_FILE = os.path.join(tempfile.gettempdir(), "st-preclass-demo-videos.json")
    module.OVERRIDES["__released"] = [DAY1]
    module.OVERRIDES.pop("__schedule", None)
    # Demo không dùng AI của preclass: bỏ key của bản offline để nó không gọi model ngầm.
    os.environ.pop("ANTHROPIC_API_KEY", None)
    module._ENV.pop("ANTHROPIC_API_KEY", None)
    sys.path.remove(backend)
    return module


def load_tutor():
    """Nạp code nhóm, bật xoay vòng key và đăng nhập."""
    # Hai bên cùng có module tên "agent": bỏ tên đã nạp của preclass trước khi nạp code nhóm.
    for name in ("agent", "ai", "tools", "tracing", "web", "insights", "improve", "gate", "auth", "keys"):
        sys.modules.pop(name, None)
    sys.path.insert(0, CODEBASE)
    import auth
    import improve
    import keys
    import web
    keys.install()
    web.auth, web.keys = auth, keys
    improve.load_active()  # prompt người duyệt đã áp dụng (nếu có)
    web.improve = improve
    return web


def make_handler(preclass, web):
    auth = web.auth

    class DemoHandler(preclass.Handler if preclass else PlainPages):
        def parse_request(self):
            """Cổng đăng nhập chung cho mọi phương thức, kể cả đường dẫn của bản preclass."""
            if not super().parse_request():
                return False
            if self._allowed():
                return True
            self.close_connection = True
            self.wfile.flush()
            return False

        def _redirect(self, to, cookie=None):
            self.send_response(303)
            self.send_header("Location", to)
            if cookie:
                self.send_header("Set-Cookie", cookie)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def _client(self):
            # Sau nginx thì địa chỉ thật nằm ở X-Real-IP; chỉ tin khi kết nối đến từ chính máy này.
            peer = self.client_address[0]
            return (self.headers.get("X-Real-IP") or peer) if peer == "127.0.0.1" else peer

        def _secure(self):
            return self.headers.get("X-Forwarded-Proto") == "https"

        def _allowed(self):
            path = unquote(urlparse(self.path).path)
            reading = self.command in ("GET", "HEAD")
            if path == "/login":
                if reading:
                    self._send(200, pages.LOGIN.encode("utf-8"), "text/html; charset=utf-8", self.command == "HEAD")
                elif self.command == "POST":
                    self._login()
                else:
                    self._json_out(405, {"error": "Không hỗ trợ."})
                return False
            if path == "/metrics" and reading and auth.is_internal(self.client_address[0], self.headers.get("X-Real-IP")):
                return True
            user = auth.user_of(self.headers.get("Cookie"))
            if path == "/logout":
                auth.logout(self.headers.get("Cookie"))
                self._redirect("/login", auth.cookie("", self._secure()))
            elif not user:
                if reading and "text/html" in (self.headers.get("Accept") or ""):
                    self._redirect("/login")
                else:
                    self._json_out(401, {"error": "Cần đăng nhập."})
            elif (path == "/admin" or path.startswith("/admin/") or path == "/metrics") and user != "admin":
                self._json_out(403, {"error": "Cần tài khoản admin. Mở /logout rồi đăng nhập lại."})
            elif not reading and (self.command != "POST" or path not in WRITES):
                self._json_out(403, {"error": "Bản demo không cho ghi vào đường dẫn này."})
            elif "/." in path or "\\" in path or path.lower().startswith(HIDDEN):
                self._json_out(404, {"error": "Không có."})
            else:
                return True
            return False

        def _body(self):
            """JSON của yêu cầu, hoặc None. Chỉ nhận application/json để trang lạ không gửi chéo nguồn được."""
            try:
                length = int(self.headers.get("Content-Length") or 0)
                if self.headers.get_content_type() != "application/json" or not 0 < length <= MAX_BODY:
                    return None
                data = json.loads(self.rfile.read(length))
            except ValueError:
                return None
            return data if isinstance(data, dict) else None

        def _login(self):
            data = self._body()
            if data is None:
                return self._json_out(400, {"error": "Cần application/json."})
            token, error = auth.login(data.get("user"), data.get("password"), self._client())
            if not token:
                return self._json_out(401, {"error": error})
            body = json.dumps({"next": "/admin" if data.get("user") == "admin" else "/"}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Set-Cookie", auth.cookie(token, self._secure()))
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send(self, status, body, ctype, head_only=False):
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            if not head_only:
                self.wfile.write(body)

        def _static(self, head_only=False):
            path = urlparse(self.path).path
            if path in OUR_FILES:
                with open(OUR_FILES[path], "rb") as f:
                    return self._send(200, f.read(), "application/javascript; charset=utf-8", head_only)
            if preclass is None:
                if path in ("/", "/index.html"):
                    return self._send(200, pages.LESSON.encode("utf-8"), "text/html; charset=utf-8", head_only)
                return super()._static(head_only)
            is_page = path == "/index.html" or (not os.path.splitext(path)[1] and not path.startswith("/media/"))
            if not is_page:
                return super()._static(head_only)
            with open(os.path.join(preclass.ROOT, "index.html"), encoding="utf-8") as f:
                html = f.read()
            marker = '<script type="module"'
            if marker not in html:
                return self._send(500, "index.html đã đổi cấu trúc".encode(), "text/plain; charset=utf-8")
            html = html.replace(marker, INJECT + marker, 1)
            return self._send(200, html.encode("utf-8"), "text/html; charset=utf-8", head_only)

        def _json_out(self, status, body):
            self._send(status, json.dumps(body, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/metrics":
                return self._send(200, web.insights.prometheus().encode("utf-8"), "text/plain; version=0.0.4; charset=utf-8")
            if path not in ("/admin", "/admin/data", "/admin/versions", "/admin/keys"):
                return super().do_GET()
            if path == "/admin/keys":
                return self._json_out(200, web.keys.listing())
            if path == "/admin/data":
                return self._json_out(200, web.insights.summary())
            if path == "/admin/versions":
                return self._json_out(200, web.improve.overview())
            with open(os.path.join(CODEBASE, "admin.html"), "rb") as f:
                return self._send(200, f.read(), "text/html; charset=utf-8")

        def do_POST(self):
            path = urlparse(self.path).path
            if path not in ("/ask", "/admin/analyze", "/admin/improve", "/admin/apply", "/admin/keys"):
                return super().do_POST()
            data = self._body()
            if path.startswith("/admin/"):
                if data is None:
                    return self._json_out(400, {"error": "Cần application/json."})
                if path == "/admin/keys":
                    if data.get("action") == "add":
                        return self._json_out(200, web.keys.add(data.get("key"), data.get("label")))
                    if data.get("action") == "test":
                        return self._json_out(200, web.keys.test(data.get("id")))
                    return self._json_out(200, web.keys.change(data.get("id"), data.get("action")))
                if path == "/admin/improve":
                    started = web.improve.start()
                    return self._json_out(200, {"started": started, "error": "" if started else "Đang có một vòng chạy."})
                if path == "/admin/apply":
                    return self._json_out(200, web.improve.apply(str(data.get("id", ""))))
                return self._json_out(200, web.insights.analyze())

            def annotate(body, question):
                body["video"] = video_hints.find(question, [p["code"] for p in body["passages"]])
                for passage in body["passages"]:
                    passage["at"] = video_hints.time_of(passage["code"])

            body, status = web.reply(data, context=video_hints.with_context, annotate=annotate)
            self._json_out(status, body)

    return DemoHandler


def main():
    ap = argparse.ArgumentParser(description="Demo trợ giảng trên bản preclass offline")
    ap.add_argument("--dir", default=os.environ.get("PRECLASS_DIR"), help="thư mục bản preclass offline")
    ap.add_argument("--port", type=int, default=8780)
    ap.add_argument("--host", default="127.0.0.1", help="để 127.0.0.1 và đặt nginx HTTPS phía trước")
    args = ap.parse_args()
    os.environ.setdefault("OTLP_ENDPOINT", "http://127.0.0.1:4320")  # Jaeger trong observability/
    preclass = load_preclass(os.path.abspath(args.dir)) if args.dir else None
    # Windows cho hai máy chủ cùng giành một cổng; tắt để bản chạy sau báo lỗi thay vì âm thầm chạy chồng.
    # Trên Linux phải cho dùng lại cổng, không thì khởi động lại bị chặn bởi kết nối cũ đang chờ đóng.
    ThreadingHTTPServer.allow_reuse_address = os.name != "nt"
    try:
        web = load_tutor()
        server = ThreadingHTTPServer((args.host, args.port), make_handler(preclass, web))
    except OSError:
        raise SystemExit("Cổng %d đang được dùng. Tắt máy chủ cũ hoặc thêm --port khác." % args.port)
    server.daemon_threads = True
    saved = web.auth.load()
    print("Demo: http://localhost:%d/" % args.port, flush=True)
    if saved:
        print("Mật khẩu của admin và hocvien nằm trong %s" % saved, flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
