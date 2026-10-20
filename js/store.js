// Local storage for Teamwork. One key, versioned. Falls back to memory when storage is blocked.

export const KEY = "teamwork.v1";

let memory = null;

function backend() {
  try {
    const t = "__teamwork_probe__";
    localStorage.setItem(t, "1");
    localStorage.removeItem(t);
    return localStorage;
  } catch (e) {
    return null;
  }
}

export function load() {
  const b = backend();
  const raw = b ? b.getItem(KEY) : memory;
  if (!raw) return { version: 1, situations: [] };
  try {
    const data = JSON.parse(raw);
    if (!data || !Array.isArray(data.situations)) return { version: 1, situations: [] };
    return data;
  } catch (e) {
    return { version: 1, situations: [] };
  }
}

export function save(data) {
  const raw = JSON.stringify(data);
  const b = backend();
  if (b) b.setItem(KEY, raw); else memory = raw;
}

export function newId() {
  return "s" + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
}

export function upsert(situation) {
  const data = load();
  const i = data.situations.findIndex((s) => s.id === situation.id);
  situation.updated = new Date().toISOString();
  if (i >= 0) data.situations[i] = situation; else data.situations.unshift(situation);
  save(data);
  return situation;
}

export function remove(id) {
  const data = load();
  data.situations = data.situations.filter((s) => s.id !== id);
  save(data);
}

export function clearAll() {
  save({ version: 1, situations: [] });
}

export function get(id) {
  return load().situations.find((s) => s.id === id) || null;
}

// Counts only. Never a score.
export function record(situations) {
  const list = situations || load().situations;
  const thought = list.filter((s) => s.read).length;
  const looked = list.filter((s) => s.lookback && s.lookback.result).length;
  const matched = list.filter((s) => s.lookback && s.lookback.result && s.lookback.result.matched === "yes").length;
  const lessons = list.filter((s) => s.lookback && s.lookback.lesson && s.lookback.lesson.trim()).length;
  return { thought, looked, matched, lessons };
}

export function dueForLookback(situations, today) {
  const now = today ? new Date(today) : new Date();
  return (situations || load().situations).filter((s) => s.post && s.post.date && !(s.lookback && s.lookback.result) && new Date(s.post.date + "T00:00:00") <= now);
}

export function openOnes(situations, today) {
  const now = today ? new Date(today) : new Date();
  return (situations || load().situations).filter((s) => s.post && s.post.date && !(s.lookback && s.lookback.result) && new Date(s.post.date + "T00:00:00") > now);
}

export function unfinished(situations) {
  return (situations || load().situations).filter((s) => !s.post && !s.conduct && s.account);
}

// Earlier lessons whose tags overlap with this situation's, for the look-back screen.
export function relatedLessons(situations, tags) {
  const want = new Set((tags || []).map((t) => t.toLowerCase()));
  return (situations || []).filter((s) => s.lookback && s.lookback.lesson && (s.lookback.result ? s.lookback.result.pattern_tags || [] : []).some((t) => want.has(t.toLowerCase()))).map((s) => s.lookback.lesson);
}
