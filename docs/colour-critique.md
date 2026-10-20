# Colour critique, 19 October 2026

A Sonnet creative director reviewed the live site and app after Matthew's reaction to the first redesign: "I think it's still below par." Critique only; the two directions below are proposals, not decisions.

## Diagnosis

The palette is one hue, a brown-orange, doing every job: ground, surface, lamp pool, text, secondary text and the accent all sit at roughly 25 to 35 degrees of hue, so nothing in the frame is a colour contrast, only a brightness one. The lamp is a brown smudge because its core (#3A2D22 at 18% alpha) is a darker version of the ground rather than a hotter colour, and a lamp must be the brightest, most saturated thing in the room before it falls off. Sage and rose are pastel, mid-saturation and near-equal in value (both about L 65 to 70), so they read as two quiet beiges beside the cream text and never as signals. Ground to surface to pool is a gap of only 4 to 6 lightness points, so the whole product lives in a narrow brown band with no deep black and no hot peak.

## Value structure (approximate L*)

Text #F3E9DA about 93. Secondary #BFAE98 about 72. Amber #F2A33A about 74. Sage #7FB0A3 about 69. Rose #D98C7A about 65. Then a gap of about 35 points down to the pool #3A2D22 at about 20, surface #2B2420 at about 16, app ground #1F1A17 at about 10, site ground #15110F at about 6. Secondary, amber, sage and rose pile up within 10 points, so the accents do not separate. Pool, surface and ground pile up within 14 points, so panels and glow barely register. Nothing sits between 75 and 93 except text, so there is no highlight tier and the lamp has no hot core.

## Direction A: Ink and ember (recommended)

- Site ground #0B1020, app ground #111730, surface #161D38, hairline rgba(244,235,221,.12).
- Lamp core #FFC15E, mid #D9622B, cool shadow edge #1B2A5C.
- Text #F4EBDD, secondary #A9B2CC (cool, so it recedes into the blue instead of fighting the amber).
- Next action: ember amber #FFB84D.
- What happened and the setup: teal #6FD3C0.
- What was concluded and the other person: orchid rose #F08FAE, pinker than today's salmon so it separates from amber by hue.
- Signature: the ember #D9622B, only inside the lamp falloff and on the focus ring, never as text.

Why it wins: blue-black and amber are true complements, so the one warm thing in a cold room genuinely glows, which is the "lamp left on" idea made literal. Blue-black is calm and slow for a stressed user; oxblood is heavier and edges toward alarm. The accents become teal, amber and orchid, a triad spread around the wheel rather than three pastels near each other.

## Direction B: Oxblood and brass

- Site ground #1A0A0E, app ground #221014, surface #2A1217.
- Lamp core #FFC46B, mid #8A3A1E, edge #3A0F18.
- Text #F6EADB, secondary #BFA79B.
- Next action: brass #F2B04C. What happened: verdigris #62C4B0. Concluded and the other person: coral #F2937F.

Richer and more luxurious, but red on red: the rose role is hard to separate from a red ground, and in a hard-moment product a red room risks reading as warning. The fallback if warmth matters more than calm.

## Light

Build the lamp as three stacked radial gradients, not one. Core: a small hot ellipse, about 18rem by 10rem, centred at 50% and -4rem so it reads as a source, #FFC15E at .55 alpha fading out. Mid: about 40rem by 26rem, same centre, #D9622B at .22 alpha to transparent at 70%. Wash: a wide 90rem by 55rem ellipse in the cool shadow #1B2A5C at .45 alpha, centred slightly lower, so the room around the light is blue and the light is orange; that contrast is what makes it read as light on a wall. A faint floor bounce, a 30rem warm ellipse at 50% 100% at .06 alpha, so the bottom of the page is not dead. On scroll, shift temperature as well as size: a tight ember at arrival, and by the start the wash widens and the core eases toward #FFD58A, so the room warms and opens as the question arrives. Switch-on animates opacity and core size together over 1600 ms, the core leading by about 300 ms.

## Paper variant

Keep it as a daylight and accessibility option, not a brand moment, with no lamp. Ground #F4EEE3, ink #1B2036, secondary #4A506B, amber #9A4F0C, teal #1F6F63, orchid #A23B5E, surface #EAE2D3. Same hue relationships by day.

## Contrast (AA: 4.5 body, 3 large and marks)

Ink and ember on #161D38 surface and #0B1020 site ground: text 14.0 and 16.0; secondary 7.8 and 8.9; ember amber 9.6 and 11.0; teal 9.3 and 10.6; orchid 7.3 and 8.3. Oxblood and brass on #2A1217: text 14.8, secondary 7.7, brass 9.3, verdigris 8.4, coral 7.7. Paper: ink 13.9, secondary 6.9, amber 5.2, teal 5.2, orchid 5.5. All pass.

## First ten variable changes, in order

1. Ground: #0B1020 site, #111730 app.
2. Amber to #FFB84D.
3. Lamp core #FFC15E at high alpha in place of #3A2D22.
4. Mid colour rgba(217,98,43,.22).
5. Add the cool shadow #1B2A5C as the wide wash layer. Re-screenshot at 390 here before going on.
6. Sage to teal #6FD3C0.
7. Rose to orchid #F08FAE.
8. Secondary to #A9B2CC, text to #F4EBDD.
9. App surface #161D38, hairline rgba(244,235,221,.12).
10. Paper variant as above.
