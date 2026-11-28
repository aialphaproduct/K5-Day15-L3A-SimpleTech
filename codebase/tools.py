"""Công cụ của bài toán A1 (trợ giảng bài học) — NHÓM VIẾT. Đọc dữ liệu đoạn bài, không tác động ra ngoài.

Mỗi công cụ có @tool; docstring ghi: tên · input · output · có tác động ra ngoài không.
Dữ liệu đoạn bài: data/lessons/passages.csv (cột code, lesson, text, source — 20 đoạn tu_viet theo Day01–Day04 và quy tắc pre-class; xem data/DATA_CARD.md).
"""
import csv
import math
import os
import re
import unicodedata

from tracing import tool, TOOLS  # noqa: F401  (TOOLS: danh sách công cụ đã đăng ký)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASSAGES = os.path.join(ROOT, "data", "lessons", "passages.csv")
STOP = {"la", "va", "cua", "co", "khong", "gi", "thi", "mot", "cac", "cho", "de", "voi", "the", "nay",
        "do", "ai", "sao", "nao", "bao", "nhieu", "minh", "ban", "toi", "duoc", "trong", "khi", "lam",
        "nhu", "vay", "ma", "hay", "con", "bi", "se", "da"}

# Mở rộng đồng nghĩa thuật ngữ chung của khoá học (không gắn với câu thử cụ thể)
SYNONYMS = {
    "ai": {"llm"},
    "llm": {"ai"},
    "deadline": {"han", "nop"},
    "quiz": {"kiem", "tra"},
    "bot": {"tro", "giang"},
}


def _plain(s: str) -> str:
    """Bỏ dấu tiếng Việt, chữ thường — để so khớp từ khoá không phụ thuộc dấu."""
    s = unicodedata.normalize("NFD", s.replace("đ", "d").replace("Đ", "D"))
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn").lower()


def _raw_tokens(s: str) -> list:
    """Tách từ giữ nguyên chữ hoa/dấu tiếng Việt để phân biệt từ viết tắt (AI, LLM) và từ đồng âm khác dấu."""
    return re.findall(r"[^\W_]+", unicodedata.normalize("NFC", s))


def _words(s: str, expand: bool = False) -> tuple:
    """Trả về (tập từ không dấu, tập từ giữ dấu viết thường). Giữ từ viết hoa toàn bộ (vd AI, LLM) khỏi STOP."""
    plain_set, exact_set = set(), set()
    for tok in _raw_tokens(s):
        p = _plain(tok)
        if len(p) <= 1:
            continue
        is_acronym = tok.isupper() and len(tok) >= 2
        if p in STOP and not is_acronym:
            continue
        plain_set.add(p)
        exact_set.add(tok.lower())
        if expand and p in SYNONYMS:
            for syn in SYNONYMS[p]:
                plain_set.add(syn)
                exact_set.add(syn)
    return plain_set, exact_set


def _load() -> list:
    if not os.path.exists(PASSAGES):
        return []
    with open(PASSAGES, encoding="utf-8-sig", newline="") as f:
        return [
            {
                "code": r["code"].strip(),
                "lesson": (r.get("lesson") or "").strip(),
                "text": r["text"].strip(),
            }
            for r in csv.DictReader(f)
            if r.get("code")
        ]


@tool
def search_passages(query: str) -> list:
    """Tìm tối đa 3 đoạn bài khớp nhất theo trọng số IDF (khớp đúng dấu với câu có dấu, hỗ trợ câu không dấu, giữ viết tắt AI/LLM và xét thêm tên bài).
    Input: câu hỏi (str). Output: danh sách {"code", "text"}, rỗng nếu không đoạn nào khớp. Không tác động ra ngoài."""
    q_plain, q_exact = _words(query, expand=True)
    if not q_plain:
        return []
    docs = _load()
    if not docs:
        return []

    # Nếu từ trong câu hỏi vốn có dấu tiếng Việt thì tránh khớp nhầm từ khác dấu (vd chạy != chảy)
    q_ascii_only = {w for w in q_exact if w == _plain(w)}

    parsed = []
    df = {}
    for p in docs:
        t_plain, t_exact = _words(p["text"])
        l_plain, _ = _words(p["lesson"])
        combined = t_plain | l_plain
        for w in combined:
            df[w] = df.get(w, 0) + 1
        parsed.append((p, t_plain, t_exact, l_plain))

    n = len(docs)
    scored = []
    for p, t_plain, t_exact, l_plain in parsed:
        score = 0.0
        exact_hits = 0
        for w_exact in q_exact:
            w = _plain(w_exact)
            idf = math.log((n + 1) / (df.get(w, 0) + 1)) + 1.0
            if w_exact in t_exact:
                score += 2.0 * idf
                exact_hits += 1
            elif w_exact in q_ascii_only and w in t_plain:
                score += 1.5 * idf
            if w in l_plain:
                score += 0.8 * idf
        if score > 0:
            scored.append((score, exact_hits, {"code": p["code"], "text": p["text"]}))
    scored.sort(key=lambda x: (-x[0], -x[1]))
    return [item for _, _, item in scored[:3]]


@tool
def get_passage(code: str) -> dict:
    """Lấy đúng một đoạn theo mã (vd GIA-01). Input: mã (str). Output: {"code", "text"} hoặc {} nếu không có. Không tác động ra ngoài."""
    for p in _load():
        if p["code"] == code.strip():
            return {"code": p["code"], "text": p["text"]}
    return {}
