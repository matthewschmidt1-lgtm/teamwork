# Teamwork: an evidence-first advisor for working with people

*Product thesis, artifact audit, knowledge architecture, experience, validation plan and design direction. Written 19 October 2026. Nothing has been built.*

**How this was written.** I read the code, copy, tests and notes of Friction, Decision OS and Stillward, the website's source and live page, and the Friction second-look brief from earlier today. Where I describe what a project does, I name the file. At your instruction, Goalpost, Fulcrum and the Can This Test Tell? study are left out of this brief entirely; Teamwork draws on the four live projects, the website's own structures, and the seven books. I have not accessed the text of any of the seven books in this session. What I say about them rests on their widely reported central ideas, on your takeaways in the website's Reading section, and on the thirty book-derived management cases in Decision OS Module 3. I say so again where it matters. Everything about users is a hypothesis; there is no real-user evidence anywhere in this family yet, and this brief does not pretend otherwise.

---

## Part one. Deliverable 1: the product thesis

### The problem

Someone leaves a meeting feeling disrespected, or reads a message from a colleague who has missed a commitment for the third time, or is told by a manager to do the thing they were told not to do last week. They know something is wrong. They do not know whether the problem is the other person, themselves, the team, or the way the organization is set up, and the advice they can get in the moment ("communicate better", "set boundaries", "assume good intent") sounds reasonable without telling them what to do on Tuesday. Most people respond anyway, from the feeling, and the next time it happens they have learned nothing except that it happens.

A general-purpose assistant already gives decent advice here. That is the fact Teamwork has to face from the first day. What a chat assistant does not do, left to itself, is refuse to diagnose a person it has never met, insist on separating what happened from what the user thinks it meant, name the explanation that is not about anyone's character, ask the user to write down what a good outcome would look like before they act, and then, weeks later, hold them to that sentence rather than to the one they remember. Those five disciplines are the product. Each of them is already practised somewhere in your existing work: the website's Learning Loop (Signal, Understanding, Decision, Action, Learning) is the shape; Friction weights what happened above what someone feels; Decision OS makes you commit before it shows the answer and tells you to rule out the situation before you explain a person; Stillward treats the user's own evidence as the only proof that counts.

### The target user and the moment

The first user is an individual contributor or first-line manager in a knowledge-work job, in the hour or the evening after a difficult interaction, or the night before a conversation they are dreading. Not HR, not an executive, not a team using it together. The moment of need is "I have to deal with this and I don't know what to do, and I want to get it right." That moment is frequent, emotionally loaded, and currently served by friends, a notes app, and whatever chat assistant is open.

### The proposed benefit

In about ten minutes, the person leaves with: a clearer account of what actually happened as distinct from what they concluded; at least one explanation that is not about the other person's character; one concrete next step with its risks stated; two or three sentences they could actually say; a written line about what a good outcome would look like and when they will check; and, if they return, an honest look at whether it worked and one lesson in their own words. The benefit is a better-made decision and a lesson retained, not harmony and not reassurance.

### What the existing work contributes, distinctly

**The website** contributes the frame. The Blind Spot section's two loops define the test for every product behaviour: did the activity change what happens next, or did it just produce another meeting? The Three Lenses (Business, System, People) are the rule that a personal problem must be looked at as a possible system problem and a possible business problem before anyone's character is discussed. The Path to Agency's six forces (Awareness, Trust, Conditions, Value, Incentives, Leverage) are already written as diagnostic cards in `Matthew Schmidt/index.html` under `ideaData`, each with healthy, warning signs, pattern, move and ask. They are a content model, not just philosophy.

**Friction** contributes the evidence discipline and the system vocabulary. Its engine discounts reassuring self-report, counts admissions about one's own part more, and counts questions about events in full (`Friction/js/content.js`, `SELF_REPORT`). Its fifteen states (direction, economics, capability, trust, loss, pressure, focus, information, decision rights, conflict avoidance, blame, centralized authority, execution, leverage, talent) are the names for "it is not the person, it is the setup". Its outcome step compares what was predicted with what was observed and lets the read change (`Friction/js/engine.js`, `applyOutcome`). Its QA record's steady finding, that the answerer matters more than the facts, is the warning Teamwork most needs to hear.

**Decision OS** contributes the management knowledge in usable form and three mechanics. Module 3, Manage (`decision-os/js/scenarios3.js`), is thirty people-management cases built from six of the seven books, each with a pause question shown before the options, two values in tension, the lesson the strong move follows and the lesson pulling the other way, and weak picks tagged into habit families: Rescuing, Avoiding, Controlling, Pleasing, Over-promising, Defending, Grinding, and One explanation ("You settle on the first story that fits and stop looking"). Its pre-meeting questions ("Am I trying to solve the problem, or prove that I'm right?" "What part of this have I contributed to?") and its principle "Before you explain a person, rule out the situation" are Teamwork's own voice already written. Its reveal rule, never show the preferred option before the choice, becomes Teamwork's "say what you expect before you look".

