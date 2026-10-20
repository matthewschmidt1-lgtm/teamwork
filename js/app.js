// Teamwork. One question per screen. The protocol runs on the server; the person stays in control here.
import { COPY } from "./content.js";
import * as store from "./store.js";
import { pageText, icsFor, moveLine, cleanSorted, addDays, fmtDate, todayISO, composeAccount } from "./text.js";
import { step as callStep, payload, AdvisorError } from "./api.js";

const app = document.getElementById("app");
const status = document.getElementById("status");
const wick = document.getElementById("wick");
let s = null;            // the current situation

document.getElementById("privacy").textContent = COPY.privacy;

// ---------- Theme: night by default, paper as the alternate ----------
const themeBtn = document.getElementById("theme");
function themeName() { return document.documentElement.getAttribute("data-theme") === "paper" ? "paper" : "night"; }
function paintTheme() { themeBtn.textContent = COPY.theme[themeName()]; }
themeBtn.addEventListener("click", () => {
  const next = themeName() === "paper" ? "night" : "paper";
  if (next === "paper") document.documentElement.setAttribute("data-theme", "paper"); else document.documentElement.removeAttribute("data-theme");
  try { localStorage.setItem("teamwork.theme", next === "paper" ? "paper" : ""); } catch (e) { /* fine */ }
  paintTheme();
});
paintTheme();

// ---------- Tiny element builder ----------
function el(spec, attrs, ...children) {
  const [tag, ...classes] = spec.split(".");
  const node = document.createElement(tag || "div");
  if (classes.length) node.className = classes.join(" ");
  if (attrs) for (const [k, v] of Object.entries(attrs)) {
    if (k === "on") for (const [ev, fn] of Object.entries(v)) node.addEventListener(ev, fn);
    else if (v === true) node.setAttribute(k, "");
    else if (v !== false && v != null) node.setAttribute(k, v);
  }
  for (const c of children.flat()) if (c != null && c !== false) node.append(c.nodeType ? c : document.createTextNode(String(c)));
  return node;
}
const btn = (label, cls, on, attrs) => el("button." + cls, Object.assign({ type: "button", on: { click: on } }, attrs || {}), label);
const label = (text, tone) => el("p.label" + (tone ? "." + tone : ""), null, text);
const fold = (summary, ...inner) => el("details", null, el("summary", null, summary), el("div.inner", null, ...inner));

function show(node, focusSel, keepScroll) {
  const y = window.scrollY;
  app.replaceChildren(node);
  if (keepScroll) { window.scrollTo(0, y); return; }
  node.classList.add("screen");
  const f = focusSel ? app.querySelector(focusSel) : app.querySelector("h1");
  if (f) { if (!f.hasAttribute("tabindex")) f.setAttribute("tabindex", "-1"); f.focus({ preventScroll: true }); }
  window.scrollTo(0, 0);
}
function say(text) { status.textContent = text; }
function persist() { if (s) store.upsert(s); }
function stopAndSave() { persist(); s = null; home(); }
function lit(n) { // the wick: three dots that fill during the opening
  wick.replaceChildren();
  if (n == null) return;
  for (let i = 0; i < 3; i++) wick.append(el("i" + (i < n ? ".lit" : "")));
}
function nav(backFn, extra, pinned) {
  const row = el("div.actions" + (pinned ? ".pinned" : ""));
  if (backFn) row.append(btn(COPY.nav.back, "secondary", backFn));
  if (extra) row.append(...extra);
  row.append(el("span.spacer"), btn(COPY.nav.stop, "link", stopAndSave));
  return row;
}

