"""Nối model — chỗ DUY NHẤT trong bản chạy thử gọi model AI. NHÓM VIẾT phần gọi model thật.

Hợp đồng (giữ nguyên để khung đo được token):
    call_model(system: str, user: str) -> dict với 4 khoá
        "text":       str   chữ model trả về
        "model":      str   tên model đã gọi (để tra giá ở bảng giá model)
        "tokens_in":  int   số token vào, lấy từ trường usage trong phản hồi API — KHÔNG ước lượng
        "tokens_out": int   số token ra, gồm cả token suy luận / suy nghĩ nếu API tính riêng
    @model_call (từ tracing.py) tự ghi mỗi lần gọi vào trace; agent.py gọi call_model bao nhiêu lần
    cũng được, khung tự cộng token.
    Lỗi gọi model (hết lượt, sai key, mất mạng): cứ để exception bay ra — khung ghi lỗi vào cột error.

Chế độ giả (mặc định khi .env chưa có MODEL_PROVIDER, hoặc MODEL_PROVIDER=fake):
    trích đoạn đầu tiên từ ngữ cảnh tìm được, model "fake", token 0 (guide bước 3.2).
    Lượt `run.py eval` / `run.py simulate` chạy bằng model giả KHÔNG được tính.

Nối model thật: điền .env (chép từ .env.example), rồi viết nhánh gọi API ở dưới theo docs/connect-model.md
(có ví dụ OpenAI, Claude, model chạy trên máy, và cách nối nhà cung cấp khác). Không dán API key vào file này.
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

from tracing import model_call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOW_RAW = False  # đổi thành True để in nguyên phản hồi của API khi cần kiểm tra tên trường

URL_OPENAI = "https://api.openai.com/v1/chat/completions"
URL_OPENAI_PROVIDERS = {
    "openai": URL_OPENAI,
    "deepseek": "https://api.deepseek.com/v1/chat/completions",
    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
    "groq": "https://api.groq.com/openai/v1/chat/completions",
}
URL_CLAUDE = "https://api.anthropic.com/v1/messages"
URL_GEMINI = "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent"
URL_OLLAMA = "http://localhost:11434/api/chat"


def load_env(path=os.path.join(ROOT, ".env")):
    """Đọc file .env (KEY=VALUE mỗi dòng) vào biến môi trường, không ghi đè biến đã có. Khung — không cần sửa."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()
MODEL_PROVIDER = (os.environ.get("MODEL_PROVIDER") or "fake").strip().lower()
MODEL_NAME = (os.environ.get("MODEL_NAME") or "").strip()
API_KEY = (os.environ.get("API_KEY") or "").strip()
API_BASE_URL = (os.environ.get("API_BASE_URL") or "").strip()


