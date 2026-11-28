// Chạy trước ứng dụng preclass: tạo phiên đăng nhập giả trên bản offline.
(function () {
  "use strict";
  window.__PC_CUSTOM = [];
  try {
    var token = localStorage.getItem("vlearn.accessToken");
    var check = new XMLHttpRequest();
    check.open("GET", "/api/auth/me", false);
    if (token) check.setRequestHeader("Authorization", "Bearer " + token);
    check.send();
    if (check.status === 200) return;
    var login = new XMLHttpRequest();
    login.open("POST", "/api/auth/login", false);
    login.setRequestHeader("Content-Type", "application/json");
    login.send(JSON.stringify({ email: "demo.hocvien@preclass.local", password: "demo" }));
    var data = JSON.parse(login.responseText).data;
    localStorage.setItem("vlearn.accessToken", data.access_token);
    localStorage.setItem("vlearn.user", JSON.stringify(data.user));
  } catch (e) {
    console.error("Không tạo được phiên demo", e);
  }
})();

// Cho widget đọc thời gian và tua trình phát bài giảng (nằm trong iframe cùng nguồn).
(function () {
  "use strict";
  function player() {
    var frame = document.querySelector("iframe");
    return frame && frame.contentWindow && frame.contentWindow.VinTutor;
  }
  window.stTutorVideo = {
    now: function () {
      var t = player();
      var cue = t && t.cues[t.index];
      if (!cue) return "";
      var s = Math.floor((cue.start || 0) / 1000);
      return String(Math.floor(s / 60)).padStart(2, "0") + ":" + String(s % 60).padStart(2, "0");
    },
    seek: function (seconds) {
      var t = player();
      if (!t || !t.cues.length) return false;
      // Giờ câu thoại trong slide lệch vài giây so với mốc lời giảng nên chọn câu bắt đầu gần mốc nhất.
      var index = 0;
      var gap = function (i) { return Math.abs((t.cues[i].start || 0) - seconds * 1000); };
      t.cues.forEach(function (cue, i) { if (gap(i) < gap(index)) index = i; });
      t.cue(index, true);
      t.play();
      return true;
    }
  };
})();

// Giao diện demo: khung "Tương tác lớp học" chỉ còn trợ giảng Simple Tech, ẩn các tính năng khác của preclass.
(function () {
  "use strict";
  var style = document.createElement("style");
  style.textContent = [
    // Nhãn nói rõ đây không phải trang thật.
    ".site-header .header-start::after { content: 'DEMO VERSION · Tham khảo giao diện Preclass'; margin-left: 12px; padding: 4px 10px;",
    "  border-radius: 999px; background: #fef3c7; border: 1px solid #f59e0b; color: #92400e; font: 700 12px system-ui, sans-serif; }",
    ".site-header a:not(.st-admin), .site-header [class*='brand'] { pointer-events: none; }",
    ".st-admin { margin-left: auto; align-self: center; padding: 6px 12px; border-radius: 8px; border: 1px solid #8e48ff; background: #8e48ff1f; color: #6d28d9;",
    "  font: 600 13px system-ui, sans-serif; text-decoration: none; }",
    // Ẩn: menu, thông báo, giao diện tối, tài khoản, dải lớp học trực tiếp, chuyển phần, hỏi tutor khi bôi đen, câu hỏi giữa video.
    "button.guide-toggle, .site-guide, .header-actions, .live-banner, .next-item-button, .deck-ask-tutor,",
    ".deck-module-end > span, .deck-module-end-actions .is-primary, .quiz-tutor-offer, .lesson-checkpoint { display: none !important; }",
    ".discussion-card > :not(#st-tutor-host):not(.chat-resize-grip) { display: none !important; }"
  ].join("\n");

  function mount() {
    if (!style.isConnected) document.head.appendChild(style);
    var header = document.querySelector(".site-header .header-inner");
    if (header && !header.querySelector(".st-admin")) {
      var link = document.createElement("a");
      link.className = "st-admin";
      link.href = "/admin";
      link.target = "_blank";
      link.rel = "noopener";
      link.textContent = "Đo lường";
      header.appendChild(link);
    }
    var card = document.querySelector(".discussion-card");
    var host = window.stTutorHost;
    if (!card || !host || host.parentNode === card) return;
    host.style.cssText = "display:flex;flex-direction:column;flex:1 1 0;min-height:360px;";
    card.appendChild(host);
  }

  document.addEventListener("st-tutor-ready", mount);
  document.addEventListener("DOMContentLoaded", function () {
    document.title = "Demo Version · Simple Tech";
    // React dựng lại khung khi đổi trang nên gắn lại mỗi khi cây DOM đổi.
    new MutationObserver(mount).observe(document.body, { childList: true, subtree: true });
    mount();
  });
})();

// Bỏ câu hỏi giữa video, mini lab và ôn tập của bài.
(function () {
  "use strict";
  var catalog = window.__pcFE;
  window.__pcFE = function (days) {
    return (catalog ? catalog(days) : days).map(function (d) {
      if (d.parentId !== "program-day01:ai-llm-foundation" || !d.deck) return d;
      return Object.assign({}, d, { labs: [], deck: Object.assign({}, d.deck, { quizKey: null }) });
    });
  };
})();
