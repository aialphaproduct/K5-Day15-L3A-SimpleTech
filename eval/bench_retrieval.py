"""Benchmark truy xuất đoạn bài (Issue #35): đo recall@1, recall@3 và lọc ngoài bài.

So sánh các cách trên 30 câu có nhãn (eval/retrieval_queries.csv) + 6 câu ngoài bài:
  1. idf_current       : bản IDF trước #35 (không ngưỡng điểm)
  2. bm25_hybrid       : BM25 (k1=1.2, b=0.75) + bigram + ngưỡng điểm/độ phủ (thuần code, 0 token)
  3. gemini_embedding  : vector cosine similarity dùng gemini-embedding-001 + ngưỡng cosine
  4. hybrid_bm25_embed : tìm kiếm lai (RRF kết hợp BM25 + gemini-embedding-001)

Chạy bằng 1 lệnh:
  python eval/bench_retrieval.py             # chạy đủ cả 4 cách (cần .env Gemini cho embedding)
  python eval/bench_retrieval.py --no-embed  # chỉ chạy 2 cách thuần code (0 token, chạy offline/CI)
"""
import argparse
import csv
import math
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "codebase"))

import tools  # noqa: E402

QUERIES_PATH = os.path.join(ROOT, "eval", "retrieval_queries.csv")


def _bigrams(tokens: list) -> set:
    return {tokens[i] + "_" + tokens[i + 1] for i in range(len(tokens) - 1)}


def _seq_tokens(s: str, expand: bool = False):
    plain_list, exact_list = [], []
    for tok in tools._raw_tokens(s):
        p = tools._plain(tok)
        if len(p) <= 1:
            continue
        is_acronym = tok.isupper() and len(tok) >= 2
        if p in tools.STOP and not is_acronym:
            continue
        plain_list.append(p)
        exact_list.append(tok.lower())
        if expand and p in tools.SYNONYMS:
            for syn in tools.SYNONYMS[p]:
                plain_list.append(syn)
                exact_list.append(syn)
    return plain_list, exact_list


def idf_current_search(query: str, docs: list, top_k: int = 3) -> list:
    """Bản IDF gốc trước #35 (không ngưỡng điểm)."""
    q_plain, q_exact = tools._words(query, expand=True)
    if not q_plain or not docs:
        return []
    q_ascii_only = {w for w in q_exact if w == tools._plain(w)}
    parsed, df = [], {}
    for p in docs:
        t_plain, t_exact = tools._words(p["text"])
        l_plain, _ = tools._words(p["lesson"])
        for w in (t_plain | l_plain):
            df[w] = df.get(w, 0) + 1
        parsed.append((p, t_plain, t_exact, l_plain))
    n = len(docs)
    scored = []
    for p, t_plain, t_exact, l_plain in parsed:
        score, exact_hits = 0.0, 0
        for w_exact in q_exact:
            w = tools._plain(w_exact)
            idf = math.log((n + 1) / (df.get(w, 0) + 1)) + 1.0
            if w_exact in t_exact:
                score += 2.0 * idf
                exact_hits += 1
            elif w_exact in q_ascii_only and w in t_plain:
                score += 1.5 * idf
            if w in l_plain:
                score += 0.8 * idf
        if score > 0:
            scored.append((score, exact_hits, p["code"]))
    scored.sort(key=lambda x: (-x[0], -x[1]))
    return [c for _, _, c in scored[:top_k]]


