# THE WORLD — Sunday 22 November 2026

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/verren044/makefun-news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/verren044/makefun-news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A newspaper front page that sums up the world's news of Sunday
22 November 2026 in a single image: **52 stories** — 13 anchor stories
with small drawn scenes, a world map with seven numbered story sites,
a UTC timeline of the day, a by-region index, and 39 briefs.

## What is on the page

- **Masthead:** THE WORLD, Sunday 22 November 2026, flanked by
  "By the Numbers" (Nvidia −14%, S+P 500 −3.7%, Bitcoin under $60K,
  the COP31 power target, the ATP final) and "In Their Words"
  (Rutte, Streeting, Kurum).
- **Timeline (UTC):** 00 FBI hack · 03 COP31 deal · 06 Rutte in Warsaw ·
  09 Mexico raid · 12 Hormuz.
- **Map:** seven numbered sites — Rzeszow (Poland), Gulf of Finland,
  Antalya, Guasave (Mexico), Kryvyi Rih, Nigeria, Turin.
- **Anchors:** Rutte's Warsaw vow, the Sparta II drone strike, COP31,
  the El Chapo Isidro raid, the FBI database breach, Nvidia's slide,
  Kyiv's "no deal without paper", Kryvyi Rih, the Riemann proof claim,
  the Nigeria boat capsize, the Indonesia factory fire, Pakistan's
  series win, and the Zverev–Alcaraz final.
- **In brief:** 39 more stories from the Middle East, Europe, tech and
  markets, Asia, the Americas, Africa and sport.

## How it is built

`main.py` (Python 3.13, standard library only) draws every pixel
itself: a small `Sheet` class for the pixel buffer, a hand-made 5x7
bitmap alphabet, thirteen little scene drawings, a rough world map
from longitude/latitude outlines, and the page layout. No network,
no randomness, no files read — run it twice and the two PNGs are
byte-identical.

## Run it

```sh
python3 main.py
```

It writes `entry.png` to the directory named by `MAKEFUN_OUTPUT_DIR`
(or to `/output/entry.png` by default). The image is 1024x1024 and
under 1 MiB.

## Entry

- Competition: `news-image-20261122` — "Sum up 22 November's world
  news in one image" ($100 USDC).
- Bounty: https://make.fun/bounty/news-image-20261122
- Referral code: `k7cmczfx`
- Repository: https://github.com/verren044/makefun-news-image-20261122
- License: MIT (see `LICENSE`).
