"""Tách 3 persona (dùng ít / vừa / nhiều) từ hành vi thật trong data/preclass/chat.csv.

Chạy:
    python evidence/count_personas.py "<đường dẫn tới data/preclass>"

Quy ước đo (Issue #38 & #13):
  - Tập lọc khớp evidence/count_tutor.py (#5): agent_id == "teaching_assistant", kind == "question"
    trong cửa sổ dữ liệu 05/11/2026 -> 25/11/2026 (21 ngày lịch).
  - Định nghĩa phiên: cột session_id gần như trống (1/1.091 dòng), nên gom các câu hỏi liên tiếp
    của cùng một học viên (hv) theo thứ tự asked_at: khoảng nghỉ <= 30 phút tính chung 1 phiên,
    khoảng nghỉ > 30 phút mở phiên mới.
  - Quy đổi sang tháng (30 ngày): uses_per_month = (số phiên / học viên trong 21 ngày) * (30 / 21).
  - Phân nhóm theo tổng số câu hỏi trong 21 ngày:
      * dung_it:    1–2 câu
      * dung_vua:   3–10 câu
      * dung_nhieu: >= 11 câu

Chỉ in số đã tổng hợp, không in mã học viên hay dữ liệu cá nhân.
"""
import csv
import os
import sys
from collections import defaultdict
from datetime import datetime

GAP_MINUTES = 30
WINDOW_DAYS = 21
MONTH_DAYS = 30


def bucket_of(n_questions: int) -> str:
    if n_questions <= 2:
        return "dung_it"
    if n_questions <= 10:
        return "dung_vua"
    return "dung_nhieu"


def main() -> int:
    folder = sys.argv[1] if len(sys.argv) > 1 else os.path.join("data", "preclass")
    chat_path = os.path.join(folder, "chat.csv")
    if not os.path.exists(chat_path):
        sys.exit("Không tìm thấy %s. Truyền đường dẫn tới thư mục data/preclass của BTC." % chat_path)

    by_hv = defaultdict(list)
    non_empty_sid = 0
    total_q = 0
    with open(chat_path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r.get("agent_id") == "teaching_assistant" and r.get("kind") == "question":
                total_q += 1
                if (r.get("session_id") or "").strip():
                    non_empty_sid += 1
                dt = datetime.fromisoformat(r["asked_at"].replace("Z", "+00:00"))
                by_hv[r["hv"]].append(dt)

    groups = defaultdict(list)
    total_sessions = 0
    for _, times in by_hv.items():
        times.sort()
        sessions = []
        cur = [times[0]]
        for t in times[1:]:
            if (t - cur[-1]).total_seconds() > GAP_MINUTES * 60:
                sessions.append(cur)
                cur = [t]
            else:
                cur.append(t)
        sessions.append(cur)
        n_q = len(times)
        n_s = len(sessions)
        total_sessions += n_s
        groups[bucket_of(n_q)].append((n_q, n_s, [len(s) for s in sessions]))

    n_hv = len(by_hv)
    print("Tập lọc: agent_id=teaching_assistant, kind=question (05/11–25/11/2026, %d ngày)" % WINDOW_DAYS)
    print("Tổng câu hỏi: %d · Học viên có >=1 câu: %d · Dòng có session_id: %d/%d (%.1f%%)"
          % (total_q, n_hv, non_empty_sid, total_q, non_empty_sid / total_q * 100 if total_q else 0))
    print("Định nghĩa phiên: ngắt phiên khi khoảng nghỉ > %d phút -> tổng %d phiên (TB %.2f lượt/phiên)"
          % (GAP_MINUTES, total_sessions, total_q / total_sessions if total_sessions else 0))
    print()

    labels = {
        "dung_it": "dung_it (1–2 câu)",
        "dung_vua": "dung_vua (3–10 câu)",
        "dung_nhieu": "dung_nhieu (>=11 câu)",
    }
    modeled_q_per_month = 0.0
    for key in ("dung_it", "dung_vua", "dung_nhieu"):
        arr = groups[key]
        g_hv = len(arr)
        g_q = sum(x[0] for x in arr)
        g_s = sum(x[1] for x in arr)
        share_pct = g_hv / n_hv * 100
        q_pct = g_q / total_q * 100
        s_per_hv_21d = g_s / g_hv
        uses_per_month = s_per_hv_21d * (MONTH_DAYS / WINDOW_DAYS)
        turns_mean = g_q / g_s
        all_turns = sorted(t for x in arr for t in x[2])
        turns_med = all_turns[len(all_turns) // 2]
        print("- %s: %d/%d học viên (%.1f%%) · %d/%d câu (%.1f%%) · %d phiên"
              % (labels[key], g_hv, n_hv, share_pct, g_q, total_q, q_pct, g_s))
        print("  -> %.2f phiên/người (21 ngày) x 30/21 = %.2f phiên/tháng · lượt/phiên TB %.2f (median %d)"
              % (s_per_hv_21d, uses_per_month, turns_mean, turns_med))
        modeled_q_per_month += (g_hv / n_hv) * uses_per_month * turns_mean

    actual_q_per_month = (total_q / n_hv) * (MONTH_DAYS / WINDOW_DAYS)
    print()
    print("Kiểm chéo tổng câu/người/tháng: dữ liệu gốc = %.2f · tổng 3 persona (chưa làm tròn) = %.2f"
          % (actual_q_per_month, modeled_q_per_month))
    return 0


if __name__ == "__main__":
    sys.exit(main())
