"""Kho tối đa 5 API key, xoay vòng và tự chuyển key khi một key bị giới hạn hoặc hỏng.

Key lưu ở logs/api-keys.json (không commit, quyền 600). Trang admin chỉ thấy 4 ký tự cuối.
Kho rỗng hoặc mọi key bị tắt thì dùng API_KEY trong .env như trước. Provider và model vẫn theo .env.
"""
import json
import os
import re
import secrets
import threading
import time

import ai

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE = os.environ.get("KEYS_FILE") or os.path.join(ROOT, "logs", "api-keys.json")
MAX_KEYS = 5
COOLDOWN = {"limit": 60, "bad": 600, "server": 15}
PROVIDERS = ("call_openai", "call_claude", "call_gemini")

_lock = threading.RLock()
_call_lock = threading.Lock()
_turn = 0
_ENV_KEY = ai.API_KEY
_runtime = {}  # id -> {"uses", "fails", "error", "until"}


def _load():
    try:
        with open(STORE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return []


def _write(items):
    os.makedirs(os.path.dirname(STORE), exist_ok=True)
    handle = os.open(STORE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(handle, "w", encoding="utf-8") as f:
        json.dump(items, f)


def _state(key_id):
    return _runtime.setdefault(key_id, {"uses": 0, "fails": 0, "error": "", "until": 0})


def listing():
    now = time.time()
    with _lock:
        items = [{
            "id": k["id"], "label": k["label"], "tail": k["key"][-4:], "enabled": k["enabled"],
            "uses": _state(k["id"])["uses"], "fails": _state(k["id"])["fails"], "error": _state(k["id"])["error"],
            "cooling": max(0, int(_state(k["id"])["until"] - now)),
        } for k in _load()]
    return {"keys": items, "max": MAX_KEYS, "provider": ai.MODEL_PROVIDER, "model": ai.MODEL_NAME,
            "env_key": bool(_ENV_KEY)}


def add(key, label=""):
    key = str(key or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9_\-.]{10,300}", key):
        return {"error": "Key không đúng dạng (10–300 ký tự, không có khoảng trắng)."}
    with _lock:
        items = _load()
        if len(items) >= MAX_KEYS:
            return {"error": "Đã đủ %d key, xoá bớt rồi thêm." % MAX_KEYS}
        if any(k["key"] == key for k in items):
            return {"error": "Key này đã có trong danh sách."}
        items.append({"id": secrets.token_hex(4), "label": str(label or "")[:40], "key": key, "enabled": True})
        _write(items)
    return {"ok": True}


def change(key_id, action):
    """action: delete | enable | disable."""
    with _lock:
        items = _load()
        found = next((k for k in items if k["id"] == key_id), None)
        if not found or action not in ("delete", "enable", "disable"):
            return {"error": "Không thấy key hoặc thao tác không hợp lệ."}
        if action == "delete":
            items.remove(found)
        else:
            found["enabled"] = action == "enable"
        _runtime.pop(key_id, None)
        _write(items)
    return {"ok": True}


def kind_of(error):
    """Loại lỗi đáng đổi key; '' là lỗi mà đổi key không giúp được."""
    text = str(error)
    found = re.match(r"HTTP (\d{3})", text)
    code = int(found.group(1)) if found else 0
    if code == 429:
        return "limit"
    if code in (401, 403) or (code == 400 and "api key" in text.lower()):
        return "bad"
    if code >= 500:
        return "server"
    return ""


def candidates():
    """Các key đang bật, bắt đầu từ lượt kế tiếp; key đang nghỉ xếp cuối."""
    global _turn
    with _lock:
        ready = [k for k in _load() if k["enabled"]]
        if not ready:
            return []
        start = _turn % len(ready)
        _turn += 1
        ready = ready[start:] + ready[:start]
        now = time.time()
        return sorted(ready, key=lambda k: _state(k["id"])["until"] > now)


def _note(key_id, error="", kind=""):
    with _lock:
        state = _state(key_id)
        state["uses"] += 1
        state["error"] = error
        state["until"] = time.time() + COOLDOWN[kind] if kind else 0
        state["fails"] += bool(error)


def _short(error):
    found = re.match(r"HTTP \d{3}", str(error))
    return found.group(0) if found else type(error).__name__


def _rotating(call):
    def wrapped(system, user):
        pool = candidates()
        if not pool:
            return call(system, user)
        last = None
        for item in pool:
            with _call_lock:
                ai.API_KEY = item["key"]
                try:
                    result = call(system, user)
                except Exception as e:
                    kind = kind_of(e)
                    _note(item["id"], _short(e), kind)
                    if not kind:
                        raise
                    last = e
                    continue
                finally:
                    ai.API_KEY = _ENV_KEY
            _note(item["id"])
            return result
        raise last
    return wrapped


def test(key_id):
    """Gọi thử model một lượt bằng đúng key đó."""
    item = next((k for k in _load() if k["id"] == key_id), None)
    call = _ORIGINAL.get({"gemini": "call_gemini", "google": "call_gemini", "anthropic": "call_claude",
                          "claude": "call_claude"}.get(ai.MODEL_PROVIDER, "call_openai"))
    if not item:
        return {"error": "Không thấy key."}
    if ai.MODEL_PROVIDER in ("fake", "ollama"):
        return {"error": "Chế độ %s không dùng API key." % ai.MODEL_PROVIDER}
    with _call_lock:
        ai.API_KEY = item["key"]
        try:
            call("", "Trả lời đúng một chữ: ok")
        except Exception as e:
            _note(item["id"], _short(e), kind_of(e))
            return {"error": "Key …%s gọi không được (%s)." % (item["key"][-4:], _short(e))}
        finally:
            ai.API_KEY = _ENV_KEY
    _note(item["id"])
    return {"ok": True, "message": "Key …%s gọi được." % item["key"][-4:]}


_ORIGINAL = {name: getattr(ai, name) for name in PROVIDERS}
_POST = ai.post_json
_installed = False


def install():
    """Gắn xoay vòng vào ai.py mà không sửa file đó. Gọi một lần khi khởi động máy chủ."""
    global _installed
    if _installed:
        return
    _installed = True

    def post_json(url, headers, body, timeout=90, retries=2):
        # Có key dự phòng thì đổi key ngay, không đứng chờ thử lại trên key đang bị giới hạn.
        spare = len([k for k in _load() if k["enabled"]]) > 1
        return _POST(url, headers, body, timeout=timeout, retries=0 if spare else retries)

    ai.post_json = post_json
    for name in PROVIDERS:
        setattr(ai, name, _rotating(_ORIGINAL[name]))
