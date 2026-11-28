"""Đếm bằng chứng A1 bằng thư viện chuẩn; không in nội dung hay mã học viên.

Chạy: python evidence/count_tutor.py "<thư mục data/preclass của BTC>"
"""
import csv
import re
import statistics
import sys
from collections import Counter
from pathlib import Path


def summarize(rows):
    questions = [r for r in rows if r.get("agent_id") == "teaching_assistant"
                 and r.get("kind") == "question"]
    if not questions:
        raise ValueError("Không có câu hỏi trợ giảng trong tập đã lọc.")
    people = Counter(r["hv"] for r in questions)
    transcripts = Counter(r["transcript"] for r in questions if r.get("transcript"))
    days = Counter()
    for r in questions:
        match = re.search(r"(Day\d+)", r.get("transcript", ""))
        if match:
            days[match.group(1)] += 1
    top_n = max(1, round(len(people) * .10))
    lengths = {}
    for field in ("do_dai_cau_hoi", "do_dai_tra_loi"):
        numbers = [float(r[field]) for r in questions if r.get(field, "").strip()]
        lengths[field] = statistics.median(numbers) if numbers else None
    return {
        "questions": len(questions), "people": len(people),
        "one_question": sum(n == 1 for n in people.values()),
        "median": statistics.median(people.values()),
        "mean": statistics.mean(people.values()), "max": max(people.values()),
        "top_share": sum(n for _, n in people.most_common(top_n)) / len(questions),
        "days": days, "transcripts": transcripts,
        "cached": sum(r.get("cached") == "True" for r in questions),
        "context": sum(bool(r.get("ngu_canh", "").strip()) for r in questions),
        "guidance": sum(bool(r.get("guidance_ids", "").strip())
                        and r["guidance_ids"].strip() != "[]" for r in questions),
        "lengths": lengths,
    }


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    folder = Path(args[0]) if args else Path("data/preclass")
    with (folder / "chat.csv").open(encoding="utf-8-sig", newline="") as f:
        s = summarize(list(csv.DictReader(f)))
    n, people = s["questions"], s["people"]
    print("1. Tổng câu hỏi trợ giảng AI (kind=question, agent=teaching_assistant):", n)
    print("2. Học viên có ≥1 câu hỏi:", people)
    print("3. Học viên chỉ hỏi đúng 1 câu:", s["one_question"], f"({s['one_question']/people*100:.1f}%)")
    print("4. Median câu / học viên:", s["median"], "· trung bình:", round(s["mean"], 1), "· max:", s["max"])
    print("5. Top 10% học viên hỏi nhiều nhất chiếm:", f"{s['top_share']*100:.1f}% câu hỏi")
    print("6. Câu hỏi theo ngày học (day → số câu):")
    for day, count in sorted(s["days"].items()):
        print(day, count)
    print("7. 10 video có nhiều câu hỏi nhất (transcript → số câu):")
    for transcript, count in s["transcripts"].most_common(10):
        print(transcript, count)
    print("8. Trả lời dùng lại từ câu cũ (cached=True):", f"{s['cached']/n*100:.1f}%")
    print("9. Dòng ghi rõ đoạn bài AI dựa vào (ngu_canh không trống):", s["context"], "/", n)
    print("10. Dòng có dùng gợi ý đã duyệt (guidance_ids khác []):", f"{s['guidance']/n*100:.1f}%")
    print("11. Độ dài câu hỏi median (ký tự):", s["lengths"]["do_dai_cau_hoi"],
          "· độ dài trả lời median:", s["lengths"]["do_dai_tra_loi"])
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    raise SystemExit(main())
