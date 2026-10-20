# Site build log, 19 October 2026

Each stage below is the implementation prompt that drove it, in the order it ran, with what was verified. The concept it builds is `docs/site-concept.md`. Nothing here has been pushed or deployed.

## 1. Concept

Prompt: "Write the site as a scene, not a page: the narrative from the first second to the call to action, art direction, type at a cinematic scale, light as the structural idea, motion with exact durations, the section map with each section's message, layout, interaction, transition and scroll behaviour, and the conversion goal. Keep to the app's palette and fonts."

Result: `docs/site-concept.md`. Verified by reading against the owner's instructions 1 and 2: every named element (visual narrative, art direction, typography, palette, composition, materials, lighting, atmosphere, depth, motion language, emotional experience; sections from load to CTA with conversion goal) has a paragraph.

## 2. Setup and architecture

Prompt: "Add the site at site/index.html with css/site.css and js/site.js. Vanilla, no libraries, no npm. The site is served at / and the app moves to /app/. Keep every other route."

Result: `server/app.py` maps `/` to `site/index.html` and `/app`, `/app/` to the app's `index.html`; the app's asset links became absolute so it works under `/app/`. Verified: `curl` on `/`, `/app/`, `/app/?who=manager`, `/css/site.css`, `/js/site.js`, `/tests/run.html` all return 200; `server/test_app.py` updated and passing (13 tests).

## 3. The scene and its sections

Prompt: "Build the eight sections: arrival with the lamp switching on; three named lines; the invented account that takes its colours and sorts into happened, told and concluded; two readings; what it won't do; what you leave with; where words go; the start, which is the app's first question with the five answers as links into the app with the answer preselected."

Result: `site/index.html` and `css/site.css`. Each section is at least 92% of the viewport; type scale 44 to 96 px for the big line, 30 to 56 px for section lines, DM Sans 18 to 20 px body. Verified in the browser pane at desktop width: arrival, named, sort, two readings, won't do, leave with, words, start. The app accepts `?who=` and opens on the second tap (`js/app.js`, `home()`).

## 4. Motion and light

Prompt: "Lamp switches on at load over 1600 ms. Lines arrive on IntersectionObserver with 600 ms and 90 ms stagger. The account's sentences take their underline colours 160 ms apart, then the blocks fade in. Scroll drives one CSS variable that grows the lamp from dim at arrival to full at the start. Reduced motion: everything visible, lamp at mid."

Result: `js/site.js` (one script, 1.8 KB) and the `--progress` variable in `css/site.css`. Verified: the pool grows as the page scrolls (screenshots of the start section show the room lit); no console errors; the page is complete with JavaScript off because reveals only hide when `html.js` is present.

## 5. Responsive, accessibility, SEO, performance

Verified: 390 px and 1440 px headless screenshots in `qa/out/`; the header no longer overlaps content on scroll (it was fixed, now absolute); headings in order (one h1, h2 per section), landmarks, skip link, 60 px rows as links with visible amber focus; contrast parchment on #15110F about 14:1, secondary about 8:1. Title, description, canonical, Open Graph and JSON-LD present. HTML, CSS and JS together are 16 KB; with the two Google font families the page stays well under the 300 KB budget. No images.

## 6. What was not verified

Real device testing, a screen reader pass, and the fonts' exact transferred size on a cold cache. The canonical URL is the Railway domain, teamwork-production-team.up.railway.app, live since 19 October 2026.

## What is cinematic about it, and what it refuses

Cinematic: one light source whose intensity is the story; type at a scale that fills the frame; one idea per viewport; a single reveal (the account sorting itself); an ending where the room is lit and the question waits. Refused: video, particles, pinned scroll scenes, horizontal motion, counters, testimonials, feature grids, device mockups, any gradient but the lamp. Each would be louder than the person it is for.
