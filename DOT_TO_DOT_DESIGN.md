# Dot-to-dot experiment

The silhouette approach below was rejected because the raw dots reveal the subject. See [the adult multi-stroke design](DOT_TO_DOT_ADULT_DESIGN.md) for the current approach, which supports pen lifts, interior detail, and sparse corners.

## Objective

Generate source line art and derive exactly **243 unique numbered points** whose straight connecting segments reconstruct it. Show the source, completed route, and identical dots without connecting lines. Offer an honest canvas animation and manual tracing mode. This is a separate workflow from the marker mosaics.

The first subject is a Christmas reindeer. The user has not accepted its artistic quality or concealment yet.

## Source requirements and extraction

Ask the image generator for one closed, thin black outer outline on white, without shading, disconnected components, or interior detail. Preserve the exact prompt and original generated PNG. The first source and prompt are in `inputs/dot-to-dot/`.

Threshold the raster at luminance 160 and use OpenCV external contour tracing. Select the contour enclosing the largest area and require a substantial enclosed silhouette. Fit it proportionally inside a 1200×1200 logical canvas with 80-unit margins. The original generated artwork remains untouched and is shown separately. The puzzle follows the outside of the ink stroke, not its centreline. Interior strokes and detached components are not reproduced; this first source has small interior strokes near leg junctions, so it is not pixel-identical to the completed puzzle.

This MVP is an outer-contour workflow, not a general multi-stroke vectorizer. It must not invent long connecting jumps between disconnected drawings.

## Exactly 243 points

1. Simplify the ordered closed contour with Douglas–Peucker, retaining shape-defining corners. Increase the tolerance only as necessary to fit below 70% of the point budget.
2. Subdivide the longest remaining edges until there are exactly 243 points. Their order follows the contour.
3. Construct a regular square lattice. For the first output, the lattice spacing is 18 logical units and its origin is (60,60).
4. Use a minimum-cost one-to-one assignment from sampled points to lattice sites, minimizing total squared displacement. Two dots cannot share a site.
5. Test full snapping first. If it introduces intersections/touches or places dots too close together, progressively reduce the pull toward the assigned sites. Reject a result if no tested strength preserves a usable path.
6. Place each number near its dot, testing several offsets to avoid other dots and previously placed labels. Record any remaining label overlaps rather than hiding them.

`points.json` is authoritative. Point IDs are 1–243. Its only edges are 1→2, 2→3, …, 242→243, and 243→1. There are **243 points and 243 segments**, because the last segment closes the loop; there is no duplicate dot 244.

The shipped reindeer uses full grid alignment, 243 unique sites, zero non-adjacent path intersections/touches, 18-unit minimum dot spacing, and no label-box overlaps. Mean displacement from the pre-grid polyline is about 6.69 units; maximum is about 12.57.

## Concealment trade-off

A sparse selection of grid sites can still reveal the silhouette. Full alignment does not mean every grid site is populated. This reindeer remains partly recognisable from the dots alone, especially its antlers and legs. There are no unnumbered decoy points and no fake interior dots.

The first experiment demonstrates geometry and interactive drawing, not successful concealment. If concealment is insufficient, the next art experiment should distribute a single winding line through more of the page, with intentional interior structure, rather than making a more distorted outer outline. Source design is the limiting factor here; a colour or opacity trick must not substitute for a harder puzzle.

## Canvas integrity and interaction

The self-contained `index.html` embeds the source PNG and the exact JSON coordinates, so it opens from disk without a server or network connection. The source image is an ordinary separate image element visible only in the source tab. It is never painted into the canvas.

Every canvas frame starts with a clean white background, optionally draws a clearly labelled alignment grid, then draws only the requested prefix of the JSON edges, followed by the same dots and optional number labels. A fractional animation step interpolates along one straight segment. It never uses curves, a raster answer layer, extra strokes, or changed dot positions.

Controls include animate/pause, reset, line-count scrubber, speed, number visibility, optional alignment grid, source/connected/puzzle views, and PNG export. Manual mode accepts dot 1 first and then only the next numbered dot; after 243 it requests dot 1 to close. It supports clicking or dragging, rejects wrong dots, and offers undo. A highlighted next dot is an explicit aid in manual mode only. The default unsolved view has no extra highlight or grid.

## Files and reproducibility

```sh
nix develop -c python -m dot_to_dot --source inputs/dot-to-dot/reindeer.png --prompt inputs/dot-to-dot/reindeer-prompt.txt --output runs/dot-to-dot-reindeer-new --points 243 --grid 18
nix develop -c python -m unittest discover -s tests -v
nix develop -c python scripts/test_dot_browser.py
```

Build into a new directory; existing runs are not overwritten. Dependencies are pinned by `flake.lock`: Pillow, NumPy, SciPy, and OpenCV. The browser smoke test uses installed Chrome and websocket-client; Chrome is not needed to generate SVG/PNG/JSON outputs.

Outputs include preserved `source.png`, `points.json`, `run.json`, numbered `dots.svg/png`, numbered `connected.svg/png`, unnumbered `answer.svg/png`, and the self-contained canvas `index.html`. The SVGs are printable vector assets. The browser test additionally saves actual canvas exports and a browser screenshot.

Checks cover exact count and order, distinct coordinates, valid bounds, exact edge sequence and closure, intersections, minimum spacing, deterministic assignment, unchanged dots in solved/unsolved SVGs, and rejection of tampered point/edge data. Browser checks exercise reveal/reset, scrubbing, real pointer drawing, wrong-point rejection, undo, animation/pause, source isolation, and unchanged point data. The source is not proof of the answer: the connected SVG and canvas are the reviewable result.

Algorithm references: [OpenCV contour extraction and simplification](https://docs.opencv.org/4.x/d3/dc0/group__imgproc__shape.html), [SciPy linear assignment](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html).
