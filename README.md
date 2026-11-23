[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/Kikuk00/makefun-news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/Kikuk00/makefun-news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

# The World Today: 22 November 2026

A newspaper-style front-page infographic summing up Sunday 22 November
2026 in one image. The date is printed big at the top, and six stories from
around the world each get their own panel with a drawn illustration, a
headline, and one short factual line.

## The six stories

1. **COP31 collapses** — The UN climate summit in Antalya ended on Sunday
   with no agreement, two days into overtime, after the EU and allies
   rejected a final text with no mention of fossil fuels.
2. **Iran strikes Bahrain** — Bahrain says an Iranian strike hit a civilian
   site, wounding two people, one critically.
3. **Drone hits flats near Kyiv** — A Russian drone hit a five-storey block
   in Dymer, near Kyiv. 14 people are missing.
4. **Warship hit at Benghazi** — Libya says a Russian corvette at Benghazi
   was hit by a suspected Ukrainian sea drone.
5. **Democrats win biggest House majority since 1992** — Chuck Hubbard beat
   Virginia Foxx in North Carolina after a recount, giving Democrats at
   least 258 House seats.
6. **BepiColombo enters orbit around Mercury** — The European-Japanese
   BepiColombo probe entered orbit around Mercury on Sunday, after a
   seven-year journey.

## How it is built

`gen.py` draws `entry.png` (1024x1024) from scratch with the Python
standard library only — a hand-written 5x7 bitmap font, flat vector
shapes, and a small PNG encoder. No external assets, no network, no
third-party packages. `main.py` copies `entry.png` to the output
directory, so both grader runs write byte-identical files.

Regenerate the image with:

```sh
python3 gen.py
```

Then test the entrypoint with:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```
