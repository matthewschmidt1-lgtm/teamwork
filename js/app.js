// Teamwork. One screen at a time. The protocol runs on the server; the person stays in control here.
import { COPY } from "./content.js";
import * as store from "./store.js";
import { pageText, icsFor, moveLine, cleanSorted, addDays, fmtDate, todayISO } from "./text.js";
import { step as callStep, payload, AdvisorError } from "./api.js";

const app = document.getElementById("app");
const status = document.getElementById("status");
let s = null;            // the current situation
let screen = "home";

document.getElementById("privacy").textContent = COPY.privacy;

// Tiny element builder: el("p.help", {attr: v}, "text", childNode, ...)
function el(spec, attrs, ...children) {
  const [tag, ...classes] = spec.split(".");
  const node = document.createElement(tag || "div");
  if (classes.length) node.className = classes.join(" ");
  if (attrs) for (const [k, v] of Object.entries(attrs)) {
    if (k === "on") for (const [ev, fn] of Object.entries(v)) node.addEventListener(ev, fn);
    else if (k === "html") node.innerHTML = v;
    else if (v === true) node.setAttribute(k, "");
    else if (v !== false && v != null) node.setAttribute(k, v);
  }
  for (const c of children.flat()) if (c != null && c !== false) node.append(c.nodeType ? c : document.createTextNode(String(c)));
  return node;
}
const btn = (label, cls, on, attrs) => el("button." + cls, Object.assign({ type: "button", on: { click: on } }, attrs || {}), label);

function show(node, focusSel) {
  app.replaceChildren(node);
  node.classList.add("screen");
  const f = focusSel ? app.querySelector(focusSel) : app.querySelector("h1");
  if (f) { if (!f.hasAttribute("tabindex")) f.setAttribute("tabindex", "-1"); f.focus({ preventScroll: true }); }
  window.scrollTo({ top: 0, behavior: "instant" in window ? "instant" : "auto" });
}
function say(text) { status.textContent = text; }
function persist() { if (s) store.upsert(s); }
function stopAndSave() { persist(); s = null; home(); }

function nav(backFn, extra) {
  const row = el("div.actions");
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
    const node = el("div.error", null, el("h1", null, "Not yet"), el("p", null, msg));
    if (e instanceof AdvisorError && e.declined) {
      node.append(btn(COPY.done.exits.conduct, "secondary", () => conduct()));
    }
    node.append(el("div.actions", null, btn(COPY.error.retry, "primary", retry), btn(COPY.error.later, "link", stopAndSave)));
    show(node);
    say(msg);
    return null;
  }
}

