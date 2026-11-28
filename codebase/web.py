"""Máy chủ trợ giảng AI: API /ask, widget và một trang mô phỏng để demo.
Chạy: python run.py   (hoặc trực tiếp: python codebase/web.py)
Mở trình duyệt: http://localhost:5000
Tiện ích trình duyệt nằm ở codebase/extension/ và gọi cùng API này.
"""
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from flask import Flask, request, jsonify, send_from_directory

import insights
from agent import answer
from tools import get_passage

MAX_CHARS = 2000
CITE = re.compile(r"\[([A-Za-z0-9\-]+)\]")
LEARNER = re.compile(r"^HV-[a-z0-9]{2,12}$")
VIDEO_AT = re.compile(r"^\d{1,2}:\d{2}$")
# Chỉ khớp tin nhắn thuần lời chào; câu có kèm nội dung hỏi vẫn đi qua trợ giảng.
GREETING = re.compile(
    r"^(xin chào|chào|chao|hello|hi|hey|alo)( (bạn|ban|trợ giảng|thầy|cô|ad|shop))?( (ạ|nhé|nha))?[\s!.?~]*$",
    re.IGNORECASE,
)
GREETING_REPLY = "Chào bạn! Bạn đang vướng chỗ nào trong bài? Ví dụ: \"LLM sinh câu trả lời bằng cách nào?\""

app = Flask(__name__)

# Trang nền chỉ để demo widget; không mô phỏng lại tính năng của trang pre-class.
HTML = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Trang mô phỏng — Trợ giảng AI Simple Tech</title>
<style>
  body { font-family: system-ui, -apple-system, sans-serif; background: #f1f5f9; color: #0f172a; margin: 0; }
  .banner { background: #fef3c7; border-bottom: 1px solid #f59e0b; padding: 10px 16px; font-size: 14px; text-align: center; }
  main { max-width: 860px; margin: 0 auto; padding: 24px 16px 120px; }
  .box { background: #cbd5e1; border-radius: 12px; display: flex; align-items: center; justify-content: center; text-align: center; color: #475569; padding: 16px; }
  .video { aspect-ratio: 16/9; }
  .quiz { min-height: 120px; margin-top: 16px; }
</style>
</head>
<body>
<div class="banner"><b>Trang mô phỏng.</b> Đây không phải preclass-online.com; phần của nhóm là nút "Hỏi trợ giảng" ở góc dưới.</div>
<main>
  <h1>Bài học pre-class</h1>
  <div class="box video">Video bài giảng (đã có sẵn trên trang pre-class)</div>
  <div class="box quiz">Câu hỏi giữa video và mini lab (đã có sẵn)</div>
</main>
<script src="/widget.js"></script>
</body>
</html>
"""


@app.route("/")
def index():
    return HTML


@app.route("/widget.js")
def widget():
    return send_from_directory(os.path.join(HERE, "extension"), "widget.js")


def reply(data, context=None, annotate=None):
    """Xử lý một yêu cầu hỏi: trả (dict, mã HTTP). Dùng chung cho Flask và demo/preclass_demo.py.

    context(câu hỏi, phút video) -> câu gửi cho trợ giảng; annotate(body, câu hỏi) bổ sung trường vào kết quả.
    """
    data = data if isinstance(data, dict) else {}
    text = data.get("text")
    if not isinstance(text, str) or not text.strip():
        return {"output": "Bạn chưa nhập câu hỏi.", "passages": []}, 400
    text = text.strip()
    if len(text) > MAX_CHARS:
        return {"output": "Câu hỏi dài quá %d ký tự." % MAX_CHARS, "passages": []}, 400
    learner = str(data.get("learner") or "")
    learner = learner if LEARNER.match(learner) else "HV-an-danh"
    video_at = str(data.get("at") or "")
    video_at = video_at if VIDEO_AT.match(video_at) else ""
    greeting = bool(GREETING.match(unicodedata.normalize("NFC", text)))
    sent = context(text, video_at) if context and not greeting else text

    def run():
        if greeting:
            return {"output": GREETING_REPLY, "passages": []}, 200
        try:
            output = answer(sent)["output"]
            passages = [get_passage(code) for code in dict.fromkeys(CITE.findall(output))]
        except Exception:
            app.logger.exception("answer() lỗi")
            return {"output": "Trợ giảng đang lỗi, bạn thử lại sau.", "passages": []}, 502
        return {
            "output": output,
            "passages": [{"code": p["code"], "text": p["text"]} for p in passages if p],
        }, 200

    (body, status), metrics = insights.measure(run)
    if annotate and status == 200 and not greeting:
        annotate(body, text)
    metrics["greeting"] = greeting
    try:
        insights.record(text, sent, video_at, learner, body, status, metrics)
    except OSError:
        app.logger.exception("không ghi được log")
    return body, status


@app.route("/ask", methods=["POST"])
def ask():
    # Chỉ nhận application/json để trang web lạ không gửi được yêu cầu chéo nguồn.
    body, status = reply(request.get_json(silent=True))
    return jsonify(body), status


def local_only(host, remote):
    """Trang đo lường có câu học viên gõ: chỉ cho mở từ chính máy này."""
    return remote in ("127.0.0.1", "::1") and (host or "").rsplit(":", 1)[0] in ("localhost", "127.0.0.1")


@app.route("/admin")
@app.route("/admin/data")
@app.route("/admin/analyze", methods=["POST"])
def admin():
    if not local_only(request.host, request.remote_addr):
        return jsonify({"error": "Chỉ mở được trên máy chạy demo."}), 403
    if request.path == "/admin":
        return send_from_directory(HERE, "admin.html")
    if request.path == "/admin/data":
        return jsonify(insights.summary())
    if not request.is_json:
        return jsonify({"error": "Cần application/json."}), 400
    return jsonify(insights.analyze())


@app.route("/metrics")
def metrics():
    if request.remote_addr not in ("127.0.0.1", "::1"):
        return "", 403
    return insights.prometheus(), 200, {"Content-Type": "text/plain; version=0.0.4; charset=utf-8"}


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 5000))
    print("Open browser: http://localhost:%d" % port)
    app.run(host=host, port=port, debug=False, threaded=True)
