# Build log — news-image-20261122

## What was built

A fresh implementation of the entry, written from the prose rebuild
spec in this session. `main.py` (792 lines, Python 3.13, standard
library only) draws a 1024x1024 newspaper front page, "THE WORLD",
Sunday 22 November 2026, with 52 stories: 13 anchor cards with drawn
scenes, a world map with 7 numbered sites, a UTC timeline, a by-region
index, and 39 briefs. Everything is drawn in code — a `Sheet` pixel
buffer, a hand-made 5x7 bitmap alphabet, thirteen scene functions,
and continent outlines from longitude/latitude points. No network,
no randomness, no files read at run time.

## Checks run

- `python3 main.py` twice with `MAKEFUN_OUTPUT_DIR` set to a scratch
  directory: both runs wrote byte-identical PNGs (`cmp` clean).
- PNG validated by hand: correct signature, every chunk CRC checks
  out, IHDR says 1024x1024.
- The finished `entry.png` was read back at full size and checked
  visually: masthead, side boxes, timeline, map, all 13 headlines,
  and all 39 briefs are legible, with no text running outside its
  box. One spelling note: the spec wrote "Streeteing" for the quote
  attribution; the entry uses the correct "STREETING".
- `entry.png` was regenerated into the entry directory by running
  `main.py` there, so the shipped image is exactly what the program
  writes.

## Outputs

- `entry.png`: 39,477 bytes,
  sha256 `98634ea3fc14854af9195e2360928bfe73ccfe8a2ee51c6db6bc7acf89407ed9`
- `main.py`: 792 lines
- Determinism: two runs byte-identical, same sha256 both times
- Limits: 1024x1024, 39,477 bytes (limit 1,048,576) — inside the caps

## Notes

- The previous implementation in this directory was replaced wholesale
  by this rebuild; the old files were never read or copied during it.
- `.makefun/owner.json`, `LICENSE`, and `.git` were left untouched.
- No submit, push, or bundle was run from this session; those steps
  belong to the parent agent.
