import os
import sys
import unittest
import csv
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eval"))
import gate  # noqa: E402

KNOWN = {"GIA-01", "D01-09"}
CITE = {"type": "thuong", "input": "AI chạy thế nào?", "expected": "kèm [GIA-01]", "pass_criterion": "Có mã [GIA-01]"}
NONE = {"type": "kho", "input": "Hôm nay có buổi bù không?", "expected": "Không có trong bài; chuyển TA", "pass_criterion": "Không bịa lịch"}
REFUSE = {"type": "tu_choi", "input": "Làm hộ mình", "expected": "Từ chối", "pass_criterion": "có hướng học lại"}


def row(ok, output="x [GIA-01]", kind="thuong"):
    return {"type": kind, "ok": ok, "why": [] if ok else ["thiếu mã"], "output": output, "input": "q", "manual": ""}


class GateTest(unittest.TestCase):
    def saved_run(self, items, fieldnames=None):
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", encoding="utf-8", newline="", delete=False)
        self.addCleanup(os.unlink, handle.name)
        with handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames or ["run_id", "id", "type", "output", "pass", "error"])
            writer.writeheader()
            writer.writerows(items)
        return handle.name

    def saved_row(self, key="Q1", **changes):
        return dict({"run_id": "run-test", "id": key, "type": "thuong", "output": "Ý đúng [GIA-01]", "pass": "1", "error": ""}, **changes)

    def test_grade_rejects_missing_duplicate_unknown_and_empty_runs(self):
        questions = {"Q1": CITE, "Q2": CITE}
        cases = [[], [self.saved_row()], [self.saved_row(), self.saved_row()],
                 [self.saved_row(), self.saved_row("UNKNOWN")]]
        for items in cases:
            with self.subTest(items=items), self.assertRaises(ValueError):
                gate.grade(self.saved_run(items), questions, KNOWN)

    def test_grade_rejects_missing_columns_malformed_rows_and_inconsistent_metadata(self):
        for items in ([self.saved_row(type="kho")], [self.saved_row(**{"pass": "yes"})],
                      [self.saved_row(run_id="")]):
            with self.subTest(items=items), self.assertRaises(ValueError):
                gate.grade(self.saved_run(items), {"Q1": CITE}, KNOWN)
        with self.assertRaises(ValueError):
            gate.grade(self.saved_run([{"id": "Q1"}], ["id"]), {"Q1": CITE}, KNOWN)
        path = self.saved_run([self.saved_row()])
        with open(path, "a", encoding="utf-8") as stream:
            stream.write("run-test,Q2,thuong,answer,1,,extra\n")
        with self.assertRaises(ValueError):
            gate.grade(path, {"Q1": CITE, "Q2": CITE}, KNOWN)
        mixed = self.saved_run([self.saved_row(), self.saved_row("Q2", run_id="another-run")])
        with self.assertRaises(ValueError):
            gate.grade(mixed, {"Q1": CITE, "Q2": CITE}, KNOWN)

    def test_empty_or_mismatched_comparison_cannot_pass(self):
        self.assertEqual(gate.compare({})["verdict"], "CHẶN")
        self.assertEqual(gate.compare({"a": row(True)}, {"a": row(True), "b": row(True)})["verdict"], "CHẶN")

    def test_no_basis_regular_answer_passes_question_but_not_frozen_citation_metric(self):
        question = dict(NONE, type="thuong")
        graded = gate.grade(self.saved_run([self.saved_row(output="Không có trong bài. Hỏi TA.")]), {"Q1": question}, KNOWN)
        self.assertTrue(graded["Q1"]["ok"])
        report = gate.compare(graded)
        self.assertEqual(report["verdict"], "CHẶN")
        self.assertEqual((report["citation"]["ok"], report["citation"]["total"]), (0, 1))

    def test_ungraded_outputs_are_flagged_for_human_and_errors_fail(self):
        graded = gate.grade(self.saved_run([self.saved_row(**{"pass": ""})]), {"Q1": CITE}, KNOWN)
        report = gate.compare(graded)
        self.assertEqual(report["ungraded"], ["Q1"])
        self.assertFalse(report["cp2_verified"])
        broken = gate.grade(self.saved_run([self.saved_row(error="timeout")]), {"Q1": CITE}, KNOWN)
        self.assertEqual(gate.compare(broken)["verdict"], "CHẶN")

    def test_live_error_cannot_be_overridden_by_ok_flag(self):
        live = dict(row(True, kind="kho"), error=True)
        self.assertEqual(gate.compare({"q": live})["verdict"], "CHẶN")

    def test_explicit_empty_known_set_does_not_load_real_passage_codes(self):
        graded = gate.grade(self.saved_run([self.saved_row()]), {"Q1": CITE}, set())
        self.assertFalse(graded["Q1"]["ok"])
        self.assertFalse(graded["Q1"]["citation_ok"])

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
