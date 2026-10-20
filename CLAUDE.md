# Teamwork

An evidence-first advisor for difficult situations with people at work. One static page plus one small
Python server that holds the model key. The brief that governs the product is `docs/teamwork-brief.md`;
the advisor's protocol is `server/protocol.md`. Read both before changing behaviour.

## Shape

- The site: `site/index.html`, `css/site.css`, `js/site.js`, served at `/`. Concept in `docs/site-concept.md`.
- The app: `index.html`, `css/teamwork.css`, `js/*.js` as ES modules, served at `/app/` (asset paths are absolute). No build step, no framework, no npm.
- `js/content.js` holds every line of copy. `js/store.js` is `localStorage` under the key `teamwork.v1`.
- `server/app.py` is a standard-library HTTP server: serves the static files and answers `POST /api/step`
  by calling the Claude API over raw HTTPS (this Mac has Python 3.9 and the SDK needs 3.10, and the family
  convention is zero dependencies). It stores nothing and logs no content. `server/library.json` is the
  principle library drawn from the website's six force cards and Decision OS Module 3.
- `TEAMWORK_MOCK=1` makes the server answer from `server/fixtures/` without a key, for UI work and tests.

## Run

    ANTHROPIC_API_KEY=... python3 server/app.py          # http://localhost:8975
    TEAMWORK_MOCK=1 python3 server/app.py                # no key, canned answers
    python3 -m unittest discover -s server -p 'test_*.py'
    open http://localhost:8975/tests/run.html             # browser tests for js/

Headless checks use Chrome: `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --dump-dom URL`.
Always use absolute paths in shell commands here; the app resets the shell's working directory between calls.

## Rules

- Never diagnose the absent person. Never say "valid". Counts, never scores. No streaks, no reminders from us.
- Happened outweighs told outweighs concluded, on every screen.
- One thing per screen. Every screen has a way back and a way to stop that keeps what exists.
- The conduct path (safety flag) gets no explanations exercise and no openers.
- No em dashes anywhere in copy or code comments (a test checks). Plain human voice.
- Scope: draws on Friction, Decision OS, Stillward, Algorithm Atlas and the website only.
- Do not deploy or push without Matthew's go-ahead.
