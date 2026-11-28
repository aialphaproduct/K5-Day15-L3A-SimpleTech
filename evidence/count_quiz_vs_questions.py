"""Phân tích bài ôn (pre_post_post) x câu hỏi trợ giảng (chat.csv) theo Day, lesson_id và kc_code (Issue #39).

Chạy:
    python evidence/count_quiz_vs_questions.py "<đường dẫn tới data/preclass>"

Quy ước đo:
  - Bài ôn (answers.csv): lọc nguon == "pre_post_post", lan_thu == 1, was_correct thuộc {True, False}.
    Tính tỷ lệ sai (was_correct == False) theo lesson_id và theo kc_code; bỏ nhóm có n < 20 lượt.
  - Câu hỏi trợ giảng (chat.csv): dùng đúng bộ lọc của evidence/count_tutor.py (#5):
    agent_id == "teaching_assistant", kind == "question"; lấy Day từ cột transcript (khớp #5).
  - Số học viên có hoạt động theo Day (events.csv): đếm số hv duy nhất có actor == "learner"
    và gắn với DayNN (từ lesson_id hoặc video). Tính số câu hỏi / học viên hoạt động mỗi Day.

Chỉ in số đã tổng hợp, không in mã học viên hay nội dung cá nhân.
"""
import csv
import os
import re
import sys
from collections import defaultdict

MIN_N = 20


def extract_day(s: str):
    m = re.search(r"day(\d+)|^d(\d+)-", s or "", re.I)
    if not m:
        return None
    return "Day%02d" % int(m.group(1) or m.group(2))


