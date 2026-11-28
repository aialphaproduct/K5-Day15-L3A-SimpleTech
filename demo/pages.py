"""Hai trang tĩnh của bản demo: đăng nhập, và trang bài học tối giản khi không kèm bản preclass offline."""

LOGIN = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Đăng nhập — Simple Tech (demo)</title>
<style>
  * { box-sizing: border-box; }
  body { margin: 0; min-height: 100vh; display: grid; place-items: center; background: #111217; color: #d8d9da;
         font-family: "Helvetica Neue", Arial, sans-serif; padding: 16px; }
  form { width: 100%; max-width: 340px; background: #181b1f; border: 1px solid #2c3235; border-radius: 4px; padding: 24px; }
  h1 { font-size: 1.1rem; margin: 0 0 4px; color: #f4f5f5; }
  p { font-size: .78rem; color: #8e9297; margin: 0 0 16px; }
  label { display: block; font-size: .72rem; text-transform: uppercase; letter-spacing: .05em; color: #8e9297; margin-bottom: 4px; }
  input { width: 100%; padding: 9px 10px; margin-bottom: 12px; background: #111217; color: #f4f5f5; border: 1px solid #2c3235; border-radius: 3px; font-size: .9rem; }
  input:focus { outline: 2px solid #5794f2; }
  button { width: 100%; padding: 10px; background: #5794f2; color: #0b0c0e; border: 0; border-radius: 3px; font-weight: 700; cursor: pointer; }
  #error { color: #f2495c; font-size: .8rem; min-height: 1.2em; margin-top: 10px; }
</style>
</head>
<body>
<form id="form">
  <h1>Trợ giảng Simple Tech</h1>
  <p>Bản demo hackathon, không phải trang pre-class thật.</p>
  <label for="user">Tài khoản</label>
  <input id="user" autocomplete="username" required>
  <label for="password">Mật khẩu</label>
  <input id="password" type="password" autocomplete="current-password" required>
  <button type="submit">Đăng nhập</button>
  <div id="error" role="alert"></div>
</form>
<script>
document.getElementById("form").addEventListener("submit", async e => {
  e.preventDefault();
  const res = await fetch("/login", { method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user: document.getElementById("user").value.trim(), password: document.getElementById("password").value }) });
  const out = await res.json();
  if (res.ok) location.href = out.next; else document.getElementById("error").textContent = out.error;
});
</script>
</body>
</html>
"""

LESSON = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bài 1 — Simple Tech (demo)</title>
<style>
  body { margin: 0; font-family: system-ui, sans-serif; background: #f1f5f9; color: #0f172a; }
  header { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; padding: 12px 16px; background: #fff; border-bottom: 1px solid #e2e8f0; }
  header b { margin-right: auto; } header a { color: #00507a; font-size: 14px; }
  .tag { padding: 4px 10px; border-radius: 999px; background: #fef3c7; border: 1px solid #f59e0b; color: #92400e; font-size: 12px; font-weight: 700; }
  main { max-width: 760px; margin: 0 auto; padding: 16px; }
  #chat { display: flex; flex-direction: column; height: 70vh; min-height: 420px; }
</style>
</head>
<body>
<header><b>Bài 1 · AI và LLM Foundation</b><span class="tag">DEMO VERSION</span><a href="/admin">Đo lường</a><a href="/logout">Đăng xuất</a></header>
<main>
  <p>Hỏi trợ giảng về Bài 1. Bản chạy trên máy chủ không kèm video và tài liệu của khoá.</p>
  <div id="chat"></div>
</main>
<script>
document.addEventListener("st-tutor-ready", () => {
  const host = window.stTutorHost;
  host.style.cssText = "display:flex;flex-direction:column;flex:1;min-height:0;";
  document.getElementById("chat").appendChild(host);
});
</script>
<script src="/st/widget.js" data-embed="1"></script>
</body>
</html>
"""