// ---------- Loading and errors ----------
async function withAdvisor(kind, fn, retry) {
  document.body.dataset.thinking = "1";
  show(el("div", null, el("h1.visually-hidden", null, COPY.loading[kind]), el("p.thinking", null, el("span.dot"), COPY.loading[kind])), ".thinking");
  say(COPY.loading[kind]);
  try {
    const result = await fn();
    delete document.body.dataset.thinking;
    return result;
  } catch (e) {
    delete document.body.dataset.thinking;
    const msg = (e instanceof AdvisorError && e.message) || COPY.error.generic;
    const node = el("div.error", null, el("h1", null, COPY.error.title), el("p", null, msg));
    if (e instanceof AdvisorError && e.declined) node.append(btn(COPY.post.exits.conduct, "secondary", () => conduct()));
    node.append(el("div.actions", null, btn(COPY.error.retry, "primary", retry), btn(COPY.error.later, "link", stopAndSave)));
    show(node);
    say(msg);
    return null;
  }
}

// ---------- Home: three taps, then an optional line ----------
let draft = { who: null, what: null, need: null, detail: "" };
const STEPS = ["who", "what", "need"];

function home() {
  draft = { who: null, what: null, need: null, detail: "" };
  delete document.body.dataset.lit;
  const pre = new URLSearchParams(location.search).get("who");
  const match = pre && COPY.home.who.options.find(([k]) => k === pre);
  if (match) {
    history.replaceState(null, "", location.pathname);
    draft.who = match[0]; draft.whoLabel = match[1];
    return homeStep(1);
  }
  homeStep(0);
}
function rows(options, chosen, onPick, quietKeys) {
  const quiet = new Set(quietKeys || []);
  const main = el("ul.rows");
  const soft = el("ul.rows.quiet-rows");
  options.forEach(([key, text]) => {
    const b = btn(text, "row", () => onPick(key, text), { "aria-pressed": chosen === key ? "true" : "false" });
    (quiet.has(key) ? soft : main).append(el("li", null, b));
  });
  return quiet.size ? [main, soft] : [main];
}
function homeStep(i) {
  const key = STEPS[i]; const C = COPY.home[key];
  lit(i);
  const node = el("div", null, el("h1", null, C.title),
    ...rows(C.options, draft[key], (k, text) => {
      draft[key] = k; draft[key + "Label"] = text;
      if (key === "what" && k === "conduct") return startConduct();
      if (i < 2) homeStep(i + 1); else homeDetail();
    }, C.quiet));
  if (i > 0) node.append(el("div.actions", null, btn(COPY.nav.back, "secondary", () => homeStep(i - 1))));
  if (i === 0) homeLists(node);
  show(node);
}
function homeDetail() {
  const C = COPY.home.detail;
  lit(3);
  const ta = el("textarea.yours", { id: "detail", rows: 3, placeholder: C.placeholder, "aria-labelledby": "detailLabel", "aria-describedby": "detailHelp" }, draft.detail || "");
  const start = (skip) => {
    draft.detail = skip ? "" : ta.value.trim();
    const labels = { who: draft.whoLabel, what: draft.whatLabel, need: draft.needLabel };
    s = { id: store.newId(), created: new Date().toISOString(), choices: { who: draft.who, what: draft.what, need: draft.need, labels }, detail: draft.detail, account: composeAccount(labels, draft.detail) };
    persist();
    reflect();
  };
  show(el("div", null, el("h1", { id: "detailLabel" }, C.title), el("p.help", { id: "detailHelp" }, C.help),
    el("div.field", null, ta),
    el("div.actions.pinned", null, btn(COPY.nav.back, "secondary", () => homeStep(2)), btn(C.go, "primary", () => start(false)), btn(C.skip, "link", () => start(true)))), "#detail");
}
function startConduct() {
  const labels = { who: draft.whoLabel, what: draft.whatLabel, need: null };
  s = { id: store.newId(), created: new Date().toISOString(), choices: { who: draft.who, what: draft.what, need: null, labels }, detail: "", account: composeAccount(labels, ""), conduct: true, safety: true };
  persist();
  conduct();
}
function homeLists(node) {
  const list = store.load().situations;
  const unfinished = store.unfinished(list);
  const due = store.dueForLookback(list);
  const open = store.openOnes(list);
  if (unfinished.length) {
    node.append(el("section", null, label(COPY.home.openTitle)));
    unfinished.slice(0, 3).forEach((u) => node.append(card(u, btn(COPY.home.continueOne, "secondary", () => { s = u; resume(); }))));
  }
  if (due.length) {
    node.append(el("section", null, label(COPY.home.dueTitle)));
    due.forEach((d) => node.append(card(d, btn(COPY.home.lookBack, "primary", () => lookback(d)), fmtDate(d.post.date))));
  }
  if (open.length) {
    node.append(el("section", null, label(COPY.home.openTitle)));
    open.forEach((o) => node.append(card(o, btn(COPY.home.lookBackEarly, "secondary", () => lookback(o)), COPY.page.by + " " + fmtDate(o.post.date))));
  }
  const r = store.record(list);
  if (r.looked) {
    node.append(el("section", null, label(COPY.home.recordTitle), el("div.record", null,
      stat(r.thought, COPY.record.situations), stat(r.looked, COPY.record.lookbacks), stat(r.matched, COPY.record.matched), stat(r.lessons, COPY.record.lessons)),
      el("p.quiet", null, COPY.home.recordNote)));
  }
  if (list.length) node.append(el("div.actions", null, btn(COPY.home.deleteAll, "link", () => { if (confirm(COPY.home.deleteAllConfirm)) { store.clearAll(); home(); } })));
}
const stat = (n, l) => el("div", null, el("span.n", null, String(n)), el("span.l", null, l));
function card(sit, action, meta) {
  const first = (sit.post && sit.post.sentence) || sit.account;
  return el("div.card", null, el("div.what", null, el("p.yours", null, first.length > 110 ? first.slice(0, 107) + "..." : first), meta ? el("p.quiet", null, meta) : null), action);
}
function resume() {
  lit(null);
  if (!s.sorted) return reflect();
  if (s.conduct) return conduct();
  if (!s.read) return want();
  if (!s.post) return read();
  return post(true);
}

