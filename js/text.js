// Pure text helpers: the copyable page, the calendar file, dates. No DOM.
import { COPY } from "./content.js";

export function addDays(iso, n) {
  const d = new Date(iso + "T00:00:00");
  d.setDate(d.getDate() + n);
  return toISODate(d);
}

export function toISODate(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return y + "-" + m + "-" + day;
}

export function fmtDate(iso) {
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" });
}

export function todayISO() {
  return toISODate(new Date());
}

function lines(title, arr) {
  if (!arr || !arr.length) return "";
  return title + "\n" + arr.map((l) => "  " + l).join("\n") + "\n\n";
}

export function pageText(s) {
  const P = COPY.page;
  let out = P.heading + "\n\n";
  out += P.account + "\n  " + (s.account || "").trim().replace(/\n+/g, "\n  ") + "\n\n";
  if (s.want) out += P.want + "\n  " + s.want + "\n\n";
  if (s.sorted) {
    out += lines(P.happened, s.sorted.happened);
    out += lines(P.told, s.sorted.told);
    out += lines(P.concluded, s.sorted.concluded);
  }
  if (s.read) {
    out += P.explanations + "\n";
    s.read.explanations.forEach((e, i) => {
      out += "  " + (i + 1) + ". " + e.text + "\n     " + COPY.read.distinguishing + ": " + e.distinguishing + "\n";
    });
    out += "\n";
    if (s.read.self_question) out += COPY.read.selfTitle + "\n  " + s.read.self_question + "\n\n";
    out += P.step + ": " + s.read.step.name + "\n  " + s.read.step.what + "\n  " + COPY.step.assumes + ": " + s.read.step.assumes + "\n  " + COPY.step.backfires + ": " + s.read.step.backfires + "\n  " + COPY.step.alternative + ": " + s.read.step.alternative + "\n\n";
    out += lines(P.words, s.words && s.words.length ? s.words : s.read.words);
  }
  if (s.post) {
    out += P.post + "\n  " + s.post.sentence + "\n  " + P.by + " " + fmtDate(s.post.date) + "\n";
  }
  return out.trim() + "\n";
}

function icsEscape(t) {
  return String(t).replace(/\\/g, "\\\\").replace(/\n/g, "\\n").replace(/,/g, "\\,").replace(/;/g, "\\;");
}

export function icsFor(s) {
  const date = (s.post.date || "").replace(/-/g, "");
  const stamp = new Date().toISOString().replace(/[-:]/g, "").replace(/\.\d{3}/, "");
  const desc = COPY.page.post + ": " + s.post.sentence;
  return [
    "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Teamwork//EN", "BEGIN:VEVENT",
    "UID:" + s.id + "@teamwork",
    "DTSTAMP:" + stamp,
    "DTSTART;VALUE=DATE:" + date,
    "SUMMARY:" + icsEscape("Look back: " + (s.read ? s.read.step.name : "Teamwork")),
    "DESCRIPTION:" + icsEscape(desc),
    "END:VEVENT", "END:VCALENDAR", "",
  ].join("\r\n");
}

// The opening account, built from three taps and an optional line.
export function composeAccount(labels, detail) {
  const lc = (t) => t.charAt(0).toLowerCase() + t.slice(1);
  const parts = [];
  if (labels.who) parts.push("This is about " + lc(labels.who) + ".");
  if (labels.what) parts.push(labels.what + ".");
  if (labels.need) parts.push("Right now I need " + lc(labels.need) + ".");
  if (detail && detail.trim()) parts.push(detail.trim());
  return parts.join(" ");
}

// Moving a line between the three groups on the reflect screen. Returns a new sorted object.
export function moveLine(sorted, from, index, to) {
  const next = { happened: [...sorted.happened], told: [...sorted.told], concluded: [...sorted.concluded] };
  if (!next[from] || !next[to] || index < 0 || index >= next[from].length) return next;
  const [line] = next[from].splice(index, 1);
  if (from !== to) next[to].push(line);
  else next[from].splice(index, 0, line);
  return next;
}

export function cleanSorted(sorted) {
  const clean = (arr) => (arr || []).map((l) => String(l).trim()).filter(Boolean);
  return { happened: clean(sorted.happened), told: clean(sorted.told), concluded: clean(sorted.concluded) };
}
