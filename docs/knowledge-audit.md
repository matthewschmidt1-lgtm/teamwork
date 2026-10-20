# Teamwork knowledge audit

Audit date 2026-10-20. Inspected: local files at commit 2621cb6, and the live site. The live question-map.html and source-map.html are byte-identical to the local files (144,959 and 204,997 bytes), so every map finding holds for both. The live /api/health returned `mode: no-key`, so the deployed advisor currently answers 503 and runs no model at all. Facts below about the model's input come from the local server/app.py and server/protocol.md. I did not run the model.

## Verdict: incomplete

The data is carefully written, honest about the books, and mostly logically sound where it is explicit. But the graph is documentation about the reasoning, not the reasoning itself: only about 6 percent of library.json reaches the advisor, and none of the links, relations or guard conditions do. The links that do exist contain a real minority of invalid or inverted ones, and the view from below, the user's weakest seat, is thinly covered.

## Findings, ranked

**1. The graph never reaches the model (confirmed defect).** `library_digest()` in server/app.py (lines 97 to 111) sends two things: the 6 forces (name, pattern, move, ask) and the 30 cases (principle, pause, next move, and the two lesson sentences). That is 11,505 characters of a 198,191 character file. Never sent: all 71 relations and their why-sentences, all 18 step blocks and 104 answer links, the 17 `applies_when` and `misleads_when` fields, every status, the 7 algorithms, 10 decision-science entries, 15 rules (as entries), loops, lenses, path, books_takeaways, books_unsourced, Friction, Stillward, habits, skills, dos_practice. Also dropped from each case: the book names, `strong_move`, `weak_habits`, `theme`, `trade`. A hand-condensed paraphrase lives in protocol.md instead, with no ids. So the maps ("How it reasons") describe a system the advisor does not run. The model is never told which ideas govern which answer. Fix: build the prompt section per request from library.json, selecting by the user's three tapped choices (who, what, need) the linked ideas, their why-sentences, status and `misleads_when`. Test: for each of the 104 answers, assert the assembled prompt contains every linked id's text, and that a prompt for "My manager" contains ds.power and its misleads line.

**2. Guard conditions are lost, so ideas arrive as laws (confirmed defect).** Every decision-science idea has a `misleads_when` that says when to stop applying it (regression to the mean: "Something real changed (a new manager, a reorganization, a promise broken)"). The protocol keeps the idea and only a generic "none of them is a law". Example in protocol.md: "an unusually bad day tends to be followed by a better one without help, so do not credit a step for a recovery that may have come anyway", with no counter-condition. Fix and test as in finding 1: include `misleads_when` beside each idea; a test checks that each used ds.* entry's guard string appears in the prompt.

**3. The data cannot tell facts from readings from synthesis, and the protocol flattens what it has (confirmed defect).** There is no tier for fact or evidence at all. Statuses: 95 owner_reading, 18 synthesis, 6 widely_reported. "Owner reading" mixes the owner's own frameworks, his readings of books, and Decision OS cases written as his readings of books. The protocol drops status completely: power asymmetry, setup versus person and the "twice" threshold are Teamwork's own synthesis (library.json says so) yet sit in one paragraph with fundamental attribution error, which is a widely reported finding, under "Ideas about people and power". The widely reported items (ds.fae, ds.psych_safety, ds.hindsight_outcome, ds.regression_mean) name research traditions with no citation and no "not checked" marker on the screen the user sees. The data is honest that books are readings (books_unsourced, `thin: true` on book.fdt, `owner_phrase_to_check`); that part is good. Fix: add a `kind_of_claim` field (fact, reading, reported, synthesis) and carry it into the prompt as a short tag the advisor must respect. Test: protocol-building fails if a synthesis item is emitted without its tag.

