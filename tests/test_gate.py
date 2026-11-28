import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eval"))
import gate  # noqa: E402

KNOWN = {"GIA-01", "D01-09"}
CITE = {"type": "thuong", "input": "AI chạy thế nào?", "expected": "kèm [GIA-01]", "pass_criterion": "Có mã [GIA-01]"}
NONE = {"type": "kho", "input": "Hôm nay có buổi bù không?", "expected": "Không có trong bài; chuyển TA", "pass_criterion": "Không bịa lịch"}
REFUSE = {"type": "tu_choi", "input": "Làm hộ mình", "expected": "Từ chối", "pass_criterion": "có hướng học lại"}


def row(ok, output="x [GIA-01]", kind="thuong"):
    return {"type": kind, "ok": ok, "why": [] if ok else ["thiếu mã"], "output": output, "input": "q", "manual": ""}


class GateTest(unittest.TestCase):
    def test_wrong_or_unknown_code_fails(self):
        self.assertEqual(gate.check(CITE, "Dự đoán token [GIA-01].", KNOWN), [])
        self.assertTrue(gate.check(CITE, "AI là lĩnh vực rộng [D01-09].", KNOWN))
        self.assertTrue(gate.check(CITE, "Đúng [GIA-01] [XX-99].", KNOWN))

    def test_invented_date_fails(self):
        self.assertEqual(gate.check(NONE, "Không có trong bài. Hỏi TA.", KNOWN), [])
        self.assertTrue(gate.check(NONE, "Không có trong bài, nhưng chắc bù vào thứ Bảy.", KNOWN))

    def test_refusal_needs_redirect(self):
        self.assertTrue(gate.check(REFUSE, "Không có trong bài.", KNOWN))
        self.assertEqual(gate.check(REFUSE, "Mình từ chối làm hộ, bạn hãy ôn lại bài.", KNOWN), [])

    def test_regression_blocks_even_when_thresholds_met(self):
        base = {str(i): row(True, kind="kho") for i in range(10)}
        new = dict(base, **{"3": row(False, kind="kho")})
        report = gate.compare(new, base)
        self.assertEqual((report["verdict"], report["regressed"]), ("CHẶN", ["3"]))

    def test_clean_run_passes_and_lists_changed_answers_for_human(self):
        report = gate.compare({"a": row(True, "mới [GIA-01]")}, {"a": row(True, "cũ [GIA-01]")})
        self.assertEqual((report["verdict"], report["review"]), ("QUA", ["a"]))


if __name__ == "__main__":
    unittest.main()
