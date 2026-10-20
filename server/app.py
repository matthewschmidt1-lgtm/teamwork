"""Teamwork server.

Serves the static site and answers POST /api/step by calling the Claude API with the
protocol in server/protocol.md and the principle library in server/library.json.
Standard library only. Stores nothing. Logs method, path, status and duration, never content.

    ANTHROPIC_API_KEY=... python3 server/app.py     # real model
    TEAMWORK_MOCK=1 python3 server/app.py           # canned answers from server/fixtures/
"""
import functools
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVER_DIR = Path(__file__).resolve().parent
MODEL = os.environ.get("TEAMWORK_MODEL", "claude-opus-5-5")
API_URL = "https://api.anthropic.com/v1/messages"
MAX_BODY = 64 * 1024
STEPS = ("reflect", "question", "read", "lookback")
EFFORT = {"reflect": "medium", "question": "medium", "read": "high", "lookback": "medium"}

STRING = {"type": "string"}
STRINGS = {"type": "array", "items": STRING}


def obj(props, required=None):
    return {
        "type": "object",
        "properties": props,
        "required": required if required is not None else list(props.keys()),
        "additionalProperties": False,
    }


SCHEMAS = {
    "reflect": obj({
        "happened": STRINGS,
        "told": STRINGS,
        "concluded": STRINGS,
        "safety_flag": {"type": "boolean"},
        "safety_kind": STRING,
        "echo": STRING,
    }),
    "question": obj({
        "ask": {"type": "boolean"},
        "question": STRING,
        "why": STRING,
        "options": STRINGS,
    }),
    "read": obj({
        "explanations": {
            "type": "array",
            "items": obj({
                "text": STRING,
                "kind": {"type": "string", "enum": ["person", "self", "system"]},
                "supports": STRINGS,
                "distinguishing": STRING,
            }),
        },
        "self_question": STRING,
        "influence": STRING,
        "step": obj({
            "name": STRING, "what": STRING, "why": STRING,
            "assumes": STRING, "backfires": STRING, "alternative": STRING,
        }),
        "words": STRINGS,
        "post": STRING,
        "manager_questions": {"type": "boolean"},
        "tension": STRING,
    }),
    "lookback": obj({
        "matched": {"type": "string", "enum": ["yes", "partly", "no", "cant_tell"]},
        "comparison": STRING,
        "inference": STRING,
        "lesson_prompt": STRING,
        "pattern_tags": STRINGS,
    }),
}

STEP_INSTRUCTIONS = {
    "reflect": "Step: reflect. Sort the account below into happened, told and concluded, set the safety flag only under rule 11, and write the echo.",
    "question": "Step: question. Decide whether one question would change your advice. If not, set ask to false and leave question empty.",
    "read": "Step: read. Give the explanations, the self question, influence, one step with its assumption, risk and alternative, the words, and the post.",
    "lookback": "Step: lookback. Compare what the person wrote then with what they say now, be honest about what one outcome can tell, and invite a lesson.",
}


def load_text(name):
    return (SERVER_DIR / name).read_text(encoding="utf-8")


@functools.lru_cache(maxsize=1)
def load_library():
    return json.loads(load_text("library.json"))


def library_digest():
    """The general part of the library, the same for every request, so it can sit in the cached prefix.

    Cases are not here. They are seat-bound (Module 3 is written from the manager's side), so they
    arrive per request in the knowledge slice, only for the seats they suit.
    """
    lib = load_library()
    lines = ["## Principle library (synthesis; attribute lightly, never as proof)", ""]
    lines.append("Forces, each with pattern, move and the question to ask:")
    for f in lib["forces"].values():
        lines.append("- %s. Pattern: %s Move: %s Ask: %s" % (f["name"], f["pattern"], f["move"], f["ask"]))
    return "\n".join(lines)


# ---------------------------------------------------------------------------------------------
# The knowledge slice: the part of the library that governs this one answer, built per request.
# It rides in the user message, after the step instruction, so the cached system prefix never changes.
# ---------------------------------------------------------------------------------------------

SLICE_CAP = 6000
STATUS_WORDS = {
    "owner_reading": "the owner's reading",
    "widely_reported": "widely reported, not checked against a text",
    "synthesis": "Teamwork's synthesis",
}

# Which seat the user holds, from the option they tapped on "Who is this about?". "My manager" means
# the user reports to the other party, so the user's seat is report; "Someone I manage" makes them the manager.
WHO_SEAT = {"manager": "report", "report": "manager", "colleague": "peer",
            "team_lead": "team_lead", "team_member": "team_member", "other": "any"}
