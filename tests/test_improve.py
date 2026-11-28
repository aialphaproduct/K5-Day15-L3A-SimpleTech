import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))

import agent  # noqa: E402
import improve  # noqa: E402


def sets(bench, heldout=(True,)):
    def graded(flags, kind):
        return {"%s%d" % (kind, i): {"type": "kho", "ok": ok, "why": [], "output": "x", "input": "q", "error": False}
                for i, ok in enumerate(flags)}
    return {"bench": graded(bench, "B"), "heldout": graded(heldout, "H")}


class ImproveTest(unittest.TestCase):
    def setUp(self):
        folder = tempfile.mkdtemp()
        for name, value in (("ROUNDS", os.path.join(folder, "r.jsonl")), ("ACTIVE", os.path.join(folder, "a.json"))):
            patch = mock.patch.object(improve, name, value)
            patch.start()
            self.addCleanup(patch.stop)
        self.addCleanup(setattr, agent, "SYSTEM", agent.SYSTEM)

    def test_candidate_must_keep_labels_and_not_copy_questions(self):
        base = improve.ORIGINAL
        self.assertEqual(improve.check_candidate(base + "\nTrả lời ngắn.", base), [])
        self.assertTrue(improve.check_candidate("Cứ trả lời tự do", base))
        self.assertTrue(improve.check_candidate(base + "\nAI chạy như thế nào vậy?", base))
        self.assertTrue(improve.check_candidate(base + "\nLuôn trích [D01-09]", base))

    def test_accept_only_when_better_without_regression(self):
        self.assertEqual(improve.judge(sets([True, False]), sets([True, True]))["verdict"], "ĐỀ XUẤT")
        self.assertEqual(improve.judge(sets([True, False]), sets([False, True]))["verdict"], "LOẠI")
        self.assertEqual(improve.judge(sets([True, False]), sets([True, False]))["verdict"], "LOẠI")
        self.assertEqual(improve.judge(sets([False], (True,)), sets([True], (False,)))["verdict"], "LOẠI")

    def test_only_accepted_round_can_be_applied_and_reverted(self):
        improve.save({"id": "V4", "verdict": "LOẠI", "prompt": "bị loại"})
        improve.save({"id": "V5", "verdict": "ĐỀ XUẤT", "prompt": "prompt mới"})
        self.assertIn("error", improve.apply("V4"))
        self.assertEqual(improve.apply("V5"), {"active": "V5"})
        self.assertEqual(agent.SYSTEM, "prompt mới")
        self.assertEqual(improve.apply(""), {"active": ""})
        self.assertEqual(agent.SYSTEM, improve.ORIGINAL)

    def test_round_never_shows_heldout_to_proposer_and_restores_prompt(self):
        seen = []

        def proposer(system, user):
            seen.append(user)
            return {"text": json.dumps({"prompt": improve.ORIGINAL + "\nHỏi lại khi mơ hồ.", "ly_do": "thử"})}

        with mock.patch.object(improve, "PAUSE", 0), \
                mock.patch.object(agent, "answer", lambda text: {"output": "Không biết."}):
            row = improve.run_round(proposer)
        heldout = improve.gate.questions("benchmark_heldout.csv")
        self.assertFalse([q for q in heldout.values() if q["input"] in seen[0]])
        self.assertEqual(row["verdict"], "LOẠI")
        self.assertEqual(agent.SYSTEM, improve.ORIGINAL)

    def test_versions_come_with_prompt_and_results(self):
        items = improve.versions()
        self.assertEqual([v["id"] for v in items], ["V0", "V1", "V2", "V3"])
        self.assertTrue(all(v["prompt"] and v["results"] for v in items))
        self.assertEqual(items[2]["prompt"], improve.ORIGINAL)


if __name__ == "__main__":
    unittest.main()
