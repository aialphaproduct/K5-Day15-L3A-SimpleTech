"""Benchmark ngữ cảnh video đang xem (Issue #37): so sánh `toan_kho`, `ca_ngay` và `hep`.

Chạy bằng 1 lệnh (0 token, chạy offline/CI):
  python eval/bench_video_context.py
"""
import csv
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "codebase"))

import tools  # noqa: E402

# 8 cặp cùng một câu hỏi đặt ở 2 video khác nhau (5 cặp cùng ngày + 3 cặp khác ngày)
SAME_QUESTION_PAIRS = [
    ("V01a", "cung_ngay", "Tại sao câu trả lời của LLM có thể sai sự thật?", "d01-r1-v02", "D01-02"),
    ("V01b", "cung_ngay", "Tại sao câu trả lời của LLM có thể sai sự thật?", "d01-r1-v03", "D01-05"),
    ("V02a", "cung_ngay", "Khi nào quá trình sinh token của LLM dừng lại?", "d01-r1-v01", "GIA-01"),
    ("V02b", "cung_ngay", "Khi nào quá trình sinh token của LLM dừng lại?", "d01-r1-v02", "D01-03"),
    ("V03a", "cung_ngay", "Số lượng token ảnh hưởng gì đến chi phí?", "d01-r1-v03", "D01-04"),
    ("V03b", "cung_ngay", "Số lượng token ảnh hưởng gì đến chi phí?", "d01-r1-v05", "D01-07"),
    ("V04a", "cung_ngay", "Làm sao tránh dữ liệu cũ làm sai câu trả lời của agent?", "d06-r1-v01", "D06-01"),
    ("V04b", "cung_ngay", "Làm sao tránh dữ liệu cũ làm sai câu trả lời của agent?", "d06-r1-v02", "D06-04"),
    ("V05a", "cung_ngay", "Agent gọi công cụ như thế nào?", "d03-r2-v01", "D03-01"),
    ("V05b", "cung_ngay", "Agent gọi công cụ như thế nào?", "d03-r2-v03", "D03-03"),
    ("V06a", "khac_ngay", "Khi nào nên dùng quy trình cố định thay vì agent?", "d02-r2-v01", "D02-02"),
    ("V06b", "khac_ngay", "Khi nào nên dùng quy trình cố định thay vì agent?", "d03-r2-v03", "D03-03"),
    ("V07a", "khac_ngay", "Khi nào cần bước người duyệt để kiểm soát rủi ro khi AI sai?", "d02-r2-v02", "D02-03"),
    ("V07b", "khac_ngay", "Khi nào cần bước người duyệt để kiểm soát rủi ro khi AI sai?", "d05-r2-v01", "D05-01"),
    ("V08a", "khac_ngay", "Trong quy trình gọi công cụ, mô hình và mã ứng dụng phối hợp ra sao?", "d01-r1-v05", "D01-08"),
    ("V08b", "khac_ngay", "Trong quy trình gọi công cụ, mô hình và mã ứng dụng phối hợp ra sao?", "d04-r3-v02", "D04-02"),
]

# 4 ca mở rộng từ video hiện tại sang cả ngày học / quy tắc chung
FALLBACK_CASES = [
    ("FB1", "mo_rong_ngay", "Tham số temperature có đảm bảo câu trả lời đúng sự thật không?", "d01-r1-v01", "D01-02"),
    ("FB2", "mo_rong_ngay", "Yêu cầu sản phẩm AI cần chốt ngưỡng chấp nhận và fallback ra sao?", "d05-r2-v01", "D05-03"),
    ("FB3", "mo_rong_ngay", "Đường ống dữ liệu raw clean serve và lineage hoạt động thế nào?", "d06-r1-v01", "D06-03"),
    ("FB4", "mo_rong_chung", "Trợ giảng có được tự đoán hạn nộp bài không?", "d01-r1-v02", "GIA-04"),
]

# 3 ca ngoài bài vẫn phải trả rỗng kể cả khi có mã video
OOS_CASES = [
    ("OOS1", "ngoai_bai", "Thời tiết Hà Nội cuối tuần này có mưa không?", "d01-r1-v02", "NONE"),
    ("OOS2", "ngoai_bai", "Sao Thổ có bao nhiêu vệ tinh?", "d06-r1-v01", "NONE"),
    ("OOS3", "ngoai_bai", "Cho mình xin công thức nấu phở bò ngon", "d05-r2-v01", "NONE"),
]


