# Sudoku → numbered-grid trial

[Open the interactive test](index.html) · [Compare the sheets](review.html)

This is day 18 of the accepted 5×5 Christmas-room scene: a cup, part of the teapot, holly and surrounding furniture. The artwork was not regenerated. It is a partial scene tile, not a standalone composition.

## Try it

1. Solve the Sudoku, or press **Fill solution (demo)**. It has 33 givens and one verified solution; its human difficulty has not been rated.
2. Select a drawing key. The corresponding Sudoku cell's digit selects **start (column, row)** and **number of connections**. Coordinates are 1-based from the top left.
3. Read the number on the starting dot. Connect successive numbers for the stated number of lines: a length of 6 means 7 dots. Lift the pen after every instruction.
4. Click dots manually, or use **Animate instruction**. **Locate start** is an optional preview aid. Zoom and scroll to read labels; **Fit** returns to the full tile.
5. Enter a wrong Sudoku digit to try its decoy. The preview uses that digit without correcting it. **Check Sudoku** is a separate, explicit answer check.

**Reveal correct drawing** decodes all correct starts and lengths. The view menu compares that result with the original snapped artwork. Turn off **Numbers and dots** to inspect the lines alone. The page starts with an unsolved Sudoku and no drawn lines; answer data are embedded for this offline review, not secured against inspection.

## Construction and measured result

- Grid: 61×61, with all **3,721 positions** present and uniformly styled. Each has exactly one unique number, from 1 through 3,721.
- Correct drawing: **38 instructions, 213 connections, 251 distinct labelled positions**. Thirty-eight initially blank Sudoku cells are drawing keys. Other cells help solve the Sudoku but unlock no drawing instruction in this trial.
- Shared junctions: the source visits 207 distinct positions. **44 repeated visits move to an unused neighbouring grid position**, at most √2 grid steps (one row and one column). This deliberately changes geometry: gaps and occasional short protrusions remain visible. The original is supplied for honest comparison. It does not preserve exact tile-seam joins for a production calendar.
- Wrong answers: **304 decoy paths**, eight per key, exclusively on positions unused by the correct drawing. Each has the same connection count as that key's correct choice. Remaining grid locations form additional short decoy sequences.
- Numbers: real and decoy paths receive consecutive runs in shuffled order. No label style or range is reserved for the real picture. The start coordinate identifies the first number; adding one repeatedly reconstructs the entire path. There are no hidden intermediate drawing instructions or extra pen-lift connectors.

The outline cannot be read from dot placement alone. Labels are artwork-dependent, however, so studying consecutive numbers can reveal paths. Random-walk decoys may be distinguishable from meaningful contours. This is an interaction and construction test, not a proof of concealment. The main practical issues to judge are number searching, label density, drawing damage at junctions, and how readily real paths can be distinguished from decoys.

## Print and artifacts

The SVG sheets are 420×420 mm, intended for an A2-size print trial with sufficient printer margins or slight scaling. The drawing square is approximately 384 mm wide; dot spacing is about 6.4 mm. Four-digit labels are still small. Printing at A4 makes this substantially harder; no physical print test has been performed. This grid has many more than the former 243 printed dots per day.

- `blank.svg` / `blank.png`: the actual numbered puzzle.
- `connected.svg` / `connected.png`: correct lines on that same numbered sheet.
- `answer.svg` / `answer.png`: decoded lines alone.
- `original.svg` / `original.png`: original reference-grid lines before separating junction visits.
- `lookup.html`: printable nine-choice table for all 38 keys.
- `puzzle.json`: Sudoku, solution, labels, choices, source paths and changed positions.
- `report.json`: measured counts and displacement.
- `browser-preview.png`: screenshot of the live interface with demo Sudoku filled and drawing blank.

## Reproduce and verify

```sh
nix develop -c python -m dot_to_dot.numbered_grid
nix develop -c python -m unittest discover -s tests -p test_numbered_grid.py
nix develop -c python scripts/test_numbered_grid_browser.py
```

The generator writes JSON, SVG and interactive HTML. The Chrome browser check also exports PNGs from the actual rendering canvas. Tests verify unique labels, reconstruction from only starts and counts, every correct route, disjoint wrong-answer paths, bounded junction displacement, Sudoku uniqueness and initially blank key cells. Browser checks cover manual consecutive-number drawing, pen lifts, wrong answers drawing decoys, animation, reset, all 213 correct connections, zoom, and viewport fit at desktop and mobile sizes.
