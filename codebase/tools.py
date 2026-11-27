"""Công cụ của bài toán A1 (trợ giảng bài học) — NHÓM VIẾT. Đọc dữ liệu đoạn bài, không tác động ra ngoài.

Mỗi công cụ có @tool; docstring ghi: tên · input · output · có tác động ra ngoài không.
Dữ liệu đoạn bài: data/lessons/passages.csv (cột code, lesson, text, source).
HIỆN TẠI file này có đoạn GIẢ để luồng chạy được. Thay bằng đoạn bài thật đã viết lại (xem data/DATA_CARD.md).
"""
import csv
import os
import re
import unicodedata

from tracing import tool, TOOLS  # noqa: F401  (TOOLS: danh sách công cụ đã đăng ký)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASSAGES = os.path.join(ROOT, "data", "lessons", "passages.csv")
STOP = {"la", "va", "cua", "co", "khong", "gi", "thi", "mot", "cac", "cho", "de", "voi", "the", "nay",
        "do", "ai", "sao", "nao", "bao", "nhieu", "minh", "ban", "toi", "duoc", "trong", "khi", "lam"}


def _plain(s: str) -> str:
    """Bỏ dấu tiếng Việt, chữ thường — để so khớp từ khoá không phụ thuộc dấu."""
    s = unicodedata.normalize("NFD", s.replace("đ", "d").replace("Đ", "D"))
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn").lower()


def _words(s: str) -> set:
    return {w for w in re.findall(r"[a-z0-9]+", _plain(s)) if w not in STOP and len(w) > 1}


def _load() -> list:
    if not os.path.exists(PASSAGES):
        return []
    with open(PASSAGES, encoding="utf-8-sig", newline="") as f:
        return [{"code": r["code"].strip(), "text": r["text"].strip()} for r in csv.DictReader(f) if r.get("code")]


@tool
def search_passages(query: str) -> list:
    """Tìm tối đa 3 đoạn bài có từ trùng với câu hỏi (không phân biệt dấu).
    Input: câu hỏi (str). Output: danh sách {"code", "text"}, rỗng nếu không đoạn nào khớp. Không tác động ra ngoài."""
    q = _words(query)
    scored = []
    for p in _load():
        overlap = len(q & _words(p["text"]))
        if overlap > 0:
            scored.append((overlap, p))
    scored.sort(key=lambda x: -x[0])
    return [p for _, p in scored[:3]]


@tool
def get_passage(code: str) -> dict:
    """Lấy đúng một đoạn theo mã (vd GIA-01). Input: mã (str). Output: {"code", "text"} hoặc {} nếu không có. Không tác động ra ngoài."""
    for p in _load():
        if p["code"] == code.strip():
            return p
    return {}
