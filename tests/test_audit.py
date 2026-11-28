"""Audit invariants: historical pass is never substituted for a frozen metric."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / "eval" / "audit.py"
SPEC = importlib.util.spec_from_file_location("metric_audit", MODULE)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class AuditTest(unittest.TestCase):
    def test_citation_requires_known_and_expected_codes_without_label_requirement(self):
        question = {"expected": "Use [DOC-1]", "pass_criterion": "cite [DOC-1]"}
        self.assertTrue(audit.citation_check(question, "Explanation [DOC-1].", {"DOC-1", "DOC-2"}))
        for output in ("Explanation.", "Explanation [DOC-2].", "Explanation [DOC-1] [UNKNOWN]."):
            self.assertFalse(audit.citation_check(question, output, {"DOC-1", "DOC-2"}))

    def test_sources_exclude_member_unverified_and_unconfirmed_source_labels(self):
        questions = [{"id": str(i), "source": "nguoi_dung: interview"} for i in range(5)]
        metadata = {
            "0": {"status": "verified_external", "reference": "interview A"},
            "1": {"status": "member", "reference": "interview B"},
            "2": {"status": "unverified", "reference": "pending"},
        }
        result = audit.audit_sources(questions, metadata)
        self.assertEqual((result["claimed"], result["verified"], result["needed"]), (5, 1, 2))
        self.assertFalse(result["met"])

    def test_pass_and_necessary_metric_conditions_are_separate(self):
        questions = [{"id": "q", "type": "thuong", "expected": "No basis", "pass_criterion": "redirect"}]
        rows = [{"id": "q", "type": "thuong", "output": "Không có trong bài. Hỏi TA.", "pass": "1", "error": ""}]
        result = audit.audit_run(rows, questions, {"DOC-1"})
        self.assertEqual(result["groups"]["thuong"]["pass"], 1)
        self.assertEqual(result["citation"]["count"], 0)
        self.assertEqual(result["citation"]["total"], 1)
        self.assertFalse(result["meaning"]["sample_sufficient"])
        self.assertIsNone(result["meaning"]["grade"])

    def test_no_basis_phrase_is_a_condition_not_a_semantic_grade(self):
        questions = [{"id": "q", "type": "kho", "expected": "", "pass_criterion": ""}]
        rows = [{"id": "q", "type": "kho", "output": "Hỏi TA, nhưng hạn chắc là ngày mai.", "pass": "0", "error": ""}]
        result = audit.audit_run(rows, questions, set())
        self.assertEqual(result["no_basis"]["kho"]["count"], 1)
        self.assertEqual(result["groups"]["kho"]["pass"], 0)
        self.assertIsNone(result["no_basis"]["kho"]["grade"])

    def test_missing_or_duplicate_run_ids_are_not_silently_skipped(self):
        questions = [{"id": "q", "type": "thuong", "expected": "", "pass_criterion": ""}]
        with self.assertRaises(ValueError):
            audit.audit_run([], questions, set())
        row = {"id": "q", "type": "thuong", "pass": "1", "output": "", "error": ""}
        with self.assertRaises(ValueError):
            audit.audit_run([row, row], questions, set())

    def test_report_output_is_exclusive_and_only_markdown(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "audit.md"
            audit.write_report(path, "report")
            with self.assertRaises(FileExistsError):
                audit.write_report(path, "replacement")
            self.assertEqual(path.read_text(encoding="utf-8"), "report")
            with self.assertRaises(ValueError):
                audit.write_report(Path(directory) / "run-1.csv", "replacement")


if __name__ == "__main__":
    unittest.main()
