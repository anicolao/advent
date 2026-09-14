# Advent on GitHub Pages

The repository is `anicolao/advent`. Its reader-facing Pages site serves the finished calendar:

- **`/2026/`** is the durable companion to the finished Mathpub book, *25 Days of Christmas Sudoku*.

Historical experiment assets remain addressable for existing bookmarks, but there are no experiment links in the homepage, calendar, daily pages or retired archive landing page. Project history is retained in Git.

## Stable reader URLs

- Calendar: `https://advent.annasdadpress.com/2026/`
- Individual days: `https://advent.annasdadpress.com/2026/day/01/` through `day/25/`
- Print selection: `https://advent.annasdadpress.com/2026/print/?from=1&to=25&mode=dots`
- Drawing assets: `/2026/tiles/01/dots.svg`, `art.svg`, and `solved.svg`.

`dots` prints the numbered sheet; `art` prints only the finished line art and trim border; `solved` prints the finished drawing over the numbered sheet. The print view accepts any inclusive date range from 1–25. It waits for every SVG to load before enabling printing. The browser print dialog can also save a PDF.

Print at **100% / actual size**, with browser headers and footers disabled. Every SVG has a six-inch inner square and room outside for its location labels. Standard A4 and US Letter sheets accommodate one daily tile. All 25 trimmed squares assemble into a 30-inch scene. The full-scene reveal is a screen/download view; printing the 25 individual sheets preserves assembly scale.

Pages start without drawing or Sudoku spoilers. Each reveal is explicit. These are publicly available solutions, not date-locked secrets; the data are intentionally downloadable.

## The 2026 edition is a snapshot

`editions/2026/calendar.json` was imported from the finished saved edition in `sudoku-challenges/advent/editions/2026-2026-moderate/`. It preserves the actual book's date order, original Sudoku givens and answers, dot coordinates, unique labels, inverse numbering, complete choices and approved drawing paths. It also preserves the saved collision-aware label positions from the source's validated preview, at its final 7.1 TeX-point label setting. SVG digit widths follow the half-em metric used by that placement algorithm.

`provenance.json` records the source commit, SHA-256 hashes of all 25 daily files, the manifest and validated preview, and the frozen calendar hash. Import checks that every source field in the preview still matches its daily JSON. The Pages build checks the snapshot hash and never reads a sibling checkout or runs a puzzle generator.

The imported edition has the final bottom-right-to-top-left zigzag order: December 1 is physical row 5, column 5; December 25 is row 1, column 1. Do not replace it with a prototype or regenerate it when experimenting.

The source Mathpub checkout is not modified. Private publication drafts, build folders, commercial activity-book PDFs and unrelated books are not copied. This site exports the drawing sheets and requested answers from the approved edition data.

### Future years and corrections

Use a new year directory for a new calendar. The importer refuses to overwrite an existing edition:

```sh
python3 scripts/import_advent.py ~/projects/sudoku-challenges --edition YEAR-SEED-LEVEL
```

Add the new year to the homepage/navigation and extend validation before deployment. Preserve older routes and assets. If an error in an already published edition needs a correction, review it explicitly, document what changed, retain the original data in Git history, and update its provenance/hash deliberately. Never silently regenerate old answers.

## Build and preview

The Pages build requires Python's standard library only:

```sh
python3 -m unittest discover -s tests -p test_site.py
python3 scripts/build_site.py
python3 -m http.server 8765 --directory _site
```

Open `http://localhost:8765/2026/`. Relative links also work under GitHub's `/advent/` project prefix. `_site/` is generated and ignored by Git. The builder copies only the site, frozen edition exports and allowlisted experiment assets.

For the local Chrome interaction and print check:

```sh
nix develop -c python scripts/test_site_browser.py
```

The test serves the site under `/`, visits all 25 daily routes, checks exact Sudoku answers and explicit reveals, exercises all drawing modes, checks that reader pages do not link to experiments, checks mobile layout, and exports 3/3/25-page print PDFs at the expected physical scale. Review screenshots and PDFs are saved under ignored `.site-review/`. Physical printer scaling still depends on the print-dialog settings.

## Custom domain and QR targets

The canonical host is `advent.annasdadpress.com`; paths do not contain the repository name `/advent/`. See [QR_LINKS.md](QR_LINKS.md) for the day-view URL contract and the 25-row CSV for book production.

GitHub Pages is configured with this custom domain. Cloudflare has a DNS-only CNAME named `advent`, targeting `anicolao.github.io`, with a 300-second TTL. GitHub Pages provides the HTTPS certificate. Keep the GitHub domain setting and `site/CNAME` consistent; with an Actions deployment, the GitHub Pages setting controls domain binding.

Cloudflare credentials are read locally from `.env`. `.env` and `.env.*` are ignored by Git and excluded from the allowlisted site build. They are not needed by the Pages workflow. Never paste credential values into commands, documentation or workflow files.

## Deploy

`.github/workflows/pages.yml` validates and builds on pushes to `main`; GitHub Actions publishes `_site/` to Pages. Pull requests run the build without deploying. The repository's Pages source must be **GitHub Actions**. This follows GitHub's [custom Pages workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) configuration.

Keep generated review files out of commits. Publication requires a successful validation/build and a successful Pages deployment. Check the public calendar and a deep day URL after release.
