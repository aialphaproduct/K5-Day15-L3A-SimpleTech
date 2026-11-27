"""Phân tích lượt bạn học AI xen vào (Issue #40): class_events.csv x chat.csv x answers.csv.

Chạy:
    python evidence/count_interventions.py "<đường dẫn tới data/preclass>"

Chỉ in số đã tổng hợp (x/N, y%), không in mã học viên hay nội dung cá nhân.
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict


def main() -> int:
    folder = sys.argv[1] if len(sys.argv) > 1 else os.path.join("data", "preclass")
    ce_path = os.path.join(folder, "class_events.csv")
    chat_path = os.path.join(folder, "chat.csv")
    ans_path = os.path.join(folder, "answers.csv")

    for p in (ce_path, chat_path, ans_path):
        if not os.path.exists(p):
            sys.exit("Không tìm thấy %s. Truyền đường dẫn tới thư mục data/preclass của BTC." % p)

    # 1. class_events.csv: director_decided
    total_dd = 0
    inserted_by_cm = Counter()
    inserted_by_type = Counter()
    ce_refs = set()
    with open(ce_path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r.get("type") != "director_decided":
                continue
            total_dd += 1
            d = json.loads(r["data"]) if r.get("data") else {}
            if d.get("inserted") is True:
                cm = d.get("classmate_id") or "(trống)"
                inserted_by_cm[cm] += 1
                inserted_by_type[d.get("intervention_type") or "(trống)"] += 1
                if (r.get("ref_id") or "").strip():
                    ce_refs.add(r["ref_id"].strip())

    total_inserted = sum(inserted_by_cm.values())

    # 2. chat.csv: các dòng trả lời lượt xen vào (intervention_id != "")
    chat_by_id = {}
    replies_by_addr = Counter()
    iids_by_addr = defaultdict(set)
    hvs_by_addr = defaultdict(set)
    all_chat_iids = set()
    chat_lm = Counter()
    int_lm = Counter()

    with open(chat_path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            chat_by_id[r["id"]] = r
            chat_lm[(r.get("learning_mode") or "").strip() or "(trống)"] += 1
            iid = (r.get("intervention_id") or "").strip()
            if not iid:
                continue
            all_chat_iids.add(iid)
            int_lm[(r.get("learning_mode") or "").strip() or "(trống)"] += 1
            addr = (r.get("addressed_agent_id") or r.get("agent_id") or "").strip() or "(trống)"
            replies_by_addr[addr] += 1
            iids_by_addr[addr].add(iid)
            hvs_by_addr[addr].add((r.get("hv") or "").strip())

    overlap_keys = len(ce_refs & all_chat_iids)
    total_replies = sum(replies_by_addr.values())

    # 3. answers.csv: điểm rubric_* cho các câu trả lời lượt xen vào
    ans_int_status = Counter()
    rubric_all = {k: Counter() for k in ("rubric_bam_bai", "rubric_y_moi", "rubric_dung_ngu_canh")}
    rubric_by_addr = defaultdict(lambda: {k: Counter() for k in ("rubric_bam_bai", "rubric_y_moi", "rubric_dung_ngu_canh")})
    ans_lm = Counter()

    with open(ans_path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            ans_lm[(r.get("learning_mode") or "").strip() or "(trống)"] += 1
            if not (r.get("intervention_id") or "").strip():
                continue
            st = (r.get("trang_thai_cham") or "").strip()
            ans_int_status[st] += 1
            if st != "da_cham":
                continue
            addr = (chat_by_id.get(r.get("ref", ""), {}).get("addressed_agent_id") or "").strip() or "(trống)"
            for k in ("rubric_bam_bai", "rubric_y_moi", "rubric_dung_ngu_canh"):
                v = (r.get(k) or "").strip()
                if v != "":
                    rubric_all[k][v] += 1
                    rubric_by_addr[addr][k][v] += 1

    print("=== 1. QUYẾT ĐỊNH XEN VÀO (class_events.csv: director_decided) ===")
    print("Tổng director_decided: %d · inserted=True: %d/%d (%.1f%%) · inserted=False: %d/%d (%.1f%%)"
          % (total_dd, total_inserted, total_dd, total_inserted / total_dd * 100,
             total_dd - total_inserted, total_dd, (total_dd - total_inserted) / total_dd * 100))
    print("Theo kiểu xen (intervention_type):", dict(inserted_by_type))

    print("\n=== 2. ĐỐI CHIẾU KHÓA NỐI VÀ PHẢN HỒI THEO BẠN HỌC AI ===")
    print("Mã ref_id trong class_events (inserted=True): %d · Mã intervention_id duy nhất trong chat.csv: %d · Trùng trực tiếp: %d"
          % (len(ce_refs), len(all_chat_iids), overlap_keys))
    print("Tổng lượt học viên trả lời có intervention_id: %d dòng trên %d mã intervention_id duy nhất"
          % (total_replies, len(all_chat_iids)))
    for cm in ("classmate_inquisitive", "classmate_deep_thinker", "classmate_clown", "classmate_note_taker"):
        ins = inserted_by_cm[cm]
        ui = len(iids_by_addr[cm])
        rep = replies_by_addr[cm]
        hvs = len(hvs_by_addr[cm])
        ratio = (ui / ins * 100) if ins else 0.0
        print("  %-24s | inserted: %3d | mã có đáp lại (chat): %2d (tỷ lệ ước lượng %.1f%%) | %2d lượt trả lời (%2d hv)"
              % (cm, ins, ui, ratio, rep, hvs))

    print("\n=== 3. ĐIỂM RUBRIC CỦA CÂU TRẢ LỜI LẠI (answers.csv) ===")
    n_scored = ans_int_status["da_cham"]
    print("Trạng thái chấm:", dict(ans_int_status))
    for k in ("rubric_bam_bai", "rubric_y_moi", "rubric_dung_ngu_canh"):
        c = rubric_all[k]
        parts = ", ".join("%s điểm: %d/%d (%.1f%%)" % (s, c[s], n_scored, c[s] / n_scored * 100) for s in ("2", "1", "0"))
        print("  %-22s -> %s" % (k, parts))

    print("\n=== 4. KIỂM TRA LEARNING_MODE (maic vs tutor) ===")
    print("chat.csv learning_mode:", dict(chat_lm))
    print("chat.csv (có intervention_id) learning_mode:", dict(int_lm))
    print("answers.csv learning_mode:", dict(ans_lm))
    return 0


if __name__ == "__main__":
    sys.exit(main())
