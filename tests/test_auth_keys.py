import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "codebase"))
sys.path.insert(0, os.path.join(ROOT, "demo"))

import ai  # noqa: E402
import auth  # noqa: E402
import keys  # noqa: E402
import preclass_demo  # noqa: E402
import web  # noqa: E402

PASSWORDS = {"ADMIN_PASSWORD": "test-admin-pass", "DEMO_PASSWORD": "test-demo-pass"}


class KeysTest(unittest.TestCase):
    def setUp(self):
        patch = mock.patch.object(keys, "STORE", os.path.join(tempfile.mkdtemp(), "keys.json"))
        patch.start()
        self.addCleanup(patch.stop)
        keys._runtime.clear()
        keys._turn = 0

    def test_at_most_five_and_never_returns_full_key(self):
        for i in range(5):
            self.assertEqual(keys.add("fake-key-number-%d" % i), {"ok": True})
        self.assertIn("error", keys.add("fake-key-number-6"))
        self.assertNotIn("fake-key-number", json.dumps(keys.listing()))
        self.assertIn("error", keys.add("có khoảng trắng"))

    def test_rotates_and_moves_on_when_limited_or_bad(self):
        for name in ("aaaaaaaaaaaa", "bbbbbbbbbbbb", "cccccccccccc"):
            keys.add(name)
        used = []

        def call(system, user):
            used.append(ai.API_KEY)
            if ai.API_KEY.startswith("a"):
                raise RuntimeError("HTTP 429: quota")
            return "ok"

        wrapped = keys._rotating(call)
        before = ai.API_KEY
        self.assertEqual([wrapped("", "") for _ in range(3)], ["ok"] * 3)
        self.assertEqual(used[0][0], "a")
        self.assertEqual(sum(k.startswith("a") for k in used), 1)  # key đang nghỉ không bị gọi lại
        self.assertEqual({k[0] for k in used}, {"a", "b", "c"})
        self.assertEqual(ai.API_KEY, before)

    def test_other_errors_do_not_burn_every_key(self):
        keys.add("aaaaaaaaaaaa")
        keys.add("bbbbbbbbbbbb")
        calls = []

        def call(system, user):
            calls.append(1)
            raise RuntimeError("HTTP 400: bad request body")

        with self.assertRaises(RuntimeError):
            keys._rotating(call)("", "")
        self.assertEqual(len(calls), 1)


class LoginTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = mock.patch.dict(os.environ, PASSWORDS)
        cls.env.start()
        auth.load()
        web.auth, web.keys = auth, keys
        handler = preclass_demo.make_handler(None, web)
        handler.log_message = lambda *a: None
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = "http://127.0.0.1:%d" % cls.server.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.env.stop()

    def call(self, path, body=None, cookie="", method=None, headers=None):
        request = urllib.request.Request(self.base + path, method=method,
                                         data=None if body is None else json.dumps(body).encode(),
                                         headers=dict({"Cookie": cookie, "Content-Type": "application/json"}, **(headers or {})))
        try:
            with urllib.request.urlopen(request, timeout=5) as r:
                return r.status, r.headers, r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            return e.code, e.headers, e.read().decode("utf-8")

    def sign_in(self, user, password):
        status, headers, _ = self.call("/login", {"user": user, "password": password})
        self.assertEqual(status, 200)
        self.assertIn("HttpOnly", headers["Set-Cookie"])
        return headers["Set-Cookie"].split(";")[0]

    def test_nothing_without_login(self):
        for path in ("/admin", "/admin/keys", "/admin/data", "/st/widget.js"):
            self.assertEqual(self.call(path)[0], 401, path)
        self.assertEqual(self.call("/ask", {"text": "chào"})[0], 401)
        self.assertEqual(self.call("/admin/keys", {"action": "add", "key": "x" * 20})[0], 401)
        self.assertIn("Đăng nhập", self.call("/", headers={"Accept": "text/html"})[2])
        self.assertEqual(self.call("/login", {"user": "admin", "password": "sai"})[0], 401)

    def test_learner_cannot_reach_admin(self):
        cookie = self.sign_in("hocvien", PASSWORDS["DEMO_PASSWORD"])
        self.assertEqual(self.call("/", cookie=cookie)[0], 200)
        for path in ("/admin", "/admin/keys", "/metrics"):
            status = self.call(path, cookie=cookie, headers={"X-Real-IP": "203.0.113.9"})[0]
            self.assertEqual(status, 403, path)
        self.assertEqual(self.call("/admin/apply", {"id": ""}, cookie=cookie)[0], 403)
        self.assertEqual(self.call("/api/instructor/x", {"a": 1}, cookie=cookie)[0], 403)

    def test_admin_and_logout(self):
        cookie = self.sign_in("admin", PASSWORDS["ADMIN_PASSWORD"])
        self.assertEqual(self.call("/admin", cookie=cookie)[0], 200)
        self.assertEqual(self.call("/backend-mock/.env", cookie=cookie)[0], 404)
        self.call("/logout", cookie=cookie)
        self.assertEqual(self.call("/admin", cookie=cookie)[0], 401)


if __name__ == "__main__":
    unittest.main()