**4. Relations: 11 fail or are inverted, several more are doubtful (confirmed defects).** I checked all 71. About 55 hold (for example `ds.base_rates supports alg.bayes`, `ds.hindsight_outcome supports rule.honest_inference`, `ds.power tension book.tdc`). These fail:
- `alg.utility specializes dos.tension`: inverted. Tension between two values is a special case of a utility trade-off, not the reverse.
- `alg.bandit tension alg.ev`: a false conflict. Explore and exploit is expected value with the value of learning included. The why-sentence says an experiment "looks poor on expected value", which is true only if the learning is left out.
- `force.leverage supports book.hom`: inverted and circular. The owner's force is offered as support for the owner's reading of a book.
- `rule.one_question supports ds.voi`: opposite direction to the convention used elsewhere (`ds.fae supports rule.non_character` runs idea to rule).
- `force.incentives supports ds.system_person` says incentives are "the most common setup cause". Nothing supports "most common", and the protocol forbids base rates.
- `lens.multiplier supports path.understanding`: the multiplier is lenses reinforcing each other; Understanding in the protocol is two or three rival readings held apart. Different operations.
- `alg.forecast supports ds.decision_vs_result`: forecast versus decision and decision versus result are separate distinctions.
- `habit.narrow specializes book.pca` and `habit.control specializes dos.before`: a behaviour does not specialize a book or a list of questions.
- `loop.activity tension loop.learning`: a contrast, not a tension.
- `ds.power supports ds.psych_safety` (relations) while `decision_science[ds.psych_safety].conflicts_with` lists `ds.power`. The file contradicts itself.
- Four tensions with `rule.safety_flag` (base_rates, fae, non_character, one_vs_pattern) are overrides by precedence, not tensions. The schema has no `overrides` kind, so the real hard rule is drawn the same as a soft trade-off.
Doubtful: `book.hgw supports ds.psych_safety` rests on the owner's reading naming psychological safety; that concept was popularized from Google research outside the book, which the library's own `owner_phrase_to_check` half admits. `path.agency specializes loop.learning` is a stretch.

**5. Answer links that do not govern the answer (confirmed defects).**
- `want.know_where` links `ds.power` with "Not knowing where you stand is often a gap in who holds the information". That is not power asymmetry.
- `read.distinguishing` links `ds.base_rates`: "'Has he done this to others?' is a base-rate question". It is a question about one person's history. The protocol says never to use base rates.
- `what.shifted` links `ds.hindsight_outcome`: "both sides remember agreeing to more than they did". Hindsight bias is about knowing the outcome; this is an extension, and it casts doubt on the user's memory in a case that may be retaliation.
- `step.assumes` links `alg.bayes`: "move it by the right amount", while the protocol bans numbers.
- `need.escalate` links `alg.tree`, which needs odds; `post.d30` links `ds.one_vs_pattern` on the unsupported idea that a longer window means more independent events.
- `what.missed` links `case.metrics-reward-the-wrong-thing` ("Fix yours first") for every seat. For a peer or an upward seat there is no number of theirs to fix.
- `who.colleague` links `ds.power`: "direct candour is more often safe". An empirical claim with no source; peers compete and hold informal power.

**6. The view from below is thin, and the cases speak only to managers (confirmed).** Only ds.power and ds.psych_safety carry the "I report to them" seat, plus one protocol sentence. The one principle about carrying truth upward, `skill.across`, has no relation and no answer link. All 30 cases are in a manager's voice (the metrics case's strong move is "Ask your director to pay you on retail"), and the digest sends all 30 with no rule for choosing one. The protocol never mentions the cases. "My team" is ambiguous between leading the team and belonging to it, yet `case.team-agrees` assumes the user is the leader ("What does disagreeing with you cost a rep?"). Potential risk: a report asking about a manager gets advice shaped by manager-side cases.

**7. Isolated and unrendered nodes (confirmed).** 40 of 119 principles have neither an answer link nor a relation: 25 of 30 cases, 5 of 8 habits, all 7 skills, force.value and 3 of 4 composite lenses. 54 have no relation at all. Stillward's four ideas have zero relations and one to four answer links each, and the app does not render the quotes: no match for "Ram Dass", "Almaas" or "quieter you" in local or live js/ or index.html. The maps therefore show Stillward lines on screens that do not display them. Their `avoid` conditions ("never on the conduct path") are strings, not edges to rule.safety_flag. The doc's "79 used" is accurate only in the sense of linked on a map.

