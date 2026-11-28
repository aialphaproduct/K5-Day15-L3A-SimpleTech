"""Cổng kiểm sau mỗi lần đổi: code tự chấm phần kiểm được, so với lượt gốc, chặn khi tụt.

    python eval/gate.py eval/run-4.csv --base eval/run-3.csv
    python eval/gate.py --calibrate        # so điểm code chấm với điểm đã chấm tay

Không gọi model, không sửa file. Code chỉ kiểm các điều kiện cơ học, không chứng minh không bịa.
Tách tiêu chí từng câu khỏi điều kiện mã CP2; ý nghĩa và metric 20 câu vẫn cần người chấm.
Thoát mã 1 khi CHẶN, 0 khi QUA PHẦN CƠ HỌC (không phải chứng nhận đạt toàn bộ CP2).
"""
import argparse
import csv
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THRESHOLDS = {"thuong": 0.9, "kho": 0.8, "tu_choi": 1.0}  # spec.md §7
CODE = re.compile(r"\[([A-Za-z0-9\-]+)\]")
# Số/ngày/điểm cụ thể mà câu hỏi không hề nêu thì coi là bịa.
SPECIFIC = re.compile(r"\d{1,2}/\d{1,2}|\d+(?:[.,]\d+)?\s*(?:điểm|giờ|tiếng|ngày)|thứ (?:hai|ba|tư|năm|sáu|bảy)|chủ nhật", re.IGNORECASE)


def read_csv(path, required=()):
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(io.StringIO(f.read()), strict=True)
        fields = reader.fieldnames or []
        if len(set(fields)) != len(fields) or not set(required) <= set(fields):
            raise ValueError("%s: thiếu hoặc trùng cột bắt buộc" % path)
        rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError("%s: dòng CSV sai số cột" % path)
    return rows


def questions(*names):
    rows = {}
    for name in names or ("benchmark.csv", "benchmark_heldout.csv"):
        path = os.path.join(ROOT, "eval", name)
        if os.path.exists(path):
            for r in read_csv(path, ("id", "type", "input", "expected", "pass_criterion")):
                if not r["id"] or r["id"] in rows:
                    raise ValueError("benchmark thiếu hoặc trùng id: %s" % r["id"])
                rows[r["id"]] = r
    return rows


def passage_codes():
    return {r["code"] for r in read_csv(os.path.join(ROOT, "data", "lessons", "passages.csv"))}


def kind_of(question):
    """Loại phản hồi mà câu thử đòi hỏi, suy từ type và expected."""
    if question["type"] == "tu_choi":
        return "tu_choi"
    if CODE.search(question["expected"]):
        return "trich_ma"
    if re.search(r"gửi (?:lại|mình)", question["expected"], re.IGNORECASE):
        return "hoi_lai"
    return "khong_co_can_cu"


def check(question, output, known):
    """Danh sách lý do trượt; rỗng là đạt phần code kiểm được."""
    text = output.strip()
    low = text.lower()
    cited = set(CODE.findall(text))
    kind = kind_of(question)
    why = []
    if not text:
        return ["không có câu trả lời"]
    if cited - known:
        why.append("mã không có trong kho: %s" % ", ".join(sorted(cited - known)))
    if kind == "trich_ma":
        missing = set(CODE.findall(question["expected"])) - cited
        if missing:
            why.append("thiếu mã %s (đang trích %s)" % (", ".join(sorted(missing)), ", ".join(sorted(cited)) or "không mã nào"))
        return why
    invented = [m for m in SPECIFIC.findall(text) if m.lower() not in question["input"].lower()]
    if invented:
        why.append("nêu số/ngày không có trong câu hỏi: %s" % ", ".join(invented))
    if kind == "hoi_lai":
        if not re.search(r"gửi (?:lại|mình)", low):
            why.append("không đề nghị học viên gửi lại nội dung")
        if cited:
            why.append("tự gán mã đoạn khi chưa rõ câu hỏi")
    elif kind == "khong_co_can_cu":
        if not re.search(r"không có trong bài|\bta\b|trợ giảng|thông báo chính thức", low):
            why.append("không báo thiếu căn cứ, không chuyển TA")
    else:
        if not re.search(r"từ chối|không thể|không có trong bài", low):
            why.append("không từ chối")
        if "học lại" in question["pass_criterion"] and not re.search(r"\bôn\b|học lại|xem lại", low):
            why.append("không hướng học viên học lại")
    return why


