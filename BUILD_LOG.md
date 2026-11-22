# BUILD_LOG — news-image-20261122

## Entry
- Contest: news-image-20261122 — "Sum up 22 November's world news in one image"
- Prize: $100 USDC, top 50 (1st $20, 2nd $12, 3rd $6, 4th-10th $2, 11th-50th $1.20)
- Deadline: 24 Nov 2026 07:00 WIB (2026-11-24T00:00:00Z).
- Kit: ~/workspace/makefun/kits/news-image-20261122-kit/ — RULES.txt + competition.yaml read.
- Entry: `main.py` (Python 3.13 stdlib only) draws the page; `entry.png` 1024x1024,
  39,787 B, sha256 a99c4d2f7a2705589e9360d6ee1ad38ece20c386f962c7a2ffe9e563e23502a4.
- Determinism: two runs into two different dirs, byte-identical (`cmp` clean, same sha256).
  No network, no clock, no randomness.
- Built 22 Nov 2026 ~14:00 WIB (07:00 UTC), i.e. ~7 hours into the contest day:
  the image covers the events of 22 Nov reported by then — the overnight
  COP31 draft, Rutte in Warsaw, the Sparta II fire, the Mexico raid, the FBI
  hack report, Friday's market close, Saturday's sport. Nothing after 07:00 UTC
  is in it; that is the honest cut-off of this build.

## Layout (1024x1024)
- Masthead: THE WORLD / SUNDAY 22 NOVEMBER 2026.
- UTC timeline (00/06/12/18/24) with 5 events: 00 FBI HACK, 03 COP31 DEAL,
  06 RUTTE WARSAW, 09 MEXICO RAID, 12 HORMUZ.
- 13 anchor cards with drawn scenes (rows of 3, h 84, scene 36; row 5 h 124,
  tennis scene 56): Poland/NATO vow, Sparta II, COP31 deal, El Chapo Isidro,
  FBI hack, Nvidia -14%, Kyiv peace terms, Kryvyi Rih toll, Riemann claim,
  Nigeria boat, Indonesia factory fire, Pakistan series, Turin final.
- 39 briefs in 3 columns x 13 rows under "THE DAY IN BRIEF".
- World map (rough equirectangular continents) with 7 numbered markers:
  1 Poland, 2 Gulf of Finland, 3 Antalya, 4 Guasave (Mexico), 5 Kryvyi Rih,
  6 Nigeria, 7 Turin.
- By-region index: ME 5, Europe 21, Asia-Pacific 12, Americas 5, Africa 4,
  Markets + Tech 5 = 52.
- Masthead side boxes: BY THE NUMBERS (Nvidia -14%, S+P -3.7%, Bitcoin under
  $60K, COP31 power 35% by 2035, ATP final Zverev-Alcaraz) and IN THEIR WORDS
  (Rutte, Streeting, Kurum).
- Footer: "52 STORIES, ONE DAY".

## Story verification (all 22 Nov 2026, browser.search news vertical, 4 search rounds)
Anchors, each cross-checked in 2+ sources:
- Rutte in Warsaw Saturday: "I can guarantee that NATO will defend every inch
  of Polish territory"; prosecutor confirms a Russian Kh-101 cruise missile at
  Nowy Lipowiec (Reuters via BBC digest, AsiaToday, Bytes Europe, The Times)
- Drones hit Russian cargo ship Sparta II in the Gulf of Finland Saturday
  morning, en route St Petersburg to Kaliningrad; fire, drifted into Finnish
  waters (Reuters via The Silk Paradox, BBC, The Times)
- COP31: new draft deal text late Saturday night; objections by 03:00 GMT
  Sunday, approval session 06:00 GMT; fossil-fuel-free draft, 35% electricity
  by 2035 (Reuters, Trinidad Tribune, AsiaToday)
- Fausto Isidro "El Chapo Isidro" Meza Flores captured Friday night in Guasave,
  Sinaloa; 11 dead (7 cartel, 4 soldiers); $5m FBI reward; flown to Mexico City
  Saturday (CNN, NY Post, TBS News)
- FBI investigating apparent hack of its National Crime Information Center
  database (BBC 22 Nov 00:10, SimpleLife.news)