**8. Implementation (confirmed unless marked).**
- docs/build-map.py and build-source-map.py check only that ids exist. No check on relation kind, direction, duplicates, the `used` flag (stored, not computed), or agreement between `conflicts_with` and relations. Four conflict pairs have no relation at all (base_rates and power, voi and safety_flag, hindsight and one_vs_pattern, system_person and safety_flag).
- Reading edges for cases are derived by a 12 character prefix match on the source string, which is brittle.
- Tension is symmetric but stored as directed `from` and `to`.
- `post.d7` is the only answer with no link.
- Potential risk: protocol rule 4 ("own part always a live question") versus "own-part patterns only when the account points at one twice" can conflict when the user taps "I think I might be the problem".
- Potential risk: rule 11 names bullying only when it targets a protected characteristic; other targeted bullying gets the two-explanations treatment, including the setup explanation.
- The default model name `claude-opus-5-5` and the beta header could not be verified from here.

## Reasoning traces

**Valid: manager seat, missed deadlines.** `who.report` links ds.system_person ("a report's miss is first read as a possible setup problem the manager helped build") and dos.before. `lens.system supports ds.system_person`, `force.conditions supports ds.system_person`, `ds.system_person supports rule.non_character`. The protocol (rule 3, and "At least one explanation must be kind system") makes the advisor always carry a setup reading, and the schema enforces `kind`. Caveat: lens.system and its book support are both the owner's reading, so the chain is coherent but not independent.

**Valid: the safety path.** `what.conduct` links rule.safety_flag and ds.one_vs_pattern ("waiting for a pattern would be the mistake here"). The tap routes to `startConduct()` in js/app.js without calling the model, and protocol rule 11 covers free text. This is the best-built chain: the override is explicit in both the graph and the code.

**Valid: candour from below.** `ds.power tension book.tdc` ("Candour with care assumes it is safe to be candid, which is least true from below"). The protocol lists "candour early against the safety of the person speaking" and tells the advisor to make the step a question or written record when below. Source (owner's reading plus synthesis), idea, prompt, behaviour all line up. The "make it a question" rule itself is synthesis with no source.

**Invalid: goalposts.** `what.shifted` to hindsight to a step. The link says both sides misremember; the protocol only gives a generic hindsight sentence; the model has no instruction about disputed agreements. The inference from outcome bias to "you probably misremember what was agreed" is unsupported, and it reaches the user only if the model happens to infer it.

**Unresolved conflicts:** Grove against the 15 Commitments, Campbell against Grove, Google against Munger, care against Charan. The library records each and the protocol names them for `tension`, which is honest. No rule says which to favour in a given seat.

## Practical usefulness by context

Manager: best supported, assuming the model follows the protocol. Reports to the other person: weakest; thin links, manager-voiced cases, one protocol sentence. Peer: the "candour is safer" claim is unsourced. Team: seat ambiguous. Conduct: strongest, but depends on tap or on model detection of rule 11, and non-protected bullying is a gap. It would mislead most where a setup explanation excuses a person who is genuinely at fault, which the guard (`misleads_when`) warns about but the model never sees.

## Priority plan

1. Compile the per-answer slice (ideas, why, status, misleads_when, tensions) into the prompt; add the coverage test. (Findings 1, 2)
2. Add the four-way claim tag and carry it into the prompt. (Finding 3)
3. Fix or remove the 11 failed relations; add an `overrides` kind; make `conflicts_with` derived from relations. (Findings 4, 8)
4. Rewrite or drop the seven answer links in finding 5. Test: a reviewer-signed table of link, answer and "would this change what the advisor says?".
5. Add upward and peer material and a seat tag on every case; clarify "My team". (Finding 6)
6. Connect or drop isolated nodes; render Stillward or remove its links; add validation to both builders. (Findings 7, 8)
7. Run real trials: for 10 seeded accounts across the five seats, compare outputs with and without the slice. Nothing has been validated with users, as the owner's own doc says.

## The final question

This is a graph of related ideas, not yet a trustworthy reasoning system. A reasoning system makes its conclusions follow from its inputs through a path you can check; here the checked, well-written graph sits beside the advisor rather than inside it, and a minority of its edges would not survive review. The honesty about sources and the explicit tensions are real strengths and are what make it worth fixing.

The single most important improvement: feed the model the relevant slice of the graph per request, with each idea's status and its `misleads_when`, and test that this slice is in the prompt.
