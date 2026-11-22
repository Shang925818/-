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
    var mq = window.matchMedia("(max-width: 720px)");

    // 只有窄屏收起时才真正禁用（inert）；宽屏下这个菜单就是普通导航
    function apply(open) {
      var mobile = mq.matches;
      var expanded = mobile && open;
      menu.classList.toggle("open", expanded);
      menu.inert = mobile && !expanded;
      toggle.setAttribute("aria-expanded", expanded ? "true" : "false");
      toggle.setAttribute("aria-label", expanded ? "关闭菜单" : "打开菜单");
    }

    apply(false);

    toggle.addEventListener("click", function () {
      apply(!menu.classList.contains("open"));
    });

    // Esc 收起并把焦点还给按钮
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menu.classList.contains("open")) {
        apply(false);
        toggle.focus();
      }
    });

    // 点导航项后自动收起
    menu.addEventListener("click", function (e) {
      if (e.target.closest("a")) apply(false);
    });

    // 视口跨过断点时复位，避免宽屏残留 inert
    var onMQ = function () { apply(false); };
    if (mq.addEventListener) mq.addEventListener("change", onMQ);
    else if (mq.addListener) mq.addListener(onMQ);
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
  /* ---------- 悬浮回到目录 ---------- */
  var backToWork = document.getElementById("backToWork");
  var workSection = document.getElementById("work");

  if (backToWork && workSection) {
    backToWork.hidden = false;   // 样式已生效，可以露面了
    var ticking = false;
    function updateFloat() {
      var y = window.scrollY || window.pageYOffset;
      var start = workSection.offsetTop - 200;
      backToWork.classList.toggle("is-on", y > start);
      ticking = false;
    }
    window.addEventListener("scroll", function () {
      if (!ticking) {
        ticking = true;
        window.requestAnimationFrame(updateFloat);
      }
    }, { passive: true });
    updateFloat();
  }

  /* 说明：素净水墨定调后去掉了深浅切换按钮；夜墨变量仍留在 CSS 里，
     以后想开回来，把 <html> 的 data-theme 改成 "dark" 即可。 */
})();
