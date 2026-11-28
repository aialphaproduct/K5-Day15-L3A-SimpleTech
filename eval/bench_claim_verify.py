"""Benchmark kiểm chứng nội dung câu trả lời theo đoạn trích (Issue #34).

So sánh 2 cách trên 20 ví dụ (eval/claim_verify_cases.csv: 10 đúng + 10 'mã đúng, ý sai'):
  1. cheap_rule : luật bằng code (kiểm số/ngày/giờ/tên học viên chưa có trong đoạn trích) — 0 token
  2. llm_verify : gọi thêm 1 lượt model chấm SUPPORTED / UNSUPPORTED

Chạy bằng 1 lệnh:
  python eval/bench_claim_verify.py           # chạy đủ cả 2 cách (cần .env cho llm_verify)
  python eval/bench_claim_verify.py --no-llm  # chỉ chạy cheap_rule (0 token)
"""
import argparse
import csv
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "codebase"))

import agent  # noqa: E402
import tools  # noqa: E402

CASES_PATH = os.path.join(ROOT, "eval", "claim_verify_cases.csv")
CITE_RE = agent.CITE
verify_claim_rule = agent.verify_claim_rule


def verify_claim_llm(question: str, answer_text: str, passage_texts: list):
    """Một lượt model chấm SUPPORTED / UNSUPPORTED (trả is_ok, reason, tokens_in, tokens_out)."""
    import ai

    ans_clean = CITE_RE.sub("", answer_text).strip()
    sys_p = (
        "Bạn là bộ kiểm tra đối chiếu nội dung. Hãy đọc ĐOẠN TRÍCH và CÂU TRẢ LỜI.\n"
        "Trả đúng 1 từ:\n"
        "- SUPPORTED: nếu các ý trong CÂU TRẢ LỜI đúng với ĐOẠN TRÍCH (được phép diễn đạt gọn/tương đương nghĩa).\n"
        "- UNSUPPORTED: nếu CÂU TRẢ LỜI bịa số liệu, ngày giờ, tên người, đảo ngược nghĩa hoặc thêm ý không có trong ĐOẠN TRÍCH."
    )
    user_p = "ĐOẠN TRÍCH:\n%s\n\nCÂU HỎI:\n%s\n\nCÂU TRẢ LỜI:\n%s" % (
        "\n".join(passage_texts),
        question,
        ans_clean,
    )
    r = ai.call_model(sys_p, user_p)
    raw = r["text"].strip().upper()
    is_ok = "SUPPORTED" in raw and "UNSUPPORTED" not in raw
    return is_ok, raw[:40], int(r["tokens_in"]), int(r["tokens_out"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-llm", action="store_true", help="Chỉ chạy luật rẻ (0 token)")
    ap.add_argument("--wait", type=float, default=4.5, help="Giây nghỉ giữa các lượt gọi model (tránh HTTP 429)")
    args = ap.parse_args()

    by_code = {p["code"]: p["text"] for p in tools._load()}
    with open(CASES_PATH, encoding="utf-8-sig", newline="") as f:
        cases = list(csv.DictReader(f))

    def run_method(name, fn, is_llm=False):
        tp = fp = tn = fn_cnt = 0
        tin_sum = tout_sum = 0
        lat_sum = 0.0
        details = []
        for idx, c in enumerate(cases):
            ptext = [by_code[c["passage_code"]]]
            t_call = time.perf_counter()
            if is_llm:
                is_ok, reason, tin, tout = fn(c["question"], c["answer"], ptext)
                lat_sum += time.perf_counter() - t_call
                tin_sum += tin
                tout_sum += tout
                if args.wait > 0 and idx + 1 < len(cases):
                    time.sleep(args.wait)
            else:
                is_ok, reason = fn(c["answer"], ptext)
                lat_sum += time.perf_counter() - t_call
            is_unsup = c["label"] == "unsupported"
            blocked = not is_ok
            if is_unsup and blocked:
                tp += 1
            elif is_unsup and not blocked:
                fn_cnt += 1
                details.append((c["id"], "BO_SOT", c["error_type"], reason))
            elif not is_unsup and blocked:
                fp += 1
                details.append((c["id"], "CHAN_NHAM", c["error_type"], reason))
            else:
                tn += 1
        return {
            "name": name,
            "tp": tp,
            "n_unsup": tp + fn_cnt,
            "fp": fp,
            "n_sup": tn + fp,
            "avg_ms": (lat_sum / len(cases)) * 1000,
            "avg_tin": tin_sum / len(cases),
            "avg_tout": tout_sum / len(cases),
            "details": details,
        }

    results = [run_method("cheap_rule (luật code)", verify_claim_rule, is_llm=False)]
    if not args.no_llm:
        import ai

        if ai.MODEL_PROVIDER != "fake":
            results.append(run_method("llm_verify (%s)" % ai.MODEL_NAME, verify_claim_llm, is_llm=True))
        else:
            print("(Bỏ qua llm_verify vì MODEL_PROVIDER=fake)")

    print("\n| Cách kiểm chứng | Bắt đúng câu sai | Chặn nhầm câu đúng | Độ trễ TB | Token TB thêm (vào/ra) |")
    print("|---|---|---|---|---|")
    for res in results:
        print(
            "| %s | %d/%d (%.0f%%) | %d/%d (%.0f%%) | %.1f ms | %.0f / %.0f |"
            % (
                res["name"],
                res["tp"], res["n_unsup"], 100 * res["tp"] / res["n_unsup"],
                res["fp"], res["n_sup"], 100 * res["fp"] / res["n_sup"],
                res["avg_ms"],
                res["avg_tin"], res["avg_tout"],
            )
        )
    for res in results:
        if res["details"]:
            print("  Chi tiết lệch [%s]: %s" % (res["name"], res["details"]))


if __name__ == "__main__":
    main()