# Which idea seats a user seat receives. Module 3 cases are tagged manager, so only a manager or a team
# lead gets them; the from-below ideas (tagged report) reach a report or a team member.
RECEIVES = {
    "manager": {"manager", "any"},
    "team_lead": {"team_lead", "manager", "any"},
    "report": {"report", "any"},
    "team_member": {"team_member", "report", "peer", "any"},
    "peer": {"peer", "any"},
    "any": {"any"},
}

# For each model step: the earlier screens the person has passed, and the screens being written now.
SCREENS = {
    "reflect": (("who", "what", "need", "detail"), ("reflect",)),
    "question": (("who", "what", "need", "detail", "reflect", "want"), ("question",)),
    "read": (("who", "what", "need", "detail", "reflect", "want"), ("read", "step", "post")),
    "lookback": (("who", "what", "need", "detail", "reflect", "want", "read", "step", "post"),
                 ("lookback_blind", "lookback_reveal", "lookback_inference")),
}
CHOICE_SCREENS = ("who", "what", "need")


def _norm(text):
    return " ".join(str(text).replace("\u2019", "'").lower().split()).rstrip(".")


def _screen(lib, step_id):
    for st in lib["steps"]:
        if st["id"] == step_id:
            return st
    return None


def resolve_choices(situation):
    """Option ids for who, what and need from the tapped labels. Unknown or missing ones are left out."""
    lib = load_library()
    ch = situation.get("choices") if isinstance(situation, dict) else None
    if isinstance(ch, dict) and isinstance(ch.get("labels"), dict):
        ch = ch["labels"]
    found = {}
    if not isinstance(ch, dict):
        return found
    for sid in CHOICE_SCREENS:
        value = ch.get(sid)
        screen = _screen(lib, sid)
        if not isinstance(value, str) or not screen:
            continue
        for o in screen["options"]:
            if _norm(value) in (_norm(o["label"]), o["id"]):
                found[sid] = o["id"]
                break
    return found


def resolve_want(situation):
    """Option ids on the want screen that the person's words match, plus 'other' for free text."""
    text = situation.get("want") if isinstance(situation, dict) else None
    if not isinstance(text, str) or not text.strip():
        return []
    screen = _screen(load_library(), "want")
    rest = _norm(text)
    ids = []
    for o in screen["options"]:
        if o["id"] in ("other", "skip"):
            continue
        label = _norm(o["label"])
        if label in rest:
            ids.append(o["id"])
            rest = rest.replace(label, " ")
    if re.search(r"[a-z]", rest):
        ids.append("other")
    return ids


def user_seat(choices):
    return WHO_SEAT.get(choices.get("who"), "any")


def _seat_ok(principle, seat):
    return principle.get("seat", "any") in RECEIVES.get(seat, {"any"})


def _clip(text, n):
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0].rstrip(",;:") + "..."


def _render_idea(p, whys, cases_by_id, density="full"):
    """One idea as a short block: label, status in words, summary, guards, and why it matters here.

    density 'full' adds applies_when; 'compact' keeps label, status, a clipped summary, the guard and the
    why; 'whole' is for the safety flag and clips nothing. The guard (misleads_when) is never clipped.
    """
    status = STATUS_WORDS.get(p.get("status"), "status not given")
    clip = (lambda t, n: t) if density == "whole" else _clip
    if p["kind"] == "case":
        c = cases_by_id.get(p["id"][len("case."):], {})
        bits = ["Case, written for a manager's seat: %s (%s)." % (p["label"], status)]
        if p.get("pause"):
            bits.append("Pause: %s" % p["pause"])
        bits.append("Next move: %s" % p["summary"])
        if density == "full" and (c.get("lens") or {}).get("lesson"):
            bits.append("Behind it: %s" % c["lens"]["lesson"])
        if (c.get("tension") or {}).get("lesson"):
            bits.append("Pulling the other way: %s" % c["tension"]["lesson"])
    else:
        bits = ["%s (%s): %s" % (p["label"], status, clip(p["summary"], 170 if density == "full" else 110))]
        if density == "full" and p.get("applies_when"):
            bits.append("Applies when: %s" % clip(p["applies_when"], 150))
        if p.get("misleads_when"):
            bits.append("Misleads when: %s" % p["misleads_when"])
    if whys:
        bits.append("Here: %s" % " ".join(whys))
    return "- " + " ".join(bits)


