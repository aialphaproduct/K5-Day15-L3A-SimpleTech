"""So sánh hành vi hỏi thật (chat.csv + answers.csv) với bộ câu thử eval/benchmark.csv (Issue #42).

Chạy:
    python evidence/count_benchmark_gap.py "<đường dẫn tới data/preclass>"

Chỉ in số đã tổng hợp (x/N, y%), không in mã học viên hay dữ liệu cá nhân.
"""
import csv
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH = os.path.join(ROOT, "eval", "benchmark.csv")


def summarize_lengths(arr: list) -> dict:
    s = sorted(arr)
    n = len(s)
    return {
        "n": n,
        "min": s[0],
        "p25": s[n // 4],
        "median": s[n // 2],
        "p75": s[(3 * n) // 4],
        "p90": s[int(n * 0.90)],
        "max": s[-1],
        "mean": sum(s) / n,
        "le20": sum(1 for x in s if x <= 20),
        "le30": sum(1 for x in s if x <= 30),
        "ge120": sum(1 for x in s if x >= 120),
    }


def main() -> int:
    folder = sys.argv[1] if len(sys.argv) > 1 else os.path.join("data", "preclass")
    chat_path = os.path.join(folder, "chat.csv")
    ans_path = os.path.join(folder, "answers.csv")

    for p in (chat_path, ans_path, BENCH):
        if not os.path.exists(p):
            sys.exit("Không tìm thấy %s." % p)

    channels = Counter()
    kinds = Counter()
    all_lens = []
    ta_q_ids = set()
    ta_lens = []

    with open(chat_path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            channels[r.get("channel") or "(trống)"] += 1
            kinds[r.get("kind") or "(trống)"] += 1
            if (r.get("do_dai_cau_hoi") or "").strip():
                ln = int(r["do_dai_cau_hoi"])
                all_lens.append(ln)
                if r.get("agent_id") == "teaching_assistant" and r.get("kind") == "question":
                    ta_q_ids.add(r["id"])
                    ta_lens.append(ln)

    ans_status = Counter()
    bam_all = Counter()
    bam_ta = Counter()
    with open(ans_path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r.get("nguon") != "chat":
                continue
            st = (r.get("trang_thai_cham") or "").strip()
            ans_status[st] += 1
            if st != "da_cham":
                continue
            v = (r.get("rubric_bam_bai") or "").strip()
            if v != "":
                bam_all[v] += 1
                if r.get("ref") in ta_q_ids:
                    bam_ta[v] += 1

    bench_lens = []
    bench_types = Counter()
    with open(BENCH, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            inp = (r.get("input") or "").strip()
            if inp:
                bench_lens.append(len(inp))
                bench_types[(r.get("type") or "").strip()] += 1

    st_all = summarize_lengths(all_lens)
    st_ta = summarize_lengths(ta_lens)
    st_b = summarize_lengths(bench_lens)

    n_chat = sum(channels.values())
    print("=== 1. PHÂN BỐ KÊNH & LOẠI TIN (chat.csv, n=%d) ===" % n_chat)
    for k, v in channels.most_common():
        print("  channel %-24s: %4d/%d (%.1f%%)" % (k, v, n_chat, v / n_chat * 100))
    for k, v in kinds.most_common():
        print("  kind    %-24s: %4d/%d (%.1f%%)" % (k, v, n_chat, v / n_chat * 100))

    print("\n=== 2. ĐIỂM rubric_bam_bai (answers.csv, nguon=chat) ===")
    print("Trạng thái chấm:", dict(ans_status))
    n_bam_all = sum(bam_all.values())
    n_bam_ta = sum(bam_ta.values())
    print("Toàn bộ tin đã chấm (n=%d): " % n_bam_all +
          ", ".join("%s điểm: %d/%d (%.1f%%)" % (k, bam_all[k], n_bam_all, bam_all[k] / n_bam_all * 100) for k in ("0", "1", "2")))
    print("Riêng câu hỏi TA (n=%d):    " % n_bam_ta +
          ", ".join("%s điểm: %d/%d (%.1f%%)" % (k, bam_ta[k], n_bam_ta, bam_ta[k] / n_bam_ta * 100) for k in ("0", "1", "2")))

    print("\n=== 3. SO SÁNH ĐỘ DÀI & TỶ LỆ NGOÀI BÀI: HÀNH VI THẬT vs BENCHMARK ===")
    for label, st in (("Toàn bộ chat.csv", st_all), ("Câu hỏi TA (chat.csv)", st_ta), ("eval/benchmark.csv", st_b)):
        print("  %-24s | n=%4d | min=%2d p25=%2d med=%2d p75=%2d p90=%3d max=%4d mean=%5.1f | <=20: %d/%d (%.1f%%) | <=30: %d/%d (%.1f%%) | >=120: %d/%d (%.1f%%)"
              % (label, st["n"], st["min"], st["p25"], st["median"], st["p75"], st["p90"], st["max"], st["mean"],
                 st["le20"], st["n"], st["le20"] / st["n"] * 100,
                 st["le30"], st["n"], st["le30"] / st["n"] * 100,
                 st["ge120"], st["n"], st["ge120"] / st["n"] * 100))

    nb = sum(bench_types.values())
    out_of_scope = bench_types["kho"] + bench_types["tu_choi"]
    print("\nBenchmark theo type (n=%d): thuong=%d/%d (%.1f%%) · kho=%d/%d (%.1f%%) · tu_choi=%d/%d (%.1f%%) · kho+tu_choi=%d/%d (%.1f%%)"
          % (nb, bench_types["thuong"], nb, bench_types["thuong"] / nb * 100,
             bench_types["kho"], nb, bench_types["kho"] / nb * 100,
             bench_types["tu_choi"], nb, bench_types["tu_choi"] / nb * 100,
             out_of_scope, nb, out_of_scope / nb * 100))
    return 0


if __name__ == "__main__":
    sys.exit(main())
