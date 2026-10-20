# Teamwork

Think through a difficult situation with someone at work. Teamwork separates what happened from what you
concluded, holds more than one explanation open, gives you one next step with its risks, and asks you to
write down what you would see if it worked, with a date. When you come back it asks what you expected
before it shows you what you wrote.

Prototype. Not yet tested with real users. Not deployed. The product brief is in `docs/teamwork-brief.md`.

## What is here

- `index.html`, `css/`, `js/`: a static page, vanilla ES modules, no build step.
- `server/app.py`: a standard-library Python server. Serves the page and answers `POST /api/step` by
  calling the Claude API with the protocol in `server/protocol.md`. Keeps nothing, logs no content.
- `server/library.json`: the principle library drawn from the website's six force cards and the thirty
  management cases in Decision OS Module 3.
- `server/fixtures/`: canned answers for mock mode.
- `tests/run.html`: browser tests for the pure modules. `server/test_app.py`: server tests.

## Run it

Without a key, with canned answers:

    TEAMWORK_MOCK=1 python3 server/app.py

With the model:

    ANTHROPIC_API_KEY=sk-ant-... python3 server/app.py

Then open http://localhost:8975. `PORT` changes the port. `TEAMWORK_MODEL` changes the model (default
`claude-opus-5-5`).

Tests:

    python3 -m unittest discover -s server -p 'test_*.py'
    open http://localhost:8975/tests/run.html

## Deploy on Railway

1. Create an empty repository on GitHub in the web interface, then from this folder:

       git remote add origin git@github.com:matthewschmidt1-lgtm/teamwork.git
       git push -u origin main

2. In Railway: New Project, Deploy from GitHub repo, pick the repository. `railway.json` tells it to run
   `python3 server/app.py`; `runtime.txt` asks for Python 3.12; `requirements.txt` is empty on purpose.
3. In the service's Variables, add `ANTHROPIC_API_KEY`. Without it the page loads and the advisor says
   it is not connected.
4. Settings, Networking, Generate Domain. Check `/api/health` shows `"mode": "live"`, then open the page
   and run one situation end to end.

## Where words go

Everything a person writes stays in their browser under `localStorage` key `teamwork.v1`. When they ask for
a read, the account, the sorted lines and their answers are sent to this server, which forwards them to the
Claude API and returns the structured answer. The server does not store or log the content. Anthropic's
data handling applies to the API call.
