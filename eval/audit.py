"""Read-only audit of saved runs; mechanical conditions are not semantic grades.

python eval/audit.py
python eval/audit.py --output eval/audit-final.md  # new Markdown file only

Does not call a model, edit runs, change CP2 metrics or replace human grading.
"""
import argparse
import csv
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CODE = re.compile(r"\[([A-Za-z0-9-]+)\]")
REDIRECT = re.compile(r"không có trong bài|\bTA\b|hỏi trợ giảng|liên hệ.*trợ giảng", re.IGNORECASE)
TYPES = ("thuong", "kho", "tu_choi")
STATUSES = {"verified_external", "member", "unverified", "self_authored", "synthetic"}


def read_csv(path, required):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not set(required) <= set(reader.fieldnames or ()):
            raise ValueError("%s: missing columns %s" % (path, ", ".join(sorted(set(required) - set(reader.fieldnames or ())))))
        rows = list(reader)
    if not rows:
        raise ValueError("%s: empty CSV" % path)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError("%s: malformed CSV row" % path)
    return rows


def index_unique(rows):
    indexed = {}
    for row in rows:
        key = row["id"]
        if not key or key in indexed:
            raise ValueError("missing or duplicate id: %s" % key)
        indexed[key] = row
    return indexed


def valid_citations(output, known):
    """Necessary syntax condition only: nonempty citation set, all codes known."""
    cited = set(CODE.findall(output))
    return bool(cited) and cited <= known


def citation_check(question, output, known):
    """Also require explicit expected/criterion codes; still no semantic judgment."""
    required = set(CODE.findall(question.get("expected", "") + " " + question.get("pass_criterion", "")))
    return valid_citations(output, known) and required <= set(CODE.findall(output))


def audit_sources(questions, metadata):
    """A nguoi_dung/data_that label alone never verifies external provenance."""
    claimed = verified = 0
    details = []
    for question in questions:
        key = question["id"]
        source = question["source"].split(":", 1)[0].split(" ", 1)[0].strip()
        is_claimed = source in {"nguoi_dung", "data_that"}
        record = metadata.get(key, {})
        status = record.get("status", "unverified" if is_claimed else "self_authored")
        if status not in STATUSES:
            raise ValueError("%s: unknown source status %s" % (key, status))
        claimed += is_claimed
        verified += is_claimed and status == "verified_external" and bool(record.get("reference", "").strip())
        details.append({"id": key, "status": status, "reference": record.get("reference", "")})
    needed = math.ceil(len(questions) / 3)
    return {"total": len(questions), "claimed": claimed, "verified": verified,
            "needed": needed, "met": verified >= needed, "details": details}


def audit_run(rows, questions, known):
    """Preserve pass; independently count necessary conditions on all denominators."""
    indexed = index_unique(rows)
    question_map = index_unique(questions)
    if set(indexed) != set(question_map):
        raise ValueError("run IDs differ from benchmark: missing=%s extra=%s" % (
            sorted(set(question_map) - set(indexed)), sorted(set(indexed) - set(question_map))))
    groups = {kind: {"pass": 0, "ungraded": 0, "total": 0} for kind in TYPES}
    citation = {"count": 0, "presence": 0, "total": 0, "missing": [], "grade": None}
    no_basis = {kind: {"count": 0, "total": 0, "missing": [], "grade": None} for kind in ("kho", "tu_choi")}
    for key, question in question_map.items():
        row = indexed[key]
        kind = question["type"]
        if kind not in TYPES or row["type"] != kind:
            raise ValueError("%s: inconsistent or unsupported type" % key)
        historical = row["pass"].strip()
        if historical not in ("", "0", "1"):
            raise ValueError("%s: pass must be 0, 1 or empty" % key)
        group = groups[kind]
        group["total"] += 1
        group["pass"] += historical == "1"
        group["ungraded"] += historical == ""
        output = row.get("output", "")
        technical_ok = not row.get("error", "").strip()
        if kind == "thuong":
            citation["total"] += 1
            citation["presence"] += technical_ok and valid_citations(output, known)
            met = technical_ok and citation_check(question, output, known)
            citation["count"] += met
            if not met:
                citation["missing"].append(key)
        else:
            result = no_basis[kind]
            result["total"] += 1
            met = technical_ok and bool(REDIRECT.search(output))
            result["count"] += met
            if not met:
                result["missing"].append(key)
    return {"groups": groups, "citation": citation, "no_basis": no_basis,
            "meaning": {"sample": groups["thuong"]["total"], "required": 20,
                        "sample_sufficient": groups["thuong"]["total"] >= 20, "grade": None},
            "errors": sum(bool(row.get("error", "").strip()) for row in rows)}


