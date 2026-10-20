# Design critique, 19 October 2026

A Sonnet design critic reviewed the running prototype after Matthew's reaction ("boring, too much text, not enough space, colors way too bland"). Mobile claims come from the CSS; the 1280 px start screen was seen directly. This is a critique, not a plan; the ranked list at the end is what to do first.

## Verdict

The owner is right, and it is not a copy problem alone. The design has no visual idea: one cream ground, one near-black, grey-brown secondary text and a 12% hairline, so every screen is the same stack of heading, grey help line, list of white boxes. The amber, the lamp and the serif exist in the CSS but are nearly invisible. Root causes in order: no colour or hierarchy idea, a flat type scale where body is 18 px and almost everything else is 15 to 17 px, and the advisor writing 250 to 600 words on the screens that matter, with a fixed 1.7 line height and no pacing.

## Screen by screen

Start. 35 words before the first tap, two stacked serif headings competing, the weakest text on the page is the help line, and five identical white pills are the card pile the brief forbade. Make it one large question, "Who is this about?", with five bare type rows and a thin rule.

What's happening. Nine boxes of 6 to 11 words, about 600 px of identical boxes that scroll on a phone, with the harassment option visually equal to "Something else". Reduce to five short phrases and give the safety option its own quiet line at the bottom.

Reflect. About 11 text styles and roughly 25 interactive controls; the owner wants minimal typing and this is an editing form. Show the sort as three coloured blocks of read-only lines, one tap to move a line, edit only on demand. Delete the group help lines.

Want. About 100 words to answer a one-tap question. Title becomes "A month from now, what's different?" and the help line goes.

Read. The worst offender: about 290 words plus nine label strings on one scroll, about 1,800 px on a phone before the button. Each explanation becomes its own coloured panel with only the two or three sentence story; supports, "what would tell" and tension go behind a "Show why" fold; influence becomes one sentence.

Step. About 240 words and four more caps labels. The step and the first line of words are the screen; assumes, backfires and alternative collapse into one "Check before you do this" fold.

Post. Right concept, but a 33-word prefilled textarea and a native date input. Show the sentence as a large serif quote with an Edit link; the date as three chips (1 week, 2 weeks, a month).

Done. Repeats every previous screen in a white box (450 to 600 words). Lead with the step and the date and a Copy button; the full page collapses behind "See the whole page".

## Colour

Default to a deep warm night, because users are stressed and often on a phone in the evening; paper as the alternate.

- Ground #1F1A17, raised surface #2B2420, lamp pool #3A2D22 radiating from the top.
- Text primary #F3E9DA, secondary #BFAE98, hairline rgba(243,233,218,.12).
- Amber #F2A33A for the next action, the lamp and the selected state only.
- Sage #7FB0A3 for "what happened" and "about the setup". Rose #D98C7A for "concluded" and "about them". Facts are cool, stories are warm, person and setup are opposite hues, so the Read screen reads at a glance. Self gets parchment, no hue.
- Paper variant: ground #F6EFE3, ink #2A211B, amber #B5651D, sage #3F7D6E, rose #A9533F.
- Colour appears as a 3 px left rule or a dot, never a fill.

## Type

Fraunces plus DM Sans is fine; the use is the problem. Fraunces at opsz 144, weight 400 gives hairline strokes that look fragile. Use opsz 36 to 72, weight 350 to 400, SOFT 50, for the question on every screen and for the user's words.

Scale (mobile / desktop): question 32/44 px, line 1.15, weight 380; step name 26/30; user's words 20/22 serif at 1.5; body 17/18 DM Sans at 1.55; secondary 15 at 1.45; label 12 caps at 0.1em, weight 600, only for three things. Five styles per screen instead of about eleven.

## Space and copy

8 px base with jumps 8, 16, 24, 40, 64, 96. Question gets 96 px above and 40 below on desktop; 64 between sections; 16 inside a block. Primary button pinned at the bottom on mobile.

Delete: "Three taps. You don't need to know what the problem is yet." / "Pick the closest. You can add detail in a moment." / "Move anything that's in the wrong place. Change any line. Add what I missed." / the three group help lines on Reflect / "Edit them until they sound like you." / "One sentence, something you could observe. Then a date to check." / the "1 of 3" counter (three dots instead).

Cut: the Read intro to "Two ways this could be true."; the Done help to "Copy this. We'll look again on the date."; the lesson help to "One line for next time."; the privacy line to "Stays in this browser."; the want help to "Pick one or two."

Also shorten the advisor's output: why, assumes, backfires and alternative at about 100 words should be 40.

## The visual idea

Make the lamp literal and structural: one warm pool of light fixed at the top, the only source, and every screen is lit by it. The three stages become a vertical wick of three dots on the left that fills as you go. Amber appears only where the light touches: the selected choice, the next action, the date. On Read, the two panels are lit unequally, the better-supported one brighter. On Done the page is the lamp at its brightest.

## Usefulness

Earns its place: the three taps, the sort, the two readings, the step with words, the observable post, the blind look-back. Does not: the want screen as a separate stop (merge into the taps or infer), Reflect as a form (confirm-only), Done as a repeat (merge with Post), assumes and alternative as separate items, self-question and tension as separate blocks, record counts before there is data. Real users will skip the detail line, the manager questions, the calendar button and the feelings chips.

## Top ten, in order

1. Cut copy; under 90 words on every screen except Read at 140.
2. Collapse Read and Step: stories only up front, the rest behind a fold.
3. Deep warm palette with sage, rose and brighter amber; hue carries happened vs concluded and person vs setup.
4. Bare type rows with one rule instead of white boxed choices.
5. One question per screen, big, with 96 px of air above.
6. Five text styles; Fraunces at opsz 36 to 72; body 17 px at 1.55.
7. Five "what's happening" options plus a separate quiet safety line.
8. Reflect confirm-only, edit on tap.
9. Merge Done into Post; step and date first; full page collapsed.
10. Make the lamp real: stronger, top-anchored, with the progress wick.