// ---------- Reflect: confirm only, act on a line by tapping it ----------
async function reflect() {
  lit(null);
  if (!s.sorted) {
    const r = await withAdvisor("reflect", () => callStep("reflect", payload(s)), reflect);
    if (!r) return;
    s.sorted = cleanSorted(r);
    s.echo = r.echo;
    s.safety = r.safety_flag ? (r.safety_kind || true) : false;
    persist();
    if (r.safety_flag) { s.conduct = true; persist(); return conduct(); }
  }
  renderReflect();
}
let openLine = null; // "happened:2" while a line's actions are shown
let reflectShown = false;
function renderReflect() {
  const C = COPY.reflect;
  const keep = reflectShown && app.querySelector(".block") != null;
  reflectShown = true;
  const node = el("div", null, el("h1", null, C.title), s.echo ? el("p", null, s.echo) : null, el("p.help", null, C.tapHint));
  ["happened", "told", "concluded"].forEach((key) => {
    const block = el("section.block." + key, null, label(C[key], key === "happened" ? "sage" : key === "concluded" ? "rose" : null));
    const list = el("ul.lines");
    s.sorted[key].forEach((line, i) => {
      const id = key + ":" + i;
      const li = el("li");
      if (openLine === id + ":edit") {
        const input = el("input", { type: "text", value: line, "aria-label": C.edit });
        const finish = () => { s.sorted[key][i] = input.value; s.sorted = cleanSorted(s.sorted); openLine = null; persist(); renderReflect(); };
        input.addEventListener("keydown", (e) => { if (e.key === "Enter") finish(); });
        li.append(input, el("div.line-actions", null, btn(C.done, "chip", finish)));
        list.append(li);
        setTimeout(() => input.focus(), 0);
        return;
      }
      const b = btn(line, "line", () => { openLine = openLine === id ? null : id; renderReflect(); }, { "aria-expanded": openLine === id ? "true" : "false" });
      li.append(b);
      if (openLine === id) {
        const acts = el("div.line-actions");
        ["happened", "told", "concluded"].filter((k) => k !== key).forEach((k) => acts.append(btn(C.moveTo + " " + C[k].toLowerCase(), "chip", () => { s.sorted = moveLine(s.sorted, key, i, k); openLine = null; persist(); renderReflect(); })));
        acts.append(btn(C.edit, "chip", () => { openLine = id + ":edit"; renderReflect(); }));
        acts.append(btn(C.remove, "chip", () => { s.sorted[key].splice(i, 1); openLine = null; persist(); renderReflect(); }));
        li.append(acts);
      }
      list.append(li);
    });
    block.append(list);
    if (openLine === key + ":new") {
      const input = el("input", { type: "text", "aria-label": C.add });
      const finish = () => { if (input.value.trim()) s.sorted[key].push(input.value.trim()); openLine = null; persist(); renderReflect(); };
      input.addEventListener("keydown", (e) => { if (e.key === "Enter") finish(); });
      block.append(input, el("div.line-actions", null, btn(C.done, "chip", finish)));
      setTimeout(() => input.focus(), 0);
    } else {
      block.append(btn(C.add, "link add", () => { openLine = key + ":new"; renderReflect(); }));
    }
    node.append(block);
  });
  node.append(nav(() => { persist(); home(); }, [btn(C.next, "primary", () => { s.sorted = cleanSorted(s.sorted); openLine = null; persist(); want(); })], true));
  show(node, null, keep);
}