def _render_relation(r, label):
    a, b = label(r["from"]), label(r["to"])
    if r["kind"] == "supports":
        return "- %s supports %s: %s" % (a, b, r["why"])
    if r["kind"] == "specializes":
        return "- %s is a narrower form of %s: %s" % (a, b, r["why"])
    return "- %s and %s pull against each other: %s" % (a, b, r["why"])


def _gather(step, situation, choices, seat, P):
    """Ideas linked from this answer, by level: 'answer' (the options the person tapped), 'step'
    (links on the screens being written, and on the reflect screen), 'part' (options of the screens
    being written). Each maps id -> list of why-sentences. Seat-bound ideas for other seats are dropped."""
    lib = load_library()
    passed, current = SCREENS[step]
    levels = {"answer": {}, "step": {}, "part": {}}
    if not choices:
        return levels
    selected = {sid: [oid] for sid, oid in choices.items()}
    selected["want"] = resolve_want(situation)

    def add(level, link):
        p = P.get(link["id"])
        if not p or p["kind"] in ("rule", "stillward") or not _seat_ok(p, seat):
            return
        whys = levels[level].setdefault(link["id"], [])
        if link["why"] not in whys:
            whys.append(link["why"])

    for sid in passed + current:
        screen = _screen(lib, sid)
        if not screen:
            continue
        if sid in current or sid == "reflect":
            for l in screen["links"]:
                add("step", l)
        for o in screen["options"]:
            if o["id"] in selected.get(sid, []):
                for l in o["links"]:
                    add("answer", l)
            elif sid in current:
                for l in o["links"]:
                    add("part", l)
    return levels


def knowledge_slice(step, situation):
    return slice_detail(step, situation)["text"]


def slice_detail(step, situation):
    """The slice of the library that governs this answer, at most SLICE_CAP characters.

    Always: the safety flag and the standing rules. Then, while room lasts: the ideas linked from the
    options the person tapped (answer level), the tensions and overrides among them, the ideas linked
    from the screens being written (step level), and the remaining relations. Cases reach only a manager
    or team lead; from-below ideas only a report or team member. Unknown choices give the rules alone.
    """
    lib = load_library()
    P = {p["id"]: p for p in lib["principles"]}
    cases_by_id = {c["id"]: c for c in lib["cases"]}
    situation = situation if isinstance(situation, dict) else {}
    choices = resolve_choices(situation)
    seat = user_seat(choices)
    levels = _gather(step, situation, choices, seat, P)
    rules = [p for p in lib["principles"] if p["kind"] == "rule"]
    label = lambda pid: P[pid]["label"]  # noqa: E731

    budget = [SLICE_CAP - 330]  # room for the header, the section titles and the blank lines

    def take(text):
        if len(text) + 1 <= budget[0]:
            budget[0] -= len(text) + 1
            return True
        return False

    safety_text = "Safety (this overrides everything below when it applies):\n" + _render_idea(P["rule.safety_flag"], [], cases_by_id, "whole")
    rules_text = "Standing rules, always in force (the protocol holds the detail): " + \
        "; ".join(r["label"] for r in rules if r["id"] != "rule.safety_flag") + "."
    take(safety_text)
    take(rules_text)

    shown, left_out, lines = [], [], {}

    def why_text(whys):
        return [_clip(whys[0], 230)] + ([_clip(whys[1], 140)] if len(whys) > 1 and len(whys[0]) < 200 else [])

    def add_ideas(level):
        for pid, whys in levels[level].items():
            if pid in shown or pid in left_out:
                continue
            line = _render_idea(P[pid], why_text(whys), cases_by_id, "compact")
            if take(line):
                shown.append(pid)
                lines[pid] = line
            else:
                left_out.append(pid)

    def enrich(level):
        """Spend what is left on fuller renderings of the answer-level ideas, in order."""
        for pid in [x for x in shown if x in levels[level]]:
            full = _render_idea(P[pid], why_text(levels[level][pid]), cases_by_id, "full")
            extra = len(full) - len(lines[pid])
            if extra <= 0:
                continue
            if extra <= budget[0]:
                budget[0] -= extra
                lines[pid] = full

    rel_lines, used_rel, announced = [], set(), set()

    def add_relations(kinds):
        universe = set(shown) | {r["id"] for r in rules}
        todo = [(i, r) for i, r in enumerate(lib["relations"])
                if i not in used_rel and r["kind"] in kinds and r["from"] in universe and r["to"] in universe
                and not (r["from"].startswith("rule.") and r["to"].startswith("rule.") and r["kind"] != "override")]
        if "override" in kinds:
            groups = {}
            for i, r in todo:
                if r["kind"] == "override":
                    groups.setdefault(r["from"], []).append((i, r))
            for src, rs in groups.items():
                lead = "- %s: This overrides the others when it applies. It overrides" % label(src) if src not in announced \
                    else "- %s also overrides" % label(src)
                line = "%s %s." % (lead, "; ".join(label(r["to"]) for _, r in rs))
                if take(line):
                    rel_lines.append(line)
                    announced.add(src)
                    used_rel.update(i for i, _ in rs)
        for i, r in todo:
            if r["kind"] != "override" and r["kind"] in kinds:
                line = _render_relation(r, label)
                if take(line):
                    rel_lines.append(line)
                    used_rel.add(i)

    add_relations(("override",))  # the safety flag over the standing rules comes before any idea
    add_ideas("answer")
    add_relations(("override", "tension"))
    add_ideas("step")
    enrich("answer")
    add_ideas("part")
    add_relations(("override", "tension", "specializes", "supports"))

    head = "Knowledge slice for this answer (the person's seat: %s). %d ideas shown" % (seat, len(shown))
    if left_out:
        head += ", %d left out to stay within the limit" % len(left_out)
    head += ". Weigh each idea by its status. Its guard says when it misleads."
    parts = [head, safety_text, rules_text]
    if shown:
        parts.append("Ideas that govern this answer:\n" + "\n".join(lines[x] for x in shown))
    if rel_lines:
        parts.append("How they relate:\n" + "\n".join(rel_lines))
    text = "\n\n".join(parts)
    while len(text) > SLICE_CAP and rel_lines:  # belt and braces: never past the cap, drop relations first
        rel_lines.pop()
        parts[-1] = "How they relate:\n" + "\n".join(rel_lines)
        text = "\n\n".join(parts)
    return {"text": text[:SLICE_CAP], "seat": seat, "choices": choices, "levels": levels,
            "shown": shown, "left_out": left_out}