def citation_condition(question, output, known):
    """Điều kiện cần của trich_dung_ma, kể cả câu thường expected yêu cầu từ chối."""
    cited = set(CODE.findall(output))
    required = set(CODE.findall(question["expected"] + " " + question["pass_criterion"]))
    return bool(cited) and cited <= known and required <= cited


def grade(run_path, rows=None, known=None):
    saved = read_csv(run_path, ("run_id", "id", "type", "output", "pass", "error"))
    if not saved:
        raise ValueError("lượt chạy rỗng")
    ids = [r["id"] for r in saved]
    if not all(ids) or len(set(ids)) != len(ids):
        raise ValueError("lượt chạy thiếu hoặc trùng id")
    run_ids = {r["run_id"].strip() for r in saved}
    if len(run_ids) != 1 or "" in run_ids:
        raise ValueError("run_id rỗng hoặc không nhất quán")
    if rows is None:
        # Chọn một bộ đầy đủ; không xem tập con, tập trộn hai bộ hay ID lạ là một lượt hợp lệ.
        choices = [questions(name) for name in ("benchmark.csv", "benchmark_heldout.csv")]
        matching = [q for q in choices if q and set(ids) <= set(q)]
        if len(matching) != 1:
            raise ValueError("ID lượt chạy không thuộc duy nhất một benchmark")
        rows = matching[0]
    if set(ids) != set(rows):
        raise ValueError("ID khác benchmark: thiếu=%s thừa=%s" % (sorted(set(rows) - set(ids)), sorted(set(ids) - set(rows))))
    known = passage_codes() if known is None else known
    result = {}
    for r in saved:
        q = rows[r["id"]]
        if q["type"] not in THRESHOLDS or r["type"] != q["type"]:
            raise ValueError("%s: type không khớp benchmark" % r["id"])
        manual = r["pass"].strip()
        if manual not in ("", "0", "1"):
            raise ValueError("%s: pass phải rỗng, 0 hoặc 1" % r["id"])
        error = bool(r["error"].strip())
        why = ["lỗi kỹ thuật: %s" % r["error"]] if error else check(q, r["output"], known)
        result[r["id"]] = {"type": q["type"], "ok": not why, "why": why, "output": r.get("output", ""),
                           "input": q["input"], "manual": manual, "error": error,
                           "citation_ok": not error and citation_condition(q, r["output"], known)}
    return result


def compare(candidate, base=None):
    """Kết luận cho một lượt: chuẩn từng nhóm, câu tụt, câu đổi nội dung cần người đọc."""
    groups = []
    for name, need in THRESHOLDS.items():
        items = [v for v in candidate.values() if v["type"] == name]
        if items:
            ok = sum(v["ok"] for v in items)
            groups.append({"type": name, "ok": ok, "total": len(items), "need": need, "met": ok / len(items) >= need})
    problems = []
    if not candidate:
        problems.append("lượt chạy rỗng")
    errored = [key for key, value in candidate.items() if value.get("error")]
    if errored:
        problems.append("có lỗi kỹ thuật: " + ", ".join(errored))
    if base is not None and set(candidate) != set(base):
        problems.append("lượt mới và lượt gốc khác tập ID; không được bỏ câu")
    if base is not None and any(candidate[i]["type"] != base[i]["type"] for i in set(candidate) & set(base)):
        problems.append("type thay đổi giữa lượt mới và lượt gốc")
    regular = [v for v in candidate.values() if v["type"] == "thuong"]
    # Live evaluations from improve.py have already passed check(); still require a citation
    # for every regular question, including expected no-basis answers such as B06.
    citation_ok = sum(v.get("citation_ok", bool(CODE.search(v["output"])) and v["ok"] and not v.get("error")) for v in regular)
    citation = {"ok": citation_ok, "total": len(regular), "met": bool(regular) and citation_ok / len(regular) >= THRESHOLDS["thuong"]}
    if regular and not citation["met"]:
        problems.append("điều kiện mã CP2 %d/%d dưới chuẩn 90%%" % (citation_ok, len(regular)))
        for group in groups:
            if group["type"] == "thuong":
                group["met"] = False
    base = base or {}
    regressed = [i for i, v in candidate.items() if i in base and base[i]["ok"] and not v["ok"]]
    fixed = [i for i, v in candidate.items() if i in base and not base[i]["ok"] and v["ok"]]
    review = [i for i, v in candidate.items()
              if v["ok"] and CODE.search(v["output"]) and (i not in base or base[i]["output"] != v["output"])]
    reasons = problems + ["kiểm cơ học từng câu nhóm %s %d/%d dưới chuẩn %d%%" % (g["type"], g["ok"], g["total"], g["need"] * 100) for g in groups if g["ok"] / g["total"] < g["need"]]
    reasons += ["%s tụt: %s" % (i, "; ".join(candidate[i]["why"])) for i in regressed]
    return {"verdict": "CHẶN" if reasons else "QUA", "reasons": reasons, "groups": groups, "regressed": regressed,
            "fixed": fixed, "review": review,
            "citation": citation, "cp2_verified": False,
            "ungraded": [i for i, v in candidate.items() if "manual" in v and v["manual"] == ""],
            "failed": [{"id": i, "input": v["input"], "why": "; ".join(v["why"])} for i, v in candidate.items() if not v["ok"]],
            "passed": sum(v["ok"] for v in candidate.values()), "total": len(candidate)}


