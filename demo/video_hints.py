"""Mốc video phần 1–3 của Bài 1 cho một câu hỏi. Chỉ lưu mốc giây và từ khoá chủ đề, không lưu lời giảng.
Mốc do Claude đối chiếu với file lời giảng của nhóm (không commit); cần người đối chiếu lại trước khi dùng thật.
Video Bài 1 là một bản ghi liên tục nên mốc giây của phần 2, phần 3 cộng thêm từ chỗ phần trước kết thúc.
"""
import re
import unicodedata

# Mã đoạn bài của nhóm → giây trong video. Đoạn không có ở đây: chưa đối chiếu được với video.
# Phần 1: 00:00–05:43. Phần 2 (~05:43–12:11): GIA-01, D01-01..03. Phần 3 (~12:11–): D01-16, D01-05, D01-04 (theo đúng
# thứ tự bài giảng: huấn luyện, rồi giới hạn 2 ảo giác, rồi giới hạn 3 cửa sổ ngữ cảnh). Đối chiếu bằng cách mở video thật.
CODE_TIMES = {"D01-06": 192, "D01-08": 207, "D01-09": 129, "D01-10": 150, "D01-11": 159, "D01-12": 192,
              "D01-13": 207, "D01-14": 254, "D01-15": 286,
              "GIA-01": 540, "D01-02": 486, "D01-03": 503, "D01-01": 693, "D01-04": 818, "D01-05": 787, "D01-16": 731}

# (giây, các cụm từ nhận ra chủ đề). Cụm cụ thể đứng trước.
TOPICS = [
    (265, ("mùa đông",)),
    (275, ("hệ chuyên gia",)),
    (254, ("dartmouth", "1956", "lịch sử ai", "ai bắt đầu")),
    (301, ("transformer", "2017")),
    (286, ("bùng nổ", "alexnet", "imagenet", "2012")),
    (150, ("deep learning", "học sâu", "mạng nơ ron")),
    (140, ("machine learning", "học máy")),
    (159, ("generative", "tạo sinh")),
    (192, ("chatbot",)),
    (217, ("agentic", "discriminative", "ba nhóm")),
    (165, ("llm là gì", "large language", "mô hình ngôn ngữ lớn là")),
    (129, ("ai là gì", "trí tuệ nhân tạo")),
    (486, ("temperature",)),
    (503, ("stop reason", "dừng sinh", "cắt giữa chừng")),
    (540, ("dự đoán token", "sinh văn bản", "token tiếp theo")),
    (693, ("attention", "cơ chế chú ý")),
    (731, ("pre-training", "rlhf", "sft", "ba chặng huấn luyện")),
    (787, ("hallucination", "ảo giác")),
    (818, ("context window", "cửa sổ ngữ cảnh")),
]
MAX_MARKS = 2


def _plain(text):
    text = unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return " %s " % " ".join(re.findall(r"[a-z0-9]+", text))


def label(seconds):
    return "%02d:%02d" % divmod(seconds, 60)


# Câu trỏ vào chỗ đang xem mà không nói rõ là gì.
VAGUE = re.compile(r"\b(doan|cai|cho|y|phan|slide|hinh) (nay|do|kia)\b|\bvua (roi|noi|giang)\b")


def with_context(question, video_at):
    """Câu mơ hồ ("đoạn này là sao") thì kèm chủ đề đang giảng ở phút học viên đang xem."""
    plain = _plain(question)
    if not video_at or len(plain.split()) > 12 or not VAGUE.search(plain):
        return question
    if any(_plain(p) in plain for _, phrases in TOPICS for p in phrases):
        return question
    minutes, seconds = video_at.split(":")
    now = int(minutes) * 60 + int(seconds) + 2
    passed = [t for t in TOPICS if t[0] <= now]
    if not passed:
        return question
    return "%s (đang xem đoạn: %s)" % (question, max(passed)[1][0])


def time_of(code):
    """Mốc video của một đoạn bài, None nếu chưa đối chiếu được với video."""
    seconds = CODE_TIMES.get(code)
    return None if seconds is None else {"seconds": seconds, "label": label(seconds)}


def find(question, codes):
    """Ưu tiên mốc gắn với đoạn được trích; không có thì gợi ý theo chủ đề trong câu hỏi."""
    mapped = sorted({CODE_TIMES[c] for c in codes if c in CODE_TIMES})
    if mapped:
        return [{"seconds": s, "label": label(s), "suggested": False} for s in mapped[:MAX_MARKS]]
    asked = _plain(question)
    hits = [s for s, phrases in TOPICS if any(_plain(p) in asked for p in phrases)]
    # Hai chủ đề chung (định nghĩa AI, LLM) chỉ dùng khi không khớp chủ đề cụ thể nào.
    hits = [s for s in hits if s not in (129, 165)] or hits
    return [{"seconds": s, "label": label(s), "suggested": True} for s in hits[:MAX_MARKS]]
