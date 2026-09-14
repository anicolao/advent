# Permanent links for the advent book

Use **`https://advent.annasdadpress.com`** as the canonical host for printed links and QR codes. Include the year so future calendars can coexist without changing the 2026 book's destinations.

## Calendar and daily pages

Calendar:

```text
https://advent.annasdadpress.com/2026/
```

Daily view:

```text
https://advent.annasdadpress.com/2026/day/DD/
```

Replace `DD` with the **two-digit December date**, from `01` through `25`. Keep the trailing slash. These URLs open the day page with numbered dots visible and Sudoku/drawing solutions hidden until the reader chooses to reveal them. They also provide the print controls.

Examples:

| Book date | QR payload |
| --- | --- |
| December 1 | `https://advent.annasdadpress.com/2026/day/01/` |
| December 9 | `https://advent.annasdadpress.com/2026/day/09/` |
| December 10 | `https://advent.annasdadpress.com/2026/day/10/` |
| December 25 | `https://advent.annasdadpress.com/2026/day/25/` |

Use the **calendar date**, not the artwork's original tile ID or its position in the assembled scene. December 1 is the bottom-right tile; December 25 is the top-left tile. The site resolves those positions from the frozen book edition.

Do not include `/advent/` in paths on the custom domain. Do not use a GitHub branch URL, local preview address, URL shortener, hash fragment or print query string for the daily book QR. `/2026` works through the host's directory redirect; encode `/2026/` to go directly to the canonical page.

## Machine-readable targets

All 25 targets are provided in:

- [CSV](links/2026-days.csv), with columns `day,url`.
- [JSON](links/2026-days.json), with numeric `day` and string `url` fields.

They are also published at `https://advent.annasdadpress.com/links/2026-days.csv` and `https://advent.annasdadpress.com/links/2026-days.json`. The site build generates these records in date order. Encode the `url` field as the QR's exact text payload; keep the date as its caption or placement key.

Equivalent Python for a Mathpub component or book-generation script:

```python
def advent_day_url(year: int, day: int) -> str:
    if not 1 <= day <= 25:
        raise ValueError("Advent day must be from 1 through 25")
    return f"https://advent.annasdadpress.com/{year}/day/{day:02d}/"

url = advent_day_url(2026, 1)
# Pass url to the book's existing QR renderer.
```

Only generate links for a year once that year's edition is published. Keep the existing Sudoku-solver QR destination separate if the book uses both: the advent URL opens the drawing companion, not the standalone Sudoku solving application.

## Optional print links

For a companion resource or instructions page, a print selection can be linked directly:

```text
https://advent.annasdadpress.com/2026/print/?from=1&to=25&mode=dots
```

`from` and `to` are inclusive December dates, 1–25. Set them equal for one day. Modes are `dots` (numbered sheet), `art` (line art only), and `solved` (line art over the numbers). A print view loads the selected sheets and offers Print / Save as PDF. The regular daily URL remains the preferred book QR target.

## Durability and release check

Preserve published year/day routes when adding later calendars. Keep the 2026 data frozen; review and record any correction explicitly. Moving hosting providers must preserve these custom-domain paths through equivalent pages or redirects.

Before printing a book, check all 25 URLs over HTTPS, open a sample on a phone, and scan the actual rendered QR codes from a print proof. Site URL verification does not test the QR renderer, ink quality or physical scan size. This change supplies URLs and documentation; it does not modify the finished Mathpub book or generate replacement QR artwork.
