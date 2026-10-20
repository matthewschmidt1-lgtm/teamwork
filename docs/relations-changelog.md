# Relations changelog

Changes made after the knowledge audit of 2026-10-20 (docs/knowledge-audit.md, findings 4, 5 and 6). Each entry says what was wrong, what was done, and why. The checks that now guard these rules live in `server/test_app.py` (class `RelationRules`).

## The rules a relation must now meet

- Direction. `supports` runs from the supporting idea to the supported one. `specializes` runs from the narrower idea to the broader one. `tension` is symmetric. `override` runs from the rule that wins to the idea it overrides.
- Every endpoint exists. `specializes` never runs from a book, loop or lens down to a case, habit or rule. No relation contradicts a `conflicts_with` entry. No pair appears twice, in either direction. Every `why` has at least eight words.

## The new kind: override

The schema had no way to say that one rule wins. The four tensions with `rule.safety_flag` were drawn like soft trade-offs. They are now `override`, from `rule.safety_flag` to the idea it overrides, and the advisor's knowledge slice renders them as "This overrides the others when it applies".

- `rule.safety_flag` overrides `ds.base_rates`, `ds.fae`, `rule.non_character`, `ds.one_vs_pattern` (the four the audit named).
- `rule.safety_flag` overrides `rule.one_step`. Not on the audit's list. It was the same shape (on the conduct path there is no single conversation step), so it moved too.

## The eleven failures

| Relation | Decision | Why |
| --- | --- | --- |
| `alg.utility specializes dos.tension` | Inverted: now `dos.tension specializes alg.utility` | Two values pulling apart is a special case of a utility trade-off, not the reverse. |
| `alg.bandit tension alg.ev` | Changed to `alg.bandit specializes alg.ev` | Explore and exploit is expected value with the value of learning counted in. The conflict only appears if the learning is left out. |
| `force.leverage supports book.hom` | Removed | The owner's force offered as support for the owner's reading of a book is circular, and reversing it is just as circular. |
| `rule.one_question supports ds.voi` | Reversed: `ds.voi supports rule.one_question` | Matches the convention used elsewhere: the idea supports the rule that applies it. |
| `force.incentives supports ds.system_person` | Kept, why rewritten | "The most common setup cause" had no support, and the protocol forbids base rates. It now says incentives are one of the setup causes to check. |
| `lens.multiplier supports path.understanding` | Removed | The multiplier is lenses reinforcing each other. Understanding is two or three rival readings held apart. Different operations. |
| `alg.forecast supports ds.decision_vs_result` | Removed | Forecast versus decision and decision versus result are separate distinctions. `alg.forecast` keeps its answer link on the step screen. |
| `habit.narrow specializes book.pca` | Removed | A behaviour does not specialize a book. |
| `habit.control specializes dos.before` | Removed | A behaviour does not specialize a list of questions. |
| `loop.activity tension loop.learning` | Removed | A contrast, not a tension. Nothing is traded off. The schema has no contrast kind, and one pair did not justify adding it. |
| `ds.power supports ds.psych_safety` | Changed to `tension`; `ds.power` now also lists `ds.psych_safety` under `conflicts_with` | The file contradicted itself. Psychological safety assumes people can speak without cost; unequal power is why that is often not true. That is a tension. |

One short why was also lengthened (`ds.system_person supports rule.non_character`) to meet the eight-word rule.

## The six answer links

| Answer | Decision | Why |
| --- | --- | --- |
| `want.know_where` with `ds.power` | Removed | "Not knowing where you stand" is a gap in information, not a power asymmetry. `book.hom` stays. |
| `read.distinguishing` with `ds.base_rates` | Removed | "Has he done this to others?" asks about one person's history. The protocol forbids base rates. `alg.tree` and `ds.voi` stay. |
| `what.shifted` with `ds.hindsight_outcome` | Replaced with `dos.commit` | Hindsight bias is about knowing an outcome, and the old why quietly doubted the person's memory in a case that may be retaliation. The new link says a goal can only be shown to have moved if the earlier one was written down with a date. |
| `step.assumes` with `alg.bayes` | Kept, why rewritten | "Move it by the right amount" implied numbers. It now says naming the assumption states what you believe so that what happens next can change it. |
| `what.missed` with `case.metrics-reward-the-wrong-thing` | Kept, why rewritten, and now seat-filtered | The case is written for a manager. The why now says it applies when the person manages the other party and not to a peer or a manager. The server also sends cases only to a manager or team lead. |
| `who.colleague` with `ds.power` | Kept, why rewritten | "Direct candour is more often safe" had no source. The why now says peers hold informal influence and compete for recognition, so the step is an agreement, not an instruction. |

Not changed, left for later: `need.escalate` with `alg.tree` (the tree needs odds), `post.d30` with `ds.one_vs_pattern` (the longer window claim), and the doubtful `book.hgw supports ds.psych_safety` and `path.agency specializes loop.learning`. The audit marked these doubtful or listed them outside the six.

## New relations (from the view-from-below work)

Eleven relations were added for the `seat.*` ideas: two `specializes` on `ds.power`, one on `ds.system_person`, four `supports`, two `tension`, and two `override` from `rule.safety_flag` (over `seat.escalation_ladder` and `seat.manager_constraints`, since a constrained manager can explain a decision and never conduct). Each has a why of at least eight words.
