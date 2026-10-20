// Browser tests for the pure modules. Open /tests/run.html; the title reads PASS n/n or FAIL.
import { COPY } from "../js/content.js";
import * as store from "../js/store.js";
import { pageText, icsFor, moveLine, cleanSorted, addDays, toISODate } from "../js/text.js";
import { payload } from "../js/api.js";

const out = document.getElementById("out");
let pass = 0, total = 0;
function test(name, fn) {
  total++;
  try { fn(); pass++; out.append(Object.assign(document.createElement("li"), { className: "ok", textContent: name })); }
  catch (e) { out.append(Object.assign(document.createElement("li"), { className: "fail", textContent: name + ": " + e.message })); }
}
const eq = (a, b, m) => { if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error((m || "") + " expected " + JSON.stringify(b) + " got " + JSON.stringify(a)); };
const ok = (v, m) => { if (!v) throw new Error(m || "not ok"); };

localStorage.removeItem(store.KEY);

const sample = {
  id: "s1", created: "2026-10-19T00:00:00Z", account: "My boss cut me off twice and gave my project to Dana.",
  sorted: { happened: ["Interrupted twice", "Project moved to Dana"], told: [], concluded: ["He doesn't respect me"] },
  want: "I'd know where I stand.",
  read: { explanations: [{ text: "A", kind: "person", supports: [], distinguishing: "x" }, { text: "B", kind: "system", supports: [], distinguishing: "y" }],
    self_question: "q", influence: "i", step: { name: "Ask", what: "w", why: "y", assumes: "a", backfires: "b", alternative: "c" }, words: ["one", "two"], post: "p", manager_questions: false, tension: "" },
  words: ["one edited", "two"],
  post: { sentence: "Within two weeks I will have heard his reason.", date: "2026-11-02" },
};

test("copy has no em dashes", () => { ok(!JSON.stringify(COPY).includes(String.fromCharCode(8212))); });
test("copy has no leftover duplicate keys", () => { ok(!("conculdedHelp" in COPY.reflect)); });

test("store saves and loads a situation", () => {
  store.upsert(JSON.parse(JSON.stringify(sample)));
  const got = store.get("s1");
  ok(got && got.account === sample.account);
  eq(store.load().situations.length, 1);
});
test("store upsert replaces, not duplicates", () => {
  const s = store.get("s1"); s.want = "changed"; store.upsert(s);
  eq(store.load().situations.length, 1); eq(store.get("s1").want, "changed");
});
test("record is counts only", () => {
  const r = store.record([sample, { id: "s2", read: null }, { id: "s3", read: {}, lookback: { result: { matched: "yes" }, lesson: "Ask sooner." } }]);
  eq(r, { thought: 2, looked: 1, matched: 1, lessons: 1 });
});
test("due and open split on the date", () => {
  const list = [sample, { id: "s4", post: { sentence: "x", date: "2026-10-01" } }];
  eq(store.dueForLookback(list, "2026-10-19T12:00:00").map((s) => s.id), ["s4"]);
  eq(store.openOnes(list, "2026-10-19T12:00:00").map((s) => s.id), ["s1"]);
});
test("reviewed situations are neither due nor open", () => {
  const list = [{ id: "s5", post: { sentence: "x", date: "2026-10-01" }, lookback: { result: { matched: "no" } } }];
  eq(store.dueForLookback(list, "2026-10-19").length, 0); eq(store.openOnes(list, "2026-10-19").length, 0);
});
test("unfinished means started but no post and not conduct", () => {
  eq(store.unfinished([{ id: "a", account: "x" }, { id: "b", account: "x", conduct: true }, sample]).map((s) => s.id), ["a"]);
});
test("related lessons match on tags", () => {
  const list = [{ id: "z", lookback: { lesson: "Ask for the reason the same day.", result: { pattern_tags: ["decision without a reason"] } } }];
  eq(store.relatedLessons(list, ["Decision Without A Reason"]), ["Ask for the reason the same day."]);
  eq(store.relatedLessons(list, ["other"]), []);
});
test("clearAll empties the store", () => { store.clearAll(); eq(store.load().situations.length, 0); });

test("moveLine moves between groups and keeps order", () => {
  const next = moveLine(sample.sorted, "concluded", 0, "happened");
  eq(next.concluded, []); eq(next.happened[2], "He doesn't respect me");
  eq(sample.sorted.concluded.length, 1, "original untouched");
});
test("moveLine ignores bad indexes", () => { eq(moveLine(sample.sorted, "told", 3, "happened"), sample.sorted); });
test("cleanSorted trims and drops empties", () => {
  eq(cleanSorted({ happened: [" a ", ""], told: null, concluded: ["b"] }), { happened: ["a"], told: [], concluded: ["b"] });
});

test("addDays crosses a month", () => { eq(addDays("2026-10-19", 14), "2026-11-02"); });
test("toISODate pads", () => { eq(toISODate(new Date(2026, 0, 5)), "2026-01-05"); });

test("pageText carries the person's words, the edited openers and the post", () => {
  const t = pageText(sample);
  ok(t.includes(sample.account)); ok(t.includes("one edited")); ok(!t.includes("\n  one\n"));
  ok(t.includes(sample.post.sentence)); ok(t.includes(COPY.page.post)); ok(!t.includes(String.fromCharCode(8212)));
});
test("ics is a valid all-day event", () => {
  const i = icsFor(sample);
  ok(i.startsWith("BEGIN:VCALENDAR")); ok(i.includes("DTSTART;VALUE=DATE:20261102")); ok(i.includes("SUMMARY:Look back: Ask")); ok(i.includes("END:VCALENDAR"));
});
test("payload sends only what the step needs", () => {
  const p = payload(sample, { post: sample.post });
  eq(Object.keys(p).sort(), ["account", "answer", "post", "question", "sorted", "want"]);
  eq(p.question, null);
});

document.getElementById("title").textContent = (pass === total ? "PASS " : "FAIL ") + pass + "/" + total;
document.title = document.getElementById("title").textContent;
