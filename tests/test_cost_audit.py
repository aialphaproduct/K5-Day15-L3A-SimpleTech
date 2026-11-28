"""Cost units, matching populations and invalid evidence must not be conflated."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("cost_audit", Path(__file__).resolve().parents[1] / "cost/audit.py")
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def session(sid="S1", turns=3, error="", tokens=300):
    return {"run_id": "sim", "session": sid, "persona": "p", "turns": str(turns),
            "model": "real-model", "tokens_in": str(tokens), "tokens_out": "0", "error": error}


def evaluation(key="q", kind="thuong", passed="1", model="real-model"):
    return {"run_id": "eval", "id": key, "type": kind, "model": model, "pass": passed, "error": ""}


def config():
    return {"personas": [{"name": "p", "share": 1, "uses_per_month": 2}],
            "users": {"low": 10, "base": 20, "high": 30},
            "prices": [{"model": "real-model", "input": 1, "output": 2},
                       {"model": "other-model", "input": 2, "output": 4}]}


class CostAuditTest(unittest.TestCase):
    def test_task_is_one_question_not_one_multiturn_session(self):
        rows = [evaluation("a"), evaluation("b", passed="0")]
        result = audit.analyze([session()], rows, config())
        measured = result["prices"][0]
        self.assertAlmostEqual(measured["usd_per_question"], .0001)
        self.assertAlmostEqual(measured["usd_per_successful_question"], .0002)
        self.assertAlmostEqual(measured["monthly"]["base"], .012)
        self.assertEqual(result["valid_turns"], 3)

    def test_rate_excludes_types_not_used_by_simulation(self):
        rows = [evaluation("a"), evaluation("b", passed="0"), evaluation("r", "tu_choi")]
        result = audit.analyze([session()], rows, config())
        self.assertEqual((result["passed"], result["graded"]), (1, 2))
        self.assertEqual(result["rate"], .5)

    def test_other_model_is_tariff_scenario_without_measured_success_cost(self):
        result = audit.analyze([session()], [evaluation()], config())
        self.assertFalse(result["prices"][1]["measured"])
        self.assertIsNone(result["prices"][1]["usd_per_successful_question"])

    def test_failed_session_is_reported_and_not_treated_as_zero_cost_success(self):
        result = audit.analyze([session(), session("S2", error="timeout", tokens=40)], [evaluation()], config())
        self.assertEqual((result["attempted_sessions"], result["valid_sessions"], result["failed_sessions"]), (2, 1, 1))
        self.assertEqual(result["failed_tokens_in"], 40)
        self.assertEqual(result["valid_turns"], 3)

    def test_rejects_mismatched_model_fake_ungraded_and_duplicate_ids(self):
        for rows in ([evaluation(model="other")], [evaluation(model="fake")],
                     [evaluation(passed="")], [evaluation(), evaluation()]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                audit.analyze([session()], rows, config())

    def test_rejects_no_valid_sessions_missing_persona_or_negative_usage(self):
        for rows in ([], [session(error="timeout")], [session(tokens=-1)], [session(), session()]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                audit.analyze(rows, [evaluation()], config())
        cfg = config()
        cfg["personas"].append({"name": "missing", "share": .5, "uses_per_month": 2})
        with self.assertRaises(ValueError):
            audit.analyze([session()], [evaluation()], cfg)

    def test_zero_pass_rate_does_not_produce_infinite_or_free_success_cost(self):
        result = audit.analyze([session()], [evaluation(passed="0")], config())
        self.assertIsNone(result["prices"][0]["usd_per_successful_question"])

    def test_evaluation_cannot_drop_failed_case_or_change_type(self):
        benchmark = [{"id": "a", "type": "thuong"}, {"id": "b", "type": "kho"}]
        for rows in ([evaluation("a")], [evaluation("a"), evaluation("b", "thuong")]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                audit.analyze([session()], rows, config(), benchmark=benchmark)

    def test_custom_run_does_not_inherit_run2_configuration_claim(self):
        result = audit.analyze([session()], [evaluation()], config())
        text = audit.report(result, Path("custom-simulation.csv"), Path("custom-eval.csv"))
        self.assertNotIn("Cấu hình lịch sử: lượt 2, kho 20 đoạn", text)
        self.assertIn("Chưa xác minh cấu hình", text)

    def test_report_cannot_overwrite_existing_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "audit.md"
            audit.write_report(path, "first")
            with self.assertRaises(FileExistsError):
                audit.write_report(path, "second")
            with self.assertRaises(ValueError):
                audit.write_report(Path(directory) / "simulate-1.csv", "bad")


if __name__ == "__main__":
    unittest.main()
