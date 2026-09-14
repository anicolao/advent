# Contour-first Christmas room: source and reduction

This source was generated specifically for a 25-tile dot-to-dot, with 243 dots per daily tile. It is one continuous scene. It uses broad outlines, large ornaments and simple interior features rather than fine drawing that would have to be discarded later.

## Source brief

The initial brief specified a Christmas room with tree, fireplace, window, cat, rocking horse and tea set, clean medium-weight lines, large open shapes, minimal interior strokes and no shading or texture. A targeted edit replaced small greenery with broad holly and ribbon, removed rug fringe, and added a toy train and slippers in the lower foreground.

Both images were produced with the built-in image-generation tool. The exact prompts and original image variants are preserved in `inputs/target-first/`. `original.png` here is the unchanged refined generated source, not a vector reconstruction.

## Actual reduction

1. Normalize to a 1500×1500 raster, threshold and thin the ink.
2. Trace connected line chains, consolidating adjacent junction pixels without merging unrelated nearby lines. Tiny filled facial marks that collapse under thinning are represented by small closed contours derived from their ink extents.
3. Simplify each chain, clip at the 5×5 tile boundaries and snap the main vertices to a shared 3-unit lattice. Paths crossing a seam use the same simplification tolerance on both sides.
4. Fit each daily point budget by adjusting simplification tolerance. In this image, **no resulting traced segments had to be discarded to satisfy a tile budget**. Twenty-three tiles use tolerance 1.2; two use 1.8 or 2.6 analysis units.
5. Add remaining required points along existing segments to reach exactly 243 used locations per tile. These points are not decoys. This may make contours more apparent before connection, especially in sparse tiles.
6. Turn edges into pen-lift sequences and assign numbers. The comparison, SVG and PNG reductions are rendered from those exact numbered points and straight edges. No generated image is used to fill in the reduced view.

The point positions and complete sequences are in `calendar.json`. `trace-report.json` records simplification and omission counts; `validation.json` records point counts, spacing, label overlaps and edge checks. There are 6,075 printed locations; shared seam points repeat on neighbouring sheets.

## What this establishes

The simpler source transfers substantially more faithfully than the detailed nativity: the principal objects and interior shapes remain readable. It is a source-transfer proof, not a claim that every daily crop has the right artistic balance or that the unconnected dots conceal the scene. Those are separate review questions. Fine features still become angular and a few very small marks simplify away during tracing/snapping.

`index.html` compares source and reduction at full-scene and daily-tile scales, with optional grid, dots and numbers. Tile 14 also has standalone connected and dots-only SVG/PNG exports. No print books or full advent-calendar package were built for this proof.

Reproduce from repository root:

```sh
nix develop -c python -m dot_to_dot.target_first
nix develop -c python -m dot_to_dot.target_first_export
```

The earlier candidate batch remains paused. Future source candidates should follow this contour-first brief and be reduced before being offered for selection.
