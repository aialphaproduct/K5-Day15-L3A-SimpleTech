"""Gói phần tối thiểu của bản preclass offline để demo Bài 1 sau đăng nhập.

    python deploy/pack-preclass.py <thư mục preclass> <file .tar.gz ra>

Chỉ lấy giao diện, máy chủ mock và slide Bài 1. Không lấy .env, lời giảng, bài khác, video khác, file tải lên,
đáp án và phản hồi (thay bằng dữ liệu rỗng). Gói này không đưa vào repo.
"""
import io
import json
import os
import sys
import tarfile

DECK = "decks/phase1/day01-ai-llm-foundation"
BLANK = ("answer_keys.json", "answer_keys_live.json", "answer_keys_live_review.json", "extra_answer_keys.json",
         "lab_keys.json", "extra_lab_keys.json", "feedback.json", "pre_post.json")
SKIP_DATA = ("state.json", "_truoc_khi_gop")


def files(source):
    for name in sorted(os.listdir(source)):
        if os.path.isfile(os.path.join(source, name)) and (name == "index.html" or name.startswith(("favicon", "apple-icon", "overrides"))):
            yield name
    for folder in ("assets", "brand", "data", DECK):
        for base, _, names in os.walk(os.path.join(source, folder)):
            for name in names:
                yield os.path.relpath(os.path.join(base, name), source).replace(os.sep, "/")
    backend = os.path.join(source, "backend-mock")
    for name in sorted(os.listdir(backend)):
        if name.endswith(".py"):
            yield "backend-mock/" + name
    for name in sorted(os.listdir(os.path.join(backend, "data"))):
        if name.endswith(".json") and name not in SKIP_DATA:
            yield "backend-mock/data/" + name


def main(source, target):
    count = 0
    with tarfile.open(target, "w:gz") as tar:
        for name in files(source):
            path = os.path.join(source, name)
            if os.path.basename(name) in BLANK and name.startswith("backend-mock/data/"):
                with open(path, encoding="utf-8") as f:
                    data = json.dumps(type(json.load(f))()).encode()
                info = tarfile.TarInfo(name)
                info.size, info.mode = len(data), 0o644
                tar.addfile(info, io.BytesIO(data))
            else:
                tar.add(path, arcname=name)
            count += 1
    print("%d file, %.1f MB -> %s" % (count, os.path.getsize(target) / 1e6, target))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
