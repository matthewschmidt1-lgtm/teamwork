# Teamwork without an API key: options

## The plain reason

Teamwork was built around the Anthropic API because the advisor's job (sort an account, ask one good question, write two explanations and one step that fit this person's story) is free-text understanding, and a model does that. The builder, not you, made the assumption that a key would exist. That was a mistake to make silently. A Claude subscription (Claude Code, claude.ai) does not include API access. The API is a separate, pay-as-you-go account at console.anthropic.com, and you have never made one. So the live Railway deploy has no ANTHROPIC_API_KEY, and every read fails with "The advisor is not connected." Also true: no answer from this advisor has ever come from a real model. Only the fixtures and the unit tests have run.

## What I found

**The knowledge is indexed by taps, not by text.** The three tapped answers (who, what, need) carry links with a reasoning sentence each. There are 13 seat ideas (ask first, written facts, escalation ladder, bring a proposal, and so on), already written as advice. The 30 cases each have a pause question, a principle, a next move and a strong move. But all 30 are written for a manager's seat, and only two are linked from any tap (one from "team lead", one from "missed"). The rest would need tagging by theme.

**Step by step:**

- **Reflect.** The typed line needs understanding. Without a model, split it into sentences and let the person sort them with the existing move, edit, remove and add buttons. That loses speed, not value. The safety flag is the weak spot: the "conduct" tap is reliable, but a harassment account typed in the free line will not be caught, so a conduct link must be visible on every screen.
- **Question.** One authored question per "what" answer, always skippable. It will ask more often than a model would, which strains protocol rule 5.
- **Read.** The hardest. It collapses to about 6 explanation pairs, 30 step cards and 5 framings. It cannot use the person's facts, only quote their sorted lines back.
- **Lookback.** Close to free. The person taps whether it worked; the comparison is their own then-and-now side by side plus fixed honest-inference copy.

**Friction as a yardstick.** Friction's engine is credible because it asks 15 to 20 questions and each answer carries authored likelihoods. Teamwork asks three taps, so that engine does not transfer. A deterministic read is credible only as a "starting read from a guide", never as a reading of this person's case.

## The three real options

| | A. Deterministic mode | B. Browser key | C. Server key, cheaper per-step models |
|---|---|---|---|
| Cost to run | $0 | You pay per use (testers need their own keys) | About $0.10 to $0.17 per situation |
| Your effort | 12 to 20 hours of authoring and testing | 3 to 5 hours | 1 to 2 hours, plus 15 minutes at the Console |
| Needs a Console account | No | Yes (for each key holder) | Yes |
| What users lose | Tailoring to their facts; free-text safety detection; a lot of the "advisor" feel | Nothing, but a poor fit for strangers | Nothing |
| Privacy | Best: nothing leaves the device | Text goes from the browser to Anthropic; key sits in localStorage | Text passes through Railway to Anthropic; server logs no content |
| Testable with real people | Yes, anyone | You and a few trusted testers only | Yes, anyone, with a spend cap |

## Option details

**B. Browser key.** The TypeScript SDK docs I fetched say browser use is "disabled by default to avoid exposing your secret API credentials" and is enabled with `dangerouslyAllowBrowser`. The docs call it acceptable for "internal tools" among trusted users or short-lived, rotated keys. I did not find the raw header in the pages I could reach. From memory the SDK sends `anthropic-dangerous-direct-browser-access: true`, which I could not confirm in the docs. Work: move build_request, the schemas and the library slicing from app.py into JavaScript (about 300 lines; the slicer is the bulk), add a settings field in js/api.js that stores the key in localStorage, and ship library.json and protocol.md to the client. Risks: the key sits in plain browser storage where extensions or page scripts can read it, and the protocol and library become public downloads. It suits you and a handful of trusted testers, and it still needs a Console account.

