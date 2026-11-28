"""Recalculate saved cost evidence with task = one question, without API calls.

python cost/audit.py --output cost/task-cost-audit.md
The default inputs describe simulation 1 / eval 2, not the current product.
"""
import argparse
import csv
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "eval"))
from run_eval import load_yaml  # noqa: E402


def number(value, name, positive=False):
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise ValueError("%s must be numeric" % name) from None
    if isinstance(value, bool) or not math.isfinite(result) or result < 0 or (positive and result == 0):
        raise ValueError("%s must be finite and %s" % (name, "positive" if positive else "nonnegative"))
    return result


def integer(value, name, positive=False):
    result = number(value, name, positive)
    if not result.is_integer():
        raise ValueError("%s must be an integer" % name)
    return int(result)


def unique_rows(rows, key):
    if not rows:
        raise ValueError("empty %s evidence" % key)
    seen = set()
    for row in rows:
        identity = row.get(key, "").strip()
        if not identity or identity in seen:
            raise ValueError("missing or duplicate %s: %s" % (key, identity))
        seen.add(identity)
    run_ids = {r.get("run_id", "").strip() for r in rows}
    if len(run_ids) != 1 or not next(iter(run_ids)):
        raise ValueError("missing or mixed run IDs")


def real_model(value):
    value = value.strip()
    if not value or value.lower() in {"fake", "mock", "none"} or "," in value:
        raise ValueError("requires one measured real model, got %r" % value)
    return value


def analyze(sessions, evaluation, cfg, types=("thuong", "kho"), benchmark=None):
    """Conditional token-cost estimate. Does not grade simulated outputs."""
    unique_rows(sessions, "session")
    unique_rows(evaluation, "id")
    if benchmark is not None:
        questions = {q["id"]: q for q in benchmark}
        if not questions or len(questions) != len(benchmark):
            raise ValueError("empty or duplicate benchmark IDs")
        if {r["id"] for r in evaluation} != set(questions):
            raise ValueError("evaluation IDs differ from complete benchmark")
        if any(r["type"] != questions[r["id"]]["type"] for r in evaluation):
            raise ValueError("evaluation type differs from benchmark")
    types = set(types)
    if not types or not types <= {"thuong", "kho", "tu_choi"}:
        raise ValueError("unsupported evaluation population")
    for row in sessions:
        real_model(row.get("model", ""))
        integer(row["turns"], "turns", positive=True)
        integer(row["tokens_in"], "tokens_in")
        integer(row["tokens_out"], "tokens_out")
    models = {real_model(row.get("model", "")) for row in sessions}
    if len(models) != 1:
        raise ValueError("simulation mixes models")
    model = next(iter(models))
    valid = [r for r in sessions if not r.get("error", "").strip()]
    failed = [r for r in sessions if r.get("error", "").strip()]
    if not valid:
        raise ValueError("no valid simulation sessions")
    graded = [r for r in evaluation if r.get("type") in types]
    if not graded:
        raise ValueError("no evaluation questions in simulation population")
    for row in evaluation:
        if row.get("type") not in {"thuong", "kho", "tu_choi"}:
            raise ValueError("unknown evaluation type")
        if row.get("pass", "").strip() not in {"0", "1"}:
            raise ValueError("evaluation must be completely graded")
        if real_model(row.get("model", "")) != model:
            raise ValueError("evaluation model differs from simulation")
        if row.get("error", "").strip() and row["pass"].strip() == "1":
            raise ValueError("technical error cannot be a successful question")
    passed = sum(r["pass"].strip() == "1" for r in graded)
    rate = passed / len(graded)
    turns = sum(int(r["turns"]) for r in valid)
    total_in = sum(int(r["tokens_in"]) for r in valid)
    total_out = sum(int(r["tokens_out"]) for r in valid)
    personas = cfg["personas"]
    names = [p["name"] for p in personas]
    if not names or len(set(names)) != len(names):
        raise ValueError("missing or duplicate personas")
    if any(r["persona"] not in names for r in sessions):
        raise ValueError("unknown simulation persona")
    weights = {p["name"]: number(p["share"], "share") for p in personas}
    weight_sum = sum(weights.values())
    if weight_sum <= 0:
        raise ValueError("persona shares sum to zero")
    for p in personas:
        number(p["uses_per_month"], "uses_per_month")
        if weights[p["name"]] > 0 and not any(r["persona"] == p["name"] for r in valid):
            raise ValueError("no valid sample for persona %s" % p["name"])
    users = {k: integer(cfg["users"][k], "users.%s" % k) for k in ("low", "base", "high")}
    prices = cfg["prices"]
    price_names = [p["model"] for p in prices]
    if not prices or len(set(price_names)) != len(price_names) or model not in price_names:
        raise ValueError("prices require unique models including measured model")
    results = []
    for price in prices:
        pi = number(price["input"], "input price") / 1_000_000
        po = number(price["output"], "output price") / 1_000_000
        cost = total_in * pi + total_out * po
        monthly_per_user = 0
        for persona in personas:
            samples = [r for r in valid if r["persona"] == persona["name"]]
            if not samples:
                continue
            mean = sum(int(r["tokens_in"]) * pi + int(r["tokens_out"]) * po for r in samples) / len(samples)
            monthly_per_user += weights[persona["name"]] / weight_sum * float(persona["uses_per_month"]) * mean
        measured = price["model"] == model
        results.append({"model": price["model"], "measured": measured,
                        "usd_per_question": cost / turns,
                        "usd_per_successful_question": cost / turns / rate if measured and rate else None,
                        "monthly": {k: n * monthly_per_user for k, n in users.items()},
                        "monthly_per_user": monthly_per_user})
    return {"model": model, "simulation_run": sessions[0]["run_id"], "eval_run": evaluation[0]["run_id"],
            "attempted_sessions": len(sessions), "valid_sessions": len(valid), "failed_sessions": len(failed),
            "valid_turns": turns, "tokens_in": total_in, "tokens_out": total_out,
            "failed_tokens_in": sum(int(r["tokens_in"]) for r in failed),
            "failed_tokens_out": sum(int(r["tokens_out"]) for r in failed),
            "passed": passed, "graded": len(graded), "rate": rate, "types": sorted(types),
            "overall_passed": sum(r["pass"].strip() == "1" for r in evaluation),
            "overall_graded": len(evaluation), "users": users, "prices": results}


