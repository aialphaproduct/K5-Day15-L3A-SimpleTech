"""Test phần đo lường. Không gọi model thật, log ghi vào thư mục tạm."""
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "codebase"))

import agent  # noqa: E402
import insights  # noqa: E402
import web  # noqa: E402


class TestInsights(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.log = patch.object(insights, "LOG", os.path.join(self.tmp.name, "log.jsonl"))
        self.log.start()
        self.client = web.app.test_client()

    def tearDown(self):
        self.log.stop()
        self.tmp.cleanup()

    def test_each_turn_is_logged_with_outcome_and_anonymous_learner(self):
        with patch.object(web, "answer", return_value={"output": agent.CLARIFY_MSG}):
            self.client.post("/ask", json={"text": "cái đó là sao", "learner": "HV-ab12", "at": "03:12"})
        self.client.post("/ask", json={"text": "chào bạn", "learner": "<script>", "at": "abc"})
        data = self.client.get("/admin/data").get_json()
        first, greeting = data["chats"][1], data["chats"][0]
        self.assertEqual((first["outcome"], first["learner"], first["video_at"]), ("hoi_lai", "HV-ab12", "03:12"))
        self.assertTrue(first["advice"])
        self.assertEqual((greeting["outcome"], greeting["learner"], greeting["video_at"]), ("chao", "HV-an-danh", ""))
        self.assertEqual((data["totals"]["turns"], data["totals"]["questions"]), (2, 1))

    def test_cost_uses_price_table_and_never_guesses(self):
        self.assertAlmostEqual(insights.cost_of(["gemini-3.1-flash-lite"], 1_000_000, 1_000_000), 1.75)
        self.assertIsNone(insights.cost_of(["model-la"], 10, 10))

    def test_outcome_classification(self):
        self.assertEqual(insights.classify(agent.NO_BASIS, ["dừng: không có đoạn nào khớp câu hỏi"], False), "khong_co_doan")
        self.assertEqual(insights.classify(agent.NO_BASIS, ["nhãn kiểm soát bởi code: NO_BASIS"], False), "khong_can_cu")
        self.assertEqual(insights.classify(agent.NO_BASIS, ["chặn: sai mã"], False), "bi_chan")
        self.assertEqual(insights.classify("Ý [GIA-01]", [], False), "tra_loi")

    def test_admin_rejects_other_hosts_and_plain_text_posts(self):
        self.assertEqual(self.client.get("/admin/data", headers={"Host": "evil.test"}).status_code, 403)
        self.assertEqual(self.client.post("/admin/analyze", data="{}", content_type="text/plain").status_code, 400)

    def test_analysis_parses_model_json_and_is_stored(self):
        with patch.object(web, "answer", return_value={"output": agent.NO_BASIS}):
            self.client.post("/ask", json={"text": "token là gì"})
        reply = {"text": 'x {"luot":[],"sua_prompt":["a"],"bo_sung_doan":["b"]} y', "model": "m"}
        with patch.object(insights, "call_model", return_value=reply):
            out = self.client.post("/admin/analyze", json={}).get_json()
        self.assertEqual((out["prompt_changes"], out["passage_gaps"]), (["a"], ["b"]))
        self.assertEqual(self.client.get("/admin/data").get_json()["analysis"]["sample"], 1)


if __name__ == "__main__":
    unittest.main()