**C. Server key.** Costs, estimated honestly. I measured the prompts: protocol.md is about 15.5k characters, the digest 1.6k, the per-step slice is capped at 6k characters, plus the person's JSON. That is roughly 6 to 7k input tokens per call, not 10 to 15k. Output is about 400 tokens for reflect, 200 for question, 2k to 3k for read (effort is "high"), 400 for lookback. On Opus at $4 and $20 per million, one full situation is about $0.10 for input and $0.07 for output, so $0.15 to $0.17 uncached. Caching only marks the second system block, so about 4k tokens get discounted, and may fall under a minimum cacheable size; I could not verify that. Realistic range: $0.10 to $0.20. A hundred test situations is $10 to $20.

Cheaper models: moving reflect, question and lookback to Sonnet 5.5 saves about $0.04 per situation, 25 to 35 percent at best, because read dominates. I would keep reflect on Opus since it carries the safety flag. In app.py, MODEL is one global from TEAMWORK_MODEL used in build_request; a STEP_MODEL dict with env overrides is about 15 lines. I could not verify that the `output_config` effort setting and fallback beta header work on Sonnet and Haiku.

Console steps: create an account at console.anthropic.com, add billing and prepay credit (I believe the minimum is around $5, not verified), set a monthly spend limit, create a key, and paste it into Railway as ANTHROPIC_API_KEY. Then redeploy.

## Other routes, briefly

- **Free tier or another provider.** Needs its own account and key, plus a rewrite of the structured-output call and a re-check of the protocol. Not worth it.
- **Local model.** Python 3.9, no Node, and a model that follows a 15k-character protocol needs hardware the stack avoids. Cannot run on Railway.
- **Your subscription as a backend.** Claude Code is for you personally, not a public site's engine. I would not build on it.

## Recommendation

Do both A and C, in that order of urgency, but start with a small piece of A.

1. Today: build deterministic mode as the default when no key is present (the server returns a mode flag on /api/health, the app switches). It puts Teamwork in front of real people at no cost and tests whether the sort, question and step are useful. The read will be weaker than a live advisor, which is fine for a pilot.
2. When you want the real thing, do C. It is cheap (about $15 for a hundred runs), the least code, and the only option that tests the actual product. Cap spend at $20 a month at first.
3. Skip B. It costs more engineering than C, exposes the protocol, and still needs a Console account.

If you will never open a Console account, A is the permanent product, and the copy should say so.

## Sketch of deterministic mode

**Screens.** Reflect becomes "sort your own words": the typed line is split into one pile and the person moves each line. The echo is a fixed sentence. Question shows the authored question, with skip. Read, step and post keep their layout. Lookback assembles its comparison from the two stored answers.

**The read.** Two explanations for the "what" tapped: one about the system (ds.fae, system-person, the lenses), one about behaviour, framed as "the facts fit this story", with supports quoting the person's happened lines. A self question from rule.own_part. One step by seat from the seat ideas, with assumption, risk and alternative; for managers, the matching case's pause and strong move. Two or three openers. A templated post sentence, editable. Add tests that every seat, what and need combination returns a complete read.

**Honesty copy.** Above the first explanation: "This is a starting read from a guide, written for situations like yours. It has not read your account, so it may miss what is specific to you. Change anything that does not fit." On the sort screen: "We cannot tell happened from told from concluded in your words. You can." Always visible: "If this involves harassment or punishment for saying no, this guide is not enough. Here is where to go instead." Exports carry the same "from a guide" label.

## What I could not verify

- The exact `anthropic-dangerous-direct-browser-access` header text and whether CORS permits it today; the docs I reached only confirm the SDK's opt-in and the warning.
- Prompt caching minimums and whether the cache applies to this layout.
- Whether `output_config`, effort levels and the fallback beta header work on Sonnet 5.5 and Haiku 5.5.
- The Console minimum prepayment and current rate limits for a new account.
- Actual output token counts, since no real model has ever answered. All costs are estimates until you run twenty real situations and read the usage figures.
- How good the deterministic read feels to a person in distress. That needs a pilot.