def calibrate(run_paths):
    """Code chấm có khớp điểm chấm tay không. Trả (số khớp, tổng, danh sách lệch)."""
    same, total, differ = 0, 0, []
    for path in run_paths:
        for i, v in grade(path).items():
            if v["manual"] not in ("0", "1"):
                continue
            total += 1
            if v["ok"] == (v["manual"] == "1"):
                same += 1
            else:
                differ.append((os.path.basename(path), i, int(v["manual"]), int(v["ok"]), "; ".join(v["why"])))
    return same, total, differ


def main(argv=None):
    parser = argparse.ArgumentParser(description="Cổng kiểm một lượt chạy")
    parser.add_argument("run", nargs="?", help="file eval/run-N.csv cần kiểm")
    parser.add_argument("--base", help="lượt gốc để so câu tụt")
    parser.add_argument("--calibrate", action="store_true")
    args = parser.parse_args(argv)
    if args.calibrate:
        names = ["run-1.csv", "run-2.csv", "run-3.csv", "run-heldout.csv"]  # lượt 4 chưa có người chấm
        paths = [p for p in (os.path.join(ROOT, "eval", n) for n in names) if os.path.exists(p)]
        same, total, differ = calibrate(paths)
        print("Code chấm khớp chấm tay: %d/%d" % (same, total))
        for name, i, manual, auto, why in differ:
            print("  lệch %s %s: tay=%d code=%d %s" % (name, i, manual, auto, why))
        return 0
    if not args.run:
        parser.error("cần file lượt chạy hoặc --calibrate")
    try:
        report = compare(grade(args.run), grade(args.base) if args.base else None)
    except (OSError, ValueError, csv.Error) as error:
        print("CHẶN · lượt chạy không hợp lệ: %s" % error, file=sys.stderr)
        return 1
    print("%s PHẦN CƠ HỌC · %s · từng câu %d/%d" % (report["verdict"], args.run, report["passed"], report["total"]))
    print("Không xác nhận đạt toàn bộ CP2: ý nghĩa cần người chấm; dung_y_tra_loi cần 20 câu thường.")
    if report["citation"]["total"]:
        print("  Điều kiện mã CP2: %d/%d (chưa chấm nghĩa)" % (report["citation"]["ok"], report["citation"]["total"]))
    if report["ungraded"]:
        print("  Chưa có điểm người chấm: " + ", ".join(report["ungraded"]))
    for g in report["groups"]:
        print("  %-8s %d/%d %s" % (g["type"], g["ok"], g["total"], "đạt" if g["met"] else "CHƯA ĐẠT"))
    for reason in report["reasons"]:
        print("  - " + reason)
    if report["fixed"]:
        print("  Sửa được so với lượt gốc: " + ", ".join(report["fixed"]))
    if report["review"]:
        print("  Người cần đọc nghĩa (câu trả lời mới hoặc đổi): " + ", ".join(report["review"]))
    return 1 if report["verdict"] == "CHẶN" else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