// ---------- Want ----------
function want() {
  const C = COPY.want;
  const picked = new Set(s.wantPicks || []);
  const chips = el("div.chips", { role: "group", "aria-label": C.title });
  C.options.forEach((o) => chips.append(btn(o, "chip", () => {
    if (picked.has(o)) picked.delete(o); else { if (picked.size >= 2) picked.delete([...picked][0]); picked.add(o); }
    chips.querySelectorAll(".chip").forEach((c) => c.setAttribute("aria-pressed", picked.has(c.textContent) ? "true" : "false"));
  }, { "aria-pressed": picked.has(o) ? "true" : "false" })));
  const other = el("input", { type: "text", id: "wantOther", "aria-label": C.otherLabel, placeholder: C.otherLabel, value: s.wantOther || "" });
  const next = (skip) => {
    s.wantPicks = skip ? [] : [...picked]; s.wantOther = skip ? "" : other.value.trim();
    s.want = skip ? "" : [...picked, s.wantOther].filter(Boolean).join(". ");
    persist(); question();
  };
  show(el("div", null, el("h1", null, C.title), el("p.help", null, C.help), el("div.field", null, chips), el("div.field", null, other),
    nav(renderReflect, [btn(C.next, "primary", () => next(false)), btn(C.skip, "link", () => next(true))], true)));
}

// ---------- Question ----------
async function question() {
  if (s.questionAsked === undefined) {
    const r = await withAdvisor("question", () => callStep("question", payload(s)), question);
    if (!r) return;
    s.questionAsked = !!r.ask;
    s.question = r.ask ? r.question : null;
    s.questionWhy = r.ask ? r.why : null;
    s.questionOptions = r.ask ? r.options : [];
    persist();
  }
  if (!s.questionAsked) return read();
  const C = COPY.question;
  const input = el("input", { type: "text", id: "answer", placeholder: C.placeholder, "aria-label": s.question, value: s.answer || "" });
  const chips = el("div.chips", { role: "group", "aria-label": s.question });
  (s.questionOptions || []).forEach((o) => chips.append(btn(o, "chip", () => { input.value = o; chips.querySelectorAll(".chip").forEach((c) => c.setAttribute("aria-pressed", c.textContent === o ? "true" : "false")); }, { "aria-pressed": "false" })));
  const next = (skip) => { s.answer = skip ? C.skip : input.value.trim(); persist(); read(); };
  show(el("div", null, el("p.eyebrow", null, C.eyebrow), el("h1", null, s.question), el("p.help", null, s.questionWhy),
    chips.children.length ? el("div.field", null, chips) : null, el("div.field", null, input),
    nav(want, [btn(C.next, "primary", () => next(false)), btn(C.skip, "link", () => next(true))], true)));
}

