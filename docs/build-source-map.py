"""Build docs/source-map.html from server/library.json.

Two diagrams, both static SVG: an overview of how the materials connect to each other, and the full
network of ideas with the library's relationships drawn between them. Run after editing the library:

    python3 docs/build-source-map.py
"""
import json
import math
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
lib = json.loads((ROOT / "server" / "library.json").read_text())
P = {p["id"]: p for p in lib["principles"]}
R = lib["relations"]

# Which material each idea belongs to, from its id prefix and source text.
MATERIALS = [
    ("books", "The seven books", "Matthew's readings on his website; Lencioni has no material yet"),
    ("site", "The website", "Two Loops, Three Lenses, six forces, the Path to Agency"),
    ("dos", "Decision OS", "Module 3 cases, habit families, skills, the algorithms"),
    ("friction", "Friction", "Fifteen states, evidence weights, the one-question rule"),
    ("stillward", "Stillward", "One thing per screen, no streaks, the feeling check"),
    ("ds", "Decision science", "Widely reported ideas and Teamwork's synthesis"),
    ("rules", "Protocol rules", "The standing rules the advisor obeys"),
]
COLOR = {"books": "#5B4B8A", "site": "#2C4A7A", "dos": "#A9533F", "friction": "#2F6F5E", "stillward": "#8A6D3B", "ds": "#1E4D3B", "rules": "#5A625C"}


def material(p):
    i = p["id"]; k = p["kind"]
    if k == "book": return "books"
    if k in ("loop", "lens", "force", "path"): return "site"
    if k in ("case", "habit", "skill", "algorithm", "decision-os"): return "dos"
    if k == "friction": return "friction"
    if k == "stillward": return "stillward"
    if k == "rule": return "rules"
    return "ds"


groups = defaultdict(list)
for p in P.values():
    groups[material(p)].append(p)

# Extra edges: each Module 3 case is the owner's reading of a book.
BOOK_IDS = {p["label"]: p["id"] for p in P.values() if p["kind"] == "book"}
reading_edges = []
for p in P.values():
    if p["kind"] == "case":
        m = re.search(r"owner's reading of: (.+)\)$", p["source"])
        if m:
            title = m.group(1).strip()
            bid = next((bid for lab, bid in BOOK_IDS.items() if lab.lower().startswith(title.lower()[:12]) or title.lower().startswith(lab.lower()[:12])), None)
            if bid: reading_edges.append({"from": p["id"], "to": bid, "kind": "reading", "why": "The case is the owner's reading of this book."})

edges = R + reading_edges


def esc(t):
    return (t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ---------- Overview: materials as nodes, edge weight = number of relationships between them ----------
pair = defaultdict(lambda: defaultdict(int))
for e in edges:
    a, b = material(P[e["from"]]), material(P[e["to"]])
    if a == b: continue
    key = tuple(sorted((a, b)))
    pair[key][e["kind"]] += 1

W, H = 1100, 680
cx, cy, rx, ry = W / 2, H / 2 + 10, 420, 240
pos = {}
for i, (mid, _, _) in enumerate(MATERIALS):
    a = -math.pi / 2 + 2 * math.pi * i / len(MATERIALS)
    pos[mid] = (cx + rx * math.cos(a), cy + ry * math.sin(a))

ov = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="ovTitle ovDesc" class="svg">',
      '<title id="ovTitle">How the materials connect</title>',
      '<desc id="ovDesc">Seven materials around a ring; the thickness of each line is the number of relationships between ideas from the two materials.</desc>']
for (a, b), kinds in sorted(pair.items()):
    n = sum(kinds.values())
    (x1, y1), (x2, y2) = pos[a], pos[b]
    mx, my = (x1 + x2) / 2 + (cy - (y1 + y2) / 2) * 0.25, (y1 + y2) / 2 + ((x1 + x2) / 2 - cx) * 0.25
    parts = ", ".join(f"{v} {k}" for k, v in sorted(kinds.items()))
    ov.append(f'<path d="M{x1:.0f},{y1:.0f} Q{mx:.0f},{my:.0f} {x2:.0f},{y2:.0f}" class="ov-edge" stroke-width="{0.8 + n * 0.9:.1f}"><title>{esc(a)} and {esc(b)}: {n} relationships ({esc(parts)})</title></path>')