def bm25_hybrid_search(
    query: str,
    docs: list,
    top_k: int = 3,
    min_score: float = 2.5,
    min_coverage: float = 0.45,
) -> list:
    """BM25 (k1=1.2, b=0.75, tính IDF riêng cho text và lesson) + bigram + ngưỡng điểm & độ phủ câu hỏi."""
    q_base_plain, q_base_exact = _seq_tokens(query, expand=False)
    q_plain_seq, q_exact_seq = _seq_tokens(query, expand=True)
    if not q_plain_seq or not docs:
        return []
    q_base_count = max(len(set(q_base_plain)), 1)
    q_exact_unique = list(dict.fromkeys(q_exact_seq))
    q_ascii_only = {w for w in q_exact_unique if w == tools._plain(w)}
    q_bigrams = _bigrams([tools._plain(w) for w in tools._raw_tokens(query) if len(tools._plain(w)) > 1])

    parsed, df_text, df_lesson = [], {}, {}
    total_len = 0
    for p in docs:
        t_plain_seq, t_exact_seq = _seq_tokens(p["text"])
        l_plain_seq, _ = _seq_tokens(p["lesson"])
        tf_plain, tf_exact = {}, {}
        for w in t_plain_seq:
            tf_plain[w] = tf_plain.get(w, 0) + 1
        for w in t_exact_seq:
            tf_exact[w] = tf_exact.get(w, 0) + 1
        l_set = set(l_plain_seq)
        doc_len = max(len(t_plain_seq), 1)
        total_len += doc_len
        for w in set(tf_plain):
            df_text[w] = df_text.get(w, 0) + 1
        for w in l_set:
            df_lesson[w] = df_lesson.get(w, 0) + 1
        t_bigrams = _bigrams([tools._plain(w) for w in tools._raw_tokens(p["text"]) if len(tools._plain(w)) > 1])
        parsed.append((p, tf_plain, tf_exact, l_set, doc_len, t_bigrams))

    n = len(docs)
    avgdl = total_len / n
    k1, b = 1.2, 0.75
    scored = []
    for p, tf_plain, tf_exact, l_set, doc_len, t_bigrams in parsed:
        score = 0.0
        exact_hits = 0
        matched_terms = set()
        for w_exact in q_exact_unique:
            w = tools._plain(w_exact)
            n_t = df_text.get(w, 0)
            if n_t > 0:
                idf_t = math.log((n - n_t + 0.5) / (n_t + 0.5) + 1.0)
                tf_e = tf_exact.get(w_exact, 0)
                tf_p = tf_plain.get(w, 0) if w_exact in q_ascii_only else 0
                if tf_e > 0:
                    bm25 = idf_t * (tf_e * (k1 + 1)) / (tf_e + k1 * (1 - b + b * doc_len / avgdl))
                    score += 1.6 * bm25
                    exact_hits += 1
                    matched_terms.add(w)
                elif tf_p > 0:
                    bm25 = idf_t * (tf_p * (k1 + 1)) / (tf_p + k1 * (1 - b + b * doc_len / avgdl))
                    score += 1.25 * bm25
                    matched_terms.add(w)
            n_l = df_lesson.get(w, 0)
            if n_l > 0 and w in l_set:
                idf_l = math.log((n - n_l + 0.5) / (n_l + 0.5) + 1.0)
                score += 0.6 * idf_l
                matched_terms.add(w)
        bg_hits = len(q_bigrams & t_bigrams)
        score += bg_hits * 1.0
        coverage = len(matched_terms) / q_base_count
        if score >= min_score and (len(matched_terms) >= 2 or coverage >= min_coverage):
            scored.append((score, exact_hits, p["code"]))
    scored.sort(key=lambda x: (-x[0], -x[1]))
    return [c for _, _, c in scored[:top_k]]


def _cosine(a: list, b: list) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


def _embed_batch(texts: list, task_type: str) -> list:
    """Gọi Gemini batchEmbedContents (gemini-embedding-001) — chỉ 1 request cho cả lô."""
    import ai

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:batchEmbedContents"
    body = {
        "requests": [
            {
                "model": "models/gemini-embedding-001",
                "taskType": task_type,
                "content": {"parts": [{"text": t}]},
            }
            for t in texts
        ]
    }
    data = ai.post_json(url, {"x-goog-api-key": ai.API_KEY}, body, timeout=60)
    return [e["values"] for e in data["embeddings"]]


def evaluate_embedding(docs: list, rows: list, min_sim: float = 0.65, min_score: float = 2.5):
    """Đo gemini_embedding (pure semantic) và hybrid_bm25_embed (RRF lai)."""
    doc_texts = ["%s | %s" % (d["lesson"], d["text"]) for d in docs]
    query_texts = [r["query"] for r in rows]

    t_doc = time.perf_counter()
    doc_vecs = _embed_batch(doc_texts, "RETRIEVAL_DOCUMENT")
    t_q = time.perf_counter()
    q_vecs = _embed_batch(query_texts, "RETRIEVAL_QUERY")
    q_embed_ms = ((time.perf_counter() - t_q) / len(rows)) * 1000
    doc_embed_ms = (t_q - t_doc) * 1000

    pos_idx = [i for i, r in enumerate(rows) if r["expected_code"] != "NONE"]
    neg_idx = [i for i, r in enumerate(rows) if r["expected_code"] == "NONE"]

    def _run_mode(name, hybrid=False):
        r1 = r3 = neg_skip = 0
        missed = []
        t0 = time.perf_counter()
        for i in pos_idx + neg_idx:
            q_vec = q_vecs[i]
            sims = [(_cosine(q_vec, dv), docs[j]["code"]) for j, dv in enumerate(doc_vecs)]
            sims.sort(reverse=True)
            if not hybrid:
                codes = [c for s, c in sims[:3] if s >= min_sim]
            else:
                bm25_codes = bm25_hybrid_search(rows[i]["query"], docs, top_k=6, min_score=min_score)
                emb_codes = [c for s, c in sims[:6] if s >= min_sim]
                if not bm25_codes and not emb_codes:
                    codes = []
                else:
                    rrf = {}
                    for rank, c in enumerate(bm25_codes):
                        rrf[c] = rrf.get(c, 0.0) + 1.0 / (20 + rank + 1)
                    for rank, c in enumerate(emb_codes):
                        rrf[c] = rrf.get(c, 0.0) + 1.0 / (20 + rank + 1)
                    codes = [c for c, _ in sorted(rrf.items(), key=lambda x: -x[1])[:3]]
            exp = rows[i]["expected_code"]
            if exp == "NONE":
                if not codes:
                    neg_skip += 1
            else:
                if codes and codes[0] == exp:
                    r1 += 1
                if exp in codes[:3]:
                    r3 += 1
                else:
                    missed.append((rows[i]["id"], exp, codes[:3]))
        rank_ms = ((time.perf_counter() - t0) / len(rows)) * 1000
        return {
            "name": name,
            "r1": r1,
            "r3": r3,
            "n_pos": len(pos_idx),
            "neg_skip": neg_skip,
            "n_neg": len(neg_idx),
            "avg_ms": q_embed_ms + rank_ms,
            "note": "batch embed doc %.0fms; ~15 tok/câu (API embedding)" % doc_embed_ms,
            "missed": missed,
        }

    return [
        _run_mode("gemini_embedding (sim>=%.2f)" % min_sim, hybrid=False),
        _run_mode("hybrid_bm25_embed (RRF)", hybrid=True),
    ]


