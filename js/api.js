// The one call to the server. The server holds the key and keeps nothing.

export class AdvisorError extends Error {
  constructor(message, status, declined) {
    super(message);
    this.status = status;
    this.declined = !!declined;
  }
}

export async function step(name, situation) {
  let res;
  try {
    res = await fetch("/api/step", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ step: name, situation }),
    });
  } catch (e) {
    throw new AdvisorError("", 0, false);
  }
  let data = {};
  try { data = await res.json(); } catch (e) { /* fall through */ }
  if (!res.ok) throw new AdvisorError(data.error || "", res.status, data.declined);
  return data.result;
}

// What the model is given at each step: only what it needs, in a stable shape.
export function payload(s, extra) {
  const base = {
    account: s.account,
    choices: s.choices ? s.choices.labels : null,
    detail: s.detail || null,
    sorted: s.sorted || null,
    want: s.want || null,
    question: s.question || null,
    answer: s.answer || null,
  };
  return Object.assign(base, extra || {});
}
