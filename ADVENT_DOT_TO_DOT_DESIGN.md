# Advent village dot-to-dot

This feasibility edition expands the accepted winter-window experiment into **25 daily sheets which assemble into one continuous 5×5 Christmas village**. Each sheet contains exactly **243 numbered locations**. There are 6,075 printed locations altogether; points on shared seams are printed on both neighbouring sheets, so this is not 6,075 distinct positions in the assembled scene.

Open [the calendar](runs/advent-organic-village/index.html) to inspect the completed drawing, all dots, an animated daily reveal, or the generated composition reference. Click a square or a numbered day to open its standalone puzzle. Daily puzzles start unsolved, with hints off, and retain winter-window’s manual drawing, pen lifts, animation, scrubber and source/answer tabs.

## Artwork and conversion

1. Generate one composition reference for the entire scene. The saved [prompt](inputs/advent/winter-village-prompt.txt) asks for a continuous winter village, with landmarks and foreground detail distributed across the square. Save the generated raster unchanged; its SHA-256 is recorded in `run.json`.
2. Author a simplified vector adaptation in [advent/artwork.py](advent/artwork.py). Roofs, mountains, streets, the river and branches live in a single 1500×1500 coordinate system. This is not 25 independently generated pictures. The owl reuses anatomy from the approved winter-window artwork. Small snow crystals, wrapping patterns and roof details are actual drawing strokes.
3. Clip paths at the 300-unit sheet boundaries. Snap endpoints to a shared 3-unit lattice, including seam intersections. Retain seam-touching paths first, then structural paths and details by priority. If the 243-point budget cannot accommodate a whole interior path, omit that path; record the number of omitted segments. The final vector source is the retained geometry, not the full candidate artwork or generated raster.
4. If a sheet has fewer than 243 vertices, subdivide its longest eligible existing segments on the lattice until it reaches 243. This introduces no new object or connection between separate strokes, but snapping can slightly bend a subdivided line. Counts are recorded per day. Subdivision can make some outlines more apparent in dots-only form; this is a feasibility tradeoff to review, not a claim that concealment is solved.
5. Decompose each graph into edge-disjoint trails. An Euler traversal uses temporary virtual edges to find pen-lift breaks; those virtual edges are discarded. Shuffle trails deterministically and assign printed IDs by first visit. Follow the listed sequence for each stroke; **do not connect all numbers 1–243 as one route**. Shared vertices may be revisited.
6. Map each sheet into a 1200×1200 page, with the assembly square at `(100,100)`–`(1100,1100)`. Place labels while avoiding other labels and dots. Reject duplicate/unused locations, overlapping number labels, altered edge coverage, or insufficient spacing. All PNG, SVG and canvas views use the same point and edge data.

An automatic skeleton-clustering experiment was rejected during development because it merged nearby architectural lines into a mesh. The shipped generator uses the authored vector process above.

## Deliverables

`runs/advent-organic-village/` contains:

- `index.html`: offline calendar, 25 day links, dots-only overview, source reference and canvas reveal.
- `full-scene.svg/png`: the exact assembled drawing, reconstructed from daily edges, with no extra raster detail.
- `all-dots.svg/png`: the same locations without connections or numbers; inspect individual sheets for readable numbering.
- `calendar.json`: all daily points, labels, strokes and edges; `run.json`: provenance and checks.
- `authored-artwork.json`: candidate vector paths before daily budget selection; `generated-reference.png` and `source-prompt.txt`: generation inputs.
- `day-01/` through `day-25/`: standalone canvas demos; numbered dots, connected dots, clean source and answer PNG/SVGs; stroke guides; point JSON; validation reports.
- `puzzles.html`, `stroke-guides.html`, `solutions.html`: separate 25-page print books. Each puzzle needs its corresponding stroke guide.
- `assembly.html`: numbered 5×5 map. Print A4 at 100%, without browser headers, then trim each drawn square to the dashed outline. Each square is 155 mm and the assembled scene is 775 mm square. SVGs allow larger printing when desired.

The calendar overview opens on the completed scene for this review. It draws actual edge prefixes during animation, never fades in a source image. Daily demos show explicit pen lifts. The overview’s dots are intentionally unnumbered at the full-scene scale; daily sheets carry all numbers.

## Reproduction and checks

```sh
nix develop -c python -m advent.build --output runs/advent-village-new
nix develop -c python -m unittest discover -s tests
nix develop -c python scripts/test_advent_browser.py
```

The generator refuses an existing output directory. The flake supplies Python, Pillow, NumPy and SciPy; source generation remains a separate image-generation step. Chrome is needed only for browser checks and PDF export. The browser-check script also exports the four print documents as PDFs. This checked-in edition includes all four PDFs.

Automated checks cover 25×243 unique daily points, all points used, exact edge coverage, no pen-lift connectors, deterministic geometry, seam clipping, label overlaps, exported geometry, and browser reveal/reset/manual drawing. Visual review must still judge daily interest, concealment, label-to-dot ambiguity, and the artistic effect of the assembled scene. The simpler village adaptation and its daily crops are a new candidate, not an assertion that every sheet matches winter-window’s difficulty.


## Organic revision and daily composition

Natural contours use Catmull–Rom control knots sampled into short straight segments before clipping and quantization. The puzzle canvas still draws straight dot-to-dot connections; it does not substitute smooth curves or paint the reference over the answer. Architecture retains its straight edges. Added focal motifs have priority over optional textures, and generation rejects a budget that would drop a required motif path.

The scene remains a shared drawing. Daily focal details are positioned deliberately inside their sheet boundaries, while roofs, branches, snowbanks and water cross between sheets. The [solved contact sheet](runs/advent-organic-village/tile-review.html) exposes each crop for review; subject captions stay off the unsolved puzzle pages. Recognizability is a human review criterion, not something the geometry tests establish.

| Days 1–5 | Days 6–10 | Days 11–15 | Days 16–20 | Days 21–25 |
| --- | --- | --- | --- | --- |
| Robin | Snow-roofed cottage | Cottage by the tree | Tree bauble | Wrapped gifts |
| Bells | Cottage and clock tower | Front-door wreath | Snowman | Sleigh |
| Dove | Dormer cottage | Street lantern | Market stall | Duck by the stream |
| Moon and cloud | Chapel window | Cottage windows | Market wares | Rabbit |
| Pine cone | Village houses | Snowy rooftop | Market and fir | Owl |

The viewport layout measures the actual header and tab height, then limits the square preview to the remaining viewport height and its column width. A resize observer and window resize listener handle text wrapping and resizing. Desktop controls scroll independently; phone controls follow the complete drawing. Short landscape windows use a compact header and side controls. Print sizing is unchanged.

The first village outputs and `advent/artwork_v1.py` are retained for comparison. No new raster was generated for this revision; the existing composition reference remains credited, while the vector artwork is revised directly.