**Stillward** contributes the way to treat a person who is not at their best: one thing per screen, the tap that advances, no streaks, no catch-up guilt, a feeling check where "Still heavy" opens three exits, and the user's own evidence as the proof ("Not our claim, yours").

### The strongest reasons this could fail

1. **It is not better than the chat assistant the user already has.** If a careful prompt in ChatGPT produces the same quality of advice, Teamwork is a thinner wrapper with a nicer font. This is the primary risk and the pilot is designed around it.
2. **A one-sided account cannot be verified, and the product may launder a grievance.** Everything the advisor knows comes from one upset person. The disciplines above reduce this; nothing removes it. Friction's QA record says this plainly about leaders; it will be truer of someone who feels wronged.
3. **Structure is the last thing an upset person wants.** If the sort-and-commit steps feel like homework, people will go back to the chat box, and if the look-back feels like homework nobody returns, and the learning claim collapses.
4. **Some situations are not advice problems.** Harassment, retaliation, discrimination, and threats to someone's job need routing to people with authority and duty, not a conversation plan.
5. **Sensitive data.** Users will type names and details about real colleagues. Retention has to be minimal and local by default, and the model call has to be honest about where words go.
6. **You.** Every project in this family is built by one person with no distribution. The expected information value of another prototype is low until one of them has met real users.

### Vision versus what is known

The vision is an advisor that helps people understand, decide, act and learn better than simpler alternatives. What is known: the evidence disciplines are implementable, because Friction implements them; the book-derived management vocabulary exists in usable form, because Decision OS Module 3 holds it; the design conventions are mature, because Stillward and the website embody them. What is not known: whether anyone wants the discipline at the moment they are upset, whether it changes what they do, and whether it beats a plain assistant. Nothing in this family has been tested with a real user.

### Outline of the remaining deliverables

Part two audits the artifacts. Part three maps the books and projects into one knowledge system. Part four is the problem map with three contrasting cases. Part five is the end-to-end experience with three reasoned scenarios. Part six is the schema and the smallest implementation. Part seven is the pilot. Part eight says what to build, defer and abandon. Part nine is the design direction, the experience map from first load to the call to action, the acceptance standard you asked for, and the build sequence as implementation prompts, held back until the pilot earns them.

---

## Part two. Deliverable 2: project and source audit

### What each project actually does

**Friction** (`Projects/Friction`, live at friction-production.up.railway.app). A fifteen-state causal Bayesian network over organizational constraints, enumerated exactly with no library, with a value-of-information question picker, seven questions always asked (the last time you heard something you did not want to, the last time a serious problem was raised, overruling, your own part, loss, the last open disagreement, the last missed number), one recommended experiment with three things to watch, and an outcome step that updates the read. All inputs are closed options except one free-text line on the learning screen. It stores up to twelve runs locally under a versioned key. Three expert-agent re-tests in `qa/experts/v5` agree that the top gap is a multi-rater step, that flattering answerers get a blank page, and that the page is generic where the person is specific. The second-look brief's recommended increment, not built, adds a free-text frame and a way to ask two colleagues the same seven questions.

**Decision OS** (`Projects/decision-os`, live). A CPG sales training site in Modules 1 and 2, Accounts and Portfolio. Module 3, Manage, is the part that matters here: thirty management cases, book-derived, with the structures described above, behind a soft client-side gate. Everything is pre-authored; the user only picks. There is no free-text entry, no follow-up date and no reminder. The only revisit is replaying cases picked weakly. Its summary speaks only with enough data: an early read under five plays, a habit named only after three tagged picks. Its honesty rules in `CLAUDE.md`: never show an answer without the logic, never reveal the preferred option before a choice, show ranges where confidence is not high, never write "because" beyond what the attribution supports.

**Stillward** (this folder, live). Three single-question screens (domain, state, energy), a practice card with a "What this means" gloss, a three-minute ring timer, a done screen with six feeling options where "Still heavy" opens sit two more minutes, try a different voice, or let it be. No accounts, no backend, a counter that only grows, no re-entry nagging. DM Serif Display and DM Sans, body 15 to 19 px at 1.75 line height, parchment and sage.

**Algorithm Atlas** (`Projects/algorithm-atlas`, live). Seventy-six lessons with live visualizations and a schema that bans em dashes and stock phrases. Relevant to Teamwork only as deep links: `bayesian-updating` ("a rule for changing your mind by the right amount") from a look-back, and the attention lesson's own caution that weights are not explanations, which is a warning for any product that shows "why" it reached a read.

**The website** (live, matches the local source). About, Operating Philosophy, The Blind Spot with the two loops, The Three Lenses, The Path to Agency, The Friction, Things I've Built, Things I believe, My Reflections, Reading, Contact. The Reading section holds six books with your takeaways: culture is an operating system; self-awareness is a professional skill; your job is to make the people around you better; understand the business underneath the job; think in models, not formulas; build systems, not heroics. Five Dysfunctions is the one book of the seven that appears nowhere in the family.

