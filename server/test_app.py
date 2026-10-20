"""Tests for the Teamwork server. Run: python3 -m unittest discover -s server -p 'test_*.py'"""
import json
import re
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

    def test_library_digest_has_forces_and_no_cases(self):
        d = app.library_digest()
        self.assertIn("Awareness", d)
        # Cases are seat-bound, so they travel in the per-request slice and never in the cached prefix.
        for c in app.load_library()["cases"]:
            self.assertNotIn(c["principle"], d)


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
            self.assertIn(r["kind"], ("supports", "tension", "specializes", "override"))
        for d in self.lib["decision_science"]:
            self.assertIn(d["status"], ("owner_reading", "widely_reported", "synthesis"))

    def test_no_em_dash_in_library(self):
        self.assertNotIn(chr(8212), (HERE / "library.json").read_text())

    def test_stillward_quotes_are_short(self):
        for q in self.lib["stillward_lines"]["lines"]:
            self.assertLess(len(q["text"].split()), 15)


LIB = json.loads((HERE / "library.json").read_text())
PRINCIPLES = {p["id"]: p for p in LIB["principles"]}
STEPS_BY_ID = {s["id"]: s for s in LIB["steps"]}
SEATS = ("manager", "report", "peer", "team_lead", "team_member", "any")
# The who option that puts the user in a given seat, for building situations in tests.
WHO_FOR_SEAT = {"manager": "report", "report": "manager", "peer": "colleague",
                "team_lead": "team_lead", "team_member": "team_member", "any": "other"}


def label_of(step_id, option_id):
    for o in STEPS_BY_ID[step_id]["options"]:
        if o["id"] == option_id:
            return o["label"]
    raise KeyError(option_id)


def situation(who=None, what=None, need=None, want=None):
    labels = {"who": label_of("who", who) if who else None, "what": label_of("what", what) if what else None,
              "need": label_of("need", need) if need else None}
    sit = {"account": "x", "choices": labels}
    if want:
        sit["want"] = label_of("want", want)
    return sit


def request_text(step, sit):
    return app.build_request(step, sit)["messages"][0]["content"]


def links_for(step_id, option_id):
    option = [o for o in STEPS_BY_ID[step_id]["options"] if o["id"] == option_id][0]
    return option["links"]


