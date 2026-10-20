# The Teamwork site: a scene, not a page

*Concept for the front door to the app. Written 19 October 2026, after the app's redesign. Cinematic here means pacing, scale, light and one reveal. It does not mean spectacle, because the person arriving has just had a bad day.*

## The narrative

The visitor arrives in a dark room. One lamp is on, dim, high on the wall. A single sentence sits under it in large type: "Something happened at work today." Nothing else. As they scroll, the light comes toward them: the pool grows, the room warms, and the sentences change from naming the feeling to showing the method. The one set piece is an account of a bad meeting that sorts itself, line by line, into what happened, what the person was told and what they concluded. Then two readings of it stand side by side. Then the site says plainly what it will not do. Then the one page a person leaves with. At the end the lamp is at its brightest and the app's first question is waiting, lit, with the five answers as the way in. The conversion is a situation begun.

The emotional arc: arrive carrying it, feel it named without being judged, see it come apart into parts, see that more than one story fits, see one step and one sentence, and step into the light to start.

## Art direction

**Light is the structure.** The lamp is a single radial pool fixed at the top of the viewport. Its size and warmth are tied to scroll progress: about 40% at arrival, 100% at the call to action. Nothing else glows. Amber appears only where the light touches: the mark, the selected row, the link into the app.

**Ground.** #15110F at arrival, the same warm family as the app's #1F1A17 but a step darker so the app feels like stepping into the lit room. Text #F3E9DA, secondary #BFAE98. Sage #7FB0A3 for what happened and the setup. Rose #D98C7A for what was concluded and the other person. The palette is the app's; the site only turns the light down and then up.

**Type at a cinematic scale.** Fraunces, optical size 72 to 144, weight 340 to 380, SOFT 50, for every line the visitor is meant to feel: 64 px on a phone, 96 px on a desktop at arrival, 44 to 56 px for the section lines. DM Sans 18 to 20 px at 1.55 for anything the advisor says. The user's example account in Fraunces at 24 to 28 px, because those are a person's words.

**Composition.** One idea per viewport. Each section is at least 90% of the viewport tall so the scroll has rhythm and the visitor is never reading two things at once. Left-aligned text on a measure of 20 to 24 words, generous left margin on desktop so the type has room to be large. No cards, no boxes, no borders except the three-pixel coloured rules that carry meaning.

**Depth.** Three layers: the lamp behind everything, the type, and the coloured rules in front. Depth comes from light falling off toward the edges and from the staggered arrival of lines, not from shadows.

**Materials.** Paper-dark, ink-light, and one warm light. Nothing textured, nothing glass.

## Motion language

- The lamp switches on at load: opacity 0 to 1 over 1600 ms with an ease-out curve, after a 200 ms hold, so the first thing that happens is light.
- Lines arrive as they enter view: 600 ms, translate 14 px to 0, opacity 0 to 1, cubic-bezier(0.2, 0.7, 0.2, 1), staggered 90 ms per line.
- The set piece: the sentences of the account take their colour one by one (an underline in sage or rose, 400 ms each, 160 ms apart), then the sorted blocks fade in below, 700 ms. Nothing moves across the screen.
- Scroll ties to light only: no parallax, no pinned scenes, no horizontal motion. Scroll progress updates one CSS variable on each animation frame.
- Reduced motion: the lamp is on from the start at its mid state, every line is visible, the set piece shows its sorted state.

## The sections, from the first second to the call to action

1. **Arrival** (0 to 3 seconds). Dark room, lamp dim, one line: "Something happened at work today." Beneath, small and quiet: "Scroll. We'll think it through." The mark "Teamwork" top left, "Open the app" top right. Layout: text in the lower left third, the lamp top centre. Interaction: none. Goal: the visitor exhales.
2. **Named.** Three lines, one per scroll beat, 44 to 56 px: "You know something is wrong." "You don't yet know what it is." "That is the right place to start." Light at 55%.
3. **The sort** (the set piece). Label "An invented example", then the account in the serif: "My manager cut me off twice in Tuesday's planning meeting while I was presenting. At the end he gave my Q1 project to Dana, in front of everyone. He doesn't respect me. He thinks Dana is better than me." On entering view the sentences take their colours, then three blocks appear: Happened (sage), Told (empty, shown as "nothing yet"), Concluded (rose, italic, dimmer). One line beneath: "Advice built on the first group holds up. Advice built on the third usually doesn't." Light 65%.
4. **Two ways this could be true.** Two panels, sage and rose rules, the two readings in two sentences each. One line beneath: "The facts fit both. One question would tell them apart." Light 75%.
5. **What it won't do.** Four lines, arriving one at a time: "Take your side by default." "Tell you what the other person is thinking." "Pretend one conversation proves anything." "Give conversation advice when the problem is conduct. Then it points you to the people whose job it is." Light 80%.
6. **What you leave with.** The kept page in miniature: a step name, the sentence as a quote with an amber rule, "Check on" and a date. One line: "One step. One sentence you'd see if it worked. One date." Light 90%.
7. **Where words go.** Three sentences in the sans, small: stays in the browser; goes to the advisor only when you ask for a read; not kept there. Light 95%.
8. **The call to action.** The lamp at full. "Who is this about?" at the arrival scale, and the five answers as bare rows, each a link into the app with the answer already chosen. Goal: a situation begun. Below, small: "About ten minutes. No account."

## Performance, SEO, accessibility

Under 300 KB with fonts, which means two font files with the exact axes needed and display swap, no images, no libraries. No layout shift: the lamp is a fixed layer and type sizes are set with clamp. Title, description, Open Graph and a small JSON-LD block. Every reveal is CSS and IntersectionObserver; the page is complete and readable with JavaScript off. Headings in order, landmarks, visible focus in amber, 44 px targets on the rows, contrast at AA on every pairing (parchment on #15110F is about 14:1, secondary about 8:1).

## What this refuses

No video, no particles, no pinned scroll scenes, no horizontal panels, no counters, no testimonials, no feature grid, no screenshots in device frames, no gradient but the one lamp. Each of those would be louder than the person it is for.
