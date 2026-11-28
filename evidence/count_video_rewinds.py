"""Phân tích đoạn video bị tua/xem lại, đối chiếu chat_sent và làm rõ quiz_item_opened/dismissed (Issue #41).

Chạy:
    python evidence/count_video_rewinds.py "<đường dẫn tới data/preclass>"

Chỉ in số đã tổng hợp (x/N, y%), không in mã học viên hay nội dung cá nhân.
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict

TARGET_VIDEOS = ("d01-r1-v02", "d01-r1-v01", "d01-r1-v05")
BIN_SECONDS = 30


def norm_video(v: str) -> str:
    v = (v or "").strip()
    if not v:
        return ""
    return os.path.splitext(os.path.basename(v))[0]


def fmt_bin(b: int) -> str:
    s0, s1 = b * BIN_SECONDS, (b + 1) * BIN_SECONDS
    return "%d:%02d–%d:%02d (%d–%ds)" % (s0 // 60, s0 % 60, s1 // 60, s1 % 60, s0, s1)


def main() -> int:
    folder = sys.argv[1] if len(sys.argv) > 1 else os.path.join("data", "preclass")
    ev_path = os.path.join(folder, "events.csv")
    chat_path = os.path.join(folder, "chat.csv")

    for p in (ev_path, chat_path):
        if not os.path.exists(p):
            sys.exit("Không tìm thấy %s. Truyền đường dẫn tới thư mục data/preclass của BTC." % p)

    chat_vid = {}
    with open(chat_path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            chat_vid[r["id"]] = norm_video(r.get("transcript", ""))

    opened_hvs = defaultdict(set)
    durations = defaultdict(list)
    rewind_bins = defaultdict(lambda: defaultdict(lambda: [0, set()]))  # vid -> bin -> [count, hvs]
    rewind_total = defaultdict(lambda: [0, set()])
    forward_total = Counter()
    seg_bins = defaultdict(lambda: defaultdict(lambda: [0, set()]))     # vid -> bin -> [views, hvs]
    chat_bins = defaultdict(lambda: defaultdict(lambda: [0, set()]))    # vid -> bin -> [count, hvs]
    chat_total = defaultdict(lambda: [0, set()])

    quiz_opened = 0
    quiz_dismissed = 0
    quiz_skipped = Counter()
    answer_video_quiz = 0

    with open(ev_path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            t = r.get("type")
            d = json.loads(r["data"]) if r.get("data") else {}

            if t == "quiz_item_opened":
                quiz_opened += 1
            elif t == "quiz_item_dismissed":
                quiz_dismissed += 1
                quiz_skipped[str(d.get("skipped_stop"))] += 1
            elif t == "answer_submitted" and d.get("nguon") == "video_quiz":
                answer_video_quiz += 1

            if r.get("actor") != "learner":
                continue

            hv = (r.get("hv") or "").strip()
            vid = norm_video(r.get("video", ""))
            if t == "chat_sent" and not vid:
                vid = chat_vid.get(r.get("ref_id", ""), "")
            if vid not in TARGET_VIDEOS:
                continue

            if t == "video_opened":
                opened_hvs[vid].add(hv)
            elif t == "video_ended" and d.get("duration") is not None:
                durations[vid].append(float(d["duration"]))
            elif t == "video_seeked":
                frm, to = d.get("from"), d.get("to")
                if frm is not None and to is not None:
                    f0, f1 = float(frm), float(to)
                    if f1 < f0:
                        b = int(max(0.0, f1) // BIN_SECONDS)
                        rewind_bins[vid][b][0] += 1
                        rewind_bins[vid][b][1].add(hv)
                        rewind_total[vid][0] += 1
                        rewind_total[vid][1].add(hv)
                    elif f1 > f0:
                        forward_total[vid] += 1
            elif t == "video_segments_flushed":
                if d.get("duration") is not None:
                    durations[vid].append(float(d["duration"]))
                for seg in (d.get("segments") or []):
                    if isinstance(seg, list) and len(seg) == 2:
                        s0, s1 = float(seg[0]), float(seg[1])
                        if s1 >= s0 >= 0:
                            for b in range(int(s0 // BIN_SECONDS), int(s1 // BIN_SECONDS) + 1):
                                seg_bins[vid][b][0] += 1
                                seg_bins[vid][b][1].add(hv)
            elif t == "chat_sent":
                vs = d.get("video_seconds")
                if vs is not None and float(vs) >= 0:
                    b = int(float(vs) // BIN_SECONDS)
                    chat_bins[vid][b][0] += 1
                    chat_bins[vid][b][1].add(hv)
                    chat_total[vid][0] += 1
                    chat_total[vid][1].add(hv)

    print("=== 1. TUA LÙI & CÂU HỎI THEO KHUNG %ds TRÊN 3 VIDEO TOP DAY01 ===" % BIN_SECONDS)
    for vid in TARGET_VIDEOS:
        dur = sorted(durations[vid])[len(durations[vid]) // 2] if durations[vid] else 0.0
        n_open = len(opened_hvs[vid])
        rw_n, rw_hvs = rewind_total[vid][0], len(rewind_total[vid][1])
        ch_n, ch_hvs = chat_total[vid][0], len(chat_total[vid][1])
        print("\n--- %s (thời lượng ~%.0fs · %d hv mở · tua lùi: %d lượt / %d hv · tua tới: %d · chat có giây: %d / %d hv) ---"
              % (vid, dur, n_open, rw_n, rw_hvs, forward_total[vid], ch_n, ch_hvs))
        all_bins = sorted(set(rewind_bins[vid].keys()) | set(chat_bins[vid].keys()))
        for b in all_bins:
            sc, sh = rewind_bins[vid][b][0], len(rewind_bins[vid][b][1])
            cc, ch = chat_bins[vid][b][0], len(chat_bins[vid][b][1])
            vc, vh = seg_bins[vid][b][0], len(seg_bins[vid][b][1])
            ratio = (vc / vh) if vh else 0.0
            print("  %-22s | tua lùi: %2d (%2d hv) | chat: %2d (%2d hv) | mật độ xem: %3d/%3d hv (%.2fx)"
                  % (fmt_bin(b), sc, sh, cc, ch, vc, vh, ratio))

    print("\n=== 2. LÀM RÕ quiz_item_opened / quiz_item_dismissed ===")
    skip_true = quiz_skipped["True"]
    skip_false = quiz_skipped["False"]
    print("quiz_item_opened: %d · quiz_item_dismissed: %d" % (quiz_opened, quiz_dismissed))
    print("  - skipped_stop=True (bỏ qua điểm dừng):  %d/%d (%.1f%%)"
          % (skip_true, quiz_dismissed, skip_true / quiz_dismissed * 100 if quiz_dismissed else 0))
    print("  - skipped_stop=False (đóng sau khi xem/tương tác): %d/%d (%.1f%%)"
          % (skip_false, quiz_dismissed, skip_false / quiz_dismissed * 100 if quiz_dismissed else 0))
    print("  - answer_submitted (nguon=video_quiz): %d dòng" % answer_video_quiz)
    return 0


if __name__ == "__main__":
    sys.exit(main())