def build_request(step, situation):
    """The JSON body for the Messages API. Pure, so it can be tested without a key."""
    if step not in STEPS:
        raise ValueError("unknown step")
    system = [
        {"type": "text", "text": load_text("protocol.md")},
        {"type": "text", "text": library_digest(), "cache_control": {"type": "ephemeral"}},
    ]
    user = STEP_INSTRUCTIONS[step] + "\n\n" + knowledge_slice(step, situation) + \
        "\n\nEverything the person has given so far, as JSON:\n" + \
        json.dumps(situation, ensure_ascii=False, indent=1)
    return {
        "model": MODEL,
        "max_tokens": 4000,
        "system": system,
        "messages": [{"role": "user", "content": user}],
        "output_config": {
            "effort": EFFORT[step],
            "format": {"type": "json_schema", "schema": SCHEMAS[step]},
        },
        "fallbacks": "default",
    }


def parse_response(data):
    """Pull the structured object out of a Messages API response."""
    if data.get("stop_reason") == "refusal":
        raise RuntimeError("declined")
    for block in data.get("content", []):
        if block.get("type") == "text":
            return json.loads(block["text"])
    raise RuntimeError("no text block")


def call_model(step, situation, api_key):
    body = json.dumps(build_request(step, situation)).encode("utf-8")
    req = urllib.request.Request(API_URL, data=body, method="POST", headers={
        "content-type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "server-side-fallback-2026-07-01",
    })
    with urllib.request.urlopen(req, timeout=120) as resp:
        return parse_response(json.loads(resp.read().decode("utf-8")))


def mock_answer(step, situation):
    """Canned answers for UI work and tests. Picks the conduct fixture on a few cue words."""
    name = step
    if step == "reflect":
        text = (situation.get("account") or "").lower()
        if any(w in text for w in ("drinks", "what i wear", "harass", "retaliat", "discriminat")):
            name = "reflect_conduct"
    return json.loads(load_text("fixtures/%s.json" % name))


MIME = {
    ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8", ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml", ".png": "image/png", ".ico": "image/x-icon",
    ".md": "text/markdown; charset=utf-8", ".txt": "text/plain; charset=utf-8",
    ".woff2": "font/woff2", ".ics": "text/calendar; charset=utf-8",
}


