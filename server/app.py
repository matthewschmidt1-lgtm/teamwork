"""Teamwork server.

Serves the static site and answers POST /api/step by calling the Claude API with the
protocol in server/protocol.md and the principle library in server/library.json.
Standard library only. Stores nothing. Logs method, path, status and duration, never content.

    ANTHROPIC_API_KEY=... python3 server/app.py     # real model
    TEAMWORK_MOCK=1 python3 server/app.py           # canned answers from server/fixtures/
"""
import json
import os
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


def library_digest():
    """A compact rendering of the library for the system prompt."""
    lib = json.loads(load_text("library.json"))
    lines = ["## Principle library (synthesis; attribute lightly, never as proof)", ""]
    lines.append("Forces, each with pattern, move and the question to ask:")
    for f in lib["forces"].values():
        lines.append("- %s. Pattern: %s Move: %s Ask: %s" % (f["name"], f["pattern"], f["move"], f["ask"]))
    lines.append("")
    lines.append("Management cases, each a principle with the two values in tension and the lesson behind it:")
    for c in lib["cases"]:
        lens = c["lens"]["lesson"] if c.get("lens") else ""
        tension = c["tension"]["lesson"] if c.get("tension") else ""
        lines.append("- %s. Pause: %s Next move: %s Behind it: %s Pulling the other way: %s"
                     % (c["principle"], c["pause"], c["next_move"], lens, tension))
    return "\n".join(lines)


def build_request(step, situation):
    """The JSON body for the Messages API. Pure, so it can be tested without a key."""
    if step not in STEPS:
        raise ValueError("unknown step")
    system = [
        {"type": "text", "text": load_text("protocol.md")},
        {"type": "text", "text": library_digest(), "cache_control": {"type": "ephemeral"}},
    ]
    user = STEP_INSTRUCTIONS[step] + "\n\nEverything the person has given so far, as JSON:\n" + \
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
