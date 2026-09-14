# Uniform reference-grid experiment

The blank sheet no longer encodes the picture. Every day uses an identical grid, with the same dots and numbered axes; no active points are highlighted by default. The browser test compares the actual blank canvas pixels across all 25 days.

Open `index.html`. It starts on tile 14 with zero connections. Use **Connect all**, **Animate**, or **Draw manually**. Coordinates are `(column, row)`, numbered from 1 at the top left. Lift the pen between stroke sequences. The assembled-scene view shows all 25 tiles; **Previous drawing** allows comparison with the accepted drawing before grid snapping.

## What changed

This is coordinate drawing, rather than ordinary dot-to-dot. The former source has 243 positions per tile; the reference sheet has more positions, many intentionally unused. All grid locations are equally styled, regardless of whether the drawing visits them. The full instruction sequences are provided separately in the interface and JSON. The template could be used for any picture.

The artwork itself was not regenerated. First, remove the 1,643 intermediate vertices previously added only to meet the exact point count, reconnecting their existing straight segments. Then snap retained vertices to a uniform lattice, discard zero-length segments caused by coinciding endpoints, and deduplicate overlapping segments. Rebuild pen-lift sequences covering exactly the retained snapped edges, with no invented connectors. The preview's final drawing and animation use these edges directly.

| Grid per tile | Printed reference dots | Used positions per tile | Collapsed source segments across 25 tiles |
| --- | ---: | ---: | ---: |
| 16×16 | 256 | 50–134 | 1,870 |
| 31×31 | 961 | 66–197 | 842 |
| 61×61 | 3,721 | 77–224 | 221 |

The 61×61 variant is the default. The compact grid damages too many small features. The fine grid retains the overall scene, with some additional angularity and loss of small features. At a 180 mm drawing-square size its points are 3 mm apart; use the SVG to print larger if preferred. This trial does not claim an ideal difficulty level or practical daily completion time.

Uniform placement resolves silhouette leakage from the **blank sheet**. Once lines are drawn, shapes naturally become recognizable. Source-view, hints and answer controls are explicit review aids, not part of the blank-sheet concealment claim.

## Files

- `index.html`: offline, viewport-sized comparison, manual drawing, pen lifts, animation, progress slider and resolution switch.
- `blank-grid-16.svg`, `blank-grid-31.svg`, `blank-grid-61.svg`: reusable blank sheets with numbered axes. No subject-dependent marks.
- `connected-16/31/61.png` and `.svg`: exact assembled results.
- `tile-14-guide-16/31/61.html`: printable sample coordinate guides. All other daily sequences are in the preview and JSON.
- `grids.json`: all three grid variants, daily edges, stroke sequences, source-to-grid mapping and the previous drawing.
- `report.json`: measured snapping and point-count statistics.

## Reproduction and checks

From repository root:

```sh
nix develop -c python -m dot_to_dot.reference_grid
nix develop -c python -m unittest discover -s tests -p test_reference_grid.py
nix develop -c python scripts/test_reference_grid_browser.py
```

Checks cover exact retained-edge coverage, valid reference IDs, unused grid points, deterministic output, identical blank-sheet pixels across all 25 tiles, zero unintended pen-lift connectors, manual drawing, undo, animation and viewport fit. This is a prototype using the existing Christmas-room source; no new image generation or full print-book production was performed.
