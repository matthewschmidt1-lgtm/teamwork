// The site's only script: reveal lines as they enter view and colour the set piece when it arrives.
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

})();