def main() -> int:
    folder = sys.argv[1] if len(sys.argv) > 1 else os.path.join("data", "preclass")
    ans_path = os.path.join(folder, "answers.csv")
    chat_path = os.path.join(folder, "chat.csv")
    ev_path = os.path.join(folder, "events.csv")

    for p in (ans_path, chat_path):
        if not os.path.exists(p):
            sys.exit("Không tìm thấy %s. Truyền đường dẫn tới thư mục data/preclass của BTC." % p)

    # 1. answers.csv: pre_post_post, lan_thu == 1
    by_lesson = defaultdict(lambda: [0, 0, set()])  # [wrong, total, hvs]
    by_kc = defaultdict(lambda: [0, 0, set()])      # (lesson_id, kc_code) -> [wrong, total, hvs]
    by_day_quiz = defaultdict(lambda: [0, 0, set()])
    total_ppp = 0
    total_ppp1 = 0

    with open(ans_path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r.get("nguon") != "pre_post_post":
                continue
            total_ppp += 1
            if str(r.get("lan_thu", "")).strip() != "1":
                continue
            wc = str(r.get("was_correct", "")).strip()
            if wc not in ("True", "False"):
                continue
            total_ppp1 += 1
            wrong = 1 if wc == "False" else 0
            lid = (r.get("lesson_id") or "").strip()
            kc = (r.get("kc_code") or "").strip()
            hv = (r.get("hv") or "").strip()
            day = extract_day(lid) or "Unknown"

            by_lesson[lid][0] += wrong
            by_lesson[lid][1] += 1
            by_lesson[lid][2].add(hv)

            by_kc[(lid, kc)][0] += wrong
            by_kc[(lid, kc)][1] += 1
            by_kc[(lid, kc)][2].add(hv)

            by_day_quiz[day][0] += wrong
            by_day_quiz[day][1] += 1
            by_day_quiz[day][2].add(hv)

    # 2. chat.csv: khớp bộ lọc count_tutor.py (#5)
    chat_by_day = defaultdict(int)
    chat_hvs_by_day = defaultdict(set)
    chat_no_transcript = 0
    total_chat = 0
    with open(chat_path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r.get("agent_id") == "teaching_assistant" and r.get("kind") == "question":
                total_chat += 1
                day = extract_day(r.get("transcript"))
                if not day:
                    chat_no_transcript += 1
                    continue
                chat_by_day[day] += 1
                chat_hvs_by_day[day].add((r.get("hv") or "").strip())

    # 3. events.csv: học viên có hoạt động theo Day (actor == learner)
    active_by_day = defaultdict(set)
    total_active_learners = set()
    has_events = os.path.exists(ev_path)
    if has_events:
        with open(ev_path, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                if r.get("actor") != "learner":
                    continue
                hv = (r.get("hv") or "").strip()
                if not hv:
                    continue
                total_active_learners.add(hv)
                day = extract_day(r.get("lesson_id")) or extract_day(r.get("video"))
                if day:
                    active_by_day[day].add(hv)

    # In báo cáo tổng hợp
    total_wrong = sum(v[0] for v in by_lesson.values())
    print("=== TỔNG QUAN BỘ LỌC (Issue #39) ===")
    print("answers.csv (pre_post_post): %d dòng · lan_thu=1 có đúng/sai: %d dòng (sai %d/%d = %.1f%%)"
          % (total_ppp, total_ppp1, total_wrong, total_ppp1, total_wrong / total_ppp1 * 100 if total_ppp1 else 0))
    print("chat.csv (teaching_assistant + question): %d câu (gắn Day qua transcript: %d, thiếu transcript: %d)"
          % (total_chat, total_chat - chat_no_transcript, chat_no_transcript))
    if has_events:
        print("events.csv (actor=learner): %d học viên có hoạt động toàn khoá" % len(total_active_learners))
    else:
        print("Lưu ý: không tìm thấy events.csv trong %s — bỏ qua cột học viên hoạt động." % folder)

    print("\n=== 1. TỶ LỆ SAI THEO LESSON_ID (n >= %d) ===" % MIN_N)
    kept_lessons = [(lid, v) for lid, v in by_lesson.items() if v[1] >= MIN_N]
    dropped_lessons = [(lid, v) for lid, v in by_lesson.items() if v[1] < MIN_N]
    kept_lessons.sort(key=lambda x: (-(x[1][0] / x[1][1]), -x[1][1]))
    for lid, (w, n, hvs) in kept_lessons:
        print("  %-46s | sai %3d/%3d (%5.1f%%) | %2d học viên" % (lid, w, n, w / n * 100, len(hvs)))
    if dropped_lessons:
        print("  (Đã bỏ %d lesson có n < %d: %s)" % (
            len(dropped_lessons), MIN_N,
            ", ".join("%s (%d/%d)" % (lid, w, n) for lid, (w, n, _) in dropped_lessons),
        ))

    print("\n=== 2. ĐỐI CHIẾU THEO DAY: BÀI ÔN x CÂU HỎI / HỌC VIÊN HOẠT ĐỘNG ===")
    all_days = sorted(set(list(by_day_quiz.keys()) + list(chat_by_day.keys()) + list(active_by_day.keys())))
    for d in all_days:
        w, n, qhvs = by_day_quiz[d]
        cq = chat_by_day[d]
        ch = len(chat_hvs_by_day[d])
        ah = len(active_by_day[d]) if has_events else 0
        err_s = "%d/%d (%.1f%%)" % (w, n, w / n * 100) if n >= MIN_N else ("bỏ (<20: %d/%d)" % (w, n) if n else "—")
        q_per_hv = "%.2f" % (cq / ah) if ah else "—"
        ask_rate = "%d/%d (%.1f%%)" % (ch, ah, ch / ah * 100) if ah else "—"
        print("  %s | sai bài ôn: %-18s (hv ôn: %2d) | câu hỏi: %3d | hv hoạt động: %3d | câu/hv: %-5s | hv hỏi: %s"
              % (d, err_s, len(qhvs), cq, ah, q_per_hv, ask_rate))

    print("\n=== 3. TỶ LỆ SAI THEO KC_CODE (n >= %d, xếp giảm dần) ===" % MIN_N)
    kept_kcs = [(k, v) for k, v in by_kc.items() if v[1] >= MIN_N]
    kept_kcs.sort(key=lambda x: (-(x[1][0] / x[1][1]), -x[1][0], x[0][1]))
    print("Tổng số nhóm (lesson_id, kc_code): %d · Đủ n >= %d: %d · Bị bỏ (<%d): %d"
          % (len(by_kc), MIN_N, len(kept_kcs), MIN_N, len(by_kc) - len(kept_kcs)))
    for idx, ((lid, kc), (w, n, hvs)) in enumerate(kept_kcs, start=1):
        print("  %2d. %-5s | %-42s | sai %2d/%2d (%5.1f%%) | %2d hv"
              % (idx, extract_day(lid) or "?", kc, w, n, w / n * 100, len(hvs)))

    return 0


if __name__ == "__main__":
    sys.exit(main())