### Useful principles, redundancies, contradictions, gaps

Principles already implemented and ready to carry over: happened outweighs impression (Friction); commit before you see (Decision OS); rule out the situation before explaining the person (Decision OS); the user's own part is always a live hypothesis (Friction's required self question, Decision OS's habit families, the 15 Commitments takeaway); say "can't tell" when you cannot (Friction's honest null); speak only with enough data (Decision OS's summary rule); one thing per screen and no guilt (Stillward); counts, never scores (all of them); a copyable plain-text result at the end (Friction's "Copy the read").

Redundancies: Friction's learning screen and Decision OS's revisit list are both look-backs of a kind, neither has a user who has returned, and neither shares code with the other. Teamwork should not be a third look-back nobody returns to; it should either be the first one somebody does, or the evidence that nobody will.

Contradictions: Friction's model assumes the respondent is a leader with authority over the system; Teamwork's user often has none, so "the experiment" cannot be an organizational change and must be something one person can do. Decision OS trains judgment on authored cases where a best answer exists; Teamwork faces live situations where it does not, so its reveal mechanic must become "state your expectation" rather than "see the right answer". Stillward refuses all structure and advice by design; Teamwork is structure and advice, and must borrow Stillward's manner without borrowing its refusal.

Missing: any book text or notes beyond your website takeaways; any real user; any example of a workplace situation written by a real person; Lencioni's material in any form; any place in the family where a person describes a problem in their own words (every input everywhere is a closed option).

### What I could not verify

I did not run any project's tests in this session. I did not check the Decision OS live site beyond its repo saying it deploys on push. I have not read the seven books in this session. I did not check the second-look brief's claims against the Friction code line by line; I relied on it where it cited paths.

---

## Part three. Deliverable 3: one knowledge and reasoning system

### The shape

Seven layers were proposed. Three are enough to start, and the other four are behaviours of the three rather than separate systems.

**The principle library** holds a few dozen entries, not seven modules. Each entry has an id, a source and chapter or page reference once you supply the material, the idea in one or two sentences, when it applies, when it misleads, what it tends to conflict with, and whether the entry is source-supported or a synthesis of mine. The website's six force cards and the thirty Module 3 principles already have this shape. Teamwork's library begins by importing those and adding Lencioni.

**The situation model** is a vocabulary for what might be going on. It has three kinds of cause and the advisor must always carry at least one of each until the facts rule it out: something about the other person's behaviour; something about the user's own part; something about the system (roles, incentives, information, decision rights, workload, priorities). Friction's fifteen states are the system vocabulary. Decision OS's habit families are the user's-part vocabulary. The books supply the behavioural vocabulary. The Three Lenses are the rule that all three are looked at.

**The protocol** is the sequence of reasoning the advisor follows. It is the Learning Loop made specific for one person's situation:

1. Take the account in the user's words. (Signal.)
2. Sort it: what happened (words said, things done, dates, who saw), what the user was told, what the user concluded. Reflect the sort back and let them correct it. This is Friction's event-versus-impression weighting made visible and editable.
3. Ask what they want to be different. Not "what do you want to do" yet.
4. Hold at least two explanations open, one of which is not about anyone's character. Say which facts would tell them apart. This is "rule out the situation" from Decision OS, Munger's insistence on more than one model, and the System lens applied before the People lens. (Understanding.)
5. Ask at most one question whose answer would change the advice. If none would, do not ask. This is Friction's value-of-information rule, which only asks a question if some answer could change the recommendation.
6. Weight the facts: happened in full, told at a discount, concluded as a hypothesis.
7. Say what the user can influence and what they cannot, and name any power or safety factor that changes the whole frame.
8. Recommend one next step, from the intervention set, with the assumption it depends on, how it could backfire, and the alternative. Give the words. (Decision.)
9. Write the post: one sentence of what they would observe if it worked, and a date. This is Decision OS's commit-before-you-see and Friction's watch list, in a sentence. (Action.)
10. At the look-back: ask what they expected and whether it happened, before showing the sentence. Then show it. Then say honestly whether one outcome can tell them anything (it usually cannot distinguish a good approach from luck; two or three similar situations can). Then one lesson in their own words, tagged to the pattern, so it surfaces next time a situation matches. (Learning.)

Layers E, F and G in your brief are steps 9, 4 and 10 of this protocol. The decision and intervention layer is the library plus a set of intervention entries with the same fields. The diagnostic layer is steps 2 through 7.

### How the books enter

I am working from their widely reported central ideas and your takeaways, not from the texts. Treat the following as a map to be checked against the material, not as settled.

