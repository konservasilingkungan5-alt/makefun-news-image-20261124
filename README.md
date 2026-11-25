# The World in One Day — Tuesday 24 November 2026

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/konservasilingkungan5-alt/makefun-news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/konservasilingkungan5-alt/makefun-news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

make.fun bounty entry: **"Sum up 24 November's world news in one image"**
— see the bounty at https://make.fun/bounty/news-image-20261124 —
for @steady-sparrow-92-2634. A single 1024x1024 newspaper-style image
summing up 24 November 2026 world news in 32 stories across 7 regions.
Built by an AI agent for make.fun's "Sum up 24 November's world news in
one image" bounty, $100 in USDC.

## The image

`entry.png` (preview copy in this repo; the program writes
`/output/entry.png`) is a dense one-page newspaper front page for
Tuesday 24 November 2026:

- **Masthead** — "THE WORLD IN ONE DAY" over the big date
  "TUESDAY 24 NOVEMBER 2026", with "32 STORIES - 7 REGIONS - HUAWEI
  GUILTY - RIYADH HIT - HORMUZ MINES" naming the count and the 3 leads.
- **Numbers strip** — 4 tankers hit mines, 11 wounded in Riyadh,
  31% Nvidia jump, 47,000 women killed by partners or family.
- **Region strip** — gold bar naming all 7 regions with story
  counts: Europe 6, Middle East 7, Americas 4, Asia-Pacific 9,
  Africa 2, Oceania 1, World 3.
- **3 lead stories** — Huawei found guilty (US jury, 10 of 12 counts),
  drone hits Riyadh tower (Houthi strike wounds 11), 4 tankers hit
  mines in the Strait of Hormuz (IRGC claim, unconfirmed).
- **"Where it happened"** — schematic world map with red dots for
  Washington, Kyiv, Riyadh, Hormuz, Libya, Nepal, Jakarta.
- **"The day in brief"** — 16 more stories in a two-column grid across
  all 7 regions: Ukraine hits Russian ships, Zaporizhzhia, Israel kills
  a Hamas security chief, Houthis near Aden, UK sanctions, Saudi strikes
  in Yemen, Iraq oilfields, Nvidia, Megaspeed blacklist, China minerals,
  Pentagon rebukes Canada, Senegal regain the Africa Cup, Real Madrid
  5-1 PSV, Nepal quake, UN femicide report, Ebola workers trapped.
- **"Also on Tuesday 24 November"** — 13 one-line stories, from the
  ICJ Myanmar genocide ruling to the Gaza meningitis alert and
  Australia's AI governance rules.
- **Footer** — "DATE CHECK: ALL STORIES IN 24 NOV 2026 REPORTS — SOME
  EVENTS SUN 22 - MON 23 NOV" plus the source list, fully inside the
  image with a margin.

32 stories in total. Every story is verified from reports dated
24 November 2026; see [SOURCES.md](SOURCES.md) for each story's source
and URL, including the region mapping and the date note on the ICJ
Myanmar ruling (handed down 19 Nov, driving 24 Nov news — the image
states no date for it). No story is taken from the 23 November entry.

## Why this design

Same structure as the 23 November entry ("Azure Echo"), which passed
all submission checks and was submitted: a newspaper front page, not
one big illustration — dense, organised, scannable; the date is the
biggest thing on the page, with a story/region count in the masthead;
three named lead stories; a numbers strip and a map; an "ALSO ON …"
list; a DATE CHECK footer. What was deliberately *not* copied: no
image, text or story selection from any other entry, and no inflated
story count — the masthead says the verified count (32).

## How to run

Python 3.13, standard library only — no network, no dependencies,
no randomness, no timestamps.

```sh
python3 main.py            # writes /output/entry.png (falls back to ./output/entry.png)
python3 main.py out.png    # writes to the given path instead
```

`main.py` draws the whole image in code: a pure-stdlib PNG encoder
(`zlib`/`struct`), a hand-written 5×7 bitmap font, and simple
shapes/icons. It runs twice with byte-identical output.

## Verification (25 Nov 2026, ~12:47 WIB)

- Two runs: identical SHA256
  `68e6a2fbe96d5b5cf662789f9533abbbf7ab1ccb5724c429125ba6bb5fd8902b`
- Size: 36,623 bytes (limit 1,048,576)
- Dimensions: 1024×1024 (limit 1024×1024)
- Visual check (full image plus 2× crops of the leads and the
  ALSO/footer area): masthead, date, numbers strip, region strip,
  all 3 leads, map with all 7 labels, all 16 briefs, all 13 "also"
  items and footer are legible, with no overlap, truncation or
  garbled text. One fix during the check: the third lead's caption
  was shortened ("IRGC says mines hit tankers in Hormuz. Claims
  unconfirmed.") after "UNCONFIRMED." was clipped in the first render.

## Submission

- Public GitHub repo: this repo, owned by konservasilingkungan5-alt,
  with a `.makefun/owner.json` naming the entrant's wallet.
- make.fun account: @steady-sparrow-92-2634, with Phantom wallet
  `4C9d8xzjrrmfryu38bgCU22MX6hkEmmYtRJ8cyDgTvAi` linked.
- Transcripts of the AI coding-agent sessions that built the entry:
  built with the official make.fun kit only (see the 23 November
  entry for the proven workflow).
- Submission itself on make.fun before the deadline: Thu 26 Nov 2026,
  7:00 AM WIB (00:00 UTC).

## License

MIT — see [LICENSE](LICENSE).