// ---------- Read: the stories up front, the why behind a fold ----------
async function read() {
  if (!s.read) {
    const r = await withAdvisor("read", () => callStep("read", payload(s)), read);
    if (!r) return;
    s.read = r;
    s.words = r.words.slice();
    persist();
  }
  const C = COPY.read;
  const node = el("div", null, el("h1", null, C.title));
  s.read.explanations.forEach((e) => node.append(el("article.reading." + e.kind, null,
    label(C.kinds[e.kind] || e.kind, e.kind === "system" ? "sage" : e.kind === "person" ? "rose" : null),
    el("p", null, e.text),
    fold(C.why,
      e.supports && e.supports.length ? el("ul", null, e.supports.map((x) => el("li", null, x))) : null,
      el("p", null, el("strong", null, C.distinguishing + ": "), e.distinguishing)))));
  if (s.read.self_question) node.append(el("div.oneline", null, label(C.selfTitle), el("p", null, s.read.self_question)));
  const more = [];
  if (s.read.influence) more.push(el("p", null, s.read.influence));
  if (s.read.tension) more.push(el("p", null, el("strong", null, C.tensionTitle + ": "), s.read.tension));
  if (more.length) node.append(fold("More", ...more));
  node.append(nav(() => (s.questionAsked ? question() : want()), [btn(C.next, "primary", stepScreen)], true));
  show(node);
}

// ---------- Step: the move and the words; checks behind a fold ----------
function stepScreen() {
  const C = COPY.step; const st = s.read.step;
  const words = el("div.words", null, label(C.wordsTitle));
  s.words.forEach((w, i) => words.append(el("textarea.yours", { "aria-label": C.wordsTitle + " " + (i + 1), rows: 2, on: { input: (e) => { s.words[i] = e.target.value; }, blur: persist } }, w)));
  const node = el("div", null, el("h1", null, C.title), el("p.step-name", null, st.name), el("p", null, st.what), words,
    fold(C.check,
      el("p", null, el("strong", null, C.why + ": "), st.why), el("p", null, el("strong", null, C.assumes + ": "), st.assumes),
      el("p", null, el("strong", null, C.backfires + ": "), st.backfires), el("p", null, el("strong", null, C.alternative + ": "), st.alternative)));
  if (s.read.manager_questions) {
    node.append(fold(C.managerTitle, el("ol", null, [
      "Am I trying to solve the problem, or prove that I'm right?", "What am I avoiding saying because it's uncomfortable?", "What part of this have I contributed to?",
      "Am I confusing accountability with punishment?", "Can I hold a high standard and genuinely want this person to succeed?"].map((q) => el("li", null, q)))));
  }
  node.append(nav(read, [btn(C.next, "primary", () => post(false))], true));
  show(node);
}