- **The 15 Commitments** supplies the user's-part vocabulary and the stance: curiosity over being right, taking responsibility without taking blame, candour, noticing when you are "below the line". It governs step 2 (separating fact from story is one of its own practices) and step 4. Your takeaway, "self-awareness is a professional skill", is the sentence Teamwork's self question should live by.
- **Five Dysfunctions** supplies team-level patterns: absence of trust, fear of conflict, lack of commitment, avoidance of accountability, inattention to results, in that dependency order. It governs the team cases in step 4 and the "silence is not agreement" family. It is absent from your other work and needs source material first.
- **Trillion Dollar Coach** supplies the relational interventions: trust built through candour and care at once, feedback that is honest and early, the manager's job as making others better. It governs step 8 when the user manages someone.
- **How Google Works** supplies the conditions vocabulary: context over control, transparency, decision rights, hiring and environment. It governs the system explanations in step 4 for knowledge-work teams.
- **What the CEO Wants You to Know** supplies the business lens: cash, margin, velocity, growth, customers. It governs the explanation "your manager is reacting to a number you cannot see" and the question "what is this person being measured on?"
- **Poor Charlie's Almanack** supplies the discipline of step 4 itself: incentive-caused bias, inconsistency avoidance, the first-conclusion tendency, inversion. It is the reason the advisor never settles on one story, and Decision OS's "One explanation" habit family is already its application.
- **High Output Management** supplies the management-system vocabulary: output is the measure, task-relevant maturity decides how closely to manage, one-on-ones and the staff meeting as instruments, leverage. It governs the explanation "this is a process problem wearing a person's face" and most delegation cases.

### Where they pull against each other

Grove measures a manager by output; the 15 Commitments measures a leader by how they show up. Lencioni wants vulnerability-based trust built in the open; Munger warns that incentives will quietly override whatever trust was built. Campbell's care for people and Charan's insistence that the business comes first collide whenever the kind thing and the commercial thing differ. The handling rule comes from Decision OS Module 3, which already renders every case as two values in tension with the lesson the strong move follows and the lesson pulling the other way. Teamwork shows the tension rather than resolving it silently, and the conditions on each principle decide which one leads in this case. Where conditions cannot decide, the advisor says so and gives the user the choice with both costs named.

### Source material needed

To attribute responsibly you need, for each book, either your own notes and marked passages, or legally held excerpts, or at minimum a chapter-level outline you have checked. Without that, every entry stays marked synthesis and the product must not display an author's name beside a claim as if it were a quotation. Priority order: Lencioni (nothing exists), Grove and the 15 Commitments (most used in the protocol), then the rest.

---

## Part four. Deliverable 4: the workplace problem map

### The taxonomy

Eighteen areas were listed in the brief. They collapse into a usable map with three axes, and a situation is placed on all three at once rather than filed under one.

**Where the cause may sit:** the other person's behaviour; the user's own part; the relationship between them (history, expectations never stated); the team (norms, dynamics, who speaks); the system (roles, decision rights, incentives, information, workload, priorities, process); the organization's situation (pressure, change, business trouble). The last two are Friction's territory and use its state names.

**What kind of trouble it is:** a misunderstanding; a broken commitment; a conflict of interest or priority; a feedback or performance problem; a trust problem; a power problem; a boundary or conduct problem; a decision that will not get made; a repeated mistake nobody retains.

**What the user needs right now:** to understand; to decide; to prepare for a conversation; to recover from one; to decide whether to escalate or leave; to check whether something they tried worked.

Overlap is normal and the advisor is required to carry it: a missed commitment (trouble) by a colleague (cause) under a reorganization (organization) where the user never stated the deadline (own part). Unusual cases that fit nowhere are handled by the protocol, which does not depend on the taxonomy: sort the facts, hold two explanations, ask one question, one step, one post. The taxonomy improves retrieval from the library; it is not a gate.

### Three contrasting cases

**Case one: the user may be mistaken.** "My boss doesn't respect me. He cut me off twice in the planning meeting and gave my project to Dana." Sorted: happened, interrupted twice in one meeting and reassignment of a project; told, nothing; concluded, disrespect. Two explanations: he does not value the user's work, or the planning meeting was running long with a decision due and Dana's team had capacity. The fact that would distinguish them: has he interrupted others, and what did he say when he reassigned it? One question: "What reason did he give, in his words?" If the answer is "none, he just moved it", the respect reading strengthens. If it is "he said your plate was full with the launch", the frame changes to a priorities conversation. The next step in either case is a question to the boss rather than a complaint, and the post is "within two weeks I will have heard his reason in his own words and know whether I am on the launch or off it." The advisor does not say the user is wrong. It says the facts so far fit two stories.

**Case two: the problem is structural.** "My team never follows through. I set clear deadlines and people miss them and nobody seems to care." Sorted: happened, three missed deadlines in the last month across two people; concluded, nobody cares. The System lens applies before the People lens: who else assigns work to these people, do they report to the user or not, what are they measured on, how many priorities do they carry. If the user is a project lead without authority over people who have two other managers, this is Friction's decision-rights and focus states, and the honest advice is that no amount of clearer deadlines fixes it. The next step is a conversation upward about allocation, not a conversation downward about accountability, and Grove's output lens is the frame. The post: "by the end of the month, the two of them have a stated share of their time on this work that their managers agreed to."