def safe_static_path(url_path):
    """Map a URL path to a file under ROOT, or None. Never serves server/ or dotfiles."""
    path = url_path.split("?", 1)[0].split("#", 1)[0]
    if path == "/" or path == "":
        path = "/site/index.html"
    if path in ("/app", "/app/"):
        path = "/index.html"
    parts = [p for p in path.split("/") if p]
    if any(p in ("..", "") or p.startswith(".") for p in parts):
        return None
    if parts and parts[0] == "server":
        return None
    target = ROOT.joinpath(*parts)
    if target.is_dir():
        target = target / "index.html"
    try:
        target.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return None
    return target if target.is_file() else None


class Handler(BaseHTTPRequestHandler):
    server_version = "Teamwork/0.1"

    def log_message(self, fmt, *args):  # quiet default logging; we log in finish_request
        pass

    SECURITY = {
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "no-referrer",
        "X-Frame-Options": "DENY",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                                   "font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
    }

    def _send(self, status, body, ctype="application/json; charset=utf-8", extra=None):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in self.SECURITY.items():
            self.send_header(k, v)
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_HEAD(self):
        self.do_GET()

    def _json(self, status, payload):
        self._send(status, json.dumps(payload).encode("utf-8"))

    def do_GET(self):
        t0 = time.time()
        if self.path.startswith("/api/health"):
            mode = "mock" if os.environ.get("TEAMWORK_MOCK") else ("live" if os.environ.get("ANTHROPIC_API_KEY") else "no-key")
            self._json(200, {"ok": True, "mode": mode, "model": MODEL})
            return self._log(200, t0)
        target = safe_static_path(self.path)
        if not target:
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return self._log(404, t0)
        ctype = MIME.get(target.suffix.lower(), "application/octet-stream")
        cache = "no-cache" if target.suffix in (".html", ".js", ".css") else "public, max-age=86400"
        self._send(200, target.read_bytes(), ctype, {"Cache-Control": cache})
        self._log(200, t0)

    def do_POST(self):
        t0 = time.time()
        if self.path.split("?")[0] != "/api/step":
            self._json(404, {"error": "not found"})
            return self._log(404, t0)
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_BODY:
            self._json(413, {"error": "That is more than this can read at once. Try a shorter account."})
            return self._log(413, t0)
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            step = payload.get("step")
            situation = payload.get("situation") or {}
            if step not in STEPS or not isinstance(situation, dict):
                raise ValueError
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
            self._json(400, {"error": "The request was not in a shape this understands."})
            return self._log(400, t0)

        try:
            if os.environ.get("TEAMWORK_MOCK"):
                time.sleep(0.4)
                result = mock_answer(step, situation)
            else:
                key = os.environ.get("ANTHROPIC_API_KEY")
                if not key:
                    self._json(503, {"error": "The advisor is not connected on this server. Your words are still here."})
                    return self._log(503, t0)
                result = call_model(step, situation, key)
            self._json(200, {"step": step, "result": result})
            self._log(200, t0)
        except urllib.error.HTTPError as e:
            status = 502 if e.code != 429 else 429
            msg = "The advisor is busy. Try again in a moment." if e.code == 429 else "The advisor did not answer. Your words are still here."
            self._json(status, {"error": msg})
            self._log(status, t0, "upstream %s" % e.code)
        except RuntimeError as e:
            if str(e) == "declined":
                self._json(422, {"error": "The advisor could not take this one on. If someone's safety or job is at risk, the people who can act are listed below.", "declined": True})
                return self._log(422, t0)
            self._json(502, {"error": "The advisor's answer did not arrive in one piece. Try again."})
            self._log(502, t0, str(e))
        except Exception as e:  # noqa: BLE001
            self._json(502, {"error": "The advisor did not answer. Your words are still here."})
            self._log(502, t0, type(e).__name__)

    def _log(self, status, t0, note=""):
        sys.stdout.write("%s %s %s %dms %s\n" % (self.command, self.path.split("?")[0], status, int((time.time() - t0) * 1000), note))
        sys.stdout.flush()


def main():
    port = int(os.environ.get("PORT", "8975"))
    httpd = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    mode = "mock" if os.environ.get("TEAMWORK_MOCK") else ("live" if os.environ.get("ANTHROPIC_API_KEY") else "no key")
    print("Teamwork on http://localhost:%d (%s, %s)" % (port, mode, MODEL))
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
