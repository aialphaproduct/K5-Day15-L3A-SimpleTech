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


# Ngưỡng tối thiểu để tránh gọi model khi câu hỏi chỉ trùng 1 từ lạc chủ đề (Issue #35)
MIN_SCORE = 2.5
MIN_COVERAGE = 0.45


def _plain(s: str) -> str:
    """Bỏ dấu tiếng Việt, chữ thường — để so khớp từ khoá không phụ thuộc dấu."""
    s = unicodedata.normalize("NFD", s.replace("đ", "d").replace("Đ", "D"))
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn").lower()


def _raw_tokens(s: str) -> list:
    """Tách từ giữ nguyên chữ hoa/dấu tiếng Việt để phân biệt từ viết tắt (AI, LLM) và từ đồng âm khác dấu."""
    return re.findall(r"[^\W_]+", unicodedata.normalize("NFC", s))


def _bigrams(tokens: list) -> set:
    return {tokens[i] + "_" + tokens[i + 1] for i in range(len(tokens) - 1)}


def _seq_tokens(s: str, expand: bool = False) -> tuple:
    """Trả về (danh sách từ không dấu, danh sách từ giữ dấu viết thường) giữ nguyên thứ tự và tần suất."""
    plain_list, exact_list = [], []
    for tok in _raw_tokens(s):
        p = _plain(tok)
        if len(p) <= 1:
            continue
        is_acronym = tok.isupper() and len(tok) >= 2
        if p in STOP and not is_acronym:
            continue
        plain_list.append(p)
        exact_list.append(tok.lower())
        if expand and p in SYNONYMS:
            for syn in SYNONYMS[p]:
                plain_list.append(syn)
                exact_list.append(syn)
    return plain_list, exact_list


def _words(s: str, expand: bool = False) -> tuple:
    """Trả về (tập từ không dấu, tập từ giữ dấu viết thường). Giữ từ viết hoa toàn bộ (vd AI, LLM) khỏi STOP."""
    plain_list, exact_list = _seq_tokens(s, expand=expand)
    return set(plain_list), set(exact_list)


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
    """Tìm tối đa 3 đoạn bài khớp nhất bằng BM25 lai (IDF riêng cho text/lesson, khớp đúng dấu, bigram và ngưỡng điểm lọc câu ngoài bài).
    Input: câu hỏi (str). Output: danh sách {"code", "text"}, rỗng nếu dưới ngưỡng điểm. Không tác động ra ngoài."""
    q_base_plain, _ = _seq_tokens(query, expand=False)
    q_plain_seq, q_exact_seq = _seq_tokens(query, expand=True)
    if not q_plain_seq:
        return []
    docs = _load()
    if not docs:
        return []

    q_base_count = max(len(set(q_base_plain)), 1)
    q_exact_unique = list(dict.fromkeys(q_exact_seq))
    # Nếu từ trong câu hỏi vốn có dấu tiếng Việt thì tránh khớp nhầm từ khác dấu (vd chạy != chảy)
    q_ascii_only = {w for w in q_exact_unique if w == _plain(w)}
    q_bigrams = _bigrams([_plain(w) for w in _raw_tokens(query) if len(_plain(w)) > 1])

    parsed, df_text, df_lesson = [], {}, {}
    total_len = 0
    for p in docs:
        t_plain_seq, t_exact_seq = _seq_tokens(p["text"])
        l_plain_seq, _ = _seq_tokens(p["lesson"])
        tf_plain, tf_exact = {}, {}
        for w in t_plain_seq:
            tf_plain[w] = tf_plain.get(w, 0) + 1
        for w in t_exact_seq:
            tf_exact[w] = tf_exact.get(w, 0) + 1
        l_set = set(l_plain_seq)
        doc_len = max(len(t_plain_seq), 1)
        total_len += doc_len
        for w in set(tf_plain):
            df_text[w] = df_text.get(w, 0) + 1
        for w in l_set:
            df_lesson[w] = df_lesson.get(w, 0) + 1
        t_bigrams = _bigrams([_plain(w) for w in _raw_tokens(p["text"]) if len(_plain(w)) > 1])
        parsed.append((p, tf_plain, tf_exact, l_set, doc_len, t_bigrams))

    n = len(docs)
    avgdl = total_len / n
    k1, b = 1.2, 0.75
    scored = []
    for p, tf_plain, tf_exact, l_set, doc_len, t_bigrams in parsed:
        score = 0.0
        exact_hits = 0
        matched_terms = set()
        for w_exact in q_exact_unique:
            w = _plain(w_exact)
            n_t = df_text.get(w, 0)
            if n_t > 0:
                idf_t = math.log((n - n_t + 0.5) / (n_t + 0.5) + 1.0)
                tf_e = tf_exact.get(w_exact, 0)
                tf_p = tf_plain.get(w, 0) if w_exact in q_ascii_only else 0
                if tf_e > 0:
                    bm25 = idf_t * (tf_e * (k1 + 1)) / (tf_e + k1 * (1 - b + b * doc_len / avgdl))
                    score += 1.6 * bm25
                    exact_hits += 1
                    matched_terms.add(w)
                elif tf_p > 0:
                    bm25 = idf_t * (tf_p * (k1 + 1)) / (tf_p + k1 * (1 - b + b * doc_len / avgdl))
                    score += 1.25 * bm25
                    matched_terms.add(w)
            n_l = df_lesson.get(w, 0)
            if n_l > 0 and w in l_set:
                idf_l = math.log((n - n_l + 0.5) / (n_l + 0.5) + 1.0)
                score += 0.6 * idf_l
                matched_terms.add(w)
        score += len(q_bigrams & t_bigrams) * 1.0
        coverage = len(matched_terms) / q_base_count
        if score >= MIN_SCORE and (len(matched_terms) >= 2 or coverage >= MIN_COVERAGE):
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