// ---------- Post, and kept: one screen ----------
let editingPost = false;
function post(kept) {
  const C = COPY.post;
  if (!s.post) s.post = { sentence: s.read.post || "", date: addDays(todayISO(), 14) };
  const node = el("div");
  if (!kept) {
    node.append(el("h1", null, C.title));
    if (editingPost) {
      const ta = el("textarea.yours", { id: "post", rows: 3, "aria-label": C.title }, s.post.sentence);
      node.append(el("div.field", null, ta), el("div.actions", null, btn(C.done, "chip", () => { s.post.sentence = ta.value.trim() || s.post.sentence; editingPost = false; persist(); post(false); })));
    } else {
      node.append(el("blockquote.quote", null, el("p.yours", null, s.post.sentence), btn(C.edit, "link", () => { editingPost = true; post(false); })));
    }
    const chips = el("div.chips", { role: "group", "aria-label": C.when });
    C.dates.forEach(([days, text]) => {
      const iso = addDays(todayISO(), Number(days));
      chips.append(btn(text, "chip", () => { s.post.date = iso; persist(); post(false); }, { "aria-pressed": s.post.date === iso ? "true" : "false" }));
    });
    node.append(label(C.when), chips, el("p.date-line", null, fmtDate(s.post.date)));
    node.append(nav(stepScreen, [btn(C.next, "primary", () => { persist(); post(true); })], true));
    show(node);
    return;
  }
  document.body.dataset.lit = "full";
  const text = pageText(s);
  const copyBtn = btn(C.copy, "primary", async () => {
    try { await navigator.clipboard.writeText(text); copyBtn.textContent = C.copied; say(C.copied); } catch (e) { window.prompt(C.copy, text); }
  });
  const ics = el("a.ics", { href: URL.createObjectURL(new Blob([icsFor(s)], { type: "text/calendar" })), download: "teamwork-lookback.ics" }, C.calendar);
  node.append(el("h1", null, C.keptTitle), el("p.step-name", null, s.read.step.name),
    el("blockquote.quote", null, el("p.yours", null, s.post.sentence)), el("p.date-line", null, COPY.page.by + " " + fmtDate(s.post.date)),
    el("p.help", null, C.keptHelp), el("div.actions", null, copyBtn, ics),
    fold(C.whole, pageNode(s)));
  const feel = el("div.chips", { role: "group", "aria-label": C.feelTitle });
  const after = el("div", { "aria-live": "polite" });
  const again = () => { s.read = null; s.words = null; s.questionAsked = undefined; s.post = null; delete document.body.dataset.lit; persist(); want(); };
  C.feelings.forEach((f) => feel.append(btn(f, "chip", () => {
    s.feeling = f; persist();
    feel.querySelectorAll(".chip").forEach((c) => c.setAttribute("aria-pressed", c.textContent === f ? "true" : "false"));
    after.replaceChildren();
    if (f === "Still stuck") {
      after.append(el("p.help", null, C.stuckHelp), el("div.actions", null, btn(C.exits.differently, "secondary", again), btn(C.exits.save, "secondary", stopAndSave), btn(C.exits.conduct, "secondary", () => { s.conduct = true; persist(); conduct(); })));
    } else if (f === "Worse") {
      after.append(el("p", null, C.worse), el("div.actions", null, btn(C.exits.differently, "secondary", again), btn(C.home, "link", stopAndSave)));
    } else {
      after.append(el("p", null, C.okay), el("div.actions", null, btn(C.home, "primary", stopAndSave)));
    }
  }, { "aria-pressed": s.feeling === f ? "true" : "false" })));
  node.append(el("section", null, label(C.feelTitle), feel, after), el("div.actions", null, el("span.spacer"), btn(COPY.nav.stop, "link", stopAndSave)));
  show(node);
}
function pageNode(sit) {
  const P = COPY.page; const list = (arr) => el("ul", null, (arr || []).map((x) => el("li", null, x)));
  const n = el("div.page", null, label(P.account), el("p.yours", null, sit.account));
  if (sit.want) n.append(label(P.want), el("p", null, sit.want));
  if (sit.sorted) { if (sit.sorted.happened.length) n.append(label(P.happened), list(sit.sorted.happened)); if (sit.sorted.told.length) n.append(label(P.told), list(sit.sorted.told)); if (sit.sorted.concluded.length) n.append(label(P.concluded), list(sit.sorted.concluded)); }
  if (sit.read) {
    n.append(label(P.explanations), el("ol", null, sit.read.explanations.map((e) => el("li", null, e.text))));
    n.append(label(P.step), el("p", null, el("strong", null, sit.read.step.name + ". "), sit.read.step.what));
    n.append(label(P.words), list(sit.words && sit.words.length ? sit.words : sit.read.words));
  }
  if (sit.post) n.append(label(P.post), el("p.yours", null, sit.post.sentence), el("p.quiet", null, P.by + " " + fmtDate(sit.post.date)));
  return n;
}