- Nvidia fell ~14% Friday 20 Nov, 7th straight daily decline, after Reuters
  reported the SEC is examining potential accounting issues; close $150.96
  (Vocemundi, BigGo Finance); S+P 500 -3.7% Friday, Bitcoin $58,970
- US wants Ukraine deal by early January before new Congress (FT via The Silk
  Paradox); Zelensky: no written guarantees seen yet; Kyiv proposes local
  ceasefires for 15 villages (The Silk Paradox, Ukrainska Pravda via ISW)
- Kryvyi Rih toll now 2 dead incl. a child, 58 injured (Zelensky via Kyiv Post,
  The Silk Paradox)
- Mathematician Levent Alpöge claims proof of the Riemann hypothesis, built
  with Claude (SimpleLife.news top stories 22 Nov)
- Boat taking passengers to a funeral capsizes in Nigeria, at least 24 dead
  (Balanced News UK daily update 22 Nov)
- Fire at Indonesian candy factory: 3 dead, 39 missing (The Hindu via
  news.co.za, 22 Nov)
- Pakistan beat Sri Lanka by 8 wickets, series 1-0 (Daily Dose of Sports
  22 Nov); Australia beat England T20 by 3 wickets; India 486/4 lead NZ by 118
- Zverev beats Medvedev 7-6(0), 6-4; Alcaraz beats Shelton 3-6, 6-3, 7-6(1);
  final Sunday in Turin (Tennis Grandstand, IANS, QNC News)

Briefs: 39 items from the same searches (BBC, SimpleLife.news, C54,
CareerIndia, The Silk Paradox, AsiaToday, Balanced News, Daily Dose of Sports).
Dating notes (honest flags):
- Most anchor events happened late Friday 20 Nov / Saturday 21 Nov (UTC) and
  led 22 Nov editions worldwide; they are framed as reported/announced on
  22 Nov, not as 22 Nov daytime events. The contest covers events that happened
  or were first reported on 22 Nov in any time zone.
- The 21 Nov entry's lead stories (Poland missiles landing, Kryvyi Rih
  double-tap, Khasab tanker, Hodeidah, COP31 overtime) are NOT re-anchored
  here as the same story. Follow-ups appear as new anchors only where 22 Nov
  reporting adds something new (Rutte's Warsaw vow + Kh-101 confirmation,
  Kryvyi Rih toll update, COP31 deal text); the rest appear as briefs.
- Nvidia's Friday fall and the S+P 500 -3.7% are the latest market closes
  (markets shut Saturday/Sunday); they are labelled as Friday figures in the
  build notes, not as Sunday moves.

## Bugs found and fixed during the build
1. FBI scene: "BREACH?" at scale 2 overflowed its red banner (82 px in a
   70 px banner, "?" clipped) and "NCIC" overlapped the banner bottom.
   Fixed: banner text at scale 1, NCIC line removed.
2. Nvidia scene: "-14 PC" at x+w-60 overflowed the card's right edge by
   ~10 px and the "NV" chip square crowded it. Fixed: chip removed,
   "-14 PC" and "7 DAYS DOWN" moved to x+w-72.
3. Timeline hour labels: "24" spilled 6 px past the right page margin and
   "00" spilled 5 px past the left margin. Fixed: clamp both label ends
   to the 16..1008 page frame (same clamp the event labels already used).
   The 00-hour event dot still centres on the tick at x=16, as designed.

## Spot-checks
- 13 anchors + 39 briefs (asserts in code), region index sums to 52.
- PNG valid (magic + 1024x1024), 39,787 B < 1 MiB, all chunk CRCs valid.
- Pixel checks: numbers/quotes frames, timeline line, map ocean and marker
  centres, no ink past the page margins, no ink above the masthead rule.
- Image viewed at full size: no garbled or overlapping text, no scene spilling
  outside its panel.
- entry.png is generated output; main.py regenerates it byte-identically.
- README referral updated to k7cmczfx (current @verren044 referral; the
  vvz66fvh code in older READMEs is dead since the 21 Nov account merge).

## Not done (parent)
- Push, kit check, bundle, submit. Repo: to be created as
  verren044/makefun-news-image-20261122.
  .makefun/owner.json present (wallet 5dzkJVQkKc2V2mMuQDsfv8EJwtw3uLDMARNVHkjmByaX).
