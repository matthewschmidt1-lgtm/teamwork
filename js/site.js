// The site's only script: reveal lines as they enter view, light the set piece, and tie the lamp to scroll.
// Without it the page is complete and fully visible.
(function () {
  document.documentElement.classList.add("js");
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Lines arrive as they enter view.
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !reduced) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -12% 0px", threshold: 0.15 });
    reveals.forEach(function (r) { io.observe(r); });
    var sort = document.querySelector(".sort");
    var so = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { sort.classList.add("lit"); so.disconnect(); } });
    }, { threshold: 0.35 });
    if (sort) so.observe(sort);
  } else {
    reveals.forEach(function (r) { r.classList.add("in"); });
    var s = document.querySelector(".sort"); if (s) s.classList.add("lit");
  }

  // The lamp follows scroll: dim at arrival, full at the start section.
  var start = document.getElementById("start");
  var root = document.documentElement;
  var ticking = false;
  function light() {
    ticking = false;
    if (!start) return;
    var end = start.offsetTop - window.innerHeight * 0.5;
    var p = end > 0 ? Math.min(1, Math.max(0, window.scrollY / end)) : 1;
    root.style.setProperty("--progress", p.toFixed(3));
  }
  if (!reduced) {
    window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(light); } }, { passive: true });
    window.addEventListener("resize", light);
    light();
  }
})();
