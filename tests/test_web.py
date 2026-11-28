"""Test API và widget của codebase/web.py. Không gọi model thật.
Chạy: python -m unittest discover -s tests -v
"""
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "codebase"))

import web  # noqa: E402


class TestWeb(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        log = patch.object(web.insights, "LOG", os.path.join(tmp.name, "log.jsonl"))
        log.start()
        self.addCleanup(log.stop)
        self.client = web.app.test_client()

    def test_ask_returns_cited_passages_only(self):
        with patch.object(web, "answer", return_value={"output": "Ý [GIA-01] [GIA-01] [KHONG-CO]"}):
            data = self.client.post("/ask", json={"text": "hỏi"}).get_json()
        self.assertEqual([p["code"] for p in data["passages"]], ["GIA-01"])
        self.assertTrue(data["passages"][0]["text"])

    def test_ask_rejects_bad_input_without_calling_agent(self):
        with patch.object(web, "answer") as agent_call:
            bad = [
                self.client.post("/ask", json={"text": "  "}),
                self.client.post("/ask", json={"text": 5}),
                self.client.post("/ask", json=["x"]),
                self.client.post("/ask", json={"text": "a" * (web.MAX_CHARS + 1)}),
                self.client.post("/ask", data=json.dumps({"text": "x"}), content_type="text/plain"),
            ]
        self.assertEqual([r.status_code for r in bad], [400] * len(bad))
        agent_call.assert_not_called()

    def test_greeting_does_not_call_agent_but_questions_do(self):
        with patch.object(web, "answer", return_value={"output": "x"}) as agent_call:
            for text in ("chào bạn", "Xin chào!", "hello"):
                self.assertEqual(self.client.post("/ask", json={"text": text}).get_json()["output"], web.GREETING_REPLY)
            agent_call.assert_not_called()
            self.client.post("/ask", json={"text": "chào bạn, token là gì?"})
        agent_call.assert_called_once()

    def test_ask_hides_agent_errors(self):
        with patch.object(web, "answer", side_effect=RuntimeError("API_KEY=bi-mat")), patch.object(web.app.logger, "exception"):
            res = self.client.post("/ask", json={"text": "hỏi"})
        self.assertEqual(res.status_code, 502)
        self.assertNotIn("bi-mat", res.get_data(as_text=True))

    def test_page_and_widget_are_served(self):
        self.assertIn("Trang mô phỏng", self.client.get("/").get_data(as_text=True))
        res = self.client.get("/widget.js")
        self.assertIn("st-tutor-host", res.get_data(as_text=True))
        res.close()


if __name__ == "__main__":
    unittest.main()
