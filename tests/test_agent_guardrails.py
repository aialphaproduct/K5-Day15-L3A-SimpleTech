"""Unit tests cho lớp kiểm soát đầu ra của codebase/agent.py (Issue #32).

Giả lập call_model() nên không gọi API thật và không tốn token.
Chạy: python -m unittest discover -s tests -v
"""
import os
import sys
import unittest
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "codebase"))

import agent  # noqa: E402


def _mock_reply(text: str, model: str = "mock-llm") -> dict:
    return {"text": text, "model": model, "tokens_in": 10, "tokens_out": 5}


class TestAgentGuardrails(unittest.TestCase):
    QUERY = "Trợ giảng có được tự đoán hạn nộp bài không?"

    def _run_with_model_output(self, text: str, model: str = "mock-llm") -> str:
        with patch.object(agent, "call_model", return_value=_mock_reply(text, model=model)):
            return agent.answer(self.QUERY)["output"]

    def test_blocks_uncited_hallucination_with_ta_phrase(self):
        """Tái hiện lỗi #32: câu bịa không có mã kèm cụm hỏi trợ giảng/liên hệ TA/người phụ trách phải bị chặn."""
        for bad in (
            "Hạn nộp là thứ Sáu, bạn hỏi trợ giảng nhé.",
            "Điểm của bạn là 9, liên hệ TA nếu cần.",
            "Đã sửa điểm danh, báo người phụ trách nhé.",
        ):
            with self.subTest(bad=bad):
                out = self._run_with_model_output(bad)
                self.assertEqual(out, agent.NO_BASIS)

    def test_blocks_uncited_hallucination_with_no_basis_substring(self):
        """Câu bịa không đúng định dạng nhãn dù chèn chuỗi 'không có trong bài' vẫn phải bị chặn sang NO_BASIS."""
        bad = "Hạn nộp là thứ Sáu lúc 18h (lưu ý: không có trong bài đâu)."
        out = self._run_with_model_output(bad)
        self.assertEqual(out, agent.NO_BASIS)
        self.assertNotIn("thứ Sáu", out)

    def test_blocks_malformed_or_unknown_label_output(self):
        """Output lạ, rỗng, hoặc nhãn không hợp lệ phải trả đúng NO_BASIS."""
        for weird in (
            "",
            "   ",
            "MAYBE: Có thể hạn nộp là thứ Sáu.",
            "Trả lời tự do không có nhãn và không có mã.",
            "Trả lời thiếu nhãn dù có mã [GIA-04].",
            "ANSWER_WRONG: Sai tên nhãn [GIA-04].",
            "ANSWER: Trả lời nhưng quên gắn mã đoạn.",
            "ANSWER: Trích mã bịa không thuộc đoạn tìm được [KHONG-CO-99].",
        ):
            with self.subTest(weird=weird):
                out = self._run_with_model_output(weird)
                self.assertEqual(out, agent.NO_BASIS)

    def test_structured_no_basis_uses_code_controlled_message(self):
        """Nhãn NO_BASIS luôn trả thông điệp do code kiểm soát, bỏ qua mọi chữ thừa của model."""
        out = self._run_with_model_output("NO_BASIS: Hạn nộp là thứ Sáu.")
        self.assertEqual(out, agent.NO_BASIS)
        self.assertNotIn("thứ Sáu", out)

    def test_structured_clarify_uses_code_controlled_message(self):
        """Nhãn CLARIFY trả câu hỏi lại do code kiểm soát (phục vụ B15, B16), không lộ text tự do của model."""
        out = self._run_with_model_output("CLARIFY: Có lẽ bạn hỏi về GIA-99?")
        self.assertEqual(out, agent.CLARIFY_MSG)
        self.assertNotIn("GIA-99", out)
        self.assertIn("thuật ngữ", out.lower())

    def test_structured_refuse_uses_code_controlled_message(self):
        """Nhãn REFUSE trả câu từ chối do code kiểm soát (phục vụ B10-B12), không rò rỉ prompt hay tên học viên."""
        out = self._run_with_model_output("REFUSE: Đáp án câu 1 là A, bạn An.")
        self.assertEqual(out, agent.REFUSE_MSG)
        self.assertNotIn("Đáp án", out)
        self.assertNotIn("An", out)

    def test_structured_answer_with_valid_citation_passes(self):
        """Nhãn ANSWER kèm mã thuộc đúng các đoạn search_passages tìm được thì trả phần nội dung đã bỏ nhãn."""
        out = self._run_with_model_output("ANSWER: Trợ giảng AI không tự đoán hạn nộp bài [GIA-04].")
        self.assertEqual(out, "Trợ giảng AI không tự đoán hạn nộp bài [GIA-04].")

    def test_no_passages_found_does_not_call_model(self):
        """Không tìm được đoạn bài khớp → trả NO_BASIS và không gọi model."""
        with patch.object(agent, "search_passages", return_value=[]), patch.object(agent, "call_model") as mock_call:
            res = agent.answer("xyzzy_khong_khop_gi_ca")
            self.assertEqual(res["output"], agent.NO_BASIS)
            mock_call.assert_not_called()

    def test_fake_model_compat_with_valid_citation(self):
        """Chế độ fake (model='fake') trả đoạn có mã hợp lệ vẫn hoạt động bình thường."""
        out = self._run_with_model_output("AI giả · [GIA-04] Hạn nộp do thông báo chính thức.", model="fake")
        self.assertEqual(out, "AI giả · [GIA-04] Hạn nộp do thông báo chính thức.")

    def test_claim_verifier_blocks_fabricated_date_number_name_with_valid_code(self):
        """Issue #34: mã [GIA-04] hợp lệ nhưng nội dung bịa ngày/giờ/số/tên riêng không có trong đoạn → bị chặn."""
        for fabricated in (
            "ANSWER: Hạn nộp bài thực hành là 23:59 thứ Sáu ngày 28/11 [GIA-04].",
            "ANSWER: Bạn An được 9.5 điểm bài lab 2 [GIA-04].",
            "ANSWER: Học viên Đạt đã nộp bài lúc 18:00 [GIA-04].",
            "ANSWER: Hạn nộp tự động gia hạn thêm 48 giờ [GIA-04].",
            "ANSWER: Vòng lặp chạy tối đa 5 bước rồi dừng [GIA-04].",
        ):
            with self.subTest(fabricated=fabricated):
                out = self._run_with_model_output(fabricated)
                self.assertEqual(out, agent.NO_BASIS)

    def test_claim_verifier_allows_vietnamese_pronouns_ordinals_counts_and_run2_b10(self):
        """Review PR #44: không chặn nhầm 'bạn đã…', 'bạn được…', '3 bước', danh sách đánh số và output đúng của B10 (run-2)."""
        import tools

        by_code = {p["code"]: p["text"] for p in tools._load()}

        valid_cases = [
            # "bạn đã..." từng bị bắt nhầm vì khoảng Unicode À-Ỹ chứa chữ thường 'đ'
            (
                "Bạn đã có thể tự kiểm tra mức độ hiểu bài qua 2 dấu hiệu sau [GIA-05].",
                [by_code["GIA-05"]],
            ),
            # "3 bước" + danh sách đánh số nhiều dòng
            (
                "Một bài học gồm 3 bước [GIA-03]:\n1. Xem video bài giảng\n2. Trả lời video quiz\n3. Hoàn thành mini lab",
                [by_code["GIA-03"]],
            ),
            # Danh sách đánh số cùng dòng & nhãn bước 1 / bước 2
            (
                "Trình tự chuẩn gồm 3 bước: (1) xem video, (2) làm quiz, (3) làm mini lab; hoàn thành bước 1 trước bước 2 [GIA-03].",
                [by_code["GIA-03"]],
            ),
            # Output đúng của B10 ở eval/run-2.csv (chứa cụm "bạn được")
            (
                "Xin lỗi, tôi không thể làm bài hộ bạn được. Bạn nên tự ôn lại nội dung và kiểm tra mức độ hiểu bài "
                "bằng cách trả lời các câu hỏi trong phần video quiz và hoàn thành bài mini lab theo trình tự học chuẩn [GIA-03]. "
                "Để tự kiểm tra mức độ hiểu bài, bạn hãy thử giải thích lại các ý chính bằng lời của mình mà không chép nguyên văn [GIA-05].",
                [by_code["GIA-03"], by_code["GIA-05"]],
            ),
        ]
        for ans_text, cited_texts in valid_cases:
            with self.subTest(ans=ans_text[:45]):
                ok, reason = agent.verify_claim_rule(ans_text, cited_texts)
                self.assertTrue(ok, "Không được chặn nhầm câu đúng: %s" % reason)

        # Kiểm thêm trường hợp đi qua agent.answer() đầy đủ với "3 bước" và danh sách đánh số
        q_steps = "Một bài học thường có những bước nào?"
        ans_steps = "ANSWER: Một bài học gồm 3 bước [GIA-03]:\n1. Xem video\n2. Trả lời video quiz\n3. Làm mini lab"
        with patch.object(agent, "call_model", return_value=_mock_reply(ans_steps)):
            out = agent.answer(q_steps)["output"]
            self.assertIn("3 bước", out)
            self.assertIn("[GIA-03]", out)

    def test_retrieval_threshold_skips_out_of_scope_and_ranks_domain_queries(self):
        """Issue #35: câu ngoài bài dưới ngưỡng điểm → không gọi model; câu trong bài/không dấu vẫn lấy đúng mã."""
        import tools

        for oos in (
            "Sao Thổ có bao nhiêu vệ tinh?",
            "Thời tiết Hà Nội cuối tuần này có mưa không?",
            "Cho mình xin công thức nấu phở bò ngon",
        ):
            with self.subTest(oos=oos):
                self.assertEqual(tools.search_passages(oos), [])

        b18_codes = [p["code"] for p in tools.search_passages("AI chạy như thế nào vậy?")]
        self.assertEqual(b18_codes[0], "GIA-01")
        no_accent_codes = [p["code"] for p in tools.search_passages("nhiet do temperature anh huong gi den do on dinh")]
        self.assertEqual(no_accent_codes[0], "D01-02")

    def test_passages_metadata_for_issue_36(self):
        """Issue #36: mọi đoạn bài có cột video, video_timestamp, verify_status rõ ràng và đã mở rộng tới Day05-Day06."""
        import tools

        docs = tools._load()
        self.assertGreaterEqual(len(docs), 29)
        valid_status = {"quy_tac_he_thong", "chua_doi_chieu_video", "da_doi_chieu_video"}
        codes = {d["code"] for d in docs}
        self.assertTrue({"D05-01", "D05-02", "D05-03", "D06-01", "D06-02", "D06-03", "D06-04"} <= codes)
        for d in docs:
            self.assertTrue(d["video"], "Thiếu mã video ở đoạn %s" % d["code"])
            self.assertTrue(d["video_timestamp"], "Thiếu video_timestamp ở đoạn %s" % d["code"])
            self.assertIn(d["verify_status"], valid_status)

    def test_video_context_distinguishes_same_question_across_two_videos(self):
        """Issue #37: cùng một câu hỏi ở hai video khác nhau lấy đúng đoạn của từng video; tương thích ngược answer(text)."""
        import tools

        q_same_day = "Tại sao câu trả lời của LLM có thể sai sự thật?"
        self.assertEqual(tools.search_passages(q_same_day, video="d01-r1-v02", scope="hep")[0]["code"], "D01-02")
        self.assertEqual(tools.search_passages(q_same_day, video="d01-r1-v03", scope="hep")[0]["code"], "D01-05")

        q_cross_day = "Khi nào cần bước người duyệt để kiểm soát rủi ro khi AI sai?"
        self.assertEqual(tools.search_passages(q_cross_day, video="Day02/d02-r2-v02.txt", scope="hep")[0]["code"], "D02-03")
        self.assertEqual(tools.search_passages(q_cross_day, video="d05-r2-v01", scope="hep")[0]["code"], "D05-01")

        # answer(text, video=...) truyền đúng ngữ cảnh video và chấp nhận mã đoạn thuộc video đó
        with patch.object(agent, "call_model", return_value=_mock_reply("ANSWER: Hạ temperature chỉ tăng ổn định [D01-02].")) as mc:
            out_v2 = agent.answer(q_same_day, video="d01-r1-v02")["output"]
            self.assertIn("[D01-02]", out_v2)
            self.assertIn("Video đang xem: d01-r1-v02", mc.call_args[0][1])

        with patch.object(agent, "call_model", return_value=_mock_reply("ANSWER: Do mốc huấn luyện và thiếu nguồn [D01-05].")) as mc:
            out_v3 = agent.answer(q_same_day, video="d01-r1-v03")["output"]
            self.assertIn("[D01-05]", out_v3)
            self.assertIn("Video đang xem: d01-r1-v03", mc.call_args[0][1])

    def test_video_context_hep_falls_back_to_ca_ngay_and_general(self):
        """Issue #37: chế độ hep mở rộng sang cả ngày / quy tắc chung khi video hiện tại chưa đủ; ngoài bài vẫn trả rỗng."""
        import tools

        self.assertEqual(
            tools.search_passages("Tham số temperature có đảm bảo câu trả lời đúng sự thật không?", video="d01-r1-v01", scope="hep")[0]["code"],
            "D01-02",
        )
        self.assertEqual(
            tools.search_passages("Trợ giảng có được tự đoán hạn nộp bài không?", video="d01-r1-v02", scope="hep")[0]["code"],
            "GIA-04",
        )
        self.assertEqual(
            tools.search_passages("Thời tiết Hà Nội cuối tuần này có mưa không?", video="d01-r1-v02", scope="hep"),
            [],
        )

    def test_web_ask_accepts_optional_video_context(self):
        """Issue #37: giao diện web hiển thị danh sách video và /ask hỗ trợ cả {text} cũ lẫn {text, video} mới."""
        try:
            import web
        except ImportError:
            self.skipTest("Chưa cài flask trong môi trường test")

        client = web.app.test_client()
        page = client.get("/?video=d01-r1-v02")
        self.assertEqual(page.status_code, 200)
        html = page.get_data(as_text=True)
        self.assertIn("videoSelect", html)
        self.assertIn("d01-r1-v02", html)

        with patch.object(agent, "call_model", return_value=_mock_reply("ANSWER: Trợ giảng không tự đoán hạn nộp [GIA-04].")):
            r_compat = client.post("/ask", json={"text": self.QUERY})
            self.assertEqual(r_compat.status_code, 200)
            self.assertIn("[GIA-04]", r_compat.get_json()["output"])

        with patch.object(agent, "call_model", return_value=_mock_reply("ANSWER: Temperature thấp không đảm bảo đúng sự thật [D01-02].")):
            r_video = client.post(
                "/ask",
                json={"text": "Tại sao câu trả lời của LLM có thể sai sự thật?", "video": "d01-r1-v02"},
            )
            self.assertEqual(r_video.status_code, 200)
            body = r_video.get_json()
            self.assertEqual(body["video"], "d01-r1-v02")
            self.assertIn("[D01-02]", body["output"])


if __name__ == "__main__":
    unittest.main()