def eval_scope(scope_name: str):
    t0 = time.perf_counter()

    def _run(query, video):
        if scope_name == "toan_kho":
            return [p["code"] for p in tools.search_passages(query)]
        return [p["code"] for p in tools.search_passages(query, video=video, scope=scope_name)]

    same_day_ok = same_day_n = 0
    cross_day_ok = cross_day_n = 0
    pair_both_ok = 0
    fb_ok = 0
    oos_ok = 0
    missed = []

    pair_hits = {}
    for cid, group, query, video, exp in SAME_QUESTION_PAIRS:
        codes = _run(query, video)
        hit = bool(codes and codes[0] == exp)
        pair_key = cid[:-1]
        pair_hits.setdefault(pair_key, []).append(hit)
        if group == "cung_ngay":
            same_day_n += 1
            same_day_ok += int(hit)
        else:
            cross_day_n += 1
            cross_day_ok += int(hit)
        if not hit:
            missed.append((cid, video, exp, codes[:2]))

    for hits in pair_hits.values():
        if all(hits):
            pair_both_ok += 1

    for cid, _, query, video, exp in FALLBACK_CASES:
        codes = _run(query, video)
        if codes and codes[0] == exp:
            fb_ok += 1
        else:
            missed.append((cid, video, exp, codes[:2]))

    for cid, _, query, video, _ in OOS_CASES:
        codes = _run(query, video)
        if not codes:
            oos_ok += 1
        else:
            missed.append((cid, video, "NONE", codes[:2]))

    total_calls = len(SAME_QUESTION_PAIRS) + len(FALLBACK_CASES) + len(OOS_CASES)
    avg_ms = ((time.perf_counter() - t0) / total_calls) * 1000
    return {
        "scope": scope_name,
        "same_day": (same_day_ok, same_day_n),
        "cross_day": (cross_day_ok, cross_day_n),
        "pairs": (pair_both_ok, len(pair_hits)),
        "fallback": (fb_ok, len(FALLBACK_CASES)),
        "oos": (oos_ok, len(OOS_CASES)),
        "avg_ms": avg_ms,
        "missed": missed,
    }


def check_benchmark_thuong():
    expected_codes = {
        "B01": "GIA-01",
        "B02": "GIA-04",
        "B03": "GIA-03",
        "B04": "GIA-05",
        "B05": "GIA-02",
        "B06": "GIA-04",
        "B17": "GIA-05",
        "B18": "GIA-01",
        "B19": "GIA-02",
    }
    bm_path = os.path.join(ROOT, "eval", "benchmark.csv")
    top1_ok = top3_ok = 0
    failed = []
    with open(bm_path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r["id"] in expected_codes:
                codes = [p["code"] for p in tools.search_passages(r["input"])]
                exp = expected_codes[r["id"]]
                if codes and codes[0] == exp:
                    top1_ok += 1
                if exp in codes[:3]:
                    top3_ok += 1
                else:
                    failed.append((r["id"], exp, codes))
    return top1_ok, top3_ok, len(expected_codes), failed


def main():
    docs = tools._load()
    print("Kho đoạn bài: %d đoạn, %d video bài giảng." % (len(docs), len(tools.list_videos())))
    print("\n| Chế độ tìm | Cùng ngày khác video (Top-1) | Khác ngày (Top-1) | Đạt trọn cặp (2/2 video) | Mở rộng khi video chưa đủ | Lọc ngoài bài | Độ trễ TB |")
    print("|---|---|---|---|---|---|---|")
    for scope in ("toan_kho", "ca_ngay", "hep"):
        r = eval_scope(scope)
        print(
            "| `%s` | %d/%d (%.0f%%) | %d/%d (%.0f%%) | %d/%d (%.0f%%) | %d/%d (%.0f%%) | %d/%d (%.0f%%) | %.1f ms |"
            % (
                r["scope"],
                r["same_day"][0], r["same_day"][1], 100 * r["same_day"][0] / r["same_day"][1],
                r["cross_day"][0], r["cross_day"][1], 100 * r["cross_day"][0] / r["cross_day"][1],
                r["pairs"][0], r["pairs"][1], 100 * r["pairs"][0] / r["pairs"][1],
                r["fallback"][0], r["fallback"][1], 100 * r["fallback"][0] / r["fallback"][1],
                r["oos"][0], r["oos"][1], 100 * r["oos"][0] / r["oos"][1],
                r["avg_ms"],
            )
        )
        if r["missed"]:
            print("  Trượt [%s]: %s" % (r["scope"], r["missed"]))

    top1_ok, top3_ok, total, failed = check_benchmark_thuong()
    print(
        "\nKiểm không hồi quy eval/benchmark.csv (9 câu thuong, video=''): %d/%d Top-1, %d/%d Recall@3 khớp mã chuẩn."
        % (top1_ok, total, top3_ok, total)
    )
    if failed:
        print("  Hồi quy Recall@3:", failed)
        sys.exit(1)


if __name__ == "__main__":
    main()
