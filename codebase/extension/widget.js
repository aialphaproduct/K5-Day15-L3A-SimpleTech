// Widget trợ giảng: nhúng vào trang demo bằng thẻ <script>. Không cài lên trang pre-class thật.
// Widget không đọc nội dung trang chủ; chỉ gửi câu học viên gõ vào ô hỏi.
(function () {
  "use strict";
  if (document.getElementById("st-tutor-host")) return;

  var inExtension = typeof chrome !== "undefined" && !!(chrome.runtime && chrome.runtime.id);
  var script = document.currentScript;
  var base = script && script.src ? new URL(script.src).origin : "";
  // data-embed: không nổi trên trang; trang chủ tự đặt window.stTutorHost vào khung của mình.
  var embed = !!(script && script.dataset.embed);

  // Mã học viên ngẫu nhiên theo trình duyệt, chỉ để trang đo lường biết các lượt của cùng một người.
  function learnerId() {
    var id = "";
    try { id = localStorage.getItem("st-learner") || ""; } catch (e) { /* trình duyệt chặn lưu */ }
    if (!/^HV-[a-z0-9]{2,12}$/.test(id)) {
      id = "HV-" + Math.random().toString(36).slice(2, 8);
      try { localStorage.setItem("st-learner", id); } catch (e) { /* dùng mã tạm */ }
    }
    return id;
  }

  // Lịch sử hỏi lưu riêng trên trình duyệt của học viên (không gửi lên máy chủ) để họ tự tìm lại câu đã hỏi.
  var HISTORY_KEY = "st-history";
  var HISTORY_MAX = 200;

  function loadHistory() {
    try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]"); } catch (e) { return []; }
  }

  function remember(question, at, data) {
    var list = loadHistory();
    // Giữ cả mốc video của đoạn căn cứ để mở lại đúng chỗ từ lịch sử.
    var marks = (data.passages || []).slice(0, 3).filter(function (p) { return p.at; }).map(function (p) { return { code: p.code, at: p.at }; });
    list.push({ q: question, a: String(data.output || ""), at: at || "", marks: marks, time: Date.now() });
    try { localStorage.setItem(HISTORY_KEY, JSON.stringify(list.slice(-HISTORY_MAX))); } catch (e) { /* đầy bộ nhớ hoặc bị chặn */ }
  }

  function clearHistory() {
    try { localStorage.removeItem(HISTORY_KEY); } catch (e) { /* bỏ qua */ }
  }

  function plain(text) {
    return (text || "").normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/đ/gi, "d").toLowerCase();
  }

  function fmtTime(ms) {
    var d = new Date(ms);
    return String(d.getHours()).padStart(2, "0") + ":" + String(d.getMinutes()).padStart(2, "0") + " " +
      String(d.getDate()).padStart(2, "0") + "/" + String(d.getMonth() + 1).padStart(2, "0");
  }

  function ask(text, at) {
    if (inExtension) {
      // Trang https không gọi thẳng được máy local, nên nhờ service worker gọi.
      return chrome.runtime.sendMessage({ type: "ask", text: text }).then(function (r) {
        if (!r || !r.ok) throw new Error("ask failed");
        return r.data;
      });
    }
    return fetch(base + "/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text, at: at || "", learner: learnerId() })
    }).then(function (res) {
      if (!res.ok) throw new Error("HTTP " + res.status);
      return res.json();
    });
  }

  var CSS = [
    ":host { all: initial; }",
    "* { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, 'Segoe UI', sans-serif; }",
    ".fab { position: fixed; right: 20px; bottom: 20px; z-index: 2147483647; background: #2563eb; color: #fff; border: 0;",
    "  border-radius: 999px; padding: 14px 20px; font-size: 14px; font-weight: 600; cursor: pointer; box-shadow: 0 6px 20px rgba(0,0,0,.3); }",
    ".panel { position: fixed; right: 20px; bottom: 80px; z-index: 2147483647; width: 380px; max-width: calc(100vw - 32px);",
    "  height: 520px; max-height: calc(100vh - 110px); display: flex; flex-direction: column; background: #1a1d26; color: #e2e8f0;",
    "  border: 1px solid #2d3148; border-radius: 14px; overflow: hidden; box-shadow: 0 12px 40px rgba(0,0,0,.45); }",
    ".panel[hidden] { display: none; }",
    ".head { display: flex; align-items: center; gap: 8px; padding: 12px 14px; border-bottom: 1px solid #2d3148; }",
    ".head strong { font-size: 14px; } .head span { font-size: 11px; color: #94a3b8; }",
    ".close { margin-left: auto; background: none; border: 0; color: #94a3b8; font-size: 20px; cursor: pointer; line-height: 1; }",
    ".msgs { flex: 1; overflow-y: auto; padding: 14px; display: flex; flex-direction: column; gap: 10px; }",
    ".msgs[hidden], .row[hidden] { display: none; }",
    ".msg { max-width: 88%; padding: 9px 12px; border-radius: 12px; font-size: 14px; line-height: 1.55; white-space: pre-wrap; overflow-wrap: anywhere; }",
    ".bot { align-self: flex-start; background: #252840; } .user { align-self: flex-end; background: #1e40af; color: #fff; }",
    ".none { border: 1px solid #b45309; color: #fbbf24; }",
    ".code { background: #164e63; color: #67e8f9; border: 0; border-radius: 4px; padding: 1px 6px; margin: 0 1px;",
    "  font-family: ui-monospace, Consolas, monospace; font-size: 12px; cursor: pointer; }",
    ".code[aria-expanded='true'] { background: #0e7490; color: #fff; }",
    ".passage { display: block; margin-top: 8px; padding: 8px 10px; border-left: 3px solid #22d3ee; background: #0f2530;",
    "  border-radius: 0 6px 6px 0; font-size: 13px; }",
    ".passage b { display: block; font-size: 11px; color: #67e8f9; margin-bottom: 2px; }",
    ".basis { display: block; margin-top: 10px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; opacity: .7; }",
    ".passage.flash { outline: 3px solid #f59e0b; }",
    ".seek { display: block; margin-top: 8px; background: #14532d; color: #bbf7d0; border: 1px solid #22c55e; border-radius: 8px;",
    "  padding: 6px 10px; font-size: 13px; cursor: pointer; text-align: left; }",
    ".when { display: block; margin-top: 4px; font-size: 11px; opacity: .75; }",
    ".row { display: flex; gap: 8px; padding: 10px; border-top: 1px solid #2d3148; }",
    ".row input { flex: 1; min-width: 0; background: #252840; border: 1px solid #2d3148; border-radius: 8px; padding: 9px 12px; color: #e2e8f0; font-size: 14px; }",
    ".row input:focus, .fab:focus-visible, .code:focus-visible { outline: 2px solid #60a5fa; outline-offset: 1px; }",
    ".row button { background: #2563eb; border: 0; border-radius: 8px; color: #fff; padding: 9px 14px; font-size: 14px; cursor: pointer; }",
    ".row button:disabled { background: #334155; cursor: default; }",
    ".embed.fab, .embed .close { display: none; }",
    ".embed.panel { position: static; width: 100%; max-width: none; height: 100%; max-height: none; flex: 1; min-height: 0; border-radius: 10px; box-shadow: none;",
    "  background: #fff; color: #1f2937; border-color: #e5e7eb; }",
    // Giao diện sáng khi đặt trong khung trao đổi của trang chủ.
    ".embed .head { border-color: #e5e7eb; } .embed .head strong { color: #0b3a5b; font-size: 15px; } .embed .head span { color: #64748b; }",
    ".embed .bot { background: #f1f5f9; } .embed .user { background: #00507a; }",
    ".embed .none { background: #fffbeb; border-color: #f59e0b; color: #92400e; }",
    ".embed .code { background: #e0f2fe; color: #075985; } .embed .code[aria-expanded='true'] { background: #075985; color: #fff; }",
    ".embed .passage { background: #f0f9ff; border-color: #0284c7; color: #1f2937; } .embed .passage b { color: #075985; }",
    ".embed .seek { background: #ecfdf5; color: #065f46; border-color: #6ee7b7; }",
    ".embed .row { border-color: #e5e7eb; } .embed .row input { background: #f4f4f5; border-color: #e5e7eb; color: #111827; }",
    ".embed .row button { background: #00507a; } .embed .row button:disabled { background: #94a3b8; }",
    ".mentions { display: flex; padding: 8px 10px 0; } .mentions[hidden] { display: none; }",
    ".mentions button { background: #f0fdf9; border: 2px solid #99d5c9; border-radius: 999px; padding: 6px 12px; font-size: 13px; color: #475569; cursor: pointer; }",
    ".mentions b { color: #065f46; margin-right: 6px; }",
    ".note { padding: 0 12px 8px; font-size: 11px; color: #64748b; }",
    ".hist-btn { background: none; border: 1px solid #2d3148; border-radius: 6px; color: #94a3b8; font-size: 12px; padding: 5px 10px; cursor: pointer; }",
    ".hist-btn[aria-pressed='true'] { background: #252840; color: #e2e8f0; }",
    ".history[hidden] { display: none; }",
    ".history { flex: 1; overflow-y: auto; padding: 10px 14px; display: flex; flex-direction: column; gap: 8px; }",
    ".history .search { padding: 9px 12px; border-radius: 8px; border: 1px solid #2d3148; background: #252840; color: #e2e8f0; font-size: 13px; }",
    ".history .empty { font-size: 13px; color: #94a3b8; padding: 6px 2px; }",
    ".hitem { border: 1px solid #2d3148; border-radius: 10px; padding: 8px 10px; background: #1e2130; }",
    ".hitem .htime { font-size: 11px; color: #64748b; display: block; margin-bottom: 3px; }",
    ".hitem .hq { font-size: 13px; font-weight: 600; }",
    ".hitem .ha { font-size: 12px; color: #cbd5e1; margin-top: 4px; white-space: pre-wrap; }",
    ".history > * { flex-shrink: 0; } .hlist { display: flex; flex-direction: column; gap: 8px; }",
    ".hagain { align-self: flex-start; margin: 6px 6px 0 0; background: none; border: 1px solid #334155; border-radius: 6px; color: #93c5fd; font-size: 12px; padding: 4px 9px; cursor: pointer; }",
    ".embed .hist-btn { border-color: #cbd5e1; color: #475569; } .embed .hist-btn[aria-pressed='true'] { background: #e5e7eb; color: #111827; }",
    ".embed .history .search { background: #f4f4f5; border-color: #e5e7eb; color: #111827; }",
    ".embed .hitem { background: #f8fafc; border-color: #e5e7eb; } .embed .hitem .ha { color: #334155; }",
    ".embed .hagain { color: #00507a; border-color: #94a3b8; }"
  ].join("\n");

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  var host = el("div");
  host.id = "st-tutor-host";
  var root = host.attachShadow({ mode: "open" });
  root.appendChild(el("style", "", CSS));

  var fab = el("button", "fab", "Hỏi trợ giảng");
  fab.type = "button";
  fab.setAttribute("aria-expanded", "false");

  var panel = el("section", "panel");
  panel.hidden = true;
  panel.setAttribute("aria-label", "Trợ giảng AI");

  var head = el("div", "head");
  var histBtn = el("button", "hist-btn", "Lịch sử");
  histBtn.type = "button";
  histBtn.setAttribute("aria-pressed", "false");
  histBtn.title = "Xem lại các câu bạn đã hỏi trên trình duyệt này";
  var close = el("button", "close", "×");
  close.type = "button";
  close.setAttribute("aria-label", "Đóng");
  head.append(
    el("strong", "", embed ? "Trao đổi" : "Trợ giảng AI"),
    el("span", "", embed ? "với trợ giảng Simple Tech (bản demo)" : "bản thử của nhóm Simple Tech"),
    histBtn,
    close
  );

  var msgs = el("div", "msgs");
  msgs.setAttribute("aria-live", "polite");

  // Mục lịch sử: chỉ đọc trên máy học viên, không gửi lên máy chủ; có ô tìm để tự tìm lại câu đã hỏi.
  var history = el("div", "history");
  history.hidden = true;
  var search = el("input", "search");
  search.type = "search";
  search.placeholder = "Tìm trong câu bạn đã hỏi…";
  search.setAttribute("aria-label", "Tìm trong lịch sử hỏi");
  var histList = el("div", "hlist");
  var clearBtn = el("button", "hagain", "Xoá lịch sử trên máy này");
  clearBtn.type = "button";
  history.append(search, histList, clearBtn);

  function renderHistory() {
    var q = plain(search.value.trim());
    var list = loadHistory().slice().reverse();
    if (q) list = list.filter(function (h) { return plain(h.q).indexOf(q) !== -1 || plain(h.a).indexOf(q) !== -1; });
    histList.replaceChildren();
    if (!list.length) {
      histList.appendChild(el("div", "empty", loadHistory().length ? "Không thấy câu nào khớp." : "Bạn chưa hỏi câu nào trên trình duyệt này."));
      return;
    }
    list.forEach(function (h) {
      var item = el("div", "hitem");
      item.append(el("span", "htime", fmtTime(h.time) + (h.at ? " · hỏi tại " + h.at : "")), el("div", "hq", h.q));
      if (h.a) item.appendChild(el("div", "ha", h.a.length > 220 ? h.a.slice(0, 220) + "…" : h.a));
      (window.stTutorVideo ? h.marks || [] : []).forEach(function (m) {
        var go = el("button", "hagain", "Mở video " + m.at.label + " (" + m.code + ")");
        go.type = "button";
        go.addEventListener("click", function () {
          if (!window.stTutorVideo.seek(m.at.seconds)) go.textContent = "Đợi video tải xong rồi bấm lại (" + m.at.label + ")";
        });
        item.appendChild(go);
      });
      var again = el("button", "hagain", "Hỏi lại câu này");
      again.type = "button";
      again.addEventListener("click", function () {
        input.value = h.q;
        toggleHistory(false);
        input.focus();
      });
      item.appendChild(again);
      histList.appendChild(item);
    });
  }

  function toggleHistory(show) {
    history.hidden = !show;
    msgs.hidden = show;
    form.hidden = show;
    histBtn.setAttribute("aria-pressed", String(show));
    histBtn.textContent = show ? "Trò chuyện" : "Lịch sử";
    if (show) { renderHistory(); search.focus(); }
  }

  histBtn.addEventListener("click", function () { toggleHistory(history.hidden); });
  search.addEventListener("input", renderHistory);
  clearBtn.addEventListener("click", function () {
    if (!window.confirm("Xoá toàn bộ lịch sử hỏi trên trình duyệt này?")) return;
    clearHistory();
    renderHistory();
  });

  var form = el("form", "row");
  var input = el("input");
  input.type = "text";
  input.maxLength = 2000;
  input.placeholder = "Hỏi về nội dung bài học…";
  input.setAttribute("aria-label", "Câu hỏi");
  var send = el("button", "", "Gửi");
  send.type = "submit";
  form.append(input, send);

  panel.append(head, msgs, history, form);

  // Gõ @ trong khung trao đổi thì gợi ý gọi trợ giảng; chỉ có một trợ giảng là SimpleTech.
  var MENTION = /@simple\s?tech/gi;
  var TYPING = /(^|\s)@([A-Za-z]*)$/;
  var mentions = el("div", "mentions");
  mentions.hidden = true;
  var option = el("button");
  option.type = "button";
  option.append(el("b", "", "@SimpleTech"), "Trợ giảng Simple Tech");
  mentions.appendChild(option);

  function pickMention() {
    input.value = input.value.replace(TYPING, "$1@SimpleTech ");
    mentions.hidden = true;
    input.focus();
  }

  if (embed) {
    input.placeholder = "Hỏi hoặc trao đổi… gõ @ để gọi trợ giảng";
    panel.insertBefore(mentions, form);
    panel.appendChild(el("div", "note", "Câu trả lời kèm mã đoạn bài để bạn tự kiểm."));
    option.addEventListener("click", pickMention);
    input.addEventListener("input", function () {
      var typing = TYPING.exec(input.value);
      mentions.hidden = !(typing && "simpletech".indexOf(typing[2].toLowerCase()) === 0);
    });
    input.addEventListener("keydown", function (e) {
      if (mentions.hidden || (e.key !== "Enter" && e.key !== "Tab")) return;
      e.preventDefault();
      pickMention();
    });
    fab.classList.add("embed");
    panel.classList.add("embed");
    panel.hidden = false;
  }
  root.append(fab, panel);

  function add(cls, text) {
    var node = el("div", "msg " + cls, text);
    msgs.appendChild(node);
    msgs.scrollTop = msgs.scrollHeight;
    return node;
  }

  // Chỉ dựng bằng textContent: câu trả lời của model không bao giờ thành HTML.
  function render(bubble, data) {
    var output = String(data.output || "Không có phản hồi.");
    var passages = {};
    (data.passages || []).forEach(function (p) { passages[p.code] = p.text; });
    bubble.textContent = "";
    if (output.indexOf("Không có trong bài") === 0) bubble.classList.add("none");

    // Căn cứ hiện sẵn dưới câu trả lời để học viên kiểm ngay, không phải đi tìm.
    var cards = {};
    var video = window.stTutorVideo;

    function seekButton(label, mark) {
      var go = el("button", "seek", label);
      go.type = "button";
      go.addEventListener("click", function () {
        if (!video.seek(mark.seconds)) go.textContent = "Chưa tua được, đợi video tải xong rồi bấm lại (" + mark.label + ")";
      });
      return go;
    }

    output.split(/\[([A-Za-z0-9\-]+)\]/).forEach(function (part, i) {
      if (i % 2 === 0) { bubble.append(part); return; }
      if (!Object.prototype.hasOwnProperty.call(passages, part)) { bubble.append("[" + part + "]"); return; }
      var chip = el("button", "code", "[" + part + "]");
      chip.type = "button";
      chip.title = "Chỉ tới đoạn căn cứ";
      chip.addEventListener("click", function () {
        var card = cards[part];
        card.classList.add("flash");
        card.scrollIntoView({ block: "nearest" });
        setTimeout(function () { card.classList.remove("flash"); }, 1500);
      });
      bubble.appendChild(chip);
    });

    var shown = (data.passages || []).slice(0, 3);
    if (shown.length) bubble.appendChild(el("span", "basis", "Căn cứ để bạn kiểm"));
    shown.forEach(function (p) {
      var card = el("span", "passage");
      card.append(el("b", "", "Đoạn " + p.code + (p.at ? " · video " + p.at.label : "")), p.text);
      if (video && p.at) card.appendChild(seekButton("▶ Mở đúng chỗ trong video (" + p.at.label + ")", p.at));
      cards[p.code] = card;
      bubble.appendChild(card);
    });

    // Mốc gợi ý theo chủ đề chỉ hiện khi không đoạn trích nào đã có mốc.
    if (!video || shown.some(function (p) { return p.at; })) return;
    (data.video || []).forEach(function (mark) {
      bubble.appendChild(seekButton((mark.suggested ? "▶ Gợi ý: video có thể nói ở " : "▶ Xem đoạn này trong video: ") + mark.label, mark));
    });
  }

  function toggle(show) {
    panel.hidden = !show;
    fab.setAttribute("aria-expanded", String(show));
    if (show) input.focus(); else fab.focus();
  }

  fab.addEventListener("click", function () { toggle(panel.hidden); });
  close.addEventListener("click", function () { toggle(false); });
  // Không để phím gõ trong widget kích hoạt phím tắt của trình phát video trên trang.
  ["keydown", "keyup", "keypress"].forEach(function (type) {
    host.addEventListener(type, function (e) {
      if (type === "keydown" && e.key === "Escape" && !embed) toggle(false);
      e.stopPropagation();
    });
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var text = input.value.trim();
    if (!text || send.disabled) return;
    input.value = "";
    send.disabled = true;
    var mine = add("user", text);
    var at = window.stTutorVideo && window.stTutorVideo.now();
    if (at) mine.appendChild(el("span", "when", "Hỏi tại " + at));
    var bubble = add("bot", "Đang tra bài…");
    mentions.hidden = true;
    // Không gửi phần gọi tên đi: nó làm lệch việc tra đoạn bài.
    var question = text.replace(MENTION, " ").replace(/\s+/g, " ").trim() || "chào bạn";
    ask(question, at)
      .then(function (data) { render(bubble, data); remember(question, at, data); })
      .catch(function () {
        bubble.classList.add("none");
        bubble.textContent = "Không gọi được trợ giảng. Kiểm tra máy chủ đang chạy rồi thử lại.";
      })
      .finally(function () {
        send.disabled = false;
        msgs.scrollTop = msgs.scrollHeight;
        input.focus();
      });
  });

  add("bot", "Bạn hỏi về nội dung bài học nhé. Câu trả lời kèm mã đoạn; bấm vào mã để xem đoạn bài và tự kiểm.");
  if (embed) {
    window.stTutorHost = host;
    document.dispatchEvent(new Event("st-tutor-ready"));
  } else {
    document.documentElement.appendChild(host);
  }
})();
