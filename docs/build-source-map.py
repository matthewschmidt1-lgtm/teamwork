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
    ov.append(f'<g class="ov-node"><circle cx="{x:.0f}" cy="{y:.0f}" r="58" fill="{COLOR[mid]}"/>'
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
    det.append(f'<g class="node" data-id="{esc(pid)}" tabindex="0"><rect x="{nx:.0f}" y="{ny:.0f}" width="{NODE_W}" height="{NODE_H}" rx="6" stroke="{COLOR[material(p)]}"/>'
               f'<text x="{nx + 8:.0f}" y="{ny + 17:.0f}" class="node-label"><tspan class="mark">{mark}</tspan> {esc(label)}</text>'
               f'<title>{esc(p["label"])} ({esc(p["kind"])}, {esc(p["status"].replace("_", " "))}). {esc(p["summary"])} Source: {esc(p["source"])}</title></g>')
det.append("</svg>")

counts = {m: len(groups[m]) for m, _, _ in MATERIALS}
kinds = defaultdict(int)
for e in edges: kinds[e["kind"]] += 1

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
  .key i.tension {{ border-top:2px dashed #A9533F; }} .key i.specializes {{ border-top:2px dotted #5B4B8A; }} .key i.supports {{ border-top-color:#2F6F5E; }} .key i.reading {{ border-top:2px solid #8A6D3B; opacity:.6; }}
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
  .edge.supports {{ stroke:#2F6F5E; }} .edge.tension {{ stroke:#A9533F; stroke-dasharray:6 4; }} .edge.specializes {{ stroke:#5B4B8A; stroke-dasharray:2 3; }} .edge.reading {{ stroke:#8A6D3B; opacity:.25; }}
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
  <p class="lede">Seven materials feed the advisor. The first drawing shows how much each pair of materials speaks to the others. The second draws every idea in the library and every relationship between them. Hover or focus a node to see its own connections; hover a line to read why it is there.</p>
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
  <p class="key"><span><i class="supports"></i>supports ({kinds["supports"]})</span><span><i class="tension"></i>pulls against ({kinds["tension"]})</span><span><i class="specializes"></i>is a narrower form of ({kinds["specializes"]})</span><span><i class="reading"></i>case is a reading of a book ({kinds["reading"]})</span><span>● owner's reading   ○ widely reported   ◆ Teamwork's synthesis</span></p>
  <div class="frame">{"".join(det)}</div>
  <p id="detailNote">Hover or focus an idea to read what it connects to.</p>
  <p class="lede">Books enter as Matthew's readings and widely reported ideas, never as quotations. The Decision OS cases are his readings of six of the seven books, which is why that cluster has so many lines back to the books. Nothing here has been tested with users.</p>
</main>
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
  function focus(id) {{
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
  nodes.forEach(function (n) {{
    var id = n.getAttribute("data-id");
    n.addEventListener("mouseenter", function () {{ focus(id); }});
    n.addEventListener("mouseleave", function () {{ focus(null); }});
    n.addEventListener("focus", function () {{ focus(id); }});
    n.addEventListener("blur", function () {{ focus(null); }});
  }});
}})();
</script>
</body>
</html>
'''
(ROOT / "docs" / "source-map.html").write_text(html)
print(f"wrote docs/source-map.html: {len(P)} ideas, {len(R)} relations, {len(reading_edges)} reading edges; clusters {counts}")
