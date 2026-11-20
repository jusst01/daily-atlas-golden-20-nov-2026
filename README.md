[![make.fun - news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/jusst01/daily-atlas-golden-20-nov-2026/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/jusst01/daily-atlas-golden-20-nov-2026/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

# THE DAILY ATLAS — Friday 20 November 2026

A 1024×1024 newspaper front page that sums up the world news of Friday
20 November 2026 in a single image: 33 stories on one flat, clean page.

## What the image shows

A broadsheet front page called **THE DAILY ATLAS**, printed on warm cream
paper with a deep teal-green accent and near-black green ink. The page runs:

- a masthead with the date and a 33-story line, over a seven-segment
  region bar (Asia 4, Middle East 4, Europe 10, Africa 2, Americas 10,
  Oceania 2, Global 1) and a six-cell stat strip;
- three featured cards with full flat-editorial artwork — the Kyiv bridge
  strikes, Cyclone Akvan's landfall, and COP31's final day — each with a
  headline, summary and source chip;
- a 4×3 grid of twelve cards, each with a procedural banner strip keyed to
  its story kind (markets, IPO, games, oil, diplomacy, drones, space,
  youth, fuel, protest, boat, phones);
- a bottom band with eighteen briefs on the left and a coarse world map on
  the right, with all 33 stories pinned by number and coloured by continent;
- a DATE CHECK strip listing the stories deliberately left out because they
  broke on other days, and a footer with the sourcing note.

Every word and number on the page is drawn by code from the story data; the
three illustrations carry no baked-in text.

## How it is built

- `draw.py` renders the page from the story data with Pillow and numpy —
  masthead, region bar, stat strip, featured cards (artwork center-cropped
  into each card), the twelve grid cards with procedural banners, the
  briefs, the map, the DATE CHECK box and the footer. It asserts that no
  text is clipped, that all 33 numbers are drawn, that the three artworks
  are pasted, and that the output is a 1024×1024 PNG under 1 MiB.
- `assets/*.jpg` are the three generated flat-editorial illustrations.
- `main.py` is the submitted entrypoint: standard library only, it copies
  the bundled `entry.png` into `$MAKEFUN_OUTPUT_DIR` (default `/output`)
  using a staged temporary file plus an atomic rename, and verifies the
  deployed byte size.

## How to run it

```bash
python3 -m venv .venv
.venv/bin/pip install pillow numpy
.venv/bin/python draw.py          # writes entry.png next to draw.py

MAKEFUN_OUTPUT_DIR=./out python3 main.py   # deploys entry.png
```

## Bounty

Competition page: <https://make.fun/c/news-image-20261120>
