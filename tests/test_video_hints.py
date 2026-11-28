import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demo"))

import video_hints  # noqa: E402


def marks(question, codes=()):
    return [(m["label"], m["suggested"]) for m in video_hints.find(question, list(codes))]


class TestVideoHints(unittest.TestCase):
    def test_cited_passage_uses_checked_time(self):
        self.assertEqual(marks("hỏi gì đó", ["D01-06"]), [("03:12", False)])

    def test_topic_in_question_gives_suggestion_with_or_without_accents(self):
        self.assertEqual(marks("Vì sao AI bùng nổ bây giờ?"), [("04:46", True)])
        self.assertEqual(marks("mua dong AI la gi"), [("04:25", True)])
        self.assertEqual(marks("LLM có phải là chatbot không?"), [("03:12", True)])

    def test_vague_question_takes_topic_at_current_minute(self):
        self.assertEqual(video_hints.with_context("đoạn này là sao ạ", "03:15"), "đoạn này là sao ạ (đang xem đoạn: chatbot)")
        for text, at in (("đoạn này là sao ạ", ""), ("đoạn này là sao ạ", "00:20"), ("chatbot là gì", "03:15"),
                         ("cái này khác machine learning sao", "03:15")):
            self.assertEqual(video_hints.with_context(text, at), text, (text, at))

    def test_passage_time_only_for_part_one(self):
        self.assertEqual(video_hints.time_of("D01-15"), {"seconds": 286, "label": "04:46"})
        self.assertIsNone(video_hints.time_of("GIA-04"))

    def test_questions_outside_part_one_get_no_time(self):
        for text in ("Hôm nay có buổi bù không?", "Điểm của mình là bao nhiêu?", "Hạn nộp lab là khi nào?"):
            self.assertEqual(marks(text), [], text)
        self.assertEqual(marks("Bài tập tuần 3 nộp ở đâu?", ["GIA-04"]), [])

    def test_part_two_and_three_have_checked_times(self):
        self.assertEqual(video_hints.time_of("GIA-01"), {"seconds": 540, "label": "09:00"})
        self.assertEqual(video_hints.time_of("D01-04"), {"seconds": 818, "label": "13:38"})
        self.assertEqual(marks("Cửa sổ ngữ cảnh là gì?", ["D01-04"]), [("13:38", False)])
        self.assertEqual(marks("Model có hay bị ảo giác (hallucination) không?"), [("13:07", True)])
        self.assertEqual(marks("Model được huấn luyện qua pre-training, SFT, RLHF như nào?"), [("12:11", True)])


if __name__ == "__main__":
    unittest.main()
