# Teamwork knowledge architecture

This explains the system behind the advisor: what is in `server/library.json` (version 2), how the pieces connect, and what is still thin. The map at `docs/question-map.html` shows the same thing visually. Rebuild it with `python3 docs/build-map.py` after any change to the library.

## How the loops, lenses and forces organize the whole

Your website gives three frames, and Teamwork uses each for a different job.

- **The two loops** decide the shape of the product. A conversation can repeat the work (the Activity Loop) or change what happens next (the Learning Loop). So every pass ends in a written expectation and a dated look-back. That is the only thing that stops the second conversation being the first one again.
- **The three lenses** (Business, System, People) decide what the advisor must hold open. It always carries a cause that is not about anyone's character, because each lens has its own blind spot when used alone. The four overlaps are not used on screen yet.
- **The six forces** (Awareness, Trust, Conditions, Value, Incentives, Leverage) are the diagnostic questions. They feed the read, the self question and the step.
- **The Path to Agency** (Knowledge, Understanding, Judgment, Agency) is the order of the screens: sort the facts, hold two readings, choose one step, act and check.

## How the books enter, and where they conflict

The six books come in only as your Reading takeaways and as widely reported ideas. Nothing is quoted and nothing has a page number. Each is marked as your reading or a widely reported idea in the library.

They pull against each other in four places, and the library records each as a tension rather than resolving it quietly: Grove's output measure against how the 15 Commitments looks at how a leader shows up; Campbell's candour with care against Grove's metrics kept visible; Google's trust and transparency against Munger's warning that incentives override trust; and care for the person against Charan's number the business must hit. The read screen shows the tension line and the advisor names both costs.

## Decision-science rules and organizational-behaviour rules

Two kinds of reasoning run side by side, and the map keeps them in separate lanes.

**Decision science** governs how evidence and choices are weighed: base rates, value of information (ask only if an answer would change the advice), one observation versus a pattern, hindsight and outcome bias, the decision versus the result, and regression to the mean. It also holds the Decision OS algorithms (Bayesian updating, value of information, expected value, decision tree, utility, explore and exploit, prediction versus decision). Teamwork uses the shape of each rule and never its arithmetic. It asks for no probabilities and shows no scores. These rules govern the question screen, the "what would tell" line, the post, and above all the look-back.

**Organizational behaviour** governs what explains behaviour: the fundamental attribution error, psychological safety, power asymmetry, and the difference between a setup problem and a person problem, plus your forces, lenses, books, habit families and management cases. These rules govern the read screen, the choice of step by seat (upward steps are questions and records, downward steps are expectations), and the conduct path.

A third group holds guardrails: the protocol rules, Stillward's practice, and the Path stages. The library holds 119 entries in all; 79 are used by at least one screen or relationship. There are 71 relationships between them (40 supports, 13 narrower forms, 18 tensions). The tensions matter most. The safety flag, for example, switches off the base rate, the attribution check, the non-character explanation and the wait for a pattern, on purpose.

## The trust design

Each screen states three things in plain words: what the advisor can know here, what it cannot know, and what you stay in control of.

- **Known:** only what you typed or tapped, and what you confirmed on the sort screen.
- **Inferred:** the two readings, the one question, the step and the sentence. These are labelled as readings and predictions, never as findings, and the advisor never ranks a reading with a number.
- **Controllable:** every line can be moved, edited or removed; every question can be skipped; every step can be changed or ignored; everything can be deleted. Nothing leaves the browser except the text for the current step, and the server stores nothing.

Every link from an answer to an idea carries one sentence saying why that idea governs that answer. You can read them all in the map, and check any of them against the idea's "misleads when" line.

## What remains thin

- **Lencioni has no material.** The Five Dysfunctions is in the library as a widely reported idea only, flagged thin. It is not in your Reading section.
- **Book ideas are readings, not texts.** Nothing was checked against the books. Psychological safety, hindsight bias, regression to the mean and the attribution error are widely reported ideas I have not sourced to papers here.
- **No workplace base rates.** The advisor is told never to quote a percentage, because there is no data behind one.
- **Power asymmetry, setup versus person and one observation versus a pattern are my synthesis.** The "twice" threshold is a protocol choice, not a finding. Your material is mostly written from the manager's seat, so the view from below is the weakest part.
- **Friction's weights and priors are your design choices,** not fitted to data, and Teamwork borrows only the vocabulary and the weighting idea.
- **The advisor reads the extra entries only through `protocol.md`.** `library_digest()` still sends forces and cases only. The new entries reach the model as plain text in the vocabulary section, not as structured data.
- **Nothing has been validated with users.** No one has yet shown that the reasoning links help, or that the trust panels are believed.
