# Ashmoret Selichot

A mobile selichot reader for the Yamim Noraim that opens to **the correct day's seder** for today's Hebrew date, with the full Hebrew text embedded.

**→ https://hereiszee.github.io/selichot-yamim-noraim/**

Installable to a phone's home screen and fully offline after the first visit.

## What it does

**Works out which day it is.** It converts the current date to the Hebrew date with the standard molad-based calculation, then resolves which selichot are said using the Ashkenaz selichot luach — not a naive count from the first day. Selichot begin the Motzaei Shabbat before Rosh Hashanah, moving a week earlier when Rosh Hashanah falls on Monday or Tuesday; none are said on Shabbat or on Rosh Hashanah itself; and the four numbered days of the Ten Days of Repentance land where the luach puts them. Because Rosh Hashanah can only fall on Monday, Tuesday, Thursday or Shabbat, the whole assignment is four fixed tables, transcribed from the [Wikisource selichot table](https://he.wikisource.org/wiki/%D7%A1%D7%93%D7%A8_%D7%94%D7%A1%D7%9C%D7%99%D7%97%D7%95%D7%AA) rather than derived.

The Hebrew date rolls over at 19:00 local time as an approximation of nightfall, so a seder opened after midnight is the one for that night and the following morning. On Shabbat or Rosh Hashanah the page says why there are none and shows the next day.

**Three nusachim.**

| In the app | Source text |
| --- | --- |
| נוסח ספרד | Selichot Nusach Polin — 14 day-sections |
| נוסח אשכנז | Selichot Nusach Ashkenaz (Lita) — 14 day-sections |
| עדות המזרח | Selichot Edot HaMizrach — one daily seder |

**Reading.** Text size, a screen-wake toggle, an index of the day's piyutim that jumps, previous/next day, reading progress, and light/dark following the device. Nusach and text size are remembered locally.

**The luach.** The season is drawn as the א–ש weekly grid from the back of a selichot book: today ringed in brass, the day being read in tekhelet, Shabbat and Yom Tov greyed out. Any selichot day is one tap away.

**The ד׳/ה׳ swap.** In years when Rosh Hashanah falls on Tuesday or Shabbat, many congregations swap the fourth and fifth days of the Ten Days so that the fifth is said on a day with keriat haTorah. The page offers that as a one-tap option rather than deciding for you.

## Texts

- **Nusach Polin** and **Nusach Ashkenaz (Lita)** — Hebrew Wikisource via [Sefaria](https://www.sefaria.org/), CC BY-SA 4.0.
- **Edot HaMizrach** — Torat Emet, public domain.

These are one printed tradition each. A shul with its own minhag will differ in places. Follow your congregation's practice.

## Layout

```
index.html              the whole app — markup, styles, calendar logic, rendering
data/polin.json         }
data/lita.json          } the texts, fetched on demand and cached
data/mizrach.json       }
sw.js                   offline cache
manifest.webmanifest    home-screen install
```

No build step and no dependencies. Open `index.html` over any static server, or push and let GitHub Pages serve it.

## Licence

Code: MIT. Texts keep their own licences, noted above and on the page.