**Case three: it is not an advice problem.** "My manager has started commenting on what I wear and suggested we discuss my review over drinks. I said no and now I'm off the client account." Sorted: happened, comments on appearance, a social invitation tied to a review, removal from an account after refusal. The protocol recognizes conduct and possible retaliation and changes register: no two-explanations exercise about the manager's intent, no conversation openers. Instead, in plain and calm words: write down the dates and words now, keep copies outside work systems, here is how to find who in your organization holds this duty, and here are outside resources. Teamwork says what it is not, without alarm, and stops offering workplace advice for this situation.

---

## Part five. Deliverable 5: the end-to-end experience

### Opening

Your suggested opening is right in substance and slightly long for someone upset. The screen shows one question and one reassurance:

> What's happening at work that's making it hard to work well with someone?
> Say it the way you'd tell a friend. You don't need to know what the problem is yet.

A single large text field. Below it, quietly: "Nothing you write is shown to anyone. You can delete it any time." No account. No choosing a category. If they type one sentence, that is enough to begin.

### The adaptive sequence

**Reflect.** The advisor shows what it heard in three short groups: what happened, what you were told, what you've concluded. Each line is editable and movable. "Did I get that right? Move anything that's in the wrong place." This is the one screen that must be exceptional, because it is the screen that makes the user feel understood and simultaneously starts the discipline.

**Want.** "If this went well, what would be different a month from now?" One line.

**Possibly one question.** Only if the answer would change the advice. The screen says why: "One thing would change what I'd suggest." Structured choices when they clarify, free text always available.

**The read.** Two explanations side by side, in prose, each with the facts that support it and the fact that would tell them apart. A line on the user's own part, framed as a question not a verdict ("One thing worth asking yourself: did he know the deadline mattered to you?"). A line on what the user can and cannot influence.

**The step.** One recommended next move, why it fits this case, what it assumes, how it could go wrong, and the alternative. Then the words: two or three openers the user can edit. If the user manages the other person, the Module 3 pre-meeting questions appear here.

**The post.** "Before you go: one sentence about what you'd see if this worked, and when you'll check." Pre-filled from the want and the step; editable. A date, default two weeks. A calendar file, no reminders from the product.

**Done.** A single page with everything above, copyable. Then Stillward's exit: "How do you feel about it now?" with options including "Still stuck", which opens "Talk it through differently", "Just save it for now", and "This isn't a conversation problem", which routes to the conduct path.

**Look back** (on return, after the date). First, blind: "What did you expect would happen?" and "What happened?" Then the post opens and the two are shown together. Then honesty about inference: one outcome cannot tell a good approach from luck; "the same thing with the same person" twice can start to. Then: "What would you tell yourself next time, in one line?" Saved against the pattern and the person, surfaced the next time a new situation matches either.

### Three scenarios, reasoned

**"I think I might be the problem."** The protocol is built for this and must not overreach. Sorted facts first; the advisor asks for the last two specific moments the user has in mind. It holds two explanations: the user's part is the main cause, or the user's part is real but a smaller factor inside a system or relationship pattern. It does not reassure ("you're being too hard on yourself") and it does not confirm. The step is usually to ask one trusted colleague one specific question ("when I pushed back in Thursday's review, how did that land?") rather than to change behaviour on a guess. The post is "by Friday I will have asked and heard the answer." Habit families from Module 3 appear only if the user's own account names a pattern twice, following Decision OS's own rule of speaking only with enough data.

**"We ran an experiment and the results look good, but I'm not sure we can trust them."** This is a different kind of question and Teamwork should say so rather than stretch. It asks what was compared, how the groups were chosen, what else changed at the same time, and whether the measurement stayed the same, and then says in words which of those is the live worry and what one check would settle it. It never says "valid". If the person wants more, the Atlas's `ab-testing` and `bayesian-updating` lessons are a click away. The post is numeric here: the number that would make them stop and the number that would make them scale, written before the next read.

**"We keep having the same disagreement and nothing changes."** Sorted: happened, the last two instances with who said what; concluded, that the other party is stubborn. Explanations: a value conflict (two legitimate priorities, Lencioni's commitment problem), or a decision-rights gap (nobody owns the call so it recurs, Grove and Google, and Friction's decision-rights state). The distinguishing fact is "who has the authority to decide this, and have they?" The step is usually to make the decision rule explicit rather than to win the argument. The post: "the next time it comes up, we know whose call it is." At the look-back, the pattern "repeat" is what the lesson attaches to.

---

## Part six. Deliverable 6: schema and minimal implementation

### Schema

Six record types, all plain JSON, all small.

