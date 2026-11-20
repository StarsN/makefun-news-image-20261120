# news-image-20261120 — One Image, One Day
[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/StarsN/makefun-news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/StarsN/makefun-news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

[make.fun bounty: Sum up 20 November's world news in one image](https://make.fun/bounty/news-image-20261120)

A newspaper front page for **Friday 20 November 2026**, drawn entirely
from code by a small Python program — standard library only, no network,
no downloaded assets. Every pixel is computed at run time from a
hand-written 5×7 bitmap font and plain geometry, so the output is fully
deterministic: run it twice, get the same bytes.

## The image

- **Top story:** the International Court of Justice rules that Myanmar
  committed genocide against the Rohingya in its 2017 crackdown — the
  first time the World Court has found a state guilty of the crime.
  By 9 votes to 6, the judges found at least 10,000 people were killed
  and ordered reparations, including the safe return of refugees.
- **Also in the picture:** Anthropic jumps 17% in the biggest IPO ever
  ($81.3bn) while the Dow sinks 1,100 points; Ukraine hits the Kerch
  Bridge for the third time in four days and Putin vows a harsher reply;
  Cyclone Akvan makes landfall near Gopalpur, Odisha, after nearly
  300,000 people are evacuated; the US Senate unanimously votes to
  force the release of the Epstein files; Iran steps up attacks on
  shipping in the Strait of Hormuz; COP31 wraps up with the fossil-fuel
  phase-out pledge dropped; Ukraine's European allies meet in Berlin
  ready for talks with Russia; and the Netherlands suspends its order
  over chipmaker Nexperia.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `entry.png` (1024×1024, about 25 KB) into `MAKEFUN_OUTPUT_DIR`,
or into `/output` when that directory exists, else `./out`.

## How it works

- `main.py` — everything in one file: the 5×7 bitmap font, a tiny
  software rasteriser (rects, lines, circles, polygons), the front-page
  scene (masthead, Peace Palace, eight news panels) and a minimal PNG
  encoder built on `zlib` and `binascii.crc32`.

Python 3 standard library only; nothing is installed and nothing is
fetched.

---

[Entered on make.fun](https://make.fun/bounty/news-image-20261120?ref=8fnx6nps&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
