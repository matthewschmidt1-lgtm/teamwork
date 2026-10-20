// Accessibility panel shared by the site and the app. Plain script, no modules, so both pages can load it.
// Settings live on <html> as data attributes and in localStorage under teamwork.a11y:
//   data-size 1..5 (text size), data-contrast "high", data-theme "night", data-leading "open", data-motion "reduce".
(function () {
  var KEY = "teamwork.a11y";
  var root = document.documentElement;
  var defaults = { size: 2, contrast: "", theme: "", leading: "", motion: "" };
  var state = load();

  function load() {
    try { return Object.assign({}, defaults, JSON.parse(localStorage.getItem(KEY) || "{}")); } catch (e) { return Object.assign({}, defaults); }
  }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { /* private mode */ } }
  function apply() {
    root.setAttribute("data-size", String(state.size));
    set("data-contrast", state.contrast); set("data-theme", state.theme); set("data-leading", state.leading); set("data-motion", state.motion);
    try { localStorage.setItem("teamwork.theme", state.theme); } catch (e) { /* fine */ }
  }
  function set(attr, val) { if (val) root.setAttribute(attr, val); else root.removeAttribute(attr); }
  apply();

  var T = {
    open: "Display settings", title: "Display", close: "Close",
    size: "Text size", smaller: "Smaller", larger: "Larger",
    contrast: "Contrast", normal: "Normal", high: "High",
    theme: "Colours", paper: "Paper", night: "Night",
    leading: "Line spacing", tight: "Normal", openL: "Open",
    motion: "Motion", moving: "On", still: "Reduced",
    reset: "Reset to defaults",
    note: "Saved in this browser only.",
  };

  function el(tag, attrs, children) {
    var n = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) { if (k === "text") n.textContent = attrs[k]; else n.setAttribute(k, attrs[k]); });
    (children || []).forEach(function (c) { n.appendChild(c); });
    return n;
  }
  function seg(label, options, get, setv) {
    var group = el("div", { class: "a11y-row", role: "group", "aria-label": label });
    group.appendChild(el("span", { class: "a11y-label", text: label }));
    var wrap = el("div", { class: "a11y-seg" });
    options.forEach(function (o) {
      var b = el("button", { type: "button", class: "a11y-opt", "aria-pressed": get() === o.value ? "true" : "false", text: o.label });
      b.addEventListener("click", function () { setv(o.value); apply(); save(); refresh(); });
      wrap.appendChild(b);
    });
    group.appendChild(wrap);
    return group;
  }
  var dialog, trigger;
  function build() {
    dialog = el("dialog", { class: "a11y", "aria-labelledby": "a11yTitle" });
    var head = el("div", { class: "a11y-head" }, [
      el("h2", { id: "a11yTitle", text: T.title }),
      el("button", { type: "button", class: "a11y-close", "aria-label": T.close, text: "×" }),
    ]);
    head.lastChild.addEventListener("click", function () { dialog.close(); });
    dialog.appendChild(head);

    var sizeRow = el("div", { class: "a11y-row", role: "group", "aria-label": T.size });
    sizeRow.appendChild(el("span", { class: "a11y-label", text: T.size }));
    var sizeWrap = el("div", { class: "a11y-seg" });
    var smaller = el("button", { type: "button", class: "a11y-opt", "aria-label": T.smaller, text: "A−" });
    var sample = el("span", { class: "a11y-size", "aria-live": "polite" });
    var larger = el("button", { type: "button", class: "a11y-opt", "aria-label": T.larger, text: "A+" });
    smaller.addEventListener("click", function () { state.size = Math.max(1, state.size - 1); apply(); save(); refresh(); });
    larger.addEventListener("click", function () { state.size = Math.min(5, state.size + 1); apply(); save(); refresh(); });
    sizeWrap.appendChild(smaller); sizeWrap.appendChild(sample); sizeWrap.appendChild(larger);
    sizeRow.appendChild(sizeWrap);
    dialog.appendChild(sizeRow);

    dialog.appendChild(seg(T.contrast, [{ value: "", label: T.normal }, { value: "high", label: T.high }], function () { return state.contrast; }, function (v) { state.contrast = v; }));
    dialog.appendChild(seg(T.theme, [{ value: "", label: T.paper }, { value: "night", label: T.night }], function () { return state.theme; }, function (v) { state.theme = v; }));
    dialog.appendChild(seg(T.leading, [{ value: "", label: T.tight }, { value: "open", label: T.openL }], function () { return state.leading; }, function (v) { state.leading = v; }));
    dialog.appendChild(seg(T.motion, [{ value: "", label: T.moving }, { value: "reduce", label: T.still }], function () { return state.motion; }, function (v) { state.motion = v; }));

    var foot = el("div", { class: "a11y-foot" });
    var reset = el("button", { type: "button", class: "a11y-reset", text: T.reset });
    reset.addEventListener("click", function () { state = Object.assign({}, defaults); apply(); save(); refresh(); });
    foot.appendChild(reset); foot.appendChild(el("span", { class: "a11y-note", text: T.note }));
    dialog.appendChild(foot);
    document.body.appendChild(dialog);
    dialog.addEventListener("click", function (e) { if (e.target === dialog) dialog.close(); });
    dialog.addEventListener("close", function () { if (trigger) trigger.focus(); });
    refresh();
  }
  function refresh() {
    if (!dialog) return;
    var labels = ["Smallest", "Default", "Larger", "Large", "Largest"];
    dialog.querySelector(".a11y-size").textContent = labels[state.size - 1];
    dialog.querySelectorAll(".a11y-row").forEach(function (row) {
      var label = row.getAttribute("aria-label");
      var key = { "Contrast": "contrast", "Colours": "theme", "Line spacing": "leading", "Motion": "motion" }[label];
      if (!key) return;
      var opts = row.querySelectorAll(".a11y-opt");
      var values = key === "contrast" ? ["", "high"] : key === "theme" ? ["", "night"] : key === "leading" ? ["", "open"] : ["", "reduce"];
      opts.forEach(function (b, i) { b.setAttribute("aria-pressed", state[key] === values[i] ? "true" : "false"); });
    });
  }
  function mount() {
    var slot = document.getElementById("a11yButton");
    if (!slot) return;
    trigger = el("button", { type: "button", class: "a11y-trigger", "aria-haspopup": "dialog", "aria-label": T.open, title: T.open, text: "Aa" });
    trigger.addEventListener("click", function () { if (!dialog) build(); if (typeof dialog.showModal === "function") dialog.showModal(); else dialog.setAttribute("open", ""); });
    slot.replaceWith(trigger);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount); else mount();
})();