// ---------- Conduct ----------
function conduct() {
  lit(null);
  const C = COPY.conduct;
  show(el("div.conduct", null, el("h1", null, C.title), el("p", null, C.lead),
    s && s.safety && typeof s.safety === "string" ? el("p.help", null, "What stood out: " + s.safety + ".") : null,
    el("section", null, label(C.stepsTitle), el("ol", null, C.steps.map((x) => el("li", null, x)))),
    fold(C.outsideTitle, el("p", null, C.outside)),
    el("div.actions", null, btn(C.keep, "primary", stopAndSave), btn(C.delete, "link", () => { if (s) store.remove(s.id); s = null; say(C.deleted); home(); }))));
}

// ---------- Look back ----------
function lookback(sit) {
  s = sit; lit(null);
  const C = COPY.lookback;
  const pick = { expected: null, happened: null };
  const chipGroup = (name, options) => {
    const g = el("div.chips", { role: "group", "aria-labelledby": name + "Label" });
    options.forEach((o) => g.append(btn(o, "chip", () => { pick[name] = o; g.querySelectorAll(".chip").forEach((c) => c.setAttribute("aria-pressed", c.textContent === o ? "true" : "false")); }, { "aria-pressed": "false" })));
    return g;
  };
  const expected = chipGroup("expected", C.expectedOptions);
  const happened = chipGroup("happened", C.happenedOptions);
  const detail = el("input", { type: "text", id: "lbDetail", "aria-label": C.detailLabel, placeholder: C.detailLabel });
  const reveal = btn(C.reveal, "primary", async () => {
    if (!pick.expected || !pick.happened) { say(C.blindHelp); (pick.expected ? happened : expected).querySelector("button").focus(); return; }
    s.lookback = { expected: pick.expected, happened: [pick.happened, detail.value.trim()].filter(Boolean).join(". ") };
    persist();
    const r = await withAdvisor("lookback", () => callStep("lookback", payload(s, { post: s.post, lookback: s.lookback, read_summary: s.read ? { step: s.read.step.name, explanations: s.read.explanations.map((e) => e.text) } : null })), () => lookback(s));
    if (!r) return;
    s.lookback.result = r; persist(); lookbackResult();
  });
  show(el("div", null, el("h1", null, C.title), el("p.help", null, C.blindHelp),
    el("div.field", null, el("p.label", { id: "expectedLabel" }, C.expected), expected),
    el("div.field", null, el("p.label", { id: "happenedLabel" }, C.happened), happened),
    el("div.field", null, detail),
    nav(() => { s = null; home(); }, [reveal], true)));
}
function lookbackResult() {
  const C = COPY.lookback; const r = s.lookback.result;
  const earlier = store.relatedLessons(store.load().situations.filter((x) => x.id !== s.id), r.pattern_tags);
  const lesson = el("textarea.yours", { id: "lesson", rows: 2, placeholder: C.lessonPlaceholder, "aria-label": C.lessonHelp }, s.lookback.lesson || "");
  const finish = (skip) => { s.lookback.lesson = skip ? "" : lesson.value.trim(); persist(); say(C.done); s = null; home(); };
  show(el("div", null, el("h1", null, C.matched[r.matched] || C.title),
    label(C.thenTitle), el("blockquote.quote", null, el("p.yours", null, s.post.sentence)),
    label(C.nowTitle), el("p.yours", null, s.lookback.expected + ". " + s.lookback.happened),
    el("p", null, r.comparison),
    fold(C.inferenceTitle, el("p", null, r.inference)),
    earlier.length ? el("section", null, label(C.earlierLessons), el("ul", null, earlier.map((x) => el("li.yours", null, x)))) : null,
    el("section", null, el("p.step-name", null, r.lesson_prompt), el("div.field", null, lesson), el("p.help", null, C.lessonHelp)),
    el("div.actions.pinned", null, btn(C.save, "primary", () => finish(false)), btn(C.skipLesson, "link", () => finish(true)))));
}

// ---------- Start ----------
window.addEventListener("beforeunload", persist);
home();