class KnowledgeSlice(unittest.TestCase):
    def assert_idea_present(self, text, pid, context):
        p = PRINCIPLES[pid]
        self.assertIn(p["label"], text, "%s: label of %s" % (context, pid))
        self.assertIn(app.STATUS_WORDS[p["status"]], text, "%s: status of %s" % (context, pid))
        if p.get("misleads_when"):
            self.assertIn(p["misleads_when"], text, "%s: guard of %s" % (context, pid))

    def seat_ok(self, pid, seat):
        return PRINCIPLES[pid].get("seat", "any") in app.RECEIVES[seat]

    def test_every_chosen_answer_reaches_the_request(self):
        for sid in ("who", "what", "need", "want"):
            for o in STEPS_BY_ID[sid]["options"]:
                if o["id"] in ("other", "skip") and sid == "want":
                    continue
                if not o["links"]:
                    continue
                seats = {PRINCIPLES[l["id"]].get("seat", "any") for l in o["links"] if not l["id"].startswith(("rule.", "still."))}
                for seat in seats or {"any"}:
                    who = WHO_FOR_SEAT[seat]
                    if sid == "who":
                        sit = situation(who=o["id"])
                        user = app.WHO_SEAT[o["id"]]
                    else:
                        sit = situation(who=who, what=o["id"] if sid == "what" else None,
                                        need=o["id"] if sid == "need" else None, want=o["id"] if sid == "want" else None)
                        if sid == "want":
                            sit["choices"]["what"] = label_of("what", "missed")
                        user = app.WHO_SEAT[who]
                    for step in ("reflect", "read", "lookback") if sid != "want" else ("question", "read", "lookback"):
                        text = request_text(step, sit)
                        for l in o["links"]:
                            if l["id"].startswith(("rule.", "still.")) or not self.seat_ok(l["id"], user):
                                continue
                            self.assert_idea_present(text, l["id"], "%s.%s via %s as %s" % (sid, o["id"], step, user))

    def test_screens_being_written_reach_their_request(self):
        # The step-level and option-level links of the screens a model step writes, for a seatless person.
        written = {"reflect": ["reflect"], "question": ["question"], "read": ["read", "step", "post"],
                   "lookback": ["lookback_blind", "lookback_reveal", "lookback_inference"]}
        for step, screens in written.items():
            sit = situation(who="other")
            detail = app.slice_detail(step, sit)
            text = detail["text"]
            wanted = []
            for sid in screens:
                wanted += STEPS_BY_ID[sid]["links"]
                for o in STEPS_BY_ID[sid]["options"]:
                    wanted += o["links"]
            for l in wanted:
                pid = l["id"]
                if pid.startswith(("rule.", "still.")) or not self.seat_ok(pid, "any"):
                    continue
                if pid in detail["left_out"]:
                    continue  # the header says it was left out; the cap decides
                self.assert_idea_present(text, pid, "screens of %s" % step)
            self.assertIn("ideas shown", text)

    def test_slice_never_exceeds_the_cap(self):
        wants = [None, "know_where", "own_part"]
        for step in app.STEPS:
            for w in STEPS_BY_ID["who"]["options"]:
                for a in STEPS_BY_ID["what"]["options"]:
                    for n in STEPS_BY_ID["need"]["options"]:
                        for want in wants:
                            sit = situation(w["id"], a["id"], n["id"], want)
                            self.assertLessEqual(len(app.knowledge_slice(step, sit)), app.SLICE_CAP)

    def test_header_counts_what_was_left_out(self):
        sit = situation("manager", "shifted", "prepare", "know_where")
        d = app.slice_detail("read", sit)
        self.assertTrue(d["left_out"], "this crowded answer should overflow")
        self.assertIn("%d left out" % len(d["left_out"]), d["text"])

    def test_answer_level_ideas_survive_the_cap(self):
        # The ideas linked from the options tapped are never the ones dropped, except in the most crowded answers.
        dropped = 0
        total = 0
        for w in STEPS_BY_ID["who"]["options"]:
            for a in STEPS_BY_ID["what"]["options"]:
                for n in STEPS_BY_ID["need"]["options"]:
                    d = app.slice_detail("read", situation(w["id"], a["id"], n["id"]))
                    total += 1
                    dropped += bool([x for x in d["levels"]["answer"] if x not in d["shown"]])
        self.assertLess(dropped / total, 0.15)

    def test_cached_system_blocks_do_not_change_between_requests(self):
        a = app.build_request("read", situation("manager", "missed", "decide"))
        b = app.build_request("read", situation("colleague", "conduct", "escalate", "own_part"))
        c = app.build_request("lookback", {})
        self.assertEqual(json.dumps(a["system"]), json.dumps(b["system"]))
        self.assertEqual(json.dumps(a["system"]), json.dumps(c["system"]))
        self.assertEqual(a["system"][0]["text"], (HERE / "protocol.md").read_text(encoding="utf-8"))
        self.assertIn("cache_control", a["system"][1])
        self.assertNotEqual(a["messages"][0]["content"], b["messages"][0]["content"])
        user = a["messages"][0]["content"]
        self.assertLess(user.index("Step: read"), user.index("Knowledge slice"))

    def test_unknown_choices_fall_back_to_the_rules(self):
        for sit in ({}, {"choices": None}, {"choices": {"who": "a banana"}}, {"choices": {"who": 5, "what": None}},
                    {"choices": {"labels": "x"}}, {"choices": ["x"]}, {"want": "x"}):
            for step in app.STEPS:
                d = app.slice_detail(step, sit)
                self.assertEqual(d["shown"], [])
                self.assertIn("Standing rules", d["text"])
                self.assertIn("The safety flag", d["text"])
                self.assertNotIn("Ideas that govern", d["text"])
                app.build_request(step, sit)  # does not raise

    def test_labels_resolve_to_option_ids(self):
        d = app.resolve_choices({"choices": {"who": "My manager", "what": "They keep missing deadlines", "need": "To decide what to do"}})
        self.assertEqual(d, {"who": "manager", "what": "missed", "need": "decide"})
        self.assertEqual(app.resolve_choices({"choices": {"labels": {"who": "A team I\u2019m part of"}}}), {"who": "team_member"})
        self.assertEqual(app.resolve_want({"want": "I know where I stand. Mine is longer than that"}), ["know_where", "other"])

    def test_overrides_are_rendered_as_overrides(self):
        text = request_text("read", situation("manager", "missed", "decide"))
        self.assertIn("This overrides the others when it applies", text)

    def test_from_below_ideas_reach_a_report_and_no_case_does(self):
        below = [p for p in LIB["principles"] if p.get("seat") == "report"]
        self.assertGreaterEqual(len(below), 8)
        for needs in (("manager", "missed", "prepare"), ("manager", "shifted", "escalate"), ("manager", "dismissed", "understand")):
            sit = situation(*needs)
            self.assertEqual(app.slice_detail("read", sit)["seat"], "report")
            text = request_text("read", sit)
            for c in LIB["cases"]:
                self.assertNotIn(c["principle"], text)
            self.assertNotIn("Case, written for a manager", text)
        text = request_text("read", situation("manager", None, "prepare"))
        self.assertIn(PRINCIPLES["seat.upward_candour"]["label"], text)
        self.assertIn(PRINCIPLES["seat.ask_first"]["misleads_when"], text)

    def test_a_manager_gets_cases_and_not_the_from_below_set(self):
        sit = situation("report", "missed", "decide")
        self.assertEqual(app.slice_detail("read", sit)["seat"], "manager")
        text = request_text("read", sit)
        self.assertIn("Case, written for a manager", text)
        self.assertIn(PRINCIPLES["case.metrics-reward-the-wrong-thing"]["label"], text)
        for p in LIB["principles"]:
            if p.get("seat") == "report":
                self.assertNotIn(p["label"], text)

    def test_peers_get_peer_ideas_and_team_members_get_from_below(self):
        text = request_text("read", situation("colleague", "repeat", "prepare"))
        self.assertIn(PRINCIPLES["seat.peer_agreement"]["label"], text)
        self.assertNotIn(PRINCIPLES["seat.upward_candour"]["label"], text)
        self.assertNotIn("Case, written for a manager", text)
        text = request_text("read", situation("team_member", "repeat", "understand"))
        self.assertIn(PRINCIPLES["seat.decision_rights_gap"]["label"], text)
        self.assertNotIn("Case, written for a manager", text)
        text = request_text("read", situation("team_lead", "repeat", "understand"))
        self.assertIn(PRINCIPLES["case.team-agrees"]["label"], text)
        self.assertNotIn(PRINCIPLES["seat.decision_rights_gap"]["label"], text)

    def test_protocol_tells_the_advisor_about_seats(self):
        p = (HERE / "protocol.md").read_text()
        for phrase in ("escalation ladder", "agreement", "Module 3 cases", "overrides others"):
            self.assertIn(phrase, p)


