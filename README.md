# THE WORLD, SUNDAY 22 NOVEMBER 2026

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/verren044/makefun-news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/verren044/makefun-news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)



One image that sums up the world's news of Sunday 22 November 2026: a dense
newspaper front page, drawn entirely in code (Python 3.13 standard library
only, deterministic, no network). Run `main.py` and it writes
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output/entry.png`), 1024x1024,
under 1 MiB.

## The image (52 stories)

- **Masthead** — "THE WORLD" with the dateline "SUNDAY 22 NOVEMBER 2026".
- **UTC timeline strip** — the day in UTC (00/06/12/18/24 ticks) with five
  timed moments: the FBI hack report (~00 UTC), the COP31 deal text
  (~03 UTC), Rutte in Warsaw (~06 UTC), the Mexico raid report (~09 UTC),
  the Hormuz reopening plan (~12 UTC).
- **Thirteen illustrated anchor cards**, each a small drawn picture strip
  with a kicker, a headline and a caption:
  1. **RUTTE VOWS: EVERY INCH** — NATO's Rutte in Warsaw: the alliance
     will defend every inch of Polish territory, after prosecutors confirm
     a Russian Kh-101 cruise missile landed in Poland. Flag, streaks,
     impact burst.
  2. **DRONES HIT SPARTA II** — two drones set the Russian military-linked
     cargo ship Sparta II ablaze in the Gulf of Finland; it drifts into
     Finnish waters. Night sea, burning ship, drones.
  3. **COP31: DEAL AT LAST?** — after two days of overtime, a new draft
     deal text is put to delegations, with objections due by 03:00 GMT and
     an approval session at 06:00 GMT. Globe, clock, flags.
  4. **EL CHAPO ISIDRO CAUGHT** — Mexican forces capture FBI Ten Most
     Wanted fugitive Fausto Isidro Meza Flores in Guasave, Sinaloa; 11
     dead in the raid. Helicopter searchlight, burning roadblock.
  5. **FBI PROBES DATABASE HACK** — the FBI investigates an apparent hack
     of its National Crime Information Center database. Server racks, red
     "BREACH?" banner.
  6. **NVIDIA SINKS 14 PC** — Nvidia falls about 14% on Friday, its
     seventh straight daily decline, after reports the SEC is examining
     potential accounting issues. Falling red bars.
  7. **NO DEAL WITHOUT PAPER** — Washington wants a Ukraine deal by early
     January, but Zelensky says Kyiv has seen no written guarantees yet.
     Flag bands, document, pen.
  8. **KRYVYI RIH TOLL RISES** — the toll from the Kryvyi Rih double-tap
     rises to 2 dead, including a child, and 58 injured. Night city, two
     blasts.
  9. **RIEMANN PROOF CLAIMED** — mathematician Levent Alpöge claims a
     proof of the Riemann hypothesis, built with Claude. Chalk zeta curve,
     critical line.
  10. **BOAT CAPSIZES, 24 DEAD** — a boat carrying passengers to a funeral
      capsizes in Nigeria; at least 24 dead. River, capsized hull, life
      ring.
  11. **FACTORY FIRE: 39 MISSING** — a fire at a candy factory in
      Indonesia leaves 3 dead and 39 missing. Factory silhouette, flames,
      smoke.
  12. **PAKISTAN TAKE SERIES 1-0** — Pakistan beat Sri Lanka by 8 wickets
      to take the Test series 1-0. Pitch, stumps, ball.
  13. **ZVEREV V ALCARAZ FINAL** — Zverev beats Medvedev 7-6(0), 6-4 and
      Alcaraz beats Shelton 3-6, 6-3, 7-6(1); the Turin final is today.
      Court, ball, "7-6 6-4".
- **THE WORLD MAP** — rough continents on a blue ocean with seven numbered
  red markers: 1 Poland, 2 Gulf of Finland, 3 Antalya, 4 Mexico,
  5 Kryvyi Rih, 6 Nigeria, 7 Turin (key in the index panel).
- **BY REGION index** — story counts per region: Middle East 5, Europe
  21, Asia-Pacific 12, Americas 5, Africa 4, Markets + Tech 5.
- **THE DAY IN BRIEF — 39 MORE STORIES** — 39 short briefs (headline +
  one-line caption) in three columns, from Iran's rolling blackouts to
  the Democrats reclaiming Congress, Norway voiding oil licences and the
  Leeds 4-1 shock over Chelsea.
- **Footer** — "52 STORIES, ONE DAY": 13 anchors + 39 briefs = 52 stories.

## Masthead side boxes

- **BY THE NUMBERS** (left of the masthead) — five figures of the day:
  Nvidia -14%, S+P 500 -3.7%, Bitcoin under $60K, COP31 power 35% by
  2035, ATP final Zverev-Alcaraz. Falling figures carry a small red
  down-triangle.
- **IN THEIR WORDS** (right of the masthead) — three quotes of the day:
  Rutte on Poland ("defend every inch of Polish territory"), Streeting
  on the strikes ("outrageous provocation"), Kurum on the COP31 deal
  ("a text all parties can agree on"); each quote has a red bar at its
  left.

## How it is built

`main.py` holds a hand-drawn 5x7 bitmap font (uppercase A-Z, 0-9, punctuation),
a pixel buffer with rect/ellipse/polygon/line primitives, and a pure-stdlib
PNG encoder (zlib + struct + CRC32). Every string is uppercased before
drawing. Two runs produce byte-identical output.

## Validation

- Two runs, identical sha256: `a99c4d2f7a2705589e9360d6ee1ad38ece20c386f962c7a2ffe9e563e23502a4`
- Size: 39,787 bytes (limit 1 MiB), 1024x1024, all PNG chunk CRCs valid
- Region spot-checks passed (numbers/quotes frames, timeline line, map
  ocean and marker centres, no ink past the page margins, no ink above the
  masthead rule)
- Visually checked at full size: no garbled or overlapping text, no scene
  spilling outside its panel; all 13 anchor headlines legible, map markers
  distinct, briefs readable

Built for the make.fun bounty — [enter via my referral link](https://make.fun/r/k7cmczfx).