def read_rows(path, required):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not set(required) <= set(reader.fieldnames or ()):
            raise ValueError("%s: missing columns" % path)
        rows = list(reader)
    if any(None in r or any(v is None for v in r.values()) for r in rows):
        raise ValueError("%s: malformed CSV" % path)
    return rows


def report(result, simulation, evaluation):
    def usd(value):
        return "—" if value is None else "$%.8f" % value

    historical = (result["simulation_run"] == "simulate-1@20261128-012032"
                  and result["eval_run"] == "run-2@20261127-215239")
    provenance = ("Cấu hình lịch sử: lượt 2, kho 20 đoạn. Không đại diện tự động cho bản cuối 28 đoạn; cần mô phỏng lượt mới bằng AI thật sau khi có cấu hình."
                  if historical else "Chưa xác minh cấu hình prompt/kho đoạn của cặp lượt này có khớp nhau; cùng model không bảo đảm cùng chất lượng. Không suy cấu hình từ tên file hay dùng số này để cam kết chi phí bản hiện tại.")
    lines = ["# Kiểm toán chi phí — task là một câu hỏi", "",
             "Báo cáo sau CP4, tính lại artifact đã lưu, không gọi AI hoặc sửa kết quả lịch sử.", "",
             "- Mô phỏng: `%s` (`%s`)." % (simulation.name, result["simulation_run"]),
             "- Đánh giá: `%s` (`%s`), model `%s`." % (evaluation.name, result["eval_run"], result["model"]),
             "- %d phiên thử; %d hợp lệ; %d lỗi. Trên phiên hợp lệ: %d câu hỏi, %d token vào / %d token ra." % (
                 result["attempted_sessions"], result["valid_sessions"], result["failed_sessions"],
                 result["valid_turns"], result["tokens_in"], result["tokens_out"]),
             "- Tỷ lệ câu đạt dùng trong công thức: **%d/%d = %.2f%%**, chỉ nhóm `%s` mà mô phỏng sử dụng. Tỷ lệ toàn benchmark là %d/%d, có cả nhóm khác." % (
                 result["passed"], result["graded"], result["rate"] * 100, ", ".join(result["types"]),
                 result["overall_passed"], result["overall_graded"]), "",
             "## Công thức và đơn vị", "",
             "1 task = 1 câu hỏi. USD/câu = tổng chi phí token của phiên hợp lệ / tổng số lượt hỏi của các phiên đó. USD/câu đạt ước tính = USD/câu / tỷ lệ đạt eval cùng model và nhóm đầu vào. Không dùng chi phí một phiên nhiều câu để gọi là chi phí một câu thành công.", "",
             "Tỷ lệ eval là giả định chuyển sang mẫu mô phỏng, chưa phải tỷ lệ thành công quan sát trực tiếp trên các câu mô phỏng. Không suy ra tỷ lệ thành công trọn phiên hoặc đạt mọi metric CP2.", "",
             "Chi phí/tháng = số người × tổng theo persona (share chuẩn hoá × phiên/người/tháng × chi phí token TB/phiên hợp lệ của persona). Quy mô thấp/cơ sở/cao: %d / %d / %d người." % (
                 result["users"]["low"], result["users"]["base"], result["users"]["high"]), "",
             "| Model / cơ sở | USD/câu | USD/câu đạt ước tính | USD/tháng thấp | cơ sở | cao | USD/người/tháng |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for price in result["prices"]:
        label = "đã đo token, proxy tỷ lệ eval" if price["measured"] else "chỉ đổi đơn giá, chưa đo chất lượng"
        lines.append("| %s (%s) | %s | %s | %s | %s | %s | %s |" % (
            price["model"], label, usd(price["usd_per_question"]), usd(price["usd_per_successful_question"]),
            *(usd(price["monthly"][k]) for k in ("low", "base", "high")), usd(price["monthly_per_user"])))
    lines += ["", "## Giới hạn", "",
              "- Các phiên lỗi có log %d token vào / %d token ra, không nằm trong trung bình trên. Lỗi API không trả usage có thể còn chi phí chưa quan sát; không coi lỗi là miễn phí. Chưa tính retry, hosting và vận hành." % (
                  result["failed_tokens_in"], result["failed_tokens_out"]),
              "- " + provenance,
              "- Hai mức giá là ảnh chụp BTC ngày 25/11/2026 trong `cost/personas.yaml`, không phải xác minh giá hiện hành. Dòng model khác chỉ ngoại suy đơn giá; để trống USD/câu đạt vì chưa đo model đó.",
              "- `cost/simulate.py`, CSV, summary và trace gốc giữ nguyên. Báo cáo này sửa cách đọc đơn vị, không thay số liệu nộp CP4.", ""]
    return "\n".join(lines)


def write_report(path, text):
    path = Path(path)
    if path.suffix.lower() != ".md":
        raise ValueError("output must be a new .md file")
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--simulation", type=Path, default=ROOT / "cost/simulate-1.csv")
    parser.add_argument("--evaluation", type=Path, default=ROOT / "eval/run-2.csv")
    parser.add_argument("--config", type=Path, default=ROOT / "cost/personas.yaml")
    parser.add_argument("--benchmark", type=Path, default=ROOT / "eval/benchmark.csv")
    parser.add_argument("--types", nargs="+", default=["thuong", "kho"], help="must match simulation input pool")
    parser.add_argument("--output", type=Path, help="new Markdown file only")
    args = parser.parse_args(argv)
    try:
        sessions = read_rows(args.simulation, ("run_id", "session", "persona", "turns", "model", "tokens_in", "tokens_out", "error"))
        evaluation = read_rows(args.evaluation, ("run_id", "id", "type", "model", "pass", "error"))
        benchmark = read_rows(args.benchmark, ("id", "type"))
        result = analyze(sessions, evaluation, load_yaml(str(args.config)), args.types, benchmark)
        text = report(result, args.simulation, args.evaluation)
        if args.output:
            write_report(args.output, text)
        else:
            print(text)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("cost audit: %s" % error, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