// ---------- Home ----------
function home() {
  screen = "home";
  const data = store.load();
  const list = data.situations;
  const ta = el("textarea.account.yours", { id: "account", placeholder: COPY.home.placeholder, "aria-describedby": "accountHelp", autocomplete: "off" });
  const go = btn(COPY.home.go, "primary", () => {
    const text = ta.value.trim();
    if (text.split(/\s+/).length < 4) { say(COPY.home.tooShort); hint.textContent = COPY.home.tooShort; ta.focus(); return; }
    s = { id: store.newId(), created: new Date().toISOString(), account: text };
    persist();
    reflect();
  });
  const hint = el("p.quiet", { id: "hint", role: "status" });
  const node = el("div", null,
    el("h1", { id: "accountLabel" }, COPY.home.question),
    el("p.help", { id: "accountHelp" }, COPY.home.help),
    el("div.field", null, (ta.setAttribute("aria-labelledby", "accountLabel"), ta)),
    hint,
    el("div.actions", null, go),
  );

  const unfinished = store.unfinished(list);
  const due = store.dueForLookback(list);
  const open = store.openOnes(list);
  if (unfinished.length) {
    node.append(el("h3", null, COPY.home.openTitle));
    unfinished.slice(0, 3).forEach((u) => node.append(card(u, btn(COPY.home.continueOne, "secondary", () => { s = u; resume(); }))));
  }
  if (due.length) {
    node.append(el("h3", null, COPY.home.dueTitle));
    due.forEach((d) => node.append(card(d, btn(COPY.home.lookBack, "primary", () => lookback(d)), fmtDate(d.post.date))));
  }
  if (open.length) {
    node.append(el("h3", null, COPY.home.openTitle));
    open.forEach((o) => node.append(card(o, btn(COPY.home.lookBackEarly, "secondary", () => lookback(o)), COPY.page.by + " " + fmtDate(o.post.date))));
  }
  const r = store.record(list);
  if (r.thought || r.looked) {
    node.append(el("h3", null, COPY.home.recordTitle), el("div.record", null,
      stat(r.thought, COPY.record.situations), stat(r.looked, COPY.record.lookbacks), stat(r.matched, COPY.record.matched), stat(r.lessons, COPY.record.lessons)),
      el("p.quiet", null, COPY.home.recordNote));
  }
  if (list.length) {
    node.append(el("div.actions", null, btn(COPY.home.deleteAll, "link", () => { if (confirm(COPY.home.deleteAllConfirm)) { store.clearAll(); home(); } })));
  }
  show(node, "#account");
}
const stat = (n, l) => el("div", null, el("span.n", null, String(n)), el("span.l", null, l));
function card(sit, action, meta) {
  const first = (sit.post && sit.post.sentence) || sit.account;
  return el("div.card", null, el("div.what", null, el("p.yours", null, first.length > 120 ? first.slice(0, 117) + "..." : first), meta ? el("p.quiet", null, meta) : null), action);
}
function resume() {
  if (!s.sorted) return reflect();
  if (s.conduct) return conduct();
  if (!s.read) return want();
  if (!s.post) return read();
  return done();
}

