#!/usr/bin/env python3
"""Build docs/question-map.html from server/library.json.

The map page is a single static file. The server hides /server/ from the browser, so the page cannot fetch
library.json. Instead this script reads server/library.json and writes the parts the map needs into the page,
between the DATA:START and DATA:END markers, as one inline JSON block. Everything else in question-map.html
(markup, CSS, JS) is hand-written and left alone.

Run after any change to server/library.json:

    python3 docs/build-map.py

Standard library only. Exits with an error if a step or relation points at a principle id that does not exist.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIB = HERE.parent / "server" / "library.json"
PAGE = HERE / "question-map.html"


def main():
    lib = json.loads(LIB.read_text(encoding="utf-8"))
    ids = {p["id"] for p in lib["principles"]}
    for s in lib["steps"]:
        for l in s["links"] + [x for o in s["options"] for x in o["links"]]:
            if l["id"] not in ids:
                sys.exit("unknown principle id in steps: %s" % l["id"])
    for r in lib["relations"]:
        if r["from"] not in ids or r["to"] not in ids:
            sys.exit("unknown principle id in relations: %s" % r)
    ds = {d["id"]: {"conflicts_with": d["conflicts_with"], "teamwork_use": d["teamwork_use"]} for d in lib["decision_science"]}
    data = {
        "version": lib["version"],
        "principles": lib["principles"],
        "steps": lib["steps"],
        "relations": lib["relations"],
        "ds_detail": ds,
        "stillward": lib["stillward_lines"]["lines"],
    }
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = PAGE.read_text(encoding="utf-8")
    pat = re.compile(r"(<!--DATA:START-->).*?(<!--DATA:END-->)", re.S)
    if not pat.search(html):
        sys.exit("markers not found in question-map.html")
    block = '<script type="application/json" id="data">%s</script>' % blob
    html = pat.sub(lambda m: m.group(1) + block + m.group(2), html)
    PAGE.write_text(html, encoding="utf-8")
    print("wrote %s (%d principles, %d steps, %d relations)" % (PAGE.name, len(data["principles"]), len(data["steps"]), len(data["relations"])))


if __name__ == "__main__":
    main()