def post_json(url: str, headers: dict, body: dict, timeout: int = 90, retries: int = 2) -> dict:
    """Gửi POST JSON, trả về JSON phản hồi. Chỉ dùng thư viện chuẩn (urllib), tự thử lại khi 429/503/timeout."""
    payload = json.dumps(body).encode("utf-8")
    req_headers = dict({"Content-Type": "application/json"}, **headers)
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, data=payload, method="POST", headers=req_headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = json.loads(r.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(3 * (attempt + 1))
                continue
            raise RuntimeError("HTTP %d: %s" % (e.code, detail))
        except (TimeoutError, urllib.error.URLError):
            if attempt < retries:
                time.sleep(3 * (attempt + 1))
                continue
            raise
    if SHOW_RAW:
        print(json.dumps(data, ensure_ascii=False, indent=2)[:3000])
    return data


def _require_config(need_key: bool = True):
    if not MODEL_NAME:
        raise RuntimeError("Thiếu MODEL_NAME trong .env (xem docs/connect-model.md).")
    if need_key and not API_KEY:
        raise RuntimeError("Thiếu API_KEY trong .env cho MODEL_PROVIDER=%s." % MODEL_PROVIDER)


def call_openai(system: str, user: str) -> dict:
    """Gọi OpenAI hoặc nhà cung cấp tương thích OpenAI (tuỳ chọn API_BASE_URL trong .env)."""
    _require_config(need_key=True)
    url = API_BASE_URL or URL_OPENAI_PROVIDERS.get(MODEL_PROVIDER, "")
    if not url:
        raise RuntimeError("Thiếu API_BASE_URL trong .env cho MODEL_PROVIDER=%s." % MODEL_PROVIDER)
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
    data = post_json(
        url,
        {"Authorization": "Bearer " + API_KEY},
        {"model": MODEL_NAME, "messages": messages},
    )
    u = data["usage"]
    content = data["choices"][0]["message"].get("content") or ""
    return {
        "text": content,
        "tokens_in": u["prompt_tokens"],
        "tokens_out": u["completion_tokens"],
    }


def call_claude(system: str, user: str) -> dict:
    """Gọi Anthropic Claude Messages API."""
    _require_config(need_key=True)
    url = API_BASE_URL or URL_CLAUDE
    data = post_json(
        url,
        {"x-api-key": API_KEY, "anthropic-version": "2023-06-01"},
        {
            "model": MODEL_NAME,
            "max_tokens": 1024,
            "system": system or "",
            "messages": [{"role": "user", "content": user}],
        },
    )
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    u = data["usage"]
    return {
        "text": text,
        "tokens_in": u["input_tokens"],
        "tokens_out": u["output_tokens"],
    }


def call_gemini(system: str, user: str) -> dict:
    """Gọi Google Gemini REST API (không cần SDK ngoài)."""
    _require_config(need_key=True)
    url = API_BASE_URL or (URL_GEMINI % urllib.parse.quote(MODEL_NAME, safe=""))
    body = {"contents": [{"role": "user", "parts": [{"text": user}]}]}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    data = post_json(url, {"x-goog-api-key": API_KEY}, body)
    candidates = data.get("candidates") or []
    parts = (candidates[0].get("content") or {}).get("parts") or [] if candidates else []
    text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
    u = data["usageMetadata"]
    tokens_in = int(u["promptTokenCount"])
    tokens_out = int(u.get("candidatesTokenCount", 0)) + int(u.get("thoughtsTokenCount", 0))
    return {
        "text": text,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
    }


def call_ollama(system: str, user: str) -> dict:
    """Gọi model chạy nội bộ qua Ollama."""
    _require_config(need_key=False)
    url = API_BASE_URL or URL_OLLAMA
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
    data = post_json(
        url,
        {},
        {"model": MODEL_NAME, "messages": messages, "stream": False},
        timeout=300,
    )
    return {
        "text": data["message"]["content"],
        "tokens_in": data.get("prompt_eval_count", 0),
        "tokens_out": data.get("eval_count", 0),
    }


@model_call
def call_model(system: str, user: str) -> dict:
    if MODEL_PROVIDER == "fake":
        context, separator, _ = user.partition("\n\nCâu hỏi:\n")
        lines = context.splitlines()
        text = "Không có trong bài."
        if separator and len(lines) >= 2 and lines[0] == "Đoạn bài:":
            text = "AI giả · " + lines[1]
        return {"text": text, "model": "fake", "tokens_in": 0, "tokens_out": 0}

    if MODEL_PROVIDER in ("openai", "openai-compatible", "deepseek", "openrouter", "groq"):
        r = call_openai(system, user)
    elif MODEL_PROVIDER in ("anthropic", "claude"):
        r = call_claude(system, user)
    elif MODEL_PROVIDER in ("gemini", "google"):
        r = call_gemini(system, user)
    elif MODEL_PROVIDER == "ollama":
        r = call_ollama(system, user)
    else:
        raise ValueError(
            "Không hỗ trợ MODEL_PROVIDER=%s (hỗ trợ: openai, anthropic, gemini, ollama, fake)."
            % MODEL_PROVIDER
        )
    return {
        "text": r["text"],
        "model": MODEL_NAME,
        "tokens_in": int(r["tokens_in"]),
        "tokens_out": int(r["tokens_out"]),
    }
