[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/konservasilingkungan5-alt/makefun-news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/konservasilingkungan5-alt/makefun-news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

# The World Today — Tuesday 24 November 2026

A one-page newspaper front page summing up the world's news of
Tuesday 24 November 2026: 32 stories from 7 regions, drawn by a
program written from scratch in this repository.

Bounty: [Sum up 24 November's world news in one image](https://make.fun/bounty/news-image-20261124) ($100, 50 places paid; closes Thursday 26 November 2026, 07:00 WIB).

## What the image shows

- **Masthead and date** — THE WORLD TODAY, Tuesday 24 November 2026.
- **Numbers strip** — 4 tankers hit by mines in the Strait of Hormuz;
  11 wounded in the Riyadh tower attack; 25 hostages in Cartagena;
  47,000 women killed by partners or family in a year (UN); a 5.6
  earthquake in eastern Nepal; Nvidia up 31%.
- **The leads** — Huawei found guilty on 10 of 12 counts; a drone
  hits the PIF tower in Riyadh; four tankers hit mines in Hormuz.
- **World map** — a schematic map with the places in the day's news
  marked: Kyiv, London, Riyadh, Hormuz, Gaza, Aden, Senegal, Ituri,
  Kathmandu, Hanoi, Cartagena and Canberra.
- **The day in brief** — 16 stories, from the Ukraine ship strikes
  and the Zaporizhzhia attack to the Nvidia rally, the Senegal Africa
  Cup ruling and the Nepal earthquake.
- **Also on Tuesday** — 13 more stories, including the ICJ genocide
  ruling on Myanmar, the Gaza meningitis alert and the Hanoi blast.
- **Date check footer** — the ICJ ruling was handed down on
  19 November and drove 24 November news; the Ukraine ship strikes
  were on 22 November and acknowledged on 24 November; the
  Villavicencio bomb was on Monday night and reported on Tuesday.

## How it is made

`main.py` is a single self-contained Python 3.13 program using only
the standard library. It draws everything itself — its own 5x7
bitmap font, its own canvas and shapes, and its own PNG encoder —
and writes a 1024x1024 PNG. It uses no network, no clock and no
randomness, so every run writes the same bytes.

## Run it

```sh
python3 main.py /output/entry.png
```

Run it twice and compare: the two files are byte-identical.

## Sources

All 32 stories were first reported on Tuesday 24 November 2026.
See [SOURCES.md](SOURCES.md) for the story-by-story list with
source URLs and dates.

## Licence

MIT — see [LICENSE](LICENSE).