class ContentAndLibraryAgree(unittest.TestCase):
    """Every screen and answer in js/content.js has a counterpart in library.steps."""

    def setUp(self):
        self.js = (HERE.parent / "js" / "content.js").read_text(encoding="utf-8")

    def section(self, start, end):
        a = self.js.index(start)
        return self.js[a:self.js.index(end, a)]

    def pairs(self, text):
        text = "\n".join(l for l in text.splitlines() if not l.strip().startswith("quiet:"))
        return re.findall(r'\["(\w+)", "([^"]+)"\]', text)

    def test_home_options_match_by_id_and_label(self):
        parts = {"who": self.section("    who: {", "    what: {"), "what": self.section("    what: {", "    need: {"),
                 "need": self.section("    need: {", "    detail: {")}
        for sid, text in parts.items():
            found = self.pairs(text)
            self.assertGreaterEqual(len(found), 5, sid)
            lib_ids = {o["id"]: o["label"] for o in STEPS_BY_ID[sid]["options"]}
            for oid, label in found:
                self.assertIn(oid, lib_ids, "%s.%s" % (sid, oid))
                self.assertEqual(lib_ids[oid], label)
            self.assertEqual({o for o, _ in found}, set(lib_ids))

    def test_team_seat_is_split(self):
        ids = [o for o, _ in self.pairs(self.section("    who: {", "    what: {"))]
        self.assertIn("team_lead", ids)
        self.assertIn("team_member", ids)
        self.assertNotIn("team", ids)

    def test_every_who_option_has_a_seat(self):
        for o in STEPS_BY_ID["who"]["options"]:
            self.assertIn(app.WHO_SEAT[o["id"]], SEATS)

    def test_screens_and_answers_exist_in_the_library(self):
        copy_to_steps = {"reflect": ["reflect"], "want": ["want"], "question": ["question"], "read": ["read"], "step": ["step"],
                         "post": ["post"], "conduct": ["conduct"], "lookback": ["lookback_blind", "lookback_reveal", "lookback_inference"],
                         "record": ["record"]}
        top = re.findall(r"^  (\w+): \{", self.js, re.M)
        for key, sids in copy_to_steps.items():
            self.assertIn(key, top)
            for sid in sids:
                self.assertIn(sid, STEPS_BY_ID, key)
        labels = lambda sid: {o["label"] for o in STEPS_BY_ID[sid]["options"]}  # noqa: E731
        want = re.search(r"want: \{.*?options: \[(.*?)\]", self.js, re.S).group(1)
        for text in re.findall(r'"([^"]+)"', want):
            self.assertIn(text, labels("want"))
        kinds = re.search(r"kinds: \{(.*?)\}", self.js, re.S).group(1)
        for text in re.findall(r'\w+: "([^"]+)"', kinds):
            self.assertIn(text, labels("read"))
        dates = re.search(r"dates: \[(.*?)\]\]", self.js, re.S).group(1)
        for n, text in re.findall(r'\["(\d+)", "([^"]+)"\]', dates + "]"):
            self.assertIn("d" + n, {o["id"] for o in STEPS_BY_ID["post"]["options"]})
            self.assertIn(text, labels("post"))
        feelings = re.search(r"feelings: \[(.*?)\]", self.js, re.S).group(1)
        for text in re.findall(r'"([^"]+)"', feelings):
            self.assertIn(text, labels("feel"))
        exits = re.search(r"exits: \{(.*?)\}", self.js, re.S).group(1)
        for text in re.findall(r'\w+: "([^"]+)"', exits):
            self.assertIn(text, labels("feel"))