for mid, name, note in MATERIALS:
    x, y = pos[mid]
    count = len(groups[mid])
    words = name.split()
    lines = [name] if len(name) <= 12 else [" ".join(words[:len(words) // 2 or 1]), " ".join(words[len(words) // 2 or 1:])]
    tspans = "".join(f'<tspan x="{x:.0f}" dy="{0 if i == 0 else 15}">{esc(l)}</tspan>' for i, l in enumerate(lines))
    y0 = y - (2 if len(lines) == 1 else 9)
    ov.append(f'<g class="ov-node" data-mat="{mid}" tabindex="0" role="button" aria-haspopup="dialog"><circle cx="{x:.0f}" cy="{y:.0f}" r="58" fill="{COLOR[mid]}"/>'
              f'<text x="{x:.0f}" y="{y0:.0f}" class="ov-name">{tspans}</text>'
              f'<text x="{x:.0f}" y="{y + 30 if len(lines) == 2 else y + 18:.0f}" class="ov-count">{count} ideas</text>'
              f'<title>{esc(name)}: {esc(note)}</title></g>')
ov.append("</svg>")

# ---------- Detail: every idea, clustered by material, every relationship drawn ----------
ORDER = ["site", "books", "dos", "ds", "friction", "stillward", "rules"]
COLS = {"dos": 3, "ds": 2}
NODE_W, NODE_H, GAP = 190, 26, 8
cluster_boxes = {}
node_pos = {}
# Lay clusters in two bands: top row (site, books, ds, friction) and bottom row (dos, stillward, rules).
layout = [["site", "books", "ds", "friction"], ["dos", "stillward", "rules"]]
DW = 1400
y = 60
for row in layout:
    x = 40
    row_h = 0
    widths = []
    for mid in row:
        items = sorted(groups[mid], key=lambda p: (p["kind"], p["label"]))
        cols = COLS.get(mid, 1 if len(items) <= 8 else 2)
        rows = math.ceil(len(items) / cols)
        w = cols * (NODE_W + GAP) + 24
        h = rows * (NODE_H + GAP) + 56
        widths.append((mid, items, cols, w, h))
        row_h = max(row_h, h)
    total = sum(w for _, _, _, w, _ in widths) + GAP * 3 * (len(widths) - 1)
    x = max(40, (DW - total) / 2)
    for mid, items, cols, w, h in widths:
        cluster_boxes[mid] = (x, y, w, h)
        for i, p in enumerate(items):
            c, r = i % cols, i // cols
            nx = x + 12 + c * (NODE_W + GAP)
            ny = y + 44 + r * (NODE_H + GAP)
            node_pos[p["id"]] = (nx, ny)
        x += w + GAP * 3
    y += row_h + 60
DH = y + 20

det = [f'<svg viewBox="0 0 {DW} {DH}" role="img" aria-labelledby="dtTitle dtDesc" class="svg detail">',
       '<title id="dtTitle">Every idea and every relationship</title>',
       f'<desc id="dtDesc">{len(P)} ideas in seven clusters with {len(edges)} relationships drawn between them.</desc>']
for mid, (x, yy, w, h) in cluster_boxes.items():
    name = next(n for m, n, _ in MATERIALS if m == mid)
    det.append(f'<rect x="{x:.0f}" y="{yy:.0f}" width="{w:.0f}" height="{h:.0f}" rx="14" class="cluster" stroke="{COLOR[mid]}"/>'
               f'<text x="{x + 14:.0f}" y="{yy + 26:.0f}" class="cluster-name" fill="{COLOR[mid]}">{esc(name)}</text>')
for e in edges:
    if e["from"] not in node_pos or e["to"] not in node_pos: continue
    (x1, y1), (x2, y2) = node_pos[e["from"]], node_pos[e["to"]]
    x1 += NODE_W / 2; y1 += NODE_H / 2; x2 += NODE_W / 2; y2 += NODE_H / 2
    mx = (x1 + x2) / 2; my = (y1 + y2) / 2 - abs(x2 - x1) * 0.12
    det.append(f'<path d="M{x1:.0f},{y1:.0f} Q{mx:.0f},{my:.0f} {x2:.0f},{y2:.0f}" class="edge {esc(e["kind"])}" data-from="{esc(e["from"])}" data-to="{esc(e["to"])}">'
               f'<title>{esc(P[e["from"]]["label"])} {esc(e["kind"])} {esc(P[e["to"]]["label"])}. {esc(e["why"])}</title></path>')
for pid, (nx, ny) in node_pos.items():
    p = P[pid]
    label = p["label"] if len(p["label"]) <= 26 else p["label"][:25] + "…"
    mark = {"owner_reading": "●", "widely_reported": "○", "synthesis": "◆"}[p["status"]]
    det.append(f'<g class="node" data-id="{esc(pid)}" tabindex="0" role="button" aria-haspopup="dialog"><rect x="{nx:.0f}" y="{ny:.0f}" width="{NODE_W}" height="{NODE_H}" rx="6" stroke="{COLOR[material(p)]}"/>'
               f'<text x="{nx + 8:.0f}" y="{ny + 17:.0f}" class="node-label"><tspan class="mark">{mark}</tspan> {esc(label)}</text>'
               f'<title>{esc(p["label"])} ({esc(p["kind"])}, {esc(p["status"].replace("_", " "))}). {esc(p["summary"])} Source: {esc(p["source"])}</title></g>')
det.append("</svg>")

counts = {m: len(groups[m]) for m, _, _ in MATERIALS}
kinds = defaultdict(int)
for e in edges: kinds[e["kind"]] += 1


# ---------- Popup data, inlined (the server hides /server/, so the page cannot fetch library.json) ----------
used_by = defaultdict(list)
steps_out = []
for n, st in enumerate(lib["steps"], 1):
    for l in st["links"]:
        used_by[l["id"]].append({"step": st["id"], "opt": None, "why": l["why"]})
    for o in st["options"]:
        for l in o["links"]:
            used_by[l["id"]].append({"step": st["id"], "opt": o["id"], "why": l["why"]})
    steps_out.append({"id": st["id"], "n": n, "title": st["title"], "options": {o["id"]: o["label"] for o in st["options"]}})
POP = {
    "ideas": {pid: {"label": p["label"], "kind": p["kind"], "status": p["status"], "summary": p["summary"], "source": p["source"], "mat": material(p), "seat": p.get("seat", "any"),
                    "used": used_by.get(pid, [])} for pid, p in P.items()},
    "rels": [{"from": e["from"], "to": e["to"], "kind": e["kind"], "why": e["why"]} for e in edges],
    "steps": {s_["id"]: s_ for s_ in steps_out},
    "mats": {mid: {"name": name, "note": note, "color": COLOR[mid],
                   "ideas": [p["id"] for p in sorted(groups[mid], key=lambda q: (q["kind"], q["label"]))]} for mid, name, note in MATERIALS},
}
POP_JSON = json.dumps(POP, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

CSS_EXTRA = """
  .node, .ov-node { cursor:pointer; }
  .node:focus-visible rect { stroke:var(--ember); stroke-width:3.5; fill:var(--ground); }
  .node.sel rect { stroke:var(--ember); stroke-width:3.5; fill:var(--ground); }
  .ov-node:focus { outline:none; }
  .ov-node:focus-visible circle, .ov-node.sel circle { stroke:var(--ember); stroke-width:5; }
  .ov-node:hover circle { stroke:var(--text); stroke-width:3; }
  .node { scroll-margin-top:100px; }
  dialog#pop { position:absolute; margin:0; padding:0; width:min(26rem, calc(100vw - 24px)); max-height:calc(100vh - 24px); overflow:auto; background:var(--surface); color:var(--text); border:2px solid var(--text-2); border-radius:14px; z-index:20; }
  dialog#pop:not([open]) { display:none; }
  dialog#pop .pin { padding:16px 18px 20px; }
  dialog#pop h2.pt { font:400 22px/1.25 "Fraunces",Georgia,serif; font-variation-settings:"opsz" 36,"SOFT" 50; margin:2px 0 8px; padding-right:3.5rem; }
  dialog#pop h2.pt:focus { outline:none; }
  dialog#pop h3 { font:600 12px/1.2 "DM Sans",sans-serif; letter-spacing:.1em; text-transform:uppercase; color:var(--text-2); margin:18px 0 8px; }
  dialog#pop p { margin:0 0 8px; font-size:15px; }
  dialog#pop .eyebrow { font:600 11px/1.4 "DM Sans",sans-serif; letter-spacing:.12em; text-transform:uppercase; color:var(--text-2); margin:0; }
  dialog#pop .badge { display:inline-block; font-size:13px; border:1px solid var(--hair); border-radius:999px; padding:2px 10px; margin:0 6px 6px 0; color:var(--text-2); }
  dialog#pop .badge.mat { color:var(--text); border-color:var(--bc, var(--hair)); border-left-width:6px; }
  dialog#pop ul { list-style:none; margin:0; padding:0; display:grid; gap:10px; }
  dialog#pop li.r { border-left:3px solid var(--text-2); padding-left:10px; }
  dialog#pop li.r.tension { border-left-style:dashed; border-color:var(--ember); }
  dialog#pop li.r.specializes { border-left-style:dotted; }
  dialog#pop li.r.override { border-left-style:solid; border-color:var(--violet, #5B4B8A); }
  dialog#pop li.r.reading { border-color:#8A6D3B; }
  dialog#pop .rt { font-size:13px; font-weight:600; color:var(--text-2); margin:0 0 2px; }
  dialog#pop li p.why { font-size:14px; margin:4px 0 0; }
  dialog#pop button, dialog#pop a { font:inherit; }
  dialog#pop .ib { display:inline-flex; align-items:center; min-height:36px; text-align:left; background:var(--ground); color:var(--text); border:1px solid var(--hair); border-radius:8px; padding:4px 10px; font-size:14px; line-height:1.3; cursor:pointer; }
  dialog#pop .ib:hover { border-color:var(--text); }
  dialog#pop .x { position:absolute; top:10px; right:12px; min-height:36px; background:transparent; color:var(--text-2); border:1px solid var(--hair); border-radius:999px; padding:4px 12px; font-size:14px; cursor:pointer; }
  dialog#pop .x:hover { color:var(--text); border-color:var(--text); }
  dialog#pop a.lk { color:var(--text); text-underline-offset:3px; font-size:14px; }
  dialog#pop a.see { display:inline-flex; align-items:center; min-height:44px; margin-top:16px; padding:0 18px; border-radius:999px; background:var(--text); color:var(--ground); text-decoration:none; font-size:15px; }
  dialog#pop button:focus-visible, dialog#pop a:focus-visible { outline:3px solid var(--focus, var(--ember)); outline-offset:2px; }
  dialog#pop .none { color:var(--text-2); font-size:14px; }
  @media (max-width:44rem) {
    dialog#pop { position:fixed; left:0; right:0; bottom:0; top:auto; width:auto; max-height:72vh; border-radius:16px 16px 0 0; border-width:2px 0 0 0; }
    body.sheet { padding-bottom:60vh; }
  }
"""

JS_EXTRA = r"""
(function () {
  var POP = JSON.parse(document.getElementById("popdata").textContent);
  var dlg = document.getElementById("pop");
  var STATUS = { owner_reading: "● The owner's reading", widely_reported: "○ Widely reported idea", synthesis: "◆ Teamwork's synthesis" };
  var REL = {
    supports: { out: "Supports", "in": "Is supported by" },
    tension: { out: "Pulls against", "in": "Pulls against" },
    specializes: { out: "Is a narrower form of", "in": "Has a narrower form" },
    override: { out: "Overrides", "in": "Is overridden by" },
    reading: { out: "Is the owner's reading of", "in": "Is read in the case" }
  };
  var ORDER = ["override", "supports", "tension", "specializes", "reading"];
  var SEAT = { manager: "Seat: you manage them", report: "Seat: you report to them", peer: "Seat: a colleague", team_lead: "Seat: you lead the team", team_member: "Seat: you are on the team" };
  var narrow = window.matchMedia("(max-width:44rem)");
  var cur = null; // { type: "idea"|"mat", id }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function nodeFor(c) {
    if (!c) return null;
    return document.querySelector(c.type === "idea" ? '.detail .node[data-id="' + c.id + '"]' : '.ov-node[data-mat="' + c.id + '"]');
  }
  function mark(c) {
    document.querySelectorAll(".node.sel, .ov-node.sel").forEach(function (n) { n.classList.remove("sel"); });
    var n = nodeFor(c); if (n) n.classList.add("sel");
    if (window.__sm_focus) window.__sm_focus(c && c.type === "idea" ? c.id : null, true);
  }
  function ideaBtn(id) {
    var b = el("button", "ib", POP.ideas[id].label); b.type = "button"; b.dataset.idea = id; return b;
  }
  function header(eyebrow, title) {
    var f = el("div", "pin");
    var x = el("button", "x", "Close"); x.type = "button"; x.id = "popClose"; x.setAttribute("aria-label", "Close the popup");
    f.append(x, el("p", "eyebrow", eyebrow));
    var h = el("h2", "pt", title); h.id = "popTitle"; h.tabIndex = -1; f.append(h);
    return f;
  }
  function build(c) {
    dlg.textContent = "";
    var f;
    if (c.type === "mat") {
      var m = POP.mats[c.id];
      f = header("Material", m.name);
      f.append(el("p", null, m.note));
      f.append(el("h3", null, m.ideas.length + " ideas"));
      var ul = el("ul");
      m.ideas.forEach(function (i) { var li = el("li"); li.append(ideaBtn(i)); ul.append(li); });
      f.append(ul);
    } else {
      var p = POP.ideas[c.id], m2 = POP.mats[p.mat];
      f = header(p.kind, p.label);
      var b1 = el("span", "badge mat", m2.name); b1.style.setProperty("--bc", m2.color);
      f.append(b1, el("span", "badge", STATUS[p.status]));
      if (p.seat && p.seat !== "any") f.append(el("span", "badge", SEAT[p.seat] || p.seat));
      f.append(el("p", null, p.summary));
      f.append(el("h3", null, "Source"), el("p", null, p.source));
      var rs = [];
      POP.rels.forEach(function (r) {
        if (r.from === c.id) rs.push({ k: r.kind, dir: "out", other: r.to, why: r.why });
        else if (r.to === c.id) rs.push({ k: r.kind, dir: "in", other: r.from, why: r.why });
      });
      f.append(el("h3", null, "Relationships (" + rs.length + ")"));
      if (!rs.length) f.append(el("p", "none", "No relationship is drawn for this idea. The screens use it directly."));
      else {
        var ul2 = el("ul");
        ORDER.forEach(function (k) {
          rs.filter(function (r) { return r.k === k; }).forEach(function (r) {
            var li = el("li", "r " + k); li.append(el("p", "rt", REL[k][r.dir]), ideaBtn(r.other), el("p", "why", r.why)); ul2.append(li);
          });
        });
        f.append(ul2);
      }
      f.append(el("h3", null, "Used on " + p.used.length + (p.used.length === 1 ? " screen or answer" : " screens and answers")));
      if (!p.used.length) f.append(el("p", "none", "No screen draws on this yet. It is kept in the library for the advisor."));
      else {
        var ul3 = el("ul");
        p.used.forEach(function (u) {
          var st = POP.steps[u.step], li = el("li");
          var a = el("a", "lk", (u.opt ? "“" + st.options[u.opt] + "” on " : "") + "Screen " + st.n + ": " + st.title);
          a.href = "question-map.html#step=" + u.step + (u.opt ? "&opt=" + u.opt : "");
          li.append(a, el("p", "why", u.why)); ul3.append(li);
        });
        f.append(ul3);
      }
      var see = el("a", "see", "See how it reasons"); see.href = "question-map.html#idea=" + c.id; f.append(see);
    }
    dlg.append(f);
    dlg.setAttribute("aria-labelledby", "popTitle");
  }
  function place() {
    if (narrow.matches) { dlg.style.left = dlg.style.top = ""; return; }
    var n = nodeFor(cur); if (!n) return;
    var r = n.getBoundingClientRect(), w = dlg.offsetWidth, h = dlg.offsetHeight, vw = document.documentElement.clientWidth, vh = window.innerHeight;
    var left = r.right + 12;
    if (left + w > vw - 12) left = r.left - w - 12;
    if (left < 12) left = Math.max(12, (vw - w) / 2);
    var top = r.top - 8;
    if (top + h > vh - 12) top = vh - 12 - h;
    if (top < 12) top = 12;
    dlg.style.left = (left + window.pageXOffset) + "px"; dlg.style.top = (top + window.pageYOffset) + "px";
  }
  var opener = null;
  function open(c, from, keepFocusOut) {
    cur = c;
    var n = nodeFor(c);
    if (n && n.scrollIntoView) n.scrollIntoView({ block: narrow.matches ? "start" : "center", inline: "center" });
    build(c); mark(c);
    document.body.classList.toggle("sheet", narrow.matches);
    if (!dlg.open) dlg.show();
    place();
    dlg.scrollTop = 0;
    var h = document.getElementById("popTitle"); if (h && !keepFocusOut) h.focus({ preventScroll: true });
    if (from) opener = from;
  }
  function close(returnFocus) {
    if (!dlg.open) return;
    var n = nodeFor(cur) || opener;
    dlg.close(); cur = null; mark(null);
    document.body.classList.remove("sheet");
    if (returnFocus && n) n.focus({ preventScroll: true });
  }
  window.__sm_open = open;
  function trigger(n) {
    if (n.classList.contains("node")) open({ type: "idea", id: n.getAttribute("data-id") }, n);
    else open({ type: "mat", id: n.getAttribute("data-mat") }, n);
  }
  document.addEventListener("click", function (e) {
    var t = e.target;
    var n = t.closest && t.closest(".detail .node, .ov-node");
    if (n) { trigger(n); return; }
    var b = t.closest && t.closest("dialog#pop button");
    if (b) {
      if (b.id === "popClose") close(true);
      else if (b.dataset.idea) { open({ type: "idea", id: b.dataset.idea }, null); }
      return;
    }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && dlg.open) { e.preventDefault(); close(true); return; }
    if ((e.key === "Enter" || e.key === " ") && e.target.matches && e.target.matches(".detail .node, .ov-node")) { e.preventDefault(); trigger(e.target); }
  });
  document.addEventListener("pointerdown", function (e) {
    if (!dlg.open) return;
    var t = e.target;
    if (dlg.contains(t) || (t.closest && t.closest(".detail .node, .ov-node"))) return;
    close(false);
  });
  window.addEventListener("resize", function () { if (dlg.open) place(); });
  function fromHash() {
    var m = location.hash.match(/^#idea=([^&]+)/);
    if (!m) return;
    var id = decodeURIComponent(m[1]);
    if (!POP.ideas[id]) return;
    var n = nodeFor({ type: "idea", id: id });
    open({ type: "idea", id: id }, n, true);
    if (n) n.focus({ preventScroll: true });
  }
  window.addEventListener("hashchange", fromHash);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { if (dlg.open) place(); });
  fromHash();
})();
"""

html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Teamwork source map</title>
<meta name="description" content="How Teamwork's materials and sources connect: the seven books, the website's structures, Decision OS, Friction, Stillward, decision science and the protocol's rules.">
<script>try{{var a=JSON.parse(localStorage.getItem("teamwork.a11y")||"{{}}"),d=document.documentElement;d.setAttribute("data-size",String(a.size||2));["contrast","theme","leading","motion"].forEach(function(k){{if(a[k])d.setAttribute("data-"+k,a[k]);}});}}catch(e){{}}</script>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT@9..144,300..600,0..100&family=DM+Sans:opsz,wght@9..40,400..600&display=swap">
<link rel="stylesheet" href="/css/a11y.css">
<style>
  :root {{ --ground:#F3EDE2; --surface:#FBF7EF; --text:#17201B; --text-2:#5A625C; --hair:rgba(23,32,27,.16); --ember:#A9533F; --green:#1E4D3B; }}
  :root[data-theme="night"] {{ --ground:#17201B; --surface:#1F2A24; --text:#F3EDE2; --text-2:#B3BDB6; --hair:rgba(243,237,226,.18); --ember:#E0876F; --green:#BFD3C8; }}
  :root[data-contrast="high"] {{ --ground:#FFFFFF; --surface:#FFFFFF; --text:#000; --text-2:#1F1F1F; --hair:rgba(0,0,0,.45); }}
  :root[data-theme="night"][data-contrast="high"] {{ --ground:#000; --surface:#000; --text:#FFF; --text-2:#E0E0E0; --hair:rgba(255,255,255,.45); }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--ground); color:var(--text); font:16px/1.5 "DM Sans",system-ui,sans-serif; -webkit-font-smoothing:antialiased; }}
  .bar {{ position:sticky; top:0; z-index:5; display:flex; justify-content:space-between; align-items:center; gap:24px; padding:14px clamp(20px,5vw,80px); background:var(--ground); border-bottom:1px solid var(--hair); }}
  .bar .mark {{ font:500 20px/1 "Fraunces",Georgia,serif; font-variation-settings:"opsz" 36,"SOFT" 50; color:var(--text); text-decoration:none; }}
  .nav {{ display:flex; align-items:center; gap:22px; }}
  .nav a {{ color:var(--text-2); text-decoration:none; font-size:15px; min-height:44px; display:inline-flex; align-items:center; }}
  .nav a:hover, .nav a[aria-current="page"] {{ color:var(--text); }}
  .nav a.open {{ color:var(--ground); background:var(--text); padding:0 16px; border-radius:999px; }}
  @media (max-width:44rem) {{ .nav a:not(.open) {{ display:none; }} }}
  main {{ padding:40px clamp(20px,5vw,80px) 60px; }}
  h1 {{ font:380 clamp(30px,4vw,48px)/1.1 "Fraunces",Georgia,serif; font-variation-settings:"opsz" 72,"SOFT" 50; margin:0 0 12px; }}
  h2 {{ font:400 26px/1.2 "Fraunces",Georgia,serif; font-variation-settings:"opsz" 36,"SOFT" 50; margin:48px 0 8px; }}
  .lede {{ color:var(--text-2); max-width:70ch; margin:0 0 8px; }}
  .key {{ display:flex; flex-wrap:wrap; gap:8px 20px; margin:12px 0 20px; font-size:14px; color:var(--text-2); }}
  .key i {{ display:inline-block; width:22px; height:0; border-top:2px solid var(--text-2); vertical-align:middle; margin-right:8px; }}
  .key i.tension {{ border-top:2px dashed #A9533F; }} .key i.specializes {{ border-top:2px dotted #5B4B8A; }} .key i.override {{ border-top:3px solid #5B4B8A; }} .key i.supports {{ border-top-color:#2F6F5E; }} .key i.reading {{ border-top:2px solid #8A6D3B; opacity:.6; }}
  .frame {{ background:var(--surface); border:1px solid var(--hair); border-radius:16px; padding:12px; overflow:auto; }}
  .svg {{ width:100%; height:auto; display:block; font-family:"DM Sans",system-ui,sans-serif; }}
  .svg.detail {{ min-width:1100px; }}
  .ov-edge {{ fill:none; stroke:var(--text-2); opacity:.45; }}
  .ov-edge:hover {{ opacity:1; stroke:var(--text); }}
  .ov-name {{ fill:#fff; font-size:13px; font-weight:600; text-anchor:middle; }}
  .ov-count {{ fill:rgba(255,255,255,.8); font-size:11px; text-anchor:middle; }}
  .cluster {{ fill:var(--ground); stroke-width:1.5; opacity:.9; }}
  .cluster-name {{ font:600 12px/1 "DM Sans",sans-serif; letter-spacing:.1em; text-transform:uppercase; }}
  .edge {{ fill:none; stroke-width:1.1; opacity:.5; }}
  .edge.supports {{ stroke:#2F6F5E; }} .edge.tension {{ stroke:#A9533F; stroke-dasharray:6 4; }} .edge.specializes {{ stroke:#5B4B8A; stroke-dasharray:2 3; }} .edge.override {{ stroke:#5B4B8A; stroke-width:2; }} .edge.reading {{ stroke:#8A6D3B; opacity:.25; }}
  .edge.on {{ opacity:1; stroke-width:2.4; }} .edge.off {{ opacity:.06; }}
  .node rect {{ fill:var(--surface); stroke-width:1.2; }}
  .node:hover rect, .node:focus rect, .node.on rect {{ stroke-width:2.4; fill:var(--ground); }}
  .node:focus {{ outline:none; }}
  .node-label {{ fill:var(--text); font-size:12px; }}
  .mark {{ fill:var(--text-2); font-size:10px; }}
  .node.dim {{ opacity:.25; }}
  .counts {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(150px,1fr)); gap:12px 24px; margin:16px 0 0; }}
  .counts b {{ display:block; font:400 26px/1.1 "Fraunces",Georgia,serif; }}
  .counts span {{ color:var(--text-2); font-size:14px; }}
  .site-foot {{ border-top:1px solid var(--hair); padding:28px clamp(20px,5vw,80px) 40px; display:flex; flex-wrap:wrap; justify-content:space-between; gap:12px 24px; color:var(--text-2); font-size:14px; }}
  .site-foot nav {{ display:flex; gap:20px; }} .site-foot a {{ color:var(--text-2); text-decoration:none; }} .site-foot a:hover {{ color:var(--text); text-decoration:underline; text-underline-offset:4px; }}
  #detailNote {{ min-height:3.2em; color:var(--text-2); font-size:15px; margin:12px 0 0; }}
{CSS_EXTRA}
</style>
</head>
<body>
<header class="bar">
  <a class="mark" href="/">Teamwork</a>
  <nav class="nav" aria-label="Site">
    <a href="/#sort">How it works</a>
    <a href="/docs/question-map.html">How it reasons</a>
    <a href="/docs/source-map.html" aria-current="page">Sources</a>
    <span id="a11yButton"></span>
    <a class="open" href="/app/">Open the app</a>
  </nav>
</header>
<main>
  <h1>Where Teamwork's ideas come from, and how they connect</h1>
  <p class="lede">Seven materials feed the advisor. The first drawing shows how much each pair of materials speaks to the others. The second draws every idea in the library and every relationship between them. Hover or focus a node to see its own connections; hover a line to read why it is there. Click a node, or press Enter on it, for the full reasoning, and click a material to list its ideas.</p>
  <div class="counts">
    <div><b>{len(P)}</b><span>ideas</span></div>
    <div><b>{len(R)}</b><span>relationships between ideas</span></div>
    <div><b>{len(reading_edges)}</b><span>cases that are readings of a book</span></div>
    <div><b>{counts["books"]}</b><span>book ideas (Lencioni has none yet)</span></div>
  </div>

  <h2>The materials</h2>
  <p class="lede">Line thickness is the number of relationships between ideas from the two materials. Hover a line for the breakdown.</p>
  <div class="frame">{"".join(ov)}</div>

  <h2>Every idea, every relationship</h2>
  <p class="key"><span><i class="supports"></i>supports ({kinds["supports"]})</span><span><i class="tension"></i>pulls against ({kinds["tension"]})</span><span><i class="specializes"></i>is a narrower form of ({kinds["specializes"]})</span><span><i class="override"></i>rule overrides ({kinds["override"]})</span><span><i class="reading"></i>case is a reading of a book ({kinds["reading"]})</span><span>● owner's reading   ○ widely reported   ◆ Teamwork's synthesis</span></p>
  <div class="frame">{"".join(det)}</div>
  <p id="detailNote">Hover or focus an idea to read what it connects to.</p>
  <p class="lede">Books enter as Matthew's readings and widely reported ideas, never as quotations. The Decision OS cases are his readings of six of the seven books, which is why that cluster has so many lines back to the books. Nothing here has been tested with users.</p>
</main>
<dialog id="pop" aria-label="Idea details"></dialog>
<script type="application/json" id="popdata">{POP_JSON}</script>
<footer class="site-foot">
  <p>Built from server/library.json by docs/build-source-map.py.</p>
  <nav aria-label="Footer"><a href="/">Site</a><a href="/app/">Open the app</a><a href="/docs/question-map.html">How it reasons</a><a href="https://matthew-schmidt-production.up.railway.app/" rel="noopener">Matthew Schmidt</a></nav>
</footer>
<script src="/js/a11y.js" defer></script>
<script>
(function () {{
  var note = document.getElementById("detailNote");
  var edges = Array.prototype.slice.call(document.querySelectorAll(".detail .edge"));
  var nodes = Array.prototype.slice.call(document.querySelectorAll(".detail .node"));
  var labels = {{}};
  nodes.forEach(function (n) {{ labels[n.getAttribute("data-id")] = n.querySelector("title").textContent.split(" (")[0]; }});
  var pinned = null;
  function focus(id, pin) {{
    if (pin) pinned = id;
    if (id == null) id = pinned;
    var on = id != null; var touched = {{}};
    var lines = [];
    edges.forEach(function (e) {{
      var hit = on && (e.getAttribute("data-from") === id || e.getAttribute("data-to") === id);
      e.classList.toggle("on", hit); e.classList.toggle("off", on && !hit);
      if (hit) {{ touched[e.getAttribute("data-from")] = true; touched[e.getAttribute("data-to")] = true; lines.push(e.querySelector("title").textContent); }}
    }});
    nodes.forEach(function (n) {{ var nid = n.getAttribute("data-id"); n.classList.toggle("on", on && nid === id); n.classList.toggle("dim", on && !touched[nid] && nid !== id); }});
    note.textContent = on ? (lines.length ? lines.join(" ") : labels[id] + " has no drawn relationship; it is used by the screens directly.") : "Hover or focus an idea to read what it connects to.";
  }}
  window.__sm_focus = focus;
  nodes.forEach(function (n) {{
    var id = n.getAttribute("data-id");
    n.addEventListener("mouseenter", function () {{ focus(id); }});
    n.addEventListener("mouseleave", function () {{ focus(null); }});
    n.addEventListener("focus", function () {{ focus(id); }});
    n.addEventListener("blur", function () {{ focus(null); }});
  }});
}})();
{JS_EXTRA}
</script>
</body>
</html>
'''
(ROOT / "docs" / "source-map.html").write_text(html)
print(f"wrote docs/source-map.html: {len(P)} ideas, {len(R)} relations, {len(reading_edges)} reading edges; clusters {counts}")
