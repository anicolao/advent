# Adult dot-to-dot: interior structure and pen lifts

The reindeer silhouette failed the concealment test: its evenly sampled boundary identified the subject before drawing. Snapping that boundary to a grid did not address the problem.

The current trial uses an intricate composition with interior features and background objects, sparse vertices along straight lines, and explicit pen lifts. The first revised artwork is an angular winter-window scene. Its raw dots fill a broad rectangle; they are not an evenly sampled animal outline. Human review is still required to establish how well the subject is concealed.

## Artwork and provenance

A new source reference was generated with the built-in image-generation tool. Its prompt is `inputs/dot-to-dot/winter-window-prompt.txt`, and its unmodified raster is `inputs/dot-to-dot/winter-window.png`.

Automatic clustering of the dense reference erased recognisable details, so the final source is an **authored vector adaptation**, defined in `dot_to_dot/winter_scene.py` and exported to `artwork.json` and `source.svg/png`. It is deliberately simpler than the generated reference. The final source shown in the app is this vector artwork; the generated reference is separately preserved as `generated-reference.png`. This is not a claim of automatic, faithful tracing of the generated image.

Each of the 243 distinct vector vertices becomes exactly one numbered location. Points are placed at corners and important changes of direction, with long straight segments represented only by their endpoints. Interior features and background linework carry the detail. No dots are added purely as decoys, and no raster or unnumbered stroke is used to finish the answer.

The strict uniform-grid idea was abandoned after a prototype badly distorted the image. The current dots have irregular spacing appropriate to the vector features. Grid regularity is subordinate to recognisable art and concealment.

## Stroke model

The puzzle has **243 unique numbered locations, 50 strokes, and 277 straight segments**. There are 49 pen lifts between the 50 strokes. Locations can be reused where strokes meet; the number of segments therefore need not equal the number of dots.

This is a sequence-list dot-to-dot, not an uninterrupted global 1→243 puzzle. Follow each row's numbers, then lift the pen and begin the next row. A sequence can revisit an earlier dot or close to its start. Each physical location has one label. The app displays the current sequence, and `instructions.html` provides all sequences for printing.

`points.json` schema 2 stores:

- `mode: multi_stroke`, canvas dimensions, and `point_count`.
- `points`: exactly 243 unique numbered locations with label positions.
- `strokes`: numbered point sequences, plus `start_edge` and exclusive `end_edge` offsets.
- `edges`: only adjacent pairs within each stroke, flattened in drawing order.

No edge is inserted between different strokes. Crossings are allowed where the authored drawing has them; a crossing without a numbered dot does not create a connection instruction. Stroke order is deterministically shuffled, with the main outer contour last. IDs are assigned on first visit to avoid spatial numbering that traces the subject immediately.

## Honest rendering and manual drawing

The source, solved SVG, PNG, and canvas all come from the same vector coordinates and stroke edges. The solved and unsolved views have identical dot and label positions. The source image is a separate reference element and never gets drawn into the canvas.

Animation draws a prefix of the edge list and pauses briefly at stroke boundaries. Moving to the next stroke does not draw a connecting segment. Manual mode requires selecting the new stroke's starting dot after a pen lift, then accepts only its listed next point. Wrong dots do nothing. Shared points can be revisited. Undo and scrubbing reconstruct state from the stroke boundaries.

The default is unsolved, with numbers shown and hints **off**. A next-dot highlight is an explicit optional aid. Source and connected artwork are behind their tabs. The printable SVG contains numbered dots only; the instructions are separate.

## Checks and review

Checks establish the exact count, unique locations, all dots used, no zero-length segments, correct stroke ranges, exact agreement between source vector edges and output edges, no phantom pen-lift connectors, and identical dots/labels before and after drawing. Label placement reports zero overlapping label boxes in this trial. The minimum permitted dot spacing is 10 logical units; printing large or zooming helps at the densest interior features.

Real Chrome tests exercise unsolved/reveal/reset, scrubbing, manual pointer input, a pen lift with no connecting line, wrong-point rejection, undo, animation/pause, source isolation, and unchanged points. These checks establish correctness, not artistic quality or concealment.

A fair concealment test shows only `dots.svg` to people who have not seen the reference or answer and records their guesses before any lines are drawn. Then review recognisability after completion and whether 50 stroke sequences are enjoyable to follow. The author cannot be a blind reviewer after seeing the source.

## Run it

```sh
nix develop -c python -m dot_to_dot.multistroke --output runs/winter-window-new
nix develop -c python -m unittest discover -s tests -v
nix develop -c python scripts/test_multistroke_browser.py
```

The build refuses to overwrite an existing directory. The browser test uses the shipped `runs/dot-to-dot-winter-window` run and installed Chrome. `index.html` embeds the point data and vector-source preview, so it works offline. Original mosaic and reindeer experiments remain intact; the adult multi-stroke mode does not change their drawing rules.