// ---------- Reflect ----------
async function reflect() {
  screen = "reflect";
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
function renderReflect() {
  const C = COPY.reflect;
  const node = el("div", null,
    el("h1", null, C.title),
    s.echo ? el("p", null, s.echo) : null,
    el("p.help", null, C.help),
  );
  const groups = [["happened", C.happened, C.happenedHelp], ["told", C.told, C.toldHelp], ["concluded", C.concluded, C.concludedHelp]];
  groups.forEach(([key, title, help]) => {
    const g = el("section.group." + key, null, el("h3", null, title), el("p.help", null, help));
    s.sorted[key].forEach((line, i) => g.append(lineRow(key, i, line, groups)));
    g.append(btn(C.add, "link add", () => { s.sorted[key].push(""); persist(); renderReflect(); focusLine(key, s.sorted[key].length - 1); }));
    node.append(g);
  });
  node.append(nav(() => { persist(); home(); }, [btn(C.next, "primary", () => { s.sorted = cleanSorted(s.sorted); persist(); want(); })]));
  show(node);
}
function focusLine(key, i) { const f = app.querySelector(`[data-key="${key}"][data-i="${i}"] input`); if (f) f.focus(); }
function lineRow(key, i, line, groups) {
  const C = COPY.reflect;
  const input = el("input", { type: "text", value: line, "aria-label": COPY.reflect[key] + " " + (i + 1), on: { input: (e) => { s.sorted[key][i] = e.target.value; }, blur: persist } });
  const sel = el("select", { "aria-label": C.moveLabel, on: { change: (e) => { s.sorted = moveLine(s.sorted, key, i, e.target.value); persist(); renderReflect(); } } });
  groups.forEach(([k]) => sel.append(el("option", { value: k, selected: k === key }, C.short[k])));
  const rm = btn("×", "remove", () => { s.sorted[key].splice(i, 1); persist(); renderReflect(); }, { "aria-label": C.remove });
  return el("div.line", { "data-key": key, "data-i": i }, input, sel, rm);
}

// ---------- Want ----------
function want() {
  screen = "want";
  const C = COPY.want;
  const ta = el("textarea.yours", { id: "want", placeholder: C.placeholder, "aria-labelledby": "wantLabel", "aria-describedby": "wantHelp" }, s.want || "");
  const next = (skip) => { s.want = skip ? "" : ta.value.trim(); persist(); question(); };
  show(el("div", null, el("h1", { id: "wantLabel" }, C.title), el("p.help", { id: "wantHelp" }, C.help), el("div.field", null, ta),
    nav(renderReflect, [btn(C.next, "primary", () => next(false)), btn(C.skip, "link", () => next(true))])), "#want");
}

// ---------- Question ----------
async function question() {
  screen = "question";
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
  (s.questionOptions || []).forEach((o) => chips.append(btn(o, "chip", () => { input.value = o; chips.querySelectorAll(".chip").forEach((c) => c.setAttribute("aria-pressed", c.textContent === o)); })));
  const next = (skip) => { s.answer = skip ? COPY.question.skip : input.value.trim(); persist(); read(); };
  show(el("div", null, el("p.eyebrow", null, C.eyebrow), el("h1", null, s.question), el("p.help", null, s.questionWhy),
    chips.children.length ? el("div.field", null, chips) : null, el("div.field", null, input),
    nav(want, [btn(C.next, "primary", () => next(false)), btn(C.skip, "link", () => next(true))])));
}

// ---------- Read ----------
async function read() {
  screen = "read";
  if (!s.read) {
    const r = await withAdvisor("read", () => callStep("read", payload(s)), read);
    if (!r) return;
    s.read = r;
    s.words = r.words.slice();
    persist();
  }
  const C = COPY.read;
  const ex = s.read.explanations;
  const grid = el("div.readings." + (ex.length === 3 ? "three" : "two"));
  ex.forEach((e) => grid.append(el("article.reading." + e.kind, null,
    el("h3", null, C.kinds[e.kind] || e.kind),
    el("p", null, e.text),
    e.supports && e.supports.length ? el("ul", null, e.supports.map((x) => el("li", null, x))) : null,
    el("p.tell", null, el("strong", null, C.distinguishing + ": "), e.distinguishing))));
  show(el("div", null, el("h1", null, C.title), el("p.help", null, C.help), grid,
    s.read.self_question ? el("div", null, el("h3", null, C.selfTitle), el("p", null, s.read.self_question)) : null,
    el("h3", null, C.influenceTitle), el("p", null, s.read.influence),
    s.read.tension ? el("div", null, el("h3", null, C.tensionTitle), el("p", null, s.read.tension)) : null,
    nav(() => (s.questionAsked ? question() : want()), [btn(C.next, "primary", stepScreen)])));
}

// ---------- Step ----------
function stepScreen() {
  screen = "step";
  const C = COPY.step; const st = s.read.step;
  const words = el("div.words", null, el("h3", null, C.wordsTitle), el("p.help", null, C.wordsHelp));
  s.words.forEach((w, i) => words.append(el("textarea.yours", { "aria-label": C.wordsTitle + " " + (i + 1), rows: 2, on: { input: (e) => { s.words[i] = e.target.value; }, blur: persist } }, w)));
  const node = el("div", null, el("h1", null, C.title), el("p.step-name", null, st.name), el("p", null, st.what),
    el("dl", null, el("dt", null, C.why), el("dd", null, st.why), el("dt", null, C.assumes), el("dd", null, st.assumes), el("dt", null, C.backfires), el("dd", null, st.backfires), el("dt", null, C.alternative), el("dd", null, st.alternative)),
    words);
  if (s.read.manager_questions) {
    node.append(el("aside.manager", null, el("h3", null, C.managerTitle), el("ol", null, [
      "Am I trying to solve the problem, or prove that I'm right?", "What am I avoiding saying because it's uncomfortable?", "What part of this have I contributed to?",
      "Am I confusing accountability with punishment?", "Can I hold a high standard and genuinely want this person to succeed?"].map((q) => el("li", null, q)))));
  }
  node.append(nav(read, [btn(C.next, "primary", post)]));
  show(node);
}

// ---------- Post ----------
function post() {
  screen = "post";
  const C = COPY.post;
  const ta = el("textarea.yours", { id: "post", rows: 3, "aria-labelledby": "postLabel", "aria-describedby": "postHelp" }, (s.post && s.post.sentence) || s.read.post || "");
  const date = el("input", { type: "date", id: "postDate", value: (s.post && s.post.date) || addDays(todayISO(), 14), min: todayISO() });
  const keep = btn(C.next, "primary", () => {
    if (!ta.value.trim() || !date.value) { ta.focus(); return; }
    s.post = { sentence: ta.value.trim(), date: date.value };
    persist(); done();
  });
  show(el("div", null, el("h1", { id: "postLabel" }, C.title), el("p.help", { id: "postHelp" }, C.help), el("div.field", null, ta),
    el("div.field", null, el("label", { for: "postDate" }, C.dateLabel), date), nav(stepScreen, [keep])), "#post");
}

// ---------- Done ----------
function done() {
  screen = "done";
  const C = COPY.done;
  const text = pageText(s);
  const copyBtn = btn(C.copy, "secondary", async () => {
    try { await navigator.clipboard.writeText(text); copyBtn.textContent = C.copied; say(C.copied); } catch (e) { window.prompt(C.copy, text); }
  });
  const ics = el("a.secondary", { href: URL.createObjectURL(new Blob([icsFor(s)], { type: "text/calendar" })), download: "teamwork-lookback.ics", role: "button", style: "display:inline-flex;align-items:center;min-height:44px;padding:0 1.25rem;border:1px solid var(--hair);border-radius:999px;color:var(--ink);text-decoration:none" }, C.calendar);
  const feel = el("div.chips", { role: "group", "aria-label": C.feelTitle });
  const after = el("div", { "aria-live": "polite" });
  C.feelings.forEach((f) => feel.append(btn(f, "chip", () => {
    s.feeling = f; persist();
    feel.querySelectorAll(".chip").forEach((c) => c.setAttribute("aria-pressed", c.textContent === f));
    after.replaceChildren();
    if (f === "Still stuck") {
      after.append(el("p.help", null, C.stuckHelp), el("div.actions", null,
        btn(C.exits.differently, "secondary", () => { s.read = null; s.words = null; s.questionAsked = undefined; s.post = null; persist(); want(); }),
        btn(C.exits.save, "secondary", stopAndSave),
        btn(C.exits.conduct, "secondary", () => { s.conduct = true; persist(); conduct(); })));
    } else if (f === "Worse") {
      after.append(el("p", null, C.worse), el("div.actions", null, btn(C.exits.differently, "secondary", () => { s.read = null; s.words = null; s.questionAsked = undefined; s.post = null; persist(); want(); }), btn(C.home, "link", stopAndSave)));
    } else {
      after.append(el("p", null, C.okay), el("div.actions", null, btn(C.home, "primary", stopAndSave)));
    }
  })));
  show(el("div", null, el("h1", null, C.title), el("p.help", null, C.help), pageNode(s),
    el("div.actions", null, copyBtn, ics),
    el("h2", null, C.feelTitle), feel, after,
    nav(post)));
}
function pageNode(sit) {
  const P = COPY.page; const list = (arr) => el("ul", null, (arr || []).map((x) => el("li", null, x)));
  const n = el("div.page", null, el("h3", null, P.account), el("p.yours", null, sit.account));
  if (sit.want) n.append(el("h3", null, P.want), el("p.yours", null, sit.want));
  if (sit.sorted) { if (sit.sorted.happened.length) n.append(el("h3", null, P.happened), list(sit.sorted.happened)); if (sit.sorted.told.length) n.append(el("h3", null, P.told), list(sit.sorted.told)); if (sit.sorted.concluded.length) n.append(el("h3", null, P.concluded), list(sit.sorted.concluded)); }
  if (sit.read) {
    n.append(el("h3", null, P.explanations), el("ol", null, sit.read.explanations.map((e) => el("li", null, e.text))));
    n.append(el("h3", null, P.step), el("p", null, el("strong", null, sit.read.step.name + ". "), sit.read.step.what));
    n.append(el("h3", null, P.words), list(sit.words && sit.words.length ? sit.words : sit.read.words));
  }
  if (sit.post) n.append(el("h3", null, P.post), el("p.post-line", null, sit.post.sentence), el("p.quiet", null, P.by + " " + fmtDate(sit.post.date)));
  return n;
}

// ---------- Conduct ----------
function conduct() {
  screen = "conduct";
  const C = COPY.conduct;
  const node = el("div.conduct", null, el("h1", null, C.title), el("p", null, C.lead),
    s && s.safety && typeof s.safety === "string" ? el("p.quiet", null, "What stood out: " + s.safety + ".") : null,
    el("h3", null, C.stepsTitle), el("ol", null, C.steps.map((x) => el("li", null, x))),
    el("h3", null, C.outsideTitle), el("p", null, C.outside),
    el("div.actions", null,
      btn(C.keep, "primary", stopAndSave),
      btn(C.delete, "link", () => { if (s) store.remove(s.id); s = null; say(C.deleted); home(); })));
  show(node);
}

// ---------- Look back ----------
function lookback(sit) {
  s = sit; screen = "lookback";
  const C = COPY.lookback;
  const expected = el("textarea.yours", { id: "expected", rows: 3, "aria-labelledby": "expLabel" }, (s.lookback && s.lookback.expected) || "");
  const happened = el("textarea.yours", { id: "happened", rows: 3, "aria-labelledby": "hapLabel" }, (s.lookback && s.lookback.happened) || "");
  const reveal = btn(C.reveal, "primary", async () => {
    if (!expected.value.trim() || !happened.value.trim()) { (expected.value.trim() ? happened : expected).focus(); return; }
    s.lookback = { expected: expected.value.trim(), happened: happened.value.trim() };
    persist();
    const r = await withAdvisor("lookback", () => callStep("lookback", payload(s, { post: s.post, lookback: s.lookback, read_summary: s.read ? { step: s.read.step.name, explanations: s.read.explanations.map((e) => e.text) } : null })), () => lookback(s));
    if (!r) return;
    s.lookback.result = r; persist(); lookbackResult();
  });
  show(el("div", null, el("h1", null, C.title), el("p.help", null, C.blindHelp),
    el("div.field", null, el("label", { id: "expLabel", for: "expected" }, C.expected), expected),
    el("div.field", null, el("label", { id: "hapLabel", for: "happened" }, C.happened), happened),
    nav(() => { s = null; home(); }, [reveal])));
}
function lookbackResult() {
  const C = COPY.lookback; const r = s.lookback.result;
  const earlier = store.relatedLessons(store.load().situations.filter((x) => x.id !== s.id), r.pattern_tags);
  const lesson = el("textarea.yours", { id: "lesson", rows: 2, placeholder: C.lessonPlaceholder, "aria-label": C.lessonHelp }, s.lookback.lesson || "");
  const finish = (skip) => { s.lookback.lesson = skip ? "" : lesson.value.trim(); persist(); say(C.done); s = null; home(); };
  show(el("div", null, el("h1", null, C.matched[r.matched] || C.title),
    el("h3", null, C.thenTitle), el("p.yours", null, s.post.sentence),
    el("h3", null, C.nowTitle), el("p.yours", null, s.lookback.expected), el("p.yours", null, s.lookback.happened),
    el("p", null, r.comparison),
    el("h3", null, C.inferenceTitle), el("p", null, r.inference),
    earlier.length ? el("div", null, el("h3", null, C.earlierLessons), el("ul", null, earlier.map((x) => el("li.yours", null, x)))) : null,
    el("h2", null, r.lesson_prompt), el("p.help", null, C.lessonHelp), el("div.field", null, lesson),
    el("div.actions", null, btn(C.save, "primary", () => finish(false)), btn(C.skipLesson, "link", () => finish(true)))));
}

// ---------- Start ----------
window.addEventListener("beforeunload", persist);
home();