- **principle**: id, source (book, chapter or page once supplied), idea, applies_when, misleads_when, conflicts_with, status (source_supported or synthesis), related.
- **intervention**: id, name, when_appropriate, assumes, backfires_when, alternatives, tradeoffs, evidence_it_helped, words (openers), principles.
- **situation** (one per episode, stored locally): id, account (verbatim), sorted {happened[], told[], concluded[]}, want, question_asked, answer, explanations[] {text, supporting_facts, distinguishing_fact, kind: person | self | system}, influence, safety_flag, step {intervention_id, why, assumes, risk, alternative, words}, post {sentence, date}, created.
- **lookback**: situation_id, expected_blind, happened_blind, post_shown, matched, inference_note, lesson, pattern_tags, person_tag, at.
- **pattern**: tag, count, lessons[] (the user's own lines), last_seen.
- **record**: counts only. Situations, look-backs done, posts that matched, lessons written.

Traceability: every explanation and step the advisor produces carries the principle ids it drew on, shown to the user as attribution in prose ("Grove's point about output applies here") only for source_supported entries, and as "a rule of thumb" for synthesis.

### The smallest implementation

The family convention is zero build, static, local storage, no backend. Teamwork breaks it in one place and only one: the reasoning requires a language model, and a model call needs a key that cannot live in a browser. So:

- One static page in the family style (vanilla modules, no framework, `localStorage` under a versioned key, all copy in one content file).
- One small Python server on Railway (this Mac has Python and no Node) that holds the key, receives the account and the protocol step, calls the model, and returns structured JSON. It stores nothing. Python keeps the whole stack in a language you already use.
- The protocol as a system prompt plus the principle and intervention libraries as JSON the prompt can cite. No vector database, no fine-tuning, no agent framework. Retrieval is the tag match in the pattern record and a plain keyword match into the library, which at a few dozen entries needs nothing more.
- The persona harness pattern from Friction, reused: scripted accounts, the real pipeline, a judge reading in the person's voice, with the usual caveat that this is rehearsal and not evidence.

Before any of that, though, there is a version with no code at all, and it is the one to run first. See part eight.

---

## Part seven. Deliverable 7: the validation plan

### Design

Twelve to sixteen people who have had a difficult workplace situation in the last two weeks and still have to act on it. Recruited from your own network and theirs, not from a panel. Each brings their real situation.

Three conditions, assigned at random, one per person:

- **A, plain assistant.** They describe the situation to a general chat assistant with no special prompt and get its advice.
- **B, the checklist.** A one-page paper version of the protocol: sort what happened from what you concluded, write a second explanation, one step, one sentence of what you'd see and a date. No model.
- **C, Teamwork.** The protocol run as a prompted conversation with the model, facilitated by you or run in a shared assistant project. Not a built app.

Everyone gets a look-back call two to three weeks later.

### What is measured, separately

- **Advice quality**, rated blind by two readers on transcripts or sheets with names removed: specific to this case rather than generic; at least one explanation not about character; the user's own part raised without blame; no diagnosis of the absent person; risks of the step named; safe routing when conduct is present.
- **Immediate experience**, reported right after: clearer about what happened, clearer about what to do, felt heard, felt judged, would do this again. Short Likert items, plus one open question.
- **Behaviour**, at the look-back: did they take the step, in what form, when.
- **Honest assessment**, at the look-back: what they recall expecting versus what they wrote, asked before the sheet is shown, and whether their account of the outcome shifted toward the result they wanted.
- **Perceived outcome**: did the situation improve, from their view; not treated as workplace benefit.

### Criteria set now, before data

Proceed to a build if C beats A on blind-rated quality in at least two thirds of matched pairs, and C is at least as good as B on behaviour and honest assessment, and at least half of C's participants say unprompted that they would use it again. Redesign if C beats A on quality but not B on behaviour: the structure works and the model adds nothing, so publish the checklist instead. Stop if A matches C on quality, or if fewer than a third take the step in any condition, or if the look-back is refused by most participants: the learning claim cannot be made.

### What this pilot cannot establish

Whether the workplace situation actually improved; whether a lesson retained changes a later decision (that needs months and repeated situations); whether the product is safe across the range of conduct cases (it needs a separate review with someone who holds that duty professionally); whether anyone pays. It also cannot separate your facilitation from the protocol unless C is run unfacilitated for at least some people, which it should be.

---

## Part eight. Deliverable 8: build, defer, abandon

### Build first

Nothing with a user interface. First the protocol document and the one-page checklist, then the pilot above. The protocol is about two pages. The checklist is one. The pilot takes three to four weeks of calendar time and a few hours of yours per week.

If the pilot passes, build the static page and the one-file Python proxy, with only the Describe, Reflect, Read, Step and Post screens, and a Look-back that works when someone returns. No account, no history view beyond the list of open posts, no pattern surfacing until there are patterns.

### Defer

The principle library beyond what the website and Module 3 already hold; Lencioni, until you have the material; pattern retrieval across situations; a team mode; anything that stores data off the device beyond the stateless model call; a link from a structural read into Friction (plausible later, not now); the experiment-trust path beyond the four plain questions above.

### Abandon

The seven-module architecture; scores, levels, streaks; a long intake; an attempt to verify the user's account; any claim that the advisor knows the other person's motives. Also abandon, for Teamwork's purposes, the idea that repeat use is the goal. The product succeeds for a user who stops needing it.

### The main risks

Technical: the model call is the first server in the family, and it must be stateless and logged nowhere. Ethical: one-sided accounts about named real people; the conduct path must be right before anything ships, and the product must never present a book's idea as evidence. Product: Friction and Decision OS already have look-backs with no returning users; a third without a pilot is the most likely way this fails.

### The single next action

Write the one-page checklist (condition B) and the two-page protocol (condition C), then recruit the first four participants. The checklist is the control that tells you whether the product is the protocol or the model, and that is the question with the highest information value in this whole plan. If the checklist does as well as the model, you publish a page and save a year.

---

## Part nine. Design direction, experience map, acceptance standard, build sequence

You asked, in three different voices, for a cinematic luxury site, for quiet luxury with human warmth for stressed people, and for an acceptance standard that judges the working interface by whether people feel clearer and more capable. These are reconcilable only if "cinematic" means pacing, composition and restraint, not spectacle. A person who has just been humiliated in a meeting does not want a film. They want a room where someone has made space for them to think. That sentence, which is your own governing principle, is the creative concept, and every choice below is tested against it.

### The concept: a lamp left on

The emotional reference is not a studio or a product launch. It is the one lit office on a floor after everyone has gone home, and a colleague you trust saying "sit down, tell me what happened". Warmth with edges. Nothing decorative. Everything you see has been placed because it is needed. The narrative arc of the site and the app is the same arc as the protocol: arrive troubled, be heard precisely, see the situation become two stories instead of one, see one step, leave with a sentence to keep.

### Art direction

**Ground and light.** A warm, matte, paper-like ground, never pure white and never a texture image. Depth comes from light, not from shadows under cards: a single soft gradient of warmth that is strongest around the text field on the first screen and fades toward the edges, as if the field were lit. No glass, no blur, no neon, no gold.

**Palette, and why.** Three neutrals and one accent. Ground, a warm off-white in the family of Stillward's parchment but a shade deeper so it reads as evening rather than morning. Ink, a near-black with a touch of warmth for all primary text. Stone, a mid warm grey for secondary text and for the user's own conclusions when they are shown beside the facts, so the eye learns that lighter means "you concluded this" and darker means "this happened". The one accent is amber, the lamp, used for exactly one thing on any screen: the next action. Nothing else is amber, ever. For the conduct path, no red: the register changes by slowing down and simplifying, not by alarm colour. Exact values are a rendering decision to be checked on screen, which is the acceptance rule below.

**Typography.** Two families, both with character, since you have said plain fonts bore you. Display and the user's own words in a serif with warmth and an optical axis, so a sentence a person typed can be set large and feel like it was written rather than submitted. Everything the advisor says in a humanist sans with generous width, comfortable at 17 to 19 px body with a line height near 1.7, because people read worse when stressed. The split carries meaning: serif is yours, sans is the advisor's. Fraunces is the obvious candidate for the serif since it is already yours; whether Teamwork should share it or have its own voice is a question to settle in the rendered comparison, not here.

**Composition.** One column, a measure of 60 to 70 characters, generous margins that widen rather than fill on large screens. One idea per screen in the app. On the site, each section is one proposition and one restrained visual. Hierarchy by size and weight and space, not by boxes; borders only around things a person can type into.

**Materials and depth.** Paper, ink, light. The only object is the text field, which has the slight depth of a page lying on a desk. The two-explanations screen uses two columns on wide screens and a vertical stack on phones, divided by light, not a line.

**Motion language.** The page breathes slower than the user does. Ambient motion is one thing, the lamp's warmth drifting across the ground on a loop of fifteen to twenty seconds, so slow that it is felt and not watched, in the family of Stillward's breathing ring and the website's signal line. Feedback motion is under 300 ms, eased, and always confirms what the user did. Transitions between protocol steps slide the completed step up and dim it to stone rather than removing it, so progress is visible without a progress bar. Nothing moves on scroll on the site except opacity. Reduced-motion users get no ambient motion and instant transitions, and the product is fully legible without any of it.

**Atmosphere and emotion.** Quiet, warm, unhurried, exact. The microcopy carries the warmth: "Say it the way you'd tell a friend." "Did I get that right?" "One thing would change what I'd suggest." "Still stuck? That's a fair answer." Never clinical, never therapeutic, never a joke about a painful situation.

### The site, from first second to call to action

The site has one job: to get the right person to type one sentence. Conversion is "a situation begun", and the whole page is short enough to read in two minutes. It follows the bar you set for the website's Friction section: one recognizable question, almost no copy, one restrained visual.

1. **Arrival (0 to 3 seconds).** The ground loads first with the warmth already present; text renders in a single pass with no layout shift and no loader. One line in the serif: "What's happening at work that's making it hard to work well with someone?" A text field, lit. Below, in the sans: "Say it the way you'd tell a friend." The first screen is the product. There is no hero image because the hero is the question.
2. **What this is (one scroll).** Three short sentences: it helps you see what happened as separate from what you concluded; it holds more than one explanation; it leaves you with one step and one sentence to check later. No feature grid.
3. **How it thinks (one scroll).** The only visual on the page: a sample account, invented and labelled as such, sorting itself into happened, told and concluded as the section scrolls into view, the concluded lines fading to stone. This is the demonstration of the core discipline and it is the moment that distinguishes Teamwork from a chat box.
4. **What it won't do (one scroll).** Written plainly: it won't take your side by default, it won't tell you what the other person is thinking, it won't pretend one conversation proves anything, and when something is not a conversation problem, it says so and points you to people with the duty to act. This section is where trust is earned, and it comes before any claim of benefit.
5. **The sentence you keep (one scroll).** A rendering of the one page a user leaves with: the two explanations, the step, the words, the post with its date. Shown as a real page, not a device mockup.
6. **Privacy (short).** Where words go and where they do not, in three sentences. The model call is named honestly.
7. **Call to action.** The same question as the top, the same field, so the page ends where it began and the user who scrolled to the bottom has lost nothing.

Accessibility and performance as requirements: WCAG AA on every surface, 44 px targets, keyboard path through everything including the sorting screen, visible focus in amber, system fonts as fallback so the first paint never waits on a web font, no third-party scripts, total page under 300 KB including fonts.

### The app, as sections of one experience

Describe, Reflect, Want, Question, Read, Step, Post, Done, Look back. Each is one screen, documented in part five. The empty state is the opening question; the loading state while the model works is a single line in stone ("Reading what you wrote") with the lamp's warmth slightly brighter and never a spinner; the error state says what failed and keeps the user's words on screen; the success state is the page itself. Every screen has a way back and a way to stop that saves what exists.

### The acceptance standard

This is a gate, not a mood board. Before the visual direction is approved:

1. The direction is shown as a working interface on a phone and a laptop, with the real protocol running behind it, not as a static design.
2. It is tested by at least four people who have dealt with a difficult workplace situation in the last month, bringing their own situation.
3. The questions asked of them are about state, not aesthetics: did you know where to start within seconds; did you feel heard; did you feel judged; are you clearer about what happened; are you clearer about what to do; would you come back after the date. "Was it beautiful" is not asked.
4. The twelve quality-gate questions from your design brief are answered in writing, with the honest answer to question twelve being "not yet" until real people have used it.
5. If the answers to the state questions are not clearly better than for the plain-assistant condition, the design has not passed, however it looks.

### The build sequence, as implementation prompts

Held until the pilot passes. Each is a self-contained prompt for a build session, in order, with the rule that every stage inspects the existing code first, keeps tests passing, and ends deployed or deployable.

1. **Protocol and checklist.** "Write the two-page Teamwork protocol as a system prompt and the one-page checklist as a printable page, from the brief in `Projects/Teamwork/teamwork-brief.md` part three. Test the protocol against the three scenarios in part five with scripted accounts. No app."
2. **Project setup.** "Create `Projects/teamwork` as a static site in the family convention: `index.html`, `css/`, `js/` as ES modules, `content.js` holding every line of copy, a `tests/run.html` harness, a `CLAUDE.md` with the honesty rules (never diagnose the absent person, never say valid, counts not scores, no em dashes). Add `railway.json` and a `server/app.py` stateless proxy that holds the model key and returns JSON for one protocol step. Serve locally with Python."
3. **Design system.** "Define the tokens: ground, ink, stone, amber; the type scale with two families and system fallbacks; spacing and motion scales including the reduced-motion path. Build the shell with the lamp gradient and the one text field. Render it on a 375 px and a 1440 px viewport in headless Chrome and check contrast on every pairing."
4. **Describe and Reflect.** "Implement the opening screen and the sort screen: the account goes to the proxy, which returns happened, told and concluded groups; each line is editable and movable by keyboard and by pointer. Store the situation locally under a versioned key. Test with the three scenarios."
5. **Want, Question, Read, Step.** "Implement the remaining protocol steps with one screen each, the two-explanations layout, the step with its assumption, risk, alternative and words, and attribution in prose only for source-supported principles. Add the conduct path and test that case three never receives openers."
6. **Post, Done, Look back.** "Implement the sentence and date, the copyable page, the .ics download, the Stillward-style exit, and the blind look-back that asks before it shows. Add the counts-only record."
7. **Site.** "Build the seven-section page from part nine around the same opening field, with the one self-sorting demonstration, no scroll-driven motion beyond opacity, and a total weight under 300 KB."
8. **Verification.** "Run the persona harness through the real pipeline, axe-core on every screen, a keyboard-only pass, forced reduced motion, and headless screenshots before and after. Fix what fails. Report exactly what was and was not verified."
9. **Deploy.** "Create the GitHub repository in the web interface, push, connect Railway to it, set the model key as a Railway variable, confirm the deployed page's title and that the proxy answers, and record the live address in `CLAUDE.md`."

### What this part does not do

It does not pick hex values, font files or easing curves, because your own rule is that the direction is approved on a working screen and not on paper. It does not design a logo. And it does not change the recommendation in part eight: none of this is built until the checklist and the model have been compared on real situations.
