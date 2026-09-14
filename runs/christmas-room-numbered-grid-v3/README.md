# Single-number dots with explicit joins

[Interactive preview](index.html) · [Printed Sudoku and lookup](lookup.pdf) · [Drawing sheet](drawing.pdf) · [Blank / connected / original comparison](review.html)

Every drawing dot now has **one unique number**, 1–966. Sudoku addresses use **R1C2** notation, with R1–R9 and C1–C9 on the borders only. No address labels appear inside Sudoku cells, in either the browser or the printed puzzle.

## How to draw

Solve a blank Sudoku cell, find its R/C address down the lookup table, and read across to its solved digit. The entry gives a drawing sector, starting number and commands:

- **+6:** draw six consecutive-number connections from your current number.
- **join 127:** draw one connection directly to dot 127. Keep the pen down.
- If another **+2** follows, continue from 127 to 128 and 129.
- Lift only after the entire entry. Then move to the next Sudoku lookup row.

Drawing sectors still use A–F across and 1–6 down. They are location aids on the drawing sheet, separate from Sudoku addresses.

**Actual example (spoiler):** R2C1 = 7 selects **B4 / 844 · +6 · join 844 · join 603 · +1**. Start at 844 in drawing sector B4, connect through 850, close back to 844, connect to 603, then 604. Lift. One numbered dot can now close a loop or serve as a shared junction without needing a second label.

The browser follows these printed commands directly. Manual drawing and animation use the same decoder. Join prompts name the exceptional destination; subsequent counting resumes from that destination. **Fill solution (demo)**, **Locate start** and **Reveal correct drawing** remain explicit review aids. A wrong Sudoku digit draws its decoy rather than being silently corrected.

## Result and tradeoffs

The 966 point locations, original geometry, 118 intermediate points and all 331 short connections are unchanged from v2. No source vertex or junction moves. All steps, including explicit joins, stay within 5% of the drawing width (about 17.4 mm on the supplied sheet).

Of 331 correct connections, **267 follow consecutive numbers and 64 are explicit joins**. Twenty of the 38 lookup entries contain joins; 18 need only consecutive numbering. Every wrong choice matches the correct choice's run lengths and join positions, so command complexity alone does not identify the correct digit. Wrong choices use only background dots and obey the same distance bound; their paths may overlap one another.

The cleaner drawing sheet needs more detailed lookup entries: the booklet is now **six A4 landscape pages**, including the Sudoku/rules page, versus four pages in v2. The drawing remains a separate **one-page A2 PDF**. Print sizes and page counts have been verified, but physical legibility and solving time have not been tested. The dot field is the same slightly irregular field accepted in v2; the new numbering still warrants a concealment review.

## Files and checks

`blank`, `connected`, `answer` and `original` SVG/PNG pairs show the actual puzzle and decoded artwork. `lookup.html` is the paginated print source; `drawing.html` is the separate sheet wrapper. `puzzle.json` stores unique labels, geometry, Sudoku and each command list. `report.json` records the counts. Earlier versions are preserved in their existing directories.

```sh
nix develop -c python -m dot_to_dot.numbered_grid_v3
nix develop -c python -m unittest discover -s tests -p test_numbered_grid_v3.py
nix develop -c python scripts/test_numbered_grid_v3_browser.py
```

The generator uses the accepted v2 artifact as immutable geometry. Checks verify one label per point, unchanged geometry, exact decoding of all correct and wrong instructions, matching run/join patterns, short joins, unique Sudoku solution and sorted R/C lookup coverage. Browser checks exercise manual joins followed by consecutive counting, pen lifts, wrong choices, animation, reset, all 331 connections, border-only Sudoku labels, desktop/mobile viewport fit, and six-page/one-page PDF output without content overflow. PNGs and PDFs are exported by the browser check.
