"""Kiểm số đếm và mẫu số khi có dòng ngoài phạm vi hoặc thiếu trường."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("count_tutor", Path(__file__).resolve().parents[1] / "evidence/count_tutor.py")
counter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(counter)


class TutorCountsTest(unittest.TestCase):
    def test_filter_missing_transcript_and_denominators(self):
        base = dict(agent_id="teaching_assistant", kind="question", hv="anonymous-a",
                    transcript="Day01/video", cached="False", guidance_ids="[]")
        rows = [dict(base, cached="True", guidance_ids='["g"]', do_dai_cau_hoi="10"),
                dict(base, transcript="", do_dai_cau_hoi="20"),
                dict(base, hv="anonymous-b", transcript="Day02/video"),
                dict(base, kind="reply"), dict(base, agent_id="other")]
        got = counter.summarize(rows)
        self.assertEqual((got["questions"], got["people"], got["one_question"]), (3, 2, 1))
        self.assertEqual(dict(got["days"]), {"Day01": 1, "Day02": 1})
        self.assertEqual((got["cached"], got["guidance"], got["context"]), (1, 1, 0))
        self.assertEqual(got["lengths"]["do_dai_cau_hoi"], 15)
        self.assertEqual(got["top_share"], 2 / 3)

    def test_empty_filtered_set_is_explicit_error(self):
        with self.assertRaisesRegex(ValueError, "Không có câu hỏi"):
            counter.summarize([])


if __name__ == "__main__":
    unittest.main()
