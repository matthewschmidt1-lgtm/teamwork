"""Tests for the Teamwork server. Run: python3 -m unittest discover -s server -p 'test_*.py'"""
import json
import unittest
from pathlib import Path

import app

HERE = Path(__file__).resolve().parent


def validate(value, schema, path="$"):
    """A small JSON Schema checker for the subset the server uses."""
    t = schema.get("type")
    if "enum" in schema:
        assert value in schema["enum"], "%s not in enum" % path
    if t == "object":
        assert isinstance(value, dict), "%s not object" % path
        for k in schema.get("required", []):
            assert k in value, "%s missing %s" % (path, k)
        if schema.get("additionalProperties") is False:
            extra = set(value) - set(schema["properties"])
            assert not extra, "%s extra keys %s" % (path, extra)
        for k, v in value.items():
            validate(v, schema["properties"][k], path + "." + k)
    elif t == "array":
        assert isinstance(value, list), "%s not array" % path
        for i, v in enumerate(value):
            validate(v, schema["items"], "%s[%d]" % (path, i))
    elif t == "string":
        assert isinstance(value, str), "%s not string" % path
    elif t == "boolean":
        assert isinstance(value, bool), "%s not boolean" % path


class Fixtures(unittest.TestCase):
    def test_every_fixture_matches_its_schema(self):
        for f in sorted((HERE / "fixtures").glob("*.json")):
            step = f.stem.split("_")[0]
            validate(json.loads(f.read_text()), app.SCHEMAS[step], f.name)

    def test_mock_routes_conduct_cases(self):
        r = app.mock_answer("reflect", {"account": "He suggested we discuss my review over drinks"})
        self.assertTrue(r["safety_flag"])
        r = app.mock_answer("reflect", {"account": "My boss cut me off twice"})
        self.assertFalse(r["safety_flag"])

    def test_read_fixture_keeps_a_non_character_explanation(self):
        r = json.loads((HERE / "fixtures" / "read.json").read_text())
        self.assertTrue(any(e["kind"] == "system" for e in r["explanations"]))


class Request(unittest.TestCase):
    def test_build_request_shape(self):
        body = app.build_request("read", {"account": "x"})
        self.assertEqual(body["model"], app.MODEL)
        self.assertEqual(body["output_config"]["format"]["type"], "json_schema")
        self.assertEqual(body["output_config"]["effort"], "high")
        self.assertEqual(body["fallbacks"], "default")
        self.assertIn("cache_control", body["system"][-1])
        self.assertIn("Step: read", body["messages"][0]["content"])
        self.assertNotIn("thinking", body)
        self.assertNotIn("tool_choice", body)

    def test_unknown_step_rejected(self):
        with self.assertRaises(ValueError):
            app.build_request("diagnose", {})

    def test_parse_response_reads_first_text_block(self):
        data = {"stop_reason": "end_turn", "content": [{"type": "thinking", "thinking": ""}, {"type": "text", "text": "{\"a\": 1}"}]}
        self.assertEqual(app.parse_response(data), {"a": 1})

    def test_parse_response_raises_on_refusal(self):
        with self.assertRaises(RuntimeError):
            app.parse_response({"stop_reason": "refusal", "content": []})

    def test_library_digest_mentions_forces_and_cases(self):
        d = app.library_digest()
        self.assertIn("Awareness", d)
        self.assertIn("Before you explain a person, rule out the situation.", d)


class Static(unittest.TestCase):
    def test_root_is_the_site_and_app_is_the_app(self):
        self.assertEqual(app.safe_static_path("/").relative_to(app.ROOT).as_posix(), "site/index.html")
        self.assertEqual(app.safe_static_path("/app/").relative_to(app.ROOT).as_posix(), "index.html")
        self.assertEqual(app.safe_static_path("/app").relative_to(app.ROOT).as_posix(), "index.html")

    def test_server_folder_and_dotfiles_hidden(self):
        self.assertIsNone(app.safe_static_path("/server/protocol.md"))
        self.assertIsNone(app.safe_static_path("/.gitignore"))
        self.assertIsNone(app.safe_static_path("/../etc/passwd"))

    def test_query_string_ignored(self):
        self.assertEqual(app.safe_static_path("/app/?who=manager").relative_to(app.ROOT).as_posix(), "index.html")


class Headers(unittest.TestCase):
    def test_security_headers_present(self):
        for k in ("Content-Security-Policy", "X-Frame-Options", "X-Content-Type-Options", "Referrer-Policy", "Permissions-Policy"):
            self.assertIn(k, app.Handler.SECURITY)
        self.assertIn("fonts.gstatic.com", app.Handler.SECURITY["Content-Security-Policy"])
        self.assertTrue(hasattr(app.Handler, "do_HEAD"))


class Copy(unittest.TestCase):
    def test_no_em_dashes_in_protocol_or_fixtures(self):
        for f in [HERE / "protocol.md"] + list((HERE / "fixtures").glob("*.json")):
            self.assertNotIn(chr(8212), f.read_text(), f.name)

    def test_protocol_has_the_standing_rules(self):
        p = (HERE / "protocol.md").read_text()
        for phrase in ("Never diagnose the absent person", "rule out the situation", "safety flag", "can't tell"):
            self.assertIn(phrase, p)


class LibraryV2(unittest.TestCase):
    def setUp(self):
        self.lib = json.loads((HERE / "library.json").read_text())

    def test_new_keys_and_old_keys(self):
        for k in ("forces", "cases", "habits", "skills", "before_questions", "books", "friction_states",
                  "loops", "lenses", "path", "books_takeaways", "stillward_lines", "algorithms",
                  "decision_science", "steps", "relations", "principles"):
            self.assertIn(k, self.lib)
        self.assertEqual(self.lib["version"], 2)
        self.assertEqual(len(self.lib["decision_science"]), 10)
        self.assertGreaterEqual(len(self.lib["relations"]), 40)

    def test_every_link_points_at_a_principle(self):
        ids = {p["id"] for p in self.lib["principles"]}
        for s in self.lib["steps"]:
            for l in s["links"] + [x for o in s["options"] for x in o["links"]]:
                self.assertIn(l["id"], ids)
                self.assertTrue(l["why"])
        for r in self.lib["relations"]:
            self.assertIn(r["from"], ids)
            self.assertIn(r["to"], ids)
            self.assertIn(r["kind"], ("supports", "tension", "specializes"))
        for d in self.lib["decision_science"]:
            self.assertIn(d["status"], ("owner_reading", "widely_reported", "synthesis"))

    def test_no_em_dash_in_library(self):
        self.assertNotIn(chr(8212), (HERE / "library.json").read_text())

    def test_stillward_quotes_are_short(self):
        for q in self.lib["stillward_lines"]["lines"]:
            self.assertLess(len(q["text"].split()), 15)


if __name__ == "__main__":
    unittest.main()
