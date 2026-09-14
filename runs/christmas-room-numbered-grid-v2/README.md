# Short connections, exact artwork, printed lookup

[Interactive prototype](index.html) · [Sudoku and lookup PDF](lookup.pdf) · [Drawing PDF](drawing.pdf) · [Original / decoded comparison](review.html)

This revision addresses three problems in the first numbered-grid trial: moving shared junctions damaged the picture, long numbered connections were difficult to find, and the web-only unlocking interaction obscured the printed process. It still uses day 18 of the Christmas-room scene.

## Actual paper process

Print `lookup.pdf` (four A4 landscape pages) and `drawing.pdf` (one A2 page). The drawing SVG can also be scaled to a chosen paper size. Physical print legibility has not yet been tested.

1. Solve the Sudoku on booklet page 1. Its rows are **A–I** and columns **1–9**.
2. Each originally blank cell has exactly one lookup row. Givens have none. There are 38 blank cells, in natural reading order, and 38 drawing instructions.
3. Find the cell's row-letter section in the booklet: A–C on page 2, D–F on page 3, G–I on page 4. Find the cell address down the left; move across to its solved digit, 1–9, at the top.
4. Read **drawing sector / starting number / +connections**. Find the start within that sector of the separate drawing sheet, follow consecutive numbers, stop after the connection count and lift your pen.
5. Tick the lookup row when done. Continue down sections A–I. There is no additional arbitrary key-number system.

**Actual worked example (spoiler):** Sudoku **A2 = 9**. Booklet page 2, row **A2**, answer column **9** says **E3 / 305 / +8**. In drawing sector E3, start at number 305 and connect 306 through 313; then stop and lift. Drawing sectors are columns A–F and rows 1–6, distinct from Sudoku cell addresses.

Each dot has two numbers. Both refer to the same physical location in different sequences. Use the number you are currently following; the other is not an instruction to jump. Because starts can have two labels, the lookup now includes an explicit starting number in addition to its sector and connection count. This is a deliberate refinement of the previous coordinate-and-length format.

## What changed in the drawing

- **Exact original geometry:** no source vertex moves. Forty-four shared locations retain their original junctions. Long segments are subdivided by points lying exactly on the original straight line. Tests verify endpoints, collinearity and total segment length, not merely segment counts.
- **Short hops:** 118 intermediate points turn the original 213 segments into 331 connections. Every correct and wrong-answer connection is at most 3 source-grid units, compared with the previous maximum of 37.22. That is 5% of the drawing width, or approximately 17.4 mm on the supplied 348 mm drawing square.
- **Fewer printed dots:** 966 locations and 1,932 unique number labels. All locations have two labels, so junctions are not specially marked. The earlier sheet had 3,721 locations and labels.
- **Location sectors:** a faint 6×6 overlay limits the initial number search to a small area. It is not a requirement that dots occupy grid intersections.
- **Irregular dot field:** intermediate points preserve the exact art; jittered background points fill gaps. This relaxes the strictly uniform grid. Dot density and local alignments may still disclose some structure; concealment needs human review again.
- **Decoys:** wrong digits select short-hop subsequences of background paths. They never use a correct drawing dot. Decoy subsequences can overlap and are not 304 separate disjoint paths. All choices can be decoded using only their starting number and connection count.
- **Sudoku:** 43 givens, 38 blanks, a verified unique solution. Its difficulty has not been rated; this is a mechanics prototype.

## Web preview

The Sudoku uses the same cell addresses as the booklet. Select a cell or enter its answer: the lookup row stays above the drawing, with the selected answer column highlighted. It does not silently correct wrong digits. Use **Fill solution (demo)** to skip solving, then draw manually or animate one instruction. **Locate start** is an optional web aid, not a requirement for the printed process. The initial page has no drawn connections and no solution filled.

The **Correct drawing** and **Original grid drawing** views have the same contours and junctions. Hide dots to compare the lines. The page includes answer data for offline review, so it is not protected against inspecting the solution.

## Files and reproduction

`blank`, `connected`, `answer` and `original` SVG/PNG pairs show the puzzle, its connected state, clean decoded lines and original lines. `lookup.html` is the actual paginated booklet source; `drawing.html` wraps the separate drawing sheet for printing. `puzzle.json` contains the exact geometry, label lookup, Sudoku and nine choices for every blank cell. `report.json` contains the measured counts.

```sh
nix develop -c python -m dot_to_dot.numbered_grid_v2
nix develop -c python -m unittest discover -s tests -p test_numbered_grid_v2.py
nix develop -c python scripts/test_numbered_grid_v2_browser.py
```

The generator writes the data, SVGs, booklet HTML and interactive HTML. The Chrome check exports canvas PNGs, screenshots and both printable PDFs. Tests cover exact original segments, maximum hop length, unique labels, shared positions, all start/count decodings, wrong-answer paths excluding real dots, Sudoku uniqueness and complete sorted lookup coverage. Browser checks cover manual drawing and pen lifts, wrong-digit decoys, animation, reset, reveal, viewport fit, zoom and booklet overflow.
