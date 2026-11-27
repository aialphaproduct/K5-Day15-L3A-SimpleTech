"""Giao diện web — trợ giảng AI nhúng dưới video pre-class.
Chạy: python run.py   (hoặc trực tiếp: python codebase/web.py)
Mở trình duyệt: http://localhost:5000
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, render_template_string

from agent import answer

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Trợ giảng AI — Simple Tech</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, -apple-system, sans-serif; background: #0f1117; color: #e2e8f0; min-height: 100vh; }

  .layout { max-width: 900px; margin: 0 auto; padding: 20px 16px 40px; }

  /* Video placeholder */
  .video-wrap { position: relative; background: #1a1d26; border-radius: 12px; overflow: hidden; margin-bottom: 20px; aspect-ratio: 16/9; }
  .video-wrap iframe { width: 100%; height: 100%; border: 0; }
  .video-label { position: absolute; top: 12px; left: 14px; background: rgba(0,0,0,.55); font-size: 12px; color: #94a3b8; padding: 4px 8px; border-radius: 6px; }

  /* Chat box */
  .chat-box { background: #1a1d26; border-radius: 12px; overflow: hidden; border: 1px solid #2d3148; }
  .chat-header { padding: 14px 18px; border-bottom: 1px solid #2d3148; display: flex; align-items: center; gap: 10px; }
  .chat-header .dot { width: 9px; height: 9px; border-radius: 50%; background: #22c55e; flex-shrink: 0; }
  .chat-header h2 { font-size: 14px; font-weight: 600; color: #f1f5f9; }
  .chat-header span { font-size: 12px; color: #64748b; margin-left: auto; }

  .messages { padding: 16px 18px; min-height: 260px; max-height: 420px; overflow-y: auto; display: flex; flex-direction: column; gap: 14px; }

  .msg { display: flex; gap: 10px; }
  .msg.user { flex-direction: row-reverse; }

  .avatar { width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 14px; }
  .avatar.bot { background: #312e81; }
  .avatar.user { background: #1e3a5f; }

  .bubble { max-width: 78%; padding: 10px 14px; border-radius: 12px; font-size: 14px; line-height: 1.6; }
  .bubble.bot { background: #252840; border-radius: 2px 12px 12px 12px; color: #e2e8f0; }
  .bubble.user { background: #1e40af; border-radius: 12px 2px 12px 12px; color: #fff; }

  .code-tag { display: inline-block; background: #164e63; color: #67e8f9; border-radius: 4px; padding: 1px 6px; font-family: monospace; font-size: 12px; margin: 0 1px; }
  .no-basis { color: #f59e0b; font-style: italic; }

  .thinking { display: flex; align-items: center; gap: 6px; color: #64748b; font-size: 13px; }
  .dots span { animation: blink 1.2s infinite; opacity: 0; display: inline-block; }
  .dots span:nth-child(2) { animation-delay: .2s; }
  .dots span:nth-child(3) { animation-delay: .4s; }
  @keyframes blink { 0%,80%,100% { opacity: 0; } 40% { opacity: 1; } }

  /* Input */
  .input-row { display: flex; gap: 8px; padding: 12px 14px; border-top: 1px solid #2d3148; background: #151720; }
  .input-row input { flex: 1; background: #252840; border: 1px solid #2d3148; border-radius: 8px; padding: 10px 14px; color: #e2e8f0; font-size: 14px; outline: none; }
  .input-row input:focus { border-color: #3b82f6; }
  .input-row input::placeholder { color: #475569; }
  .input-row button { background: #2563eb; border: 0; border-radius: 8px; color: #fff; padding: 10px 18px; font-size: 14px; cursor: pointer; font-weight: 500; transition: background .15s; white-space: nowrap; }
  .input-row button:hover { background: #1d4ed8; }
  .input-row button:disabled { background: #334155; cursor: default; }
</style>
</head>
<body>
<div class="layout">

  <div class="video-wrap">
    <iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ?controls=1" allowfullscreen></iframe>
    <div class="video-label">📺 Video bài học · Day 01</div>
  </div>

  <div class="chat-box">
    <div class="chat-header">
      <div class="dot"></div>
      <h2>Trợ giảng AI</h2>
      <span>Hỏi về nội dung video vừa xem</span>
    </div>
    <div class="messages" id="msgs">
      <div class="msg">
        <div class="avatar bot">🤖</div>
        <div class="bubble bot">Xin chào! Bạn có câu hỏi gì về nội dung video vừa xem không? Tôi sẽ trả lời kèm mã đoạn bài để bạn kiểm chứng.</div>
      </div>
    </div>
    <div class="input-row">
      <input id="inp" type="text" placeholder="Hỏi về nội dung bài học…" autocomplete="off">
      <button id="btn" onclick="send()">Gửi</button>
    </div>
  </div>

</div>

<script>
const msgs = document.getElementById("msgs");
const inp  = document.getElementById("inp");
const btn  = document.getElementById("btn");

inp.addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } });

function formatText(text) {
  // Highlight passage codes like [GIA-01]
  return text
    .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
    .replace(/\\[([A-Za-z0-9\\-]+)\\]/g, '<span class="code-tag">[$1]</span>')
    .replace(/Không có trong bài[^.]*\\./g, m => '<span class="no-basis">' + m + '</span>');
}

function append(role, html) {
  const row = document.createElement("div");
  row.className = "msg " + role;
  row.innerHTML = '<div class="avatar ' + role + '">' + (role==="bot"?"🤖":"👤") + '</div>'
    + '<div class="bubble ' + role + '">' + html + '</div>';
  msgs.appendChild(row);
  msgs.scrollTop = msgs.scrollHeight;
  return row;
}

async function send() {
  const text = inp.value.trim();
  if (!text) return;
  inp.value = "";
  btn.disabled = true;

  append("user", text.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"));

  const thinking = append("bot",
    '<div class="thinking">Đang tra bài <span class="dots"><span>.</span><span>.</span><span>.</span></span></div>');

  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    const data = await res.json();
    thinking.querySelector(".bubble").innerHTML = formatText(data.output || "Không có phản hồi.");
  } catch(err) {
    thinking.querySelector(".bubble").innerHTML = '<span class="no-basis">Lỗi kết nối — thử lại nhé.</span>';
  }
  btn.disabled = false;
  inp.focus();
}
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(force=True)
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"output": "Bạn chưa nhập câu hỏi."}), 400
    result = answer(text)
    output = result.get("output", "") if isinstance(result, dict) else str(result)
    return jsonify({"output": output})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("Open browser: http://localhost:%d" % port)
    app.run(host="0.0.0.0", port=port, debug=False)