def evaluate(name: str, rows: list, search_fn):
    pos = [r for r in rows if r["expected_code"] != "NONE"]
    neg = [r for r in rows if r["expected_code"] == "NONE"]
    r1 = r3 = neg_skip = 0
    lat_sum = 0.0
    missed = []
    for r in pos:
        t_call = time.perf_counter()
        codes = search_fn(r["query"])
        lat_sum += time.perf_counter() - t_call
        exp = r["expected_code"]
        if codes and codes[0] == exp:
            r1 += 1
        if exp in codes[:3]:
            r3 += 1
        else:
            missed.append((r["id"], exp, codes[:3]))
    for r in neg:
        t_call = time.perf_counter()
        codes = search_fn(r["query"])
        lat_sum += time.perf_counter() - t_call
        if not codes:
            neg_skip += 1
    avg_ms = (lat_sum / len(rows)) * 1000
    return {
        "name": name,
        "r1": r1,
        "r3": r3,
        "n_pos": len(pos),
        "neg_skip": neg_skip,
        "n_neg": len(neg),
        "avg_ms": avg_ms,
        "note": "0 token (thuần code)",
        "missed": missed,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-embed", "--no-llm", dest="no_embed", action="store_true", help="Chỉ chạy 2 cách thuần code (0 token)")
    ap.add_argument("--min-score", type=float, default=2.5, help="Ngưỡng điểm cho bm25_hybrid")
    ap.add_argument("--min-sim", type=float, default=0.68, help="Ngưỡng cosine cho gemini_embedding")
    args = ap.parse_args()

    docs = tools._load()
    with open(QUERIES_PATH, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    results = [
        evaluate("idf_current (trước)", rows, lambda q: idf_current_search(q, docs, top_k=3)),
        evaluate("bm25_hybrid (min=%.1f)" % args.min_score, rows, lambda q: bm25_hybrid_search(q, docs, top_k=3, min_score=args.min_score)),
    ]
    if not args.no_embed:
        import ai

        if ai.MODEL_PROVIDER in ("gemini", "google") and ai.API_KEY:
            results.extend(evaluate_embedding(docs, rows, min_sim=args.min_sim, min_score=args.min_score))
        else:
            print("(Bỏ qua gemini_embedding vì chưa cấu hình Gemini API key trong .env)")

    print("\n| Phương pháp | Recall@1 | Recall@3 | Lọc ngoài bài (không gọi model) | Độ trễ TB | Chi phí thêm |")
    print("|---|---|---|---|---|---|")
    for res in results:
        print(
            "| %s | %d/%d (%.1f%%) | %d/%d (%.1f%%) | %d/%d (%.1f%%) | %.1f ms | %s |"
            % (
                res["name"],
                res["r1"], res["n_pos"], 100 * res["r1"] / res["n_pos"],
                res["r3"], res["n_pos"], 100 * res["r3"] / res["n_pos"],
                res["neg_skip"], res["n_neg"], 100 * res["neg_skip"] / res["n_neg"],
                res["avg_ms"],
                res["note"],
            )
        )
    for res in results:
        if res["missed"]:
            print("  Trượt recall@3 [%s]: %s" % (res["name"], res["missed"]))


if __name__ == "__main__":
    main()