class RelationRules(unittest.TestCase):
    BROAD = {"book", "loop", "lens"}
    NARROW = {"case", "habit", "rule"}

    def test_endpoints_exist_and_kinds_are_known(self):
        for r in LIB["relations"]:
            self.assertIn(r["from"], PRINCIPLES, r)
            self.assertIn(r["to"], PRINCIPLES, r)
            self.assertIn(r["kind"], ("supports", "specializes", "tension", "override"), r)

    def test_specializes_never_runs_from_broad_to_narrow(self):
        for r in LIB["relations"]:
            if r["kind"] == "specializes":
                self.assertFalse(PRINCIPLES[r["from"]]["kind"] in self.BROAD and PRINCIPLES[r["to"]]["kind"] in self.NARROW, r)

    def test_overrides_run_from_a_rule(self):
        overrides = [r for r in LIB["relations"] if r["kind"] == "override"]
        self.assertGreaterEqual(len(overrides), 4)
        for r in overrides:
            self.assertTrue(r["from"].startswith("rule."), r)

    def test_no_relation_contradicts_conflicts_with(self):
        pairs = set()
        for d in LIB["decision_science"]:
            for other in d["conflicts_with"]:
                pairs.add(frozenset((d["id"], other)))
        for r in LIB["relations"]:
            if frozenset((r["from"], r["to"])) in pairs:
                self.assertIn(r["kind"], ("tension", "override"), r)

    def test_no_duplicate_or_reversed_pairs(self):
        seen = set()
        for r in LIB["relations"]:
            key = frozenset((r["from"], r["to"]))
            self.assertNotIn(key, seen, r)
            self.assertNotEqual(r["from"], r["to"])
            seen.add(key)

    def test_every_relation_explains_itself(self):
        for r in LIB["relations"]:
            self.assertGreaterEqual(len(r["why"].split()), 8, r)

    def test_direction_note_is_in_the_schema_comment(self):
        for phrase in ("supports runs from the supporting idea to the supported one", "specializes runs from the narrower idea to the broader one",
                       "tension is symmetric", "override runs from the rule that wins to the idea it overrides"):
            self.assertIn(phrase, LIB["note"])

    def test_the_six_repaired_links_are_gone_or_rewritten(self):
        def has(step, option, pid):
            return any(l["id"] == pid for l in links_for(step, option))
        self.assertFalse(has("want", "know_where", "ds.power"))
        self.assertFalse(has("read", "distinguishing", "ds.base_rates"))
        self.assertFalse(has("what", "shifted", "ds.hindsight_outcome"))
        for l in links_for("step", "assumes"):
            self.assertNotIn("right amount", l["why"])
        for l in links_for("who", "colleague"):
            self.assertNotIn("more often safe", l["why"])


class Seats(unittest.TestCase):
    def test_every_case_has_the_manager_seat(self):
        cases = [p for p in LIB["principles"] if p["kind"] == "case"]
        self.assertEqual(len(cases), 30)
        for p in cases:
            self.assertEqual(p["seat"], "manager")
        for c in LIB["cases"]:
            self.assertEqual(c["seat"], "manager")

    def test_seat_values_are_known(self):
        for p in LIB["principles"]:
            self.assertIn(p.get("seat", "any"), SEATS, p["id"])

    def test_the_view_from_below_and_the_side(self):
        new = [p for p in LIB["principles"] if p["id"].startswith("seat.")]
        self.assertGreaterEqual(len(new), 10)
        for p in new:
            self.assertEqual(p["status"], "synthesis")
            self.assertEqual(p["lane"], "organizational_behaviour")
            self.assertTrue(p["applies_when"] and p["misleads_when"], p["id"])
            linked = any(l["id"] == p["id"] for s in LIB["steps"] for l in s["links"] + [x for o in s["options"] for x in o["links"]])
            self.assertTrue(linked, "%s should be linked from an answer" % p["id"])
        self.assertGreaterEqual(len([p for p in new if p["seat"] == "report"]), 6)
        self.assertGreaterEqual(len([p for p in new if p["seat"] == "peer"]), 2)
        self.assertGreaterEqual(len([p for p in new if p["seat"] == "team_member"]), 2)

    def test_no_em_dashes_in_new_text(self):
        self.assertNotIn(chr(8212), (HERE / "library.json").read_text())
        self.assertNotIn(chr(8212), (HERE / "app.py").read_text())


if __name__ == "__main__":
    unittest.main()
