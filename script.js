/* ============================================================
   个人主页 · 交互脚本 —— 纯 vanilla，无依赖
   移动端菜单 / 滚动入场 / 深浅主题（localStorage 记忆）
   ============================================================ */

(function () {
  "use strict";

  var prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- 移动端菜单 ---------- */
  var toggle = document.getElementById("navToggle");
  var menu = document.getElementById("navMenu");

  if (toggle && menu) {
    toggle.addEventListener("click", function () {
      var open = menu.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "关闭菜单" : "打开菜单");
    });
    // 点导航项后自动收起
    menu.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        menu.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* ---------- 滚动入场（.reveal → .in） ---------- */
  var reveals = document.querySelectorAll(".reveal");

  if ("IntersectionObserver" in window && !prefersReduced) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });

    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }
  /* 说明：素净水墨定调后去掉了深浅切换按钮；夜墨变量仍留在 CSS 里，
     以后想开回来，把 <html> 的 data-theme 改成 "dark" 即可。 */
})();