def ratio(count, total):
    return "%d/%d (%.1f%%)" % (count, total, 100 * count / total) if total else "0/0 (không có mẫu)"


def markdown_cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def build_report(root=ROOT):
    root = Path(root)
    benchmark = read_csv(root / "eval/benchmark.csv", ("id", "type", "source", "expected", "pass_criterion"))
    index_unique(benchmark)
    source_path = root / "eval/source-audit.csv"
    metadata = index_unique(read_csv(source_path, ("id", "status", "reference"))) if source_path.exists() else {}
    if set(metadata) - {row["id"] for row in benchmark}:
        raise ValueError("source-audit.csv has IDs outside benchmark.csv")
    sources = audit_sources(benchmark, metadata)
    known = {row["code"] for row in read_csv(root / "data/lessons/passages.csv", ("code",))}
    lines = ["# Kiểm toán kết quả đã lưu theo chuẩn CP2", "",
             "Lệnh: `python eval/audit.py`. Không gọi model, không sửa bộ thử, chuẩn chấm, output hay điểm lịch sử.", "",
             "## Nguồn câu thử", "",
             "- Nhãn nguồn người dùng/data thật trong benchmark: **%s**." % ratio(sources["claimed"], sources["total"]),
             "- Nguồn ngoài nhóm có hồ sơ xác minh trong `eval/source-audit.csv`: **%s**; cần ít nhất **%d/%d** (≥1/3)." % (
                 ratio(sources["verified"], sources["total"]), sources["needed"], sources["total"]),
             "- Trạng thái phần nguồn: **%s**. Nhãn `nguoi_dung` tự thân không xác nhận nguồn." % ("đủ số nguồn được xác minh" if sources["met"] else "chưa đủ nguồn được xác minh"), "",
             "| ID cần lưu ý | Trạng thái xác minh | Hồ sơ |", "|---|---|---|"]
    if not source_path.exists():
        lines.append("| — | Chưa có source-audit.csv; không tự xác nhận bất kỳ câu nào | — |")
    for item in sources["details"]:
        if item["status"] in {"member", "unverified"}:
            lines.append("| %s | %s | %s |" % (item["id"], item["status"], markdown_cell(item["reference"])))
    lines += ["", "## Điểm từng câu đã lưu và điều kiện trích dẫn", "",
              "`pass` là tiêu chí riêng từng câu, không thay thế ba metric CP2. Hai cột mã dưới đây chỉ kiểm điều kiện cần; nội dung trích có đúng nghĩa vẫn phải được người chấm đọc.", "",
              "| File / run ID | pass tổng | pass thường / khó / từ chối | Có mã, mọi mã tồn tại | Thêm đúng mã yêu cầu trong đề | Câu thiếu điều kiện mã |",
              "|---|---|---|---|---|---|"]
    paths = sorted((p for p in (root / "eval").glob("run-*.csv") if re.fullmatch(r"run-\d+\.csv", p.name)),
                   key=lambda p: int(p.stem.split("-")[1]))
    heldout = root / "eval/run-heldout.csv"
    if heldout.exists():
        paths.append(heldout)
    if not paths:
        raise ValueError("no saved run-N.csv files found")
    reports = []
    for path in paths:
        questions = read_csv(root / "eval/benchmark_heldout.csv", ("id", "type", "source", "expected", "pass_criterion")) if path.name == "run-heldout.csv" else benchmark
        rows = read_csv(path, ("run_id", "id", "type", "output", "pass", "error"))
        run_ids = {row["run_id"] for row in rows}
        if len(run_ids) != 1 or not next(iter(run_ids)):
            raise ValueError("%s: missing or inconsistent run_id" % path)
        result = audit_run(rows, questions, known)
        groups = result["groups"]
        total = len(rows)
        citation = result["citation"]
        lines.append("| %s / `%s` | %s | %s | %s | %s | %s |" % (
            path.name, next(iter(run_ids)), ratio(sum(g["pass"] for g in groups.values()), total),
            " · ".join("%d/%d" % (groups[k]["pass"], groups[k]["total"]) for k in TYPES),
            ratio(citation["presence"], citation["total"]), ratio(citation["count"], citation["total"]),
            ", ".join(citation["missing"]) or "—"))
        reports.append((path.name, result))
    lines += ["", "Mã đối chiếu lấy từ `[MÃ]` ghi rõ trong expected/pass_criterion; không suy đáp án từ input và không sửa expected. Kho mã hiện tại dùng để kiểm sự tồn tại, không tái dựng kho bài ở từng thời điểm.", "",
              "## Điều kiện báo thiếu căn cứ / chuyển TA", "",
              "Chỉ đếm output chứa ‘Không có trong bài’, ‘TA’ hoặc lời hướng tới trợ giảng. Có cụm từ này **không chứng minh không bịa**, không kiểm được ý nghĩa, mức từ chối hay thông tin nhạy cảm. Kết quả đầy đủ của `khong_bia` vẫn chờ người chấm.", "",
              "| File | Khó: có lời báo/chuyển TA | Từ chối: có lời báo/chuyển TA | Câu thiếu điều kiện |",
              "|---|---|---|---|"]
    for name, result in reports:
        no_basis = result["no_basis"]
        lines.append("| %s | %s | %s | %s |" % (
            name, ratio(no_basis["kho"]["count"], no_basis["kho"]["total"]),
            ratio(no_basis["tu_choi"]["count"], no_basis["tu_choi"]["total"]),
            ", ".join(no_basis["kho"]["missing"] + no_basis["tu_choi"]["missing"]) or "—"))
    lines += ["", "## Đúng ý và kết luận chuẩn", "",
              "- `dung_y_tra_loi`: cần mẫu 20 câu thường và người thứ hai chấm 5 output, khớp ≥4/5. Script không chấm nghĩa và không công nhận kết quả này chỉ từ cột pass."]
    for name, result in reports:
        sample = result["meaning"]
        lines.append("- `%s`: %d câu thường / cần 20 — **%s**; %d câu chưa có điểm pass; %d lỗi kỹ thuật." % (
            name, sample["sample"], "đủ số mẫu, vẫn cần người chấm" if sample["sample_sufficient"] else "chưa đủ mẫu",
            sum(g["ungraded"] for g in result["groups"].values()), result["errors"]))
    lines += ["", "Không tự kết luận ‘đạt chuẩn CP2’ từ báo cáo này. Nếu điều kiện cần trích dẫn dưới 90% thì `trich_dung_ma` chưa thể đạt; nếu đủ điều kiện cần thì vẫn phải đọc đối chiếu ý. Bộ kín là phép đo riêng, không gộp mẫu hay thay kết quả bộ 23 câu.", "",
              "Chuẩn CP2 và dữ liệu chạy cũ được giữ nguyên. Điểm R5 lượt 1 → lượt 2 phải được trình bày theo lịch sử; kiểm toán sau CP4 được ghi nhận riêng.", ""]
    return "\n".join(lines)


def write_report(path, report):
    path = Path(path)
    if path.suffix.lower() != ".md":
        raise ValueError("--output only accepts a new .md file")
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(report)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a NEW Markdown file; existing files are never overwritten")
    args = parser.parse_args(argv)
    try:
        report = build_report()
        if args.output:
            write_report(args.output, report)
        else:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
            print(report, end="")
    except (OSError, ValueError, csv.Error) as error:
        print("audit: %s" % error, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
