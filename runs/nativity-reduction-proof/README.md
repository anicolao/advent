# Nativity: reduction proof

This is a **diagnostic result, not accepted puzzle artwork**. It answers whether one of the detailed generated candidates survives the agreed 243 locations per daily tile. There are 25 tiles and 6,075 printed locations. Each tile has its own numbering and explicit pen-lift sequences.

Open `index.html` for an unchanged-source versus actual-reduction comparison. Choose a tile to compare its source crop with its exact 243-point geometry, or use its animation link for the existing manual drawing demo. The reduced drawing contains only point-to-point segments, never an image overlay.

## What was actually done

1. Read candidate 01, the stable Nativity. Normalize to a 1500×1500 analysis raster.
2. Threshold dark ink at 130 and thin it into a pixel skeleton. Trace connected chains without grouping nearby, unrelated lines.
3. Simplify each traced chain using a 1.7-unit polyline tolerance.
4. Clip into 25 regions of 300×300 units and snap vertices to a 3-unit lattice.
5. Keep the longest eligible chain fragments within each tile's 243-point budget. Subdivide retained segments if necessary to reach exactly 243 used points.
6. Decompose retained edges into trails with explicit pen lifts. Export point JSON, numbered dots, connected drawings and the canvas demo.

Reproduce from the repository root:

```sh
nix develop -c python -m dot_to_dot.reduction_proof
```

This experimental command regenerates this proof directory. It does not run image generation or change the accepted village calendars.

## What the proof shows

The broad scene remains identifiable, but facial features, contour continuity and small subjects suffer badly. Hatching and straw compete with meaningful lines for the dot budget. Independent selection in each tile can remove one side of a cross-boundary feature. Concealment is also unproven.

The successful village was **an authored vector adaptation**, not an automatic reduction preserving the generated drawing's quality. Presenting highly detailed raster candidates without a reduction proof overstated how directly their appearance would transfer.

A more defensible next source-art brief is sparse contour-only illustration with deliberate facial landmarks and interior shapes, minimal hatching, and details composed around the daily budgets. Before generating another large batch, validate a representative face/subject tile and its neighbours. This baseline does not solve the source-to-puzzle art direction.

The original generated source is preserved as `original.png`; the exact final retained vector geometry is `reduced.svg`. Prompts for the paused candidate batch are in `inputs/art-candidates/prompts.json` at the repository root. `validation.json` records the actual point/edge checks and the limitations above.
